---
name: nano-banana-2-openrouter
description: Generate text-to-image via OpenRouter using google/gemini-3.1-flash-image-preview (a.k.a. "nano-banana-2"). Trigger on "generate an image", "create a picture", "make an illustration", "draw", or any text-to-image request — especially when the user mentions OpenRouter, Gemini image, nano-banana, or wants a fast Google-hosted alternative to gpt-image-2 / nano-banana-pro. Use even when the user does not name the model.
homepage: https://openrouter.ai/
metadata:
  {
    "openclaw":
      {
        "emoji": "🍌",
        "requires": { "bins": ["uv"], "env": ["OPENROUTER_API_KEY"] },
        "primaryEnv": "OPENROUTER_API_KEY"
      }
  }
---

# Nano-Banana 2 (OpenRouter)

Use the bundled script to generate an image from a text prompt via OpenRouter's `google/gemini-3.1-flash-image-preview`.

## When to use

- Text-to-image generation requested by the user.
- The user mentions OpenRouter, Gemini image, nano-banana, or wants a fast Google-hosted alternative to `gpt-image-2-openrouter`.
- The user wants a cheap or low-latency draft before committing to a heavier model.

## When NOT to use

- Image editing, inpainting, or multi-image composition → use `nano-banana-pro`.
- The user specifically asks for `openai/gpt-5.4-image-2` → use `gpt-image-2-openrouter`.
- Non-image tasks (text generation, classification, embeddings).
- `OPENROUTER_API_KEY` is not set and the user cannot provide one.

## Generate

```bash
uv run {baseDir}/scripts/generate_image.py --prompt "your image description" --filename "output.png"
```

API key

- `OPENROUTER_API_KEY` env var
- Or pass `--api-key` / `-k` on the command line

Optional flags

- `--aspect-ratio` — e.g. `1:1`, `16:9`, `4:3`, `3:4`, `9:16`
- `--image-size` — `1K` | `2K` | `4K` (OpenRouter resolution tier)
- `--quality` — `low` | `medium` | `high` | `auto` (passthrough; Gemini may ignore)
- `--output-format` — `png` | `jpeg` | `webp`
- `--background` — `auto` | `opaque` (passthrough; Gemini may ignore)

Notes

- Text-to-image only. For editing or multi-image composition use the `nano-banana-pro` skill instead. For an OpenAI-hosted alternative use `gpt-image-2-openrouter`.
- Use timestamped filenames: `yyyy-mm-dd-hh-mm-ss-name.png`.
- The script saves raw bytes from the model — alpha channel (RGBA) is preserved if the response contains one.
- The script prints `Image saved: <path>` and a `MEDIA: <path>` line so the path is easy to surface to the user.
- Do not read the image back; report the saved path only.
