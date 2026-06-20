# ============================================================
#   MAIN.PY — Ek video ka poora pipeline chalao
#   Usage: python main.py                  (random topic)
#          python main.py "Custom Topic"   (specific topic)
# ============================================================

import os
import sys
import shutil
import uuid
from datetime import datetime

from script_gen import generate_script
from voice_gen import generate_voiceover, get_audio_duration
from video_fetcher import fetch_pexels_videos
from video_gen import build_video
from thumbnail_gen import generate_thumbnail
from youtube_uploader import upload_video
from logger import logger, log_video, get_today_count
from config import VIDEOS_PER_DAY, CLIP_DURATION


def make_one_video(topic: str = None) -> dict:
    """
    Ek complete video banao aur upload karo.
    Returns: result dict with status and details
    """
    result = {
        "success": False,
        "title": None,
        "video_id": None,
        "error": None,
    }

    run_id = datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + uuid.uuid4().hex[:6]
    clip_dir = f"output/videos/clips_{run_id}"

    try:
        # ── Step 1: Script generate karo ───────────────────────
        logger.info("📝 Step 1/6: Generating script...")
        data = generate_script(topic)
        title = data["title"]
        result["title"] = title
        logger.info(f"   Title: {title}")

        # ── Step 2: Voiceover banao ────────────────────────────
        logger.info("🎙️  Step 2/6: Generating voiceover...")
        audio_path = generate_voiceover(data["script"], run_id)
        if not audio_path:
            raise RuntimeError("Voiceover generation failed")

        # ── Step 3: Stock clips download karo ─────────────────
        logger.info(f"🎬 Step 3/6: Fetching Pexels clips for '{data['search_query']}'...")
        audio_duration = get_audio_duration(audio_path)
        num_clips = max(5, int(audio_duration / CLIP_DURATION) + 2)
        clips = fetch_pexels_videos(data["search_query"], num_clips, clip_dir)
        logger.info(f"   Downloaded {len(clips)} clips")

        # ── Step 4: Video assemble karo ────────────────────────
        logger.info("🎞️  Step 4/6: Building video...")
        video_path = build_video(audio_path, clips, run_id, title)
        if not video_path:
            raise RuntimeError("Video build failed")

        # ── Step 5: Thumbnail banao ────────────────────────────
        logger.info("🖼️  Step 5/6: Generating thumbnail...")
        thumb_path = generate_thumbnail(title, run_id)

        # ── Step 6: YouTube pe upload karo ─────────────────────
        logger.info("⬆️  Step 6/6: Uploading to YouTube...")
        video_id = upload_video(
            video_path=video_path,
            title=title,
            description=data["description"],
            tags=data["tags"],
            thumbnail_path=thumb_path,
        )

        if video_id:
            result["success"] = True
            result["video_id"] = video_id
            log_video(title, data["topic"], video_id, video_path, status="uploaded")
            logger.info(f"🎉 DONE! https://youtube.com/watch?v={video_id}")
        else:
            raise RuntimeError("YouTube upload returned no video ID")

    except Exception as e:
        result["error"] = str(e)
        logger.error(f"❌ Pipeline error: {e}")
        log_video(
            result.get("title") or "Unknown",
            topic or "Unknown",
            None,
            "",
            status="failed",
            error=str(e),
        )

    finally:
        # Cleanup temp clips folder
        if os.path.exists(clip_dir):
            shutil.rmtree(clip_dir, ignore_errors=True)

    return result


def run_daily_batch():
    """
    Aaj ke VIDEOS_PER_DAY videos ek ke baad ek banao.
    (Scheduler ke bina manually chalane ke liye)
    """
    today_count = get_today_count()
    remaining = VIDEOS_PER_DAY - today_count

    if remaining <= 0:
        logger.info(f"✅ Already made {today_count} videos today. Limit reached.")
        return

    logger.info(f"🚀 Making {remaining} videos (already done today: {today_count})")

    for i in range(remaining):
        logger.info(f"\n{'='*50}")
        logger.info(f"VIDEO {i + 1}/{remaining}")
        logger.info(f"{'='*50}")
        result = make_one_video()
        if result["success"]:
            logger.info(f"✅ Video {i+1} done!")
        else:
            logger.error(f"❌ Video {i+1} failed: {result['error']}")


# ── Entry point ───────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) > 1:
        custom_topic = " ".join(sys.argv[1:])
        logger.info(f"🎯 Custom topic: {custom_topic}")
        make_one_video(custom_topic)
    else:
        make_one_video()
