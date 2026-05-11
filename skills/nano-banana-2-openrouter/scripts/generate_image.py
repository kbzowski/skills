#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "requests>=2.31",
# ]
# ///
"""
Generate images via OpenRouter using google/gemini-3.1-flash-image-preview (nano-banana-2).

Usage:
    uv run generate_image.py --prompt "your image description" --filename "output.png" [options]
"""

import argparse
import base64
import os
import sys
from pathlib import Path


OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "google/gemini-3.1-flash-image-preview"


def get_api_key(provided_key: str | None) -> str | None:
    if provided_key:
        return provided_key
    return os.environ.get("OPENROUTER_API_KEY")


def main():
    parser = argparse.ArgumentParser(
        description="Generate images via OpenRouter (google/gemini-3.1-flash-image-preview)"
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
    parser.add_argument(
        "--aspect-ratio",
        help='OpenRouter image_config aspect_ratio, e.g. "1:1", "16:9", "4:3", "3:4", "9:16"'
    )
    parser.add_argument(
        "--image-size",
        choices=["1K", "2K", "4K"],
        help="OpenRouter image_config image_size tier"
    )
    parser.add_argument(
        "--quality",
        choices=["low", "medium", "high", "auto"],
        help="image_config quality (passthrough; Gemini may ignore)"
    )
    parser.add_argument(
        "--output-format",
        choices=["png", "jpeg", "webp"],
        help="image_config output format (passthrough)"
    )
    parser.add_argument(
        "--background",
        choices=["auto", "opaque"],
        help="image_config background (passthrough; Gemini may ignore)"
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

    output_path = Path(args.filename)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    image_config: dict = {}
    if args.aspect_ratio:
        image_config["aspect_ratio"] = args.aspect_ratio
    if args.image_size:
        image_config["image_size"] = args.image_size
    if args.quality:
        image_config["quality"] = args.quality
    if args.output_format:
        image_config["output_format"] = args.output_format
    if args.background:
        image_config["background"] = args.background

    payload: dict = {
        "model": MODEL,
        "messages": [{"role": "user", "content": args.prompt}],
        "modalities": ["image", "text"],
    }
    if image_config:
        payload["image_config"] = image_config

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-Title": "nano-banana-2-openrouter",
    }

    print(f"Generating image with {MODEL}...")
    if image_config:
        print(f"image_config: {image_config}")

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

    output_path.write_bytes(image_bytes)

    full_path = output_path.resolve()
    print(f"\nImage saved: {full_path}")
    print(f"MEDIA: {full_path}")


if __name__ == "__main__":
    main()
