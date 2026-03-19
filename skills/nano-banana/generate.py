# /// script
# requires-python = ">=3.11"
# dependencies = ["google-genai", "Pillow"]
# ///
"""Generate an image using Google's Nano Banana 2 (Gemini 3.1 Flash Image)."""

import argparse
import io
import json
import sys
from pathlib import Path

from google import genai
from google.genai import types
from PIL import Image

VALID_RESOLUTIONS = ["0.5K", "1K", "2K", "4K"]
VALID_ASPECT_RATIOS = [
    "1:1", "1:4", "1:8", "2:3", "3:2", "3:4",
    "4:1", "4:3", "4:5", "5:4", "8:1", "9:16", "16:9", "21:9",
]


def load_project_config(config_path: Path | None) -> dict:
    """Load .nano-banana.json from the given path or current directory."""
    if config_path:
        path = config_path
    else:
        path = Path.cwd() / ".nano-banana.json"

    if not path.exists():
        return {}

    with path.open() as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(description="Generate an image with Nano Banana 2")
    parser.add_argument("prompt", help="Image generation prompt")
    parser.add_argument("-o", "--output", default="generated-image.png",
                        help="Output file path (default: generated-image.png)")
    parser.add_argument("-r", "--resolution", choices=VALID_RESOLUTIONS,
                        help="Output resolution (default: from config or 2K)")
    parser.add_argument("-a", "--aspect-ratio",
                        help="Aspect ratio (default: from config or 16:9)")
    parser.add_argument("-i", "--input", type=Path,
                        help="Input image for editing/refinement")
    parser.add_argument("-c", "--config", type=Path,
                        help="Path to .nano-banana.json (default: ./.nano-banana.json)")
    parser.add_argument("-w", "--max-width", type=int,
                        help="Max width in px for WebP/JPEG output (default: 1400)")
    parser.add_argument("-q", "--quality", type=int,
                        help="Quality for WebP/JPEG output, 1-100 (default: 85)")
    args = parser.parse_args()

    # Load project config, CLI flags override config defaults
    project_config = load_project_config(args.config)
    defaults = project_config.get("defaults", {})

    resolution = args.resolution or defaults.get("resolution", "2K")
    aspect_ratio = args.aspect_ratio or defaults.get("aspect_ratio", "16:9")

    if resolution not in VALID_RESOLUTIONS:
        print(f"Invalid resolution: {resolution}. Must be one of {VALID_RESOLUTIONS}", file=sys.stderr)
        sys.exit(1)

    if aspect_ratio not in VALID_ASPECT_RATIOS:
        print(f"Invalid aspect ratio: {aspect_ratio}. Must be one of {VALID_ASPECT_RATIOS}", file=sys.stderr)
        sys.exit(1)

    client = genai.Client()

    # Build contents: text-only or text + reference image
    if args.input:
        if not args.input.exists():
            print(f"Input image not found: {args.input}", file=sys.stderr)
            sys.exit(1)
        reference_image = Image.open(args.input)
        contents = [args.prompt, reference_image]
    else:
        contents = args.prompt

    response = client.models.generate_content(
        model="gemini-3.1-flash-image-preview",
        contents=contents,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE", "TEXT"],
            image_config=types.ImageConfig(
                aspect_ratio=aspect_ratio,
                image_size=resolution,
            ),
        ),
    )

    for part in response.candidates[0].content.parts:
        if part.inline_data:
            output_path = Path(args.output)
            suffix = output_path.suffix.lower()

            if suffix in (".webp", ".jpg", ".jpeg"):
                img = Image.open(io.BytesIO(part.inline_data.data))
                max_width = args.max_width or defaults.get("max_width", 1400)
                quality = args.quality or defaults.get("quality", 85)
                if img.width > max_width:
                    scale = max_width / img.width
                    img = img.resize(
                        (max_width, round(img.height * scale)),
                        Image.LANCZOS,
                    )
                save_kwargs = {"quality": quality}
                if suffix == ".webp":
                    save_kwargs["method"] = 6  # best compression
                img.save(output_path, **save_kwargs)
                orig_kb = len(part.inline_data.data) / 1024
                final_kb = output_path.stat().st_size / 1024
                print(f"Image saved to: {output_path.resolve()}")
                print(f"  {img.width}x{img.height}, {final_kb:.0f}KB (from {orig_kb:.0f}KB PNG)")
            else:
                output_path.write_bytes(part.inline_data.data)
                print(f"Image saved to: {output_path.resolve()}")
            return

    # No image returned — print any text response
    for part in response.candidates[0].content.parts:
        if part.text:
            print(f"Model returned text instead of image: {part.text}", file=sys.stderr)

    print("No image was generated.", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
