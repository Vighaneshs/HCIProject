import os
import logging
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from llm_client import call_provider

# Load environment variables from .env 
load_dotenv()

# Config
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://127.0.0.1:3000").split(",")

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)

app = FastAPI(title="Screenshot -> LLM backend (simple)")

# Allow CORS so the frontend can call the API in dev.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in ALLOWED_ORIGINS if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    """Simple health check."""
    return {"status": "ok"}

@app.post("/api/analyze")
async def analyze(image: UploadFile = File(...), task: str = Form("something")):
    """
    Accepts a multipart/form-data POST:
      - image: file (PNG/JPEG)
      - task: optional text describing the task
    Returns JSON: {"status":"ok", "reply": "..."} or error JSON.
    """
    # Simple validation
    if image.content_type not in ("image/png", "image/jpeg", "image/jpg"):
        raise HTTPException(status_code=400, detail="Unsupported image type. Use PNG or JPEG.")

    try:
        # Read the bytes
        content = await image.read()

        logging.info("Received image size=%d bytes; task=%s", len(content), task)

        # Call the LLM provider 
        ok, reply = call_provider(content, task)

        if not ok:
            logging.error("Provider error: %s", reply)
            return JSONResponse(status_code=500, content={"status": "error", "message": str(reply)})

        # Success
        return JSONResponse(status_code=200, content={"status": "ok", "reply": reply})

    except Exception as e:
        logging.exception("Unhandled exception in /api/analyze")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host=HOST, port=PORT, reload=True)