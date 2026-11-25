# ABOUTME: Tests for the dev-jawn /cost script: one named test per #134 acceptance criterion plus units.
# ABOUTME: Fixture transcript trees are built per test with transcript_builder; nothing touches ~/.claude.
from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import hashlib  # noqa: E402
import json  # noqa: E402
import shutil  # noqa: E402
import subprocess  # noqa: E402
import tempfile  # noqa: E402
import unittest  # noqa: E402
from datetime import datetime, timezone  # noqa: E402

import attribution  # noqa: E402
import cost  # noqa: E402
import outcome  # noqa: E402
import transcripts  # noqa: E402
import weights  # noqa: E402
from outcome import GitHubState  # noqa: E402
from transcript_builder import TranscriptTree  # noqa: E402

ALL = cost.Scope.all_dirs()
SHAPES = Path(__file__).resolve().parent / "fixtures" / "record_shapes.jsonl"


COST_PY = Path(__file__).resolve().parent.parent / "cost.py"
PLUGIN_JSON = Path(__file__).resolve().parents[3] / ".claude-plugin" / "plugin.json"
FIXTURE_CWD = "/work/repo"
OFFLINE_WARNING = "cost: offline; outcome unknown\n"


def tree_digest(root) -> dict:
    return {str(p): (p.stat().st_mtime_ns, hashlib.sha256(p.read_bytes()).hexdigest())
            for p in sorted(Path(root).rglob("*")) if p.is_file()}


def offline(_n):
    return None


def run_cli(projects_dir, repo, *argv):
    """Run cost.py end to end, scoped to the fixture tree only and never calling gh."""
    return subprocess.run(
        [sys.executable, str(COST_PY), *argv, "--projects-dir", str(projects_dir), "--repo", str(repo),
         "--project", FIXTURE_CWD + "*", "--offline"],
        capture_output=True, text=True, timeout=60)


class CostTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.tree = TranscriptTree(self.tmp / "projects")

    def tearDown(self):
        self._tmp.cleanup()

    def issue(self, n, **kwargs):
        kwargs.setdefault("scope", ALL)
        kwargs.setdefault("github", offline)
        return cost.issue_report(n, self.tree.root, **kwargs)

    def row(self, report, phase):
        rows = [r for r in report.phases if r.phase == phase]
        self.assertEqual(len(rows), 1, f"expected one {phase} row, got {[r.phase for r in report.phases]}")
        return rows[0]

    # --- AC7 -------------------------------------------------------------
    def test_ac07_weighting_peak_context_and_share_over_200k(self):
        s = self.tree.session("s1")
        s.skill("dev-jawn:spec", "#7")
        s.turn("claude-opus-5-5", 100, 10, 1000, cw5m=200)    # 100 + 50 + 50 + 250 = 450, ctx 1,300
        s.turn("claude-sonnet-5-5", 100, 10, 1000, cw1h=100)  # 50 + 25 + 25 + 100 = 200, ctx 1,200
        s.turn("claude-opus-5-5", 1000, 0, 249000)            # 1,000 + 12,450 = 13,450, ctx 250,000
        s.skill("dev-jawn:architecture", "#7")
        # Two message iterations of 150,010 context each: the top-level sum (300,020) is not a context.
        s.turn("claude-opus-5-5", 0, 0, 0, iterations=[(10, 5, 150000, 0, 0), (10, 5, 150000, 0, 0)])
        # 2 x (10 + 25 + 7,500) = 15,070
        s.turn("claude-opus-5-5", 2, 1, 100, advisor=("claude-fable-5-2", 210000, 100))
        # executor 2 + 5 + 5 = 12, ctx 102; advisor 420,000 + 1,000 = 421,000 at Fable weight, ctx 210,000

        report = self.issue(7)

        spec = self.row(report, "spec")
        self.assertEqual(spec.weighted, 450 + 200 + 13450)
        self.assertEqual(spec.peak_context, 250000)
        self.assertEqual(spec.share_over_200k, Fraction(13450, 450 + 200 + 13450))
        self.assertEqual(spec.models, {"claude-opus-5-5": 450 + 13450, "claude-sonnet-5-5": 200})

        arch = self.row(report, "architecture")
        self.assertEqual(arch.weighted, 15070 + 12 + 421000)
        self.assertEqual(arch.advisor, 421000)
        self.assertEqual(arch.peak_context, 210000)
        self.assertEqual(arch.share_over_200k, Fraction(421000, 15070 + 12 + 421000))
        self.assertEqual(report.totals.weighted, 450 + 200 + 13450 + 15070 + 12 + 421000)

    # --- AC8 -------------------------------------------------------------
    def test_ac08_unknown_model_warns_and_uses_opus_weight(self):
        s = self.tree.session("s1")
        s.skill("dev-jawn:dod", "#7")
        s.turn("claude-mystery-9", 100, 10, 0)  # Opus weights: 100 + 50 = 150

        report = self.issue(7)

        self.assertEqual(report.totals.weighted, 150)
        self.assertEqual(len(report.warnings), 1)
        self.assertIn("claude-mystery-9", report.warnings[0])
        self.assertIn("claude-mystery-9", cost.report.render(cost.report.issue_table(report)))

    # --- AC9 -------------------------------------------------------------
    def test_ac09_malformed_usage_record_exits_nonzero_with_file_and_line(self):
        cases = {
            "missing requestId": json.dumps({"type": "assistant", "timestamp": "2026-11-01T00:10:00.000Z",
                                             "message": {"id": "msg_x", "model": "claude-opus-5-5",
                                                         "usage": {"input_tokens": 1, "output_tokens": 1,
                                                                   "cache_read_input_tokens": 0,
                                                                   "cache_creation_input_tokens": 0}}}),
            "usage field not an integer": json.dumps({"type": "assistant", "requestId": "req_x",
                                                      "message": {"id": "msg_x", "model": "claude-opus-5-5",
                                                                  "usage": {"input_tokens": "1", "output_tokens": 1,
                                                                            "cache_read_input_tokens": 0,
                                                                            "cache_creation_input_tokens": 0}}}),
            "invalid JSON mid-file": '{"type": "assistant", ',
        }
        for name, bad_line in cases.items():
            with self.subTest(name):
                tree = TranscriptTree(self.tmp / name.replace(" ", "-"))
                s = tree.session("s1")
                s.skill("dev-jawn:dod", "#7").turn("claude-opus-5-5", 10, 1, 0)
                s.raw_line(bad_line)
                bad_number = len(s.path.read_text().splitlines())
                s.turn("claude-opus-5-5", 10, 1, 0)

                done = run_cli(tree.root, self.tmp, "#7")

                self.assertEqual(done.returncode, 1)
                self.assertEqual(done.stdout, "")
                self.assertIn(f"{s.path}:{bad_number}:", done.stderr)

    def test_truncated_final_line_without_newline_is_skipped(self):
        s = self.tree.session("s1")
        s.skill("dev-jawn:dod", "#7").turn("claude-opus-5-5", 10, 0, 0)
        s.raw_line('{"type": "assistant", "message": {"id": "msg_live', newline=False)

        self.assertEqual(self.issue(7).totals.weighted, 10)

    # --- AC1 -------------------------------------------------------------
    def test_ac01_bound_session_counts_main_and_subagents_per_phase(self):
        s = self.tree.session("s1")
        s.skill("dev-jawn:spec", "#7")
        s.turn("claude-opus-5-5", 1000, 0, 0)                       # spec main 1,000
        s.spawn("toolu_A", "Draft stories")
        s.subagent("a1", "general-purpose", "Draft stories", "toolu_A").turn("claude-opus-5-5", 2000, 0, 0)
        s.command("dev-jawn:architecture", "#7")
        s.turn("claude-opus-5-5", 300, 0, 0)                        # architecture main 300
        s.spawn("toolu_B", "Architect #7", "dev-jawn:architect")
        s.subagent("a2", "dev-jawn:architect", "Architect #7", "toolu_B").turn("claude-opus-5-5", 4000, 0, 0)

        report = self.issue(7)

        spec, arch = self.row(report, "spec"), self.row(report, "architecture")
        self.assertEqual((spec.main, spec.subagent), (1000, 2000))
        self.assertEqual((arch.main, arch.subagent), (300, 4000))
        self.assertEqual((report.totals.main, report.totals.subagent), (1300, 6000))

    # --- AC2 -------------------------------------------------------------
    def test_ac02_first_binding_backdates_to_session_start(self):
        with self.subTest("bound by /spec filing the issue"):
            tree = TranscriptTree(self.tmp / "filing")
            s = tree.session("s1")
            s.user_text("sea foam please")
            s.turn("claude-opus-5-5", 500, 0, 0)                     # before any skill: pending
            s.skill("dev-jawn:spec", "sea foam")                     # no #N, branch main: still pending
            s.turn("claude-opus-5-5", 700, 0, 0)
            s.filing("https://github.com/o/r/issues/7")              # binds #7 in spec
            s.turn("claude-opus-5-5", 100, 0, 0)

            report = cost.issue_report(7, tree.root, scope=ALL, github=offline)

            self.assertEqual([r.phase for r in report.phases], ["spec"])
            self.assertEqual(report.totals.weighted, 500 + 700 + 100)
        with self.subTest("bound by a skill invoked with #N"):
            tree = TranscriptTree(self.tmp / "skill")
            s = tree.session("s1")
            s.turn("claude-opus-5-5", 500, 0, 0)
            s.command("dev-jawn:ready", "#7")
            s.turn("claude-opus-5-5", 100, 0, 0)

            report = cost.issue_report(7, tree.root, scope=ALL, github=offline)

            self.assertEqual([r.phase for r in report.phases], ["ready"])
            self.assertEqual(report.totals.weighted, 600)

    # --- AC3 -------------------------------------------------------------
    def test_ac03_nested_subagents_roll_up_to_spawning_phase(self):
        s = self.tree.session("s1")
        s.skill("dev-jawn:implement", "#7")
        s.turn("claude-opus-5-5", 10, 0, 0)
        s.spawn("toolu_A", "Look around")
        a1 = s.subagent("a1", "general-purpose", "Look around", "toolu_A")
        a1.turn("claude-opus-5-5", 100, 0, 0)
        a1.spawn("toolu_B", "Dig deeper")
        a2 = a1.subagent("a2", "general-purpose", "Dig deeper", "toolu_B")
        a2.turn("claude-opus-5-5", 1000, 0, 0)
        a2.spawn("toolu_C", "Deepest")
        a2.subagent("a3", "general-purpose", "Deepest", "toolu_C").turn("claude-opus-5-5", 10000, 0, 0)
        s.skill("dev-jawn:dod", "#7")                                # phase changes after the spawn
        s.turn("claude-opus-5-5", 5, 0, 0)

        report = self.issue(7)

        build = self.row(report, "build")
        self.assertEqual((build.main, build.subagent), (10, 100 + 1000 + 10000))
        self.assertEqual(self.row(report, "dod").weighted, 5)

    # --- AC4 -------------------------------------------------------------
    def test_ac04_two_issue_spawn_splits_evenly_and_is_marked_shared(self):
        s = self.tree.session("s1")
        s.skill("dev-jawn:spec", "#7")
        s.spawn("toolu_A", "Spec pair #7 + #8")
        pair = s.subagent("a1", "general-purpose", "Spec pair #7 + #8", "toolu_A")
        pair.turn("claude-opus-5-5", 1001, 0, 0)                     # half each: 1001/2
        pair.spawn("toolu_B", "Architect #8 crest", "dev-jawn:architect")
        pair.subagent("a2", "dev-jawn:architect", "Architect #8 crest", "toolu_B").turn("claude-opus-5-5", 600, 0, 0)

        seven, eight = self.issue(7), self.issue(8)

        for report in (seven, eight):
            spec = self.row(report, "spec")
            self.assertEqual(spec.weighted, Fraction(1001, 2))
            self.assertEqual(spec.shared, Fraction(1001, 2))
        self.assertEqual(self.row(eight, "architecture").weighted, 600)  # one #N replaces the pair
        self.assertNotIn("architecture", [r.phase for r in seven.phases])

    # --- AC5 -------------------------------------------------------------
    def test_ac05_unbound_tokens_land_on_unattributed_and_lines_sum(self):
        s = self.tree.session("s1")
        s.turn("claude-opus-5-5", 40, 0, 0)                          # a segment that never binds
        s.clear()
        s.skill("dev-jawn:spec", "#7")                               # binding backdates to this /clear only
        s.turn("claude-opus-5-5", 1000, 0, 0)
        s.clear()
        s.turn("claude-opus-5-5", 200, 0, 0)
        s.spawn("toolu_A", "Explore")
        s.subagent("a1", "general-purpose", "Explore", "toolu_A").turn("claude-sonnet-5-5", 300, 0, 0)  # 150
        direct = 40 + 1000 + 200 + 150

        report = cost.session_report("s1", self.tree.root)

        rows = dict(report.rows)
        self.assertEqual(rows, {"#7": 1000, "unattributed": 40 + 350})
        self.assertEqual(sum(rows.values()), direct)
        self.assertEqual(report.total, direct)

    # --- AC10 ------------------------------------------------------------
    def test_ac10_session_view_lists_each_issue_and_unattributed(self):
        s = self.tree.session("s1")
        s.skill("dev-jawn:spec", "#7").turn("claude-opus-5-5", 100, 0, 0)
        s.skill("dev-jawn:ready", "#8").turn("claude-opus-5-5", 200, 0, 0)
        other = self.tree.session("s2")
        other.skill("dev-jawn:spec", "#9").turn("claude-opus-5-5", 400, 0, 0)

        report = cost.session_report("s1", self.tree.root)

        self.assertEqual(dict(report.rows), {"#7": 100, "#8": 200, "unattributed": 0})
        self.assertEqual(report.total, 300)

    # --- AC6 -------------------------------------------------------------
    def test_ac06_repeated_phase_reports_attempts_and_rework(self):
        s = self.tree.session("s1")
        s.skill("dev-jawn:spec", "#7").turn("claude-opus-5-5", 10, 0, 0)
        for run, tool_id in enumerate(("toolu_A", "toolu_B")):
            s.skill("dev-jawn:architecture", "#7").turn("claude-opus-5-5", 5, 0, 0)
            s.spawn(tool_id, "Architect #7", "dev-jawn:architect")
            s.subagent(f"a{run}", "dev-jawn:architect", "Architect #7", tool_id).turn("claude-opus-5-5", 100, 0, 0)
        s.command("dev-jawn:dod").turn("claude-opus-5-5", 5, 0, 0)  # no #N: enters dod for the bound #7

        report = self.issue(7)

        arch, spec = self.row(report, "architecture"), self.row(report, "spec")
        self.assertEqual((arch.attempts, arch.rework), (2, True))
        self.assertEqual((spec.attempts, spec.rework), (1, False))
        self.assertEqual(self.row(report, "dod").attempts, 1)
        self.assertTrue(any("architecture" in note and "2" in note
                            for note in cost.report.issue_table(report).notes))

    def test_pair_agent_counts_one_spec_entry_per_issue(self):
        # Real #1118 shape: a "Spec pair" agent spawned from autopilot runs /spec once per issue.
        s = self.tree.session("s1")
        s.skill("dev-jawn:autopilot", "#7").turn("claude-opus-5-5", 10, 0, 0)
        s.spawn("toolu_A", "Spec pair #7 + #8")
        pair = s.subagent("a1", "general-purpose", "Spec pair #7 + #8", "toolu_A")
        pair.skill("dev-jawn:spec", "#7").turn("claude-opus-5-5", 100, 0, 0)
        pair.skill("dev-jawn:spec", "#8").turn("claude-opus-5-5", 100, 0, 0)

        for n in (7, 8):
            with self.subTest(issue=n):
                self.assertEqual(self.row(self.issue(n), "spec").attempts, 1)

    # --- AC11 ------------------------------------------------------------
    def test_ac11_top_pressure_names_agent_with_most_tokens_over_200k(self):
        s = self.tree.session("s1")
        s.skill("dev-jawn:implement", "#7")
        s.spawn("toolu_X", "Builder X")
        x = s.subagent("ax", "general-purpose", "Builder X", "toolu_X")
        x.turn("claude-opus-5-5", 0, 0, 450000)                     # peak 450K, 22,500 over 200K
        s.spawn("toolu_Y", "Builder Y")
        y = s.subagent("ay", "general-purpose", "Builder Y", "toolu_Y")
        for _ in range(3):
            y.turn("claude-opus-5-5", 0, 0, 250000)                 # peak 250K, 3 x 12,500 = 37,500 over

        report = self.issue(7)

        self.assertIn("Builder Y", report.top_pressure.agent)
        self.assertEqual(report.top_pressure.over_200k, 37500)
        self.assertEqual(report.top_pressure.peak_context, 250000)

    # --- AC12 ------------------------------------------------------------
    def test_ac12_outcome_and_dod_round_count(self):
        s = self.tree.session("s1")
        s.skill("dev-jawn:dod", "#7").turn("claude-opus-5-5", 10, 0, 0)
        s.text("DOD VERDICT: #7 status=FAIL route=/implement")
        s.text("**DOD VERDICT: #7 status=PASS route=/submit")
        s.user_text("DOD VERDICT: #7 status=PASS (quoted in a skill body, not a round)")
        states = {
            "merged": GitHubState(merged=True, stage_human=True),
            "open": GitHubState(),
            "stopped": GitHubState(stage_human=True),
        }
        for expected, state in states.items():
            with self.subTest(expected):
                report = self.issue(7, github=lambda n, state=state: state)
                self.assertEqual(report.outcome, expected)
                self.assertEqual(report.dod_rounds, 2)
        ready_pr = GitHubState(stage_human=True, open_ready_pr=True)  # /submit sets stage:human on ready PRs
        self.assertEqual(self.issue(7, github=lambda n: ready_pr).outcome, "open")

    def test_outcome_lookup_reads_gh_json(self):
        replies = {
            "issue": {"labels": [{"name": "stage:human"}], "closedByPullRequestsReferences": []},
            "pr": [{"number": 3, "isDraft": False, "headRefName": "feature/7-thing", "closingIssuesReferences": []}],
        }

        def runner(argv, **_kwargs):
            body = replies["issue"] if argv[1] == "issue" else replies["pr"]
            return subprocess.CompletedProcess(argv, 0, stdout=json.dumps(body), stderr="")

        state = outcome.lookup(7, runner=runner)
        self.assertEqual(state, GitHubState(merged=False, stage_human=True, open_ready_pr=True))

        def failing(argv, **_kwargs):
            return subprocess.CompletedProcess(argv, 1, stdout="", stderr="gh: not logged in")

        self.assertIsNone(outcome.lookup(7, runner=failing))
        self.assertEqual(outcome.outcome(None), "unknown")

    # --- AC16 ------------------------------------------------------------
    def test_ac16_nothing_found_reports_and_exits_zero(self):
        s = self.tree.session("s1", cwd=FIXTURE_CWD)
        s.skill("dev-jawn:spec", "#7").turn("claude-opus-5-5", 10, 0, 0)  # in scope, a different issue

        done = run_cli(self.tree.root, self.tmp, "#999")
        found = run_cli(self.tree.root, self.tmp, "#7")

        self.assertEqual(done.returncode, 0)
        self.assertIn("#999", done.stdout)
        self.assertNotIn("weighted", done.stdout)
        self.assertEqual(done.stderr, OFFLINE_WARNING)
        self.assertIn("weighted", found.stdout)  # the same scope does find #7

    # --- AC13 ------------------------------------------------------------
    def test_ac13_snapshot_written_with_phases_models_version_and_time(self):
        s = self.tree.session("s1", cwd=FIXTURE_CWD)
        s.skill("dev-jawn:spec", "#7").turn("claude-opus-5-5", 1000, 10, 0)  # 1,050
        s.skill("dev-jawn:implement", "#7").turn("claude-sonnet-5-5", 400, 0, 0)  # 200
        repo = self.tmp / "repo"
        repo.mkdir()

        done = run_cli(self.tree.root, repo, "#7", "--snapshot")

        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(done.stderr, OFFLINE_WARNING)
        self.assertTrue(done.stdout.startswith("#7:"))
        data = json.loads((repo / ".dev-jawn" / "cost" / "7.json").read_text())
        expected_keys = {"schema", "issue", "repo", "snapshot_time", "plugin_version", "weight_table", "outcome",
                         "dod_rounds", "sessions", "totals", "phases", "models", "top_pressure", "warnings",
                         "first_activity", "last_activity"}
        self.assertLessEqual(expected_keys, set(data))
        self.assertEqual(data["issue"], 7)
        self.assertEqual([p["phase"] for p in data["phases"]], ["spec", "build"])
        self.assertEqual([p["weighted"] for p in data["phases"]], [1050, 200])
        self.assertEqual(data["totals"]["weighted"], 1250)
        self.assertEqual(data["models"]["claude-opus-5-5"]["input"], 1000)
        self.assertEqual(data["models"]["claude-sonnet-5-5"]["weighted"], 200)
        self.assertEqual(data["plugin_version"], json.loads(PLUGIN_JSON.read_text())["version"])
        self.assertEqual(data["sessions"], ["s1"])
        stamp = datetime.strptime(data["snapshot_time"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        self.assertLess(abs((datetime.now(timezone.utc) - stamp).total_seconds()), 120)
        self.assertLessEqual(data["first_activity"], data["last_activity"])

    # --- AC14 ------------------------------------------------------------
    def test_ac14_snapshot_used_when_transcripts_absent(self):
        s = self.tree.session("s1", cwd=FIXTURE_CWD)
        s.skill("dev-jawn:spec", "#7").turn("claude-opus-5-5", 12345, 0, 0)
        repo = self.tmp / "repo"
        repo.mkdir()
        run_cli(self.tree.root, repo, "#7", "--snapshot")
        taken = json.loads((repo / ".dev-jawn" / "cost" / "7.json").read_text())["snapshot_time"]
        shutil.rmtree(self.tree.root)
        self.tree.root.mkdir()

        done = run_cli(self.tree.root, repo, "#7")
        summary = run_cli(self.tree.root, repo, "#7", "--summary")

        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertIn(taken, done.stdout)
        self.assertIn("snapshot", done.stdout)
        self.assertIn("12,345", done.stdout)
        self.assertEqual(summary.stdout.count("\n"), 1)
        self.assertTrue(summary.stdout.startswith("#7: 12,345 "))

    # --- units: phase mapping, scope, read-only ---------------------------
    def test_description_and_agent_type_map_to_phases(self):
        cases = {
            ("general-purpose", "Build #1118 breakers to ready PR"): "build",
            ("general-purpose", "Implement AC3"): "build",
            ("general-purpose", "Architect #1119 crest foam"): "architecture",
            ("general-purpose", "Spec pair #1118 + #1119"): "spec",
            ("general-purpose", "Special handling"): None,
            ("general-purpose", "Review lens: tests"): "submit",
            ("general-purpose", "/code-review high"): "submit",
            ("general-purpose", "DoD run"): "dod",
            ("general-purpose", "Ready gate #7"): "ready",
            ("general-purpose", "Design critic pass 2"): "ui-design",
            ("general-purpose", "Rewrite #1118 acceptance tests"): None,
            ("dev-jawn:architect", "anything"): "architecture",
            ("dev-jawn:test-adequacy-reviewer", "anything"): "submit",
        }
        for (agent_type, description), phase in cases.items():
            with self.subTest(description):
                self.assertEqual(attribution.phase_for_agent(agent_type, description), phase)

    def test_scope_keeps_worktrees_and_deleted_worktrees_of_this_repo_only(self):
        main_repo = self.tmp / "proj"
        git = ["git", "-c", "core.hooksPath=/dev/null", "-c", "user.name=t", "-c", "user.email=t@example.com"]
        subprocess.run(git + ["init", "-q", str(main_repo)], check=True, capture_output=True)
        subprocess.run(git + ["-C", str(main_repo), "commit", "-q", "--allow-empty", "-m", "init"],
                       check=True, capture_output=True)
        subprocess.run(git + ["-C", str(main_repo), "worktree", "add", "-q", str(self.tmp / "proj-wt")],
                       check=True, capture_output=True)
        root = str(main_repo.resolve())
        scope = cost.Scope.for_repo(main_repo)

        self.assertTrue(scope.includes(root))
        self.assertTrue(scope.includes(root + "/sub/dir"))
        self.assertTrue(scope.includes(str((self.tmp / "proj-wt").resolve())))   # (a) live worktree
        self.assertTrue(scope.includes(root + "-1148"))                           # (b) deleted worktree
        (self.tmp / "proj-other").mkdir()                                         # exists, not a worktree
        self.assertFalse(scope.includes(str((self.tmp / "proj-other").resolve())))
        self.assertFalse(scope.includes("/somewhere/else"))
        self.assertTrue(cost.Scope.for_repo(main_repo, ["/somewhere/*"]).includes("/somewhere/else"))  # (c)

    def test_run_never_writes_to_the_transcript_tree(self):
        s = self.tree.session("s1", cwd=FIXTURE_CWD)
        s.skill("dev-jawn:spec", "#7").turn("claude-opus-5-5", 10, 0, 0)
        s.spawn("toolu_A", "Explore")
        s.subagent("a1", "general-purpose", "Explore", "toolu_A").turn("claude-opus-5-5", 10, 0, 0)
        before = tree_digest(self.tree.root)

        self.issue(7)
        cost.session_report("s1", self.tree.root)
        run_cli(self.tree.root, self.tmp, "#7")

        self.assertEqual(tree_digest(self.tree.root), before)

    # --- units: weights and real-format drift -----------------------------
    def test_model_normalization_strips_1m_marker_and_date_suffix(self):
        self.assertEqual(weights.normalize_model("claude-opus-5-5[1m]"), "claude-opus-5-5")
        self.assertEqual(weights.normalize_model("claude-sonnet-5-5-20261001"), "claude-sonnet-5-5")
        self.assertTrue(weights.is_known("claude-fable-5-2[1m]"))
        self.assertFalse(weights.is_known("claude-mystery-9"))

    def test_builder_records_use_only_keys_real_transcripts_carry(self):
        real = [json.loads(line) for line in SHAPES.read_text().splitlines()]
        by_shape = {r["_shape"]: r for r in real}
        s = self.tree.session("s1")
        s.skill("dev-jawn:spec", "#7").turn("claude-opus-5-5", 1, 1, 1, advisor=("claude-fable-5-2", 1, 1))
        s.command("dev-jawn:dod", "#7").filing("https://github.com/o/r/issues/7")
        built = [json.loads(line) for line in s.path.read_text().splitlines()]
        pairs = [
            (built[0], by_shape["assistant-skill"]),
            (built[1], by_shape["assistant-advisor"]),
            (built[3], by_shape["user-command"]),
            (built[5], by_shape["user-tool-result"]),
        ]
        for mine, theirs in pairs:
            with self.subTest(shape=theirs["_shape"]):
                self.assertLessEqual(set(mine) - {"agentId"}, set(theirs))
                if mine["type"] == "assistant":
                    self.assertLessEqual(set(mine["message"]), set(theirs["message"]))
                    mine_usage, real_usage = mine["message"]["usage"], theirs["message"]["usage"]
                    self.assertLessEqual(set(mine_usage), set(real_usage))
                    for it in mine_usage.get("iterations", []):
                        real_it = next(r for r in real_usage["iterations"] if r["type"] == it["type"])
                        self.assertLessEqual(set(it), set(real_it))
        # The parser reads the scrubbed real records without a format error, advisor iteration included.
        kinds = {t.kind for t in transcripts.parse(SHAPES).turns}
        self.assertIn("advisor_message", kinds)


if __name__ == "__main__":
    unittest.main()
