import os, random
from moviepy.editor import VideoFileClip, AudioFileClip, ColorClip, CompositeVideoClip, TextClip, concatenate_videoclips

SHORTS_W, SHORTS_H = 1080, 1920
AFFILIATE_LINK = "https://i.mec.me/?c=pt6wsw2v"

def _try_text(text, size, color, duration, pos):
    try:
        return (TextClip(text, fontsize=size, color=color, font="DejaVu-Sans-Bold", stroke_color="black", stroke_width=3)
                .set_position(pos).set_duration(duration))
    except: return None

def create_short(clip_paths, audio_path, title, filename, output_dir="output/shorts"):
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{filename}_short.mp4")
    SHORT_DUR = 58
    try:
        if not clip_paths:
            bg = ColorClip(size=(SHORTS_W,SHORTS_H), color=(10,5,20), duration=SHORT_DUR)
        else:
            segs = []
            random.shuffle(clip_paths)
            for i in range(SHORT_DUR//5+1):
                src = clip_paths[i % len(clip_paths)]
                try:
                    vc = VideoFileClip(src, audio=False)
                    tw = vc.h * 9 // 16
                    if tw <= vc.w:
                        xc = (vc.w - tw)//2
                        vc = vc.crop(x1=xc, y1=0, x2=xc+tw, y2=vc.h)
                    vc = vc.resize((SHORTS_W,SHORTS_H))
                    if vc.duration > 6:
                        s = random.uniform(0, vc.duration-5.5)
                        vc = vc.subclip(s, s+5)
                    else:
                        vc = vc.loop(duration=5)
                    segs.append(vc)
                except: segs.append(ColorClip(size=(SHORTS_W,SHORTS_H),color=(10,5,20),duration=5))
            bg = concatenate_videoclips(segs, method="compose").subclip(0, SHORT_DUR)
        audio = AudioFileClip(audio_path)
        audio_dur = min(audio.duration, SHORT_DUR)
        audio = audio.subclip(0, audio_dur)
        layers = [bg]
        for txt, color, ypos in [
            ("🔥 FREE CRYPTO AIRDROP", "yellow", 80),
            (title[:55]+"..." if len(title)>55 else title, "white", SHORTS_H//2-100),
            (random.choice(["💰 Link in Description!","👇 Join FREE Below!","🚀 Start Earning Now!"]), "lime", SHORTS_H//2+150),
            ("✅ NO INVESTMENT NEEDED", "white", SHORTS_H-200),
        ]:
            c = _try_text(txt, 50, color, audio_dur, ("center", ypos))
            if c: layers.append(c)
        final = CompositeVideoClip(layers).set_audio(audio).set_duration(audio_dur)
        final.write_videofile(output_path, fps=30, codec="libx264", audio_codec="aac", preset="fast", threads=4, logger=None)
        audio.close(); final.close()
        if os.path.exists(output_path) and os.path.getsize(output_path) > 5000:
            print(f"✅ Short: {output_path}")
            return output_path
    except Exception as e:
        print(f"❌ Short failed: {e}")
    return None

def upload_short(video_path, title, description, tags):
    try:
        from youtube_uploader import upload_video
        short_id = upload_video(
            video_path=video_path,
            title=f"#Shorts {title[:85]}",
            description=f"#Shorts #CryptoAirdrop #FreeCrypto\n\n💰 Join FREE:\n👉 {AFFILIATE_LINK}",
            tags=tags + ["shorts","youtubeshorts","crypto shorts"],
            privacy="public",
        )
        if short_id: print(f"✅ Short uploaded: https://youtube.com/shorts/{short_id}")
        return short_id
    except Exception as e:
        print(f"⚠️  Short upload failed: {e}")
        return None
