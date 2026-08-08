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
    # Shock/Discovery
    "This SECRET {platform} Airdrop Is Making People ${amount} Per Day",
    "I Accidentally Found a ${amount} Crypto Airdrop Nobody Knows About",
    "This ${amount} Airdrop Has Been Hidden From You On Purpose",
    "I Can't Believe This ${amount} Airdrop Is Still Available Right Now",
    # Urgency
    "HURRY: Only {days} Days Left To Claim This ${amount} {platform} Airdrop",
    "LAST CHANCE: This ${amount} Airdrop Closes In {days} Days Forever",
    "ACT NOW: Free ${amount} Crypto Airdrop Expires In {days} Days",
    "ALERT: ${amount} Free Crypto Available But Only For {days} More Days",
    "TIME SENSITIVE: Claim Your Free ${amount} Before This Airdrop Ends",
    "CLOSING SOON: ${amount} {platform} Airdrop - Only {days} Days Left",
    # Results/Proof
    "I Made ${amount} From Crypto Airdrops This Week - Here Is Exactly How",
    "Real Proof: I Withdrew ${amount} From This {platform} Airdrop Yesterday",
    "I Claimed {num} Airdrops In One Day And Made ${amount} - Full Breakdown",
    "My Honest Results After Doing Crypto Airdrops For 30 Days - ${amount}",
    "I Documented Every Airdrop I Did This Month - Made ${amount} Total",
    "Zero To ${amount}: My Complete Crypto Airdrop Journey This Month",
    "Watch Me Turn $0 Into ${amount} Using Only Free Crypto Airdrops",
    # Strategy
    "The ${amount} Airdrop Strategy Rich People Use But Never Talk About",
    "How Smart People Are Making ${amount} Monthly With {platform} Airdrops",
    "The Exact Strategy I Used To Make ${amount} From Crypto Airdrops",
    "Copy This Exact Airdrop Method That Made Me ${amount} This Month",
    "The {platform} Airdrop Blueprint That Generated ${amount} For Me",
    "How I Built A ${amount} Per Month Income Stream Using Only Free Airdrops",
    # Speed/Easy
    "Claim ${amount} In Free Crypto In Just {minutes} Minutes - Here How",
    "The Easiest ${amount} You Will Ever Make - {minutes} Minute Airdrop",
    "I Made ${amount} In {minutes} Minutes With This Simple Crypto Airdrop",
    "This {minutes} Minute Trick Gets You ${amount} In Free Crypto Daily",
    "Fastest ${amount} I Ever Made - This Airdrop Takes {minutes} Minutes",
    "Lazy Person Guide To Making ${amount} With {minutes} Minute Airdrops",
    # Beginner
    "I Started With $0 And Made ${amount} With Crypto Airdrops - Here How",
    "Complete Beginner Makes ${amount} With Crypto Airdrops - My Story",
    "No Experience Needed: How I Made ${amount} With My First Crypto Airdrop",
    "My First Crypto Airdrop Paid Me ${amount} - Step By Step Tutorial",
    "If I Started Over Today I Would Do This ${amount} Airdrop First",
    "Anyone Can Do This: ${amount} Crypto Airdrop For Complete Beginners",
    # Comparison
    "I Compared {num} Crypto Airdrops - This One Paid ${amount} The Most",
    "Ranked: The Top {num} Airdrops That Actually Paid Me Real Money",
    "I Did {num} Airdrops This Week - Here Are The Results",
    "{num} Airdrops I Check Every Single Day To Earn ${amount} Monthly",
    "I Tested Every Major {platform} Airdrop - Winner Paid ${amount}",
    # Platform specific
    "Nobody Told Me About This {platform} Airdrop - I Made ${amount}",
    "{platform} Just Launched A ${amount} Airdrop And Nobody Is Talking",
    "This New {platform} Airdrop Is Paying ${amount} To Early Claimers",
    "How I Claimed ${amount} From The {platform} Airdrop In {minutes} Minutes",
    "The {platform} Airdrop That Changed My Life - ${amount} In One Day",
    "Breaking: {platform} Airdrop Now Live - ${amount} Available Per User",
    # Question hooks
    "Can You Really Make ${amount} With Free Crypto Airdrops? I Tested It",
    "Is This ${amount} {platform} Airdrop Legit? My Honest Review",
    "Why Are {num} People Claiming This ${amount} Airdrop Every Single Day?",
    "Are Crypto Airdrops Still Worth It? I Made ${amount} Testing Them",
    # Passive income
    "How I Set Up A ${amount} Per Month Passive Income With Crypto Airdrops",
    "Set This Up Once And Earn ${amount} Monthly From Crypto Airdrops",
    "The ${amount} Monthly Side Hustle Nobody Is Talking About - Airdrops",
    "I Built A ${amount} Per Day Income Stream Using Only Free Crypto Airdrops",
    # Exclusive/Insider
    "Insiders Are Quietly Making ${amount} With This {platform} Airdrop",
    "The ${amount} Airdrop Only {num} People Know About Right Now",
    "The Underground ${amount} Airdrop Strategy The Pros Use Daily",
    "Exclusive: The ${amount} Airdrop That Top Crypto Traders Are Claiming",
    # Story format
    "How I Made ${amount} My First Week Doing Crypto Airdrops",
    "I Quit My Job After Making ${amount} With Crypto Airdrops - Here Is How",
    "My {num} Month Update: I Made ${amount} Total From Crypto Airdrops",
    # Warning format
    "Do NOT Miss This ${amount} {platform} Airdrop - It Closes Soon",
    "Stop Wasting Time - This ${amount} Airdrop Is The Only One That Matters",
    "Everyone Is Doing Airdrops Wrong - Here Is How I Made ${amount}",
    "The Biggest Mistake People Make With Crypto Airdrops Costs Them ${amount}",
    # Trending/News
    "Breaking: New ${amount} Crypto Airdrop Just Launched - Claim Now",
    "Just Announced: {platform} Is Giving Away ${amount} In Free Airdrops",
    "Hot Right Now: The ${amount} {platform} Airdrop Everyone Is Claiming",
    # Achievement
    "From $0 To ${amount} In {days} Days Using Only Free Crypto Airdrops",
    "Challenge: Can You Make ${amount} With Free Airdrops In {days} Days?",
    "I Challenged Myself To Make ${amount} With Airdrops In {days} Days",
    "Goal Achieved: ${amount} From Crypto Airdrops In Just {days} Days",
    # Emotional
    "This ${amount} Crypto Airdrop Literally Changed My Financial Life",
    "I Was Broke Until I Found This ${amount} Crypto Airdrop Strategy",
    "The ${amount} Airdrop That Helped Me Pay My Bills This Month",
    "How I Made ${amount} From Airdrops While Unemployed - True Story",
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
    "How to Spot Fake Crypto Airdrops Before Losing Money",
    "The Best Crypto Wallets for Claiming Airdrops in 2025",
    "How to Automate Your Crypto Airdrop Strategy",
    "Top 10 Highest Paying Crypto Airdrops of All Time",
    "How to Claim Airdrops on Mobile Phone Full Tutorial",
    "Solana vs Ethereum Airdrops Which Pays More",
    "How to Stay Safe While Claiming Crypto Airdrops",
    "How to Build a 500 Dollar Monthly Income with Airdrops",
    "Binance Airdrop Guide Everything You Need to Know",
    "How to Track Upcoming Crypto Airdrops Before Launch",
    "The Best Airdrop Farming Strategy for Beginners",
    "How to Use Multiple Wallets to Multiply Airdrop Earnings",
    "Crypto Airdrop Calendar Best Drops This Month",
    "How to Qualify for Tier 1 Crypto Airdrops",
    "The Difference Between Retroactive and New Airdrops",
    "How to Claim Airdrops Without Gas Fees",
    "Top DeFi Protocols Likely to Airdrop Tokens Soon",
    "How to Use Galxe for Maximum Airdrop Earnings",
    "Layer Zero Airdrop Strategy How I Made 300 Dollars",
    "How to Farm Airdrops on Multiple Chains Simultaneously",
    "The Best Free Tools for Finding Crypto Airdrops",
    "How to Never Miss a Crypto Airdrop Again",
    "Airdrop vs Staking Which Makes More Money",
    "The Psychology Behind Successful Airdrop Farming",
    "How to Use Twitter for Finding Early Crypto Airdrops",
    "Crypto Airdrop Whitelist Guide How to Get Early Access",
    "How to Evaluate if a Crypto Airdrop is Worth Your Time",
    "The Best Discord Servers for Crypto Airdrop Alerts",
    "How to Turn Airdrop Tokens into Real Cash Instantly",
    "Arbitrum Airdrop Lessons What I Learned Making 400 Dollars",
    "How to Participate in GameFi Airdrops for Free",
    "The Complete NFT Airdrop Guide for Crypto Beginners",
    "How to Use Zealy for Earning Crypto Airdrops",
    "Top Testnet Opportunities That Could Become Airdrops",
    "How to Build Airdrop Eligibility on New Blockchains",
    "How to Manage 10 Wallets for Maximum Airdrop Income",
    "How to Get Whitelisted for Exclusive Crypto Airdrops",
    "How to Claim Airdrops Using Only Your Phone",
    "ZkSync Airdrop Strategy That Paid Me 500 Dollars",
    "How to Stay Organized When Farming Multiple Airdrops",
    "The Future of Crypto Airdrops What is Coming in 2025",
    "How to Compound Airdrop Earnings for Maximum Returns",
    "Top Crypto Projects Most Likely to Airdrop This Year",
    "How to Farm Airdrops With Zero Starting Capital",
    "Polygon Airdrop Guide How to Earn Free MATIC",
    "The Complete Guide to Retroactive Crypto Airdrops",
    "How to Earn from Crypto Airdrops While Working Full Time",
    "Top Crypto Communities That Share Airdrop Alpha",
    "How to Scale Your Airdrop Income to 1000 Dollars Per Month",
    "Cosmos Ecosystem Airdrops Complete Farming Guide",
    "How to Get Free Crypto Through Referral Airdrops",
    "The Most Underrated Crypto Airdrop Strategies of 2025",
    "How to Get Free NFTs Through Crypto Airdrops",
    "How to Earn Crypto Airdrops Through Gaming",
    "Best Practices for Long Term Airdrop Farming Success",
    "How to Join a DAO and Earn Free Crypto Airdrops",
    "The Biggest Crypto Airdrops Coming in the Next 6 Months",
    "How to Use DeBank to Track All Your Airdrop Earnings",
    "Best Crypto Airdrop Strategies That Actually Work in 2025",
    "How to Make 100 Dollars Per Day With Crypto Airdrops",
    "The Complete Beginner Guide to Web3 Airdrop Farming",
    "How to Find Hidden Gem Airdrops Before They Go Viral",
    "Top Crypto Airdrops for People With No Experience",
    "How to Double Your Airdrop Earnings With This Simple Trick",
    "The Safest Way to Claim Crypto Airdrops Without Getting Scammed",
    "How to Turn Crypto Airdrops Into a Full Time Income",
    "Best Crypto Airdrop Tools Every Farmer Needs in 2025",
    "How to Get Started With Crypto Airdrops With Zero Money",
    "The Ultimate Crypto Airdrop Checklist for Maximum Earnings",
    "How to Withdraw Airdrop Profits to Your Bank Account Fast",
    "Top Crypto Airdrops That Paid the Most Money This Year",
    "How to Avoid the Most Common Crypto Airdrop Mistakes",
    "The Best Strategy for Claiming Multiple Airdrops Daily",
    "How to Verify if a Crypto Airdrop is Legitimate",
    "Top Crypto Airdrops With Instant Withdrawal Options",
    "How to Earn Free Crypto Every Day With Airdrops",
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


def generate_viral_title(topic: str = None):
    """Generate a 100% unique AI-powered viral title using Groq LLaMA."""
    import json, os, requests

    # Load recent titles to avoid repeats
    recent_titles = []
    try:
        brain_file = os.path.expanduser("~/youtube_bot_data/brain_data.json")
        if os.path.exists(brain_file):
            with open(brain_file) as f:
                data = json.load(f)
            recent_titles = [v.get("title", "") for v in data.get("uploaded_videos", [])[-20:]]
    except Exception:
        pass

    recent_str = "\n".join(f"- {t}" for t in recent_titles[-10:]) if recent_titles else "None"
    topic_hint = topic or random.choice(TRENDING_TOPICS)
    platform = random.choice(PLATFORMS)
    amount = random.choice(AMOUNTS)

    prompt = f"""You are a viral YouTube title expert for a crypto airdrop channel.

Generate 1 unique, click-worthy YouTube video title about: "{topic_hint}"

Rules:
- Must be completely different from these recent titles:
{recent_str}
- Include a specific dollar amount like ${amount}
- Must create curiosity, urgency, or shock
- Max 80 characters
- No hashtags, no quotes in title
- Use power words: EXPOSED, HIDDEN, SECRET, WARNING, URGENT, SHOCKING, REVEALED, etc.
- Mention {platform} if relevant
- Make it feel personal and authentic

Reply with ONLY the title, nothing else."""

    try:
        from config import GROQ_API_KEY, GROQ_MODEL
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": GROQ_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 100,
            "temperature": 0.9
        }
        resp = requests.post("https://api.groq.com/openai/v1/chat/completions",
                           headers=headers, json=payload, timeout=15)
        if resp.status_code == 200:
            title = resp.json()["choices"][0]["message"]["content"].strip()
            title = title.strip('"').strip("'").strip()
            if title and len(title) > 10 and title not in recent_titles:
                print(f"✅ AI Title: {title}")
                return title
    except Exception as e:
        print(f"⚠️ AI title failed, using template: {e}")

    # Fallback to template
    for _ in range(15):
        template = random.choice(VIRAL_HOOKS)
        title = template.format(
            amount=amount,
            days=random.choice(DAYS),
            num=random.choice(NUMS),
            minutes=random.choice(MINUTES),
            platform=platform,
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
