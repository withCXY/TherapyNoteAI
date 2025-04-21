from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import os
from datetime import datetime
import json
from services.language_service import LanguageService

app = FastAPI(title="Medical Conversation Analysis System")

# Initialize language service
language_service = LanguageService()

# CORS middleware configuration
origins = [
    "http://localhost:3000",  # React development server
    "http://localhost:8000",  # Backend server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class Conversation(BaseModel):
    id: str
    doctor_id: str
    patient_id: str
    date: datetime
    summary: Optional[str] = None
    transcript: Optional[str] = None
    report: Optional[str] = None

class ConversationCreate(BaseModel):
    doctor_id: str
    patient_id: str

class LanguageUpdate(BaseModel):
    language: str

# In-memory storage (replace with database in production)
conversations = {}

@app.middleware("http")
async def language_middleware(request: Request, call_next):
    # Get language from cookie or default to English
    language = request.cookies.get("language", "en")
    language_service.set_language(language)
    response = await call_next(request)
    return response

@app.get("/")
async def root():
    return {"message": language_service.get_translation("welcome")}

@app.get("/translations")
async def get_translations():
    return language_service.get_all_translations()

@app.post("/language")
async def set_language(language_update: LanguageUpdate):
    if language_service.set_language(language_update.language):
        response = JSONResponse(content={"message": "Language updated successfully"})
        response.set_cookie(
            key="language",
            value=language_update.language,
            httponly=True,
            samesite="lax",
            max_age=31536000  # 1 year
        )
        return response
    raise HTTPException(status_code=400, detail="Invalid language code")

@app.post("/conversations/", response_model=Conversation)
async def create_conversation(conversation: ConversationCreate):
    conversation_id = str(len(conversations) + 1)
    new_conversation = Conversation(
        id=conversation_id,
        doctor_id=conversation.doctor_id,
        patient_id=conversation.patient_id,
        date=datetime.now(),
    )
    conversations[conversation_id] = new_conversation
    return new_conversation

@app.get("/conversations/", response_model=List[Conversation])
async def get_conversations():
    return list(conversations.values())

@app.get("/conversations/{conversation_id}", response_model=Conversation)
async def get_conversation(conversation_id: str):
    if conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversations[conversation_id]

@app.post("/conversations/{conversation_id}/record")
async def upload_recording(conversation_id: str, file: UploadFile = File(...)):
    if conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # TODO: Implement audio processing and transcription
    return {"message": "Recording uploaded successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 