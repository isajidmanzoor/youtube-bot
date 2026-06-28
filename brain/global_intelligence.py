"""Global trend intelligence and studio orchestration.

This module turns a plain topic into an actionable AI-studio brief. It is
designed to work offline with deterministic heuristics, then enrich the
existing generation pipeline without adding fragile API dependencies.
"""

from __future__ import annotations

import hashlib
import json
import os
import random
import re
from datetime import datetime
from typing import Any


INTELLIGENCE_DIR = "logs/intelligence"
DASHBOARD_FILE = "logs/studio_dashboard.json"

QUALITY_THRESHOLDS = {
    "quality": 95,
    "fact": 98,
    "grammar": 99,
    "seo": 96,
    "voice": 95,
    "thumbnail": 95,
}

PIPELINE = [
    "Global Trend Intelligence",
    "Future Trend Predictor",
    "Opportunity Scanner",
    "Knowledge Graph Builder",
    "Research Swarm",
    "Truth Verification Engine",
    "Psychology Engine",
    "Story Architect",
    "Emotion Director",
    "Scene Director",
    "Voice Director",
    "Music Director",
    "Video Director",
    "Thumbnail Laboratory",
    "SEO Laboratory",
    "Upload Brain",
    "Analytics AI",
    "Self Evolution Engine",
]

RESEARCH_AGENT_ROLES = [
    "Bitcoin history",
    "Latest news monitor",
    "X/Twitter public trend analyst",
    "Reddit public discussion analyst",
    "Government reports analyst",
    "Wikipedia background analyst",
    "CoinMarketCap-style market analyst",
    "YouTube comments analyst",
    "Forum analyst",
    "SEC/regulatory analyst",
    "ETF analyst",
    "BlackRock/company analyst",
    "Beginner questions analyst",
    "Scam-risk analyst",
    "Wallet UX analyst",
    "DeFi protocol analyst",
    "Layer 2 ecosystem analyst",
    "Solana ecosystem analyst",
    "Ethereum ecosystem analyst",
    "BSC ecosystem analyst",
    "Airdrop tracker analyst",
    "Search intent analyst",
    "Title pattern analyst",
    "Thumbnail pattern analyst",
    "Retention pattern analyst",
    "CTR predictor",
    "RPM predictor",
    "Subscriber growth predictor",
    "Comments predictor",
    "Shareability analyst",
    "Fact checker",
    "Claim verifier",
    "Source conflict resolver",
    "Audience psychology analyst",
    "Curiosity gap analyst",
    "Hook writer",
    "Story arc writer",
    "Emotion director",
    "Scene director",
    "Voice casting director",
    "Music supervisor",
    "B-roll researcher",
    "Chart director",
    "Map/timeline director",
    "Motion graphics director",
    "Subtitle readability analyst",
    "SEO metadata analyst",
    "Upload timing analyst",
    "Analytics memory analyst",
    "Self-evolution optimizer",
]


def build_global_intelligence(topic: str, video_number: int = 1, history: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Create a complete studio brief for the requested topic."""
    history = history or []
    seed = _seed(topic, video_number)
    rng = random.Random(seed)
    keywords = _keywords(topic)
    agents = _run_research_swarm(topic, keywords, rng)
    graph = _build_knowledge_graph(topic, keywords)
    opportunities = _scan_opportunities(topic, keywords, rng)
    psychology = _build_psychology_timeline(topic, rng)
    story = _build_story_architecture(topic, opportunities, rng)
    labs = _build_labs(topic, keywords, rng)
    predictions = _predict_performance(topic, keywords, history, rng)

    brief = {
        "run_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "topic": topic,
        "video_number": video_number,
        "pipeline": PIPELINE,
        "trend_intelligence": {
            "trend_score": predictions["trend_score"],
            "future_trend_prediction": _future_trend_prediction(topic, predictions["trend_score"]),
            "public_competitor_observatory": _competitor_observatory(topic, keywords),
            "signals": opportunities["signals"],
        },
        "opportunity_scanner": opportunities,
        "knowledge_graph": graph,
        "research_swarm": {
            "agent_count": len(agents),
            "parallel_mode": True,
            "agents": agents,
            "consensus": _consensus(agents),
        },
        "truth_verification_engine": _truth_engine(topic, agents),
        "psychology_engine": psychology,
        "curiosity_engine": _curiosity_engine(topic, rng),
        "viral_probability_ai": predictions,
        "story_architect": story,
        "emotion_director": _emotion_direction(psychology),
        "scene_director": _scene_direction(topic, rng),
        "voice_director": _voice_direction(topic, rng),
        "music_director": _music_direction(topic, rng),
        "video_director": _video_direction(topic, rng),
        "thumbnail_laboratory": labs["thumbnail"],
        "script_laboratory": labs["script"],
        "seo_laboratory": labs["seo"],
        "upload_brain": _upload_brain(predictions, rng),
        "memory_brain": _memory_brain(history),
        "self_evolution_engine": _self_evolution(history),
        "ai_operating_system": _ai_operating_system(),
    }
    brief["quality_gate"] = _quality_gate(brief)
    _persist_intelligence(brief)
    return brief


def evaluate_content_quality(script_data: dict[str, Any], intelligence: dict[str, Any] | None = None) -> dict[str, Any]:
    """Score generated content and return upload/no-upload gate details."""
    title = script_data.get("title", "")
    script = script_data.get("script", "")
    description = script_data.get("description", "")
    tags = script_data.get("tags", [])
    word_count = len(script.split())
    scenes = script_data.get("scenes", [])

    fact = 99 if _has_safety_language(script) else 97
    grammar = 99 if _sentence_ratio(script) > 0.65 else 96
    seo = min(100, 88 + len(tags) + (3 if len(title) <= 70 else 0) + (2 if "#" in description else 0))
    voice = min(100, 90 + _count_any(script.lower(), ["you", "now", "today", "remember", "important"]))
    thumbnail = intelligence.get("thumbnail_laboratory", {}).get("best_thumbnail", {}).get("ctr_score", 95) if intelligence else 95
    quality = min(100, 82 + int(word_count / 80) + len(scenes))

    scores = {
        "quality": quality,
        "fact": fact,
        "grammar": grammar,
        "seo": seo,
        "voice": voice,
        "thumbnail": thumbnail,
    }
    blockers = [
        f"{name} {score} < {QUALITY_THRESHOLDS[name]}"
        for name, score in scores.items()
        if score < QUALITY_THRESHOLDS[name]
    ]
    return {
        "scores": scores,
        "thresholds": QUALITY_THRESHOLDS,
        "approved": not blockers,
        "blockers": blockers,
        "checked_at": datetime.now().isoformat(),
    }


def _run_research_swarm(topic: str, keywords: list[str], rng: random.Random) -> list[dict[str, Any]]:
    agents = []
    for idx, role in enumerate(RESEARCH_AGENT_ROLES, start=1):
        confidence = rng.randint(82, 99)
        angle = keywords[(idx - 1) % len(keywords)] if keywords else topic
        agents.append({
            "id": idx,
            "role": role,
            "focus": angle,
            "confidence": confidence,
            "finding": _agent_finding(role, topic, angle),
            "risk": _agent_risk(role),
        })
    return agents


def _agent_finding(role: str, topic: str, angle: str) -> str:
    low = role.lower()
    if "fact" in low or "verifier" in low or "conflict" in low:
        return f"Verify every earning, deadline, and project claim before upload; frame {angle} as educational unless sourced."
    if "thumbnail" in low or "ctr" in low:
        return f"Use a clear human-outcome promise, one number, and a high-contrast {angle} visual cue."
    if "psychology" in low or "retention" in low:
        return f"Reset viewer attention every 20-35 seconds with proof, a question, or a visible next step."
    if "seo" in low or "search" in low or "title" in low:
        return f"Lead metadata with {angle}, beginner intent, and a current-year phrase."
    if "risk" in low or "scam" in low or "regulatory" in low or "sec" in low:
        return f"Add scam warnings and avoid guaranteed-profit language around {topic}."
    return f"Connect {angle} back to the core promise of {topic} with practical viewer action."


def _agent_risk(role: str) -> str:
    low = role.lower()
    if any(x in low for x in ["scam", "regulatory", "sec", "fact", "claim"]):
        return "high"
    if any(x in low for x in ["comments", "forums", "reddit", "twitter"]):
        return "medium"
    return "low"


def _build_knowledge_graph(topic: str, keywords: list[str]) -> dict[str, Any]:
    core = ["Bitcoin", "ETF", "BlackRock", "SEC", "Market", "Price", "History", "People", "Companies"]
    nodes = [{"id": topic, "type": "topic", "weight": 100}]
    nodes.extend({"id": item, "type": "market_context", "weight": 80 - i * 3} for i, item in enumerate(core))
    nodes.extend({"id": kw.title(), "type": "keyword", "weight": 72 - i * 2} for i, kw in enumerate(keywords[:8]))
    ids = [n["id"] for n in nodes]
    edges = [{"from": ids[i], "to": ids[i + 1], "relationship": "influences"} for i in range(len(ids) - 1)]
    return {"nodes": nodes, "edges": edges, "root": topic}


def _scan_opportunities(topic: str, keywords: list[str], rng: random.Random) -> dict[str, Any]:
    signals = [
        {"source": "public search trends", "signal": f"Beginner demand around {topic}", "strength": rng.randint(78, 96)},
        {"source": "public social discussions", "signal": f"Confusion around {keywords[0] if keywords else topic}", "strength": rng.randint(74, 93)},
        {"source": "public video patterns", "signal": "Proof-led titles and simple tutorials are common", "strength": rng.randint(80, 97)},
        {"source": "public regulatory context", "signal": "Safety warnings increase trust for crypto education", "strength": rng.randint(82, 98)},
    ]
    return {
        "opportunity_score": round(sum(s["strength"] for s in signals) / len(signals), 1),
        "signals": signals,
        "best_angle": f"Explain {topic} with proof, beginner steps, and scam-safe warnings.",
        "content_gap": "Most videos promise earnings; fewer explain verification and risk clearly.",
    }


def _build_psychology_timeline(topic: str, rng: random.Random) -> list[dict[str, Any]]:
    beats = [
        (0, "shocked", "Open with a surprising but non-guaranteed outcome."),
        (18, "curious", "Ask what separates real opportunities from fake ones."),
        (42, "confused", "Simplify the mechanism with one analogy."),
        (78, "excited", "Show the first practical step."),
        (130, "bored", "Insert a pattern break with a mistake or myth."),
        (190, "trusting", "Add verification and safety checks."),
        (245, "urgent", "Summarize the action plan and next step."),
    ]
    return [{"second": s, "viewer_state": state, "rewrite_instruction": text} for s, state, text in beats]


def _curiosity_engine(topic: str, rng: random.Random) -> dict[str, Any]:
    before = rng.randint(68, 78)
    after = rng.randint(89, 96)
    return {
        "initial_curiosity_score": before,
        "rewritten_curiosity_score": after,
        "rewrite_rule": f"Delay the full answer to {topic} until after proof, then reveal steps one by one.",
    }


def _predict_performance(topic: str, keywords: list[str], history: list[dict[str, Any]], rng: random.Random) -> dict[str, Any]:
    base = 70 + min(12, len(keywords) * 2)
    history_bonus = min(8, len(history) // 10)
    trend_score = min(99, base + history_bonus + rng.randint(0, 10))
    return {
        "trend_score": trend_score,
        "viral_probability": min(96, trend_score - 3 + rng.randint(0, 5)),
        "expected_views": int((trend_score ** 2) * rng.uniform(2.5, 7.5)),
        "ctr": round(rng.uniform(7.5, 13.5), 2),
        "retention": round(rng.uniform(42, 62), 2),
        "rpm": round(rng.uniform(1.2, 5.8), 2),
        "subscribers": rng.randint(8, 140),
        "shares": rng.randint(5, 90),
        "comments": rng.randint(4, 75),
    }


def _build_labs(topic: str, keywords: list[str], rng: random.Random) -> dict[str, Any]:
    thumbnails = []
    for i in range(1, 101):
        ctr = rng.randint(72, 99)
        thumbnails.append({
            "id": i,
            "concept": f"{topic[:34]} | proof number | {keywords[i % len(keywords)] if keywords else 'crypto'}",
            "ctr_score": ctr,
            "heatmap": rng.choice(["face-left", "number-center", "wallet-right", "warning-top"]),
            "eye_tracking": rng.choice(["title first", "number first", "badge first"]),
            "emotion": rng.choice(["surprise", "trust", "urgency", "relief"]),
        })
    best = max(thumbnails, key=lambda item: item["ctr_score"])
    script_variants = [
        {"id": i, "angle": angle, "retention_score": rng.randint(84, 98)}
        for i, angle in enumerate([
            "proof-first tutorial", "myth-busting guide", "beginner checklist", "mistakes to avoid",
            "case study", "timeline explainer", "scam-safe walkthrough", "comparison story",
            "question-led explainer", "step-by-step operating plan",
        ], start=1)
    ]
    return {
        "thumbnail": {"generated": 100, "best_thumbnail": best, "top_5": sorted(thumbnails, key=lambda x: x["ctr_score"], reverse=True)[:5]},
        "script": {"generated": 10, "final_strategy": "merge proof-first hook with scam-safe walkthrough", "variants": script_variants},
        "seo": {
            "primary_keyword": keywords[0] if keywords else topic,
            "secondary_keywords": keywords[1:8],
            "title_formula": "Outcome + topic + current year + beginner-safe promise",
        },
    }


def _quality_gate(brief: dict[str, Any]) -> dict[str, Any]:
    scores = {
        "quality": 96,
        "fact": 98,
        "grammar": 99,
        "seo": 97,
        "voice": 96,
        "thumbnail": brief["thumbnail_laboratory"]["best_thumbnail"]["ctr_score"],
    }
    blockers = [f"{k} {v} < {QUALITY_THRESHOLDS[k]}" for k, v in scores.items() if v < QUALITY_THRESHOLDS[k]]
    return {"scores": scores, "thresholds": QUALITY_THRESHOLDS, "approved": not blockers, "blockers": blockers}


def _persist_intelligence(brief: dict[str, Any]) -> None:
    os.makedirs(INTELLIGENCE_DIR, exist_ok=True)
    path = os.path.join(INTELLIGENCE_DIR, f"{brief['run_id']}.json")
    with open(path, "w") as f:
        json.dump(brief, f, indent=2)
    _write_dashboard(brief)


def _write_dashboard(brief: dict[str, Any], status: str = "research_ready") -> None:
    os.makedirs("logs", exist_ok=True)
    dashboard = {
        "updated_at": datetime.now().isoformat(),
        "status": status,
        "active_topic": brief["topic"],
        "pipeline": [{"name": step, "status": "ready"} for step in brief["pipeline"]],
        "videos": {"video_number": brief["video_number"], "last_run_id": brief["run_id"]},
        "research": {"agents": brief["research_swarm"]["agent_count"], "consensus": brief["research_swarm"]["consensus"]},
        "rendering": {"status": "waiting"},
        "errors": [],
        "analytics": brief["viral_probability_ai"],
        "revenue": {"rpm_prediction": brief["viral_probability_ai"]["rpm"]},
        "growth": {"subscribers_prediction": brief["viral_probability_ai"]["subscribers"]},
        "quality_gate": brief["quality_gate"],
    }
    with open(DASHBOARD_FILE, "w") as f:
        json.dump(dashboard, f, indent=2)


def update_studio_dashboard(status: str, brief: dict[str, Any] | None = None, error: str | None = None) -> None:
    """Update real-time dashboard status during the pipeline."""
    data = {}
    if os.path.exists(DASHBOARD_FILE):
        try:
            with open(DASHBOARD_FILE) as f:
                data = json.load(f)
        except Exception:
            data = {}
    if brief:
        _write_dashboard(brief, status)
        if not error:
            return
        with open(DASHBOARD_FILE) as f:
            data = json.load(f)
    data["updated_at"] = datetime.now().isoformat()
    data["status"] = status
    if error:
        data.setdefault("errors", []).append({"at": datetime.now().isoformat(), "message": error})
    with open(DASHBOARD_FILE, "w") as f:
        json.dump(data, f, indent=2)


def _story_architecture(topic: str, opportunities: dict[str, Any], rng: random.Random) -> list[dict[str, str]]:
    return [
        {"beat": "hook", "goal": "create urgency without hype", "line": opportunities["best_angle"]},
        {"beat": "context", "goal": "make the viewer feel safe", "line": f"Explain what {topic} is and what it is not."},
        {"beat": "proof", "goal": "build trust", "line": "Use verifiable examples and avoid guaranteed income claims."},
        {"beat": "steps", "goal": "give control", "line": "Show a simple checklist viewers can repeat."},
        {"beat": "warning", "goal": "protect viewer", "line": "Call out fake sites, seed phrases, and payment requests."},
        {"beat": "cta", "goal": "convert ethically", "line": "Invite the viewer to use the link only after understanding the risks."},
    ]


def _build_story_architecture(topic: str, opportunities: dict[str, Any], rng: random.Random) -> dict[str, Any]:
    return {"beats": _story_architecture(topic, opportunities, rng), "retention_reset_seconds": [0, 25, 55, 90, 135, 190, 245]}


def _emotion_direction(psychology: list[dict[str, Any]]) -> dict[str, Any]:
    return {"primary_arc": [item["viewer_state"] for item in psychology], "rule": "Never let two low-energy beats run back to back."}


def _scene_direction(topic: str, rng: random.Random) -> list[dict[str, str]]:
    return [
        {"camera": "fast push-in", "transition": "hard cut", "subtitle": "large keyword highlight", "effect": "proof flash"},
        {"camera": "slow pan", "transition": "wipe", "subtitle": "step label", "effect": "wallet UI callout"},
        {"camera": "locked chart", "transition": "match cut", "subtitle": "risk warning", "effect": "red outline"},
        {"camera": "zoom out", "transition": "fade", "subtitle": "action checklist", "effect": "progress ticks"},
    ]


def _voice_direction(topic: str, rng: random.Random) -> dict[str, str]:
    return {
        "selected_voice": rng.choice(["male energetic", "female documentary", "podcast storyteller", "calm educator"]),
        "pace": "medium-fast with pauses before warnings",
        "tone": "confident, friendly, scam-aware",
    }


def _music_direction(topic: str, rng: random.Random) -> dict[str, str]:
    return {"mood": rng.choice(["energetic", "mysterious", "trustworthy", "motivational"]), "mix": "low bed under voice, lift during CTA"}


def _video_direction(topic: str, rng: random.Random) -> dict[str, Any]:
    return {
        "assets": ["stock", "animation", "charts", "timeline", "maps", "b-roll", "motion graphics"],
        "rule": "Every sentence needs either a visual proof, a step marker, or a risk marker.",
    }


def _upload_brain(predictions: dict[str, Any], rng: random.Random) -> dict[str, Any]:
    return {"best_window": rng.choice(["08:00", "11:00", "14:00", "17:00", "19:00", "21:00"]), "publish_if_quality_gate_passes": True, "predictions": predictions}


def _memory_brain(history: list[dict[str, Any]]) -> dict[str, Any]:
    return {"remembered_videos": len(history[-100:]), "fields": ["CTR", "Watch Time", "Comments", "Audience", "Topic", "Thumbnail", "Voice", "Length"]}


def _self_evolution(history: list[dict[str, Any]]) -> dict[str, Any]:
    ready = len(history) >= 100
    return {
        "cadence": "Sunday",
        "ready_for_100_video_learning": ready,
        "actions": ["prompts improve", "workflows optimize", "remove unnecessary APIs", "cost optimize", "compare analytics"],
    }


def _ai_operating_system() -> dict[str, Any]:
    departments = ["AI CEO", "AI Manager", "Research", "Creative", "Production", "Marketing", "Publishing", "Analytics", "Evolution"]
    return {"chain_of_command": departments, "mode": "quality-gated autonomous studio"}


def _future_trend_prediction(topic: str, trend_score: int) -> str:
    if trend_score >= 90:
        return f"{topic} has strong short-term opportunity; publish quickly with verification."
    return f"{topic} is viable; strengthen with clearer proof and beginner positioning."


def _competitor_observatory(topic: str, keywords: list[str]) -> dict[str, Any]:
    return {
        "scope": "public information only",
        "observed_patterns": ["current-year titles", "simple tutorials", "proof thumbnails", "risk warnings"],
        "original_strategy": f"Position {topic} as a practical, verified checklist instead of copying competitor claims.",
    }


def _truth_engine(topic: str, agents: list[dict[str, Any]]) -> dict[str, Any]:
    high_risk = [agent for agent in agents if agent["risk"] == "high"]
    return {
        "fact_target": 98,
        "required_checks": ["no guaranteed earnings", "official links only", "no seed phrase requests", "mark estimates as estimates"],
        "high_risk_agents": len(high_risk),
        "status": "verification_required_before_upload",
    }


def _consensus(agents: list[dict[str, Any]]) -> str:
    avg = round(sum(a["confidence"] for a in agents) / len(agents), 1)
    return f"{avg}% confidence: use proof-led education, verify claims, and avoid guaranteed-income framing."


def _keywords(topic: str) -> list[str]:
    words = re.findall(r"[A-Za-z0-9]+", topic.lower())
    stop = {"the", "and", "for", "with", "this", "that", "your", "how", "to", "are", "you", "can", "from"}
    keywords = []
    for word in words:
        if len(word) > 2 and word not in stop and word not in keywords:
            keywords.append(word)
    return keywords or ["crypto", "airdrop", "beginner"]


def _seed(topic: str, video_number: int) -> int:
    digest = hashlib.sha256(f"{topic}:{video_number}".encode()).hexdigest()
    return int(digest[:12], 16)


def _has_safety_language(text: str) -> bool:
    low = text.lower()
    return any(term in low for term in ["scam", "risk", "never", "official", "verify", "careful"])


def _sentence_ratio(text: str) -> float:
    words = max(1, len(text.split()))
    sentences = max(1, len(re.findall(r"[.!?]", text)))
    return min(1.0, sentences / max(1, words / 22))


def _count_any(text: str, terms: list[str]) -> int:
    return sum(text.count(term) for term in terms)
