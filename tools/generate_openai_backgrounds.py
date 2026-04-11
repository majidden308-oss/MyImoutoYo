import argparse
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


API_URL = "https://api.openai.com/v1/images/generations"
DEFAULT_MODEL = "gpt-image-1"
DEFAULT_OUTPUT_FORMAT = "png"
DEFAULT_BACKGROUND = "opaque"
DEFAULT_QUALITY = "high"
DEFAULT_SIZE = "1536x1024"


def load_manifest(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, list):
        raise ValueError("Manifest must be a JSON array.")
    return data


def make_request(api_key: str, item: dict, model: str, dry_run: bool) -> bytes | None:
    payload = {
        "model": model,
        "prompt": item["prompt"],
        "size": item.get("size", DEFAULT_SIZE),
        "quality": item.get("quality", DEFAULT_QUALITY),
        "output_format": item.get("output_format", DEFAULT_OUTPUT_FORMAT),
        "background": item.get("background", DEFAULT_BACKGROUND),
        "n": 1,
        "response_format": "b64_json",
    }

    if dry_run:
        print(f"[dry-run] Would generate {item['filename']} with size={payload['size']} quality={payload['quality']}")
        return None

    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        API_URL,
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=300) as response:
        result = json.loads(response.read().decode("utf-8"))

    image_b64 = result["data"][0]["b64_json"]
    return base64.b64decode(image_b64)


def save_image(output_dir: Path, filename: str, image_bytes: bytes, overwrite: bool) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / filename
    if path.exists() and not overwrite:
        raise FileExistsError(f"{path} already exists. Use --overwrite to replace it.")
    path.write_bytes(image_bytes)
    return path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate Ren'Py background images with the OpenAI Images API."
    )
    parser.add_argument(
        "--manifest",
        default=str(Path(__file__).with_name("openai_background_manifest.json")),
        help="Path to the JSON manifest describing output files and prompts.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(Path(__file__).resolve().parents[1] / "game" / "images"),
        help="Directory where generated images should be saved.",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help="OpenAI image model to use. Defaults to gpt-image-1.",
    )
    parser.add_argument(
        "--only",
        nargs="*",
        help="Optional list of filenames or scene ids to generate.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing image files.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned generations without calling the API.",
    )
    parser.add_argument(
        "--delay-seconds",
        type=float,
        default=1.0,
        help="Delay between API calls to be gentle on rate limits.",
    )
    return parser.parse_args()


def should_include(item: dict, only: set[str] | None) -> bool:
    if not only:
        return True
    return item["filename"] in only or item["scene_id"] in only


def main() -> int:
    args = parse_args()
    manifest_path = Path(args.manifest)
    output_dir = Path(args.output_dir)
    only = set(args.only or [])

    try:
        manifest = load_manifest(manifest_path)
    except Exception as exc:
        print(f"Failed to load manifest: {exc}", file=sys.stderr)
        return 1

    api_key = os.environ.get("OPENAI_API_KEY")
    if not args.dry_run and not api_key:
        print("OPENAI_API_KEY is not set.", file=sys.stderr)
        return 1

    selected = [item for item in manifest if should_include(item, only if only else None)]
    if not selected:
        print("No manifest entries matched --only filter.", file=sys.stderr)
        return 1

    failures = 0
    for index, item in enumerate(selected, start=1):
        print(f"[{index}/{len(selected)}] {item['scene_id']} -> {item['filename']}")
        try:
            image_bytes = make_request(api_key or "", item, args.model, args.dry_run)
            if image_bytes is not None:
                path = save_image(output_dir, item["filename"], image_bytes, args.overwrite)
                print(f"  saved: {path}")
        except FileExistsError as exc:
            print(f"  skipped: {exc}")
        except urllib.error.HTTPError as exc:
            failures += 1
            detail = exc.read().decode("utf-8", errors="replace")
            print(f"  http error {exc.code}: {detail}", file=sys.stderr)
        except urllib.error.URLError as exc:
            failures += 1
            print(f"  network error: {exc}", file=sys.stderr)
        except Exception as exc:
            failures += 1
            print(f"  error: {exc}", file=sys.stderr)

        if index < len(selected) and not args.dry_run and args.delay_seconds > 0:
            time.sleep(args.delay_seconds)

    if failures:
        print(f"Completed with {failures} failure(s).", file=sys.stderr)
        return 1

    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
