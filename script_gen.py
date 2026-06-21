# ============================================================
#   SCRIPT_GEN.PY — Groq AI se video script generate karo
# ============================================================

import requests
import json
import random
import os
from config import GROQ_API_KEY, GROQ_MODEL, GROQ_MAX_TOKENS, TOPICS_FILE, CHANNEL_TOPIC


def get_random_topic():
    """Topics file se random topic lo."""
    try:
        with open(TOPICS_FILE, "r") as f:
            topics = [t.strip() for t in f.readlines() if t.strip()]
        if not topics:
            return f"Tips about {CHANNEL_TOPIC}"
        return random.choice(topics)
    except Exception:
        return f"Tips about {CHANNEL_TOPIC}"


def generate_script(topic=None):
    """
    Groq API se complete video script generate karo.
    Returns: dict with title, description, tags, script, search_query
    """
    if not topic:
        topic = get_random_topic()

    prompt = f"""You are a professional YouTube script writer.
Create a complete YouTube video script about: "{topic}"

Return ONLY valid JSON in this exact format:
{{
    "title": "Catchy YouTube title under 60 chars",
    "description": "YouTube description 150 words with keywords. End with: Start earning today: https://i.mec.me/?c=pt6wsw2v",
    "tags": ["crypto airdrop", "free crypto", "airdrop 2025", "earn crypto", "crypto wallet", "tag6", "tag7", "tag8"],
    "search_query": "crypto wallet money",
    "script": "Full voiceover script 200-250 words. Natural human speaking style. Talk like a real person sharing their crypto earnings experience. Mention real wallet platforms like MetaMask, Trust Wallet, Phantom. No special characters.",
    "comment": "Join free airdrop and earn real crypto daily! Link in description: https://i.mec.me/?c=pt6wsw2v"
}}

Rules:
- Title must be engaging with numbers or power words
- Description must end with the earning link
- Script must sound like a real human sharing experience
- Mention real crypto platforms and wallets naturally
- Tags must include crypto airdrop related keywords"""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": GROQ_MAX_TOKENS,
        "temperature": 0.7,
    }

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"].strip()

        # Clean JSON if wrapped in markdown
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        data = json.loads(content)

        required = ["title", "description", "tags", "search_query", "script"]
        for field in required:
            if field not in data:
                raise ValueError(f"Missing field: {field}")

        data["topic"] = topic
        print(f"✅ Script generated: {data['title']}")
        return data

    except requests.exceptions.RequestException as e:
        print(f"❌ Groq API error: {e}")
        return _fallback_script(topic)
    except json.JSONDecodeError as e:
        print(f"❌ JSON parse error: {e}")
        return _fallback_script(topic)
    except Exception as e:
        print(f"❌ Script gen error: {e}")
        return _fallback_script(topic)


def _fallback_script(topic):
    """Agar API fail ho toh fallback use karo."""
    return {
        "title": f"Complete Guide to {topic}",
        "description": (
            f"In this video we cover everything about {topic}. "
            "Perfect for beginners and professionals."
        ),
        "tags": ["software testing", "QA", "tech tips", "tutorial", "guide", topic.lower()],
        "search_query": "technology tutorial",
        "script": (
            f"Welcome to our channel! Today we are going to talk about {topic}. "
            "This is one of the most important topics in software development and testing. "
            f"Whether you are a beginner or an experienced professional, this video will help you understand {topic} better. "
            f"Let us start with the basics. {topic} is a crucial concept that every developer and tester should know. "
            "In today's fast-paced world of software development, understanding this topic can make a huge difference in your career. "
            "We will cover the key concepts, best practices, and real-world examples. "
            f"By the end of this video, you will have a solid understanding of {topic}. "
            "Do not forget to like this video and subscribe to our channel for more amazing content. "
            "Stay tuned for more tips and tutorials. Thank you for watching!"
        ),
        "topic": topic,
    }
