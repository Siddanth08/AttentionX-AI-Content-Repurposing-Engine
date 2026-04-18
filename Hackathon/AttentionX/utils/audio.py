import os
from pathlib import Path
from moviepy.video.io.VideoFileClip import VideoFileClip


def extract_audio(video_path: str, audio_path: str = None) -> str:
    """Extract audio from a video file and save it as WAV."""
    try:
        video_path = str(video_path).replace('\\', '/')
        
        if audio_path is None:
            base = os.path.splitext(video_path)[0]
            audio_path = f"{base}_audio.wav"
        
        audio_path = str(audio_path).replace('\\', '/')
        
        # Ensure output directory exists
        output_dir = Path(audio_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with VideoFileClip(video_path) as clip:
            if clip.audio is None:
                raise ValueError("Video has no audio track.")
            clip.audio.write_audiofile(audio_path)

        return audio_path
    except Exception as e:
        raise Exception(f"Audio extraction failed: {str(e)}")

