#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "requests>=2.31",
#   "pillow>=10.0.0",
# ]
# ///
"""
Generate images via OpenRouter using openai/gpt-5.4-image-2.

Usage:
    uv run generate_image.py --prompt "your image description" --filename "output.png" [--api-key KEY]
"""

import argparse
import base64
import os
import sys
from io import BytesIO
from pathlib import Path


OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "openai/gpt-5.4-image-2"


def get_api_key(provided_key: str | None) -> str | None:
    if provided_key:
        return provided_key
    return os.environ.get("OPENROUTER_API_KEY")


def main():
    parser = argparse.ArgumentParser(
        description="Generate images via OpenRouter (openai/gpt-5.4-image-2)"
    )
    parser.add_argument("--prompt", "-p", required=True, help="Image description/prompt")
    parser.add_argument(
        "--filename", "-f", required=True,
        help="Output filename (e.g., sunset-mountains.png)"
    )
    parser.add_argument(
        "--api-key", "-k",
        help="OpenRouter API key (overrides OPENROUTER_API_KEY env var)"
    )

    args = parser.parse_args()

    api_key = get_api_key(args.api_key)
    if not api_key:
        print("Error: No API key provided.", file=sys.stderr)
        print("Please either:", file=sys.stderr)
        print("  1. Provide --api-key argument", file=sys.stderr)
        print("  2. Set OPENROUTER_API_KEY environment variable", file=sys.stderr)
        sys.exit(1)

    import requests
    from PIL import Image as PILImage

    output_path = Path(args.filename)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": args.prompt}],
        "modalities": ["image", "text"],
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-Title": "gpt-image-openrouter",
    }

    print(f"Generating image with {MODEL}...")

    try:
        resp = requests.post(OPENROUTER_URL, json=payload, headers=headers, timeout=180)
    except requests.RequestException as e:
        print(f"Network error contacting OpenRouter: {e}", file=sys.stderr)
        sys.exit(1)

    if resp.status_code != 200:
        print(f"OpenRouter returned HTTP {resp.status_code}: {resp.text}", file=sys.stderr)
        sys.exit(1)

    try:
        data = resp.json()
        message = data["choices"][0]["message"]
        if message.get("content"):
            print(f"Model response: {message['content']}")
        images = message.get("images") or []
        if not images:
            print("Error: response contained no images.", file=sys.stderr)
            print(f"Raw response: {data}", file=sys.stderr)
            sys.exit(1)
        url = images[0]["image_url"]["url"]
    except (KeyError, IndexError, ValueError) as e:
        print(f"Error parsing OpenRouter response: {e}", file=sys.stderr)
        print(f"Raw body: {resp.text}", file=sys.stderr)
        sys.exit(1)

    if url.startswith("data:"):
        try:
            _, b64 = url.split(",", 1)
        except ValueError:
            print(f"Error: malformed data URL: {url[:80]}...", file=sys.stderr)
            sys.exit(1)
        image_bytes = base64.b64decode(b64)
    else:
        try:
            image_bytes = requests.get(url, timeout=60).content
        except requests.RequestException as e:
            print(f"Error downloading image from {url}: {e}", file=sys.stderr)
            sys.exit(1)

    image = PILImage.open(BytesIO(image_bytes))
    if image.mode == "RGBA":
        rgb_image = PILImage.new("RGB", image.size, (255, 255, 255))
        rgb_image.paste(image, mask=image.split()[3])
        rgb_image.save(str(output_path), "PNG")
    elif image.mode == "RGB":
        image.save(str(output_path), "PNG")
    else:
        image.convert("RGB").save(str(output_path), "PNG")

    full_path = output_path.resolve()
    print(f"\nImage saved: {full_path}")
    print(f"MEDIA: {full_path}")


if __name__ == "__main__":
    main()
