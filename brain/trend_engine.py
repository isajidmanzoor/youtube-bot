# ============================================================
#   TREND ENGINE — Auto-detect trending crypto topics
# ============================================================

import requests
import json
import random
import os
from datetime import datetime

AFFILIATE_LINK = "https://i.mec.me/?c=pt6wsw2v"

# Trending topic templates with viral hooks
VIRAL_HOOKS = [
    "Nobody Is Talking About This ${amount} Crypto Airdrop (But They Should)",
    "I Found a HIDDEN Crypto Airdrop That Paid Me ${amount} Overnight",
    "This Crypto Airdrop Made Me ${amount} While I Was SLEEPING",
    "URGENT: This Free Crypto Airdrop Ends in {days} Days - Claim Now",
    "I Tested {num} Crypto Airdrops So You Don't Have To - SHOCKING Results",
    "The ${amount} Crypto Airdrop That EVERYONE Is Missing Right Now",
    "How a 17 Year Old Made ${amount} With Free Crypto Airdrops",
    "MILLIONAIRES Are Using This {platform} Airdrop Strategy (Now You Can Too)",
    "This ${amount} Airdrop Took Me Only {minutes} Minutes to Claim",
    "EXPOSED: The Real Truth About Crypto Airdrops and How I Made ${amount}",
    "Watch Me Claim ${amount} in Free Crypto LIVE - Step By Step",
    "The Crypto Airdrop Strategy That Made Me ${amount} With ZERO Investment",
    "WARNING: You Are Losing ${amount} Every Month By NOT Doing Crypto Airdrops",
    "From Broke to ${amount}: My Complete Crypto Airdrop Story",
    "This {platform} Airdrop is Giving Away ${amount} to Early Users - Join Now",
]

TRENDING_TOPICS = [
    "How to Earn Free Crypto with Airdrops in 2025",
    "Best Crypto Airdrops Paying Real Money This Week",
    "How to Connect MetaMask Wallet for Airdrops",
    "Top Binance Wallet Airdrops You Must Join Today",
    "How to Claim Airdrop Tokens on Trust Wallet",
    "Best DeFi Airdrops Paying Real Money Right Now",
    "How to Withdraw Airdrop Earnings to Your Bank",
    "Top Web3 Airdrops Paying in USDT and BTC",
    "How to Avoid Fake Crypto Airdrops and Scams",
    "Best Layer 2 Airdrops You Can Join for Free",
    "How to Maximize Airdrop Earnings with Multiple Wallets",
    "Top NFT Airdrops That Are Paying Real Crypto",
    "How to Join Telegram Airdrops and Get Paid",
    "Best New Crypto Projects Giving Free Tokens",
    "How to Convert Airdrop Tokens to Real Money",
    "Top Solana Airdrops Paying This Month",
    "How to Earn Passive Income with Crypto Airdrops",
    "Best Ethereum Airdrops You Can Claim Today",
    "How to Get Whitelisted for Exclusive Airdrops",
    "Real Airdrop Earnings Proof and Withdrawal Guide",
    "Crypto Airdrop Tutorial for Complete Beginners",
    "How Much Money Can You Make From Crypto Airdrops",
    "Best Crypto Airdrop Tracker Apps and Websites",
    "How to Find New Crypto Airdrops Before Everyone Else",
    "Top 5 Crypto Airdrops with Highest Token Value",
]

WALLETS = ["MetaMask", "Trust Wallet", "Phantom", "Binance Wallet", "Coinbase Wallet", "OKX Wallet"]
PLATFORMS = ["Solana", "Ethereum", "BSC", "Polygon", "Arbitrum", "Optimism", "Avalanche", "Base"]
AMOUNTS = ["50", "100", "200", "500", "150", "300", "250", "75", "400", "120", "350", "450"]
DAYS = ["7", "14", "3", "10", "21", "5"]
NUMS = ["5", "7", "10", "3", "8", "12", "6", "15"]
MINUTES = ["10", "15", "5", "20", "8", "12"]

INTROS = [
    "Hey guys welcome back! What I am about to show you today took me months to figure out but you are going to learn it in the next five minutes.",
    "What is up everyone! Stop what you are doing right now because this video could literally change your financial situation starting today.",
    "Hey! Before I get into this I just want to say that everything I am showing you is one hundred percent real. I have the withdrawal receipts to prove it.",
    "Welcome back to the channel! I get hundreds of messages every week asking me how I make money with crypto without risking my own money. Today I am finally revealing everything.",
    "What is going on guys! So I have been quietly making money with crypto airdrops for over a year now and I decided it is time to share my entire strategy with you.",
    "Hey everyone! I know there is a lot of scam content out there about making money with crypto. That is exactly why I made this video - to show you what actually works.",
    "What is up! I remember when I first started in crypto I had no money to invest. Then I discovered airdrops and everything changed. Let me show you exactly what I did.",
    "Hey guys! Today is going to be one of those videos you watch and then immediately share with your friends. I am showing you how to get free crypto that you can actually withdraw.",
]

SECTION_HOOKS = [
    "But here is the thing that most people get wrong...",
    "Now this is the part that blew my mind when I first discovered it...",
    "And this is where it gets really interesting...",
    "I want to stop here for a second because this is super important...",
    "This next part is what separates people who actually make money from those who do not...",
    "Okay so here is the secret that nobody talks about...",
    "Now pay close attention here because this changed everything for me...",
    "This is the mistake I made when I first started and I do not want you to make it too...",
]

OUTROS = [
    f"Alright guys that is everything! The link to get started is right in the description below. It is completely free, takes about two minutes to set up, and you can start claiming tokens today. I check this platform every single day and it has never let me down. Hit that subscribe button and I will see you in the next video. Peace!",
    f"And there you have it - my complete strategy revealed. Now the ball is in your court. The link is in the description, join for free, connect your wallet, and start earning. Thousands of people are already doing this and getting paid daily. If you found this helpful please like the video and subscribe. See you next time!",
    f"That is all for today! Look I know it sounds too good to be true but I showed you the real numbers. The link is in the description. Click it, sign up for free, and start earning. You have nothing to lose because it costs absolutely nothing. Subscribe for more real crypto tips and I will catch you in the next one!",
    f"So that is my complete airdrop playbook. I have been using this exact strategy for months and I have never had a withdrawal fail. The link to join is in the description below. It is free, it works, and you can start today. Make sure you subscribe so you do not miss my next video where I reveal even more crypto earning strategies. See you there!",
]


def get_trending_topic():
    """Get a random trending topic."""
    return random.choice(TRENDING_TOPICS)


def generate_viral_title():
    """Generate a viral title with random variables, avoiding recent exact repeats."""
    recent_titles = []
    try:
        import json, os
        brain_file = os.path.expanduser("~/youtube_bot_data/brain_data.json")
        if os.path.exists(brain_file):
            with open(brain_file) as f:
                data = json.load(f)
            recent_titles = [v.get("title", "") for v in data.get("uploaded_videos", [])[-6:]]
    except Exception:
        pass

    for _ in range(15):
        template = random.choice(VIRAL_HOOKS)
        title = template.format(
            amount=random.choice(AMOUNTS),
            days=random.choice(DAYS),
            num=random.choice(NUMS),
            minutes=random.choice(MINUTES),
            platform=random.choice(PLATFORMS),
        )
        if title not in recent_titles:
            return title
    return title


def get_random_elements():
    """Get all random elements for a unique video."""
    return {
        "topic": get_trending_topic(),
        "title": generate_viral_title(),
        "wallet": random.choice(WALLETS),
        "platform": random.choice(PLATFORMS),
        "amount": random.choice(AMOUNTS),
        "amount2": random.choice(AMOUNTS),
        "days": random.choice(DAYS),
        "num": random.choice(NUMS),
        "intro": random.choice(INTROS),
        "section_hook": random.choice(SECTION_HOOKS),
        "outro": random.choice(OUTROS),
        "affiliate_link": AFFILIATE_LINK,
    }
