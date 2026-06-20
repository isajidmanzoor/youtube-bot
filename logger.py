# ============================================================
#   LOGGER.PY — Clean logging system
# ============================================================

import os
import json
import logging
from datetime import datetime
from config import LOGS_DIR

os.makedirs(LOGS_DIR, exist_ok=True)

# ── Python logger setup ───────────────────────────────────────
_log_file = os.path.join(LOGS_DIR, f"bot_{datetime.now().strftime('%Y%m%d')}.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(_log_file, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("youtube_bot")

# ── Video log JSON ────────────────────────────────────────────
_VIDEO_LOG = os.path.join(LOGS_DIR, "videos.json")


def _load_video_log() -> list:
    if os.path.exists(_VIDEO_LOG):
        try:
            with open(_VIDEO_LOG, "r") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def _save_video_log(data: list):
    with open(_VIDEO_LOG, "w") as f:
        json.dump(data, f, indent=2)


def log_video(
    title: str,
    topic: str,
    video_id: str | None,
    video_path: str,
    status: str = "uploaded",
    error: str = None,
):
    """Video ka record JSON log mein save karo."""
    records = _load_video_log()
    records.append(
        {
            "timestamp": datetime.now().isoformat(),
            "title": title,
            "topic": topic,
            "youtube_id": video_id,
            "video_path": video_path,
            "status": status,
            "error": error,
            "url": f"https://youtube.com/watch?v={video_id}" if video_id else None,
        }
    )
    _save_video_log(records)
    if video_id:
        logger.info(f"Video logged: {title} → https://youtube.com/watch?v={video_id}")
    else:
        logger.error(f"Video failed: {title} | {error}")


def get_today_count() -> int:
    """Aaj kitne videos upload hue."""
    today = datetime.now().strftime("%Y-%m-%d")
    records = _load_video_log()
    return sum(
        1 for r in records
        if r.get("timestamp", "").startswith(today) and r.get("status") == "uploaded"
    )


def print_stats():
    """Summary print karo."""
    records = _load_video_log()
    total = len(records)
    success = sum(1 for r in records if r.get("status") == "uploaded")
    failed = total - success
    logger.info(f"📊 Stats — Total: {total} | Success: {success} | Failed: {failed}")
