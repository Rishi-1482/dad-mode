import base64
import os

from fastapi import Header, HTTPException

from fastapi import FastAPI, File, UploadFile, Depends
from pydantic import BaseModel

from app.services.dad import ask_dad
from app.services.voice import generate_speech, transcribe_audio
from app.services.rag import retrieve
from app.services.web import search_web
from app.services.assistant import answer_question
from contextlib import asynccontextmanager

from app.services.rag import ensure_knowledge_base


APP_API_TOKEN = os.getenv("APP_API_TOKEN")

def verify_api_token(x_app_token: str | None = Header(default=None)):
    if not APP_API_TOKEN:
        raise HTTPException(status_code=500, detail="API token not configured")
    
    if x_app_token != APP_API_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid API token")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Initialize ChromaDB and ingest documents.
    """
    ensure_knowledge_base()
    yield

app = FastAPI(title="Dad Mode API", lifespan=lifespan)


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


class VoiceResponse(BaseModel):
    transcript: str
    response: str
    audio_base64: str

class RAGRequest(BaseModel):
    message: str

class WebSearchRequest(BaseModel):
    message: str

class AskRequest(BaseModel):
    message: str

@app.get("/")
def root():
    return {"message": "Dad Mode API is running"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    response = ask_dad(request.message)

    return ChatResponse(response=response)


@app.post("/voice", dependencies=[Depends(verify_api_token)])
async def voice(file: UploadFile = File(...)):
    audio_bytes = await file.read()

    transcript = transcribe_audio(
        audio_bytes,
        file.filename or "recording.wav"
    )

    result = answer_question(transcript)

    response = result["response"]
    
    audio_base64 = generate_speech(response)

    return VoiceResponse(
        transcript=transcript,
        response=response,
        audio_base64=audio_base64,
    )


@app.post("/rag-chat", response_model=ChatResponse)
def rag_chat(request: RAGRequest):

    results = retrieve(
        request.message,
        n_results=3,
    )

    context_parts = []

    for result in results:
        context_parts.append(
            f"Source: {result['source']}\n"
            f"{result['document']}"
        )

    context = "\n\n---\n\n".join(context_parts)

    response = ask_dad(
        request.message,
        context=context,
    )

    sources = list(
        dict.fromkeys(
            result["source"]
            for result in results
        )
    )

    return {
        "response": response,
        "sources": sources,
    }

@app.post("/web-search")
def web_search(request: WebSearchRequest):
    result = search_web(request.message)

    return {
        "response": result["answer"],
        "sources": result["sources"],
    }

@app.post("/ask", dependencies=[Depends(verify_api_token)])
def ask(request: AskRequest):

    result = answer_question(request.message)

    return result
