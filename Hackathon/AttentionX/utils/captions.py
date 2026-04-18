from moviepy import TextClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip


def add_captions(clip, caption_text: str):
    """Overlay a subtitle caption onto a clip."""
    text = caption_text.strip() or "AttentionX Highlight"

    subtitle = TextClip(
        text,
        None,
        color="white",
        stroke_color="black",
        stroke_width=2,
        bg_color="black",
        method="caption",
        size=(int(clip.size[0] * 0.92), None),
    ).set_duration(clip.duration)

    subtitle = subtitle.set_position(("center", clip.size[1] - subtitle.h - 24))
    return CompositeVideoClip([clip, subtitle])
