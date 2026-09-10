#!/usr/bin/env python3
# ABOUTME: Snapshots and reports Claude Code subagent model/effort/token spend from local JSONL transcripts.
# ABOUTME: `mark` freezes a cutoff plus current config; `report --since` measures only turns after it.
import argparse, collections, csv, datetime as dt, glob, json, os, subprocess, sys

HOME = os.path.expanduser("~")
SNAP_DIR = os.path.join(HOME, ".claude", "spend-snapshots")

# $ per 1M tokens (input, output). Cache write = 1.25x input, cache read = 0.1x input.
MAIN = "main-session (not a subagent)"
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


def add_turn(agg, rec, msg):
    u = msg.get("usage") or {}
    agg["turns"] += 1
    agg["input"] += u.get("input_tokens", 0)
    agg["cache_write"] += u.get("cache_creation_input_tokens", 0)
    agg["cache_read"] += u.get("cache_read_input_tokens", 0)
    agg["output"] += u.get("output_tokens", 0)


def in_window(ts, since, until):
    if since and (not ts or ts < since):
        return False
    if until and (not ts or ts >= until):
        return False
    return True


def collect(since=None, until=None):
    agent_type = build_agent_index()
    by_key = collections.defaultdict(new_usage)
    sessions = collections.defaultdict(set)
    seen = set()
    # Main-loop turns: top-level session transcripts, excluding sidechain lines,
    # which are subagent work written into the parent file by older versions.
    for path in glob.glob(os.path.join(HOME, ".claude/projects/*/*.jsonl")):
        with open(path, errors="replace") as fh:
            for line in fh:
                try:
                    rec = json.loads(line)
                except ValueError:
                    continue
                if rec.get("isSidechain"):
                    continue
                msg = rec.get("message")
                if not isinstance(msg, dict) or not msg.get("model"):
                    continue
                if not in_window(rec.get("timestamp"), since, until):
                    continue
                uid = rec.get("uuid") or rec.get("requestId")
                if uid:
                    if uid in seen:
                        continue
                    seen.add(uid)
                add_turn(by_key[(MAIN, msg["model"], rec.get("effort"))], rec, msg)
                sessions[MAIN].add(rec.get("sessionId") or path)
    for path in glob.glob(os.path.join(HOME, ".claude/projects/*/*/subagents/agent-*.jsonl")):
        agent_id = os.path.basename(path)[len("agent-"):-len(".jsonl")]
        atype = agent_type.get(agent_id, "unknown")
        with open(path, errors="replace") as fh:
            for line in fh:
                try:
                    rec = json.loads(line)
                except ValueError:
                    continue
                if not in_window(rec.get("timestamp"), since, until):
                    continue
                msg = rec.get("message")
                if not isinstance(msg, dict) or not msg.get("model"):
                    continue
                add_turn(by_key[(atype, msg["model"], rec.get("effort"))], rec, msg)
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


def write_csv(path, header, rows):
    """Write to `path`, or to stdout when path is "-"."""
    fh = sys.stdout if path == "-" else open(path, "w", newline="")
    try:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerows(rows)
    finally:
        if fh is not sys.stdout:
            fh.close()
            print(f"wrote {len(rows)} rows to {path}")


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
    if args.csv:
        write_csv(args.csv,
                  ["window_since", "window_until", "agent", "model", "effort", "runs",
                   "turns", "input_tokens", "cache_write_tokens", "cache_read_tokens",
                   "output_tokens", "usd"],
                  [[since or "", until or "", a, m, e or "", runs.get(a, 0), u["turns"],
                    u["input"], u["cache_write"], u["cache_read"], u["output"],
                    round(cost(m, u), 4)] for (a, m, e), u in sorted(rows.items())])
        return
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
    for atype in sorted({k[0] for k in rows}, key=lambda a: (a != MAIN, a)):
        sub = {k: v for k, v in rows.items() if k[0] == atype}
        atotal = sum(cost(m, u) for (_, m, _), u in sub.items())
        total += atotal
        n = runs.get(atype, 0)
        label = "sessions" if atype == MAIN else "runs"
        per = f", ${atotal / n:.4f}/{label[:-1]}" if n else ""
        print(f"{atype}  ({n} {label}, ${atotal:.2f}{per})")
        for (_, model, effort), u in sorted(sub.items(), key=lambda kv: -cost(kv[0][1], kv[1])):
            print(f"    {model:<20} effort={str(effort):<7} turns={u['turns']:<6} "
                  f"in={u['input']:<8} cw={u['cache_write']:<10} cr={u['cache_read']:<11} "
                  f"out={u['output']:<8} ${cost(model, u):.2f}")
        print()
    main_total = sum(cost(m, u) for (a, m, _), u in rows.items() if a == MAIN)
    print(f"TOTAL ${total:.2f}  (main-session ${main_total:.2f}, "
          f"subagents ${total - main_total:.2f}, "
          f"{(total - main_total) / total * 100 if total else 0:.0f}% subagent)")
    if UNPRICED:
        print(f"WARNING: no price for {sorted(UNPRICED)} - counted as $0")



# --- Per-tool / per-skill attribution ------------------------------------

CHARS_PER_TOKEN = 4  # only used to bound attribution, never to report a total
OVERHEAD = "(system prompt, tools, unattributed)"
CONVERSATION = "(conversation text: prompts and assistant output)"


def block_chars(block):
    if not isinstance(block, dict):
        return len(str(block))
    if block.get("type") == "text":
        return len(block.get("text") or "")
    content = block.get("content")
    if isinstance(content, str):
        return len(content)
    return len(json.dumps(content or block, default=str))


def walk_transcript(path):
    """Yield (assistant_record, message, pending) per assistant turn.

    `pending` is the list of (label, chars) that entered context since the
    previous assistant turn: tool results labeled by their tool (Skill calls by
    skill name, including the SKILL.md body that arrives as the next user text),
    and conversation text.
    """
    tool_names, pending, out, last_skill = {}, [], [], None
    with open(path, errors="replace") as fh:
        for line in fh:
            try:
                rec = json.loads(line)
            except ValueError:
                continue
            msg = rec.get("message")
            if not isinstance(msg, dict):
                continue
            content = msg.get("content")
            if msg.get("role") == "assistant" and msg.get("model"):
                out.append((rec, msg, pending))
                pending = []
                for block in content or []:
                    if isinstance(block, dict) and block.get("type") == "tool_use":
                        name = block.get("name")
                        if name == "Skill":
                            name = "Skill:" + str((block.get("input") or {}).get("skill"))
                        tool_names[block.get("id")] = name
                pending.append((CONVERSATION, sum(block_chars(b) for b in content or [])))
                continue
            if isinstance(content, str):
                pending.append((CONVERSATION, len(content)))
                continue
            for block in content or []:
                if not isinstance(block, dict):
                    continue
                if block.get("type") == "tool_result":
                    label = tool_names.get(block.get("tool_use_id"), "(unknown tool)")
                    pending.append((label, block_chars(block)))
                    last_skill = label if label.startswith("Skill:") else None
                elif block.get("type") == "text":
                    # A skill's body arrives as the user text right after its result.
                    label = last_skill or CONVERSATION
                    pending.append((label, block_chars(block)))
                    last_skill = None
    return out


def attribute(path, since, until, rows, calls, measured):
    """Estimate the context tokens each tool and skill contributes.

    Attribution is character-based (`CHARS_PER_TOKEN`), not billed tokens: a
    turn's `cache_creation_input_tokens` re-counts the whole prefix whenever the
    cache TTL lapses, so billed input cannot be split across the items that
    caused it. Measured totals are tracked alongside so the estimate's coverage
    is visible in the footer.
    """
    turns = walk_transcript(path)
    total_turns = len(turns)
    for i, (rec, msg, pending) in enumerate(turns):
        if not in_window(rec.get("timestamp"), since, until):
            continue
        u = msg.get("usage") or {}
        model, effort = msg["model"], rec.get("effort")
        measured["new"] += u.get("input_tokens", 0) + u.get("cache_creation_input_tokens", 0)
        measured["cache_read"] += u.get("cache_read_input_tokens", 0)
        measured["output"] += u.get("output_tokens", 0)
        remaining = total_turns - i - 1
        for label, chars in pending:
            if not chars:
                continue
            tok = chars / CHARS_PER_TOKEN
            agg = rows[(label, model, effort)]
            agg["added"] += tok
            agg["carry"] += tok * remaining
        for block in msg.get("content") or []:
            if isinstance(block, dict) and block.get("type") == "tool_use":
                name = block.get("name")
                if name == "Skill":
                    name = "Skill:" + str((block.get("input") or {}).get("skill"))
                calls[(name, model, effort)] += 1


def new_attr():
    return {"added": 0.0, "carry": 0.0}


def attributed_cost(model, agg):
    """Write the tokens in once, then re-read them on every later turn."""
    inp = PRICES.get(normalize(model), (0.0, 0.0))[0]
    return (agg["added"] * 1.25 * inp + agg["carry"] * 0.10 * inp) / 1_000_000


def kind_of(label):
    if label.startswith("Skill:"):
        return "skill"
    if label.startswith("mcp__"):
        return "mcp-tool"
    if label.startswith("("):
        return "non-tool"
    return "tool"


def cmd_tools(args):
    since, until = resolve(args.since), resolve(args.until)
    rows = collections.defaultdict(new_attr)
    calls = collections.Counter()
    measured = collections.Counter()
    paths = glob.glob(os.path.join(HOME, ".claude/projects/*/*.jsonl"))
    if not args.main_only:
        paths += glob.glob(os.path.join(HOME, ".claude/projects/*/*/subagents/agent-*.jsonl"))
    if args.project:
        paths = [p for p in paths if args.project in p]
    if args.session:
        paths = [p for p in paths if args.session in p]
    for path in paths:
        attribute(path, since, until, rows, calls, measured)
    by_label = collections.defaultdict(new_attr)
    label_models = collections.defaultdict(lambda: collections.defaultdict(new_attr))
    for (label, model, effort), agg in rows.items():
        for k in ("added", "carry"):
            by_label[label][k] += agg[k]
            label_models[label][model][k] += agg[k]
    label_calls = collections.Counter()
    for (name, _, _), n in calls.items():
        label_calls[name] += n
    if args.csv:
        write_csv(args.csv,
                  ["window_since", "window_until", "label", "kind", "model", "effort",
                   "calls", "added_tokens", "carry_tokens", "usd"],
                  [[since or "", until or "", l, kind_of(l), m, e or "",
                    calls.get((l, m, e), 0), round(a["added"]), round(a["carry"]),
                    round(attributed_cost(m, a), 4)]
                   for (l, m, e), a in sorted(rows.items())])
        return
    if args.json:
        print(json.dumps({"since": since, "until": until, "rows": [
            {"label": l, "model": m, "effort": e, "added_tokens": round(a["added"]),
             "carry_tokens": round(a["carry"]), "usd": round(attributed_cost(m, a), 2)}
            for (l, m, e), a in sorted(rows.items())],
            "calls": {f"{n}|{m}|{e}": c for (n, m, e), c in sorted(calls.items())}}, indent=2))
        return
    print(f"window: {since or 'all time'} -> {until or 'now'}")
    print("added = tokens the item put into context; carry = those tokens re-read on later turns\n")
    order = sorted(by_label, key=lambda l: -sum(
        attributed_cost(m, a) for m, a in label_models[l].items()))
    grand = 0.0
    for label in order:
        usd = sum(attributed_cost(m, a) for m, a in label_models[label].items())
        grand += usd
        n = label_calls.get(label)
        per = f", {usd / n:.3f}/call" if n else ""
        print(f"{label:<45} calls={n or '-':<6} added={by_label[label]['added']:>12,.0f} "
              f"carry={by_label[label]['carry']:>14,.0f}  ${usd:.2f}{per}")
        if args.by_model:
            for model, agg in sorted(label_models[label].items(),
                                     key=lambda kv: -attributed_cost(kv[0], kv[1])):
                print(f"    {model:<24} added={agg['added']:>12,.0f} "
                      f"carry={agg['carry']:>14,.0f}  ${attributed_cost(model, agg):.2f}")
    attributed = sum(a["added"] for a in by_label.values())
    print(f"\nTOTAL ${grand:.2f} over {attributed:,.0f} estimated context tokens")
    print(f"measured in the same window: {measured['new']:,} new input tokens, "
          f"{measured['cache_read']:,} cache reads, {measured['output']:,} output")
    print(f"estimate covers {attributed / measured['new'] * 100 if measured['new'] else 0:.0f}% "
          f"of measured new input; the rest is system prompt, tool schemas, and cache "
          f"re-creation after a TTL lapse, none of which belongs to a single tool")
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
    r.add_argument("--csv", metavar="PATH", help='write CSV to PATH ("-" for stdout)')
    r.set_defaults(func=cmd_report)
    t = sub.add_parser("tools", help="attribute context tokens to tools and skills")
    t.add_argument("--since")
    t.add_argument("--until")
    t.add_argument("--project", help="substring match on the project directory")
    t.add_argument("--by-model", action="store_true", help="split each row by model")
    t.add_argument("--main-only", action="store_true", help="skip subagent transcripts")
    t.add_argument("--session", help="substring match on one session transcript filename")
    t.add_argument("--json", action="store_true")
    t.add_argument("--csv", metavar="PATH", help='write CSV to PATH ("-" for stdout)')
    t.set_defaults(func=cmd_tools)
    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
