import os
from pydub import AudioSegment
import openai
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class AudioService:
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
    async def process_audio(self, audio_file_path: str) -> Optional[str]:
        try:
            # Convert audio to mp3 if needed
            audio = AudioSegment.from_file(audio_file_path)
            mp3_path = audio_file_path.replace(os.path.splitext(audio_file_path)[1], ".mp3")
            audio.export(mp3_path, format="mp3")
            
            # Transcribe using OpenAI Whisper
            with open(mp3_path, "rb") as audio_file:
                transcript = self.openai_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )
            
            # Clean up temporary file
            os.remove(mp3_path)
            
            return transcript.text
        except Exception as e:
            print(f"Error processing audio: {str(e)}")
            return None
    
    async def generate_summary(self, transcript: str) -> Optional[str]:
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a medical assistant. Summarize the following conversation in a structured format, highlighting key medical information, symptoms, and treatment discussions."},
                    {"role": "user", "content": transcript}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating summary: {str(e)}")
            return None 