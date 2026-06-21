# ============================================================
#   ADVANCED_SCRIPT_GEN.PY — AI Scene Director
#   Generates 700-900 word scripts with scene breakdown
# ============================================================

import requests
import json
import random
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from brain.trend_engine import get_random_elements, AFFILIATE_LINK

try:
    from config import GROQ_API_KEY, GROQ_MODEL
except ImportError:
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
    GROQ_MODEL = "llama-3.3-70b-versatile"


def generate_advanced_script():
    """Generate a complete 5+ minute video script with scenes."""
    e = get_random_elements()

    prompt = f"""You are an elite YouTube scriptwriter for a crypto education channel.
Create a DETAILED 5-minute video script (750-850 words) about: "{e['topic']}"

Use this EXACT title: "{e['title']}"
Start with this EXACT intro: "{e['intro']}"
End with this EXACT outro: "{e['outro']}"
Include this section hook naturally: "{e['section_hook']}"

The script should cover:
1. HOOK (0:00-0:30) - Grab attention immediately
2. CREDIBILITY (0:30-1:00) - Why should they trust you, show proof
3. WHAT ARE AIRDROPS (1:00-1:45) - Explain simply for beginners  
4. STEP BY STEP GUIDE (1:45-3:00) - How to join {e['platform']} airdrops using {e['wallet']}
5. PRO TIPS (3:00-3:45) - Advanced strategies to earn more like ${e['amount']}
6. MISTAKES TO AVOID (3:45-4:15) - Common pitfalls
7. EARNINGS PROOF (4:15-4:45) - Talk about real withdrawals of ${e['amount2']}
8. CALL TO ACTION (4:45-5:00) - Push them to description link

Voice style: Energetic, conversational, like a friend sharing a secret. Use "you" frequently.
NO robotic language. Sound like a real person.

Return ONLY this exact JSON format:
{{
  "title": "{e['title']}",
  "script": "FULL SCRIPT HERE - 750-850 words",
  "scenes": [
    {{"time": "0:00", "scene": "Hook", "visual": "crypto wallet with money", "text_overlay": "FREE CRYPTO"}},
    {{"time": "0:30", "scene": "Credibility", "visual": "withdrawal screenshot", "text_overlay": "${e['amount']} EARNED"}},
    {{"time": "1:00", "scene": "Education", "visual": "airdrop platform", "text_overlay": "WHAT ARE AIRDROPS"}},
    {{"time": "1:45", "scene": "Tutorial", "visual": "{e['wallet']} wallet", "text_overlay": "STEP 1"}},
    {{"time": "2:30", "scene": "Tutorial2", "visual": "{e['platform']} network", "text_overlay": "STEP 2"}},
    {{"time": "3:00", "scene": "ProTips", "visual": "multiple wallets", "text_overlay": "PRO TIP"}},
    {{"time": "3:45", "scene": "Mistakes", "visual": "warning sign", "text_overlay": "AVOID THIS"}},
    {{"time": "4:15", "scene": "Proof", "visual": "bank transfer", "text_overlay": "${e['amount2']} WITHDRAWN"}},
    {{"time": "4:45", "scene": "CTA", "visual": "link in description", "text_overlay": "JOIN FREE"}}
  ],
  "description": "🔥 I earned ${e['amount']} with FREE crypto airdrops on {e['platform']} using {e['wallet']}! Watch this full tutorial to learn my exact strategy.\\n\\n⏱️ TIMESTAMPS\\n0:00 - How I Made ${e['amount']} with Airdrops\\n0:30 - Proof of Withdrawal\\n1:00 - What Are Crypto Airdrops\\n1:45 - Step by Step Tutorial\\n3:00 - Pro Tips to Maximize Earnings\\n3:45 - Mistakes to Avoid\\n4:15 - Live Earnings Proof\\n4:45 - Get Started Free\\n\\n💰 JOIN FREE - Start Earning Today:\\n👉 {AFFILIATE_LINK}\\n\\n✅ 100% FREE - No investment needed\\n✅ Works worldwide\\n✅ Withdraw anytime to {e['wallet']}\\n✅ Earning in minutes\\n\\n🔔 Subscribe for daily crypto tips!\\n\\n#CryptoAirdrop #FreeCrypto #Airdrop2025 #EarnCrypto #PassiveIncome #{e['platform']}Airdrop #{e['wallet'].replace(' ','')} #CryptoTips #MakeMoneyCrypto #FreeTokens",
  "tags": ["crypto airdrop 2025", "free crypto", "{e['topic'].lower()[:20]}", "{e['wallet'].lower()}", "airdrop 2025", "earn crypto free", "passive income crypto", "{e['platform'].lower()} airdrop", "make money crypto", "free tokens", "crypto tips 2025", "crypto tutorial"],
  "search_query": "{e['platform'].lower()} crypto blockchain technology",
  "comment": "🔥 Just withdrew ${e['amount']} using this FREE airdrop! No investment needed 🚀\\n👉 {AFFILIATE_LINK}\\n✅ Takes 2 minutes to set up - Join before it fills up!"
}}"""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 4000,
        "temperature": 0.92,
    }

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=60,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"].strip()

        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        data = json.loads(content)
        data["topic"] = e["topic"]
        data["elements"] = e

        word_count = len(data.get("script", "").split())
        print(f"✅ Script: {data['title']}")
        print(f"   Words: {word_count} (~{word_count // 150} min read)")
        return data

    except Exception as ex:
        print(f"❌ Script error: {ex}")
        return _fallback(e)


def _fallback(e):
    script = f"""{e['intro']}

Today we are diving deep into {e['topic']}. I have been doing this for months now and I want to share everything I know with you.

First let me explain what crypto airdrops actually are. An airdrop is when a cryptocurrency project gives away free tokens to users. They do this to promote their platform and attract new users. The beautiful thing is you do not need to invest any money. You just complete simple tasks and earn tokens.

{e['section_hook']}

Now let me show you exactly how I use {e['wallet']} to claim airdrops on {e['platform']}. The first thing you need to do is download {e['wallet']} from the official website or app store. It is completely free. Once you have your wallet set up you will get a wallet address. This is like your bank account number for crypto.

Step one is to find legitimate airdrops. I use dedicated airdrop tracking websites to find new projects. Always look for projects with real websites, active social media, and clear whitepapers. Never trust airdrops that ask you to send crypto first.

Step two is to connect your {e['wallet']} wallet to the airdrop platform. This is safe as long as you are on the official website. You just click connect wallet and approve the connection.

Step three is to complete the required tasks. These usually include following on Twitter, joining Telegram, and sometimes testing the platform. Each completed task earns you points or tokens.

The pro tip that most people miss is to join airdrops as early as possible. Early participants usually get more tokens because the supply is larger before other users join. I set alerts for new project launches so I can join within the first few hours.

Another strategy is to use multiple wallets. You can create several {e['wallet']} wallets and join the same airdrop multiple times. This multiplies your earnings without any extra effort.

Now let me talk about avoiding scams. If an airdrop asks you to send crypto to receive crypto it is one hundred percent a scam. Legitimate airdrops never require payment. Also be careful of fake websites that look like real projects. Always double check the URL before connecting your wallet.

Let me share my real results. Using these strategies on {e['platform']} I have earned over ${e['amount']} in the past {e['days']} days alone. My biggest single withdrawal was ${e['amount2']}. I transfer everything directly to my bank through a crypto exchange.

The key is consistency. I spend about fifteen to twenty minutes per day checking new airdrops and completing tasks. That is it. The rest happens automatically as the tokens accumulate in my wallet.

{e['outro']}"""

    return {
        "title": e["title"],
        "script": script,
        "scenes": [
            {"time": "0:00", "scene": "Hook", "visual": "crypto money", "text_overlay": "FREE CRYPTO"},
            {"time": "1:00", "scene": "Tutorial", "visual": "wallet setup", "text_overlay": "STEP BY STEP"},
            {"time": "3:00", "scene": "ProTips", "visual": "earnings", "text_overlay": "PRO TIPS"},
            {"time": "4:30", "scene": "CTA", "visual": "join now", "text_overlay": "JOIN FREE"},
        ],
        "description": f"Learn {e['topic']}!\n\n💰 Start FREE:\n👉 {AFFILIATE_LINK}\n\n#CryptoAirdrop #FreeCrypto #Airdrop2025",
        "tags": ["crypto airdrop", "free crypto", "airdrop 2025", "earn crypto", "passive income"],
        "search_query": f"{e['platform'].lower()} crypto blockchain",
        "comment": f"🔥 FREE crypto airdrop! No investment needed!\n👉 {AFFILIATE_LINK}",
        "topic": e["topic"],
        "elements": e,
    }
