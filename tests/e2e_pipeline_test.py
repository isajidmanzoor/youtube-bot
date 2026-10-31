"""End-to-end test of the full video pipeline (advanced_main.make_complete_video).

Everything runs for real — topic picking, titles, scripts, quality and
uniqueness gates, clip planning, moviepy rendering, thumbnails, shorts, the
upload/comment calls and the persistent memory — except the network:
Groq, Pexels, news, music, TTS and the YouTube API are replaced by local fakes.

    python tests/e2e_pipeline_test.py                 # 1 rendered + 25 soak videos
    python tests/e2e_pipeline_test.py --render 1 --soak 10

Needs moviepy==1.0.3, Pillow, numpy, imageio-ffmpeg (requirements.txt).
Renders at 640x360 to stay fast (VIDEO_WIDTH/VIDEO_HEIGHT/FPS env vars).
"""
import argparse
import io
import itertools
import json
import os
import pickle
import random
import re
import shutil
import subprocess
import sys
import tempfile
import types
import zlib

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ap = argparse.ArgumentParser()
ap.add_argument("--render", type=int, default=1, help="videos rendered for real with moviepy (incl. a 1080x1920 short, slow)")
ap.add_argument("--soak", type=int, default=25, help="videos run with rendering stubbed, to test uniqueness")
ap.add_argument("--voice-seconds", type=float, default=60.0, help="voice length of the rendered videos")
ap.add_argument("--soak-voice-seconds", type=float, default=300.0, help="voice length of the soak videos (5 min, like production)")
ap.add_argument("--keep", action="store_true", help="keep the temp work dir")
args = ap.parse_args()

WORK = tempfile.mkdtemp(prefix="ytbot_e2e_")
os.environ.update({
    "HOME": WORK, "USERPROFILE": WORK, "YT_BOT_DATA_DIR": os.path.join(WORK, "youtube_bot_data"),
    "VIDEO_WIDTH": "640", "VIDEO_HEIGHT": "360", "FPS": "12",
})
os.chdir(WORK)
sys.path.insert(0, REPO)
rng = random.Random(1234)

import imageio_ffmpeg  # noqa: E402
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()


def ffmpeg(*a):
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", *a], check=True)


# ── sample media ─────────────────────────────────────────────
MEDIA = os.path.join(WORK, "_media")
os.makedirs(MEDIA)
SAMPLE_CLIPS = []
for i, src in enumerate(["testsrc", "testsrc2", "smptebars"]):
    p = os.path.join(MEDIA, f"sample{i}.mp4")
    ffmpeg("-f", "lavfi", "-i", f"{src}=duration={10 + 3 * i}:size=640x360:rate=12", "-pix_fmt", "yuv420p", p)
    SAMPLE_CLIPS.append(open(p, "rb").read())

from PIL import Image  # noqa: E402
_buf = io.BytesIO()
Image.new("RGB", (800, 600), (40, 90, 160)).save(_buf, "JPEG")
SAMPLE_JPG = _buf.getvalue()


def make_voice(path, seconds):
    ffmpeg("-f", "lavfi", "-i", f"sine=frequency=220:duration={seconds}", "-ar", "44100", path)


# ── fake network ─────────────────────────────────────────────
WORDS = ("wallet bridge gas snapshot claim token quest testnet ledger approval signature contract "
         "phishing domain bookmark explorer swap liquidity points season eligibility criteria sybil "
         "cluster farming budget spreadsheet calendar habit patience receipt network fee layer rollup "
         "validator governance vote forum roadmap audit drainer permit revoke allowance hardware "
         "seed phrase burner discord telegram moderator announcement deadline vesting unlock market "
         "volume price tax record export history dashboard tracker alert filter checklist routine "
         "mistake myth reality question answer clue puzzle detective analogy lifecycle stage "
         "careful honest simple practical concrete specific beginner patient curious skeptical").split()
LLM = {"mode": "ok", "last_script": None, "calls": 0}


class Resp:
    def __init__(self, status=200, payload=None, text="", content=b""):
        self.status_code, self._p, self.text, self.content = status, payload, text, content

    def json(self):
        return self._p

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")

    def iter_content(self, chunk_size=8192):
        for i in range(0, len(self.content), chunk_size):
            yield self.content[i:i + chunk_size]


def _phrase(n):
    return " ".join(rng.choice(WORDS) for _ in range(n))


def _sentence(n=None):
    s = rng.choice(["you ", "now you ", "remember, you ", "today you ", ""]) + _phrase(n or rng.randint(7, 13))
    return s[0].upper() + s[1:] + "."


def fake_llm(prompt):
    if "title expert" in prompt:
        topic = re.search(r'video about: "(.*?)"', prompt).group(1)
        fmt = re.search(r'The video format is "(.*?)"', prompt)
        lead = rng.choice(["Why", "The", "What", "How", "Nobody Explains", "Before You", "Inside"])
        return f"{lead} {topic.split(' ')[0]} {_phrase(3).title()} ({fmt.group(1).split(' ')[0] if fmt else 'Guide'})"
    if "Return ONLY this exact JSON format" in prompt:
        if LLM["mode"] == "copycat" and LLM["last_script"]:
            return LLM["last_script"]
        n_scenes = int(re.search(r"Give (\d+)-(\d+) scenes", prompt).group(2))
        title = re.search(r'Use this EXACT title: "(.*?)"', prompt).group(1)
        body = [f"Why does {_phrase(4)} decide everything for you?"]
        body += [_sentence() for _ in range(rng.randint(62, 80))]
        body.insert(20, "Never share your seed phrase and always verify the official link.")
        body.append("The link in the description is an affiliate link, so I may earn a commission. What would you check first?")
        sentences = [b for b in body if b]
        step = len(sentences) / n_scenes  # spread over the script, like the prompt asks
        picks = [int(k * step) + rng.randint(-1, 1) for k in range(1, n_scenes)]
        says = [sentences[0]] + [sentences[k] for k in picks]
        # the model sometimes changes a word; one scene gets a small difference
        says[2] = re.sub(r"\b\w+\b", "uh", says[2], count=1)
        data = {
            "title": title,
            "curiosity_question": f"Which {_phrase(3)} matters most?",
            "payoff": _sentence(),
            "thumbnail_text": _phrase(3).upper(),
            "script": " ".join(body),
            "scenes": [{"time": f"{i // 2}:{rng.randint(0, 5)}0", "scene": _phrase(2).title(), "says": " ".join(says[i].split()[:8]),
                        "visual": _phrase(2), "text_overlay": _phrase(4)} for i in range(n_scenes)],
            "description_intro": _sentence() + " " + _sentence(),
            "tags": [_phrase(2) for _ in range(10)],
            "search_query": _phrase(2),
            "comment_question": f"Which {_phrase(3)} would you try first?",
        }
        LLM["last_script"] = "```json\n" + json.dumps(data) + "\n```"
        return LLM["last_script"]
    return "Thanks for the question - always verify official links first."


def fake_post(url, headers=None, json=None, timeout=None, **kw):
    LLM["calls"] += 1
    if "groq.com" in url:
        if LLM["mode"] == "fail":
            return Resp(500, {})
        return Resp(200, {"choices": [{"message": {"content": fake_llm(json["messages"][0]["content"])}}]})
    return Resp(404, {})


PEXELS_CATALOG = 6000  # real Pexels has far more; section 4b shrinks it to test running out
PEXELS_PAGES = []


def fake_get(url, timeout=None, params=None, headers=None, stream=False, **kw):
    if "coindesk" in url:
        return Resp(200, text="<title><![CDATA[Ethereum fees fall after upgrade]]></title>")
    if "api.pexels.com/videos/search" in url:
        per, page = params["per_page"], params["page"]
        # like the real API, each search text has its own result list of limited size
        total = 30 + zlib.crc32(params["query"].encode()) % 50
        start = zlib.crc32(params["query"].encode()) % PEXELS_CATALOG
        ids = [(start + k) % PEXELS_CATALOG + 1 for k in range((page - 1) * per, min(total, page * per))]
        PEXELS_PAGES.append(page)
        return Resp(200, {"total_results": total, "videos": [{"id": i, "video_files": [
            {"file_type": "video/mp4", "width": 640, "link": f"https://fake.pexels/v/{i}.mp4"}]} for i in ids]})
    if url.startswith("https://fake.pexels/v/"):
        i = int(url.rsplit("/", 1)[1].split(".")[0])
        return Resp(200, content=SAMPLE_CLIPS[i % len(SAMPLE_CLIPS)])
    if "api.pexels.com/v1/search" in url:
        ids = [rng.randint(1, 10_000) for _ in range(params.get("per_page", 10))]
        return Resp(200, {"photos": [{"id": i, "src": {"large": f"https://fake.pexels/p/{i}.jpg"}} for i in ids]})
    if url.startswith("https://fake.pexels/p/"):
        return Resp(200, content=SAMPLE_JPG)
    return Resp(404, {})


sys.modules["requests"] = types.SimpleNamespace(post=fake_post, get=fake_get,
                                                exceptions=types.SimpleNamespace(RequestException=RuntimeError))

# TTS: edge-tts writes a real audio file of the configured length
VOICE = {"seconds": args.voice_seconds}


class Communicate:
    def __init__(self, text, voice, rate=None, pitch=None, boundary="SentenceBoundary"):
        self.text, self.boundary = text, boundary

    async def save(self, path):
        make_voice(path, VOICE["seconds"])

    async def stream(self):
        tmp = os.path.join(MEDIA, "voice_tmp.mp3")
        make_voice(tmp, VOICE["seconds"])
        yield {"type": "audio", "data": open(tmp, "rb").read()}
        words = self.text.split()
        weights = [1 + 0.15 * len(w) + (2.5 if w[-1] in ".?!" else 0) for w in words]
        scale = VOICE["seconds"] * 0.97 / sum(weights)
        t = 0.3
        for w, wt in zip(words, weights):
            VOICE_WORDS.append((t, w))
            yield {"type": "WordBoundary", "offset": int(t * 1e7), "duration": int(wt * scale * 0.7 * 1e7), "text": w.strip(".,?!")}
            t += wt * scale


VOICE_WORDS = []


sys.modules["edge_tts"] = types.SimpleNamespace(Communicate=Communicate)
Communicate.__signature__ = None  # inspect.signature reads __init__
sys.modules["gtts"] = types.SimpleNamespace(gTTS=None)

# YouTube API
API = {"inserts": [], "comments": [], "playlists": [], "playlist_items": []}


class Exec:
    def __init__(self, fn):
        self.fn = fn

    def execute(self):
        return self.fn()

    def next_chunk(self):
        return None, self.fn()


class Service:
    def videos(self):
        class V:
            def insert(self, part, body, media_body):
                API["inserts"].append(body)
                return Exec(lambda: {"id": f"vid{len(API['inserts']):03d}"})

            def list(self, part, id):
                return Exec(lambda: {"items": [{"id": v, "statistics": {"viewCount": "0"}} for v in id.split(",")]})
        return V()

    def commentThreads(self):
        class C:
            def insert(self, part, body):
                API["comments"].append(body["snippet"])
                return Exec(lambda: {})

            def list(self, **kw):
                return Exec(lambda: {"items": []})
        return C()

    def playlists(self):
        class P:
            def insert(self, part, body):
                API["playlists"].append(body["snippet"]["title"])
                return Exec(lambda: {"id": f"PL{len(API['playlists'])}"})
        return P()

    def playlistItems(self):
        class I:
            def insert(self, part, body):
                API["playlist_items"].append((body["snippet"]["playlistId"], body["snippet"]["resourceId"]["videoId"]))
                return Exec(lambda: {})
        return I()

    def thumbnails(self):
        class T:
            def set(self, videoId, media_body):
                return Exec(lambda: {})
        return T()


def mod(name, **attrs):
    m = types.ModuleType(name)
    m.__dict__.update(attrs)
    sys.modules[name] = m
    return m


mod("google"); mod("google.auth"); mod("google.auth.transport")
mod("google.auth.transport.requests", Request=object)
mod("google_auth_oauthlib"); mod("google_auth_oauthlib.flow", InstalledAppFlow=object)
mod("googleapiclient"); mod("googleapiclient.discovery", build=lambda *a, **k: Service())
mod("googleapiclient.http", MediaFileUpload=lambda *a, **k: None)


class Creds:
    valid, expired, refresh_token = True, False, None


mod("e2e_creds", Creds=Creds)
Creds.__module__ = "e2e_creds"
with open("youtube_token.pickle", "wb") as f:
    pickle.dump(Creds(), f)

# ── run the real pipeline ────────────────────────────────────
import advanced_main  # noqa: E402
import advanced_script_gen  # noqa: E402
from advanced_video_gen import plan_clip_windows, _scene_labels_from_plan  # noqa: E402
from brain import uniqueness as U  # noqa: E402
import scene_sync  # noqa: E402
from advanced_thumbnail_gen import _fit_title  # noqa: E402

TIMELINES, PLANS = [], []
_orig_timeline = advanced_main.scene_timeline


def capture_timeline(script, scenes, audio_path, total_dur):
    tl = _orig_timeline(script, scenes, audio_path, total_dur)
    TIMELINES.append({"timeline": tl, "words": scene_sync.load_word_times(audio_path), "dur": total_dur,
                      "scenes": scenes})
    return tl


advanced_main.scene_timeline = capture_timeline
_orig_plan = scene_sync.plan_scene_segments


def capture_plan(timeline, scene_clips, durations, *a, **k):
    plan, repeats = _orig_plan(timeline, scene_clips, durations, *a, **k)
    PLANS.append({"plan": plan, "repeats": repeats, "timeline": timeline, "scene_clips": scene_clips, "durations": durations})
    return plan, repeats


scene_sync.plan_scene_segments = capture_plan

FAILS = []


def check(cond, msg):
    print(("  PASS " if cond else "  FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


SCRIPTS = []
_orig_gen = advanced_main.generate_advanced_script


def capture_script(*a, **k):
    data = _orig_gen(*a, **k)
    SCRIPTS.append(data)
    return data


advanced_main.generate_advanced_script = capture_script

FETCHED = []
_orig_fetch = advanced_main.fetch_pexels_videos


def capture_fetch(*a, **k):
    got = _orig_fetch(*a, **k)
    FETCHED[-1].extend(got)
    return got


advanced_main.fetch_pexels_videos = capture_fetch

BAD = re.compile(r"(?i)\$\d+\s*(earned|withdrawn)|withdrawal proof|no investment|free crypto|i made \$|zero investment")
RESULTS = []


def run_one(tag, render=True):
    FETCHED.append([])
    n_inserts, n_comments = len(API["inserts"]), len(API["comments"])
    if not render:
        def fake_render(audio, clips, filename, *a, **k):
            p = os.path.join("output", "videos", f"{filename}.mp4")
            os.makedirs(os.path.dirname(p), exist_ok=True)
            shutil.copy(os.path.join(MEDIA, "sample0.mp4"), p)
            return p
        advanced_main.build_advanced_video = fake_render
        advanced_main.create_short = lambda *a, **k: None
    n_timelines = len(TIMELINES)
    r = advanced_main.make_complete_video()
    r["timeline"] = TIMELINES[-1] if len(TIMELINES) > n_timelines else None
    r["clips"] = [os.path.basename(c) for c in FETCHED[-1]]
    r["new_inserts"] = API["inserts"][n_inserts:]
    r["new_comments"] = API["comments"][n_comments:]
    r["data"] = SCRIPTS[-1] if SCRIPTS else None
    RESULTS.append(r)
    print(f"[{tag}] success={r['success']} title={r['title']!r} error={r['error']}")
    return r


print(f"\n=== Work dir: {WORK}")
print("\n=== 1. Rendered end-to-end videos (moviepy, thumbnail, short, upload)")
import advanced_video_gen  # noqa: E402
import shorts_gen  # noqa: E402
real_build, real_short = advanced_video_gen.build_advanced_video, shorts_gen.create_short
for i in range(args.render):
    advanced_main.build_advanced_video, advanced_main.create_short = real_build, real_short
    r = run_one(f"render {i + 1}")
    check(r["success"], f"render {i + 1}: pipeline succeeded")
    if not r["success"]:
        continue
    vids = sorted(f for f in os.listdir("output/videos") if f.endswith(".mp4"))
    from moviepy.editor import VideoFileClip
    final = max((os.path.join("output/videos", f) for f in vids), key=os.path.getmtime)
    clip = VideoFileClip(final)
    check(abs(clip.duration - args.voice_seconds) < 2.5, f"render {i + 1}: video length {clip.duration:.1f}s matches voice")
    check((clip.w, clip.h) == (640, 360), f"render {i + 1}: video size {clip.w}x{clip.h}")
    clip.close()
    thumbs = [f for f in os.listdir("output/thumbnails") if f.endswith(".jpg")]
    check(len(thumbs) >= i + 1, f"render {i + 1}: thumbnail written")
    shorts = os.listdir("output/shorts") if os.path.isdir("output/shorts") else []
    check(len(shorts) >= i + 1, f"render {i + 1}: short rendered")
    main_uploads = [b for b in r["new_inserts"] if not b["snippet"]["title"].endswith("#Shorts")]
    short_uploads = [b for b in r["new_inserts"] if b["snippet"]["title"].endswith("#Shorts")]
    check(len(main_uploads) == 1 and len(short_uploads) == 1, f"render {i + 1}: 1 main + 1 short uploaded")
    check(len(r["new_comments"]) == 1, f"render {i + 1}: exactly one comment")
    pl = PLANS[-1]
    plan, tl = pl["plan"], pl["timeline"]
    check(pl["repeats"] == 0, f"render {i + 1}: no footage repeated ({len(plan)} segments)")
    ends = [round(at + ln, 2) for _, _, at, ln in plan]
    check(plan[0][2] == 0 and all(abs(a - b[2]) < 0.05 for a, b in zip(ends, plan[1:])) and abs(ends[-1] - tl[-1]["end"]) < 0.05,
          f"render {i + 1}: segments cover the whole voice with no gaps")
    own = 0
    for path, _, at, ln in plan:
        k = max(j for j, item in enumerate(tl) if item["start"] <= at + 0.01)
        own += path in pl["scene_clips"].get(k, [])
    check(own == len(plan), f"render {i + 1}: every segment shows its own scene's footage ({own}/{len(plan)})")
    if short_uploads:
        sd = short_uploads[0]["snippet"]["description"]
        check(f"youtu.be/{r['video_id']}" in sd, f"render {i + 1}: the short links to the full video")
    frames = [f for f in os.listdir("output/thumbnails") if f.endswith("_frame.jpg")]
    check(len(frames) >= i + 1, f"render {i + 1}: thumbnail background is a frame from the video")

print(f"\n=== 2. Soak: {args.soak} more videos in a row (render stubbed)")
VOICE["seconds"] = args.soak_voice_seconds
for i in range(args.soak):
    run_one(f"soak {i + 1}", render=False)

ok = [r for r in RESULTS if r["success"]]
check(ok and len(ok) == len(RESULTS), f"all {len(RESULTS)} videos succeeded")
datas = [r["data"] for r in ok]

titles = [d["title"] for d in datas]
check(len(set(titles)) == len(titles), "no repeated title")
worst = max((U.text_similarity(a, b) for a, b in itertools.combinations(titles, 2)), default=0)
check(worst < U.TITLE_SIMILARITY_LIMIT, f"no two titles are near-duplicates (max similarity {worst:.2f})")
angles = [f"{d['topic']}|{d['format']['key']}" for d in datas]
check(len(set(angles)) == len(angles), "no repeated topic+format combination")
fmts = [d["format"]["key"] for d in datas]
check(all(a != b for a, b in zip(fmts, fmts[1:])), "back-to-back videos never share a format")
check(len(set(fmts)) >= min(len(U.FORMATS), len(datas)) * 0.8, f"{len(set(fmts))} different formats used")
for field in ["curiosity_question", "thumbnail_text", "comment"]:
    vals = [d.get(field) for d in datas]
    check(all(vals) and len(set(vals)) == len(vals), f"every video has its own {field}")
openings = [U.first_sentence(d["script"]) for d in datas]
check(len(set(openings)) == len(openings), "no repeated opening line")
check(all(not re.match(r"(?i)(hey|what is up|welcome back)", o) for o in openings), "scripts open with the hook, not a greeting")
overlays = ["|".join(s["text_overlay"] for s in d["scenes"]) for d in datas]
check(len(set(overlays)) == len(overlays), "no repeated on-screen text sequence")
fps = [U.fingerprint(d["script"]) for d in datas]
worst = max((U.fingerprint_similarity(a, b) for a, b in itertools.combinations(fps, 2)), default=0)
check(worst < U.SCRIPT_SIMILARITY_LIMIT, f"no two scripts overlap (max {worst:.0%})")

all_clips = [c for r in ok for c in r["clips"]]
check(len(all_clips) == len(set(all_clips)), f"no stock clip reused across videos ({len(all_clips)} clips)")
check(all(len(r["clips"]) >= 6 for r in ok), "every video got at least 6 fresh clips")

for d in datas:
    blob = json.dumps({k: d.get(k) for k in ("title", "script", "scenes", "description", "comment", "thumbnail_text")})
    if BAD.search(blob):
        check(False, f"honesty/label check failed in {d['title']!r}: {BAD.search(blob).group(0)}")
        break
else:
    check(True, "no fake-earnings claims and no placeholder labels in any video")
check(all("i.mec.me/?c=pt6wsw2v" in d["description"] and "ffiliate" in d["description"] for d in datas),
      "every description has the link + affiliate disclosure")
check(all("i.mec.me/?c=pt6wsw2v" in d["comment"] for d in datas), "every comment has the link")
check(all(len(r["new_comments"]) == 1 for r in ok), "exactly one comment per main video")

print("\n=== 2a. Thumbnail faces and SEO")
reactions = mem_now = json.load(open(U.MEMORY_FILE)).get("reaction_photo", [])
n_thumbs = len(json.load(open(U.MEMORY_FILE)).get("thumb_layout", []))
check(len(reactions) == n_thumbs and len(set(reactions)) == len(reactions),
      f"every thumbnail has its own shocked face, never reused ({len(set(reactions))} faces / {n_thumbs} thumbnails)")
rq = json.load(open(U.MEMORY_FILE)).get("reaction_query", [])
check(all(a != b for a, b in zip(rq, rq[1:])), "reaction face search rotates (no two in a row alike)")
import advanced_thumbnail_gen as _TG
check(rq and all(q in _TG.STYLISH_REACTION_QUERIES for q in rq),
      f"thumbnail faces are modern, stylish people ({sum(q in _TG.STYLISH_REACTION_QUERIES for q in rq)}/{len(rq)})")
mains = [b for b in API["inserts"] if not b["snippet"]["title"].endswith("#Shorts")]
check(all(len(b["snippet"]["title"]) <= 70 for b in mains), f"all titles fit in search results (max {max(len(b['snippet']['title']) for b in mains)} chars)")
tag_chars = [sum(len(t) + (2 if " " in t else 0) for t in b["snippet"]["tags"]) + len(b["snippet"]["tags"]) - 1 for b in API["inserts"]]
check(max(tag_chars) <= 500, f"tags stay inside YouTube's 500-character limit (max {max(tag_chars)})")
check(all(len({t.lower() for t in b["snippet"]["tags"]}) == len(b["snippet"]["tags"]) for b in API["inserts"]), "no duplicate tags")
vids = [r["video_id"] for r in ok]
in_playlist = {v for _, v in API["playlist_items"]}
check(all(v in in_playlist for v in vids), "every video is added to its series playlist")
check(len(API["playlists"]) == len(set(API["playlists"])), f"each series playlist is created once ({len(API['playlists'])} playlists)")
descs = [b["snippet"]["description"] for b in mains]
watch_next = [d for d in descs[1:] if "▶️ WATCH NEXT" in d]
check(len(watch_next) == len(descs) - 1, f"every video after the first links to the previous one ({len(watch_next)}/{len(descs) - 1})")

print("\n=== 2b. Footage and labels follow the voice")
soak = [r for r in ok if r.get("timeline") and r["timeline"]["dur"] > 200]
worst_off, matched, total_scenes = 0.0, 0, 0
for r in soak:
    t = r["timeline"]
    words = [(tm, w.lower().strip(".,?!")) for tm, w in t["words"]]
    for item in t["timeline"]:
        says = scene_sync._tokens(item["scene"].get("says", ""))
        total_scenes += 1
        # where the voice really says this scene's words (ignoring the one changed word)
        hits = [tm for k, (tm, w) in enumerate(words) if [x for _, x in words[k:k + 6]][1:6] == says[1:6]]
        if item["start"] == 0 and hits and hits[0] < 1:
            matched += 1
            continue
        if hits:
            matched += 1
            worst_off = max(worst_off, min(abs(h - item["start"]) for h in hits))
check(total_scenes and matched == total_scenes, f"every scene was found in the voice ({matched}/{total_scenes})")
check(worst_off < 0.5, f"scene footage starts when the voice says it (worst {worst_off:.2f}s off)")
scene_counts = [len(r["timeline"]["timeline"]) for r in soak]
check(all(c >= 7 for c in scene_counts), f"scenes are kept, not merged away ({min(scene_counts, default=0)}-{max(scene_counts, default=0)} per video)")
stamps_ok = True
for d in datas:
    block = d["description"].split("⏱️ TIMESTAMPS\n")[1].split("\n\n")[0] if "⏱️ TIMESTAMPS" in d["description"] else ""
    secs = [int(m) * 60 + int(s_) for m, s_ in re.findall(r"^(\d+):(\d{2}) - ", block, re.M)]
    stamps_ok &= bool(secs) and secs[0] == 0 and len(secs) >= 3 and all(b - a >= 10 for a, b in zip(secs, secs[1:]))
check(stamps_ok, "description chapters use the real voice times (start 0:00, 3+, 10s apart)")
labels_t = [l[0] for r in soak[:1] for l in _scene_labels_from_plan(None, r["timeline"]["dur"], r["timeline"]["timeline"])]
check(labels_t and all(abs(a - (b["start"] + 0.3)) < 0.01 for a, b in zip(labels_t, soak[0]["timeline"]["timeline"])),
      "on-screen labels appear when the voice reaches their scene")

from brain.trend_engine import get_random_elements  # noqa: E402
fb = advanced_script_gen._fallback(get_random_elements("Testnet Farming Basics"), U.format_details(U.FORMATS[0]))
fb_tokens = scene_sync._tokens(fb["script"])
found = [scene_sync._find_phrase(fb_tokens, s["says"], 0) for s in fb["scenes"]]
check(all(f is not None for f in found) and found == sorted(found), "fallback script scenes are anchored to its narration")

check(PEXELS_PAGES and PEXELS_PAGES[0] == 1 and max(PEXELS_PAGES) <= 4, f"Pexels paging starts at page 1 and stops by page 4 (max {max(PEXELS_PAGES)})")
labels = [t for d in datas for _, _, t, _ in _scene_labels_from_plan(d["scenes"], 300)]
check(not any(t in {"LARGE KEYWORD HIGHLIGHT", "STEP LABEL", "RISK WARNING", "ACTION CHECKLIST"} for t in labels),
      "on-screen labels come from the script, not studio placeholders")

mem = json.load(open(U.MEMORY_FILE)) if os.path.exists(U.MEMORY_FILE) else {}
layouts = mem.get("thumb_layout", [])
check(all(a != b for a, b in zip(layouts, layouts[1:])), "thumbnail layout never repeats back-to-back")
check(len(set(layouts[:8])) == min(8, len(layouts)), "first 8 thumbnails use 8 different layouts")
badges = mem.get("thumb_badge", [])
check(len(set(badges[:12])) == min(12, len(badges)), "first 12 thumbnails use 12 different badges")
hooks = mem.get("section_hook", [])
check(len(hooks) == len(ok) and len(set(hooks[:8])) == min(8, len(hooks)), "section hook style rotates through all 8 before repeating")
intro_refs = mem.get("intro_style", [])
check(all(a != b for a, b in zip(intro_refs, intro_refs[1:])), "intro style reference never repeats back-to-back")

print("\n=== 3. Clip planner: no footage repeats inside a video")
paths = []
for i in range(3):
    p = os.path.join(MEDIA, f"plan{i}.mp4")
    shutil.copy(os.path.join(MEDIA, f"sample{i}.mp4"), p)
    paths.append(p)
windows, seg = plan_clip_windows(paths, 30, 6)
check(len(windows) == len(set(windows)), f"{len(windows)} segments, all different windows (seg {seg}s)")
check(all(a[0] != b[0] for a, b in zip(windows, windows[1:])), "same clip never plays twice in a row")
for p in set(w[0] for w in windows):
    starts = sorted(s for q, s in windows if q == p)
    check(all(b - a >= seg - 1e-6 for a, b in zip(starts, starts[1:])), f"windows of {os.path.basename(p)} do not overlap")

# Production-sized case: a 5-minute video gets 300/12 = 25 stock clips
advanced_video_gen._clip_duration = lambda p: 15.0  # pessimistic: real Pexels clips are often longer
windows, seg = plan_clip_windows([f"clip{i}.mp4" for i in range(25)], 300, 6)
check(len(windows) == len(set(windows)) and len(windows) * (seg - 0.5) >= 301,
      f"5-min video from 25 clips: {len(windows)} segments of {seg}s, none repeated")

# Production-sized scene plan: 10 scenes over 5 minutes, ~3 clips of 15s per scene
tl = [{"start": 30.0 * k, "end": 30.0 * (k + 1), "scene": {}} for k in range(10)]
sc = {k: [f"s{k}c{j}.mp4" for j in range(3)] for k in range(10)}
durs = {c: 15.0 for cs in sc.values() for c in cs}
plan, repeats = _orig_plan(tl, sc, durs)
check(repeats == 0, f"5-min scene plan: {len(plan)} segments, no footage repeated")
check(all(p in sc[int(at // 30)] for p, _, at, _ in plan), "5-min scene plan: each scene uses only its own clips")
spans = {}
for p, st, _, ln in plan:
    spans.setdefault(p, []).append((st, st + ln))
check(all(b[0] >= a[1] - 1e-6 for v in spans.values() for a, b in zip(sorted(v), sorted(v)[1:])), "5-min scene plan: no two pieces of one clip overlap")
check(all(a[0] != b[0] for a, b in zip(plan, plan[1:])), "5-min scene plan: same clip never plays twice in a row")
sc_short = dict(sc)
sc_short[4] = []  # a scene whose search found nothing borrows unused footage instead of repeating
plan, repeats = _orig_plan(tl, sc_short, durs)
check(repeats == 0, "a scene with no clips borrows unused footage, nothing repeats")

print("\n=== 3b. Thumbnail text always fits, nothing is cut")
from PIL import ImageDraw  # noqa: E402
draw = ImageDraw.Draw(Image.new("RGB", (1280, 720)))
texts = [d["thumbnail_text"] for d in datas] + ["WHY 90% OF AIRDROP WALLETS GET DISQUALIFIED BEFORE SNAPSHOT", "GAS"]
cut = [t for t in texts if " ".join(_fit_title(draw, t, 676, 370)[2]).split() != t.split()]
check(not cut, f"all {len(texts)} thumbnail texts fit in 3 lines without dropping words {cut[:1]}")
sizes = [_fit_title(draw, d["thumbnail_text"], 676, 370)[1] for d in datas]
check(min(sizes) >= 70, f"short thumbnail texts are big (smallest font {min(sizes)}px)")

print("\n=== 4. Duplicate protection")
LLM["mode"] = "copycat"
before = len(API["inserts"])
r = run_one("copycat")
check(not r["success"] and "Uniqueness gate" in (r["error"] or ""), "a script that copies an old video is blocked")
check(len(API["inserts"]) == before, "nothing was uploaded for the duplicate")

LLM["mode"] = "fail"
r1 = run_one("groq down #1")
check(r1["success"], "with the AI down, the honest fallback script is used once")
r2 = run_one("groq down #2")
check(not r2["success"] and "Uniqueness gate" in (r2["error"] or ""), "the same fallback is not uploaded a second time")

print("\n=== 4b. Pexels runs out of never-used footage")
LLM["mode"] = "ok"
PEXELS_CATALOG = 40  # every search now returns clips that earlier videos already used
r = run_one("starved", render=False)
check(r["success"], "the video is still made when no fresh footage is left")
check(len(r["clips"]) >= 6 and len(r["clips"]) == len(set(r["clips"])),
      f"it reuses the oldest clips instead of showing none ({len(r['clips'])} clips, none twice in the video)")

print(f"\n{len(FAILS)} failure(s)")
if not args.keep:
    os.chdir(REPO)
    shutil.rmtree(WORK, ignore_errors=True)
sys.exit(1 if FAILS else 0)
