#!/usr/bin/env bash
# Transcribe Apple Voice Memo .m4a via mlx-whisper.
# Usage: transcribe-voice.sh <input.m4a> <output_dir>
# Outputs: <output_dir>/<basename>.txt

set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <input.m4a> <output_dir>" >&2
  exit 64
fi

INPUT="$1"
OUTDIR="$2"
MODEL="${MLX_WHISPER_MODEL:-mlx-community/whisper-large-v3-mlx}"

if [[ ! -f "$INPUT" ]]; then
  echo "Input not found: $INPUT" >&2
  exit 66
fi

mkdir -p "$OUTDIR"

if ! command -v mlx_whisper >/dev/null 2>&1; then
  echo "mlx_whisper not on PATH. Install with: uv tool install mlx-whisper" >&2
  exit 69
fi

mlx_whisper \
  --model "$MODEL" \
  --output-dir "$OUTDIR" \
  --output-format txt \
  --language en \
  --word-timestamps False \
  --condition-on-previous-text False \
  "$INPUT"

BASENAME="$(basename "$INPUT" .m4a)"
echo "$OUTDIR/$BASENAME.txt"
