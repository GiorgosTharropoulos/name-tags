#!/usr/bin/env python3
from __future__ import annotations

import argparse
from dataclasses import dataclass
from math import ceil
from pathlib import Path

from reportlab.lib.colors import Color
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas

SUPPORTED_IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"}


@dataclass(frozen=True)
class Rect:
    width_cm: float
    height_cm: float


@dataclass(frozen=True)
class TagPdfConfig:
    input_dir: str | Path
    output_pdf: str | Path
    tag_rect: Rect = Rect(width_cm=9.0, height_cm=5.5)
    margin_cm: float = 0.7
    gap_cm: float = 0.3
    use_landscape: bool = True
    show_cutting_guides: bool = True
    show_crop_marks: bool = True


def cm_to_pt(value_cm: float) -> float:
    return value_cm * cm


@dataclass(frozen=True)
class RectPosition:
    x: float
    y: float
    width: float
    height: float


def draw_cutting_guides(canvas_obj: canvas.Canvas, rect: RectPosition) -> None:
    canvas_obj.setStrokeColor(Color(0.55, 0.55, 0.55))
    canvas_obj.setLineWidth(0.5)
    canvas_obj.rect(rect.x, rect.y, rect.width, rect.height, stroke=1, fill=0)


def draw_crop_marks(canvas_obj: canvas.Canvas, rect: RectPosition) -> None:
    canvas_obj.setStrokeColor(Color(0.2, 0.2, 0.2))
    canvas_obj.setLineWidth(0.25)
    mark_len = 0.5 * cm
    canvas_obj.line(rect.x, rect.y, rect.x, rect.y - mark_len)
    canvas_obj.line(rect.x, rect.y + rect.height, rect.x, rect.y + rect.height + mark_len)
    canvas_obj.line(rect.x + rect.width, rect.y, rect.x + rect.width, rect.y - mark_len)
    canvas_obj.line(rect.x + rect.width, rect.y + rect.height, rect.x + rect.width, rect.y + rect.height + mark_len)
    canvas_obj.line(rect.x, rect.y, rect.x - mark_len, rect.y)
    canvas_obj.line(rect.x + rect.width, rect.y, rect.x + rect.width + mark_len, rect.y)
    canvas_obj.line(rect.x, rect.y + rect.height, rect.x - mark_len, rect.y + rect.height)
    canvas_obj.line(rect.x + rect.width, rect.y + rect.height, rect.x + rect.width + mark_len, rect.y + rect.height)


def collect_images(input_dir: Path) -> list[Path]:
    if not input_dir.exists():
        raise FileNotFoundError(f"Input directory does not exist: {input_dir}")
    if not input_dir.is_dir():
        raise NotADirectoryError(f"Input path is not a directory: {input_dir}")

    images = [
        path
        for path in sorted(input_dir.iterdir(), key=lambda item: item.name.lower())
        if path.is_file() and path.suffix.lower() in SUPPORTED_IMAGE_SUFFIXES
    ]
    if not images:
        raise ValueError(f"No supported image files found in {input_dir}")
    return images


def make_tag_pdf(config: TagPdfConfig) -> tuple[Path, int, int]:
    input_path = Path(config.input_dir)
    images = collect_images(input_path)

    page_size = landscape(A4) if config.use_landscape else A4
    tag_w = cm_to_pt(config.tag_rect.width_cm)
    tag_h = cm_to_pt(config.tag_rect.height_cm)
    margin_x = cm_to_pt(config.margin_cm)
    margin_y = cm_to_pt(config.margin_cm)
    gap_x = cm_to_pt(config.gap_cm)
    gap_y = cm_to_pt(config.gap_cm)

    available_w = page_size[0] - 2 * margin_x
    available_h = page_size[1] - 2 * margin_y

    cols = max(1, int((available_w + gap_x) // (tag_w + gap_x)))
    rows = max(1, int((available_h + gap_y) // (tag_h + gap_y)))

    total_slots = cols * rows
    pages = ceil(len(images) / total_slots)

    output_path = Path(config.output_pdf)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    c = canvas.Canvas(str(output_path), pagesize=page_size)
    c.setTitle("Name tags")

    index = 0
    for page in range(pages):
        for row in range(rows):
            for col in range(cols):
                if index >= len(images):
                    break
                img_path = images[index]
                x = margin_x + col * (tag_w + gap_x)
                y = page_size[1] - margin_y - (row + 1) * tag_h - row * gap_y
                rect = RectPosition(x=x, y=y, width=tag_w, height=tag_h)
                if config.show_cutting_guides:
                    draw_cutting_guides(c, rect)
                if config.show_crop_marks:
                    draw_crop_marks(c, rect)
                c.drawImage(str(img_path), x, y, width=tag_w, height=tag_h)
                index += 1
            if index >= len(images):
                break
        if page < pages - 1:
            c.showPage()

    c.save()
    print(f"Created {output_path} with {pages} page(s)")
    print(f"Layout: {cols} columns x {rows} rows per page")
    return output_path, cols, rows


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate a PDF of name-tag images arranged in a grid")
    parser.add_argument("--input-dir", default="name_tags", help="Directory containing image files")
    parser.add_argument("--output-pdf", default="name_tags_no_gap_crop.pdf", help="Output PDF path")
    parser.add_argument("--tag-width-cm", type=float, default=9.0, help="Tag width in centimeters")
    parser.add_argument("--tag-height-cm", type=float, default=5.5, help="Tag height in centimeters")
    parser.add_argument("--margin-cm", type=float, default=0.7, help="Page margin in centimeters")
    parser.add_argument("--gap-cm", type=float, default=0.0, help="Gap between tags in centimeters")
    parser.add_argument("--portrait", action="store_true", help="Use portrait orientation instead of landscape")
    parser.add_argument("--no-cutting-lines", action="store_true", help="Disable the cutting guide lines around each tag")
    parser.add_argument("--crop-marks", action="store_true", help="Add crop marks around each tag")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    config = TagPdfConfig(
        input_dir=args.input_dir,
        output_pdf=args.output_pdf,
        tag_rect=Rect(width_cm=args.tag_width_cm, height_cm=args.tag_height_cm),
        margin_cm=args.margin_cm,
        gap_cm=args.gap_cm,
        use_landscape=not args.portrait,
        show_cutting_guides=not args.no_cutting_lines,
        show_crop_marks=not args.no_cutting_lines or args.crop_marks,
    )
    make_tag_pdf(config)


if __name__ == "__main__":
    main()
