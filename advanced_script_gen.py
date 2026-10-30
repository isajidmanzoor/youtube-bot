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
    GROQ_MODEL = "openai/gpt-oss-120b"


def generate_advanced_script(topic: str = None, intelligence: dict | None = None):
    """Generate a complete 5+ minute video script with scenes."""
    # Title is generated for the chosen topic, so title and script always match
    e = get_random_elements(topic)

    intelligence_prompt = _format_intelligence_for_prompt(intelligence) if intelligence else ""

    # Add latest crypto news for current, relevant content
    news_prompt = ""
    try:
        from news_fetcher import get_latest_crypto_news
        news = get_latest_crypto_news(limit=3)
        if news:
            news_list = "\n".join(f"- {n}" for n in news)
            news_prompt = f"\n\nIMPORTANT: Reference at least one of these real recent crypto news events naturally in your script (in the hook or 'why now' section, as context that the space is active right now):\n{news_list}\n"
    except Exception:
        pass

    prompt = f"""You are an elite YouTube scriptwriter for an honest crypto education channel.
Create a DETAILED 5-minute video script (750-850 words) about: "{e['topic']}"

Use this EXACT title: "{e['title']}"
Start with this EXACT intro: "{e['intro']}"
End with this EXACT outro: "{e['outro']}"
Include this section hook naturally: "{e['section_hook']}"

The script should cover:
1. HOOK (0:00-0:30) - Open with the most useful or surprising fact about the topic; deliver on the title fast
2. WHY NOW (0:30-1:00) - Why this matters right now (use the news context if given)
3. THE BASICS (1:00-1:45) - Explain the core idea simply for beginners
4. STEP BY STEP GUIDE (1:45-3:00) - Concrete steps for {e['platform']} using {e['wallet']}
5. PRO TIPS (3:00-3:45) - Practical strategies to improve eligibility, without guaranteeing results
6. MISTAKES TO AVOID (3:45-4:15) - Common pitfalls and scams
7. REALITY CHECK (4:15-4:45) - Honest expectations: costs, time, risk, and that many people earn little or nothing
8. CALL TO ACTION (4:45-5:00) - Point to the description link (affiliate) and ask a question for the comments

Voice style: Energetic, conversational, like a knowledgeable friend. Use "you" frequently. Short sentences.
NO robotic language. Every 30 seconds give the viewer a new concrete detail so they keep watching.
HONESTY RULES (YouTube removes or buries channels that break these):
- The narrator is a guide, not a success story. NEVER claim personal earnings, withdrawals, screenshots, receipts, or "I made $X".
- Never promise profits, "free money", "no investment needed", or guaranteed results. Mention gas fees and time cost.
- Do not invent specific project names, dates, or reward amounts that are not in the news context.
- Warn viewers to verify official links, never share seed phrases, and avoid airdrops that ask for upfront payments.
{intelligence_prompt}{news_prompt}

Return ONLY this exact JSON format:
{{
  "title": "{e['title']}",
  "script": "FULL SCRIPT HERE - 750-850 words",
  "scenes": [
    {{"time": "0:00", "scene": "Hook", "visual": "crypto wallet on phone", "text_overlay": "WATCH THIS FIRST"}},
    {{"time": "0:30", "scene": "WhyNow", "visual": "crypto news headlines", "text_overlay": "WHY IT MATTERS NOW"}},
    {{"time": "1:00", "scene": "Education", "visual": "blockchain network", "text_overlay": "THE BASICS"}},
    {{"time": "1:45", "scene": "Tutorial", "visual": "{e['wallet']} wallet", "text_overlay": "STEP 1"}},
    {{"time": "2:30", "scene": "Tutorial2", "visual": "{e['platform']} network", "text_overlay": "STEP 2"}},
    {{"time": "3:00", "scene": "ProTips", "visual": "checklist on laptop", "text_overlay": "PRO TIP"}},
    {{"time": "3:45", "scene": "Mistakes", "visual": "warning sign", "text_overlay": "AVOID THIS"}},
    {{"time": "4:15", "scene": "RealityCheck", "visual": "person thinking at laptop", "text_overlay": "REALITY CHECK"}},
    {{"time": "4:45", "scene": "CTA", "visual": "link in description", "text_overlay": "LINK IN DESCRIPTION"}}
  ],
  "description": "Learn {e['topic'].lower()} on {e['platform']} using {e['wallet']} - step by step, with the risks explained. Educational only, not financial advice; results are not guaranteed.\\n\\n⏱️ TIMESTAMPS\\n0:00 - Intro\\n0:30 - Why It Matters Now\\n1:00 - The Basics\\n1:45 - Step by Step Tutorial\\n3:00 - Pro Tips\\n3:45 - Mistakes to Avoid\\n4:15 - Reality Check\\n4:45 - Next Steps\\n\\n🔗 PLATFORM I MENTION:\\n👉 https://i.mec.me/?c=pt6wsw2v\\n(Affiliate link - I may earn a commission at no extra cost to you.)\\n\\n🛡️ SAFETY\\n• Verify official links first\\n• Never share your seed phrase\\n• Never pay to receive an airdrop\\n\\n🔔 Subscribe for practical crypto guides!\\n\\n#CryptoAirdrop #CryptoEducation #CryptoSafety #{e['platform']} #{e['wallet'].replace(' ','')} #Web3",
  "tags": ["crypto airdrop", "{e['topic'].lower()[:30]}", "{e['wallet'].lower()}", "{e['platform'].lower()} airdrop", "airdrop guide", "crypto for beginners", "crypto safety", "airdrop tutorial", "web3", "crypto tutorial"],
  "search_query": "{e['platform'].lower()} crypto blockchain technology",
  "comment": "What part of {e['topic'].lower()} should I cover next? 👇\\n\\n🔗 Platform from the video (affiliate): https://i.mec.me/?c=pt6wsw2v\\n🛡️ Verify official links, never share your seed phrase, never pay upfront."
}}"""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": GROQ_MODEL, "reasoning_effort": "low",
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

Today we are diving deep into {e['topic']}. I will keep it practical, and I will be honest about the risks too.

First let me explain what crypto airdrops actually are. An airdrop is when a cryptocurrency project distributes tokens to users, usually to reward early activity and grow its community. Some airdrops have been worth a lot, many are worth very little, and some are outright scams. Knowing the difference is the whole game.

{e['section_hook']}

Now let me show you how to approach airdrops on {e['platform']} using {e['wallet']}. The first thing you need to do is download {e['wallet']} from the official website or app store only. Create a separate wallet just for airdrops, so your main savings are never exposed. Write your seed phrase on paper and never type it into any website.

Step one is to find legitimate airdrops. Use well known airdrop tracking websites and the official social accounts of projects. Always look for projects with real websites, active social media, and clear whitepapers. Never trust airdrops that ask you to send crypto first.

Step two is to connect your {e['wallet']} wallet to the airdrop platform. This is safe as long as you are on the official website. You just click connect wallet and approve the connection.

Step three is to actually use the product. Most modern airdrops reward real activity like swapping, bridging, or providing liquidity over time, not just following on social media. Keep in mind that every transaction costs gas fees.

The pro tip that most people miss is consistency over volume. Using a few solid projects regularly over several months usually beats spamming dozens of random ones in one day.

Another strategy some people discuss is using multiple wallets, but you need to be careful. Some projects ban duplicate accounts, so always read the official rules first. The smarter approach is to track many legitimate projects, stay early, and keep your wallet security clean.

Now let me talk about avoiding scams. If an airdrop asks you to send crypto to receive crypto, treat it as a scam. Legitimate airdrops should not ask for your seed phrase, private key, or upfront payment. Also be careful of fake websites that look like real projects. Always double check the URL before connecting your wallet.

Here is the reality check. Airdrops are not guaranteed income. You spend time and gas fees, eligibility rules change, and token prices move. Treat it as learning about crypto, and only spend what you can afford to lose. After claiming, revoke token approvals you no longer need.

{e['outro']}"""

    return {
        "title": e["title"],
        "script": script,
        "scenes": [
            {"time": "0:00", "scene": "Hook", "visual": "crypto safety opener", "text_overlay": "VERIFY FIRST"},
            {"time": "0:30", "scene": "WhyNow", "visual": "verification checklist", "text_overlay": "CHECK LINKS"},
            {"time": "1:00", "scene": "Education", "visual": "airdrop diagram", "text_overlay": "HOW IT WORKS"},
            {"time": "1:45", "scene": "Tutorial", "visual": "wallet setup", "text_overlay": "STEP 1"},
            {"time": "2:30", "scene": "Tutorial2", "visual": "platform walkthrough", "text_overlay": "STEP 2"},
            {"time": "3:00", "scene": "ProTips", "visual": "eligibility checklist", "text_overlay": "PRO TIP"},
            {"time": "3:45", "scene": "Mistakes", "visual": "warning sign", "text_overlay": "AVOID SCAMS"},
            {"time": "4:15", "scene": "RealityCheck", "visual": "risk check", "text_overlay": "REALITY CHECK"},
            {"time": "4:45", "scene": "CTA", "visual": "safe next step", "text_overlay": "LINK IN DESCRIPTION"},
        ],
        "description": f"Learn {e['topic']} safely. Educational only, not financial advice; results are not guaranteed.\n\n🔗 Platform I mention:\nhttps://i.mec.me/?c=pt6wsw2v\n(Affiliate link - I may earn a commission at no extra cost to you.)\n\n🛡️ Verify official links, never share your seed phrase, never pay to receive an airdrop.\n\n#CryptoAirdrop #CryptoEducation #CryptoSafety",
        "tags": ["crypto airdrop", "airdrop guide", "crypto for beginners", "crypto safety", e["topic"].lower()[:30]],
        "search_query": f"{e['platform'].lower()} crypto blockchain",
        "comment": f"What should I cover next? 👇\n\n🔗 Platform from the video (affiliate): https://i.mec.me/?c=pt6wsw2v\n🛡️ Verify official links and never share your seed phrase.",
        "topic": e["topic"],
        "elements": e,
        "intelligence": _compact_intelligence(intelligence) if intelligence else None,
    }
