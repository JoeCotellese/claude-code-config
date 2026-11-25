# ABOUTME: Tests for the dev-jawn /cost script: one named test per #134 acceptance criterion plus units.
# ABOUTME: Fixture transcript trees are built per test with transcript_builder; nothing touches ~/.claude.
from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import json  # noqa: E402
import tempfile  # noqa: E402
import unittest  # noqa: E402

import cost  # noqa: E402
import transcripts  # noqa: E402
import weights  # noqa: E402
from transcript_builder import TranscriptTree  # noqa: E402

ALL = cost.Scope.all_dirs()
SHAPES = Path(__file__).resolve().parent / "fixtures" / "record_shapes.jsonl"


def offline(n):
    return None


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
