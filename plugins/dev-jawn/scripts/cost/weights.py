# ABOUTME: Weight table for /cost: each model's token classes scaled to Opus 5.5 input-token units.
# ABOUTME: weigh() returns an exact Fraction; unknown models fall back to Opus weights and are flagged.
from __future__ import annotations

import re
from fractions import Fraction as F

# Prices from the claude-api skill's model table, cached 2026-11-03. One weighted token is one
# Opus 5.5 input token ($4/MTok). Classes: input, output, cache_read, cache_write_5m (1.25x
# input), cache_write_1h (2x input).
WEIGHT_TABLE_DATE = "2026-11-03"
OPUS = "claude-opus-5-5"
WEIGHTS = {
    "claude-opus-5-5": (F(1), F(5), F(1, 20), F(5, 4), F(2)),
    "claude-sonnet-5-5": (F(1, 2), F(5, 2), F(1, 40), F(5, 8), F(1)),
    "claude-fable-5-2": (F(2), F(10), F(1, 20), F(5, 2), F(4)),
    # The skill gives no Haiku 5.5 cache-read price; 1/400 applies its generic "cache reads cost
    # about 0.1x base input" rule to the $0.10 input price. Inferred, not quoted.
    "claude-haiku-5-5": (F(1, 40), F(1, 8), F(1, 400), F(1, 32), F(1, 20)),
    # $5/$25 per MTok; cache read by the same 0.1x rule.
    "claude-opus-5": (F(5, 4), F(25, 4), F(1, 8), F(25, 16), F(5, 2)),
}

CLASSES = ("input", "output", "cache_read", "cache_write_5m", "cache_write_1h")


def normalize_model(model: str) -> str:
    """Strip the 1M-context marker and a -YYYYMMDD snapshot suffix."""
    model = model.replace("[1m]", "").strip()
    return re.sub(r"-\d{8}$", "", model)


def is_known(model: str) -> bool:
    return normalize_model(model) in WEIGHTS


def weigh(model: str, tokens: dict) -> F:
    """Weighted tokens for one turn. `tokens` has the five CLASSES keys as integers."""
    weights = WEIGHTS.get(normalize_model(model), WEIGHTS[OPUS])
    return sum((w * tokens[c] for w, c in zip(weights, CLASSES)), F(0))
