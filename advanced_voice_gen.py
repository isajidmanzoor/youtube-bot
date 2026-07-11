# ============================================================
#   ADVANCED_VOICE_GEN.PY — Natural voice with pauses
# ============================================================

import os
import random
from gtts import gTTS
from config import AUDIO_DIR

# Speed variations for natural feel
SPEEDS = [False, False, False, True]  # 75% normal, 25% slow


def _add_natural_pauses(script: str) -> str:
    """Add natural pauses to make speech sound more human."""
    # Add pause after sentences
    script = script.replace(". ", "... ")
    script = script.replace("! ", "!... ")
    script = script.replace("? ", "?... ")

    # Add pause after section keywords
    keywords = [
        "Step one", "Step two", "Step three", "Step four",
        "First", "Second", "Third", "Finally",
        "Now", "Remember", "Important", "Warning",
        "Pro tip", "The key is", "Here is the secret",
    ]
    for kw in keywords:
        script = script.replace(kw, f"... {kw}")

    return script


MALE_VOICES = ["Daniel", "Fred"]
FEMALE_VOICES = ["Samantha", "Karen"]

def generate_advanced_voiceover(script: str, filename: str, voice_profile: dict = None, gender: str = None) -> str | None:
    """
    Generate voiceover with natural variations using macOS 'say' for gender control.
    Returns: output file path or None
    """
    import subprocess, shutil
    os.makedirs(AUDIO_DIR, exist_ok=True)
    output_path = os.path.join(AUDIO_DIR, f"{filename}.mp3")

    if gender:
        clean_for_say = script.replace("*", "").replace("#", "").replace("_", "")
        clean_for_say = clean_for_say.replace("👉", "").replace("✅", "").replace("🔥", "")
        clean_for_say = clean_for_say.replace("💰", "").replace("🚀", "").replace("⚡", "")
        clean_for_say = " ".join(clean_for_say.split())
        voice_name = random.choice(MALE_VOICES if gender == "male" else FEMALE_VOICES)
        aiff_path = output_path.replace(".mp3", ".aiff")
        try:
            subprocess.run(["say", "-v", voice_name, "-o", aiff_path, clean_for_say], check=True, timeout=600)
            subprocess.run(["ffmpeg", "-y", "-i", aiff_path, output_path], check=True, capture_output=True)
            os.remove(aiff_path)
            if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
                size_kb = os.path.getsize(output_path) / 1024
                print(f"✅ Voice: {output_path} ({size_kb:.0f}KB, gender={gender}, voice={voice_name})")
                return output_path
        except Exception as e:
            print(f"⚠️ macOS say failed, falling back to gTTS: {e}")

    # Clean script
    clean = script.replace("*", "").replace("#", "").replace("_", "")
    clean = clean.replace("👉", "").replace("✅", "").replace("🔥", "")
    clean = clean.replace("💰", "").replace("🚀", "").replace("⚡", "")
    clean = " ".join(clean.split())

    # Add natural pauses
    clean = _add_natural_pauses(clean)

    accents = [
        ("en", "com"),
        ("en", "co.uk"),
        ("en", "com.au"),
        ("en", "co.in"),
    ]
    if voice_profile:
        lang = "en"
        tld = voice_profile.get("tld", "com")
        slow = bool(voice_profile.get("slow", False))
    else:
        lang, tld = random.choice(accents)
        slow = random.choice(SPEEDS)

    try:
        tts = gTTS(text=clean, lang=lang, tld=tld, slow=slow)
        tts.save(output_path)

        if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
            size_kb = os.path.getsize(output_path) / 1024
            style = voice_profile.get("style", "auto") if voice_profile else "auto"
            print(f"✅ Voice: {output_path} ({size_kb:.0f}KB, style={style}, accent={tld})")
            return output_path
        return None

    except Exception as e:
        print(f"⚠️  Accent {tld} failed, trying default: {e}")
        try:
            tts = gTTS(text=clean, lang="en", slow=False)
            tts.save(output_path)
            if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
                print(f"✅ Voice (fallback): {output_path}")
                return output_path
        except Exception as e2:
            print(f"❌ Voice gen failed: {e2}")
        return None


def get_audio_duration(audio_path: str) -> float:
    """Get audio duration in seconds."""
    try:
        from moviepy.editor import AudioFileClip
        clip = AudioFileClip(audio_path)
        duration = clip.duration
        clip.close()
        return duration
    except Exception:
        return 60.0
