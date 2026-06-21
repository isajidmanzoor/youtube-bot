# ============================================================
#   CONFIG.PY — Sirf yahan apni settings daalo
# ============================================================

# ── API Keys ─────────────────────────────────────────────────
GROQ_API_KEY          = "YOUR_GROQ_API_KEY"       # groq.com (FREE)
PEXELS_API_KEY        = "YOUR_PEXELS_API_KEY"     # pexels.com/api (FREE)

# ── YouTube OAuth ─────────────────────────────────────────────
YOUTUBE_CLIENT_SECRET = "client_secret.json"

# ── Channel Settings ─────────────────────────────────────────
CHANNEL_TOPIC         = "QA Testing and AI Tools Tips"
VIDEO_LANGUAGE        = "en"
VIDEO_CATEGORY_ID     = "28"
VIDEO_PRIVACY         = "public"

# ── Voice (Edge TTS FREE) ────────────────────────────────────
ACTIVE_VOICE          = "en-US-GuyNeural"

# ── Video Settings ────────────────────────────────────────────
VIDEOS_PER_DAY        = 6
VIDEO_WIDTH           = 1920
VIDEO_HEIGHT          = 1080
FPS                   = 24
CLIP_DURATION         = 4

# ── Upload Times (24hr) ──────────────────────────────────────
UPLOAD_TIMES = ["08:00", "11:00", "14:00", "17:00", "19:00", "21:00"]

# ── Groq Model ───────────────────────────────────────────────
GROQ_MODEL            = "llama-3.3-70b-versatile"
GROQ_MAX_TOKENS            = 3000

# ── Paths ────────────────────────────────────────────────────
OUTPUT_DIR            = "output"
VIDEOS_DIR            = "output/videos"
AUDIO_DIR             = "output/audio"
THUMBS_DIR            = "output/thumbnails"
LOGS_DIR              = "logs"
TOPICS_FILE           = "topics/topics.txt"
