"""Simple pipeline test without moviepy editor"""
import os
import sys
from pathlib import Path

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

print("AttentionX - Simple Test")
print("=" * 60)

# Check if we have a video to work with
test_files = list(OUTPUT_DIR.glob("*.mp4")) + list(OUTPUT_DIR.glob("*.mov"))

if not test_files:
    print("❌ No video files found in outputs/")
    print("📝 Please upload a video through the Streamlit app at http://localhost:8502")
    print("   Then the pipeline will automatically generate clips")
    sys.exit(1)

video_file = test_files[0]
print(f"\n📹 Found video: {video_file.name}")

try:
    from utils.audio import extract_audio
    from utils.transcription import transcribe_audio
    from utils.peak_detection import detect_peak_segments
    from utils.video_processing import create_clips
    
    # Extract audio
    print("\n🎵 Step 1: Extracting audio...")
    audio_path = extract_audio(str(video_file))
    print(f"   ✅ Audio extracted: {Path(audio_path).name}")
    
    # Transcribe
    print("\n📝 Step 2: Transcribing speech...")
    segments = transcribe_audio(audio_path)
    print(f"   ✅ Found {len(segments)} speech segments")
    
    # Detect peaks
    print("\n🎯 Step 3: Finding best moments...")
    best_segments = detect_peak_segments(segments, audio_path)
    print(f"   ✅ Selected {len(best_segments)} best clips")
    
    if best_segments:
        for i, seg in enumerate(best_segments, 1):
            start = seg['start']
            end = seg['end']
            print(f"      Clip {i}: {start:.1f}s - {end:.1f}s")
        
        # Create clips
        print("\n🎬 Step 4: Rendering vertical clips...")
        clips = create_clips(str(video_file), best_segments, output_dir=str(OUTPUT_DIR))
        print(f"   ✅ Created {len(clips)} MP4 clips!")
        
        for i, clip in enumerate(clips, 1):
            size_mb = Path(clip).stat().st_size / (1024**2)
            print(f"      {Path(clip).name} ({size_mb:.1f} MB)")
        
        print("\n" + "=" * 60)
        print("✨ SUCCESS! Clips are ready in outputs/")
        print("=" * 60)
    else:
        print("   ⚠️  No peak moments detected. Try a different video.")
        
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
