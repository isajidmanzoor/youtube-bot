# ============================================================
#   CONFIG.PY — Sirf yahan apni settings daalo
# ============================================================

import os

# ── API Keys ─────────────────────────────────────────────────
GROQ_API_KEY          = os.getenv("GROQ_API_KEY", "YOUR_GROQ_API_KEY")       # groq.com (FREE)
PEXELS_API_KEY        = os.getenv("PEXELS_API_KEY", "YOUR_PEXELS_API_KEY")   # pexels.com/api (FREE)

# ── YouTube OAuth ─────────────────────────────────────────────
YOUTUBE_CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET", "client_secret.json")

# ── Channel Settings ─────────────────────────────────────────
CHANNEL_TOPIC         = os.getenv("CHANNEL_TOPIC", "QA Testing and AI Tools Tips")
VIDEO_LANGUAGE        = os.getenv("VIDEO_LANGUAGE", "en")
VIDEO_CATEGORY_ID     = os.getenv("VIDEO_CATEGORY_ID", "28")
VIDEO_PRIVACY         = os.getenv("VIDEO_PRIVACY", "public")

# ── Voice (Edge TTS FREE) ────────────────────────────────────
ACTIVE_VOICE          = os.getenv("ACTIVE_VOICE", "en-US-GuyNeural")

# ── Video Settings ────────────────────────────────────────────
VIDEOS_PER_DAY        = int(os.getenv("VIDEOS_PER_DAY", "6"))
VIDEO_WIDTH           = int(os.getenv("VIDEO_WIDTH", "1920"))
VIDEO_HEIGHT          = int(os.getenv("VIDEO_HEIGHT", "1080"))
FPS                   = int(os.getenv("FPS", "24"))
CLIP_DURATION         = int(os.getenv("CLIP_DURATION", "4"))

# ── Upload Times (24hr) ──────────────────────────────────────
UPLOAD_TIMES = ["08:00", "11:00", "14:00", "17:00", "19:00", "21:00"]

# ── Groq Model ───────────────────────────────────────────────
GROQ_MODEL            = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_MAX_TOKENS       = int(os.getenv("GROQ_MAX_TOKENS", "3000"))

# ── Paths ────────────────────────────────────────────────────
OUTPUT_DIR            = "output"
VIDEOS_DIR            = "output/videos"
AUDIO_DIR             = "output/audio"
THUMBS_DIR            = "output/thumbnails"
LOGS_DIR              = "logs"
TOPICS_FILE           = "topics/topics.txt"
