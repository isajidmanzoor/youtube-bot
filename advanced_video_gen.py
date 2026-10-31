# ============================================================
#   ADVANCED_VIDEO_GEN.PY — Real zoom effects + transitions
#   Scene-based editing with actual zoom and fade effects
# ============================================================

import os
import math
import random
from moviepy.editor import (
    VideoFileClip, AudioFileClip, ColorClip,
    concatenate_videoclips, CompositeVideoClip, TextClip,
)
from config import VIDEO_WIDTH, VIDEO_HEIGHT, FPS, VIDEOS_DIR

AFFILIATE_LINK = "https://i.mec.me/?c=pt6wsw2v"


def _resize_fill(clip, w, h):
    """Resize clip to fill frame exactly."""
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


def _apply_zoom_effect(clip, zoom_type="in"):
    """Apply real zoom in or zoom out effect."""
    try:
        duration = clip.duration
        w, h = VIDEO_WIDTH, VIDEO_HEIGHT

        if zoom_type == "in":
            def zoom_in(t):
                scale = 1 + 0.05 * (t / duration)  # 1.0 to 1.05
                new_w = int(w * scale)
                new_h = int(h * scale)
                x = (new_w - w) // 2
                y = (new_h - h) // 2
                return clip.resize((new_w, new_h)).crop(x1=x, y1=y, x2=x+w, y2=y+h).get_frame(t)

            return clip.fl(lambda gf, t: zoom_in(t), apply_to=["mask"])

        elif zoom_type == "out":
            def zoom_out(t):
                scale = 1.05 - 0.05 * (t / duration)  # 1.05 to 1.0
                new_w = int(w * scale)
                new_h = int(h * scale)
                x = (new_w - w) // 2
                y = (new_h - h) // 2
                return clip.resize((new_w, new_h)).crop(x1=x, y1=y, x2=x+w, y2=y+h).get_frame(t)

            return clip.fl(lambda gf, t: zoom_out(t), apply_to=["mask"])

    except Exception:
        pass
    return clip


def _apply_real_zoom(clip, zoom_type="in"):
    """Real zoom using moviepy resize over time."""
    try:
        duration = clip.duration
        if zoom_type == "in":
            clip = clip.resize(lambda t: 1 + 0.04 * t / duration)
        else:
            clip = clip.resize(lambda t: 1.04 - 0.04 * t / duration)

        # Crop to original size after zoom
        clip = clip.crop(
            x_center=clip.w / 2,
            y_center=clip.h / 2,
            width=VIDEO_WIDTH,
            height=VIDEO_HEIGHT,
        )
    except Exception:
        pass
    return clip


def _try_text(text, fontsize, color, duration, position, start=0):
    """Create text overlay, return None if fails."""
    try:
        return (
            TextClip(
                text,
                fontsize=fontsize,
                color=color,
                font="DejaVu-Sans-Bold",
                stroke_color="black",
                stroke_width=2,
            )
            .set_position(position)
            .set_duration(duration)
            .set_start(start)
            .crossfadein(0.3)
            .crossfadeout(0.3)
        )
    except Exception:
        return None


def build_advanced_video(
    audio_path: str,
    clip_paths: list,
    filename: str,
    scenes: list = None,
    title: str = "",
    film_directives: list = None,
) -> str | None:
    """Build video with real zoom effects and scene-based editing."""
    os.makedirs(VIDEOS_DIR, exist_ok=True)
    output_path = os.path.join(VIDEOS_DIR, f"{filename}.mp4")

    try:
        audio = AudioFileClip(audio_path)
        total_dur = audio.duration
        print(f"📢 Audio: {total_dur:.1f}s ({total_dur/60:.1f}min)")

        # ── Build scene segments with zoom effects ─────────────
        film_directives = film_directives or []
        zoom_types = ["in", "out", "in", "out", "in"]  # alternating
        seg_duration = 6  # 6 seconds per clip for better zoom visibility

        if not clip_paths:
            print("⚠️  No clips — color background")
            bg = ColorClip(size=(VIDEO_WIDTH, VIDEO_HEIGHT), color=(10, 5, 20), duration=total_dur)
        else:
            segments = []
            # Every segment is a different, non-overlapping piece of footage
            windows, seg_duration = plan_clip_windows(clip_paths, total_dur, seg_duration)
            num_segs = len(windows)

            for i in range(num_segs):
                src, start_t = windows[i]
                try:
                    vc = VideoFileClip(src, audio=False)
                    vc = _resize_fill(vc, VIDEO_WIDTH, VIDEO_HEIGHT)

                    if vc.duration >= start_t + seg_duration:
                        vc = vc.subclip(start_t, start_t + seg_duration)
                    else:
                        vc = vc.loop(duration=seg_duration)

                    vc = vc.set_fps(FPS)

                    # Apply REAL zoom effect (alternating)
                    directive = film_directives[i % len(film_directives)] if film_directives else {}
                    zoom_hint = directive.get("zoom", "")
                    if "out" in zoom_hint:
                        zoom = "out"
                    elif "push" in zoom_hint or "in" in zoom_hint:
                        zoom = "in"
                    else:
                        zoom = zoom_types[i % len(zoom_types)]
                    vc = _apply_real_zoom(vc, zoom)

                    # Add crossfade transition
                    if segments:
                        vc = vc.crossfadein(0.5)

                    segments.append(vc)

                except Exception as e:
                    print(f"⚠️  Clip {i}: {e}")
                    segments.append(
                        ColorClip(size=(VIDEO_WIDTH, VIDEO_HEIGHT),
                                 color=(random.randint(5,20), random.randint(5,20), random.randint(5,20)),
                                 duration=seg_duration)
                    )

            bg = concatenate_videoclips(segments, method="compose", padding=-0.5)
            bg = bg.subclip(0, total_dur)

        # ── Text overlay layers ────────────────────────────────
        layers = [bg]

        # 1. Title card (first 5 seconds)
        if title:
            short_title = title[:55] + "..." if len(title) > 55 else title
            t = _try_text(short_title, 46, "white", 5, ("center", VIDEO_HEIGHT - 160), 0)
            if t:
                layers.append(t)

        # 2. Scene labels at key moments
        scene_labels = _scene_labels_from_plan(scenes, total_dur) or [
            (total_dur * 0.12, 3.5, "WHAT ARE CRYPTO AIRDROPS?", "yellow"),
            (total_dur * 0.28, 3.5, "STEP BY STEP GUIDE", "white"),
            (total_dur * 0.45, 3.5, "PRO TIPS", "cyan"),
            (total_dur * 0.62, 3.5, "AVOID THESE MISTAKES", "red"),
            (total_dur * 0.78, 3.5, "REALITY CHECK", "lime"),
            (total_dur * 0.90, 3.5, "LINK IN DESCRIPTION", "yellow"),
        ]

        for start_t, dur, text, color in scene_labels:
            if start_t + dur < total_dur:
                overlay = _try_text(text, 40, color, dur, ("center", 55), start_t)
                if overlay:
                    layers.append(overlay)

        # 3. Persistent watermark
        wm = _try_text("Link in Description", 28, "white", total_dur, (30, 30), 0)
        if wm:
            layers.append(wm)

        # 4. Affiliate link (last 35 seconds)
        link_start = max(0, total_dur - 35)
        link = _try_text(
            AFFILIATE_LINK,
            32, "yellow", min(35, total_dur),
            ("center", VIDEO_HEIGHT - 65),
            link_start
        )
        if link:
            layers.append(link)

        # 5. Subscribe CTA (last 12 seconds)
        sub_start = max(0, total_dur - 12)
        sub = _try_text(
            "LIKE & SUBSCRIBE for daily crypto guides!",
            34, "white", min(12, total_dur),
            ("center", VIDEO_HEIGHT - 115),
            sub_start
        )
        if sub:
            layers.append(sub)

        # ── Final composite + export ───────────────────────────
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
            print(f"✅ Video: {output_path} ({size_mb:.1f}MB, {total_dur/60:.1f}min)")
            return output_path

        return None

    except Exception as e:
        print(f"❌ Video error: {e}")
        return None


def _clip_duration(path):
    try:
        vc = VideoFileClip(path, audio=False)
        d = vc.duration or 0
        vc.close()
        return d
    except Exception:
        return 0


def plan_clip_windows(clip_paths, total_dur, seg_duration=6, max_seg=12):
    """Cut clips into non-overlapping windows so no footage repeats inside a video.

    If there is not enough footage, segments get longer (up to max_seg) before
    anything is reused. Consecutive segments never come from the same clip.
    Returns (windows, seg_duration) where windows is a list of (path, start).
    """
    durations = {p: _clip_duration(p) for p in dict.fromkeys(clip_paths)}
    usable = {p: d for p, d in durations.items() if d > 0} or {p: seg_duration for p in durations}
    padding = 0.5  # concatenate overlap
    needed_time = total_dur + 1

    def cut(seg):
        per_clip = {}
        for p, d in usable.items():
            n = max(1, int(d // seg))
            offset = random.uniform(0, max(0, d - n * seg))
            starts = [offset + k * seg for k in range(n)]
            random.shuffle(starts)
            per_clip[p] = starts
        return per_clip

    def coverage(seg):
        return sum(max(1, int(d // seg)) for d in usable.values()) * (seg - padding)

    # Shortest segment length that covers the audio; if none does, the one covering the most
    lengths = [seg_duration + 0.5 * k for k in range(int((max_seg - seg_duration) * 2) + 1)]
    seg = next((s for s in lengths if coverage(s) >= needed_time), max(lengths, key=coverage))
    per_clip = cut(seg)

    # Interleave clips so the same clip never plays twice in a row
    windows, last = [], None
    pools = {p: list(s) for p, s in per_clip.items()}
    while any(pools.values()):
        choices = [p for p, s in pools.items() if s and p != last] or [p for p, s in pools.items() if s]
        p = max(choices, key=lambda c: (len(pools[c]), random.random()))
        windows.append((p, pools[p].pop()))
        last = p

    needed = math.ceil(needed_time / (seg - padding))
    if len(windows) < needed:
        print(f"⚠️  Only {len(windows)} unique segments for {needed} needed — some footage repeats")
        windows = (windows * math.ceil(needed / max(1, len(windows))))[:needed]
    return windows[:needed], seg


def _scene_labels_from_plan(scenes, total_dur):
    if not scenes:
        return []
    colors = {
        "shocked": "yellow",
        "curious": "cyan",
        "confused": "white",
        "excited": "lime",
        "bored": "orange",
        "trusting": "white",
        "urgent": "red",
    }
    labels = []
    count = len(scenes)
    for idx, scene in enumerate(scenes):
        start = min(total_dur - 4, total_dur * (idx / max(1, count)))
        # text_overlay is written for this video; "subtitle" is only a style hint
        # from the studio brief (e.g. "step label") and must not appear on screen
        text = scene.get("text_overlay") or scene.get("scene") or "NEXT STEP"
        color = colors.get(scene.get("viewer_state"), "white")
        labels.append((max(0, start), 3.5, str(text).upper()[:42], color))
    return labels
