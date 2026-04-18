import os
from pathlib import Path
import streamlit as st
from utils.audio import extract_audio
from utils.transcription import transcribe_audio
from utils.peak_detection import detect_peak_segments
from utils.video_processing import create_clips

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def set_page_style():
    st.set_page_config(
        page_title="AttentionX - AI Video Editor",
        page_icon="✨",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    st.markdown(
        """
        <style>
        * {
            margin: 0;
            padding: 0;
        }
        html, body, [data-testid="stAppViewContainer"] {
            background: linear-gradient(135deg, #f5f7fa 0%, #e9ecef 50%, #f0f3f7 100%) !important;
        }
        [data-testid="stAppViewContainer"] {
            background-color: transparent !important;
        }
        .main {
            padding: 40px 28px !important;
            max-width: 1500px !important;
            margin: 0 auto !important;
        }
        h1, h2, h3 {
            color: #1a202c;
            font-weight: 700;
            letter-spacing: -0.015em;
        }
        h1 {
            font-size: 2.8rem !important;
        }
        h2 {
            font-size: 1.8rem !important;
        }
        h3 {
            font-size: 1.3rem !important;
        }
        p, label, .stMarkdown {
            color: #4a5568;
            line-height: 1.7;
            font-size: 1.05rem;
        }
        .header-container {
            text-align: center;
            margin-bottom: 50px;
            padding: 40px 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(102, 126, 234, 0.25);
            color: white;
        }
        .header-title {
            font-size: 3.2rem;
            font-weight: 800;
            margin-bottom: 16px;
            letter-spacing: -0.02em;
            text-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .header-subtitle {
            font-size: 1.2rem;
            color: rgba(255,255,255,0.95);
            max-width: 700px;
            margin: 0 auto;
            font-weight: 300;
            letter-spacing: 0.3px;
        }
        .card-container {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 28px;
            margin-bottom: 32px;
        }
        .card {
            background: white;
            border: 1px solid #e2e8f0;
            border-radius: 16px;
            padding: 32px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            transition: all 0.3s ease;
        }
        .card:hover {
            box-shadow: 0 12px 40px rgba(102, 126, 234, 0.15);
            transform: translateY(-4px);
        }
        .card h3 {
            margin-bottom: 16px;
            font-size: 1.4rem;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .card p {
            color: #5f6368;
            font-size: 1.05rem;
            margin-bottom: 0;
        }
        .upload-area {
            background: linear-gradient(135deg, #f0f2f5 0%, #fafbfc 100%);
            border: 2px dashed #667eea;
            border-radius: 16px;
            padding: 36px;
            text-align: center;
            transition: all 0.2s ease;
        }
        [data-testid="stFileUploader"] {
            background: transparent !important;
            border: none !important;
            padding: 0 !important;
        }
        [data-testid="stFileUploader"] > section {
            background: transparent !important;
            border: none !important;
        }
        .stButton > button {
            background: linear-gradient(135deg, #667eea, #764ba2) !important;
            color: white !important;
            border: none !important;
            padding: 16px 40px !important;
            border-radius: 12px !important;
            font-weight: 700 !important;
            font-size: 1.1rem !important;
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4) !important;
            transition: all 0.3s ease !important;
            letter-spacing: 0.4px !important;
        }
        .stButton > button:hover {
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.5) !important;
            transform: translateY(-2px) !important;
        }
        .stButton > button:active {
            transform: translateY(0) !important;
        }
        [data-testid="stDownloadButton"] > button {
            background: linear-gradient(135deg, #48bb78, #38a169) !important;
            color: white !important;
            border: none !important;
            padding: 12px 28px !important;
            border-radius: 10px !important;
            font-weight: 600 !important;
            font-size: 1rem !important;
            box-shadow: 0 4px 15px rgba(72, 187, 120, 0.3) !important;
        }
        .status-badge {
            display: inline-block;
            padding: 14px 20px;
            border-radius: 10px;
            margin-bottom: 24px;
            font-weight: 600;
            font-size: 1.05rem;
            border-left: 5px solid;
        }
        .status-info {
            background: linear-gradient(135deg, #e0e7ff 0%, #f0f4ff 100%);
            color: #3730a3;
            border-left-color: #667eea;
        }
        .status-success {
            background: linear-gradient(135deg, #dcfce7 0%, #f0fdf4 100%);
            color: #15803d;
            border-left-color: #48bb78;
        }
        .status-error {
            background: linear-gradient(135deg, #fee2e2 0%, #fef2f2 100%);
            color: #991b1b;
            border-left-color: #dc2626;
        }
        .clip-container {
            background: white;
            border: 2px solid #e2e8f0;
            border-radius: 16px;
            padding: 28px;
            margin: 28px 0;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            transition: all 0.3s ease;
        }
        .clip-container:hover {
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.15);
        }
        .clip-header {
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-weight: 700;
            margin-bottom: 20px;
            font-size: 1.2rem;
        }
        [data-testid="stVideo"] {
            border-radius: 12px !important;
            overflow: hidden;
            box-shadow: 0 8px 25px rgba(0,0,0,0.12) !important;
        }
        .divider {
            border: none;
            border-top: 2px solid #e2e8f0;
            margin: 32px 0;
        }
        .footer {
            text-align: center;
            margin-top: 50px;
            padding: 32px;
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
            border-radius: 16px;
            color: #5f6368;
            font-size: 1rem;
            border: 1px solid #e2e8f0;
        }
        .right-panel {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        .tip-box {
            background: linear-gradient(135deg, #fff5e6 0%, #fffbf0 100%);
            border-left: 5px solid #f59e0b;
            padding: 20px;
            border-radius: 12px;
        }
        .tip-box h3 {
            color: #b45309;
            margin-bottom: 12px;
        }
        .tip-box p {
            color: #92400e;
            font-size: 1rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def save_uploaded_file(uploaded_file, destination: Path) -> Path:
    """Save uploaded file with proper error handling"""
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("wb") as out_file:
            out_file.write(uploaded_file.getbuffer())
        return destination
    except Exception as e:
        raise Exception(f"File save error: {str(e)}")


def sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing/replacing problematic characters"""
    import re
    # Remove/replace problematic characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    # Remove consecutive underscores
    filename = re.sub(r'_+', '_', filename)
    return filename



def main():
    set_page_style()

    # Header
    st.markdown(
        """
        <div class="header-container">
            <div class="header-title">✨ AttentionX</div>
            <p class="header-subtitle">Transform your videos into engaging short clips using AI-powered transcription and smart editing</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Main content grid
    col_main, col_side = st.columns([2, 1], gap="large")

    with col_main:
        # Upload section
        st.markdown(
            """
            <div class="card">
                <h3>📹 Upload Your Video</h3>
                <p style="font-size: 1.05rem; color: #5f6368; margin-bottom: 20px;">MP4, MOV, AVI, or MKV format • Max 2GB</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        uploaded_video = st.file_uploader("", type=["mp4", "mov", "avi", "mkv"], label_visibility="collapsed")

        if uploaded_video is not None:
            # Save file to outputs directory with sanitized filename
            try:
                safe_filename = sanitize_filename(uploaded_video.name)
                video_path = OUTPUT_DIR / safe_filename
                save_uploaded_file(uploaded_video, video_path)
                video_path_str = str(video_path).replace('\\', '/')

                # Display video
                st.markdown("### Preview")
                st.video(video_path_str)

                # Generate button
                if st.button("✨ Generate Clips", use_container_width=True, key="generate_btn"):
                    progress_container = st.container()
                    
                    with progress_container:
                        try:
                            # Progress tracking
                            status_display = st.empty()
                            progress_display = st.empty()

                            # Extract audio
                            status_display.markdown(
                                '<div class="status-badge status-info">🎵 Extracting audio...</div>',
                                unsafe_allow_html=True,
                            )
                            progress_display.progress(15)
                            audio_path = extract_audio(video_path_str)

                            # Transcribe
                            status_display.markdown(
                                '<div class="status-badge status-info">📝 Transcribing speech...</div>',
                                unsafe_allow_html=True,
                            )
                            progress_display.progress(35)
                            transcript_segments = transcribe_audio(audio_path)

                            # Detect peaks
                            status_display.markdown(
                                '<div class="status-badge status-info">🎯 Finding best moments...</div>',
                                unsafe_allow_html=True,
                            )
                            progress_display.progress(55)
                            best_segments = detect_peak_segments(transcript_segments, audio_path)

                            if not best_segments:
                                status_display.markdown(
                                    '<div class="status-badge status-error">❌ No strong segments found</div>',
                                    unsafe_allow_html=True,
                                )
                                st.error("Try a video with clearer speech and more variation.")
                                return

                            # Create clips
                            status_display.markdown(
                                '<div class="status-badge status-info">🎬 Creating clips...</div>',
                                unsafe_allow_html=True,
                            )
                            progress_display.progress(85)
                            clip_paths = create_clips(video_path_str, best_segments, output_dir=str(OUTPUT_DIR))

                            # Success
                            status_display.empty()
                            progress_display.empty()

                            st.markdown(
                                f'<div class="status-badge status-success">✅ Created {len(clip_paths)} clip{"s" if len(clip_paths) != 1 else ""}</div>',
                                unsafe_allow_html=True,
                            )

                            # Display clips
                            for idx, clip_path in enumerate(clip_paths, 1):
                                st.markdown("---")
                                st.markdown(
                                    f"""
                                    <div class="clip-container">
                                        <div class="clip-header">📎 Clip {idx}</div>
                                    </div>
                                    """,
                                    unsafe_allow_html=True,
                                )
                                st.video(clip_path)

                                col_btn, _ = st.columns([0.3, 0.7])
                                with col_btn:
                                    with open(clip_path, "rb") as f:
                                        st.download_button(
                                            "📥 Download",
                                            data=f,
                                            file_name=Path(clip_path).name,
                                            mime="video/mp4",
                                            use_container_width=True,
                                        )

                        except Exception as err:
                            status_display.empty()
                            progress_display.empty()
                            st.markdown(
                                f'<div class="status-badge status-error">❌ Error: {str(err)}</div>',
                                unsafe_allow_html=True,
                            )

            except Exception as save_err:
                st.markdown(
                    f'<div class="status-badge status-error">❌ File error: {str(save_err)}</div>',
                    unsafe_allow_html=True,
                )

        else:
            st.markdown(
                """
                <div class="card">
                    <p>💡 Upload a video file to get started. AttentionX will automatically find the best moments and create short vertical clips.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with col_side:
        st.markdown(
            """
            <div class="card">
                <h3>💡 How It Works</h3>
                <div style="font-size: 1.05rem; color: #5f6368; line-height: 1.9;">
                    <p><strong style="color: #667eea;">1.</strong> Upload your video</p>
                    <p><strong style="color: #667eea;">2.</strong> AI analyzes content</p>
                    <p><strong style="color: #667eea;">3.</strong> Finds key moments</p>
                    <p><strong style="color: #667eea;">4.</strong> Creates vertical clips</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="tip-box">
                <h3 style="font-size: 1.15rem; margin-bottom: 12px;">✅ Pro Tips</h3>
                <div style="font-size: 1rem; line-height: 1.8;">
                    <p>✓ Clear audio works best</p>
                    <p>✓ Visible speakers help</p>
                    <p>✓ High-energy moments</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        """
        <div class="footer">
            <h3 style="font-size: 1.3rem; margin-bottom: 12px; background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">✨ Made for Creators</✨></h3>
            <p style="font-size: 1rem; color: #5f6368; margin: 8px 0;">Powered by AI • Fast processing • Professional results</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()





if __name__ == "__main__":
    main()
