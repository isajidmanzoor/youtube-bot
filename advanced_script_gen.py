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
from brain.uniqueness import seen, uniqueness_report, FORMATS, format_details

try:
    from config import GROQ_API_KEY, GROQ_MODEL
except ImportError:
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
    GROQ_MODEL = "openai/gpt-oss-120b"


DISCLOSURE = "(Affiliate link - I may earn a commission at no extra cost to you.)"
MAX_ATTEMPTS = 3


def generate_advanced_script(topic: str = None, intelligence: dict | None = None, video_format: dict | None = None):
    """Generate a complete 5+ minute curiosity-driven script that repeats nothing from past videos."""
    video_format = video_format or format_details(random.choice(FORMATS))
    # Title is generated for the chosen topic, so title and script always match
    e = get_random_elements(topic, video_format)

    intelligence_prompt = _format_intelligence_for_prompt(intelligence) if intelligence else ""

    # Add latest crypto news for current, relevant content
    news_prompt = ""
    try:
        from news_fetcher import get_latest_crypto_news
        news = get_latest_crypto_news(limit=3)
        if news:
            news_list = "\n".join(f"- {n}" for n in news)
            news_prompt = f"\n\nIMPORTANT: Reference at least one of these real recent crypto news events naturally in your script (as context that the space is active right now):\n{news_list}\n"
    except Exception:
        pass

    feedback = ""
    best = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        prompt = _build_prompt(e, video_format, intelligence_prompt, news_prompt, feedback)
        data = _call_model(prompt, temperature=min(1.1, 0.92 + 0.08 * (attempt - 1)))
        if not data:
            break
        data = _finalize(data, e, video_format, intelligence)
        report = data["uniqueness"]
        if report["unique"]:
            return data
        print(f"⚠️ Draft {attempt} repeats past content: {'; '.join(report['problems'])}")
        if best is None or report["script_overlap"] < best["uniqueness"]["script_overlap"]:
            best = data
        feedback = ("\n\nYOUR PREVIOUS DRAFT WAS REJECTED because it repeated past videos: "
                    + "; ".join(report["problems"])
                    + ". Write a completely different opening line, curiosity question, thumbnail text, on-screen text and wording.")

    # Caller blocks the upload if even the best draft still repeats past content
    if best:
        return best
    return _finalize(_fallback(e, video_format, intelligence), e, video_format, intelligence)


def _build_prompt(e, video_format, intelligence_prompt, news_prompt, feedback):
    past_openings = "\n".join(f"- {o}" for o in seen("opening")[-15:]) or "- none yet"
    past_questions = "\n".join(f"- {q}" for q in seen("curiosity_question")[-15:]) or "- none yet"
    past_thumbs = ", ".join(seen("thumbnail_text")[-20:]) or "none yet"
    sections = "\n".join(f"{i}. {s}" for i, s in enumerate(video_format["sections"], 1))

    return f"""You are an elite YouTube scriptwriter for an honest crypto education channel.
Create a DETAILED 5-minute video script (750-850 words) about: "{e['topic']}"

Use this EXACT title: "{e['title']}"

VIDEO FORMAT: {video_format['name']}
{video_format['structure']}
Sections, in order:
{sections}
Where it fits, use {e['platform']} and {e['wallet']} as the concrete example.

CURIOSITY ENGINE (this is what keeps people watching):
- Sentence 1 IS the hook: a precise, surprising question or contrast about the topic. No greeting, no "welcome back", no channel intro.
- Within the first 15 seconds, promise what the viewer will know by the end (the open loop).
- Every 45-60 seconds, close one small loop and open the next one ("but that is not the part that catches most people...").
- Tease the strongest point early and reveal it late, right before the call to action.
- Every question you open MUST be answered inside this video. Never tease something the video does not deliver.
- Use concrete details, not vague hype. Short sentences. Talk to "you".
- Section hook you may adapt: "{e['section_hook']}"
- Intro style reference (do NOT copy it): "{e['intro']}"
- Outro style reference (do NOT copy it): "{e['outro']}"
- The final lines must say the link in the description is an affiliate link and that you may earn a commission, then invite a comment.

NEVER REPEAT THE CHANNEL'S PAST VIDEOS:
Opening lines already used (do not reuse their wording or structure):
{past_openings}
Curiosity questions already used:
{past_questions}
Thumbnail texts already used: {past_thumbs}

HONESTY RULES (YouTube removes or buries channels that break these):
- The narrator is a guide, not a success story. NEVER claim personal earnings, withdrawals, screenshots, receipts, or "I made $X".
- Never promise profits, "free money", "no investment needed", or guaranteed results. Mention gas fees and time cost.
- Do not invent specific project names, dates, or reward amounts that are not in the news context.
- Warn viewers to verify official links, never share seed phrases, and avoid airdrops that ask for upfront payments.
{intelligence_prompt}{news_prompt}{feedback}

Return ONLY this exact JSON format:
{{
  "title": "{e['title']}",
  "curiosity_question": "the one question the hook opens and the ending answers",
  "payoff": "one sentence: the answer revealed at the end",
  "thumbnail_text": "2-4 punchy words, different from the title, no dollar amounts",
  "script": "FULL SCRIPT HERE - 750-850 words",
  "scenes": [
    {{"time": "0:00", "scene": "section name", "says": "the first 6-10 words of the script where this scene starts, copied exactly", "visual": "2-4 word stock footage search that SHOWS what is said in this scene", "text_overlay": "max 6 words, written for THIS video"}}
  ],
  "description_intro": "2 sentences; the first one contains the main phrase people search for this topic (it is shown in search results), both honest and specific to this video",
  "tags": ["12 tags: the exact search phrases a viewer would type for this video, from specific (project, wallet, task) to broad (crypto airdrop)"],
  "search_query": "2-4 word stock footage search for the main visual",
  "comment_question": "one specific question to ask viewers in the comments"
}}
Give 8-10 scenes: one or two per section, in order, with times spread across 0:00-5:00.
SCENES MUST MATCH THE VOICE: each "says" is copied word for word from the script, in script order,
and each "visual" is a concrete thing a camera can film at that moment (e.g. "hardware wallet closeup",
"person reading phone warning", "calendar marking date"), never an abstract idea, and never the same visual twice."""


def _call_model(prompt: str, temperature: float = 0.92):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": GROQ_MODEL, "reasoning_effort": "low",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 4000,
        "temperature": temperature,
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
        if not data.get("script"):
            raise ValueError("empty script")
        return data
    except Exception as ex:
        print(f"❌ Script error: {ex}")
        return None


def _finalize(data, e, video_format, intelligence):
    """Fill metadata (link + disclosure always present) and run the uniqueness check."""
    data["title"] = e["title"]
    data["topic"] = e["topic"]
    data["format"] = video_format
    data["elements"] = e
    if intelligence:
        data["intelligence"] = _compact_intelligence(intelligence)

    script = data.get("script", "").strip()
    if "affiliate" not in script[-600:].lower():
        script += (" The link in the description is an affiliate link, so I may earn a commission"
                   " at no extra cost to you. Tell me in the comments what you want explained next.")
    data["script"] = script

    scenes = [s for s in data.get("scenes", []) if isinstance(s, dict)]
    for s in scenes:
        s["text_overlay"] = str(s.get("text_overlay", "")).strip().upper()[:42]
    data["scenes"] = scenes

    timestamps = "\n".join(f"{s.get('time', '')} - {s.get('scene', '')}" for s in scenes if s.get("time"))
    intro = data.get("description_intro") or f"{e['title']} - explained step by step, with the risks."
    data["description"] = (
        f"{intro}\n\nEducational only, not financial advice; results are not guaranteed.\n\n"
        + (f"⏱️ TIMESTAMPS\n{timestamps}\n\n" if timestamps else "")
        + f"🔗 PLATFORM I MENTION:\n👉 {AFFILIATE_LINK}\n{DISCLOSURE}\n\n"
        "🛡️ SAFETY\n• Verify official links first\n• Never share your seed phrase\n• Never pay to receive an airdrop\n\n"
        "🔔 Subscribe for practical crypto guides!\n\n"
        f"#CryptoAirdrop #CryptoEducation #CryptoSafety #{e['platform']} #{e['wallet'].replace(' ', '')} #Web3"
    )

    question = data.get("comment_question") or f"What part of {e['topic'].lower()} should I cover next?"
    data["comment"] = (f"{question} 👇\n\n🔗 Platform from the video (affiliate): {AFFILIATE_LINK}\n"
                       "🛡️ Verify official links, never share your seed phrase, never pay upfront.")

    tags = [str(t) for t in data.get("tags", []) if t]
    for t in ["crypto airdrop", "crypto for beginners", "crypto safety", e["topic"].lower()[:30], f"{e['platform'].lower()} airdrop"]:
        if t not in tags:
            tags.append(t)
    data["tags"] = tags[:15]
    data["search_query"] = data.get("search_query") or f"{e['platform'].lower()} crypto blockchain"

    data["uniqueness"] = uniqueness_report(data)
    word_count = len(script.split())
    print(f"✅ Script: {data['title']} | {video_format['name']}")
    print(f"   Words: {word_count} (~{word_count // 150} min read) | overlap with past: {data['uniqueness']['script_overlap']:.0%}")
    return data


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


def _fallback(e, video_format: dict | None = None, intelligence: dict | None = None):
    question = f"What actually decides whether {e['topic'].lower()} works out for you, or costs you money?"
    script = f"""{question} Stay with me, because the answer is not the one most people expect, and I will give it to you before the end.

{e['intro']}

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

So, back to the question from the start. What decides the outcome is not luck or speed. It is whether you verify every link, keep a separate wallet, and treat your time and gas fees as a real cost.

{e['outro']}"""

    # "says" anchors each scene to the narration, so its footage appears when it is spoken
    base_scenes = [
        {"time": "0:00", "scene": "Hook", "says": question, "visual": "person thinking at laptop", "text_overlay": "VERIFY FIRST"},
        {"time": "0:30", "scene": "WhyNow", "says": "Today we are diving deep into", "visual": "person reading phone", "text_overlay": "CHECK LINKS"},
        {"time": "1:00", "scene": "Education", "says": "First let me explain what crypto airdrops actually are", "visual": "crypto coins closeup", "text_overlay": "HOW IT WORKS"},
        {"time": "1:45", "scene": "Tutorial", "says": "Now let me show you how to approach airdrops", "visual": "smartphone wallet app", "text_overlay": "STEP 1"},
        {"time": "2:30", "scene": "Tutorial2", "says": "Step two is to connect your", "visual": "hands typing laptop", "text_overlay": "STEP 2"},
        {"time": "3:00", "scene": "ProTips", "says": "The pro tip that most people miss", "visual": "calendar planning notes", "text_overlay": "PRO TIP"},
        {"time": "3:45", "scene": "Mistakes", "says": "Now let me talk about avoiding scams", "visual": "warning sign screen", "text_overlay": "AVOID SCAMS"},
        {"time": "4:15", "scene": "RealityCheck", "says": "Here is the reality check", "visual": "person counting receipts", "text_overlay": "REALITY CHECK"},
        {"time": "4:45", "scene": "CTA", "says": "So, back to the question from the start", "visual": "person nodding at camera", "text_overlay": "LINK IN DESCRIPTION"},
    ]
    # Format sections replace the generic hook/why-now/basics/tips/reality labels,
    # keeping 9 scenes (the quality gate counts scenes)
    sections = (video_format or {}).get("sections") or []
    scenes = [dict(s) for s in base_scenes]
    for slot, section in zip([0, 1, 2, 5, 7], sections):
        scenes[slot].update({"scene": section, "text_overlay": section.upper()[:42]})

    return {
        "title": e["title"],
        "curiosity_question": question,
        "thumbnail_text": f"{(video_format or {}).get('name', 'The real answer').split(' (')[0]}",
        "script": script,
        "scenes": scenes,
        "description": f"Learn {e['topic']} safely. Educational only, not financial advice; results are not guaranteed.\n\n🔗 Platform I mention:\nhttps://i.mec.me/?c=pt6wsw2v\n(Affiliate link - I may earn a commission at no extra cost to you.)\n\n🛡️ Verify official links, never share your seed phrase, never pay to receive an airdrop.\n\n#CryptoAirdrop #CryptoEducation #CryptoSafety",
        "tags": ["crypto airdrop", "airdrop guide", "crypto for beginners", "crypto safety", e["topic"].lower()[:30]],
        "search_query": f"{e['platform'].lower()} crypto blockchain",
        "comment": f"What should I cover next? 👇\n\n🔗 Platform from the video (affiliate): https://i.mec.me/?c=pt6wsw2v\n🛡️ Verify official links and never share your seed phrase.",
        "topic": e["topic"],
        "elements": e,
        "intelligence": _compact_intelligence(intelligence) if intelligence else None,
    }
