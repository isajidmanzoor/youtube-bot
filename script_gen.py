# ============================================================
#   SCRIPT_GEN.PY — 100% Unique, 5+ minute videos
# ============================================================

import requests
import json
import random
import os
from config import GROQ_API_KEY, GROQ_MODEL, GROQ_MAX_TOKENS, TOPICS_FILE, CHANNEL_TOPIC

AFFILIATE_LINK = "https://i.mec.me/?c=pt6wsw2v"

TITLE_STYLES = [
    "How I Made ${amount} with Crypto Airdrops in {days} Days - Full Proof",
    "Top {num} Crypto Airdrops Paying Real Money RIGHT NOW in 2025",
    "I Tried {num} Crypto Airdrops for {days} Days - Honest Results",
    "Free Crypto Airdrop Pays ${amount} Daily to Your {wallet} Wallet",
    "{num} Airdrops That Actually Sent Money to My {wallet} - Withdrawal Proof",
    "Crypto Airdrop Secret: How to Earn ${amount} Per Week Step by Step",
    "WARNING: {num} Fake vs Real Crypto Airdrops Fully Exposed 2025",
    "From $0 to ${amount}: My Complete Crypto Airdrop Journey Revealed",
    "Best Crypto Airdrop Strategy to Earn ${amount} Monthly - Beginners Guide",
    "Live Withdrawal Proof: I Made ${amount} from Crypto Airdrops Today",
    "How to Find Legit Crypto Airdrops That Pay Real Money in 2025",
    "{num} Crypto Airdrop Platforms I Use Daily to Earn Passive Income",
]

WALLETS = ["MetaMask", "Trust Wallet", "Phantom", "Binance", "Coinbase Wallet", "OKX Wallet"]
AMOUNTS = ["50", "100", "200", "500", "150", "300", "250", "75", "400", "120"]
DAYS = ["7", "14", "30", "3", "10", "21"]
NUMS = ["5", "7", "10", "3", "8", "12", "6"]
PLATFORMS = ["DeFi", "Web3", "Layer 2", "Solana", "Ethereum", "BSC", "Polygon", "Arbitrum"]

SCRIPT_INTROS = [
    "Hey guys, welcome back to the channel! Today I am going to share something that completely changed my crypto game. I have been doing this for months now and the results are insane.",
    "What is up everyone! I just got back from checking my crypto wallet and you will not believe what I found. Today I am breaking down exactly how I did it step by step.",
    "Hey what is up! Before we start, make sure you stay till the end because I have real withdrawal proof to show you. This is something I wish someone had told me earlier.",
    "Welcome back! Today we are talking about something I get asked about every single day. People keep asking me how I make money with crypto without investing my own money.",
    "Hey everyone! I was super skeptical at first too, but the results I am going to show you today are one hundred percent real. No scams, no fake screenshots, just real earnings.",
    "What is going on guys! So I have been getting a lot of questions about passive crypto income lately. Today I am going to walk you through my entire strategy from start to finish.",
]

SCRIPT_OUTROS = [
    f"So that is everything you need to know to get started with crypto airdrops today. I have left the link in the description below. It is completely free to join and you can start earning within minutes. Click the link, connect your wallet, and start claiming your free crypto. Do not forget to like this video and subscribe for more crypto tips. See you in the next one!",
    f"Alright guys that is a wrap for today. If you want to start earning free crypto like I showed you, the link is right there in the description. Thousands of people are already using this and getting paid daily. It takes less than five minutes to set up. Hit that subscribe button and I will see you in the next video!",
    f"And that is how simple it really is. Stop leaving free money on the table. The link to get started is in the description below. Join today, complete the simple tasks, and watch the tokens roll into your wallet. Make sure you subscribe so you never miss my latest crypto tips. Thanks for watching!",
    f"That is my complete airdrop strategy revealed. Now it is your turn to take action. The link is in the description, it is free, and you can withdraw your earnings anytime. If this video helped you please give it a thumbs up and share it with a friend who needs to hear this. Subscribe and I will see you next time!",
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
    amount2 = random.choice(AMOUNTS)
    platform = random.choice(PLATFORMS)
    days = random.choice(DAYS)
    num = random.choice(NUMS)

    prompt = f"""You are an experienced YouTube crypto educator making a detailed educational video.
Topic: "{topic}"
Title: "{unique_title}"

Write a LONG detailed script (700-800 words minimum) that sounds like a real human speaking.
Include these sections naturally:
1. Hook and intro (use this exact intro: "{intro}")
2. Personal story about discovering airdrops
3. Step by step explanation of {topic}
4. How to use {wallet} for airdrops
5. Tips to maximize earnings on {platform}
6. Common mistakes to avoid
7. Real earnings discussion (mention ${amount} and ${amount2})
8. Outro (use this exact outro: "{outro}")

Return ONLY valid JSON:
{{
    "title": "{unique_title}",
    "description": "In this video I reveal my complete crypto airdrop strategy for {topic}. I show you real withdrawal proofs and step by step how to earn free crypto using {wallet} on {platform}.\\n\\n⏱️ TIMESTAMPS:\\n00:00 - Introduction\\n00:45 - What are Crypto Airdrops\\n01:30 - My Personal Story\\n02:15 - Step by Step Guide\\n03:00 - {wallet} Setup\\n03:45 - Maximizing Earnings\\n04:15 - Common Mistakes\\n04:45 - Withdrawal Proof\\n\\n💰 Start Earning FREE Crypto Today (takes 2 minutes):\\n👉 {AFFILIATE_LINK}\\n\\n✅ 100% FREE to join\\n✅ No investment needed\\n✅ Withdraw anytime\\n✅ Works worldwide\\n\\n#CryptoAirdrop #FreeCrypto #Airdrop2025 #EarnCrypto #PassiveIncome #{wallet.replace(' ','')} #{platform}Airdrop #CryptoTips",
    "tags": ["crypto airdrop 2025", "free crypto", "{topic.lower()[:25]}", "{wallet.lower()}", "airdrop 2025", "earn crypto free", "passive income crypto", "crypto wallet", "{platform.lower()} airdrop", "make money crypto", "free tokens", "crypto tips"],
    "search_query": "{platform.lower()} crypto blockchain",
    "script": "WRITE THE FULL 700-800 WORD SCRIPT HERE starting with the intro I gave you",
    "comment": "🔥 I just withdrew ${amount} using this FREE airdrop! Join here 👉 {AFFILIATE_LINK} ✅ No investment needed - starts paying in minutes!"
}}

IMPORTANT: The script MUST be 700-800 words. Make it sound natural, conversational, educational. Real human voice, no robotic language."""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 3000,
        "temperature": 0.9,
    }

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=45,
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
        print(f"✅ Script generated: {data['title']} ({len(data['script'].split())} words)")
        return data

    except Exception as e:
        print(f"❌ Script gen error: {e}")
        return _fallback_script(topic, unique_title, intro, outro, wallet, amount, platform)


def _fallback_script(topic, title, intro, outro, wallet, amount, platform):
    return {
        "title": title,
        "description": f"Learn how to earn free crypto with airdrops! {topic}\n\n💰 Start Earning Today:\n👉 {AFFILIATE_LINK}\n\n✅ FREE to join ✅ No investment needed\n\n#CryptoAirdrop #FreeCrypto #Airdrop2025",
        "tags": ["crypto airdrop", "free crypto", "earn crypto", "airdrop 2025", "passive income", topic.lower()[:20]],
        "search_query": f"{platform.lower()} crypto",
        "script": f"{intro} Today we are covering {topic} in detail. I have been using {wallet} to collect airdrops on {platform} and earned ${amount} in just days. Let me walk you through everything step by step. First you need to set up your {wallet} wallet if you do not have one already. It is completely free and takes about two minutes. Once your wallet is ready you can start joining airdrop campaigns. The way airdrops work is simple. Crypto projects give away free tokens to attract new users. All you have to do is complete simple tasks like following their social media, joining their telegram, or testing their platform. Each task rewards you with tokens that have real monetary value. The key to maximizing your earnings is to join multiple airdrops at the same time. I typically join between five and ten new airdrops every week. Some pay small amounts and some pay very large amounts. The ones on {platform} have been especially profitable for me lately. The most important thing is to never pay to join an airdrop. Legitimate airdrops are always completely free. If anyone asks you to send crypto to receive crypto that is one hundred percent a scam. I have made all my earnings without investing a single dollar of my own money. Everything came from completing free tasks and claiming tokens. The tokens go directly to my {wallet} wallet and I can withdraw them anytime I want. I have done multiple withdrawals and every single one went through without any issues. If you want to get started today I have left a link in the description. It is the platform I personally use and recommend. It is free to join and you can start earning within minutes. {outro}",
        "comment": f"🔥 FREE CRYPTO AIRDROP - I earned ${amount} with this! Join here 👉 {AFFILIATE_LINK} ✅ No investment needed!",
        "topic": topic,
    }
