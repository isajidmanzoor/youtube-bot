import subprocess, os

WAV2LIP_DIR = os.path.expanduser("~/wav2lip-test/Wav2Lip")
WAV2LIP_PYTHON = os.path.join(WAV2LIP_DIR, "venv", "bin", "python")
AVATAR_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "avatar")

def generate_avatar_clip(audio_path, run_id, gender="female"):
    audio_abs = os.path.abspath(audio_path)
    out_path = os.path.join(WAV2LIP_DIR, "results", f"avatar_{run_id}.mp4")
    face_file = "host_face_male.jpg" if gender == "male" else "host_face_female.jpg"
    avatar_face = os.path.join(AVATAR_DIR, face_file)

    cmd = [
        WAV2LIP_PYTHON, "inference.py",
        "--checkpoint_path", "checkpoints/wav2lip_gan.pth",
        "--face", avatar_face,
        "--audio", audio_abs,
        "--outfile", out_path,
    ]
    env = os.environ.copy()
    env["OMP_NUM_THREADS"] = "4"
    env["MKL_NUM_THREADS"] = "4"
    env["VECLIB_MAXIMUM_THREADS"] = "4"
    env["NUMEXPR_NUM_THREADS"] = "4"
    result = subprocess.run(cmd, cwd=WAV2LIP_DIR, capture_output=True, text=True, timeout=3600, env=env)
    if result.returncode != 0:
        print("Wav2Lip failed:", result.stderr[-2000:])
        return None
    return out_path if os.path.exists(out_path) else None


def overlay_avatar_on_video(main_video_path, avatar_clip_path, output_path):
    """Overlays the talking avatar clip in the bottom-right corner of the main video."""
    from moviepy.editor import VideoFileClip, CompositeVideoClip

    main_clip = VideoFileClip(main_video_path)
    avatar_clip = VideoFileClip(avatar_clip_path)

    avatar_w = int(main_clip.w * 0.25)
    avatar_clip = avatar_clip.resize(width=avatar_w)

    if avatar_clip.duration < main_clip.duration:
        avatar_clip = avatar_clip.loop(duration=main_clip.duration)
    else:
        avatar_clip = avatar_clip.subclip(0, main_clip.duration)

    margin = 20
    position = (main_clip.w - avatar_w - margin, main_clip.h - avatar_clip.h - margin)
    avatar_clip = avatar_clip.set_position(position)

    final = CompositeVideoClip([main_clip, avatar_clip])
    final.write_videofile(output_path, fps=main_clip.fps, codec="libx264", audio_codec="aac", logger=None)

    main_clip.close()
    avatar_clip.close()
    final.close()
    return output_path
