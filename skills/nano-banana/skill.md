---
name: nano-banana
description: "Generate images using Google's Nano Banana 2 model. Invoke with /nano-banana followed by a prompt description, or when the user asks to generate, create, or make an image."
---

# Nano Banana — Image Generation Skill

Generate images using Google's Nano Banana 2 (Gemini 3.1 Flash Image) model.

## Project Config Detection

On every invocation, check for `.nano-banana.json` in the current working directory.

- **If found**: Load the config and apply it during prompt enhancement (see "Using the Medium Config" below).
- **If not found**: Ask the user — "No `.nano-banana.json` found in this project. Want me to set one up, or generate without a style profile?" If they want setup, follow the "Setup Flow" below.

## Setup Flow

When the user wants to create a `.nano-banana.json` for their project, interview them with these questions:

1. **What kind of content is this for?** (personal blog, company blog, food blog, product marketing, social media, documentation, etc.)
2. **Describe the visual feel you're going for.** Offer starter examples if they're unsure:
   - *Personal blog*: "Warm, authentic, editorial. Natural lighting, shallow depth of field, Fujifilm color science."
   - *Company blog*: "Clean, professional, modern. Studio softbox lighting, crisp focus, minimal backgrounds."
   - *Food blog*: "Inviting overhead or 45° shots. Natural window light, rustic surfaces, rich warm tones."
   - *Product marketing*: "Polished, high-contrast studio shots. Dramatic lighting, clean backgrounds, premium feel."
   - *Social media*: "Bold, eye-catching, vibrant saturation. Strong composition with room for text overlay."
3. **Default aspect ratio?** Suggest based on their medium (blog hero → 16:9, social → 1:1, Pinterest → 9:16, etc.)
4. **Default resolution?** (0.5K, 1K, 2K, 4K — suggest 2K as a good default)
5. **Any recurring visual elements?** Things that should appear consistently (brand colors, specific props, surface textures, typography style).
6. **Camera and lens preferences?** (e.g., "shot on Fujifilm" for warm tones, "macro lens" for detail, "GoPro" for action)

After the interview, generate the `.nano-banana.json` and write it to the project root. The schema:

```json
{
  "medium": "<medium name>",
  "defaults": {
    "aspect_ratio": "<ratio>",
    "resolution": "<resolution>"
  },
  "style": {
    "description": "<one-line summary of the visual identity>",
    "lighting": "<lighting direction>",
    "color_grading": "<color/film stock direction>",
    "composition": "<default composition approach>",
    "camera": "<camera and lens defaults>",
    "materiality": "<textures, surfaces, materials>"
  },
  "recurring_elements": [
    "<element 1>",
    "<element 2>"
  ]
}
```

See `config.example.json` in the skill directory for a complete example.

## Usage

The user provides an image description. Your job is to:

1. **Enhance the prompt** using the Nano Banana prompting framework, applying the medium config if available (see below).

2. **Show the user the enhanced prompt** so they can approve or tweak it before generating.

3. **Run the generation script** using the Bash tool:
   ```bash
   uv run ~/.claude/skills/nano-banana/generate.py "the enhanced prompt" -o output-filename.png
   ```

   Optional flags (override config defaults):
   - `-i` / `--input`: input image for editing/refinement (enables image-to-image mode)
   - `-r` / `--resolution`: `0.5K`, `1K`, `2K` (default), `4K`
   - `-a` / `--aspect-ratio`: `1:1`, `2:3`, `3:2`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `21:9`, etc.
   - `-o` / `--output`: output file path (default: `generated-image.png`)
   - `-c` / `--config`: path to config file (default: `./.nano-banana.json`)

   When a `.nano-banana.json` exists, the script reads defaults from it automatically. CLI flags override config values.

4. **Show the result** to the user by reading the generated image file with the Read tool.

5. **Iterate** — when the user wants changes, ask: **"Refine the existing image, or start from scratch?"**

   - **Refine existing**: Pass the previously generated image as input with `-i` so the model uses it as a reference. Adjust the prompt to describe only what should change (e.g., "Make the background warmer" or "Add a coffee cup to the left side").
     ```bash
     uv run ~/.claude/skills/nano-banana/generate.py "Make the background warmer and add soft bokeh" -i previous-output.png -o refined-output.png
     ```
   - **Start from scratch**: Run without `-i`, using a revised prompt from the ground up.

## Using the Medium Config for Prompt Enhancement

When a `.nano-banana.json` is loaded, weave its style properties into the `[Style]` segment of the prompting framework:

**Formula**: `[Subject] + [Action] + [Location/context] + [Composition] + [Style]`

How each config field maps to the prompt:

| Config field | Prompt segment | Example |
|---|---|---|
| `style.composition` | `[Composition]` | "Overhead flat-lay" |
| `style.lighting` | `[Style]` lighting clause | "Soft natural window light, diffused" |
| `style.color_grading` | `[Style]` color clause | "Warm, rich tones" |
| `style.camera` | `[Style]` camera clause | "Shot on Fujifilm X-T5, 56mm f/1.2" |
| `style.materiality` | `[Location/context]` surfaces | "On rustic wood table with linen" |
| `recurring_elements` | Append to scene description | "Fresh herbs as garnish props" |

The user's specific request always takes priority — the config provides defaults that fill in gaps the user didn't specify.

## Prompting Tips (from the Nano Banana guide)

- Be specific: concrete details on subject, lighting, composition
- Use positive framing: describe what you want, not what you don't want (e.g. "empty street" instead of "no cars")
- Control the camera: use photographic terms like "low angle", "aerial view", "f/1.8"
- Define lighting: "three-point softbox", "golden hour backlighting", "chiaroscuro"
- Specify materiality: textures, fabrics, surfaces
- Choose film stock/color grading: "1980s color film", "muted teal tones"
- Use quotes for any text that should appear in the image
- Name specific cameras for visual DNA: "shot on Fujifilm", "GoPro fisheye"

## Requirements

- `GOOGLE_API_KEY` environment variable must be set
- Uses `uv run` with inline dependencies (no pre-install needed)
