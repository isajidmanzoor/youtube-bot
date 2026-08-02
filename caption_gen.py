import os
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip

def get_font(size):
    paths = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Arial.ttf",
    ]
    for p in paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except:
                continue
    return ImageFont.load_default()

def transcribe_audio(audio_path):
    from faster_whisper import WhisperModel
    model = WhisperModel("base", device="cpu", compute_type="int8")
    segments, _ = model.transcribe(audio_path, word_timestamps=True)
    words = []
    for segment in segments:
        for word in segment.words:
            words.append({"word": word.word.strip(), "start": word.start, "end": word.end})
    return words

def make_caption_clip(word, video_w, video_h, duration):
    font_size = int(video_h * 0.072)
    font = get_font(font_size)
    dummy = Image.new("RGBA", (1, 1))
    d = ImageDraw.Draw(dummy)
    bbox = d.textbbox((0, 0), word, font=font)
    tw = bbox[2] - bbox[0] + 40
    th = bbox[3] - bbox[1] + 20
    img = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.text((6, 6), word, font=font, fill=(0, 0, 0, 200))
    draw.rounded_rectangle([0, 0, tw, th], radius=10, fill=(255, 220, 0, 230))
    draw.text((20, 10), word, font=font, fill=(0, 0, 0, 255))
    clip = ImageClip(img).set_duration(duration)
    clip = clip.set_position(("center", int(video_h * 0.78)))
    return clip

def add_captions_to_video(video_path, audio_path, output_path):
    print("Transcribing audio for captions...")
    words = transcribe_audio(audio_path)
    video = VideoFileClip(video_path)
    vw, vh = video.size
    caption_clips = []
    for w in words:
        duration = w["end"] - w["start"]
        if duration <= 0:
            continue
        cap = make_caption_clip(w["word"], vw, vh, duration)
        cap = cap.set_start(w["start"])
        caption_clips.append(cap)
    final = CompositeVideoClip([video] + caption_clips)
    final.write_videofile(output_path, fps=video.fps, codec="libx264", audio_codec="aac", logger=None)
    video.close()
    final.close()
    print("Captions added: " + output_path)
    return output_path
