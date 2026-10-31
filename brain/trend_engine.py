# ============================================================
#   TREND ENGINE — Auto-detect trending crypto topics
#   Honest, curiosity-driven titles (no fake earnings claims —
#   YouTube suppresses "free money" / fake-proof content as spam)
# ============================================================

import requests
import json
import random
import os
from datetime import datetime

AFFILIATE_LINK = "https://i.mec.me/?c=pt6wsw2v"

# Fallback title templates — curiosity + clear value, no invented income or fake urgency
VIRAL_HOOKS = [
    "Crypto Airdrops Explained in {minutes} Minutes (Beginner Guide)",
    "I Checked {num} Crypto Airdrops - Here Is What Actually Matters",
    "{platform} Airdrops: How Eligibility Really Works",
    "The {num} Airdrop Mistakes That Get Wallets Drained",
    "How to Spot a Fake {platform} Airdrop in 30 Seconds",
    "Are Crypto Airdrops Still Worth Your Time? Honest Breakdown",
    "Airdrop Farming on {platform}: A Realistic Step by Step Guide",
    "{wallet} Setup for Airdrops - Do This Before You Connect Anything",
    "Why Most People Never Qualify for Big Airdrops",
    "Retroactive Airdrops Explained - How Past Projects Picked Winners",
    "What Nobody Tells You About Crypto Airdrop Taxes and Fees",
    "{num} Red Flags That Mean an Airdrop Is a Scam",
    "Testnets to Airdrops: How Early Users Get Noticed",
    "Airdrop Checklist: {num} Things to Verify Before You Claim",
    "Wallet Drainer Scams Explained - Protect Your Airdrop Wallet",
    "How to Track Upcoming Airdrops Without Paying for Tools",
    "{platform} vs Ethereum Airdrops: Which Is Easier for Beginners?",
    "Airdrop Points Programs Explained Simply",
    "Should You Use Multiple Wallets for Airdrops? The Real Risks",
    "How to Read an Airdrop Announcement (and Catch the Catch)",
]

TRENDING_TOPICS = [
    "Crypto Airdrops Explained for Complete Beginners",
    "How to Connect MetaMask Safely for Airdrops",
    "How to Claim Airdrop Tokens on Trust Wallet Step by Step",
    "How to Avoid Fake Crypto Airdrops and Scams",
    "How to Spot Wallet Drainer Links Before You Click",
    "How to Verify if a Crypto Airdrop is Legitimate",
    "Retroactive vs Points-Based Airdrops Explained",
    "How Airdrop Eligibility and Snapshots Work",
    "Best Free Tools to Track Upcoming Crypto Airdrops",
    "How to Find New Crypto Airdrops Early",
    "Layer 2 Airdrops Explained Arbitrum Optimism Base",
    "Solana Airdrops Guide Using Phantom Wallet",
    "Testnets and How They Lead to Airdrops",
    "How to Use Galxe and Zealy Quests Safely",
    "Airdrop Farming Strategy for Beginners With a Small Budget",
    "Gas Fees and Hidden Costs of Airdrop Farming",
    "Should You Use Multiple Wallets for Airdrops",
    "How to Set Up a Separate Burner Wallet for Airdrops",
    "How to Revoke Token Approvals After Claiming Airdrops",
    "What Happens After You Claim an Airdrop Selling vs Holding",
    "How Crypto Airdrops Are Taxed in General",
    "Lessons From Famous Past Airdrops Uniswap Arbitrum Jupiter",
    "Why Most Airdrop Farmers Get Little or Nothing",
    "Telegram and Discord Airdrop Scams Explained",
    "How to Read a Project Whitepaper Before Farming Its Airdrop",
    "DeFi Protocols Without Tokens Yet and Why That Matters",
    "Airdrop Points Programs Explained",
    "How to Stay Organized When Farming Multiple Airdrops",
    "How to Claim Airdrops on Mobile Safely",
    "Crypto Airdrop Security Checklist",
    "Seed Phrase Safety Everything Beginners Must Know",
    "How to Use DeBank to Track Your Wallet Activity",
    "NFT Airdrops Explained and How to Avoid Scam NFTs",
    "Are Crypto Airdrops Still Worth It This Year",
    "How to Evaluate if a Crypto Airdrop is Worth Your Time",
]

WALLETS = ["MetaMask", "Trust Wallet", "Phantom", "Binance Wallet", "Coinbase Wallet", "OKX Wallet"]
PLATFORMS = ["Solana", "Ethereum", "BSC", "Polygon", "Arbitrum", "Optimism", "Avalanche", "Base"]
DAYS = ["7", "14", "3", "10", "21", "5"]
NUMS = ["5", "7", "10", "3", "8", "12", "6", "15"]
MINUTES = ["10", "15", "5", "20", "8", "12"]

INTROS = [
    "Hey guys welcome back! In the next few minutes I am going to walk you through this step by step, including the parts most videos skip.",
    "What is up everyone! Airdrops can be worth your time, but only if you avoid the traps. Let me show you how this really works.",
    "Hey! Quick heads up before we start: this is education, not financial advice. Now let's break this down properly.",
    "Welcome back to the channel! A lot of people ask how airdrops actually work and whether they are worth it. Today I am answering that honestly.",
    "What is going on guys! There is a ton of hype around airdrops, so today we are cutting through it and looking at what actually matters.",
    "Hey everyone! I know there is a lot of scam content out there about crypto. That is exactly why this video focuses on doing it the safe way.",
    "What is up! If you are new to crypto and do not want to risk your savings, airdrops are one place to learn. Here is how to start without getting burned.",
    "Hey guys! By the end of this video you will know exactly how to approach this, and which red flags should make you walk away.",
]

SECTION_HOOKS = [
    "But here is the thing that most people get wrong...",
    "Now this is the part that surprises most beginners...",
    "And this is where it gets really interesting...",
    "I want to stop here for a second because this is super important...",
    "This next part is what separates careful farmers from people who get drained...",
    "Okay so here is the detail that a lot of videos leave out...",
    "Now pay close attention here because this is where people lose money...",
    "This is a very common mistake and I do not want you to make it...",
]

OUTROS = [
    "Alright guys that is everything! The link I use is in the description - it is an affiliate link, so I may earn a small commission at no cost to you. Always verify things yourself. Hit subscribe and I will see you in the next video. Peace!",
    "And there you have it. Remember: never share your seed phrase, and never pay to receive an airdrop. If you want to try the platform I mentioned, the affiliate link is in the description. Like the video if it helped and subscribe for more. See you next time!",
    "That is all for today! Results with airdrops are never guaranteed, so treat this as learning, not a paycheck. The link is in the description if you want to check it out. Subscribe for more honest crypto guides and I will catch you in the next one!",
    "So that is the full breakdown. Take it slow, use a separate wallet, and double check every link. The platform link is in the description and in the pinned comment. Make sure you subscribe so you do not miss the next guide. See you there!",
]


def get_trending_topic():
    """Get a random trending topic."""
    return random.choice(TRENDING_TOPICS)


def _past_titles() -> list:
    """Every title this channel has published (uniqueness memory + brain history)."""
    from brain.uniqueness import seen
    titles = list(seen("title"))
    try:
        brain_file = os.path.expanduser("~/youtube_bot_data/brain_data.json")
        if os.path.exists(brain_file):
            with open(brain_file) as f:
                data = json.load(f)
            titles += [v.get("title", "") for v in data.get("uploaded_videos", [])]
    except Exception:
        pass
    return [t for t in dict.fromkeys(titles) if t]


def _title_is_fresh(title: str, past: list) -> bool:
    from brain.uniqueness import text_similarity, TITLE_SIMILARITY_LIMIT
    return bool(title) and all(text_similarity(title, old) < TITLE_SIMILARITY_LIMIT for old in past)


def generate_viral_title(topic: str = None, platform: str = None, wallet: str = None, video_format: dict = None):
    """Generate a curiosity-driven title that matches the topic and never resembles a past title."""
    past = _past_titles()
    recent_str = "\n".join(f"- {t}" for t in past[-30:]) if past else "None"
    topic_hint = topic or random.choice(TRENDING_TOPICS)
    platform = platform or random.choice(PLATFORMS)
    wallet = wallet or random.choice(WALLETS)
    format_hint = f'\nThe video format is "{video_format["name"]}": {video_format["structure"]}' if video_format else ""

    prompt = f"""You are a YouTube title expert for an honest crypto education channel.

Write 1 YouTube title for a video about: "{topic_hint}"{format_hint}

Rules:
- The title MUST accurately describe that exact topic and format (viewers leave fast if the title over-promises, which kills recommendations)
- Create a curiosity gap the video really answers: an unexpected contrast, a precise question, a hidden detail, or a surprising mistake
- Use a different structure and different key words from ALL of these past titles:
{recent_str}
- NEVER claim personal earnings, withdrawals, dollar amounts made, "free money", "zero investment", or guaranteed results
- No fake urgency (no "ends in X days", "last chance", "act now")
- Max 70 characters, no hashtags, no quotes, at most one ALL-CAPS word
- Mention {platform} or {wallet} only if it fits the topic

Reply with ONLY the title, nothing else."""

    try:
        from config import GROQ_API_KEY, GROQ_MODEL
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        for attempt in range(3):
            payload = {
                "model": GROQ_MODEL, "reasoning_effort": "low",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 400,
                "temperature": 0.9 + attempt * 0.05
            }
            resp = requests.post("https://api.groq.com/openai/v1/chat/completions",
                               headers=headers, json=payload, timeout=15)
            if resp.status_code != 200:
                break
            title = resp.json()["choices"][0]["message"]["content"].strip()
            title = title.strip('"').strip("'").strip()
            if len(title) > 10 and _title_is_fresh(title, past):
                print(f"✅ AI Title: {title}")
                return title
            print(f"⚠️ AI title too close to an old one, retrying: {title}")
    except Exception as e:
        print(f"⚠️ AI title failed, using template: {e}")

    # Topic itself (optionally with the format) is a safe, on-topic fallback
    candidates = [topic] if topic else []
    if topic and video_format:
        candidates.append(f"{topic}: {video_format['name']}")
    for c in candidates:
        if _title_is_fresh(c, past):
            return c

    title = candidates[-1] if candidates else None
    for _ in range(30):
        template = random.choice(VIRAL_HOOKS)
        candidate = template.format(
            days=random.choice(DAYS),
            num=random.choice(NUMS),
            minutes=random.choice(MINUTES),
            platform=platform,
            wallet=wallet,
        )
        if _title_is_fresh(candidate, past):
            return candidate
        title = title or candidate
    return title


def get_random_elements(topic: str = None, video_format: dict = None):
    """Get all random elements for a unique video. Title is generated for `topic`."""
    from brain.uniqueness import pick_fresh
    topic = topic or get_trending_topic()
    wallet = random.choice(WALLETS)
    platform = random.choice(PLATFORMS)
    return {
        "topic": topic,
        "title": generate_viral_title(topic, platform=platform, wallet=wallet, video_format=video_format),
        "format": video_format,
        "wallet": wallet,
        "platform": platform,
        "days": random.choice(DAYS),
        "num": random.choice(NUMS),
        # Style references only — the script writes its own fresh intro/outro
        "intro": pick_fresh("intro_style", INTROS),
        "section_hook": pick_fresh("section_hook", SECTION_HOOKS),
        "outro": pick_fresh("outro_style", OUTROS),
        "affiliate_link": AFFILIATE_LINK,
    }
