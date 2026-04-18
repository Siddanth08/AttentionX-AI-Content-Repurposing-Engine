# AttentionX – Automated Content Repurposing Engine

## Overview
AttentionX is a Streamlit-powered hackathon project that transforms long-form video into ready-to-share short clips. It automatically extracts the audio, transcribes the speech with OpenAI Whisper, detects emotional peak segments, crops video to vertical mobile format, adds dynamic captions, and presents the clips for preview and download.

## Problem Statement
Creators often spend too much time manually hunting for the best moments in long videos and formatting clips for social media. AttentionX solves this by automating the end-to-end repurposing pipeline with AI-powered transcription, audio analysis, and video editing.

## Solution
AttentionX analyzes uploaded video to identify high-impact, emotionally charged segments using audio loudness and keyword detection. It then cuts those scenes into short vertical clips, overlays captions, and delivers a set of polished downloads directly in the browser.

## Features
- Upload long video files via a web interface
- Audio extraction via MoviePy
- Speech-to-text transcription with OpenAI Whisper
- Emotional peak detection using audio energy and keyword importance
- Automatic clip creation with vertical 9:16 cropping
- Face-aware cropping using MediaPipe (fallback to center crop)
- Dynamic bottom captions using MoviePy TextClip
- Browser preview and download buttons for generated clips

## Tech Stack
- Python
- Streamlit
- MoviePy
- Librosa
- OpenCV
- MediaPipe
- Whisper
- NumPy

## How to Run
1. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the app:
   ```bash
   streamlit run app.py
   ```

## Demo Instructions
1. Open the app in your browser.
2. Upload a long-form video file (MP4, MOV, AVI, MKV).
3. Click **Generate Clips**.
4. Preview the output clips and download the ones you like.

## Demo Video
Placeholder for demo video link: [Add your demo video here](#)
