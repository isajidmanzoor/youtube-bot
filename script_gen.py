# ============================================================
#   SCRIPT_GEN.PY — 100% Unique every time
# ============================================================

import requests
import json
import random
import os
from config import GROQ_API_KEY, GROQ_MODEL, GROQ_MAX_TOKENS, TOPICS_FILE, CHANNEL_TOPIC

AFFILIATE_LINK = "https://i.mec.me/?c=pt6wsw2v"

TITLE_STYLES = [
    "How I Made ${amount} with Crypto Airdrops in {days} Days",
    "Top {num} Crypto Airdrops Paying Real Money RIGHT NOW",
    "I Tried {num} Crypto Airdrops - Here's What Happened",
    "Free Crypto Airdrop Pays ${amount} to Your Wallet Daily",
    "{num} Airdrops That Actually Sent Money to My {wallet}",
    "Crypto Airdrop Secret: How to Earn ${amount} Per Week",
    "WARNING: {num} Fake vs Real Crypto Airdrops Exposed",
    "From $0 to ${amount}: My Crypto Airdrop Journey",
    "Best Crypto Airdrop Strategy to Earn ${amount} Monthly",
    "Live Proof: Withdrew ${amount} from Crypto Airdrop Today",
]

WALLETS = ["MetaMask", "Trust Wallet", "Phantom", "Binance", "Coinbase Wallet"]
AMOUNTS = ["50", "100", "200", "500", "150", "300", "250", "75"]
DAYS = ["7", "14", "30", "3", "10"]
NUMS = ["5", "7", "10", "3", "8", "12"]

SCRIPT_INTROS = [
    "Hey guys, welcome back! Today I'm going to share something that completely changed my crypto game.",
    "What's up everyone! I just got back from checking my crypto wallet and you won't believe what happened.",
    "Hey what's up! Before we start, make sure you stay till the end because I have proof to show you.",
    "Welcome back to the channel! Today we are talking about something I get asked about every single day.",
    "Hey everyone! I was skeptical at first too, but the results I'm going to show you are 100% real.",
]

SCRIPT_OUTROS = [
    f"Don't forget to check the link in the description to get started today: {AFFILIATE_LINK}",
    f"I've left the link below in the description. Click it and start earning right now: {AFFILIATE_LINK}",
    f"The link to join is in the description below. Thousands of people are already earning daily: {AFFILIATE_LINK}",
    f"Check out the link in description to claim your free crypto today: {AFFILIATE_LINK}",
]


def get_random_topic():
    try:
        with open(TOPICS_FILE, "r") as f:
            topics = [t.strip() for t in f.readlines() if t.strip()]
        if not topics:
            return f"Tips about {CHANNEL_TOPIC}"
        return random.choice(topics)
    except Exception:
        return f"Tips about {CHANNEL_TOPIC}"


def _random_title():
    style = random.choice(TITLE_STYLES)
    return style.format(
        amount=random.choice(AMOUNTS),
        days=random.choice(DAYS),
        num=random.choice(NUMS),
        wallet=random.choice(WALLETS),
    )


def generate_script(topic=None):
    if not topic:
        topic = get_random_topic()

    unique_title = _random_title()
    intro = random.choice(SCRIPT_INTROS)
    outro = random.choice(SCRIPT_OUTROS)
    wallet = random.choice(WALLETS)
    amount = random.choice(AMOUNTS)
    platform = random.choice(["DeFi", "Web3", "Layer 2", "Solana", "Ethereum", "BSC"])

    prompt = f"""You are a YouTube content creator making videos about crypto airdrops.
Topic: "{topic}"
Use this exact title: "{unique_title}"

Start the script with: "{intro}"
End the script with: "{outro}"

Return ONLY valid JSON:
{{
    "title": "{unique_title}",
    "description": "In this video I show you exactly how to earn free crypto through airdrops. We cover {topic}. I'll show you real wallet screenshots and withdrawal proof using {wallet}. These are legitimate {platform} projects giving away free tokens.\\n\\n💰 Start Earning Today: {AFFILIATE_LINK}\\n\\n#CryptoAirdrop #FreeCrypto #Airdrop2025 #Earn Crypto #PassiveIncome",
    "tags": ["crypto airdrop", "free crypto", "{topic.lower()[:20]}", "{wallet.lower()}", "airdrop 2025", "earn crypto", "passive income", "crypto wallet", "{platform.lower()} airdrop", "make money crypto"],
    "search_query": "{platform.lower()} crypto wallet",
    "script": "{intro} Today we are talking about {topic}. I have been using {wallet} to collect airdrop tokens and the results are amazing. In just {amount} days I collected over ${amount} worth of tokens. The best part is it is completely free to join. You just need a {wallet} wallet and follow the steps I show you. First you need to connect your wallet to the airdrop platform. Then complete simple tasks like following social media accounts or joining telegram groups. Each task gives you tokens worth real money. I have withdrawn multiple times and the money goes straight to my wallet. The key is to be consistent and join new airdrops early before they become popular. Right now there are amazing opportunities in the {platform} space. {outro}",
    "comment": "🔥 FREE CRYPTO AIRDROP - Earn daily! Join here: {AFFILIATE_LINK} ✅ Withdrawals PROOF in video!"
}}

Make the script sound natural, conversational, like a real person sharing experience. 200-220 words total."""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": GROQ_MAX_TOKENS,
        "temperature": 0.9,
    }

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"].strip()

        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        data = json.loads(content)

        required = ["title", "description", "tags", "search_query", "script"]
        for field in required:
            if field not in data:
                raise ValueError(f"Missing field: {field}")

        data["topic"] = topic
        print(f"✅ Script generated: {data['title']}")
        return data

    except Exception as e:
        print(f"❌ Script gen error: {e}")
        return _fallback_script(topic, unique_title, intro, outro)


def _fallback_script(topic, title, intro, outro):
    wallet = random.choice(WALLETS)
    amount = random.choice(AMOUNTS)
    return {
        "title": title,
        "description": f"Learn how to earn free crypto with airdrops! {topic}\n\n💰 Start Earning: {AFFILIATE_LINK}\n\n#CryptoAirdrop #FreeCrypto #Airdrop2025",
        "tags": ["crypto airdrop", "free crypto", "earn crypto", "airdrop 2025", "passive income", topic.lower()],
        "search_query": "crypto wallet money",
        "script": f"{intro} Today we talk about {topic}. Using {wallet} I earned ${amount} from airdrops. The link is in the description. {outro}",
        "comment": f"🔥 FREE CRYPTO - Join here: {AFFILIATE_LINK}",
        "topic": topic,
    }
