# ABOUTME: Tests for the dev-jawn /cost script: one named test per #134 acceptance criterion plus units.
# ABOUTME: Fixture transcript trees are built per test with transcript_builder; nothing touches ~/.claude.
from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import json  # noqa: E402
import subprocess  # noqa: E402
import tempfile  # noqa: E402
import unittest  # noqa: E402

import cost  # noqa: E402
import transcripts  # noqa: E402
import weights  # noqa: E402
from transcript_builder import TranscriptTree  # noqa: E402

ALL = cost.Scope.all_dirs()
SHAPES = Path(__file__).resolve().parent / "fixtures" / "record_shapes.jsonl"


COST_PY = Path(__file__).resolve().parent.parent / "cost.py"
FIXTURE_CWD = "/work/repo"


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
        s.skill("dev-jawn:spec", "#7")
        s.turn("claude-opus-5-5", 1000, 0, 0)
        s.clear()
        s.turn("claude-opus-5-5", 200, 0, 0)
        s.spawn("toolu_A", "Explore")
        s.subagent("a1", "general-purpose", "Explore", "toolu_A").turn("claude-sonnet-5-5", 300, 0, 0)  # 150
        direct = 1000 + 200 + 150

        report = cost.session_report("s1", self.tree.root)

        rows = dict(report.rows)
        self.assertEqual(rows, {"#7": 1000, "unattributed": 350})
        self.assertEqual(sum(rows.values()), direct)
        self.assertEqual(report.total, direct)

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
