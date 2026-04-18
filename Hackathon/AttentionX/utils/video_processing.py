import os
from pathlib import Path
import cv2
import numpy as np
from moviepy import VideoFileClip
from moviepy.video.fx import Crop
import mediapipe as mp
from utils.captions import add_captions


def _detect_face_box(frame):
    """Detect face in frame"""
    try:
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        with mp.solutions.face_detection.FaceDetection(min_detection_confidence=0.5) as detector:
            results = detector.process(rgb_frame)
            if not results.detections:
                return None

            detection = results.detections[0]
            bbox = detection.location_data.relative_bounding_box
            h, w, _ = frame.shape
            x = int(bbox.xmin * w)
            y = int(bbox.ymin * h)
            width = int(bbox.width * w)
            height = int(bbox.height * h)
            return x, y, width, height
    except Exception:
        return None


def _create_vertical_crop_box(frame, face_box=None):
    """Create vertical 9:16 crop coordinates"""
    h, w, _ = frame.shape
    target_width = min(w, int(h * 9 / 16))
    target_height = min(h, int(w * 16 / 9))
    if target_width / target_height > 9 / 16:
        target_height = int(target_width * 16 / 9)
    else:
        target_width = int(target_height * 9 / 16)

    if face_box:
        fx, fy, fw, fh = face_box
        face_center_x = fx + fw / 2
        face_center_y = fy + fh / 2
        x1 = int(np.clip(face_center_x - target_width / 2, 0, w - target_width))
        y1 = int(np.clip(face_center_y - target_height / 2, 0, h - target_height))
    else:
        x1 = int((w - target_width) / 2)
        y1 = int((h - target_height) / 2)

    x2 = x1 + target_width
    y2 = y1 + target_height
    return x1, y1, x2, y2


def crop_vertical(video_path: str, start: float = None, end: float = None):
    """Crop a video to vertical 9:16 format using face detection or center crop."""
    try:
        video_path = str(video_path).replace('\\', '/')
        clip = VideoFileClip(video_path)
        
        if start is not None or end is not None:
            clip = clip.subclipped(start or 0, end or clip.duration)

        frame = clip.get_frame(min(0.5, clip.duration - 0.01))
        face_box = _detect_face_box(frame)

        x1, y1, x2, y2 = _create_vertical_crop_box(frame, face_box)
        cropped = Crop(clip, x1, y1, x2, y2)
        cropped.size = (x2 - x1, y2 - y1)
        return cropped
    except Exception as e:
        raise Exception(f"Crop error: {str(e)}")


def create_clips(video_path: str, segments, output_dir: str = "outputs"):
    """Create captioned vertical clips from video segments and save them to disk."""
    try:
        video_path = str(video_path).replace('\\', '/')
        output_folder = Path(output_dir)
        output_folder.mkdir(parents=True, exist_ok=True)

        clips = []
        for index, segment in enumerate(segments, start=1):
            try:
                start = float(segment["start"])
                end = float(segment["end"])
                duration = max(1.0, end - start)
                if duration < 2.5:
                    end = start + 2.5

                cropped_clip = crop_vertical(video_path, start=start, end=end)
                # caption_text = segment.get("text", "AttentionX highlight")
                # captioned_clip = add_captions(cropped_clip, caption_text)
                captioned_clip = cropped_clip

                output_path = output_folder / f"attentionx_clip_{index}.mp4"
                output_path_str = str(output_path).replace('\\', '/')
                
                captioned_clip.write_videofile(
                    output_path_str,
                    codec="libx264",
                    audio_codec="aac",
                )
                clips.append(output_path_str)
                captioned_clip.close()
                cropped_clip.close()
            except Exception as clip_err:
                raise Exception(f"Clip {index} failed: {str(clip_err)}")

        return clips
    except Exception as e:
        raise Exception(f"Clip creation error: {str(e)}")
