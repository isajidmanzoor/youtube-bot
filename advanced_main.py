import os, sys, shutil, uuid, random, glob
from datetime import datetime

from advanced_script_gen import generate_advanced_script
from advanced_voice_gen import generate_advanced_voiceover, get_audio_duration
from advanced_thumbnail_gen import generate_advanced_thumbnail
from advanced_video_gen import build_advanced_video
from brain.analytics_brain import get_smart_topic, record_video, check_and_learn
from brain.uniqueness import pick_fresh, record_video_memory, uniqueness_report
from brain.global_intelligence import (
    build_global_intelligence,
    enhance_script_data,
    evaluate_content_quality,
    update_studio_dashboard,
)
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
        logger.info("🧠 Step 1/9: Analytics Brain...")
        bd = get_smart_topic()
        topic, palette, vnum = bd["topic"], bd["recommended_palette"], bd["video_number"]
        logger.info(f"   Topic: {topic} | Palette: {palette} | #{vnum}")

        logger.info("🌐 Step 2/9: Global Trend Intelligence...")
        intelligence = build_global_intelligence(topic=topic, video_number=vnum)
        update_studio_dashboard("script_generation", intelligence)
        logger.info(
            f"   Research agents: {intelligence['research_swarm']['agent_count']} | "
            f"Viral probability: {intelligence['viral_probability_ai']['viral_probability']}%"
        )

        logger.info("📝 Step 3/9: AI Script Laboratory (5+ min)...")
        data = generate_advanced_script(topic=topic, intelligence=intelligence, video_format=bd.get("format"))
        data = enhance_script_data(data, intelligence)
        title = data["title"]; result["title"] = title
        logger.info(f"   {title} | {len(data['script'].split())} words")

        logger.info("🧪 Step 4/9: Quality Gate...")
        content_gate = evaluate_content_quality(data, intelligence)
        data["quality_gate"] = content_gate
        logger.info(f"   Scores: {content_gate['scores']}")
        if not content_gate["approved"]:
            raise RuntimeError("Quality gate failed: " + "; ".join(content_gate["blockers"]))
        uniq = data.get("uniqueness") or uniqueness_report(data)
        logger.info(f"   Uniqueness: overlap with past scripts {uniq['script_overlap']:.0%} | format: {data['format']['name']}")
        if not uniq["unique"]:
            raise RuntimeError("Uniqueness gate failed: " + "; ".join(uniq["problems"]))

        logger.info("🎙️  Step 5/9: Natural Voice...")
        update_studio_dashboard("voice_generation")
        persona_gender = random.choice(["male", "female"])
        logger.info(f"   Persona: {persona_gender}")
        raw_audio = generate_advanced_voiceover(
            data["script"],
            f"{run_id}_raw",
            voice_profile=data.get("studio_directives", {}).get("voice"),
            gender=persona_gender,
        )
        if not raw_audio: raise RuntimeError("Voice failed")
        dur = get_audio_duration(raw_audio)
        logger.info(f"   {dur:.1f}s ({dur/60:.1f}min)")

        logger.info("🎵 Step 6/9: Background Music...")
        mood = intelligence.get("music_director", {}).get("mood") or random.choice(["energetic","exciting","motivational","trustworthy","mysterious"])
        music = generate_background_music(dur+5, mood=mood, filename=f"{run_id}_music")
        os.makedirs(AUDIO_DIR, exist_ok=True)
        final_audio = os.path.join(AUDIO_DIR, f"{run_id}.mp3")
        audio_path = mix_audio_with_music(raw_audio, music, final_audio, 0.07) if music else raw_audio

        logger.info("🎬 Step 7/9: Stock Clips...")
        update_studio_dashboard("researching_visuals")
        query_pool = [
            data.get("search_query", "crypto"),
            "cryptocurrency wallet", "blockchain technology", "bitcoin trading",
            "digital finance", "crypto investor", "money technology",
            "fintech app", "online banking", "stock market trading",
            "business laptop working", "financial charts graph",
            "crypto mining rig", "ethereum coin", "digital currency exchange",
            "trading desk monitors", "smartphone banking app", "crypto chart analysis",
            "hands typing laptop", "business success money", "cash counting hands",
            "office team meeting", "startup entrepreneur", "modern office workspace",
            "data server room", "network technology abstract", "digital wallet phone",
            "credit card payment", "investment growth chart", "handshake business deal",
            "coding programmer screen", "crypto coins closeup", "gold coins stack",
            "financial advisor meeting", "stock exchange floor", "young entrepreneur working",
            "cryptocurrency mining farm", "digital transformation business", "fintech startup office",
            "money growth concept", "blockchain network visualization", "crypto trader desk setup",
            "wallet app interface", "banking technology future",
        ]
        # Enough footage that no shot repeats inside the video (~1 clip per 12s),
        # from this video's own scene visuals first, then least-used pool queries
        total_needed = max(6, int(dur / 12))
        scene_queries = [s.get("visual") for s in data.get("scenes", []) if s.get("visual")]
        queries = list(dict.fromkeys([q for q in [data.get("search_query")] + scene_queries if q]))
        clips, used_queries = [], []
        for _ in range(12):
            if len(clips) >= total_needed:
                break
            q = queries.pop(0) if queries else pick_fresh("clip_query", query_pool)
            if q in used_queries:
                q = pick_fresh("clip_query", [x for x in query_pool if x not in used_queries] or query_pool)
            used_queries.append(q)
            exclude = {os.path.basename(c)[7:-4] for c in clips}
            clips += fetch_pexels_videos(q, min(5, total_needed - len(clips)), clip_dir, exclude_ids=exclude)
        logger.info(f"   {len(clips)} unique clips from {len(used_queries)} searches")

        logger.info("🎞️  Step 8/9: Building Video...")
        update_studio_dashboard("rendering")
        video_path = build_advanced_video(
            audio_path,
            clips,
            run_id,
            data.get("scenes", []),
            title,
            film_directives=data.get("studio_directives", {}).get("sentence_directions", []),
        )
        if not video_path: raise RuntimeError("Video build failed")

        # Add captions to video
        try:
            from caption_gen import add_captions_to_video
            logger.info("📝 Adding captions to video...")
            captioned_path = video_path.replace(".mp4", "_captioned.mp4")
            video_path = add_captions_to_video(video_path, audio_path, captioned_path)
            logger.info(f"   Captions added: {video_path}")
        except Exception as e:
            logger.info(f"   Captions skipped: {e}")

        # Add breaking news ticker
        try:
            from moviepy.editor import VideoFileClip
            from news_ticker import add_news_ticker
            from news_fetcher import get_latest_crypto_news
            logger.info("📰 Adding breaking news ticker...")
            headlines = get_latest_crypto_news(limit=5)
            if headlines:
                clip = VideoFileClip(video_path)
                ticker_video = add_news_ticker(clip, headlines)
                ticker_path = video_path.replace(".mp4", "_ticker.mp4")
                ticker_video.write_videofile(ticker_path, fps=clip.fps, codec="libx264", audio_codec="aac", logger=None)
                clip.close()
                ticker_video.close()
                video_path = ticker_path
                logger.info(f"   News ticker added: {video_path}")
        except Exception as e:
            logger.info(f"   News ticker skipped: {e}")




        logger.info("🖼️  Step 9/9: AI Thumbnail + Upload Brain...")
        os.makedirs(THUMBS_DIR, exist_ok=True)
        # Thumbnail carries the short curiosity text, so it adds to the title instead of repeating it
        thumb = generate_advanced_thumbnail(data.get("thumbnail_text") or title, run_id, THUMBS_DIR, force_palette=palette, gender=persona_gender)

        logger.info("⬆️  Uploading...")
        update_studio_dashboard("uploading")
        video_id = upload_video(video_path, title, data["description"], data["tags"], thumb)
        if video_id:
            _pin_comment(video_id, data.get("comment",""))
            record_video(title, topic, video_id, title[:30], palette)
            record_video_memory(data, extra={
                "clip_id": [os.path.basename(c)[7:-4] for c in clips if os.path.basename(c).startswith("pexels_")],
                "clip_query": used_queries,
            })
            check_and_learn()
            update_studio_dashboard("uploaded", intelligence)
            result.update({"success": True, "video_id": video_id})
            log_video(title, topic, video_id, video_path, status="uploaded")
            logger.info(f"✅ https://youtube.com/watch?v={video_id} ({dur/60:.1f}min | {mood})")
            try:
                sp = create_short(clips[:5], audio_path, title, run_id, hook=data.get("thumbnail_text"))
                if sp:
                    sid = upload_short(sp, title, data["description"], data["tags"])
                    if sid: result["short_id"] = sid; logger.info(f"📱 https://youtube.com/shorts/{sid}")
            except Exception as se: logger.warning(f"⚠️ Short: {se}")
            try:
                from comment_replier import reply_to_comments
                import json
                brain_file = os.path.expanduser("~/youtube_bot_data/brain_data.json")
                if os.path.exists(brain_file):
                    with open(brain_file) as bf:
                        brain = json.load(bf)
                    for v in brain.get("uploaded_videos", [])[-5:]:
                        vid_id = v.get("video_id")
                        if vid_id:
                            replied = reply_to_comments(vid_id, v.get("topic", "crypto airdrops"), max_replies=3)
                            logger.info(f"   Auto-replied to {replied} comments on {vid_id}")
            except Exception as e:
                logger.info(f"   Auto-reply skipped: {e}")
        else: raise RuntimeError("Upload failed")
    except Exception as e:
        result["error"] = str(e); logger.error(f"❌ {e}")
        update_studio_dashboard("failed", error=str(e))
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
        if not comment_text: comment_text = f"What should I cover next? 👇\n\n🔗 Platform from the video (affiliate): {AFFILIATE_LINK}\n🛡️ Verify official links and never share your seed phrase."
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
