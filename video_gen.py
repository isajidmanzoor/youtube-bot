# ============================================================
#   VIDEO_GEN.PY — MoviePy se final video assemble karo
# ============================================================

import os
import math
import random
from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    concatenate_videoclips,
    ColorClip,
    CompositeVideoClip,
    TextClip,
)
from config import VIDEO_WIDTH, VIDEO_HEIGHT, FPS, CLIP_DURATION, VIDEOS_DIR


def _resize_clip(clip, target_w: int, target_h: int):
    """Clip ko target resolution pe crop/resize karo (no black bars)."""
    clip_ratio = clip.w / clip.h
    target_ratio = target_w / target_h

    if clip_ratio > target_ratio:
        # Clip wider — height match, crop sides
        new_h = target_h
        new_w = int(clip.w * target_h / clip.h)
    else:
        # Clip taller — width match, crop top/bottom
        new_w = target_w
        new_h = int(clip.h * target_w / clip.w)

    clip = clip.resize((new_w, new_h))
    x_center = (new_w - target_w) // 2
    y_center = (new_h - target_h) // 2
    clip = clip.crop(x1=x_center, y1=y_center, x2=x_center + target_w, y2=y_center + target_h)
    return clip


def _make_fallback_clip(duration: float, color=(30, 30, 50)):
    """Agar video clips na hon toh solid color clip use karo."""
    return ColorClip(size=(VIDEO_WIDTH, VIDEO_HEIGHT), color=color, duration=duration)


def build_video(
    audio_path: str,
    clip_paths: list[str],
    filename: str,
    title: str = "",
) -> str | None:
    """
    Audio + stock clips ko merge karke final MP4 banao.
    Returns: output file path or None on error
    """
    os.makedirs(VIDEOS_DIR, exist_ok=True)
    output_path = os.path.join(VIDEOS_DIR, f"{filename}.mp4")

    try:
        # ── Load audio ─────────────────────────────────────────
        audio = AudioFileClip(audio_path)
        total_duration = audio.duration
        print(f"📢 Audio duration: {total_duration:.1f}s")

        # ── Build background clip sequence ─────────────────────
        num_clips_needed = math.ceil(total_duration / CLIP_DURATION)

        if not clip_paths:
            print("⚠️  No clips — using fallback color background")
            bg = _make_fallback_clip(total_duration)
        else:
            segments = []
            random.shuffle(clip_paths)

            for i in range(num_clips_needed):
                src = clip_paths[i % len(clip_paths)]
                try:
                    vc = VideoFileClip(src, audio=False)
                    vc = _resize_clip(vc, VIDEO_WIDTH, VIDEO_HEIGHT)

                    # Take a random CLIP_DURATION-second segment
                    if vc.duration > CLIP_DURATION + 1:
                        max_start = vc.duration - CLIP_DURATION - 0.5
                        start = random.uniform(0, max_start)
                        vc = vc.subclip(start, start + CLIP_DURATION)
                    else:
                        vc = vc.loop(duration=CLIP_DURATION)

                    vc = vc.set_fps(FPS)
                    segments.append(vc)
                except Exception as e:
                    print(f"⚠️  Clip load error ({src}): {e}")
                    segments.append(_make_fallback_clip(CLIP_DURATION))

            bg = concatenate_videoclips(segments, method="compose")
            bg = bg.subclip(0, total_duration)

        # ── Overlay: subtle title card (first 3s) ──────────────
        layers = [bg]

        if title:
            try:
                txt = (
                    TextClip(
                        title,
                        fontsize=48,
                        color="white",
                        font="DejaVu-Sans-Bold",
                        stroke_color="black",
                        stroke_width=2,
                        size=(VIDEO_WIDTH - 100, None),
                        method="caption",
                    )
                    .set_position(("center", VIDEO_HEIGHT - 130))
                    .set_duration(min(3, total_duration))
                    .set_start(0)
                    .crossfadeout(0.5)
                )
                layers.append(txt)
            except Exception:
                pass  # TextClip optional — Imagemagick missing ho sakta

        final = CompositeVideoClip(layers).set_audio(audio)
        final = final.set_duration(total_duration)

        # ── Export ─────────────────────────────────────────────
        final.write_videofile(
            output_path,
            fps=FPS,
            codec="libx264",
            audio_codec="aac",
            preset="fast",
            threads=4,
            logger=None,  # moviepy verbose output suppress
        )

        # Cleanup
        audio.close()
        final.close()

        if os.path.exists(output_path) and os.path.getsize(output_path) > 10_000:
            print(f"✅ Video saved: {output_path}")
            return output_path
        else:
            print("❌ Video file missing or too small")
            return None

    except Exception as e:
        print(f"❌ build_video error: {e}")
        return None
