# ============================================================
#   ADVANCED_VIDEO_GEN.PY — Scene-based video with overlays
# ============================================================

import os
import math
import random
import shutil
from moviepy.editor import (
    VideoFileClip, AudioFileClip, ColorClip,
    concatenate_videoclips, CompositeVideoClip, TextClip,
)
from config import VIDEO_WIDTH, VIDEO_HEIGHT, FPS, VIDEOS_DIR

AFFILIATE_LINK = "https://i.mec.me/?c=pt6wsw2v"


def _resize_clip(clip, w, h):
    """Resize and crop clip to fill frame."""
    clip_ratio = clip.w / clip.h
    target_ratio = w / h
    if clip_ratio > target_ratio:
        new_h = h
        new_w = int(clip.w * h / clip.h)
    else:
        new_w = w
        new_h = int(clip.h * w / clip.w)
    clip = clip.resize((new_w, new_h))
    x = (new_w - w) // 2
    y = (new_h - h) // 2
    return clip.crop(x1=x, y1=y, x2=x + w, y2=y + h)


def _make_color_clip(duration, color=None):
    """Fallback color clip."""
    if color is None:
        colors = [(10, 5, 0), (0, 10, 25), (0, 8, 0), (15, 0, 30)]
        color = random.choice(colors)
    return ColorClip(size=(VIDEO_WIDTH, VIDEO_HEIGHT), color=color, duration=duration)


def _try_text_clip(text, fontsize, color, duration, position, bg_color=None):
    """Try to create a TextClip, return None if fails."""
    try:
        kwargs = {
            "fontsize": fontsize,
            "color": color,
            "font": "DejaVu-Sans-Bold",
            "stroke_color": "black",
            "stroke_width": 2,
        }
        if bg_color:
            kwargs["bg_color"] = bg_color

        clip = (TextClip(text, **kwargs)
                .set_position(position)
                .set_duration(duration))
        return clip
    except Exception:
        return None


def build_advanced_video(
    audio_path: str,
    clip_paths: list,
    filename: str,
    scenes: list = None,
    title: str = "",
) -> str | None:
    """
    Build advanced video with scene-based editing.
    """
    os.makedirs(VIDEOS_DIR, exist_ok=True)
    output_path = os.path.join(VIDEOS_DIR, f"{filename}.mp4")

    try:
        # ── Load audio ─────────────────────────────────────────
        audio = AudioFileClip(audio_path)
        total_dur = audio.duration
        print(f"📢 Audio: {total_dur:.1f}s (~{total_dur/60:.1f} min)")

        # ── Build scene clips ──────────────────────────────────
        if not clip_paths:
            print("⚠️  No clips — using color backgrounds")
            bg = _make_color_clip(total_dur)
        else:
            segments = []
            num_clips = math.ceil(total_dur / 5)  # 5 sec per clip
            random.shuffle(clip_paths)

            for i in range(num_clips):
                src = clip_paths[i % len(clip_paths)]
                try:
                    vc = VideoFileClip(src, audio=False)
                    vc = _resize_clip(vc, VIDEO_WIDTH, VIDEO_HEIGHT)

                    # Random start point for variety
                    clip_dur = 5
                    if vc.duration > clip_dur + 1:
                        max_start = vc.duration - clip_dur - 0.5
                        start = random.uniform(0, max_start)
                        vc = vc.subclip(start, start + clip_dur)
                    else:
                        vc = vc.loop(duration=clip_dur)

                    vc = vc.set_fps(FPS)
                    segments.append(vc)
                except Exception as e:
                    print(f"⚠️  Clip {i} error: {e}")
                    segments.append(_make_color_clip(5))

            bg = concatenate_videoclips(segments, method="compose")
            bg = bg.subclip(0, total_dur)

        # ── Overlay layers ────────────────────────────────────
        layers = [bg]

        # 1. Title card (first 4 seconds)
        if title:
            title_short = title[:50] + "..." if len(title) > 50 else title
            title_clip = _try_text_clip(
                title_short, 48, "white", min(4, total_dur),
                ("center", VIDEO_HEIGHT - 150)
            )
            if title_clip:
                layers.append(title_clip.crossfadeout(0.5))

        # 2. Scene text overlays at intervals
        overlay_times = [
            (total_dur * 0.15, "WHAT ARE AIRDROPS?", "yellow"),
            (total_dur * 0.30, "STEP BY STEP GUIDE", "white"),
            (total_dur * 0.50, "PRO TIPS", "cyan"),
            (total_dur * 0.70, "AVOID THESE MISTAKES", "red"),
            (total_dur * 0.85, "WITHDRAWAL PROOF", "lime"),
        ]

        for start_t, overlay_text, color in overlay_times:
            if start_t + 3 < total_dur:
                ov = _try_text_clip(
                    f"▶ {overlay_text}",
                    42, color, 3.0,
                    ("center", 60)
                )
                if ov:
                    layers.append(ov.set_start(start_t).crossfadein(0.3).crossfadeout(0.3))

        # 3. Persistent link watermark (last 30 seconds)
        link_start = max(0, total_dur - 30)
        link_clip = _try_text_clip(
            f"🔗 {AFFILIATE_LINK}",
            30, "yellow", min(30, total_dur),
            ("center", VIDEO_HEIGHT - 60)
        )
        if link_clip:
            layers.append(link_clip.set_start(link_start))

        # 4. Subscribe reminder (last 10 seconds)
        sub_start = max(0, total_dur - 10)
        sub_clip = _try_text_clip(
            "👍 LIKE & SUBSCRIBE for more FREE CRYPTO tips!",
            34, "white", min(10, total_dur),
            ("center", VIDEO_HEIGHT - 110)
        )
        if sub_clip:
            layers.append(sub_clip.set_start(sub_start))

        # ── Composite and export ──────────────────────────────
        final = CompositeVideoClip(layers).set_audio(audio).set_duration(total_dur)

        final.write_videofile(
            output_path,
            fps=FPS,
            codec="libx264",
            audio_codec="aac",
            preset="fast",
            threads=4,
            logger=None,
        )

        audio.close()
        final.close()

        if os.path.exists(output_path) and os.path.getsize(output_path) > 10_000:
            size_mb = os.path.getsize(output_path) / 1024 / 1024
            print(f"✅ Video: {output_path} ({size_mb:.1f} MB)")
            return output_path
        return None

    except Exception as e:
        print(f"❌ Video build error: {e}")
        return None
