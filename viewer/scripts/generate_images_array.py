#!/usr/bin/env python3
"""Generate ordered JSON image arrays for viewer series manifests."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Scan an image folder and output a JSON array (or full series object) "
            "for viewer/series-manifest.json."
        )
    )
    parser.add_argument(
        "images_dir",
        help="Directory containing slice images for one series."
    )
    parser.add_argument(
        "--mode",
        choices=["array", "series"],
        default="array",
        help="Output only the images array (default) or a full series object."
    )
    parser.add_argument(
        "--series-id",
        help="Series id (required when --mode series)."
    )
    parser.add_argument(
        "--label",
        help="Series label (defaults to series id when --mode series)."
    )
    parser.add_argument(
        "--description",
        default="",
        help="Optional series description (series mode only)."
    )
    parser.add_argument(
        "--image-base-path",
        help=(
            "Path prefix used for imageBasePath in series mode. "
            "If omitted, computed relative to viewer/ when possible."
        )
    )
    parser.add_argument(
        "--extensions",
        default="png,webp,jpg,jpeg",
        help="Comma-separated file extensions to include (default: png,webp,jpg,jpeg)."
    )
    return parser.parse_args()


def natural_key(text: str) -> list[object]:
    parts = re.findall(r"\d+|\D+", text)
    key: list[object] = []
    for part in parts:
        if part.isdigit():
            key.append(int(part))
        else:
            key.append(part.lower())
    return key


def collect_images(images_dir: Path, allowed_exts: set[str]) -> list[str]:
    files = [
        p.name
        for p in images_dir.iterdir()
        if p.is_file() and p.suffix.lower().lstrip(".") in allowed_exts
    ]
    files.sort(key=natural_key)
    return files


def compute_default_base_path(images_dir: Path) -> str:
    viewer_dir = Path(__file__).resolve().parents[1]
    try:
        rel = images_dir.resolve().relative_to(viewer_dir.resolve())
        return f"./{rel.as_posix()}"
    except ValueError:
        return images_dir.as_posix()


def main() -> int:
    args = parse_args()
    images_dir = Path(args.images_dir).expanduser()
    if not images_dir.exists() or not images_dir.is_dir():
        print(f"Error: images_dir not found or not a directory: {images_dir}", file=sys.stderr)
        return 1

    allowed_exts = {ext.strip().lower().lstrip(".") for ext in args.extensions.split(",") if ext.strip()}
    if not allowed_exts:
        print("Error: no valid extensions provided", file=sys.stderr)
        return 1

    images = collect_images(images_dir, allowed_exts)
    if not images:
        print(f"Error: no matching images found in {images_dir}", file=sys.stderr)
        return 1

    if args.mode == "array":
        print(json.dumps(images, indent=2))
        return 0

    if not args.series_id:
        print("Error: --series-id is required in --mode series", file=sys.stderr)
        return 1

    series_obj = {
        "id": args.series_id,
        "label": args.label or args.series_id,
        "imageBasePath": args.image_base_path or compute_default_base_path(images_dir),
        "images": images
    }
    if args.description:
        series_obj["description"] = args.description

    print(json.dumps(series_obj, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
