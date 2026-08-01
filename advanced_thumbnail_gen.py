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


REMBG_PYTHON = os.path.expanduser("~/rembg-test/venv/bin/python")

def _remove_background(input_path, output_path):
    """Calls the isolated rembg venv via subprocess to cut out the subject with real transparency."""
    import subprocess
    script = "from rembg import remove; from PIL import Image; img = Image.open('{}'); result = remove(img); result.save('{}')".format(input_path, output_path)
    cmd = [REMBG_PYTHON, "-c", script]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        print(f"rembg failed: {result.stderr[-500:]}")
        return False
    return os.path.exists(output_path)


def _add_reaction_face(img, palette, seed_val):
    """Add a large, dynamic 'shocked reaction' face cutout (real background removal, viral thumbnail style)."""
    try:
        random.seed(seed_val)
        reaction_queries = [
            "shocked surprised man face reaction",
            "shocked surprised woman face reaction",
            "amazed excited person reaction face",
            "surprised person mouth open reaction",
            "excited shocked face expression",
        ]
        query = random.choice(reaction_queries)
        photo_path = _fetch_pexels_photo(query, cache_dir="output/thumbnails/_reaction_cache")
        if not photo_path:
            return img

        cutout_path = photo_path.replace(".jpg", "_cutout.png")
        if not os.path.exists(cutout_path):
            if not os.path.exists(REMBG_PYTHON) or not _remove_background(os.path.abspath(photo_path), os.path.abspath(cutout_path)):
                return img

        face = Image.open(cutout_path).convert("RGBA")
        fw, fh = face.size
        target_h = int(THUMB_H * 0.95)
        target_w = int(fw * (target_h / fh))
        face = face.resize((target_w, target_h))
        face = ImageEnhance.Contrast(face).enhance(1.15)
        face = ImageEnhance.Color(face).enhance(1.2)

        # Always right side for consistent layout (text always has left half free)
        pos_x = THUMB_W - target_w - 10
        pos_y = THUMB_H - target_h

        # Soft drop shadow behind the cutout for depth
        shadow = Image.new("RGBA", face.size, (0, 0, 0, 0))
        alpha = face.split()[3]
        shadow.paste((0, 0, 0, 120), (0, 0), alpha)
        shadow = shadow.filter(ImageFilter.GaussianBlur(12))

        img_rgba = img.convert("RGBA")
        img_rgba.paste(shadow, (pos_x + 8, pos_y + 10), shadow)
        img_rgba.paste(face, (pos_x, pos_y), face)
        return img_rgba.convert("RGB")
    except Exception as e:
        print(f"Reaction face add failed: {e}")
        return img


def _add_avatar_to_thumbnail(img, palette, layout, gender="female"):
    """Paste a circular-cropped avatar with a dynamic multi-layer glow border, slight tilt, and grain."""
    try:
        avatar_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "avatar")
        face_file = "host_face_male.jpg" if gender == "male" else "host_face_female.jpg"
        face_path = os.path.join(avatar_dir, face_file)
        if not os.path.exists(face_path):
            return img

        size = random.randint(130, 150)
        avatar = Image.open(face_path).convert("RGB").resize((size, size))
        avatar = ImageEnhance.Contrast(avatar).enhance(1.15)
        avatar = ImageEnhance.Color(avatar).enhance(1.1)

        # Circular mask
        mask = Image.new("L", (size, size), 0)
        mdraw = ImageDraw.Draw(mask)
        mdraw.ellipse([0, 0, size, size], fill=255)

        # Multi-layer glow ring (outer soft glow + inner solid ring)
        ring_size = size + 28
        ring = Image.new("RGBA", (ring_size, ring_size), (0, 0, 0, 0))
        rdraw = ImageDraw.Draw(ring)
        rdraw.ellipse([0, 0, ring_size, ring_size], fill=palette["secondary"] + (140,))
        ring = ring.filter(ImageFilter.GaussianBlur(8))
        rdraw2 = ImageDraw.Draw(ring)
        inner_pad = 8
        rdraw2.ellipse([inner_pad, inner_pad, ring_size - inner_pad, ring_size - inner_pad],
                       fill=palette["primary"] + (255,))

        # Slight random tilt for dynamic feel
        angle = random.uniform(-6, 6)
        ring = ring.rotate(angle, expand=True, resample=Image.BICUBIC)

        # Random corner (bottom side only, avoids title & badge collisions)
        pos_x = THUMB_W - ring.width - 20
        pos_y = THUMB_H - 70 - ring.height - 15

        img_rgba = img.convert("RGBA")
        img_rgba.paste(ring, (pos_x, pos_y), ring)

        # Paste avatar centered inside the ring (accounting for rotation padding)
        offset_x = pos_x + (ring.width - size) // 2
        offset_y = pos_y + (ring.height - size) // 2
        img_rgba.paste(avatar, (offset_x, offset_y), mask)

        img = img_rgba.convert("RGB")

        # Subtle grain/noise texture for cinematic uniqueness
        noise = Image.effect_noise((THUMB_W, THUMB_H), random.randint(18, 30)).convert("L")
        noise_rgb = Image.merge("RGB", (noise, noise, noise))
        img = Image.blend(img, noise_rgb, 0.03)

        return img
    except Exception as e:
        print(f"Avatar thumbnail add failed: {e}")
        return img


def _draw_coin(draw, cx, cy, r, palette, symbol="$"):
    """Draw a shiny 3D-ish coin with symbol."""
    # Shadow
    draw.ellipse([cx - r + 4, cy - r + 6, cx + r + 4, cy + r + 6], fill=(0, 0, 0, 90))
    # Outer ring
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=palette["secondary"])
    # Inner face
    inner = int(r * 0.78)
    draw.ellipse([cx - inner, cy - inner, cx + inner, cy + inner], fill=palette["primary"])
    # Highlight
    hl = int(r * 0.35)
    draw.ellipse([cx - inner + 6, cy - inner + 6, cx - inner + 6 + hl, cy - inner + 6 + hl],
                 fill=tuple(min(255, c + 60) for c in palette["primary"]))
    # Symbol
    coin_font = _get_font(int(r * 1.1))
    draw.text((cx, cy), symbol, font=coin_font, fill=palette["bg"], anchor="mm")


def _draw_wallet(draw, x, y, w, h, palette):
    """Draw a simple stylized crypto wallet icon."""
    # Wallet body
    draw.rounded_rectangle([x, y, x + w, y + h], radius=14, fill=palette["secondary"])
    draw.rounded_rectangle([x + 6, y + 6, x + w - 6, y + h - 6], radius=10, fill=palette["bg"])
    # Card slot / flap
    flap_h = h // 3
    draw.rounded_rectangle([x + 6, y + h - flap_h - 6, x + w - 6, y + h - 6], radius=8, fill=palette["primary"])
    # Button/clasp circle
    br = 10
    draw.ellipse([x + w - 6 - br * 2, y + h - flap_h // 2 - br, x + w - 6, y + h - flap_h // 2 + br],
                 fill=palette["secondary"])


def _fetch_pexels_photo(query, cache_dir="output/thumbnails/_prop_cache"):
    """Fetch a real stock photo from Pexels (photos API, not videos) and cache it."""
    import requests, hashlib
    from config import PEXELS_API_KEY
    os.makedirs(cache_dir, exist_ok=True)
    cache_key = hashlib.md5(query.encode()).hexdigest()[:10]
    cache_path = os.path.join(cache_dir, f"{cache_key}.jpg")
    if os.path.exists(cache_path):
        return cache_path
    try:
        headers = {"Authorization": PEXELS_API_KEY}
        params = {"query": query, "per_page": 5, "page": random.randint(1, 3)}
        r = requests.get("https://api.pexels.com/v1/search", headers=headers, params=params, timeout=15)
        r.raise_for_status()
        photos = r.json().get("photos", [])
        if not photos:
            return None
        photo = random.choice(photos)
        img_url = photo["src"]["large"]
        img_data = requests.get(img_url, timeout=15).content
        with open(cache_path, "wb") as f:
            f.write(img_data)
        return cache_path
    except Exception as e:
        print(f"Pexels photo fetch failed: {e}")
        return None


def _paste_prop_with_shadow(img_rgba, prop_path, x, y, size, rounded=True):
    """Paste a real photo prop with drop shadow and rounded/circular mask for a polished look."""
    prop = Image.open(prop_path).convert("RGB")
    # Center-crop to square
    w, h = prop.size
    m = min(w, h)
    prop = prop.crop(((w - m) // 2, (h - m) // 2, (w + m) // 2, (h + m) // 2)).resize((size, size))
    prop = ImageEnhance.Contrast(prop).enhance(1.15)
    prop = ImageEnhance.Color(prop).enhance(1.2)

    mask = Image.new("L", (size, size), 0)
    mdraw = ImageDraw.Draw(mask)
    if rounded:
        mdraw.ellipse([0, 0, size, size], fill=255)
    else:
        mdraw.rounded_rectangle([0, 0, size, size], radius=size // 8, fill=255)

    # Drop shadow
    shadow = Image.new("RGBA", (size + 20, size + 20), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow)
    if rounded:
        sdraw.ellipse([10, 14, size + 10, size + 14], fill=(0, 0, 0, 130))
    else:
        sdraw.rounded_rectangle([10, 14, size + 10, size + 14], radius=size // 8, fill=(0, 0, 0, 130))
    shadow = shadow.filter(ImageFilter.GaussianBlur(6))

    img_rgba.paste(shadow, (x - 10, y - 10), shadow)
    img_rgba.paste(prop, (x, y), mask)
    return img_rgba


def _draw_profit_chart(img_rgba, x, y, w, h, palette):
    """Draw a stylized upward-trending profit chart with a glowing green line and profit badge."""
    overlay = Image.new("RGBA", img_rgba.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Chart background panel
    draw.rounded_rectangle([x, y, x + w, y + h], radius=14, fill=(0, 0, 0, 160))

    # Generate a jagged-but-upward line
    points = []
    n = 6
    base_y = y + h - 12
    top_y = y + 12
    for i in range(n):
        px = x + 10 + i * (w - 20) / (n - 1)
        trend = (i / (n - 1))  # 0 -> 1 upward
        jitter = random.uniform(-8, 8)
        py = base_y - trend * (base_y - top_y) + jitter
        points.append((px, py))

    profit_color = (60, 255, 130)
    draw.line(points, fill=profit_color, width=5, joint="curve")
    for px, py in points:
        draw.ellipse([px - 3, py - 3, px + 3, py + 3], fill=profit_color)

    # Filled area under line (subtle)
    poly = points + [(points[-1][0], base_y), (points[0][0], base_y)]
    draw.polygon(poly, fill=profit_color + (40,))

    # Profit badge text (e.g. +347%)
    profit_pct = random.randint(120, 480)
    badge_font = _get_font(30)
    badge_text = f"+{profit_pct}%"
    draw.text((x + w - 12, y + 10), badge_text, font=badge_font, fill=profit_color, anchor="ra")

    img_rgba.paste(overlay, (0, 0), overlay)
    return img_rgba


def _add_crypto_props(img, palette, layout):
    """Add REAL stock photo coin(s) and a wallet/cash prop for an authentic, advanced look."""
    try:
        img_rgba = img.convert("RGBA")

        coin_query = random.choice(["gold coins bitcoin", "bitcoin coin macro", "gold coin stack"])
        wallet_query = random.choice(["leather wallet money", "digital wallet phone", "cash money hand"])

        coin_photo = _fetch_pexels_photo(coin_query)
        wallet_photo = _fetch_pexels_photo(wallet_query)

        # All props confined to the LEFT half so the right side stays clear for the reaction face
        if coin_photo:
            coin_size = 130
            cx, cy = 30, 90
            img_rgba = _paste_prop_with_shadow(img_rgba, coin_photo, cx, cy, coin_size, rounded=True)
            ring_overlay = Image.new("RGBA", img_rgba.size, (0, 0, 0, 0))
            rdraw = ImageDraw.Draw(ring_overlay)
            pad = 10
            for w_ in range(5, 2, -1):
                rdraw.ellipse([cx - pad, cy - pad, cx + coin_size + pad, cy + coin_size + pad],
                              outline=(255, 30, 30, 220), width=w_)
            img_rgba = Image.alpha_composite(img_rgba, ring_overlay)

        if wallet_photo:
            wallet_size = 110
            wx, wy = 30, THUMB_H - 70 - wallet_size - 15
            img_rgba = _paste_prop_with_shadow(img_rgba, wallet_photo, wx, wy, wallet_size, rounded=False)

        chart_w, chart_h = 190, 110
        chart_x = (wx + wallet_size + 15) if wallet_photo else 30
        chart_y = THUMB_H - 70 - chart_h - 15
        img_rgba = _draw_profit_chart(img_rgba, chart_x, chart_y, chart_w, chart_h, palette)
        return img_rgba.convert("RGB")
    except Exception as e:
        print(f"Crypto props add failed: {e}")
        return img


def generate_advanced_thumbnail(title: str, filename: str, output_dir: str = "output/thumbnails", force_palette: str = None, gender: str = "female") -> str | None:
    """Generate a professional unique thumbnail."""
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{filename}.jpg")

    palette = next((p for p in PALETTES if p["name"] == force_palette), None) or random.choice(PALETTES)
    layout = random.choice(LAYOUTS)
    badge = random.choice(BADGE_TEXTS)

    try:
        # ── Base canvas — real blurred background photo for depth ──
        bg_queries = [
            "crypto trading dark background", "stock market neon city",
            "financial technology abstract", "digital money glow",
            "cryptocurrency network dark", "business success dramatic",
        ]
        bg_photo_path = _fetch_pexels_photo(random.choice(bg_queries), cache_dir="output/thumbnails/_bg_cache")
        if bg_photo_path:
            bg_photo = Image.open(bg_photo_path).convert("RGB")
            bw, bh = bg_photo.size
            target_ratio = THUMB_W / THUMB_H
            src_ratio = bw / bh
            if src_ratio > target_ratio:
                new_h = bh
                new_w = int(bh * target_ratio)
            else:
                new_w = bw
                new_h = int(bw / target_ratio)
            left = (bw - new_w) // 2
            top = (bh - new_h) // 2
            bg_photo = bg_photo.crop((left, top, left + new_w, top + new_h)).resize((THUMB_W, THUMB_H))
            bg_photo = bg_photo.filter(ImageFilter.GaussianBlur(6))
            bg_photo = ImageEnhance.Brightness(bg_photo).enhance(0.45)
            bg_photo = ImageEnhance.Color(bg_photo).enhance(1.3)
            # Tint with palette primary color for cohesion
            tint = Image.new("RGB", (THUMB_W, THUMB_H), palette["primary"])
            img = Image.blend(bg_photo, tint, 0.12)
        else:
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
        lines = _wrap_text(title_upper, max_chars=12)

        # Dynamic font size based on line count
        sizes = {1: 110, 2: 82, 3: 62}
        font_size = sizes.get(len(lines), 62)
        title_font = _get_font(font_size)

        line_height = font_size + 20
        total_h = len(lines) * line_height
        start_y = (THUMB_H - total_h) // 2 - 10

        # Adjust x based on layout
        # Always anchor text to the left half so it never collides with the reaction face on the right
        text_x = 50
        panel_pad = 16
        panel_top = start_y - panel_pad
        panel_bottom = start_y + total_h + panel_pad
        panel_right = int(THUMB_W * 0.56)
        panel_overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        pdraw = ImageDraw.Draw(panel_overlay)
        pdraw.rectangle([0, panel_top, panel_right, panel_bottom], fill=(0, 0, 0, 150))
        img = Image.alpha_composite(img.convert("RGBA"), panel_overlay).convert("RGB")
        draw = ImageDraw.Draw(img)
        title_color = (255, 255, 255)

        for i, line in enumerate(lines):
            y = start_y + i * line_height

            # Draw each line with outline + shadow
            _draw_text_with_outline(
                draw, (text_x, y), line, title_font,
                title_color, (0, 0, 0), 4
            )

            # Accent line under first word of first line
            if i == 0:
                first_word = line.split()[0] if line.split() else line
                bbox = draw.textbbox((text_x, y), first_word, font=title_font)
                draw.rectangle(
                    [text_x, bbox[3] + 3, bbox[2], bbox[3] + 8],
                    fill=palette["primary"]
                )

        # ── Crypto props (coins + wallet) ───────────────────
        # Unique seed per video (based on filename) so each thumbnail's reaction face differs
        _reaction_seed = hash(filename) % 100000
        img = _add_reaction_face(img, palette, _reaction_seed)

        img = _add_crypto_props(img, palette, layout)

        # ── Avatar face (host persona) ─────────────────────
        draw = ImageDraw.Draw(img)

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
        img = ImageEnhance.Contrast(img).enhance(1.12)
        img = ImageEnhance.Color(img).enhance(1.1)
        img = ImageEnhance.Sharpness(img).enhance(1.2)

        img.save(output_path, "JPEG", quality=96)
        print(f"✅ Thumbnail: {palette['name']} | {layout}")
        return output_path

    except Exception as e:
        print(f"❌ Thumbnail error: {e}")
        return None
