# ============================================================
#   ADVANCED_SCRIPT_GEN.PY — AI Scene Director
#   Generates 700-900 word scripts with scene breakdown
# ============================================================

from __future__ import annotations

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


def generate_advanced_script(topic: str = None, intelligence: dict | None = None):
    """Generate a complete 5+ minute video script with scenes."""
    e = get_random_elements()
    if topic:
        e["topic"] = topic

    intelligence_prompt = _format_intelligence_for_prompt(intelligence) if intelligence else ""

    # Add latest crypto news for current, relevant content
    news_prompt = ""
    try:
        from news_fetcher import get_latest_crypto_news
        news = get_latest_crypto_news(limit=3)
        if news:
            news_list = "\n".join(f"- {n}" for n in news)
            news_prompt = f"\n\nLATEST CRYPTO NEWS (reference naturally if relevant, do not just read the headlines):\n{news_list}\n"
    except Exception:
        pass

    # Add latest crypto news for current, relevant content
    news_prompt = ""
    try:
        from news_fetcher import get_latest_crypto_news
        news = get_latest_crypto_news(limit=3)
        if news:
            news_list = "\n".join(f"- {n}" for n in news)
            news_prompt = f"\n\nLATEST CRYPTO NEWS (reference naturally if relevant, do not just read the headlines):\n{news_list}\n"
    except Exception:
        pass

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
5. PRO TIPS (3:00-3:45) - Advanced strategies to improve eligibility without guaranteeing results
6. MISTAKES TO AVOID (3:45-4:15) - Common pitfalls
7. PROOF & RISK CHECK (4:15-4:45) - Explain how to verify real results and avoid fake claims
8. CALL TO ACTION (4:45-5:00) - Push them to description link

Voice style: Energetic, conversational, like a friend sharing a secret. Use "you" frequently.
NO robotic language. Sound like a real person.
Use safe educational framing. Do not promise guaranteed profits. Warn viewers to verify official links, never share seed phrases, and avoid airdrops that ask for upfront payments.
{intelligence_prompt}{news_prompt}

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
  "description": "🔥 Learn how crypto airdrops work on {e['platform']} using {e['wallet']}. This is an educational walkthrough, not financial advice and not a guaranteed earning claim. Always verify official links, never share your seed phrase, and avoid any airdrop asking for upfront payment.\\n\\n⏱️ TIMESTAMPS\\n0:00 - What Makes This Opportunity Interesting\\n0:30 - Verification Checklist\\n1:00 - What Are Crypto Airdrops\\n1:45 - Step by Step Tutorial\\n3:00 - Pro Tips to Improve Eligibility\\n3:45 - Mistakes to Avoid\\n4:15 - Proof and Risk Check\\n4:45 - Get Started Safely\\n\\n💰 START SAFELY:\\n👉 https://i.mec.me/?c=pt6wsw2v\\n\\n✅ Free to learn\\n✅ Verify official links first\\n✅ Never share seed phrases\\n✅ Results are not guaranteed\\n\\n🔔 Subscribe for daily crypto education!\\n\\n#CryptoAirdrop #FreeCrypto #Airdrop2025 #CryptoEducation #CryptoSafety #{e['platform']}Airdrop #{e['wallet'].replace(' ','')} #CryptoTips #Web3",
  "tags": ["crypto airdrop 2025", "free crypto", "{e['topic'].lower()[:20]}", "{e['wallet'].lower()}", "airdrop 2025", "earn crypto free", "passive income crypto", "{e['platform'].lower()} airdrop", "make money crypto", "free tokens", "crypto tips 2025", "crypto tutorial"],
  "search_query": "{e['platform'].lower()} crypto blockchain technology",
  "comment": "🔥 Airdrop safety checklist: verify official links, never share your seed phrase, and avoid upfront payment requests.\\n👉 https://i.mec.me/?c=pt6wsw2v"
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
        if intelligence:
            data["intelligence"] = _compact_intelligence(intelligence)

        word_count = len(data.get("script", "").split())
        print(f"✅ Script: {data['title']}")
        print(f"   Words: {word_count} (~{word_count // 150} min read)")
        return data

    except Exception as ex:
        print(f"❌ Script error: {ex}")
        return _fallback(e, intelligence)


def _format_intelligence_for_prompt(intelligence: dict) -> str:
    """Summarize the studio brief for the model without bloating the prompt."""
    viral = intelligence.get("viral_probability_ai", {})
    opportunity = intelligence.get("opportunity_scanner", {})
    truth = intelligence.get("truth_verification_engine", {})
    story = intelligence.get("story_architect", {}).get("beats", [])
    psychology = intelligence.get("psychology_engine", [])
    thumbnail = intelligence.get("thumbnail_laboratory", {}).get("best_thumbnail", {})
    seo = intelligence.get("seo_laboratory", {})

    beats = "; ".join(f"{b.get('beat')}: {b.get('line')}" for b in story[:6])
    emotions = "; ".join(
        f"{p.get('second')}s={p.get('viewer_state')} -> {p.get('rewrite_instruction')}"
        for p in psychology[:7]
    )

    return f"""

AI STUDIO INTELLIGENCE:
- Opportunity: {opportunity.get('best_angle', '')}
- Content gap: {opportunity.get('content_gap', '')}
- Viral probability: {viral.get('viral_probability', 'n/a')}%, expected CTR {viral.get('ctr', 'n/a')}%, retention {viral.get('retention', 'n/a')}%
- Story beats: {beats}
- Psychology timeline: {emotions}
- SEO primary keyword: {seo.get('primary_keyword', '')}
- Thumbnail concept: {thumbnail.get('concept', '')}
- Truth rules: {', '.join(truth.get('required_checks', []))}
"""


def _compact_intelligence(intelligence: dict) -> dict:
    return {
        "run_id": intelligence.get("run_id"),
        "trend_score": intelligence.get("viral_probability_ai", {}).get("trend_score"),
        "viral_probability": intelligence.get("viral_probability_ai", {}).get("viral_probability"),
        "quality_gate": intelligence.get("quality_gate"),
        "best_thumbnail": intelligence.get("thumbnail_laboratory", {}).get("best_thumbnail"),
        "research_consensus": intelligence.get("research_swarm", {}).get("consensus"),
    }


def _fallback(e, intelligence: dict | None = None):
    script = f"""{e['intro']}

Today we are diving deep into {e['topic']}. I have been doing this for months now and I want to share everything I know with you.

First let me explain what crypto airdrops actually are. An airdrop is when a cryptocurrency project gives away free tokens to users. They do this to promote their platform and attract new users. The beautiful thing is you do not need to invest any money. You just complete simple tasks and earn tokens.

{e['section_hook']}

Now let me show you exactly how I use {e['wallet']} to claim airdrops on {e['platform']}. The first thing you need to do is download {e['wallet']} from the official website or app store. It is completely free. Once you have your wallet set up you will get a wallet address. This is like your bank account number for crypto.

Step one is to find legitimate airdrops. I use dedicated airdrop tracking websites to find new projects. Always look for projects with real websites, active social media, and clear whitepapers. Never trust airdrops that ask you to send crypto first.

Step two is to connect your {e['wallet']} wallet to the airdrop platform. This is safe as long as you are on the official website. You just click connect wallet and approve the connection.

Step three is to complete the required tasks. These usually include following on Twitter, joining Telegram, and sometimes testing the platform. Each completed task earns you points or tokens.

The pro tip that most people miss is to join airdrops as early as possible. Early participants usually get more tokens because the supply is larger before other users join. I set alerts for new project launches so I can join within the first few hours.

Another strategy some people discuss is using multiple wallets, but you need to be careful. Some projects ban duplicate accounts, so always read the official rules first. The smarter approach is to track many legitimate projects, stay early, and keep your wallet security clean.

Now let me talk about avoiding scams. If an airdrop asks you to send crypto to receive crypto, treat it as a scam. Legitimate airdrops should not ask for your seed phrase, private key, or upfront payment. Also be careful of fake websites that look like real projects. Always double check the URL before connecting your wallet.

Let me share the kind of result people look for. Using these strategies on {e['platform']}, some users report rewards around ${e['amount']} during active campaigns, but results are never guaranteed. Token values move, eligibility rules change, and you should verify everything before spending time on a project.

The key is consistency. I spend about fifteen to twenty minutes per day checking new airdrops and completing tasks. That is it. The rest happens automatically as the tokens accumulate in my wallet.

{e['outro']}"""

    return {
        "title": e["title"],
        "script": script,
        "scenes": [
            {"time": "0:00", "scene": "Hook", "visual": "crypto safety opener", "text_overlay": "VERIFY FIRST"},
            {"time": "0:30", "scene": "Credibility", "visual": "verification checklist", "text_overlay": "CHECK LINKS"},
            {"time": "1:00", "scene": "Education", "visual": "airdrop diagram", "text_overlay": "HOW IT WORKS"},
            {"time": "1:45", "scene": "Tutorial", "visual": "wallet setup", "text_overlay": "STEP 1"},
            {"time": "2:30", "scene": "Tutorial2", "visual": "platform walkthrough", "text_overlay": "STEP 2"},
            {"time": "3:00", "scene": "ProTips", "visual": "eligibility checklist", "text_overlay": "PRO TIP"},
            {"time": "3:45", "scene": "Mistakes", "visual": "warning sign", "text_overlay": "AVOID SCAMS"},
            {"time": "4:15", "scene": "Proof", "visual": "risk check", "text_overlay": "NO GUARANTEE"},
            {"time": "4:45", "scene": "CTA", "visual": "safe next step", "text_overlay": "START SAFELY"},
        ],
        "description": f"Learn {e['topic']} safely. Educational only, not financial advice. Verify official links, never share your seed phrase, and avoid upfront payment requests.\n\nStart safely:\nhttps://i.mec.me/?c=pt6wsw2v\n\n#CryptoAirdrop #FreeCrypto #Airdrop2025 #CryptoSafety",
        "tags": ["crypto airdrop", "free crypto", "airdrop 2025", "earn crypto", "passive income"],
        "search_query": f"{e['platform'].lower()} crypto blockchain",
        "comment": f"🔥 FREE crypto airdrop tutorial! Verify official links and never share your seed phrase.\n👉 https://i.mec.me/?c=pt6wsw2v",
        "topic": e["topic"],
        "elements": e,
        "intelligence": _compact_intelligence(intelligence) if intelligence else None,
    }
