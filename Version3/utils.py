import openai
import os
from pydub import AudioSegment
import tempfile
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import time
import base64
from io import BytesIO

def get_microphone_devices():
    """
    Get list of available microphone devices
    """
    devices = sd.query_devices()
    input_devices = [device for device in devices if device['max_input_channels'] > 0]
    return input_devices

def record_audio(duration=10, sample_rate=44100, device_id=None):
    """
    Record audio from microphone
    Args:
        duration: Recording duration in seconds
        sample_rate: Sample rate for recording
        device_id: ID of the input device to use
    Returns:
        Path to the recorded audio file
    """
    try:
        # Get default input device if none specified
        if device_id is None:
            device_id = sd.default.device[0]
        
        print(f"Recording for {duration} seconds using device {device_id}...")
        
        # Record audio
        recording = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1,
            device=device_id,
            dtype='float32'
        )
        
        # Wait for recording to complete
        sd.wait()
        
        # Create temporary file for the recording
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            wav.write(temp_file.name, sample_rate, recording)
            return temp_file.name
            
    except Exception as e:
        print(f"Error in recording: {e}")
        print("Available input devices:")
        for i, device in enumerate(get_microphone_devices()):
            print(f"{i}: {device['name']}")
        return None

def process_audio_data(audio_data):
    """
    Process audio data from Streamlit's audio recorder
    Args:
        audio_data: Base64 encoded audio data
    Returns:
        Path to the processed audio file
    """
    try:
        # Decode base64 audio data
        audio_bytes = base64.b64decode(audio_data.split(',')[1])
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_file.write(audio_bytes)
            return temp_file.name
            
    except Exception as e:
        print(f"Error processing audio data: {e}")
        return None

def transcribe_audio(audio_path):
    """
    Transcribe audio file using OpenAI's Whisper API
    """
    try:
        with open(audio_path, "rb") as audio_file:
            transcript = openai.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        return transcript.text
    except Exception as e:
        print(f"Error in transcription: {e}")
        return None

def generate_summary(text):
    """
    Generate a summary of the transcribed text using OpenAI's GPT model
    """
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes therapy sessions."},
                {"role": "user", "content": f"Please provide a concise summary of the following therapy session:\n\n{text}"}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error in summary generation: {e}")
        return None

def generate_report(summary):
    """
    Generate a detailed therapy report based on the summary
    """
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional therapist creating detailed session reports."},
                {"role": "user", "content": f"Based on the following summary, create a detailed therapy session report including key points, observations, and recommendations:\n\n{summary}"}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error in report generation: {e}")
        return None

def convert_audio_format(input_path, output_format='wav'):
    """
    Convert audio file to specified format
    """
    try:
        audio = AudioSegment.from_file(input_path)
        with tempfile.NamedTemporaryFile(suffix=f'.{output_format}', delete=False) as temp_file:
            audio.export(temp_file.name, format=output_format)
            return temp_file.name
    except Exception as e:
        print(f"Error in audio conversion: {e}")
        return None 