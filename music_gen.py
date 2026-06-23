# ============================================================
#   MUSIC_GEN.PY — Real royalty-free background music
#   Downloads actual music from Free Music Archive
# ============================================================

import os
import random
import requests

MUSIC_DIR = "output/music"

# Real royalty-free music URLs (CC0 license - no copyright)
MUSIC_TRACKS = {
    "energetic": [
        "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
        "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3",
        "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-6.mp3",
    ],
    "exciting": [
        "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3",
        "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-8.mp3",
        "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-11.mp3",
    ],
    "motivational": [
        "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-4.mp3",
        "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-7.mp3",
        "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-13.mp3",
    ],
    "trustworthy": [
        "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-5.mp3",
        "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-9.mp3",
        "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-14.mp3",
    ],
    "mysterious": [
        "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-10.mp3",
        "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-12.mp3",
        "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-16.mp3",
    ],
}


def generate_background_music(duration: float, mood: str = None, filename: str = "bg_music") -> str | None:
    """Download real royalty-free music for background."""
    if not mood:
        mood = random.choice(list(MUSIC_TRACKS.keys()))

    os.makedirs(MUSIC_DIR, exist_ok=True)
    output_path = os.path.join(MUSIC_DIR, f"{filename}.mp3")

    urls = MUSIC_TRACKS.get(mood, MUSIC_TRACKS["energetic"])
    url = random.choice(urls)

    try:
        print(f"🎵 Downloading music: mood={mood}")
        response = requests.get(url, timeout=30, stream=True)
        response.raise_for_status()

        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        if os.path.exists(output_path) and os.path.getsize(output_path) > 10000:
            print(f"✅ Music downloaded: {output_path} ({os.path.getsize(output_path)//1024}KB)")
            return output_path
        else:
            print("⚠️  Music download too small")
            return None

    except Exception as e:
        print(f"⚠️  Music download failed: {e}")
        return None


def mix_audio_with_music(voice_path: str, music_path: str, output_path: str, music_volume: float = 0.07) -> str | None:
    """Mix voiceover with background music at low volume."""
    try:
        from moviepy.editor import AudioFileClip, CompositeAudioClip

        voice = AudioFileClip(voice_path)
        music = AudioFileClip(music_path)

        # Loop or trim music to match voice duration
        if music.duration < voice.duration:
            loops = int(voice.duration / music.duration) + 1
            from moviepy.editor import concatenate_audioclips
            music = concatenate_audioclips([music] * loops).subclip(0, voice.duration)
        else:
            music = music.subclip(0, voice.duration)

        music = music.volumex(music_volume)
        mixed = CompositeAudioClip([voice, music])
        mixed.write_audiofile(output_path, fps=44100, logger=None)

        voice.close()
        music.close()

        print(f"✅ Audio mixed with music: {output_path}")
        return output_path

    except Exception as e:
        print(f"⚠️  Mix failed (using voice only): {e}")
        return voice_path
