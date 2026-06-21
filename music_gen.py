import os, random, struct, wave, math

MUSIC_DIR = "output/music"
MOODS = {
    "energetic": {"freq": 528, "bpm": 128},
    "trustworthy": {"freq": 396, "bpm": 80},
    "exciting": {"freq": 639, "bpm": 110},
    "mysterious": {"freq": 285, "bpm": 70},
    "motivational": {"freq": 417, "bpm": 100},
}

def generate_background_music(duration, mood=None, filename="bg_music"):
    if not mood: mood = random.choice(list(MOODS.keys()))
    mood_data = MOODS.get(mood, MOODS["energetic"])
    os.makedirs(MUSIC_DIR, exist_ok=True)
    path = os.path.join(MUSIC_DIR, f"{filename}.wav")
    sample_rate = 44100
    num_samples = int(sample_rate * (duration + 2))
    bpm = mood_data["bpm"]
    beat_interval = int(sample_rate * 60 / bpm)
    with wave.open(path, "w") as wav:
        wav.setnchannels(1); wav.setsampwidth(2); wav.setframerate(sample_rate)
        frames = []
        for i in range(num_samples):
            t = i / sample_rate
            val = math.sin(2 * math.pi * 80 * t) * 0.3
            beat_pos = i % beat_interval
            if beat_pos < int(sample_rate * 0.1):
                decay = 1 - (beat_pos / (sample_rate * 0.1))
                val += math.sin(2 * math.pi * 200 * t) * decay * 0.4
            val += math.sin(2 * math.pi * mood_data["freq"] * t) * 0.05 * math.sin(2 * math.pi * 0.3 * t)
            fade = int(sample_rate * 2)
            if i < fade: val *= i / fade
            elif i > num_samples - fade: val *= (num_samples - i) / fade
            frames.append(struct.pack("<h", int(max(-32767, min(32767, val * 0.06 * 32767)))))
        wav.writeframes(b"".join(frames))
    print(f"✅ Music: {path} | mood={mood}")
    return path

def mix_audio_with_music(voice_path, music_path, output_path, music_volume=0.07):
    try:
        from moviepy.editor import AudioFileClip, CompositeAudioClip
        voice = AudioFileClip(voice_path)
        music = AudioFileClip(music_path)
        if music.duration < voice.duration:
            music = music.audio_loop(duration=voice.duration)
        else:
            music = music.subclip(0, voice.duration)
        music = music.volumex(music_volume)
        mixed = CompositeAudioClip([voice, music])
        mixed.write_audiofile(output_path, fps=44100, logger=None)
        voice.close(); music.close()
        print(f"✅ Mixed audio: {output_path}")
        return output_path
    except Exception as e:
        print(f"⚠️  Mix failed: {e}")
        return voice_path
