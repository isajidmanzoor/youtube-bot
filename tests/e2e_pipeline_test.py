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
ap.add_argument("--voice-seconds", type=float, default=24.0)
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
        data = {
            "title": title,
            "curiosity_question": f"Which {_phrase(3)} matters most?",
            "payoff": _sentence(),
            "thumbnail_text": _phrase(3).upper(),
            "script": " ".join(body),
            "scenes": [{"time": f"{i}:{rng.randint(0, 5)}0", "scene": _phrase(2).title(),
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


PEXELS_CATALOG = 600  # small on purpose: forces the "look at more pages" path


def fake_get(url, timeout=None, params=None, headers=None, stream=False, **kw):
    if "coindesk" in url:
        return Resp(200, text="<title><![CDATA[Ethereum fees fall after upgrade]]></title>")
    if "api.pexels.com/videos/search" in url:
        per, page = params["per_page"], params["page"]
        # like the real API, each search text has its own result list
        start = (zlib.crc32(params["query"].encode()) + (page - 1) * per) % PEXELS_CATALOG
        ids = [(start + k) % PEXELS_CATALOG + 1 for k in range(per)]
        return Resp(200, {"videos": [{"id": i, "video_files": [
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
    def __init__(self, text, voice, rate=None, pitch=None):
        self.text = text

    async def save(self, path):
        make_voice(path, VOICE["seconds"])


sys.modules["edge_tts"] = types.SimpleNamespace(Communicate=Communicate)
sys.modules["gtts"] = types.SimpleNamespace(gTTS=None)

# YouTube API
API = {"inserts": [], "comments": []}


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
    r = advanced_main.make_complete_video()
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
    main_uploads = [b for b in r["new_inserts"] if not b["snippet"]["title"].startswith("#Shorts")]
    short_uploads = [b for b in r["new_inserts"] if b["snippet"]["title"].startswith("#Shorts")]
    check(len(main_uploads) == 1 and len(short_uploads) == 1, f"render {i + 1}: 1 main + 1 short uploaded")
    check(len(r["new_comments"]) == 1, f"render {i + 1}: exactly one comment")

print(f"\n=== 2. Soak: {args.soak} more videos in a row (render stubbed)")
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

print(f"\n{len(FAILS)} failure(s)")
if not args.keep:
    os.chdir(REPO)
    shutil.rmtree(WORK, ignore_errors=True)
sys.exit(1 if FAILS else 0)
