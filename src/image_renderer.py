"""Renders a quote onto a base image and saves to posts/."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from . import config


def _load_font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    if not path.exists():
        raise FileNotFoundError(
            f"Font not found at {path}. Run scripts/download_fonts.sh first."
        )
    return ImageFont.truetype(str(path), size)


def _wrap_text(
    text: str,
    font: ImageFont.FreeTypeFont,
    draw: ImageDraw.ImageDraw,
    max_width: int,
) -> list[str]:
    out: list[str] = []
    for paragraph in text.split("\n"):
        if not paragraph.strip():
            out.append("")
            continue
        words = paragraph.split(" ")
        current = ""
        for w in words:
            candidate = (current + " " + w).strip()
            bbox = draw.textbbox((0, 0), candidate, font=font)
            if bbox[2] - bbox[0] <= max_width:
                current = candidate
            else:
                if current:
                    out.append(current)
                current = w
        if current:
            out.append(current)
    return out


def _measure_block(
    lines: Iterable[str],
    font: ImageFont.FreeTypeFont,
    draw: ImageDraw.ImageDraw,
    line_spacing: int,
) -> tuple[int, int]:
    lines = list(lines)
    if not lines:
        return 0, 0
    max_w, total_h = 0, 0
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line or " ", font=font)
        max_w = max(max_w, bbox[2] - bbox[0])
        total_h += bbox[3] - bbox[1]
        if i < len(lines) - 1:
            total_h += line_spacing
    return max_w, total_h


def _draw_block(
    draw: ImageDraw.ImageDraw,
    lines: list[str],
    font: ImageFont.FreeTypeFont,
    center_x: int,
    top_y: int,
    line_spacing: int,
    fill: tuple[int, int, int],
) -> int:
    y = top_y
    for line in lines:
        bbox = draw.textbbox((0, 0), line or " ", font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        x = center_x - w // 2
        draw.text((x + 2, y + 2), line, font=font, fill=(0, 0, 0, 120))
        draw.text((x, y), line, font=font, fill=fill)
        y += h + line_spacing
    return y


def _prepare_base(image_path: Path) -> Image.Image:
    img = Image.open(image_path).convert("RGB")
    target_ratio = config.IMG_WIDTH / config.IMG_HEIGHT
    src_ratio = img.width / img.height
    if src_ratio > target_ratio:
        new_width = int(img.height * target_ratio)
        left = (img.width - new_width) // 2
        img = img.crop((left, 0, left + new_width, img.height))
    else:
        new_height = int(img.width / target_ratio)
        top = (img.height - new_height) // 2
        img = img.crop((0, top, img.width, top + new_height))
    img = img.resize((config.IMG_WIDTH, config.IMG_HEIGHT), Image.LANCZOS)
    img = img.filter(ImageFilter.GaussianBlur(radius=1.5))
    return img


def render_quote(
    base_image_path: Path,
    quote_text: str,
    author: str,
    output_path: Path,
    handle: str | None = None,
) -> Path:
    """Render the post image and save to output_path. Returns output_path."""
    base = _prepare_base(base_image_path)
    composite = base.convert("RGBA")
    draw = ImageDraw.Draw(composite)

    quote_font = _load_font(config.FONT_QUOTE, config.QUOTE_FONT_SIZE)
    author_font = _load_font(config.FONT_AUTHOR, config.AUTHOR_FONT_SIZE)

    max_text_width = config.IMG_WIDTH - 2 * config.SIDE_PADDING

    # Opening quote mark on its own line for elegance
    quote_lines = _wrap_text(f"“{quote_text}”", quote_font, draw, max_text_width)
    author_line = f"— {author}"

    _, quote_h = _measure_block(quote_lines, quote_font, draw, config.LINE_SPACING_QUOTE)
    _, author_h = _measure_block([author_line], author_font, draw, 0)

    total_text_h = quote_h + config.GAP_QUOTE_AUTHOR + author_h

    pad = config.TEXT_PANEL_PADDING
    panel_top = max(80, (config.IMG_HEIGHT - total_text_h) // 2 - pad)
    panel_bottom = panel_top + total_text_h + 2 * pad
    panel_left = config.SIDE_PADDING - pad
    panel_right = config.IMG_WIDTH - config.SIDE_PADDING + pad

    panel = Image.new("RGBA", (config.IMG_WIDTH, config.IMG_HEIGHT), (0, 0, 0, 0))
    ImageDraw.Draw(panel).rounded_rectangle(
        [panel_left, panel_top, panel_right, panel_bottom],
        radius=config.TEXT_PANEL_CORNER_RADIUS,
        fill=(*config.OVERLAY_COLOR, config.OVERLAY_OPACITY),
    )
    composite = Image.alpha_composite(composite, panel)
    draw = ImageDraw.Draw(composite)

    center_x = config.IMG_WIDTH // 2
    text_top = panel_top + pad

    after_quote = _draw_block(
        draw, quote_lines, quote_font, center_x,
        text_top, config.LINE_SPACING_QUOTE, config.TEXT_COLOR,
    )
    _draw_block(
        draw, [author_line], author_font, center_x,
        after_quote + config.GAP_QUOTE_AUTHOR, 0, config.AUTHOR_COLOR,
    )

    if handle:
        try:
            handle_font = _load_font(config.FONT_HANDLE, config.HANDLE_FONT_SIZE)
            bbox = draw.textbbox((0, 0), handle, font=handle_font)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            x = (config.IMG_WIDTH - w) // 2
            y = config.IMG_HEIGHT - h - 60
            draw.text((x + 1, y + 1), handle, font=handle_font, fill=(0, 0, 0, 120))
            draw.text((x, y), handle, font=handle_font, fill=config.HANDLE_COLOR)
        except FileNotFoundError:
            pass

    output_path.parent.mkdir(parents=True, exist_ok=True)
    composite.convert("RGB").save(output_path, "JPEG", quality=92, optimize=True)
    return output_path
