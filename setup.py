#!/usr/bin/env python3
# ============================================================
#   SETUP.PY — Pehli baar chalao, sab check karega
#   Usage: python setup.py
# ============================================================

import sys
import os
import importlib


def check(label, fn):
    try:
        fn()
        print(f"  ✅ {label}")
        return True
    except Exception as e:
        print(f"  ❌ {label}: {e}")
        return False


def main():
    print("\n" + "=" * 50)
    print("  YouTube Bot — Setup Checker")
    print("=" * 50)

    errors = 0

    # ── Python version ─────────────────────────────────────────
    ok = check(
        f"Python {sys.version_info.major}.{sys.version_info.minor}",
        lambda: (_ for _ in ()).throw(Exception("Python 3.10+ required"))
        if sys.version_info < (3, 10)
        else None,
    )
    if not ok:
        errors += 1

    # ── Required packages ──────────────────────────────────────
    print("\n📦 Packages:")
    packages = [
        ("requests", "requests"),
        ("edge_tts", "edge-tts"),
        ("moviepy", "moviepy"),
        ("PIL", "Pillow"),
        ("googleapiclient", "google-api-python-client"),
        ("google_auth_oauthlib", "google-auth-oauthlib"),
        ("apscheduler", "APScheduler"),
    ]
    for mod, pkg in packages:
        ok = check(pkg, lambda m=mod: importlib.import_module(m))
        if not ok:
            errors += 1

    # ── ffmpeg ────────────────────────────────────────────────
    print("\n🎬 System tools:")
    import shutil
    ok = check("ffmpeg", lambda: (_ for _ in ()).throw(Exception("ffmpeg not found")) if not shutil.which("ffmpeg") else None)
    if not ok:
        errors += 1
        print("     👉 Install: sudo apt install ffmpeg  OR  brew install ffmpeg")

    # ── Config keys ───────────────────────────────────────────
    print("\n🔑 Config keys (config.py):")
    from config import GROQ_API_KEY, PEXELS_API_KEY, YOUTUBE_CLIENT_SECRET

    ok = check(
        "GROQ_API_KEY",
        lambda: (_ for _ in ()).throw(Exception("Still placeholder")) if "YOUR" in GROQ_API_KEY else None,
    )
    if not ok:
        errors += 1
        print("     👉 Get free key: https://console.groq.com")

    ok = check(
        "PEXELS_API_KEY",
        lambda: (_ for _ in ()).throw(Exception("Still placeholder")) if "YOUR" in PEXELS_API_KEY else None,
    )
    if not ok:
        errors += 1
        print("     👉 Get free key: https://www.pexels.com/api")

    ok = check(
        "client_secret.json",
        lambda: (_ for _ in ()).throw(Exception("File not found")) if not os.path.exists(YOUTUBE_CLIENT_SECRET) else None,
    )
    if not ok:
        errors += 1
        print("     👉 Google Cloud Console → APIs → YouTube Data API v3 → Credentials → OAuth 2.0 Client")

    # ── Folder structure ──────────────────────────────────────
    print("\n📁 Folders:")
    folders = ["output/videos", "output/audio", "output/thumbnails", "logs", "topics"]
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        check(folder, lambda f=folder: None if os.path.isdir(f) else (_ for _ in ()).throw(Exception()))

    # ── Summary ───────────────────────────────────────────────
    print("\n" + "=" * 50)
    if errors == 0:
        print("  🎉 All checks passed! Run: python main.py")
    else:
        print(f"  ⚠️  {errors} issue(s) found. Fix them above, then re-run.")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    main()
