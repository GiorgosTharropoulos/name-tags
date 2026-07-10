# Name Tags PDF Generator

Generate a PDF of name-tag images arranged in a grid for easy printing and cutting.

## Features

- Reads image files from a directory
- Arranges images into a printable grid on A4 pages
- Supports landscape or portrait layout
- Adds optional cutting guide lines around each tag
- Adds optional crop marks for easier cutting
- Supports zero-gap layouts for tighter packing

## Installation

This project uses `uv`.

```bash
uv sync
```

## Usage

Generate the default PDF (no gaps, crop marks enabled):

```bash
uv run name-tags-pdf --input-dir "$HOME/Downloads/name-tags" --output-pdf /tmp/name_tags_no_gap_crop.pdf
```

Generate a variant without crop marks:

```bash
uv run name-tags-pdf --input-dir "$HOME/Downloads/name-tags" --output-pdf /tmp/name_tags.pdf --gap-cm 0.3
```

Disable the cutting guide lines:

```bash
uv run name-tags-pdf --input-dir "$HOME/Downloads/name-tags" --output-pdf /tmp/name_tags_no_gap_crop.pdf --no-cutting-lines
```

## Notes

For accurate dimensions:

- Print at 100% scale
- Do not use "fit to page" or "shrink oversized pages"
- Use A4 paper and landscape orientation
