# ============================================================
#   THUMBNAIL_GEN.PY — Unique dynamic thumbnails
# ============================================================

import os
import random
import textwrap
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from config import THUMBS_DIR

THUMB_W = 1280
THUMB_H = 720

# Many unique color schemes
COLOR_SCHEMES = [
    {"bg": (8, 8, 20),      "accent": (255, 50, 50),   "text": (255, 255, 255), "glow": (255, 0, 0)},
    {"bg": (5, 20, 50),     "accent": (0, 200, 255),   "text": (255, 255, 255), "glow": (0, 150, 255)},
    {"bg": (15, 40, 15),    "accent": (0, 255, 80),    "text": (255, 255, 255), "glow": (0, 200, 50)},
    {"bg": (40, 10, 50),    "accent": (220, 0, 255),   "text": (255, 255, 255), "glow": (180, 0, 255)},
    {"bg": (50, 25, 5),     "accent": (255, 150, 0),   "text": (255, 255, 255), "glow": (255, 120, 0)},
    {"bg": (5, 40, 50),     "accent": (0, 255, 220),   "text": (255, 255, 255), "glow": (0, 200, 180)},
    {"bg": (50, 5, 20),     "accent": (255, 20, 100),  "text": (255, 255, 255), "glow": (255, 0, 80)},
    {"bg": (20, 20, 5),     "accent": (220, 220, 0),   "text": (0, 0, 0),       "glow": (200, 200, 0)},
    {"bg": (0, 0, 0),       "accent": (255, 255, 255), "text": (0, 0, 0),       "glow": (200, 200, 200)},
    {"bg": (30, 10, 10),    "accent": (255, 80, 0),    "text": (255, 255, 255), "glow": (255, 60, 0)},
]

LAYOUTS = ["left_bar", "top_bar", "diagonal", "corner_box", "center_line", "double_bar"]

_counter = 0


def _get_font(size):
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


def _draw_glow(draw, x, y, w, h, color, radius=30):
    """Draw glow effect behind text area."""
    for i in range(radius, 0, -5):
        alpha_color = tuple(max(0, c - i * 3) for c in color)
        draw.rectangle([x - i, y - i, x + w + i, y + h + i], fill=alpha_color)


def generate_thumbnail(title: str, filename: str) -> str | None:
    global _counter
    os.makedirs(THUMBS_DIR, exist_ok=True)
    output_path = os.path.join(THUMBS_DIR, f"{filename}.jpg")

    scheme = COLOR_SCHEMES[_counter % len(COLOR_SCHEMES)]
    layout = LAYOUTS[_counter % len(LAYOUTS)]
    _counter += 1

    try:
        img = Image.new("RGB", (THUMB_W, THUMB_H), scheme["bg"])
        draw = ImageDraw.Draw(img)

        # ── Background pattern (unique per layout) ─────────────
        if layout == "left_bar":
            draw.rectangle([0, 0, 18, THUMB_H], fill=scheme["accent"])
            draw.rectangle([0, THUMB_H - 10, THUMB_W, THUMB_H], fill=scheme["accent"])

        elif layout == "top_bar":
            draw.rectangle([0, 0, THUMB_W, 18], fill=scheme["accent"])
            draw.rectangle([0, THUMB_H - 18, THUMB_W, THUMB_H], fill=scheme["accent"])

        elif layout == "diagonal":
            for i in range(0, THUMB_W, 80):
                draw.line([(i, 0), (i + 200, THUMB_H)], fill=scheme["accent"], width=3)
            # Dark overlay to keep text readable
            overlay = Image.new("RGB", (THUMB_W, THUMB_H), scheme["bg"])
            img = Image.blend(img, overlay, 0.7)
            draw = ImageDraw.Draw(img)

        elif layout == "corner_box":
            draw.rectangle([0, 0, 400, THUMB_H], fill=tuple(max(0, c - 20) for c in scheme["bg"]))
            draw.rectangle([400, 0, 405, THUMB_H], fill=scheme["accent"])

        elif layout == "center_line":
            draw.rectangle([0, THUMB_H // 2 - 3, THUMB_W, THUMB_H // 2 + 3], fill=scheme["accent"])
            draw.rectangle([0, 0, THUMB_W, 8], fill=scheme["accent"])
            draw.rectangle([0, THUMB_H - 8, THUMB_W, THUMB_H], fill=scheme["accent"])

        elif layout == "double_bar":
            draw.rectangle([0, 0, 12, THUMB_H], fill=scheme["accent"])
            draw.rectangle([24, 0, 36, THUMB_H], fill=scheme["accent"])
            draw.rectangle([0, THUMB_H - 12, THUMB_W, THUMB_H], fill=scheme["accent"])

        # ── Random decorative dots/circles ────────────────────
        for _ in range(random.randint(3, 8)):
            cx = random.randint(0, THUMB_W)
            cy = random.randint(0, THUMB_H)
            r = random.randint(5, 25)
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=scheme["accent"])

        # ── Watermark ─────────────────────────────────────────
        wm_font = _get_font(24)
        draw.text((THUMB_W - 20, 20), "CRYPTO TIPS", font=wm_font,
                  fill=scheme["accent"], anchor="rt")

        # ── Money badge (random position) ─────────────────────
        badge_texts = ["FREE", "EARN NOW", "REAL MONEY", "LIVE PROOF", "CLICK NOW", "JOIN FREE"]
        badge = random.choice(badge_texts)
        badge_font = _get_font(36)
        bx = random.choice([30, THUMB_W - 200])
        by = random.choice([20, THUMB_H - 70])
        draw.rectangle([bx - 10, by - 5, bx + 180, by + 45], fill=scheme["accent"])
        draw.text((bx, by), badge, font=badge_font, fill=scheme["bg"])

        # ── Main title ────────────────────────────────────────
        title_upper = title.upper()
        wrapped = textwrap.fill(title_upper, width=20)
        lines = wrapped.split("\n")[:3]

        font_size = 95 if len(lines) == 1 else (75 if len(lines) == 2 else 58)
        title_font = _get_font(font_size)

        total_h = len(lines) * (font_size + 16)
        start_y = (THUMB_H - total_h) // 2

        # Offset based on layout
        x_offset = 60 if layout == "corner_box" else 45

        for idx, line in enumerate(lines):
            y = start_y + idx * (font_size + 16)

            # Shadow
            draw.text((x_offset + 5, y + 5), line, font=title_font, fill=(0, 0, 0))
            # Main text
            draw.text((x_offset, y), line, font=title_font, fill=scheme["text"])

            # Accent underline on first line only
            if idx == 0:
                bbox = draw.textbbox((x_offset, y), line, font=title_font)
                draw.rectangle(
                    [x_offset, bbox[3] + 4, bbox[2], bbox[3] + 10],
                    fill=scheme["accent"],
                )

        img.save(output_path, "JPEG", quality=95)
        print(f"✅ Thumbnail saved: {output_path}")
        return output_path

    except Exception as e:
        print(f"❌ Thumbnail error: {e}")
        return None
