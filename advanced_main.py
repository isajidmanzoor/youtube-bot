# ============================================================
#   ADVANCED_MAIN.PY — Full pipeline orchestrator
# ============================================================

import os
import sys
import shutil
import uuid
from datetime import datetime

# Add parent dir to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from advanced_script_gen import generate_advanced_script
from advanced_voice_gen import generate_advanced_voiceover, get_audio_duration
from advanced_thumbnail_gen import generate_advanced_thumbnail
from advanced_video_gen import build_advanced_video

# Import from parent
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from video_fetcher import fetch_pexels_videos
from youtube_uploader import upload_video
from logger import logger, log_video, get_today_count
from config import VIDEOS_PER_DAY, CLIP_DURATION, VIDEOS_DIR, AUDIO_DIR, THUMBS_DIR


def make_advanced_video() -> dict:
    """
    Full advanced pipeline — generates one unique 5+ minute video.
    """
    result = {"success": False, "title": None, "video_id": None, "error": None}

    run_id = datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + uuid.uuid4().hex[:6]
    clip_dir = f"output/videos/clips_{run_id}"

    try:
        # ── Step 1: Generate Advanced Script ──────────────────
        logger.info("🧠 Step 1/6: AI Script Generation...")
        data = generate_advanced_script()
        title = data["title"]
        result["title"] = title
        scenes = data.get("scenes", [])
        logger.info(f"   📝 Title: {title}")
        logger.info(f"   📊 Scenes: {len(scenes)}")
        word_count = len(data["script"].split())
        logger.info(f"   📖 Words: {word_count} (~{word_count//150} min)")

        # ── Step 2: Generate Advanced Voice ───────────────────
        logger.info("🎙️  Step 2/6: Generating Natural Voiceover...")
        audio_path = generate_advanced_voiceover(data["script"], run_id)
        if not audio_path:
            raise RuntimeError("Voiceover generation failed")

        audio_duration = get_audio_duration(audio_path)
        logger.info(f"   ⏱️  Duration: {audio_duration:.1f}s ({audio_duration/60:.1f} min)")

        if audio_duration < 60:
            raise RuntimeError(f"Audio too short: {audio_duration:.1f}s - script may be too short")

        # ── Step 3: Fetch Video Clips ──────────────────────────
        logger.info(f"🎬 Step 3/6: Fetching Stock Clips...")
        search_query = data.get("search_query", "crypto blockchain technology")
        num_clips = max(8, int(audio_duration / 5) + 3)
        clips = fetch_pexels_videos(search_query, num_clips, clip_dir)
        logger.info(f"   ✅ Downloaded {len(clips)} clips")

        # ── Step 4: Build Advanced Video ──────────────────────
        logger.info("🎞️  Step 4/6: Building Advanced Video with Overlays...")
        video_path = build_advanced_video(
            audio_path=audio_path,
            clip_paths=clips,
            filename=run_id,
            scenes=scenes,
            title=title,
        )
        if not video_path:
            raise RuntimeError("Video build failed")

        # ── Step 5: Generate Advanced Thumbnail ───────────────
        logger.info("🖼️  Step 5/6: Generating Professional Thumbnail...")
        thumb_path = generate_advanced_thumbnail(title, run_id, THUMBS_DIR)

        # ── Step 6: Upload to YouTube ──────────────────────────
        logger.info("⬆️  Step 6/6: Uploading to YouTube...")
        video_id = upload_video(
            video_path=video_path,
            title=title,
            description=data["description"],
            tags=data["tags"],
            thumbnail_path=thumb_path,
        )

        # Add pinned comment with affiliate link
        if video_id:
            _add_pinned_comment(video_id, data.get("comment", ""))

        if video_id:
            result["success"] = True
            result["video_id"] = video_id
            log_video(title, data["topic"], video_id, video_path, status="uploaded")
            logger.info(f"🎉 SUCCESS! https://youtube.com/watch?v={video_id}")
            logger.info(f"   ⏱️  Video length: {audio_duration/60:.1f} minutes")
        else:
            raise RuntimeError("Upload failed - no video ID returned")

    except Exception as e:
        result["error"] = str(e)
        logger.error(f"❌ Pipeline error: {e}")
        log_video(
            result.get("title") or "Unknown", "Unknown",
            None, "", status="failed", error=str(e)
        )

    finally:
        if os.path.exists(clip_dir):
            shutil.rmtree(clip_dir, ignore_errors=True)

    return result


def _add_pinned_comment(video_id: str, comment_text: str):
    """Add and pin a comment with the affiliate link."""
    try:
        import pickle
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build

        TOKEN_FILE = "youtube_token.pickle"
        if not os.path.exists(TOKEN_FILE):
            return

        with open(TOKEN_FILE, "rb") as f:
            creds = pickle.load(f)

        if creds.expired and creds.refresh_token:
            creds.refresh(Request())

        service = build("youtube", "v3", credentials=creds)

        if not comment_text:
            comment_text = f"🔥 FREE CRYPTO AIRDROP - No investment needed!\n👉 https://i.mec.me/?c=pt6wsw2v\n✅ Join thousands earning daily!"

        thread = service.commentThreads().insert(
            part="snippet",
            body={
                "snippet": {
                    "videoId": video_id,
                    "topLevelComment": {
                        "snippet": {"textOriginal": comment_text}
                    }
                }
            }
        ).execute()

        comment_id = thread["snippet"]["topLevelComment"]["id"]
        logger.info(f"✅ Comment added: {comment_id}")

    except Exception as e:
        logger.warning(f"⚠️  Comment failed (non-critical): {e}")


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("  ADVANCED YouTube Bot — Starting")
    logger.info("=" * 60)
    result = make_advanced_video()
    if result["success"]:
        logger.info(f"✅ Done! Video: https://youtube.com/watch?v={result['video_id']}")
    else:
        logger.error(f"❌ Failed: {result['error']}")
        exit(1)
