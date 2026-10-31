# ============================================================
#   SCENE_SYNC.PY — Put each scene's footage where the voice says it
#   Word timings come from edge-tts; without them, the script text
#   is used to estimate when each scene starts.
# ============================================================

import json
import os
import random
import re

MIN_SCENE = 4.0      # shorter scenes are merged into the previous one
CHAPTER_GAP = 10     # YouTube chapters must be at least 10s apart


def _tokens(text):
    return re.findall(r"[a-z0-9']+", str(text).lower())


def words_file(audio_path):
    return audio_path + ".words.json"


def load_word_times(audio_path):
    """[(seconds, word), ...] written by the voice generator, or [] if missing."""
    try:
        with open(words_file(audio_path)) as f:
            return [(float(t), str(w)) for t, w in json.load(f)]
    except Exception:
        return []


def _estimate_word_times(script, total_dur):
    """Spread the script's words over the audio, with a little extra time at sentence ends."""
    words = str(script).split()
    weights = [len(w) + 1 + (6 if w[-1:] in ".!?" else 2 if w[-1:] in ",;:" else 0) for w in words]
    total = sum(weights) or 1
    times, acc = [], 0
    for w, wt in zip(words, weights):
        times.append((total_dur * acc / total, w))
        acc += wt
    return times


def _find_phrase(tokens, phrase, start):
    """Index in tokens where phrase begins (searching from start), allowing small differences."""
    want = _tokens(phrase)[:6]
    if len(want) < 2:
        return None
    best, best_score = None, 0
    for i in range(start, max(start, len(tokens) - 1)):
        window = tokens[i:i + len(want)]
        score = sum(1 for a, b in zip(window, want) if a == b) / len(want)
        if score > best_score:
            best, best_score = i, score
            if score == 1:
                break
    return best if best_score >= 0.6 else None


def _parse_time(value):
    m = re.match(r"\s*(\d+):(\d{2})", str(value or ""))
    return int(m.group(1)) * 60 + int(m.group(2)) if m else None


def scene_timeline(script, scenes, audio_path, total_dur):
    """Start/end time of each scene, matched to the narration.

    Each scene's "says" (its first words in the script) is located in the
    spoken words. Scenes without a match fall back to their planned "time",
    scaled to the real audio length, then to an even split.
    """
    scenes = [s for s in (scenes or []) if isinstance(s, dict)]
    if not scenes or total_dur <= 0:
        return [{"start": 0.0, "end": total_dur, "scene": {}}]

    timed = load_word_times(audio_path) if audio_path else []
    source = "voice" if timed else "script"
    if not timed:
        timed = _estimate_word_times(script, total_dur)
    tokens, times = [], []
    for t, w in timed:
        for tok in _tokens(w):
            tokens.append(tok)
            times.append(t)

    planned = [_parse_time(s.get("time")) for s in scenes]
    known = [p for p in planned if p is not None]
    plan_end = max(known) + 30 if known else None

    starts, cursor, matched = [], 0, 0
    for i, s in enumerate(scenes):
        idx = _find_phrase(tokens, s.get("says", ""), cursor) if tokens else None
        if idx is not None:
            starts.append(times[idx])
            cursor = idx + 1
            matched += 1
        elif planned[i] is not None and plan_end:
            starts.append(total_dur * planned[i] / plan_end)
        else:
            starts.append(total_dur * i / len(scenes))
    starts[0] = 0.0

    # Keep times in order, and merge scenes too short to show anything
    timeline = []
    for s, start in zip(scenes, starts):
        if timeline and (start <= timeline[-1]["start"] or start - timeline[-1]["start"] < MIN_SCENE):
            continue
        if total_dur - start < MIN_SCENE:
            continue
        timeline.append({"start": round(start, 2), "scene": s})
    for a, b in zip(timeline, timeline[1:]):
        a["end"] = b["start"]
    timeline[-1]["end"] = total_dur
    print(f"🎯 Scene sync: {len(timeline)} scenes, {matched}/{len(scenes)} matched to the {source} words")
    return timeline


def _fmt(sec):
    sec = int(sec)
    return f"{sec // 60}:{sec % 60:02d}"


def retime_description(description, timeline):
    """Replace the planned timestamps with the real ones from the voice."""
    lines, last = [], None
    for item in timeline:
        name = item["scene"].get("scene")
        if not name or (last is not None and item["start"] - last < CHAPTER_GAP):
            continue
        lines.append(f"{_fmt(item['start'])} - {name}")
        last = item["start"]
    block = "⏱️ TIMESTAMPS\n"
    if block not in description:
        return description
    head, rest = description.split(block, 1)
    tail = rest.split("\n\n", 1)[1] if "\n\n" in rest else ""
    if len(lines) < 3:  # YouTube needs 3+ chapters starting at 0:00
        return head + tail
    return head + block + "\n".join(lines) + "\n\n" + tail


class FootageAllocator:
    """Hands out pieces of clips so the same footage is never shown twice in one video."""

    def __init__(self, durations):
        self.free = {p: [(0.0, d)] for p, d in durations.items() if d > 0}
        self.repeats = 0

    def _take_from(self, path, length):
        spans = [s for s in self.free.get(path, []) if s[1] - s[0] >= length]
        if not spans:
            return None
        span = random.choice(spans)
        # Cut from one end of the free span, so what is left stays in one usable piece
        start = round(random.choice([span[0], span[1] - length]), 2)
        self.free[path].remove(span)
        self.free[path] += [s for s in [(span[0], start), (start + length, span[1])] if s[1] - s[0] >= 1.0]
        return start

    def take(self, preferred, length, avoid=None, borrow=True):
        """(path, start) for `length` seconds, from preferred clips first, then (if borrow) any clip."""
        others = [p for p in self.free if p not in preferred] if borrow else []
        for group in (list(preferred), others):
            random.shuffle(group)
            group.sort(key=lambda p: (p == avoid, -max([e - s for s, e in self.free.get(p, [])] or [0])))
            for p in group:
                start = self._take_from(p, length)
                if start is not None:
                    return p, start
        return None

    def take_any(self, preferred, length, avoid=None):
        """Like take(), but repeats footage instead of failing when everything is used."""
        got = self.take(preferred, length, avoid)
        if got:
            return got
        pool = [p for p in (list(preferred) or list(self.free)) if p != avoid] or list(preferred) or list(self.free)
        if not pool:
            return None
        self.repeats += 1
        return random.choice(pool), 0.0


def plan_scene_segments(timeline, scene_clips, durations, seg_target=7.0, min_seg=3.0):
    """List of (path, start_in_clip, video_time, length) covering the whole timeline.

    Every scene is filled with its own clips (searched for what is said in it).
    If a scene runs out, unused footage from other scenes is borrowed before
    anything repeats.
    """
    alloc = FootageAllocator(durations)
    plan, last = [], None
    for i, item in enumerate(timeline):
        length = item["end"] - item["start"]
        n = max(1, round(length / seg_target))
        clips = [c for c in scene_clips.get(i, []) if c in alloc.free]
        t = item["start"]
        while length - (t - item["start"]) > 0.05:
            remaining = item["end"] - t
            seg = remaining if n <= 1 else remaining / n
            # This scene's own footage first, in shorter pieces if needed; then borrow
            got = alloc.take(clips, seg, avoid=last, borrow=False)
            while not got and seg / 2 >= min_seg:
                seg /= 2
                got = alloc.take(clips, seg, avoid=last, borrow=False)
            if not got:
                seg = remaining if n <= 1 else remaining / n
                got = alloc.take(clips, seg, avoid=last)
            if not got:
                seg = min(remaining, seg_target)
                got = alloc.take_any(clips, seg, avoid=last)
                if not got:
                    return plan, alloc.repeats
            path, start = got
            plan.append((path, start, round(t, 2), round(seg, 2)))
            last, t, n = path, t + seg, max(1, n - 1)
    if alloc.repeats:
        print(f"⚠️  Not enough footage: {alloc.repeats} segment(s) had to repeat")
    return plan, alloc.repeats
