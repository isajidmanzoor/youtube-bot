import os, sys, shutil, uuid, random, glob
from datetime import datetime

from advanced_script_gen import generate_advanced_script
from advanced_voice_gen import generate_advanced_voiceover, get_audio_duration
from advanced_thumbnail_gen import generate_advanced_thumbnail
from advanced_video_gen import build_advanced_video
from brain.analytics_brain import get_smart_topic, record_video
from music_gen import generate_background_music, mix_audio_with_music
from shorts_gen import create_short, upload_short
from video_fetcher import fetch_pexels_videos
from youtube_uploader import upload_video
from logger import logger, log_video
from config import VIDEOS_DIR, AUDIO_DIR, THUMBS_DIR

AFFILIATE_LINK = "https://i.mec.me/?c=pt6wsw2v"

def make_complete_video():
    result = {"success": False, "title": None, "video_id": None, "short_id": None, "error": None}
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + uuid.uuid4().hex[:6]
    clip_dir = f"output/videos/clips_{run_id}"
    try:
        logger.info("🧠 Step 1/8: Analytics Brain...")
        bd = get_smart_topic()
        topic, palette, vnum = bd["topic"], bd["recommended_palette"], bd["video_number"]
        logger.info(f"   Topic: {topic} | Palette: {palette} | #{vnum}")

        logger.info("📝 Step 2/8: AI Script (5+ min)...")
        data = generate_advanced_script(topic=topic)
        title = data["title"]; result["title"] = title
        logger.info(f"   {title} | {len(data['script'].split())} words")

        logger.info("🎙️  Step 3/8: Natural Voice...")
        raw_audio = generate_advanced_voiceover(data["script"], f"{run_id}_raw")
        if not raw_audio: raise RuntimeError("Voice failed")
        dur = get_audio_duration(raw_audio)
        logger.info(f"   {dur:.1f}s ({dur/60:.1f}min)")

        logger.info("🎵 Step 4/8: Background Music...")
        mood = random.choice(["energetic","exciting","motivational","trustworthy","mysterious"])
        music = generate_background_music(dur+5, mood=mood, filename=f"{run_id}_music")
        os.makedirs(AUDIO_DIR, exist_ok=True)
        final_audio = os.path.join(AUDIO_DIR, f"{run_id}.mp3")
        audio_path = mix_audio_with_music(raw_audio, music, final_audio, 0.07) if music else raw_audio

        logger.info("🎬 Step 5/8: Stock Clips...")
        clips = fetch_pexels_videos(random.choice([data.get("search_query","crypto"),"cryptocurrency wallet","blockchain"]), max(10,int(dur/5)+4), clip_dir)
        logger.info(f"   {len(clips)} clips")

        logger.info("🎞️  Step 6/8: Building Video...")
        video_path = build_advanced_video(audio_path, clips, run_id, data.get("scenes",[]), title)
        if not video_path: raise RuntimeError("Video build failed")

        logger.info("🖼️  Step 7/8: AI Thumbnail...")
        os.makedirs(THUMBS_DIR, exist_ok=True)
        thumb = generate_advanced_thumbnail(title, run_id, THUMBS_DIR, force_palette=palette)

        logger.info("⬆️  Step 8/8: Upload...")
        video_id = upload_video(video_path, title, data["description"], data["tags"], thumb)
        if video_id:
            _pin_comment(video_id, data.get("comment",""))
            record_video(title, topic, video_id, title[:30], palette)
            result.update({"success": True, "video_id": video_id})
            log_video(title, topic, video_id, video_path, status="uploaded")
            logger.info(f"✅ https://youtube.com/watch?v={video_id} ({dur/60:.1f}min | {mood})")
            try:
                sp = create_short(clips[:5], audio_path, title, run_id)
                if sp:
                    sid = upload_short(sp, title, data["description"], data["tags"])
                    if sid: result["short_id"] = sid; logger.info(f"📱 https://youtube.com/shorts/{sid}")
            except Exception as se: logger.warning(f"⚠️ Short: {se}")
        else: raise RuntimeError("Upload failed")
    except Exception as e:
        result["error"] = str(e); logger.error(f"❌ {e}")
        log_video(result.get("title") or "Unknown","Unknown",None,"",status="failed",error=str(e))
    finally:
        if os.path.exists(clip_dir): shutil.rmtree(clip_dir, ignore_errors=True)
        for f in glob.glob(f"output/music/{run_id}*.wav"):
            try: os.remove(f)
            except: pass
    return result

def _pin_comment(video_id, comment_text):
    try:
        import pickle
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
        if not os.path.exists("youtube_token.pickle"): return
        with open("youtube_token.pickle","rb") as f: creds = pickle.load(f)
        if creds.expired and creds.refresh_token: creds.refresh(Request())
        service = build("youtube","v3",credentials=creds)
        if not comment_text: comment_text = f"🔥 FREE CRYPTO!\n👉 {AFFILIATE_LINK}\n✅ No investment needed!"
        service.commentThreads().insert(part="snippet",body={"snippet":{"videoId":video_id,"topLevelComment":{"snippet":{"textOriginal":comment_text}}}}).execute()
        logger.info("✅ Comment pinned")
    except Exception as e: logger.warning(f"⚠️ Comment: {e}")

if __name__ == "__main__":
    logger.info("="*55+"\n  Advanced YouTube Bot v2.0 — ALL Features\n"+"="*55)
    r = make_complete_video()
    if r["success"]:
        logger.info(f"🎉 Main: https://youtube.com/watch?v={r['video_id']}")
        if r.get("short_id"): logger.info(f"📱 Short: https://youtube.com/shorts/{r['short_id']}")
    else:
        logger.error(f"❌ {r['error']}"); exit(1)
