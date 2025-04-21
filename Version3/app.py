import streamlit as st
import sounddevice as sd
import soundfile as sf
import numpy as np
import tempfile
import os
import time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import openai
from pydub import AudioSegment
import pandas as pd
import json

# Load environment variables
load_dotenv()

# Configure OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize session state variables
if 'recordings' not in st.session_state:
    st.session_state.recordings = []
if 'transcripts' not in st.session_state:
    st.session_state.transcripts = []
if 'summaries' not in st.session_state:
    st.session_state.summaries = []

# Set page config
st.set_page_config(
    page_title="AI Therapy Notes Assistant",
    page_icon="🎙️",
    layout="wide"
)

# Application title and description
st.title("AI Therapy Notes Assistant")
st.markdown("""
This application helps therapists manage their session notes through AI-powered
transcription and summarization. Record your therapy sessions or upload audio files
to get instant transcriptions and summaries.
""")

def record_audio(duration=300):
    """Record audio for a specified duration."""
    sample_rate = 44100
    recording = sd.rec(int(duration * sample_rate),
                      samplerate=sample_rate,
                      channels=1,
                      dtype=np.float32)
    
    # Create a progress bar
    progress_bar = st.progress(0)
    for i in range(duration):
        if not st.session_state.get('recording', True):
            sd.stop()
            break
        progress_bar.progress((i + 1) / duration)
        st.session_state.current_time = i
        time.sleep(1)
    
    sd.wait()
    return recording, sample_rate

def save_audio(recording, sample_rate):
    """Save the recorded audio to a temporary file."""
    temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
    sf.write(temp_audio.name, recording, sample_rate)
    return temp_audio.name

def transcribe_audio(audio_path):
    """Transcribe audio using OpenAI's Whisper API."""
    with open(audio_path, "rb") as audio_file:
        transcript = openai.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
    return transcript.text

def generate_summary(transcript):
    """Generate a summary of the transcript using OpenAI's API."""
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a professional therapist's assistant. Summarize the therapy session transcript in a structured way, highlighting key points, observations, and potential action items."},
            {"role": "user", "content": f"Please summarize this therapy session transcript:\n\n{transcript}"}
        ]
    )
    return response.choices[0].message.content

def save_session_data(audio_path, transcript, summary):
    """Save session data to a JSON file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_data = {
        "timestamp": timestamp,
        "audio_path": audio_path,
        "transcript": transcript,
        "summary": summary
    }
    
    # Create data directory if it doesn't exist
    data_dir = Path("session_data")
    data_dir.mkdir(exist_ok=True)
    
    # Save to JSON file
    with open(data_dir / f"session_{timestamp}.json", "w") as f:
        json.dump(session_data, f)
    
    return session_data

# Main application layout
tab1, tab2, tab3 = st.tabs(["Record Session", "Upload Audio", "View History"])

with tab1:
    st.header("Record New Session")
    
    if st.button("Start Recording"):
        st.session_state.recording = True
        recording, sample_rate = record_audio()
        audio_path = save_audio(recording, sample_rate)
        
        with st.spinner("Transcribing audio..."):
            transcript = transcribe_audio(audio_path)
        
        with st.spinner("Generating summary..."):
            summary = generate_summary(transcript)
        
        session_data = save_session_data(audio_path, transcript, summary)
        
        st.success("Recording processed successfully!")
        st.subheader("Transcript")
        st.write(transcript)
        st.subheader("Summary")
        st.write(summary)

with tab2:
    st.header("Upload Audio File")
    uploaded_file = st.file_uploader("Choose an audio file", type=['mp3', 'wav', 'm4a'])
    
    if uploaded_file is not None:
        # Save uploaded file
        temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        temp_audio.write(uploaded_file.read())
        
        with st.spinner("Transcribing audio..."):
            transcript = transcribe_audio(temp_audio.name)
        
        with st.spinner("Generating summary..."):
            summary = generate_summary(transcript)
        
        session_data = save_session_data(temp_audio.name, transcript, summary)
        
        st.success("Audio processed successfully!")
        st.subheader("Transcript")
        st.write(transcript)
        st.subheader("Summary")
        st.write(summary)

with tab3:
    st.header("Session History")
    data_dir = Path("session_data")
    if data_dir.exists():
        session_files = list(data_dir.glob("*.json"))
        if session_files:
            sessions_data = []
            for file in session_files:
                with open(file, "r") as f:
                    data = json.load(f)
                    sessions_data.append({
                        "Date": datetime.strptime(data["timestamp"], "%Y%m%d_%H%M%S").strftime("%Y-%m-%d %H:%M:%S"),
                        "Transcript": data["transcript"][:100] + "...",
                        "Summary": data["summary"][:100] + "..."
                    })
            
            df = pd.DataFrame(sessions_data)
            st.dataframe(df)
        else:
            st.info("No previous sessions found.")
    else:
        st.info("No previous sessions found.")
