# ============================================================
#   ADVANCED_THUMBNAIL_GEN.PY — Professional AI Thumbnails
#   Each thumbnail is 100% unique with advanced effects
# ============================================================

import os
import random
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

THUMB_W = 1280
THUMB_H = 720
AFFILIATE_LINK = "https://i.mec.me/?c=pt6wsw2v"

# Professional color palettes used by top YouTubers
PALETTES = [
    {"name": "fire",     "bg": (10, 5, 0),     "primary": (255, 80, 0),   "secondary": (255, 200, 0), "text": (255, 255, 255)},
    {"name": "ice",      "bg": (0, 10, 25),     "primary": (0, 180, 255),  "secondary": (100, 230, 255), "text": (255, 255, 255)},
    {"name": "matrix",   "bg": (0, 8, 0),       "primary": (0, 255, 70),   "secondary": (0, 180, 50),  "text": (255, 255, 255)},
    {"name": "purple",   "bg": (15, 0, 30),     "primary": (180, 0, 255),  "secondary": (255, 100, 255), "text": (255, 255, 255)},
    {"name": "gold",     "bg": (20, 15, 0),     "primary": (255, 200, 0),  "secondary": (255, 150, 0),  "text": (0, 0, 0)},
    {"name": "danger",   "bg": (20, 0, 0),      "primary": (255, 0, 50),   "secondary": (255, 100, 0),  "text": (255, 255, 255)},
    {"name": "cyber",    "bg": (0, 0, 20),      "primary": (0, 255, 200),  "secondary": (0, 200, 255),  "text": (255, 255, 255)},
    {"name": "royal",    "bg": (5, 0, 25),      "primary": (100, 50, 255), "secondary": (200, 100, 255), "text": (255, 255, 255)},
    {"name": "toxic",    "bg": (5, 15, 0),      "primary": (150, 255, 0),  "secondary": (200, 255, 50), "text": (0, 0, 0)},
    {"name": "blood",    "bg": (15, 0, 0),      "primary": (200, 0, 0),    "secondary": (255, 50, 50),  "text": (255, 255, 255)},
    {"name": "ocean",    "bg": (0, 10, 20),     "primary": (0, 120, 200),  "secondary": (0, 200, 180),  "text": (255, 255, 255)},
    {"name": "sunset",   "bg": (20, 5, 0),      "primary": (255, 100, 50), "secondary": (255, 200, 100), "text": (255, 255, 255)},
]

BADGE_TEXTS = [
    "FREE", "EARN NOW", "REAL MONEY", "LIVE PROOF",
    "CLICK NOW", "JOIN FREE", "PAID DAILY", "LEGIT",
    "WORKING 2025", "NO SCAM", "INSTANT PAY", "TRY NOW",
]

LAYOUTS = [
    "split_left", "split_right", "center_dramatic",
    "top_heavy", "bottom_banner", "diagonal_split",
    "frame_border", "spotlight",
]


def _get_font(size: int):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "C:/Windows/Fonts/arialbd.ttf",
    ]
    for p in paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()


def _draw_gradient(img, color1, color2, direction="horizontal"):
    """Draw a smooth gradient."""
    draw = ImageDraw.Draw(img)
    w, h = img.size
    if direction == "horizontal":
        for x in range(w):
            r = int(color1[0] + (color2[0] - color1[0]) * x / w)
            g = int(color1[1] + (color2[1] - color1[1]) * x / w)
            b = int(color1[2] + (color2[2] - color1[2]) * x / w)
            draw.line([(x, 0), (x, h)], fill=(r, g, b))
    else:
        for y in range(h):
            r = int(color1[0] + (color2[0] - color1[0]) * y / h)
            g = int(color1[1] + (color2[1] - color1[1]) * y / h)
            b = int(color1[2] + (color2[2] - color1[2]) * y / h)
            draw.line([(0, y), (w, y)], fill=(r, g, b))
    return img


def _draw_glow_circle(draw, cx, cy, radius, color, intensity=8):
    """Draw glowing circle effect."""
    for i in range(intensity, 0, -1):
        alpha = int(40 * i / intensity)
        r = min(255, color[0] + alpha)
        g = min(255, color[1] + alpha)
        b = min(255, color[2] + alpha)
        size = radius + i * 15
        draw.ellipse([cx - size, cy - size, cx + size, cy + size],
                     fill=(max(0, r - 150), max(0, g - 150), max(0, b - 150)))


def _draw_text_with_shadow(draw, pos, text, font, color, shadow_offset=4):
    """Draw text with professional shadow."""
    x, y = pos
    # Multiple shadow layers for depth
    for offset in [6, 4, 2]:
        shadow_color = (0, 0, 0)
        draw.text((x + offset, y + offset), text, font=font, fill=shadow_color)
    # Main text
    draw.text((x, y), text, font=font, fill=color)


def _draw_text_with_outline(draw, pos, text, font, color, outline_color=(0,0,0), outline_width=3):
    """Draw text with thick outline for maximum readability."""
    x, y = pos
    for dx in range(-outline_width, outline_width + 1):
        for dy in range(-outline_width, outline_width + 1):
            if dx != 0 or dy != 0:
                draw.text((x + dx, y + dy), text, font=font, fill=outline_color)
    draw.text((x, y), text, font=font, fill=color)


def _wrap_text(text, max_chars=18):
    """Wrap text into lines."""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        if len(current) + len(word) + 1 <= max_chars:
            current = current + " " + word if current else word
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines[:3]


def generate_advanced_thumbnail(title: str, filename: str, output_dir: str = "output/thumbnails", force_palette: str = None) -> str | None:
    """Generate a professional unique thumbnail."""
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{filename}.jpg")

    palette = next((p for p in PALETTES if p["name"] == force_palette), None) or random.choice(PALETTES)
    layout = random.choice(LAYOUTS)
    badge = random.choice(BADGE_TEXTS)

    try:
        # ── Base canvas ──────────────────────────────────────
        img = Image.new("RGB", (THUMB_W, THUMB_H), palette["bg"])

        # ── Background effect based on layout ─────────────────
        if layout == "split_left":
            left = Image.new("RGB", (THUMB_W // 2, THUMB_H), palette["bg"])
            right = Image.new("RGB", (THUMB_W // 2, THUMB_H), 
                             tuple(min(255, c + 30) for c in palette["bg"]))
            _draw_gradient(left, palette["bg"], tuple(c // 3 for c in palette["primary"]))
            img.paste(left, (0, 0))
            img.paste(right, (THUMB_W // 2, 0))

        elif layout == "split_right":
            _draw_gradient(img, palette["bg"], 
                          tuple(min(255, c + 20) for c in palette["bg"]), "horizontal")

        elif layout == "center_dramatic":
            _draw_gradient(img, palette["bg"],
                          tuple(min(255, c // 2) for c in palette["primary"]), "vertical")

        elif layout == "diagonal_split":
            draw_temp = ImageDraw.Draw(img)
            points = [(0, 0), (THUMB_W * 2 // 3, 0), (THUMB_W // 3, THUMB_H), (0, THUMB_H)]
            draw_temp.polygon(points, fill=tuple(c // 4 for c in palette["primary"]))

        elif layout == "spotlight":
            draw_temp = ImageDraw.Draw(img)
            _draw_glow_circle(draw_temp, THUMB_W // 2, THUMB_H // 2, 200, palette["primary"], 12)

        elif layout == "frame_border":
            draw_temp = ImageDraw.Draw(img)
            border = 25
            draw_temp.rectangle([0, 0, THUMB_W, border], fill=palette["primary"])
            draw_temp.rectangle([0, THUMB_H - border, THUMB_W, THUMB_H], fill=palette["primary"])
            draw_temp.rectangle([0, 0, border, THUMB_H], fill=palette["primary"])
            draw_temp.rectangle([THUMB_W - border, 0, THUMB_W, THUMB_H], fill=palette["primary"])

        # ── Particle effects (random dots) ────────────────────
        draw = ImageDraw.Draw(img)
        for _ in range(random.randint(15, 35)):
            px = random.randint(0, THUMB_W)
            py = random.randint(0, THUMB_H)
            pr = random.randint(2, 12)
            opacity = random.randint(30, 100)
            color = palette["primary"]
            draw.ellipse([px - pr, py - pr, px + pr, py + pr],
                        fill=tuple(max(0, c - 100) for c in color))

        # ── Glow circles in corners ───────────────────────────
        corner = random.choice([(0, 0), (THUMB_W, 0), (0, THUMB_H), (THUMB_W, THUMB_H)])
        _draw_glow_circle(draw, corner[0], corner[1], 100, palette["primary"], 6)

        # ── Money/emoji symbols scattered ─────────────────────
        symbol_font = _get_font(40)
        symbols = ["$", "₿", "💰", "🚀", "⚡"]
        for _ in range(random.randint(2, 5)):
            sx = random.randint(50, THUMB_W - 100)
            sy = random.randint(50, THUMB_H - 100)
            draw.text((sx, sy), random.choice(["$", "$", "$"]),
                     font=symbol_font, fill=palette["primary"])

        # ── BADGE (top corner) ────────────────────────────────
        badge_font = _get_font(38)
        badge_w = len(badge) * 22 + 30
        bx = random.choice([20, THUMB_W - badge_w - 20])
        by = 20
        # Badge background
        draw.rectangle([bx - 8, by - 5, bx + badge_w, by + 52],
                      fill=palette["primary"])
        # Badge glow
        draw.rectangle([bx - 10, by - 7, bx + badge_w + 2, by + 54],
                      outline=palette["secondary"], width=2)
        draw.text((bx, by + 5), badge, font=badge_font, fill=palette["bg"])

        # ── Channel watermark ─────────────────────────────────
        wm_font = _get_font(22)
        wm_x = THUMB_W // 2
        draw.text((wm_x, 15), "CRYPTO AIRDROP DAILY", font=wm_font,
                 fill=palette["secondary"], anchor="mt")

        # ── MAIN TITLE ────────────────────────────────────────
        title_upper = title.upper()
        lines = _wrap_text(title_upper, max_chars=16)

        # Dynamic font size based on line count
        sizes = {1: 110, 2: 82, 3: 62}
        font_size = sizes.get(len(lines), 62)
        title_font = _get_font(font_size)

        line_height = font_size + 20
        total_h = len(lines) * line_height
        start_y = (THUMB_H - total_h) // 2 - 10

        # Adjust x based on layout
        if layout == "split_left":
            text_x = 50
        elif layout == "split_right":
            text_x = THUMB_W // 2 + 20
        else:
            text_x = 50

        for i, line in enumerate(lines):
            y = start_y + i * line_height

            # Draw each line with outline + shadow
            _draw_text_with_outline(
                draw, (text_x, y), line, title_font,
                palette["text"], (0, 0, 0), 4
            )

            # Accent line under first word of first line
            if i == 0:
                first_word = line.split()[0] if line.split() else line
                bbox = draw.textbbox((text_x, y), first_word, font=title_font)
                draw.rectangle(
                    [text_x, bbox[3] + 3, bbox[2], bbox[3] + 8],
                    fill=palette["primary"]
                )

        # ── Bottom accent bar with earnings ──────────────────
        bar_h = 70
        draw.rectangle([0, THUMB_H - bar_h, THUMB_W, THUMB_H], fill=palette["primary"])
        earn_font = _get_font(32)
        earn_texts = [
            "💰 FREE TO JOIN - LINK IN DESCRIPTION",
            "🔥 CLAIM YOUR FREE CRYPTO TODAY",
            "✅ NO INVESTMENT NEEDED - START NOW",
            "🚀 EARN DAILY - 100% FREE",
            "💎 JOIN THOUSANDS EARNING FREE CRYPTO",
        ]
        earn_text = random.choice(earn_texts)
        draw.text((THUMB_W // 2, THUMB_H - bar_h // 2), earn_text,
                 font=earn_font, fill=palette["bg"], anchor="mm")

        # ── Save ──────────────────────────────────────────────
        # Slight enhancement
        img = ImageEnhance.Contrast(img).enhance(1.1)
        img = ImageEnhance.Sharpness(img).enhance(1.2)

        img.save(output_path, "JPEG", quality=96)
        print(f"✅ Thumbnail: {palette['name']} | {layout}")
        return output_path

    except Exception as e:
        print(f"❌ Thumbnail error: {e}")
        return None
