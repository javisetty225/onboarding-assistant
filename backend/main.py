"""FastAPI application: the HTTP front door to the assistant."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from . import config
from .answerer import answer
from .schemas import AskRequest, AskResponse

app = FastAPI(title="Payrails Onboarding Assistant", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "llm_configured": bool(config.ANTHROPIC_API_KEY),
        "answer_model": config.ANSWER_MODEL,
    }


@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    return answer(req.question, top_k=req.top_k)


@app.get("/")
def index():
    return FileResponse(config.FRONTEND_DIR / "index.html")


app.mount("/static", StaticFiles(directory=str(config.FRONTEND_DIR)), name="static")