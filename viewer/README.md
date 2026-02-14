# CT Stack Viewer Scaffold

This is a static single-pane stack viewer scaffold intended for deployment as a Render Static Site (or any static host).

## Files

- `index.html`: viewer UI
- `styles.css`: layout/theme
- `app.js`: manifest loader + slice navigation logic
- `scripts/generate_images_array.py`: helper to build `images` arrays from a folder
- `scripts/generate_manifest_from_assets.py`: helper to auto-build full `series-manifest.json` from `ID_*` folders
- `series-manifest.json`: active data manifest used by the app
- `series-manifest.sample.json`: backup sample data manifest

## Manifest contract

Edit `series-manifest.json` and configure your series entries.

Each series supports:

- `id` (required)
- `label` (required)
- `slices` (required with `imagePattern`; optional with `images` or `image`)
- `imagePattern` (required if each slice has its own image)
- `image` (optional alternative: one static image for the whole series)
- `images` (optional alternative: explicit ordered filename/path list for per-slice images)
- `imageBasePath` (optional prefix applied to each entry in `images`)
- `startIndex` (optional, default `0`)
- `description` (optional)

Pattern tokens:

- `{index}`: absolute index, no padding
- `{indexPadded}`: absolute index, zero-padded to 3 digits

Example:

```json
{
  "id": "series_001",
  "label": "Series 001",
  "slices": 24,
  "imagePattern": "https://cdn.prescottlab.xyz/series_001/combined/slice_{indexPadded}.webp"
}
```

If filenames include variable metadata (for example different prediction values/IDs per slice), use `images`:

```json
{
  "id": "series_002",
  "label": "Series 002",
  "imageBasePath": "./assets/series_002/combined",
  "images": [
    "000_img000_pred-any_p0.021_s0.00001_ID_254787153.png",
    "001_img001_pred-any_p0.021_s0.00001_ID_1e22b2b1b.png"
  ]
}
```

## Auto-generate images array

Use the helper script to scan a folder and output sorted filenames.

Output only an `images` array:

```bash
python3 viewer/scripts/generate_images_array.py \
  viewer/assets/1e22b2b1b/combined
```

Output a full series object you can paste into `series-manifest.json`:

```bash
python3 viewer/scripts/generate_images_array.py \
  viewer/assets/1e22b2b1b/combined \
  --mode series \
  --series-id 1e22b2b1b \
  --label "Series ID 1e22b2b1b" \
  --description "Combined panel images per slice."
```

Notes:

- Sort is natural (numeric prefixes like `000`, `001`, ... stay in order).
- Default extensions are `png,webp,jpg,jpeg`.
- Override extensions with `--extensions`.

## Auto-generate full manifest from `ID_*` directories

If you copy many study folders into `viewer/assets/` (for example `ID_7d7a460d1a`, `ID_8b19b004d0`), use:

```bash
python3 viewer/scripts/generate_manifest_from_assets.py \
  viewer/assets \
  --study-glob 'ID_*' \
  --output viewer/series-manifest.json
```

If images are inside a nested folder like `ID_xxx/combined/`, add:

```bash
python3 viewer/scripts/generate_manifest_from_assets.py \
  viewer/assets \
  --study-glob 'ID_*' \
  --images-subdir combined \
  --output viewer/series-manifest.json
```

## Suggested asset layout

```text
viewer/
  assets/
    7d7a460d1a/
      combined/
        slice_000.webp
        ...
    series_002/
      combined/
        000_img000_pred-any_p0.021_s0.00001_ID_254787153.png
        001_img001_pred-any_p0.021_s0.00001_ID_1e22b2b1b.png
        ...
```

## Local preview

From repo root:

```bash
python3 -m http.server 8000
```

Then open `http://localhost:8000/viewer/`.

## Render deployment

1. Create a new **Static Site** in Render from this repo/branch.
2. Set publish directory to `viewer`.
3. Add custom domain `viewer.prescottlab.xyz`.
4. Add a DNS `CNAME` pointing `viewer` to the Render hostname.
