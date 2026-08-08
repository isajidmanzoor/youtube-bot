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
    "How to Get Free Crypto with Zero Investment in 2025",
    "Crypto Airdrops for Beginners - Complete Step by Step Guide",
    "How to Make Your First $100 with Crypto Airdrops",
    "I Claimed 50 Crypto Airdrops - Here Are My Real Results",
    "Live Withdrawal Proof - Crypto Airdrop Actually Paid Me",
    "Best Solana Airdrops Paying Right Now - Don't Miss These",
    "How to Use MetaMask to Claim Crypto Airdrops Daily",
    "Trust Wallet Airdrop Tutorial - Step by Step 2025",
    "How Much Can You Really Earn from Crypto Airdrops",
    "Crypto Airdrop Strategy That Earns Me $200 Per Month",
    "5 Airdrops I Check Every Single Day to Earn Free Crypto",
    "New Crypto Airdrop Just Launched - Join Before It Fills Up",
    "Layer 2 Airdrops are Blowing Up Right Now - Here is Why",
    "What is a Crypto Airdrop and How Does It Actually Work",
    "How I Found a Hidden Airdrop That Paid Me $500",
    "My Crypto Airdrop Journey - From Zero to Consistent Earner",
    "Best Airdrop Platforms That Have Never Scammed Anyone",
    "How to Track All Your Airdrop Earnings in One Place",
    "Web3 Airdrop Season is Back - How to Maximize Your Earnings",
    "I Spent 30 Days Only Using Crypto Airdrops - Results",
    "Ethereum Airdrop Guide - How to Qualify and Earn Free ETH",
    "How to Stack Multiple Crypto Airdrops for Maximum Earnings",
    "Real vs Fake Crypto Airdrops - How to Tell the Difference",
    "DeFi Airdrop Guide for Beginners - Earn Free Tokens Today",
    "How to Withdraw Airdrop Tokens to Your Bank Account",
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
    """
    Check real YouTube performance and learn from it.
    Updates view counts for uploaded videos.
    """
    brain = _load_brain()
    videos = brain.get("uploaded_videos", [])

    if not videos or not youtube_api_key:
        print("🧠 Brain: No videos to analyze yet")
        return

    # Check views for last 10 videos
    recent = [v for v in videos if v.get("video_id")][-10:]
    ids = ",".join([v["video_id"] for v in recent])

    try:
        url = f"https://www.googleapis.com/youtube/v3/videos?part=statistics&id={ids}&key={youtube_api_key}"
        resp = requests.get(url, timeout=15)
        data = resp.json()

        view_data = {}
        for item in data.get("items", []):
            vid = item["id"]
            views = int(item.get("statistics", {}).get("viewCount", 0))
            view_data[vid] = views

        # Update brain with real views
        for v in brain["uploaded_videos"]:
            if v.get("video_id") in view_data:
                v["views"] = view_data[v["video_id"]]

        # Find best performing palette
        palette_views = {}
        for v in brain["uploaded_videos"]:
            p = v.get("palette", "")
            views = v.get("views", 0)
            if p:
                palette_views[p] = palette_views.get(p, 0) + views

        if palette_views:
            brain["best_palette"] = max(palette_views, key=palette_views.get)
            print(f"🧠 Brain learned: Best palette = {brain['best_palette']}")

        _save_brain(brain)
        print(f"🧠 Brain: Updated {len(view_data)} video stats")

    except Exception as e:
        print(f"⚠️  Brain analytics failed: {e}")


def get_smart_topic() -> dict:
    """Smart topic selection based on what has NOT been done recently."""
    brain = _load_brain()

    # Avoid last 30 used topics
    recent_topics = [v.get("topic", "") for v in brain.get("uploaded_videos", [])[-30:]]
    available = [t for t in ALL_TOPICS if t not in recent_topics]
    if not available:
        available = ALL_TOPICS

    topic = random.choice(available)

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
    print(f"🧠 Brain: Video #{video_num} | Topic chosen | Palette: {recommended_palette}")
    if best_palette:
        print(f"   Best performing palette so far: {best_palette}")

    return {
        "topic": topic,
        "recommended_palette": recommended_palette,
        "video_number": video_num,
    }
