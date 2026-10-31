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
    "GUIDE", "STEP BY STEP", "BEGINNER", "AVOID THIS",
    "WATCH FIRST", "EXPLAINED", "CHECKLIST", "SAFETY",
    "NEW", "HOW TO", "WARNING", "TUTORIAL",
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


REACTION_QUERIES = [
    "shocked man face", "shocked woman face", "surprised man mouth open",
    "surprised woman mouth open", "man hands on head shocked", "woman covering mouth surprised",
    "stunned man looking at phone", "shocked woman looking at phone", "shocked man looking at laptop",
    "surprised woman looking at laptop", "man in disbelief", "woman in disbelief",
    "shocked businessman", "shocked young woman", "amazed man wide eyes",
    "amazed woman wide eyes", "surprised student", "shocked senior man",
    "shocked teenager face", "scared surprised face", "man shouting wow",
    "woman gasping surprised", "worried shocked man", "confused shocked woman",
]


def _face_card(photo_path, palette, height):
    """The photo cropped around the face (upper middle) as a tilted card with a glowing border."""
    photo = Image.open(photo_path).convert("RGB")
    w, h = photo.size
    side = min(w, int(h * 0.8))
    top = int(max(0, min(h - side, h * 0.06)))  # portraits: the face sits in the upper part
    left = (w - side) // 2
    face = photo.crop((left, top, left + side, top + side)).resize((height, height))
    face = ImageEnhance.Contrast(face).enhance(1.2)
    face = ImageEnhance.Color(face).enhance(1.25)
    face = ImageEnhance.Sharpness(face).enhance(1.3)
    border = 12
    card = Image.new("RGBA", (height + 2 * border, height + 2 * border), palette["secondary"] + (255,))
    mask = Image.new("L", (height, height), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, height, height], radius=height // 10, fill=255)
    card.paste(face, (border, border), mask)
    outer = Image.new("L", card.size, 0)
    ImageDraw.Draw(outer).rounded_rectangle([0, 0, card.width, card.height], radius=height // 10 + border, fill=255)
    card.putalpha(outer)
    return card.rotate(random.uniform(-5, 5), expand=True, resample=Image.BICUBIC)


def _add_reaction_face(img, palette, seed_val=None):
    """Add a large shocked reaction face on the right, never the same photo twice.

    With rembg installed the person is cut out (viral thumbnail style);
    otherwise the face is shown as a framed card. Returns (img, added).
    """
    try:
        from brain.uniqueness import pick_fresh, remember
        query = pick_fresh("reaction_query", REACTION_QUERIES)
        photo_path = _fetch_pexels_photo(query, cache_dir="output/thumbnails/_reaction_cache", kind="reaction_photo")
        if not photo_path:
            return img, False
        remember("reaction_query", query)

        cutout_path = photo_path.replace(".jpg", "_cutout.png")
        has_cutout = os.path.exists(cutout_path) or (
            os.path.exists(REMBG_PYTHON) and _remove_background(os.path.abspath(photo_path), os.path.abspath(cutout_path)))
        img_rgba = img.convert("RGBA")
        if has_cutout:
            face = Image.open(cutout_path).convert("RGBA")
            # Where the photo itself cut the person off (head cropped at the top, shoulder
            # at the side) the cutout has a hard straight edge: push that edge off the canvas
            sw, sh = face.size
            box = face.split()[3].point(lambda a: 255 if a > 40 else 0).getbbox() or (0, 0, sw, sh)
            cut_top, cut_right = box[1] <= 2, box[2] >= sw - 2
            face = face.crop(box)
            fw, fh = face.size
            target_h = THUMB_H if cut_top else int(THUMB_H * 0.95)
            target_w = int(fw * (target_h / fh))
            if target_w > int(THUMB_W * 0.55):
                target_w = int(THUMB_W * 0.55)
                target_h = int(fh * (target_w / fw))
            face = face.resize((target_w, target_h))
            face = ImageEnhance.Contrast(face).enhance(1.15)
            face = ImageEnhance.Color(face).enhance(1.2)
            # Always right side (the text owns the left half)
            pos_x = THUMB_W - target_w + (int(target_w * 0.04) if cut_right else -10)
            pos_y = -int(target_h * 0.02) if cut_top else THUMB_H - target_h
        else:
            face = _face_card(photo_path, palette, int(THUMB_H * 0.62))
            pos_x = THUMB_W - face.width - 25
            pos_y = max(60, (THUMB_H - 70 - face.height) // 2 + 15)

        # Soft drop shadow behind the face for depth
        shadow = Image.new("RGBA", face.size, (0, 0, 0, 0))
        shadow.paste((0, 0, 0, 140), (0, 0), face.split()[3])
        shadow = shadow.filter(ImageFilter.GaussianBlur(12))
        img_rgba.paste(shadow, (pos_x + 8, pos_y + 10), shadow)
        img_rgba.paste(face, (pos_x, pos_y), face)
        print(f"   Reaction face: '{query}' ({'cutout' if has_cutout else 'card'})")
        return img_rgba.convert("RGB"), True
    except Exception as e:
        print(f"Reaction face add failed: {e}")
        return img, False


def _add_avatar_to_thumbnail(img, palette, layout, gender="female", size=None):
    """Paste a circular-cropped avatar with a dynamic multi-layer glow border, slight tilt, and grain.
    Returns (img, added)."""
    try:
        avatar_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "avatar")
        face_file = "host_face_male.jpg" if gender == "male" else "host_face_female.jpg"
        face_path = os.path.join(avatar_dir, face_file)
        if not os.path.exists(face_path):
            return img, False

        size = size or random.randint(130, 150)
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

        # Right side, above the bottom bar (the title stays on the left)
        pos_x = THUMB_W - ring.width - 30
        pos_y = max(70, (THUMB_H - 70 - ring.height) // 2 + 20)

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

        return img, True
    except Exception as e:
        print(f"Avatar thumbnail add failed: {e}")
        return img, False


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


USED_PHOTOS_FILE = os.path.expanduser("~/youtube_bot_data/used_photos.json")

def _load_used_photos():
    import json as _json
    try:
        with open(USED_PHOTOS_FILE) as f:
            return set(_json.load(f))
    except Exception:
        return set()

def _remember_photo(pid):
    import json as _json
    if pid is None:
        return
    try:
        os.makedirs(os.path.dirname(USED_PHOTOS_FILE), exist_ok=True)
        ids = list(_load_used_photos())
        ids.append(pid)
        with open(USED_PHOTOS_FILE, "w") as f:
            _json.dump(ids[-300:], f)
    except Exception:
        pass


def _fetch_pexels_photo(query, cache_dir="output/thumbnails/_prop_cache", kind=None):
    """Fetch a real stock photo from Pexels (photos API, not videos) and cache it.

    kind: when given (e.g. "reaction_photo"), a photo used in any past thumbnail
    is never picked again; the id is kept in the uniqueness memory.
    """
    import requests, hashlib
    from config import PEXELS_API_KEY
    os.makedirs(cache_dir, exist_ok=True)
    if kind:
        return _fetch_fresh_photo(query, cache_dir, kind)
    # Add random salt so each run fetches a fresh unique photo
    salt = str(random.randint(1, 999))
    cache_key = hashlib.md5((query + salt).encode()).hexdigest()[:10]
    cache_path = os.path.join(cache_dir, f"{cache_key}.jpg")
    if os.path.exists(cache_path):
        return cache_path
    try:
        headers = {"Authorization": PEXELS_API_KEY}
        params = {"query": query, "per_page": 40, "page": random.randint(1, 4)}
        r = requests.get("https://api.pexels.com/v1/search", headers=headers, params=params, timeout=15)
        r.raise_for_status()
        photos = r.json().get("photos", [])
        if not photos and params["page"] != 1:
            params["page"] = 1
            r = requests.get("https://api.pexels.com/v1/search", headers=headers, params=params, timeout=15)
            r.raise_for_status()
            photos = r.json().get("photos", [])
        if not photos:
            return None
        used = _load_used_photos()
        fresh = [p for p in photos if p.get("id") not in used] or photos
        photo = random.choice(fresh)
        _remember_photo(photo.get("id"))
        img_url = photo["src"]["large"]
        img_data = requests.get(img_url, timeout=15).content
        with open(cache_path, "wb") as f:
            f.write(img_data)
        return cache_path
    except Exception as e:
        print(f"Pexels photo fetch failed: {e}")
        return None


def _fetch_fresh_photo(query, cache_dir, kind):
    """A photo for `query` whose id was never used under `kind`. Looks through up to 4 result pages."""
    import requests
    from config import PEXELS_API_KEY
    from brain.uniqueness import seen, remember
    used = {str(x) for x in seen(kind)} | {str(x) for x in _load_used_photos()}
    headers = {"Authorization": PEXELS_API_KEY}
    try:
        for page in range(1, 5):
            r = requests.get("https://api.pexels.com/v1/search", headers=headers,
                             params={"query": query, "per_page": 40, "page": page, "orientation": "portrait"}, timeout=15)
            r.raise_for_status()
            photos = r.json().get("photos", [])
            fresh = [ph for ph in photos if str(ph.get("id")) not in used]
            if fresh:
                photo = random.choice(fresh[:15])  # the first results match the search best
                path = os.path.join(cache_dir, f"{kind}_{photo.get('id')}.jpg")
                with open(path, "wb") as f:
                    f.write(requests.get(photo["src"]["large"], timeout=15).content)
                remember(kind, str(photo.get("id")))
                _remember_photo(photo.get("id"))
                return path
            if len(photos) < 40:
                break
        print(f"Pexels: no unused photo for '{query}'")
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

    # No percentage label: a made-up profit number is an earnings claim

    img_rgba.paste(overlay, (0, 0), overlay)
    return img_rgba


def _add_crypto_props(img, palette, layout, top=None):
    """Add REAL stock photo coin(s) and a wallet/cash prop for an authentic, advanced look.
    Props sit in one row between `top` and the bottom bar; skipped if there is no room."""
    try:
        row_bottom = THUMB_H - 70 - 15
        size = min(130, row_bottom - (top or 0) - 10)
        if size < 70:
            return img
        img_rgba = img.convert("RGBA")

        coin_query = random.choice(["gold coins bitcoin", "bitcoin coin macro", "gold coin stack"])
        wallet_query = random.choice(["leather wallet money", "digital wallet phone", "cash money hand"])

        coin_photo = _fetch_pexels_photo(coin_query)
        wallet_photo = _fetch_pexels_photo(wallet_query)

        # All props confined to the LEFT half so the right side stays clear for the reaction face
        wallet_size = coin_size = size
        cx, cy = 30, row_bottom - coin_size
        if coin_photo:
            img_rgba = _paste_prop_with_shadow(img_rgba, coin_photo, cx, cy, coin_size, rounded=True)
            ring_overlay = Image.new("RGBA", img_rgba.size, (0, 0, 0, 0))
            rdraw = ImageDraw.Draw(ring_overlay)
            pad = 10
            for w_ in range(5, 2, -1):
                rdraw.ellipse([cx - pad, cy - pad, cx + coin_size + pad, cy + coin_size + pad],
                              outline=(255, 30, 30, 220), width=w_)
            img_rgba = Image.alpha_composite(img_rgba, ring_overlay)

        wx = (cx + coin_size + 30) if coin_photo else 30
        wy = row_bottom - wallet_size
        if wallet_photo:
            img_rgba = _paste_prop_with_shadow(img_rgba, wallet_photo, wx, wy, wallet_size, rounded=False)

        chart_w, chart_h = 190, size
        chart_x = (wx + wallet_size + 20) if wallet_photo else wx
        chart_y = row_bottom - chart_h
        img_rgba = _draw_profit_chart(img_rgba, chart_x, chart_y, chart_w, chart_h, palette)
        return img_rgba.convert("RGB")
    except Exception as e:
        print(f"Crypto props add failed: {e}")
        return img


def _fit_title(draw, text, max_w, max_h, max_lines=3):
    """Largest font where every word fits in max_lines lines inside max_w x max_h. Never drops words."""
    words = text.split()
    for size in range(150, 39, -4):
        font = _get_font(size)
        lines, cur = [], ""
        for w in words:
            trial = f"{cur} {w}".strip()
            if draw.textlength(trial, font=font) <= max_w:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        line_h = int(size * 1.12)
        widest = max(draw.textlength(l, font=font) for l in lines) if lines else 0
        if len(lines) <= max_lines and line_h * len(lines) <= max_h and widest <= max_w:
            return font, size, lines, line_h
    # Too long even at the smallest size: keep the whole words that fit
    font, size = _get_font(40), 40
    lines, cur = [], ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if draw.textlength(trial, font=font) <= max_w:
            cur = trial
        elif len(lines) + 1 < max_lines:
            lines.append(cur)
            cur = w
        else:
            break
    lines.append(cur)
    return font, size, lines, int(size * 1.12)


def _photo_background(path, palette):
    """Cover-crop a photo to the thumbnail size, keep it visible, tint lightly."""
    bg = Image.open(path).convert("RGB")
    bw, bh = bg.size
    target_ratio = THUMB_W / THUMB_H
    if bw / bh > target_ratio:
        new_w, new_h = int(bh * target_ratio), bh
    else:
        new_w, new_h = bw, int(bw / target_ratio)
    left, top = (bw - new_w) // 2, (bh - new_h) // 2
    bg = bg.crop((left, top, left + new_w, top + new_h)).resize((THUMB_W, THUMB_H))
    bg = ImageEnhance.Brightness(bg).enhance(0.8)
    bg = ImageEnhance.Contrast(bg).enhance(1.15)
    bg = ImageEnhance.Color(bg).enhance(1.25)
    tint = Image.new("RGB", (THUMB_W, THUMB_H), palette["primary"])
    return Image.blend(bg, tint, 0.10)


def _layout_overlay(layout, palette):
    """Layout accents as a translucent layer, so the background photo stays visible."""
    fx = Image.new("RGBA", (THUMB_W, THUMB_H), (0, 0, 0, 0))
    d = ImageDraw.Draw(fx)
    p, bgc = palette["primary"], palette["bg"]
    if layout == "split_left":
        d.rectangle([0, 0, THUMB_W // 2, THUMB_H], fill=bgc + (110,))
    elif layout == "split_right":
        d.rectangle([THUMB_W // 2, 0, THUMB_W, THUMB_H], fill=p + (40,))
    elif layout == "center_dramatic":
        for y in range(0, THUMB_H, 4):
            d.rectangle([0, y, THUMB_W, y + 4], fill=p + (int(70 * y / THUMB_H),))
    elif layout == "top_heavy":
        d.rectangle([0, 0, THUMB_W, 90], fill=p + (150,))
    elif layout == "bottom_banner":
        d.rectangle([0, THUMB_H - 190, THUMB_W, THUMB_H - 70], fill=bgc + (120,))
    elif layout == "diagonal_split":
        d.polygon([(0, 0), (THUMB_W * 2 // 3, 0), (THUMB_W // 3, THUMB_H), (0, THUMB_H)], fill=p + (55,))
    elif layout == "frame_border":
        b = 22
        for box in ([0, 0, THUMB_W, b], [0, THUMB_H - b, THUMB_W, THUMB_H], [0, 0, b, THUMB_H], [THUMB_W - b, 0, THUMB_W, THUMB_H]):
            d.rectangle(box, fill=p + (255,))
    elif layout == "spotlight":
        for r in range(420, 0, -20):
            a = int(60 * (1 - r / 420))
            d.ellipse([THUMB_W * 3 // 4 - r, THUMB_H // 2 - r, THUMB_W * 3 // 4 + r, THUMB_H // 2 + r], fill=p + (a,))
    # Readability: darken behind the title (left side) with a soft gradient
    for x in range(0, int(THUMB_W * 0.62), 4):
        a = int(185 * (1 - x / (THUMB_W * 0.62)) ** 0.8)
        d.rectangle([x, 0, x + 4, THUMB_H], fill=(0, 0, 0, a))
    return fx


def _accent_word(words):
    """The word to highlight: one with a number, else the longest."""
    with_digit = [i for i, w in enumerate(words) if any(c.isdigit() for c in w)]
    if with_digit:
        return with_digit[0]
    return max(range(len(words)), key=lambda i: len(words[i])) if words else -1


def _readable_on(color):
    """Black or white, whichever reads better on `color`."""
    return (0, 0, 0) if sum(color) > 450 else (255, 255, 255)


def generate_advanced_thumbnail(title: str, filename: str, output_dir: str = "output/thumbnails", force_palette: str = None,
                                gender: str = "female", bg_image: str = None, bg_query: str = None) -> str | None:
    """Generate a professional unique thumbnail.

    title: the short thumbnail text (2-5 words work best; longer text is shrunk, never cut).
    bg_image: a frame from the video itself, so the thumbnail shows what the video shows.
    bg_query: Pexels photo search used when there is no frame.
    """
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{filename}.jpg")

    palette = next((p for p in PALETTES if p["name"] == force_palette), None) or random.choice(PALETTES)
    from brain.uniqueness import pick_fresh, remember
    layout = pick_fresh("thumb_layout", LAYOUTS)
    badge = pick_fresh("thumb_badge", BADGE_TEXTS)

    try:
        # ── Background: the video's own frame, else a stock photo ──
        bg_queries = [
            "crypto trading dark background", "stock market neon city",
            "financial technology abstract", "digital money glow",
            "cryptocurrency network dark", "business success dramatic",
            "bitcoin blockchain neon", "trading screen candlestick chart",
            "futuristic city night lights", "abstract digital grid dark",
            "gold coins dark background", "server room blue light",
            "glowing data network", "city skyline night finance",
            "dark abstract particles", "neon circuit board",
        ]
        style_query = pick_fresh("thumb_bg_query", bg_queries)
        from_frame = bool(bg_image and os.path.exists(bg_image))
        bg_photo_path = bg_image if from_frame else _fetch_pexels_photo(bg_query or style_query, cache_dir="output/thumbnails/_bg_cache")
        if bg_photo_path:
            img = _photo_background(bg_photo_path, palette)
        else:
            img = Image.new("RGB", (THUMB_W, THUMB_H), palette["bg"])
            _draw_gradient(img, palette["bg"], tuple(c // 3 for c in palette["primary"]))

        img = Image.alpha_composite(img.convert("RGBA"), _layout_overlay(layout, palette)).convert("RGB")
        draw = ImageDraw.Draw(img)

        # ── Subtle particles and a corner glow on the right (the title owns the left) ──
        for _ in range(random.randint(8, 16)):
            px = random.randint(THUMB_W // 2, THUMB_W)
            py = random.randint(0, THUMB_H - 80)
            pr = random.randint(2, 7)
            draw.ellipse([px - pr, py - pr, px + pr, py + pr], fill=palette["secondary"])
        corner = random.choice([(THUMB_W, 0), (THUMB_W, THUMB_H)])
        glow = Image.new("RGBA", (THUMB_W, THUMB_H), (0, 0, 0, 0))
        gdraw = ImageDraw.Draw(glow)
        for r in range(260, 0, -26):
            gdraw.ellipse([corner[0] - r, corner[1] - r, corner[0] + r, corner[1] + r],
                          fill=palette["primary"] + (int(50 * (1 - r / 260)),))
        img = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")

        # ── Right side: reaction cutout, else the host avatar ──
        img, has_face = _add_reaction_face(img, palette)
        if not has_face:
            img, has_face = _add_avatar_to_thumbnail(img, palette, layout, gender, size=300)
        draw = ImageDraw.Draw(img)

        # ── BADGE (top left, sized to its text) ──
        badge_font = _get_font(36)
        bb = draw.textbbox((0, 0), badge, font=badge_font)
        bw_, bh_ = bb[2] - bb[0] + 32, bb[3] - bb[1] + 22
        bx, by = 30, 26
        draw.rectangle([bx - 3, by - 3, bx + bw_ + 3, by + bh_ + 3], fill=palette["secondary"])
        draw.rectangle([bx, by, bx + bw_, by + bh_], fill=palette["primary"])
        draw.text((bx + bw_ // 2, by + bh_ // 2), badge, font=badge_font, fill=_readable_on(palette["primary"]), anchor="mm")

        # ── Channel watermark ──
        wm_font = _get_font(22)
        _draw_text_with_outline(draw, (THUMB_W - 330, 34), "CRYPTO AIRDROP DAILY", wm_font, (255, 255, 255), (0, 0, 0), 2)

        # ── MAIN TEXT: auto-sized so every word fits, one word highlighted ──
        text = " ".join(str(title).upper().split())
        text_x = 40
        max_w = int(THUMB_W * (0.56 if has_face else 0.88)) - text_x
        area_top = by + bh_ + 30
        area_h = THUMB_H - 70 - 30 - area_top - 150  # leave a strip for the props
        title_font, font_size, lines, line_h = _fit_title(draw, text, max_w, area_h)
        total_h = line_h * len(lines)
        start_y = area_top + max(0, (area_h - total_h) // 2)
        accent = _accent_word(text.split())
        accent_color = palette["secondary"] if sum(palette["secondary"]) > 250 else (255, 230, 0)
        word_i = 0
        for i, line in enumerate(lines):
            y = start_y + i * line_h
            x = text_x
            for w in line.split():
                color = accent_color if word_i == accent else (255, 255, 255)
                _draw_text_with_outline(draw, (x, y), w, title_font, color, (0, 0, 0), max(3, font_size // 22))
                x += draw.textlength(w + " ", font=title_font)
                word_i += 1
        text_bottom = start_y + total_h

        # ── Crypto props (coins + wallet) in the strip under the text ──
        img = _add_crypto_props(img, palette, layout, top=text_bottom + 15)
        draw = ImageDraw.Draw(img)

        # ── Bottom accent bar ──
        bar_h = 70
        draw.rectangle([0, THUMB_H - bar_h, THUMB_W, THUMB_H], fill=palette["primary"])
        earn_font = _get_font(32)
        earn_texts = [
            "STEP BY STEP GUIDE",
            "BEGINNER FRIENDLY WALKTHROUGH",
            "WHAT MOST PEOPLE GET WRONG",
            "AVOID THESE MISTAKES",
            "FULL GUIDE + SAFETY CHECKLIST",
        ]
        earn_text = pick_fresh("thumb_bar", earn_texts)
        draw.text((THUMB_W // 2, THUMB_H - bar_h // 2), earn_text,
                 font=earn_font, fill=_readable_on(palette["primary"]), anchor="mm")

        # ── Save ──
        img = ImageEnhance.Contrast(img).enhance(1.08)
        img = ImageEnhance.Sharpness(img).enhance(1.2)

        for quality in (95, 88, 80, 70):
            img.save(output_path, "JPEG", quality=quality, optimize=True)
            if os.path.getsize(output_path) < 1_900_000:  # YouTube limit is 2MB
                break
        # Remember the style so the next thumbnails rotate to unused ones
        remember("thumb_layout", layout)
        remember("thumb_badge", badge)
        remember("thumb_bg_query", style_query)
        remember("thumb_bar", earn_text)
        print(f"✅ Thumbnail: {palette['name']} | {layout} | {'video frame' if from_frame else 'photo'} bg | {font_size}px text")
        return output_path

    except Exception as e:
        print(f"❌ Thumbnail error: {e}")
        return None
