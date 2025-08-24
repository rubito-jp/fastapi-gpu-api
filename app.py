from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
from vvclient import Client 
import tempfile
import os

app = FastAPI(title="VOICEVOX FastAPI Wrapper")

class TTSRequest(BaseModel):
    text: str
    speaker: int = 1

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/speakers")
async def list_speakers():
    async with Client() as client:
        speakers = await client.speakers()
    return speakers

@app.post("/speak")
async def speak(req: TTSRequest):
    async with Client() as client:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
            tmp_path = tmpfile.name

        try:
            audio_query = await client.create_audio_query(req.text, speaker=req.speaker)
            audio_bytes = await audio_query.synthesis(speaker=req.speaker)
            
            with open(tmp_path, "wb") as f:
                f.write(audio_bytes)

            return FileResponse(tmp_path, media_type="audio/wav", filename="voice.wav")

        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

@app.get("/")
async def root():
    return {"message": "VOICEVOX FastAPI Wrapper is running"}
