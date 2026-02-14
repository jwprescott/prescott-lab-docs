#!/usr/bin/env python3
"""Generate a full viewer manifest by scanning study folders in assets/."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Scan assets study directories (for example ID_*) and generate a full "
            "series-manifest JSON document."
        )
    )
    parser.add_argument(
        "assets_dir",
        nargs="?",
        default="viewer/assets",
        help="Assets root directory (default: viewer/assets)."
    )
    parser.add_argument(
        "--study-glob",
        default="ID_*",
        help="Glob used to discover study folders under assets_dir (default: ID_*)."
    )
    parser.add_argument(
        "--images-subdir",
        default="",
        help="Optional subdirectory inside each study folder containing images."
    )
    parser.add_argument(
        "--extensions",
        default="png,webp,jpg,jpeg",
        help="Comma-separated image extensions (default: png,webp,jpg,jpeg)."
    )
    parser.add_argument(
        "--id-prefix",
        default="ID_",
        help="If study dir starts with this prefix, remove it for the 'id' field."
    )
    parser.add_argument(
        "--base-path-prefix",
        default="./assets",
        help="Prefix used to build imageBasePath in output (default: ./assets)."
    )
    parser.add_argument(
        "--output",
        help="Write JSON to this path instead of stdout (e.g. viewer/series-manifest.json)."
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


def strip_prefix(value: str, prefix: str) -> str:
    if prefix and value.startswith(prefix):
        return value[len(prefix) :]
    return value


def join_url_path(prefix: str, suffix: str) -> str:
    base = (prefix or "").rstrip("/")
    tail = (suffix or "").strip("/")
    if base and tail:
        return f"{base}/{tail}"
    if base:
        return base
    return tail


def main() -> int:
    args = parse_args()
    assets_dir = Path(args.assets_dir).expanduser()
    if not assets_dir.exists() or not assets_dir.is_dir():
        print(f"Error: assets_dir not found or not a directory: {assets_dir}", file=sys.stderr)
        return 1

    allowed_exts = {ext.strip().lower().lstrip(".") for ext in args.extensions.split(",") if ext.strip()}
    if not allowed_exts:
        print("Error: no valid extensions provided", file=sys.stderr)
        return 1

    study_dirs = [p for p in assets_dir.glob(args.study_glob) if p.is_dir()]
    study_dirs.sort(key=lambda p: natural_key(p.name))
    if not study_dirs:
        print(f"Error: no study directories matched '{args.study_glob}' in {assets_dir}", file=sys.stderr)
        return 1

    series = []
    for study_dir in study_dirs:
        images_dir = study_dir / args.images_subdir if args.images_subdir else study_dir
        if not images_dir.exists() or not images_dir.is_dir():
            print(f"Warning: skipping {study_dir.name} (missing images dir: {images_dir})", file=sys.stderr)
            continue

        images = collect_images(images_dir, allowed_exts)
        if not images:
            print(f"Warning: skipping {study_dir.name} (no matching images in {images_dir})", file=sys.stderr)
            continue

        relative_images_part = f"{study_dir.name}/{args.images_subdir}".strip("/")
        image_base_path = join_url_path(args.base_path_prefix, relative_images_part)
        series_obj = {
            "id": strip_prefix(study_dir.name, args.id_prefix),
            "label": study_dir.name,
            "imageBasePath": image_base_path,
            "images": images
        }
        series.append(series_obj)

    if not series:
        print("Error: no valid series found after scanning study directories", file=sys.stderr)
        return 1

    manifest = {"series": series}
    payload = json.dumps(manifest, indent=2)
    if args.output:
        output_path = Path(args.output).expanduser()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(payload + "\n", encoding="utf-8")
        print(f"Wrote {len(series)} series to {output_path}")
        return 0

    print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
