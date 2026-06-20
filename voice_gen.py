# ============================================================
#   VOICE_GEN.PY — Edge TTS se FREE voiceover banao
# ============================================================

import asyncio
import os
import edge_tts
from config import ACTIVE_VOICE, AUDIO_DIR


async def _generate_audio(script: str, output_path: str, voice: str):
    """Async Edge TTS call."""
    communicate = edge_tts.Communicate(script, voice)
    await communicate.save(output_path)


def generate_voiceover(script: str, filename: str, voice: str = None) -> str | None:
    """
    Script ko MP3 voiceover mein convert karo.
    Returns: output file path or None on error
    """
    if not voice:
        voice = ACTIVE_VOICE

    os.makedirs(AUDIO_DIR, exist_ok=True)
    output_path = os.path.join(AUDIO_DIR, f"{filename}.mp3")

    try:
        clean_script = script.replace("*", "").replace("#", "").replace("_", "")
        clean_script = " ".join(clean_script.split())

        # Fix for nested event loop (e.g. Jupyter / some schedulers)
        try:
            loop = asyncio.get_running_loop()
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(asyncio.run, _generate_audio(clean_script, output_path, voice))
                future.result()
        except RuntimeError:
            asyncio.run(_generate_audio(clean_script, output_path, voice))

        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            print(f"✅ Voiceover saved: {output_path}")
            return output_path
        else:
            print("❌ Voiceover file empty or missing")
            return None

    except Exception as e:
        print(f"❌ Voice gen error: {e}")
        return None


def get_audio_duration(audio_path: str) -> float:
    """Audio duration seconds mein lo."""
    try:
        from moviepy.editor import AudioFileClip
        clip = AudioFileClip(audio_path)
        duration = clip.duration
        clip.close()
        return duration
    except Exception as e:
        print(f"❌ Duration error: {e}")
        return 60.0
