# ============================================================
#   UNIQUENESS.PY — Persistent "never repeat" memory
#   Remembers every title, angle, opening line, overlay, clip,
#   thumbnail text and script fingerprint across runs, so no two
#   videos look or sound the same (YouTube buries reused content).
#   Stored next to brain_data.json so it survives git checkout.
# ============================================================

import json
import os
import random
import re
import zlib
from datetime import datetime

DATA_DIR = os.environ.get("YT_BOT_DATA_DIR") or os.path.expanduser("~/youtube_bot_data")
MEMORY_FILE = os.path.join(DATA_DIR, "uniqueness.json")

MAX_ITEMS = 2000          # per kind, oldest dropped first
MINHASH_SIZE = 64
SCRIPT_SIMILARITY_LIMIT = 0.35   # estimated Jaccard of word 5-grams
TEXT_SIMILARITY_LIMIT = 0.6      # word-set Jaccard for opening lines / questions
# Titles are short and share niche words ("crypto airdrop"), so they only
# count as repeats when nearly all their key words match
TITLE_SIMILARITY_LIMIT = 0.75

_STOP = {"the", "a", "an", "and", "or", "to", "of", "in", "on", "for", "is", "it", "you",
         "your", "this", "that", "how", "what", "why", "with", "are", "be", "do", "i"}

# Video formats — each gives the script a different structure, so the same
# topic can be covered many times without the video feeling like a repeat.
# Every format is built around an open loop that is paid off inside the video.
FORMATS = [
    {"key": "countdown", "name": "Countdown (best saved for last)",
     "structure": "Count down {n} points from least to most important. Tease the #1 point in the first 20 seconds but reveal it last.",
     "sections": ["The #1 point teased", "Point {n}", "Points {n_minus} to 2", "The #1 point revealed", "What to do next"]},
    {"key": "myth_reality", "name": "Myth vs Reality",
     "structure": "Bust {n} popular myths. For each: state the myth, ask the viewer if they believe it, then reveal the reality with a concrete example.",
     "sections": ["The myth almost everyone believes", "Myths 1-2", "The myth that costs people the most", "Reality check", "What to do instead"]},
    {"key": "mystery", "name": "Mystery / case study",
     "structure": "Open with a puzzling real-world pattern (no invented names or numbers). Investigate it like a detective, ruling out wrong explanations, and reveal the real cause near the end.",
     "sections": ["The puzzle", "First suspect", "The clue most people miss", "The real answer", "How to use this"]},
    {"key": "question", "name": "One big question",
     "structure": "Pose one precise question in the first sentence. Build the answer in layers, each layer raising a smaller question that the next layer answers. Give the full answer at the end.",
     "sections": ["The question", "Why the obvious answer is wrong", "Layer 1", "Layer 2", "The full answer"]},
    {"key": "before_after", "name": "Before you click",
     "structure": "Walk through the exact moment a beginner is about to connect a wallet or claim. Pause before each click and explain what to check and why.",
     "sections": ["The moment before the click", "Check 1", "The check that stops most scams", "After the click", "Your checklist"]},
    {"key": "beginner_vs_pro", "name": "Beginner vs careful pro",
     "structure": "Compare what a rushed beginner does with what a careful, experienced user does at each stage. End with the single habit that makes the biggest difference.",
     "sections": ["Two people, same airdrop", "Setup", "Activity", "Claiming", "The habit that matters most"]},
    {"key": "first_week", "name": "First week plan",
     "structure": "Lay out a realistic day-by-day plan for someone's first {n} days. Tease the day where most people quit and explain why.",
     "sections": ["The plan", "Days 1-2", "The day most people quit", "Final days", "Keep or stop?"]},
    {"key": "red_flags", "name": "Red flag hunt",
     "structure": "Show {n} warning signs, from obvious to subtle. Ask the viewer to spot the problem before each reveal. The subtlest flag comes last.",
     "sections": ["Can you spot it?", "Obvious flags", "Subtle flags", "The flag even pros miss", "Your safety routine"]},
    {"key": "explain_like_five", "name": "Explain it simply",
     "structure": "Explain the topic with one everyday analogy that carries through the whole video. Reveal at the end where the analogy breaks down, because that is where people get hurt.",
     "sections": ["The analogy", "How it works", "Real example", "Where the analogy breaks", "What it means for you"]},
    {"key": "timeline", "name": "Timeline / how it changed",
     "structure": "Explain how this part of crypto evolved in stages (no invented dates or amounts). Tease what changed most recently and why it matters now, and reveal it at the end.",
     "sections": ["Where it started", "Stage 2", "What changed", "Where it is now", "What to watch next"]},
    {"key": "cost_breakdown", "name": "True cost breakdown",
     "structure": "Break down the real costs: gas, time, risk, attention. Ask the viewer to guess the most overlooked cost, and reveal it last.",
     "sections": ["Guess the hidden cost", "Visible costs", "Time and risk", "The cost nobody counts", "Is it worth it for you?"]},
    {"key": "checklist", "name": "Pre-flight checklist",
     "structure": "Build a {n}-step checklist live, explaining why each step exists. Tease the step most people skip and show what happens when they do.",
     "sections": ["Why a checklist", "Steps 1-3", "The step people skip", "Final steps", "Save this list"]},
    {"key": "what_if", "name": "What if?",
     "structure": "Run through {n} what-if scenarios (e.g. what if the site is fake, what if gas spikes). Each scenario ends with a clear answer. The most dangerous scenario comes last.",
     "sections": ["What if...", "Scenario 1", "Scenarios 2-3", "The dangerous one", "Your plan"]},
    {"key": "debunk_advice", "name": "Popular advice, tested",
     "structure": "Take {n} pieces of common advice and test each against how airdrops actually work. Tease which advice is the worst and reveal it last.",
     "sections": ["Advice everyone repeats", "Advice 1", "Advice 2", "The worst advice", "Better advice"]},
    {"key": "anatomy", "name": "Anatomy of one airdrop",
     "structure": "Dissect a generic airdrop lifecycle step by step (announcement, eligibility, snapshot, claim, sell or hold). Tease the stage where most value is lost.",
     "sections": ["The lifecycle", "Announcement", "Eligibility and snapshot", "The stage where value is lost", "Claim and after"]},
]


# ── storage ──────────────────────────────────────────────────

def _load() -> dict:
    try:
        with open(MEMORY_FILE) as f:
            return json.load(f)
    except Exception:
        return {}


def _save(mem: dict):
    os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
    tmp = MEMORY_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(mem, f)
    os.replace(tmp, MEMORY_FILE)


def seen(kind: str) -> list:
    return list(_load().get(kind, []))


def remember(kind: str, *values):
    mem = _load()
    items = mem.setdefault(kind, [])
    for v in values:
        if v is not None and v != "":
            items.append(v)
    mem[kind] = items[-MAX_ITEMS:]
    _save(mem)


# ── similarity helpers ───────────────────────────────────────

def _words(text: str) -> list:
    return re.findall(r"[a-z0-9]+", str(text).lower())


def normalize(text: str) -> str:
    return " ".join(_words(text))


def _content_words(text: str) -> set:
    return {w for w in _words(text) if w not in _STOP}


def text_similarity(a: str, b: str) -> float:
    wa, wb = _content_words(a), _content_words(b)
    if not wa or not wb:
        return 1.0 if normalize(a) == normalize(b) else 0.0
    return len(wa & wb) / len(wa | wb)


def most_similar(text: str, kind: str) -> tuple:
    best, best_text = 0.0, None
    for old in seen(kind):
        s = text_similarity(text, old)
        if s > best:
            best, best_text = s, old
    return best, best_text


def is_fresh_text(text: str, kind: str, limit: float = TEXT_SIMILARITY_LIMIT) -> bool:
    if not text:
        return False
    return most_similar(text, kind)[0] < limit


def fingerprint(script: str, k: int = 5) -> list:
    """MinHash signature of word k-grams — compact, compares scripts in O(64)."""
    w = _words(script)
    grams = {" ".join(w[i:i + k]) for i in range(max(1, len(w) - k + 1))}
    hashes = [zlib.crc32(g.encode()) for g in grams] or [0]
    sig = []
    for seed in range(MINHASH_SIZE):
        salt = (seed * 0x9E3779B1) & 0xFFFFFFFF
        sig.append(min((h ^ salt) * 2654435761 % 4294967311 for h in hashes))
    return sig


def fingerprint_similarity(a: list, b: list) -> float:
    if not a or not b:
        return 0.0
    return sum(1 for x, y in zip(a, b) if x == y) / min(len(a), len(b))


def script_overlap(script: str) -> float:
    fp = fingerprint(script)
    return max((fingerprint_similarity(fp, old) for old in seen("script_fp")), default=0.0)


def first_sentence(script: str) -> str:
    m = re.split(r"(?<=[.!?])\s+", script.strip(), maxsplit=1)
    return m[0] if m else ""


# ── pickers ──────────────────────────────────────────────────

def pick_fresh(kind: str, options: list, rng=random):
    """Pick an option never used before; else the least recently used one."""
    if not options:
        return None
    used = seen(kind)
    unused = [o for o in options if o not in used]
    if unused:
        return rng.choice(unused)
    last_seen = {o: i for i, o in enumerate(used)}
    oldest = min(options, key=lambda o: last_seen.get(o, -1))
    return oldest


def pick_angle(topics: list, recent_topics: list = None, rng=random) -> tuple:
    """Choose a (topic, format) pair that has never been made before.

    15 formats x the topic pool gives hundreds of distinct videos, and the
    format also rotates so back-to-back videos never share a structure.
    """
    used = set(seen("angle"))
    recent_formats = seen("format")[-len(FORMATS) // 2:]
    recent_topics = set(recent_topics or [])
    formats = [f for f in FORMATS if f["key"] not in recent_formats] or FORMATS

    pairs = [(t, f) for t in topics for f in formats if f"{t}|{f['key']}" not in used]
    preferred = [(t, f) for t, f in pairs if t not in recent_topics]
    pool = preferred or pairs
    if not pool:
        # Every combination used — fall back to the least used topic with a rotated format
        topic_count = {}
        for a in used:
            t = a.split("|", 1)[0]
            topic_count[t] = topic_count.get(t, 0) + 1
        t = min(topics, key=lambda x: topic_count.get(x, 0))
        return t, rng.choice(formats)
    return rng.choice(pool)


def format_details(fmt: dict, rng=random) -> dict:
    n = rng.choice([3, 4, 5, 6, 7])
    fill = {"n": n, "n_minus": n - 1}
    return {
        "key": fmt["key"],
        "name": fmt["name"],
        "structure": fmt["structure"].format(**fill),
        "sections": [s.format(**fill) for s in fmt["sections"]],
    }


def record_video_memory(data: dict, extra: dict = None):
    """Store everything that must not repeat in a future video."""
    extra = extra or {}
    mem = _load()

    def add(kind, *values):
        items = mem.setdefault(kind, [])
        items.extend(v for v in values if v)
        mem[kind] = items[-MAX_ITEMS:]

    fmt = (data.get("format") or {}).get("key")
    add("title", data.get("title"))
    add("topic", data.get("topic"))
    add("format", fmt)
    add("angle", f"{data.get('topic')}|{fmt}" if fmt else None)
    add("opening", first_sentence(data.get("script", "")))
    add("curiosity_question", data.get("curiosity_question"))
    add("thumbnail_text", data.get("thumbnail_text"))
    add("overlay_set", "|".join(normalize(s.get("text_overlay", "")) for s in data.get("scenes", [])))
    add("overlay", *[normalize(s.get("text_overlay", "")) for s in data.get("scenes", [])])
    add("script_fp", fingerprint(data.get("script", "")))
    elements = data.get("elements") or {}
    add("intro_style", elements.get("intro"))
    add("section_hook", elements.get("section_hook"))
    add("outro_style", elements.get("outro"))
    for kind, values in extra.items():
        add(kind, *(values if isinstance(values, list) else [values]))
    mem["updated_at"] = datetime.now().isoformat()
    _save(mem)


def uniqueness_report(data: dict) -> dict:
    """Check a generated video against everything published before."""
    problems = []
    title_sim, title_old = most_similar(data.get("title", ""), "title")
    if title_sim >= TITLE_SIMILARITY_LIMIT:
        problems.append(f"title too close to an old title: {title_old!r}")
    opening = first_sentence(data.get("script", ""))
    open_sim, open_old = most_similar(opening, "opening")
    if open_sim >= TEXT_SIMILARITY_LIMIT:
        problems.append(f"opening line repeats an old one: {open_old!r}")
    q = data.get("curiosity_question", "")
    if q and not is_fresh_text(q, "curiosity_question"):
        problems.append("curiosity question was used before")
    thumb = data.get("thumbnail_text", "")
    if thumb and normalize(thumb) in {normalize(t) for t in seen("thumbnail_text")}:
        problems.append("thumbnail text was used before")
    overlay_set = "|".join(normalize(s.get("text_overlay", "")) for s in data.get("scenes", []))
    if overlay_set and overlay_set in seen("overlay_set"):
        problems.append("on-screen text sequence is identical to an old video")
    overlap = script_overlap(data.get("script", ""))
    if overlap >= SCRIPT_SIMILARITY_LIMIT:
        problems.append(f"script overlaps {overlap:.0%} with an old script")
    return {"unique": not problems, "problems": problems, "script_overlap": round(overlap, 3)}


