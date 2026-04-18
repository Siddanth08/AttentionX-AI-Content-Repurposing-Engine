"""Test the complete pipeline with a short generated video"""
import os
from pathlib import Path
import numpy as np
from moviepy import VideoClip, AudioFileClip
import scipy.io.wavfile as wavfile

# Create outputs directory
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

# Generate short test video (5 seconds)
print("🎬 Creating test video...")
fps = 30
duration = 5

# Create audio first
print("🎵 Creating test audio...")
sample_rate = 44100
t = np.linspace(0, duration, int(sample_rate * duration))
frequency = 1000
audio = 0.3 * np.sin(2 * np.pi * frequency * t)

# Add some variation to make peak detection work
audio[int(sample_rate * 1):int(sample_rate * 1.5)] *= 2  # Boost around 1-1.5s
audio[int(sample_rate * 3):int(sample_rate * 3.5)] *= 1.8  # Boost around 3-3.5s

audio_int16 = (audio * 32767).astype(np.int16)
audio_file = OUTPUT_DIR / "test_audio.wav"
wavfile.write(audio_file, sample_rate, audio_int16)

# Create video using make_frame
def make_frame(t):
    frame = np.ones((1080, 1920, 3), dtype=np.uint8) * 100
    frame[200:300, 500:600] = [int(t * 255) % 255, int(t*2 * 255) % 255, int(t*3 * 255) % 255]
    frame[400:600, 1000:1200] = [255, 100, 50]
    return frame

video_file = OUTPUT_DIR / "test_video.mp4"
video = VideoClip(make_frame, duration=duration).with_fps(fps)
audio_clip = AudioFileClip(str(audio_file))
video = video.with_audio(audio_clip)
video.write_videofile(str(video_file), codec="libx264", audio_codec="aac")
video.close()
audio_clip.close()

print(f"✅ Test video created: {video_file}")

# Now run the pipeline
print("\n" + "="*50)
print("🚀 Running AttentionX Pipeline")
print("="*50)

from utils.audio import extract_audio
from utils.transcription import transcribe_audio
from utils.peak_detection import detect_peak_segments
from utils.video_processing import create_clips

try:
    # Extract audio
    print("\n🎵 Step 1: Extracting audio...")
    audio_path = extract_audio(str(video_file))
    print(f"   ✅ Audio extracted: {audio_path}")
    
    # Transcribe
    print("\n📝 Step 2: Transcribing speech...")
    segments = transcribe_audio(audio_path)
    print(f"   ✅ Transcribed {len(segments)} segments")
    for seg in segments[:3]:
        print(f"      - [{seg['start']:.1f}s-{seg['end']:.1f}s] {seg['text'][:50]}")
    
    # Detect peaks
    print("\n🎯 Step 3: Detecting peak moments...")
    best_segments = detect_peak_segments(segments, audio_path)
    print(f"   ✅ Found {len(best_segments)} best segments")
    for i, seg in enumerate(best_segments, 1):
        print(f"      Clip {i}: [{seg['start']:.1f}s-{seg['end']:.1f}s] (score: {seg.get('score', 'N/A')})")
    
    if not best_segments:
        print("   ⚠️  No segments found, using first half of video...")
        best_segments = [{
            'start': 0,
            'end': duration / 2,
            'text': 'AttentionX Highlight'
        }]
    
    # Create clips
    print("\n🎬 Step 4: Creating vertical clips...")
    clips = create_clips(str(video_file), best_segments, output_dir=str(OUTPUT_DIR))
    print(f"   ✅ Generated {len(clips)} clips!")
    for i, clip in enumerate(clips, 1):
        print(f"      Clip {i}: {clip}")
    
    print("\n" + "="*50)
    print("✨ Pipeline Complete! Clips ready in outputs/")
    print("="*50)
    
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
