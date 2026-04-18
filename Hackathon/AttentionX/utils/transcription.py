import whisper
import numpy as np
from functools import lru_cache
from scipy.io import wavfile


@lru_cache(maxsize=1)
def get_whisper_model():
    return whisper.load_model("base")


def transcribe_audio(audio_path: str):
    """Run Whisper transcription and return a list of timestamped segments."""
    print(f"   Loading audio from {audio_path}...")
    
    # Use scipy to read WAV (no FFmpeg needed!)
    sr, audio_data = wavfile.read(audio_path)
    
    # Convert to float32 and normalize
    if audio_data.dtype != np.float32:
        audio_data = audio_data.astype(np.float32) / np.max(np.abs(audio_data))
    
    # Convert to mono if stereo
    if audio_data.ndim > 1:
        audio_data = audio_data.mean(axis=1)
    
    # Resample if needed
    if sr != 16000:
        print(f"   Resampling from {sr}Hz to 16000Hz...")
        import librosa
        audio_data = librosa.resample(audio_data, orig_sr=sr, target_sr=16000)
        sr = 16000
    
    print(f"   Audio loaded: {len(audio_data)} samples at {sr}Hz")
    print(f"   Duration: {len(audio_data)/sr:.1f} seconds")
    print(f"   Running Whisper transcription...")
    
    model = get_whisper_model()
    result = model.transcribe(audio_data, language="en", verbose=False)
    
    segments = result.get("segments", [])
    print(f"   ✅ Found {len(segments)} speech segments")
    
    return [
        {
            "start": float(segment["start"]),
            "end": float(segment["end"]),
            "text": segment["text"].strip(),
        }
        for segment in segments
    ]
