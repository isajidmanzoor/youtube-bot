# ============================================================
#   THUMBNAIL_GEN.PY — Pillow se eye-catching thumbnail banao
# ============================================================

import os
import textwrap
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from config import THUMBS_DIR, VIDEO_WIDTH, VIDEO_HEIGHT


# Thumbnail size (YouTube standard)
THUMB_W = 1280
THUMB_H = 720

# Color schemes (cycle through for variety)
COLOR_SCHEMES = [
    {"bg": (15, 15, 35),    "accent": (255, 60, 60),   "text": (255, 255, 255)},
    {"bg": (10, 30, 60),    "accent": (0, 180, 255),   "text": (255, 255, 255)},
    {"bg": (20, 40, 20),    "accent": (50, 220, 80),   "text": (255, 255, 255)},
    {"bg": (50, 20, 60),    "accent": (200, 80, 255),  "text": (255, 255, 255)},
    {"bg": (60, 30, 10),    "accent": (255, 160, 0),   "text": (255, 255, 255)},
]

_scheme_index = 0


def _get_font(size: int):
    """Try system bold fonts, fallback to default."""
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "C:/Windows/Fonts/arialbd.ttf",
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def generate_thumbnail(title: str, filename: str) -> str | None:
    """
    Professional YouTube thumbnail banao.
    Returns: output file path or None on error
    """
    global _scheme_index
    os.makedirs(THUMBS_DIR, exist_ok=True)
    output_path = os.path.join(THUMBS_DIR, f"{filename}.jpg")

    scheme = COLOR_SCHEMES[_scheme_index % len(COLOR_SCHEMES)]
    _scheme_index += 1

    try:
        img = Image.new("RGB", (THUMB_W, THUMB_H), scheme["bg"])
        draw = ImageDraw.Draw(img)

        # ── Gradient overlay (top-left glow) ──────────────────
        for i in range(200):
            alpha = int(60 * (1 - i / 200))
            r = scheme["accent"][0]
            g = scheme["accent"][1]
            b = scheme["accent"][2]
            draw.ellipse(
                [-i, -i, 400 - i, 400 - i],
                fill=(r, g, b, 0),  # just for structure; actual blend below
            )

        # ── Accent bar on left ─────────────────────────────────
        draw.rectangle([0, 0, 12, THUMB_H], fill=scheme["accent"])

        # ── Bottom accent strip ────────────────────────────────
        draw.rectangle([0, THUMB_H - 8, THUMB_W, THUMB_H], fill=scheme["accent"])

        # ── Channel watermark top-right ────────────────────────
        wm_font = _get_font(22)
        draw.text((THUMB_W - 20, 20), "QA Tips", font=wm_font, fill=scheme["accent"], anchor="rt")

        # ── Main title text ────────────────────────────────────
        title_clean = title.upper()
        words = title_clean.split()

        # Try to fit in 2 lines max
        wrapped = textwrap.fill(title_clean, width=22)
        lines = wrapped.split("\n")[:3]

        font_size = 90 if len(lines) == 1 else (72 if len(lines) == 2 else 58)
        title_font = _get_font(font_size)

        total_h = len(lines) * (font_size + 14)
        start_y = (THUMB_H - total_h) // 2

        for idx, line in enumerate(lines):
            y = start_y + idx * (font_size + 14)
            x = 50

            # Shadow
            draw.text((x + 4, y + 4), line, font=title_font, fill=(0, 0, 0))
            # Main text
            draw.text((x, y), line, font=title_font, fill=scheme["text"])

            # Accent underline on first line
            if idx == 0:
                bbox = draw.textbbox((x, y), line, font=title_font)
                draw.rectangle(
                    [x, bbox[3] + 4, bbox[2], bbox[3] + 10],
                    fill=scheme["accent"],
                )

        img.save(output_path, "JPEG", quality=95)
        print(f"✅ Thumbnail saved: {output_path}")
        return output_path

    except Exception as e:
        print(f"❌ Thumbnail error: {e}")
        return None
