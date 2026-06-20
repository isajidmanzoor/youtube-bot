import os
from gtts import gTTS
from config import AUDIO_DIR

def generate_voiceover(script: str, filename: str, voice: str = None) -> str | None:
    os.makedirs(AUDIO_DIR, exist_ok=True)
    output_path = os.path.join(AUDIO_DIR, f"{filename}.mp3")
    try:
        clean_script = script.replace("*", "").replace("#", "").replace("_", "")
        clean_script = " ".join(clean_script.split())
        tts = gTTS(text=clean_script, lang="en", slow=False)
        tts.save(output_path)
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            print(f"✅ Voiceover saved: {output_path}")
            return output_path
        return None
    except Exception as e:
        print(f"❌ Voice gen error: {e}")
        return None

def get_audio_duration(audio_path: str) -> float:
    try:
        from moviepy.editor import AudioFileClip
        clip = AudioFileClip(audio_path)
        duration = clip.duration
        clip.close()
        return duration
    except Exception as e:
        print(f"❌ Duration error: {e}")
        return 60.0
