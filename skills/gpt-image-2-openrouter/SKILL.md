---
name: gpt-image-2-openrouter
description: Generate images via OpenRouter using the openai/gpt-5.4-image-2 model. Trigger whenever the user asks to "generate an image", "create a picture", "make an illustration", "draw", or any text-to-image request — especially if they mention OpenRouter, gpt-5.4-image, or want an alternative to nano-banana / Gemini image generation. Use this skill even if the user does not explicitly name the model.
homepage: https://openrouter.ai/
metadata:
  {
    "openclaw":
      {
        "emoji": "🎨",
        "requires": { "bins": ["uv"], "env": ["OPENROUTER_API_KEY"] },
        "primaryEnv": "OPENROUTER_API_KEY"
      }
  }
---

# GPT Image (OpenRouter)

Use the bundled script to generate an image from a text prompt via OpenRouter's `openai/gpt-5.4-image-2`.

Generate

```bash
uv run {baseDir}/scripts/generate_image.py --prompt "your image description" --filename "output.png"
```

API key

- `OPENROUTER_API_KEY` env var
- Or pass `--api-key` / `-k` on the command line

Notes

- Text-to-image only. For editing or multi-image composition use the `nano-banana-pro` skill instead.
- Use timestamped filenames: `yyyy-mm-dd-hh-mm-ss-name.png`.
- The script prints `Image saved: <path>` and a `MEDIA: <path>` line so the path is easy to surface to the user.
- Do not read the image back; report the saved path only.
