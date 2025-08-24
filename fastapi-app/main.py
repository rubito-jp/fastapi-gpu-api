from fastapi import FastAPI, HTTPException
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
    try:
        async with Client() as client:
            speakers = await client.speakers()
        return speakers
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/speak")
async def speak(req: TTSRequest):
    tmp_path = None
    try:
        async with Client() as client:
            audio_query = await client.create_audio_query(req.text, speaker=req.speaker)
            audio_bytes = await audio_query.synthesis(speaker=req.speaker)

            # Tạo file tạm
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
                tmp_path = tmpfile.name
                tmpfile.write(audio_bytes)

        # Trả về file âm thanh
        return FileResponse(tmp_path, media_type="audio/wav", filename="voice.wav")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Xóa file tạm sau khi response xong
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except:
                pass

@app.get("/")
async def root():
    return {"message": "VOICEVOX FastAPI Wrapper is running"}
