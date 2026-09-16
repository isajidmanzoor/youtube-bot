import os
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import VideoClip, CompositeVideoClip

def get_ticker_font(size):
    paths = ["/System/Library/Fonts/Helvetica.ttc", "/Library/Fonts/Arial Bold.ttf"]
    for p in paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except:
                continue
    return ImageFont.load_default()

def add_news_ticker(video_clip, news_headlines):
    """Add a scrolling 'BREAKING NEWS' ticker banner at the bottom of the video."""
    if not news_headlines:
        return video_clip

    vw, vh = video_clip.size
    ticker_h = int(vh * 0.06)
    font = get_ticker_font(int(ticker_h * 0.55))

    ticker_text = "  •  ".join(news_headlines) + "  •  "
    ticker_text = ticker_text * 3  # repeat so it loops smoothly

    # Measure full text width
    dummy = Image.new("RGB", (1, 1))
    d = ImageDraw.Draw(dummy)
    bbox = d.textbbox((0, 0), ticker_text, font=font)
    text_w = bbox[2] - bbox[0]

    # Build the full scrolling strip image once
    strip = Image.new("RGB", (text_w + vw, ticker_h), (20, 20, 20))
    sd = ImageDraw.Draw(strip)
    sd.text((vw, (ticker_h - (bbox[3]-bbox[1])) // 2), ticker_text, font=font, fill=(255, 255, 255))

    import numpy as np
    strip_arr = np.array(strip)

    scroll_speed = 90  # pixels per second

    def make_frame(t):
        offset = int((scroll_speed * t) % (text_w + vw))
        frame = strip_arr[:, offset:offset + vw]
        if frame.shape[1] < vw:
            frame = np.hstack([frame, strip_arr[:, :vw - frame.shape[1]]])
        return frame

    ticker_clip = VideoClip(make_frame, duration=video_clip.duration)
    ticker_clip = ticker_clip.set_position(("center", vh - ticker_h))

    # "BREAKING NEWS" label box on the left
    label_w = int(vw * 0.16)
    label_img = Image.new("RGB", (label_w, ticker_h), (200, 0, 0))
    ld = ImageDraw.Draw(label_img)
    label_font = get_ticker_font(int(ticker_h * 0.5))
    ld.text((10, (ticker_h - int(ticker_h*0.5)) // 2), "BREAKING", font=label_font, fill=(255, 255, 255))
    from moviepy.editor import ImageClip
    label_clip = ImageClip(np.array(label_img)).set_duration(video_clip.duration)
    label_clip = label_clip.set_position((0, vh - ticker_h))

    return CompositeVideoClip([video_clip, ticker_clip, label_clip])
