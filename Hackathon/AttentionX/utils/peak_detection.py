import numpy as np
import librosa

KEYWORDS = ["important", "must", "key", "secret", "remember"]


def detect_peak_segments(transcript_segments, audio_path: str, max_segments: int = 4):
    """Select top segments using audio energy and keyword importance."""
    if not transcript_segments:
        return []

    audio, sr = librosa.load(audio_path, sr=22050)
    hop_length = 512
    rms = librosa.feature.rms(y=audio, hop_length=hop_length, frame_length=1024)[0]
    times = np.arange(len(rms)) * hop_length / sr
    duration = len(audio) / sr

    scored_segments = []
    for segment in transcript_segments:
        start = max(0.0, float(segment["start"]))
        end = min(duration, float(segment["end"]))
        if end <= start:
            continue

        frame_mask = (times >= start) & (times <= end)
        energy = float(np.mean(rms[frame_mask])) if np.any(frame_mask) else 0.0

        lower_text = segment["text"].lower()
        keyword_boost = 1.0 + 0.9 * sum(word in lower_text for word in KEYWORDS)
        score = energy * keyword_boost

        scored_segments.append(
            {
                "start": start,
                "end": end,
                "text": segment["text"],
                "score": score,
                "keyword_hits": sum(word in lower_text for word in KEYWORDS),
            }
        )

    scored_segments.sort(key=lambda seg: seg["score"], reverse=True)
    selected = []
    for candidate in scored_segments:
        if len(selected) >= max_segments:
            break

        segment_duration = candidate["end"] - candidate["start"]
        if segment_duration < 2.5:
            padding = (2.5 - segment_duration) / 2
            candidate["start"] = max(0.0, candidate["start"] - padding)
            candidate["end"] = min(duration, candidate["end"] + padding)

        if candidate["end"] - candidate["start"] > 20:
            candidate["end"] = candidate["start"] + 20

        selected.append(
            {
                "start": round(candidate["start"], 2),
                "end": round(candidate["end"], 2),
                "text": candidate["text"],
            }
        )

    return selected
