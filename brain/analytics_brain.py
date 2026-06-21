import json, os, random
from datetime import datetime

BRAIN_FILE = "logs/brain_data.json"
AFFILIATE_LINK = "https://i.mec.me/?c=pt6wsw2v"

TRENDING_NOW = [
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
]

PALETTES = ["fire","ice","matrix","purple","gold","danger","cyber","royal","toxic","blood","ocean","sunset"]

def _load_brain():
    if os.path.exists(BRAIN_FILE):
        try:
            with open(BRAIN_FILE) as f: return json.load(f)
        except: pass
    return {"video_count": 0, "top_performing": []}

def _save_brain(data):
    os.makedirs("logs", exist_ok=True)
    with open(BRAIN_FILE, "w") as f: json.dump(data, f, indent=2)

def record_video(title, topic, video_id, title_style, palette):
    brain = _load_brain()
    brain["video_count"] = brain.get("video_count", 0) + 1
    brain.setdefault("top_performing", []).append({
        "title": title, "topic": topic, "video_id": video_id,
        "palette": palette, "uploaded_at": datetime.now().isoformat()
    })
    brain["top_performing"] = brain["top_performing"][-50:]
    _save_brain(brain)
    print(f"🧠 Brain: Recorded video #{brain['video_count']}")

def get_smart_topic():
    brain = _load_brain()
    recent_topics = [v.get("topic","") for v in brain.get("top_performing",[])[-6:]]
    available = [t for t in TRENDING_NOW if t not in recent_topics] or TRENDING_NOW
    recent_palettes = [v.get("palette","") for v in brain.get("top_performing",[])[-4:]]
    available_palettes = [p for p in PALETTES if p not in recent_palettes] or PALETTES
    return {
        "topic": random.choice(available),
        "recommended_palette": random.choice(available_palettes),
        "video_number": brain.get("video_count", 0) + 1,
    }
