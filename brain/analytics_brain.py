# ============================================================
#   ANALYTICS_BRAIN.PY — Real trending topics + self-learning
#   Uses YouTube API to check real video performance
# ============================================================

import json
import os
import random
import requests
from datetime import datetime

BRAIN_FILE = os.path.expanduser("~/youtube_bot_data/brain_data.json")
AFFILIATE_LINK = "https://i.mec.me/?c=pt6wsw2v"

# Base topics — rotated smartly
ALL_TOPICS = [
    "Crypto Airdrops for Beginners - Complete Step by Step Guide",
    "How Much Can You Realistically Earn from Crypto Airdrops",
    "How to Use MetaMask Safely for Crypto Airdrops",
    "Trust Wallet Airdrop Tutorial - Step by Step",
    "What is a Crypto Airdrop and How Does It Actually Work",
    "Layer 2 Airdrops Explained - How Eligibility Works",
    "Real vs Fake Crypto Airdrops - How to Tell the Difference",
    "Ethereum Airdrop Guide - How Qualification Usually Works",
    "DeFi Airdrop Guide for Beginners",
    "Solana Airdrops Explained - Phantom Wallet Walkthrough",
    "How to Track Your Airdrop Activity in One Place",
    "The Hidden Costs of Airdrop Farming - Gas, Time and Risk",
    "Airdrop Scams That Drain Wallets - And How to Avoid Them",
    "How to Cash Out Airdrop Tokens Safely",
]

PALETTES = ["fire","ice","matrix","purple","gold","danger","cyber","royal","toxic","blood","ocean","sunset"]


def _load_brain() -> dict:
    if os.path.exists(BRAIN_FILE):
        try:
            with open(BRAIN_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "video_count": 0,
        "uploaded_videos": [],
        "topic_performance": {},
        "best_palette": None,
        "created_at": datetime.now().isoformat(),
    }


def _save_brain(data: dict):
    os.makedirs(os.path.dirname(BRAIN_FILE), exist_ok=True)
    with open(BRAIN_FILE, "w") as f:
        json.dump(data, f, indent=2)


def record_video(title: str, topic: str, video_id: str, title_style: str, palette: str):
    """Record video — self-learning starts here."""
    brain = _load_brain()
    brain["video_count"] = brain.get("video_count", 0) + 1

    brain.setdefault("uploaded_videos", []).append({
        "title": title,
        "topic": topic,
        "video_id": video_id,
        "palette": palette,
        "uploaded_at": datetime.now().isoformat(),
        "views": 0,  # Will be updated by check_performance()
    })

    # Keep last 100
    brain["uploaded_videos"] = brain["uploaded_videos"][-100:]
    _save_brain(brain)
    print(f"🧠 Brain: Recorded video #{brain['video_count']} — {title[:50]}")


def check_and_learn(youtube_api_key: str = None):
    """Refresh real view counts from YouTube using the OAuth token (1 quota unit per 50 videos)."""
    brain = _load_brain()
    videos = [v for v in brain.get("uploaded_videos", []) if v.get("video_id")]
    if not videos:
        print("🧠 Brain: No videos to analyze yet")
        return
    try:
        import pickle
        from googleapiclient.discovery import build
        with open("youtube_token.pickle", "rb") as f:
            creds = pickle.load(f)
        yt = build("youtube", "v3", credentials=creds, cache_discovery=False)
        view_data = {}
        recent = videos[-50:]
        resp = yt.videos().list(part="statistics", id=",".join(v["video_id"] for v in recent)).execute()
        for item in resp.get("items", []):
            view_data[item["id"]] = int(item.get("statistics", {}).get("viewCount", 0))
        for v in brain["uploaded_videos"]:
            if v.get("video_id") in view_data:
                v["views"] = view_data[v["video_id"]]
        total = sum(view_data.values())
        print(f"🧠 Brain: refreshed {len(view_data)} videos, total views {total}")
        # Only learn a "best palette" when there is real signal, otherwise it is just noise
        if total >= 50:
            pv = {}
            for v in brain["uploaded_videos"]:
                if v.get("palette") and v.get("video_id") in view_data:
                    pv.setdefault(v["palette"], []).append(v.get("views", 0))
            avg = {k: sum(x) / len(x) for k, x in pv.items() if len(x) >= 3}
            if avg:
                brain["best_palette"] = max(avg, key=avg.get)
                print(f"🧠 Brain learned: Best palette = {brain['best_palette']}")
        else:
            brain["best_palette"] = None
        _save_brain(brain)
    except Exception as e:
        print(f"⚠️  Brain analytics failed: {e}")


def get_smart_topic() -> dict:
    """Pick a topic + video format combination that has never been made before."""
    from brain.trend_engine import TRENDING_TOPICS
    from brain.uniqueness import pick_angle, format_details

    brain = _load_brain()

    # Avoid last 30 used topics, and never repeat a topic+format pair
    recent_topics = [v.get("topic", "") for v in brain.get("uploaded_videos", [])[-30:]]
    pool = list(dict.fromkeys(list(ALL_TOPICS) + list(TRENDING_TOPICS)))
    topic, fmt = pick_angle(pool, recent_topics)
    video_format = format_details(fmt)

    # Use best performing palette if we know it, else rotate
    best_palette = brain.get("best_palette")
    recent_palettes = [v.get("palette", "") for v in brain.get("uploaded_videos", [])[-4:]]
    available_palettes = [p for p in PALETTES if p not in recent_palettes]

    if best_palette and random.random() > 0.3:
        # 70% chance use best palette
        recommended_palette = best_palette
    elif available_palettes:
        recommended_palette = random.choice(available_palettes)
    else:
        recommended_palette = random.choice(PALETTES)

    video_num = brain.get("video_count", 0) + 1
    print(f"🧠 Brain: Video #{video_num} | Format: {video_format['name']} | Palette: {recommended_palette}")
    if best_palette:
        print(f"   Best performing palette so far: {best_palette}")

    return {
        "topic": topic,
        "recommended_palette": recommended_palette,
        "video_number": video_num,
        "format": video_format,
    }
