#!/usr/bin/env python3
# ABOUTME: Snapshots and reports Claude Code subagent model/effort/token spend from local JSONL transcripts.
# ABOUTME: `mark` freezes a cutoff plus current config; `report --since` measures only turns after it.
import argparse, collections, datetime as dt, glob, json, os, subprocess, sys

HOME = os.path.expanduser("~")
SNAP_DIR = os.path.join(HOME, ".claude", "spend-snapshots")

# $ per 1M tokens (input, output). Cache write = 1.25x input, cache read = 0.1x input.
UNPRICED = set()

PRICES = {
    "claude-fable-5-1": (10.0, 50.0), "claude-fable-5": (10.0, 50.0),
    "claude-opus-5": (5.0, 25.0), "claude-opus-4-8": (5.0, 25.0),
    "claude-opus-4-7": (5.0, 25.0), "claude-opus-4-6": (5.0, 25.0),
    "claude-sonnet-5": (2.0, 10.0), "claude-sonnet-4-6": (3.0, 15.0),
    "claude-haiku-4-5": (1.0, 5.0),
}


def normalize(model):
    """Strip a dated snapshot suffix so claude-haiku-4-5-20251001 prices as claude-haiku-4-5."""
    parts = model.rsplit("-", 1)
    return parts[0] if len(parts) == 2 and parts[1].isdigit() and len(parts[1]) == 8 else model


def cost(model, u):
    model = normalize(model)
    if model not in PRICES and model != "<synthetic>":
        UNPRICED.add(model)
    inp, out = PRICES.get(model, (0.0, 0.0))
    return (
        u["input"] * inp
        + u["cache_write"] * inp * 1.25
        + u["cache_read"] * inp * 0.10
        + u["output"] * out
    ) / 1_000_000


def new_usage():
    return {"turns": 0, "input": 0, "cache_write": 0, "cache_read": 0, "output": 0}


def build_agent_index():
    """Map subagent transcript agentId -> the subagent_type that spawned it."""
    spawn, agent_type = {}, {}
    for path in glob.glob(os.path.join(HOME, ".claude/projects/*/*.jsonl")):
        with open(path, errors="replace") as fh:
            for line in fh:
                try:
                    rec = json.loads(line)
                except ValueError:
                    continue
                msg = rec.get("message")
                if isinstance(msg, dict):
                    for block in msg.get("content") or []:
                        if not isinstance(block, dict):
                            continue
                        if block.get("type") == "tool_use" and block.get("name") in ("Task", "Agent"):
                            st = (block.get("input") or {}).get("subagent_type")
                            if st:
                                spawn[block["id"]] = st
                res = rec.get("toolUseResult")
                if isinstance(res, dict) and res.get("agentId"):
                    tid = rec.get("toolUseID")
                    if not tid and isinstance(msg, dict):
                        for block in msg.get("content") or []:
                            if isinstance(block, dict) and block.get("type") == "tool_result":
                                tid = block.get("tool_use_id")
                    if tid in spawn:
                        agent_type[res["agentId"]] = spawn[tid]
    return agent_type


def collect(since=None, until=None):
    agent_type = build_agent_index()
    by_key = collections.defaultdict(new_usage)
    sessions = collections.defaultdict(set)
    for path in glob.glob(os.path.join(HOME, ".claude/projects/*/*/subagents/agent-*.jsonl")):
        agent_id = os.path.basename(path)[len("agent-"):-len(".jsonl")]
        atype = agent_type.get(agent_id, "unknown")
        with open(path, errors="replace") as fh:
            for line in fh:
                try:
                    rec = json.loads(line)
                except ValueError:
                    continue
                ts = rec.get("timestamp")
                if since and (not ts or ts < since):
                    continue
                if until and (not ts or ts >= until):
                    continue
                msg = rec.get("message")
                if not isinstance(msg, dict) or not msg.get("model"):
                    continue
                u = msg.get("usage") or {}
                key = (atype, msg["model"], rec.get("effort"))
                agg = by_key[key]
                agg["turns"] += 1
                agg["input"] += u.get("input_tokens", 0)
                agg["cache_write"] += u.get("cache_creation_input_tokens", 0)
                agg["cache_read"] += u.get("cache_read_input_tokens", 0)
                agg["output"] += u.get("output_tokens", 0)
                sessions[atype].add(agent_id)
    return by_key, {k: len(v) for k, v in sessions.items()}


def config_state():
    agents = {}
    for path in glob.glob(os.path.join(HOME, ".claude/agents/*.md")):
        model = effort = None
        with open(path, errors="replace") as fh:
            text = fh.read()
        front = text.split("---")[1] if text.startswith("---") and text.count("---") >= 2 else ""
        for line in front.splitlines():
            if line.startswith("model:"):
                model = line.split(":", 1)[1].strip()
            elif line.startswith("effort:"):
                effort = line.split(":", 1)[1].strip()
        agents[os.path.basename(path)] = {"model": model, "effort": effort}
    try:
        version = subprocess.run(["claude", "--version"], capture_output=True, text=True, timeout=15).stdout.strip()
    except Exception:
        version = None
    return {
        "env": {k: os.environ.get(k) for k in
                ("CLAUDE_CODE_SUBAGENT_MODEL", "CLAUDE_CODE_SUBAGENT_MODEL_FORCE", "ANTHROPIC_MODEL")},
        "agents": agents,
        "claude_version": version,
    }


def cmd_mark(args):
    os.makedirs(SNAP_DIR, exist_ok=True)
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    snap = {"name": args.name, "cutoff": now, "config": config_state()}
    path = os.path.join(SNAP_DIR, f"{args.name}.json")
    with open(path, "w") as fh:
        json.dump(snap, fh, indent=2)
    print(f"marked {args.name} at {now} -> {path}")


def resolve(ref):
    if not ref:
        return None
    path = os.path.join(SNAP_DIR, f"{ref}.json")
    if os.path.exists(path):
        with open(path) as fh:
            return json.load(fh)["cutoff"]
    return ref


def cmd_report(args):
    since, until = resolve(args.since), resolve(args.until)
    by_key, runs = collect(since, until)
    rows = collections.defaultdict(new_usage)
    for (atype, model, effort), u in by_key.items():
        tgt = rows[(atype, model, effort)]
        for k in u:
            tgt[k] += u[k]
    if args.json:
        print(json.dumps({
            "since": since, "until": until,
            "rows": [{"agent": a, "model": m, "effort": e, **u, "usd": round(cost(m, u), 4)}
                     for (a, m, e), u in sorted(rows.items())],
            "runs": runs,
        }, indent=2))
        return
    print(f"window: {since or 'all time'} -> {until or 'now'}\n")
    total = 0.0
    for atype in sorted({k[0] for k in rows}):
        sub = {k: v for k, v in rows.items() if k[0] == atype}
        atotal = sum(cost(m, u) for (_, m, _), u in sub.items())
        total += atotal
        n = runs.get(atype, 0)
        per = f", ${atotal / n:.4f}/run" if n else ""
        print(f"{atype}  ({n} runs, ${atotal:.2f}{per})")
        for (_, model, effort), u in sorted(sub.items(), key=lambda kv: -cost(kv[0][1], kv[1])):
            print(f"    {model:<20} effort={str(effort):<7} turns={u['turns']:<6} "
                  f"in={u['input']:<8} cw={u['cache_write']:<10} cr={u['cache_read']:<11} "
                  f"out={u['output']:<8} ${cost(model, u):.2f}")
        print()
    print(f"TOTAL ${total:.2f}")
    if UNPRICED:
        print(f"WARNING: no price for {sorted(UNPRICED)} - counted as $0")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("mark", help="freeze a cutoff timestamp plus current config")
    m.add_argument("name")
    m.set_defaults(func=cmd_mark)
    r = sub.add_parser("report", help="aggregate subagent spend in a time window")
    r.add_argument("--since", help="snapshot name or ISO-8601 UTC timestamp")
    r.add_argument("--until", help="snapshot name or ISO-8601 UTC timestamp")
    r.add_argument("--json", action="store_true")
    r.set_defaults(func=cmd_report)
    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
