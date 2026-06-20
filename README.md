# 🤖 YouTube Auto Bot — Complete Setup Guide

Fully automated YouTube channel bot.
**6 videos/day | 100% FREE | Zero manual work**

---

## 📁 Folder Structure

```
youtube_bot/
├── config.py            ← ⭐ APNI SETTINGS YAHAN DAALO
├── main.py              ← Ek video banao
├── scheduler.py         ← 24/7 auto scheduler
├── setup.py             ← Pehli baar chalao (checker)
├── script_gen.py        ← Groq AI script writer
├── voice_gen.py         ← Edge TTS voiceover
├── video_fetcher.py     ← Pexels stock clips
├── video_gen.py         ← MoviePy video editor
├── thumbnail_gen.py     ← Auto thumbnail
├── youtube_uploader.py  ← YouTube API uploader
├── logger.py            ← Logs system
├── requirements.txt     ← Python packages
├── topics/
│   └── topics.txt       ← Video topics (ek per line)
├── output/
│   ├── videos/          ← Final MP4s
│   ├── audio/           ← Voiceover MP3s
│   └── thumbnails/      ← Thumbnail JPGs
└── logs/                ← Daily logs + videos.json
```

---

## ⚡ Quick Setup (Step by Step)

### Step 1 — Python & ffmpeg install karo
```bash
# Ubuntu/Mac
sudo apt install ffmpeg python3-pip   # Ubuntu
brew install ffmpeg                    # Mac

python3 --version   # 3.10+ chahiye
```

### Step 2 — Packages install karo
```bash
cd youtube_bot
pip install -r requirements.txt
```

### Step 3 — FREE API Keys lo

| API | Link | Daily Limit |
|-----|------|------------|
| Groq AI | https://console.groq.com | 14,400 req/day FREE |
| Pexels | https://www.pexels.com/api | 200/hour FREE |

### Step 4 — YouTube OAuth setup karo
1. https://console.cloud.google.com pe jao
2. New Project banao
3. APIs & Services → Enable → **YouTube Data API v3**
4. Credentials → Create → **OAuth 2.0 Client ID** → Desktop App
5. Download JSON → rename to `client_secret.json` → is folder mein rakh do

### Step 5 — config.py edit karo
```python
GROQ_API_KEY   = "gsk_xxxxxxxxxxxx"     # Apni Groq key
PEXELS_API_KEY = "xxxxxxxxxxxxxxxxx"     # Apni Pexels key
CHANNEL_TOPIC  = "Your Channel Topic"   # Apna topic
```

### Step 6 — Setup check karo
```bash
python setup.py
```
Sab ✅ dikhne chahiye.

### Step 7 — Test karo (ek video)
```bash
python main.py
```
Pehli baar browser khulega YouTube login ke liye — allow karo.

### Step 8 — 24/7 scheduler chalao
```bash
python scheduler.py
```

---

## 🕐 Upload Schedule (Pakistan Time)

| Video | Time |
|-------|------|
| Video 1 | 8:00 AM |
| Video 2 | 11:00 AM |
| Video 3 | 2:00 PM |
| Video 4 | 5:00 PM |
| Video 5 | 7:00 PM |
| Video 6 | 9:00 PM |

---

## 📊 API Limits (Safe Zone)

| Service | Daily Limit | We Use |
|---------|------------|--------|
| YouTube API | 10,000 units | 9,600 (6×1600) |
| Groq AI | 14,400 req | ~6 req |
| Pexels | 4,800 videos | ~30 clips |
| Edge TTS | Unlimited | 6 calls |

---

## 🛠️ Commands

```bash
# Ek video banao (random topic)
python main.py

# Custom topic pe video
python main.py "How to Write Test Cases"

# 24/7 scheduler start karo
python scheduler.py

# Setup check
python setup.py
```

---

## ⚠️ Common Errors & Fixes

| Error | Fix |
|-------|-----|
| `client_secret.json not found` | Google Cloud se download karo |
| `Groq API error 401` | GROQ_API_KEY galat hai |
| `ffmpeg not found` | `sudo apt install ffmpeg` |
| `Quota exceeded` | YouTube daily limit (kal try karo) |
| `edge_tts not found` | `pip install edge-tts` |

---

## 📝 Custom Topics Add Karo

`topics/topics.txt` mein naye topics add karo (ek per line):
```
My New Topic 1
My New Topic 2
```

---

*100% FREE. No cost. No ads. Channel grows on autopilot.*
