import json
import threading
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.analyzer import analyzer
from backend.database import get_history, init_db, save_analysis
from backend.models import AnalyzeRequest, AnalyzeResponse, EmotionScore, HistoryItem


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    threading.Thread(target=analyzer.load_models, daemon=True).start()
    yield


app = FastAPI(title="Sentiment Analysis API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/status")
async def status():
    return {
        "models_ready": analyzer.is_ready,
        "models_loading": analyzer.is_loading,
    }


@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze_text(request: AnalyzeRequest):
    if not analyzer.is_ready:
        raise HTTPException(
            status_code=503,
            detail="Models are still loading. Please try again in a moment.",
        )

    result = analyzer.analyze(request.text)

    await save_analysis(
        text=request.text,
        sentiment=result["sentiment"],
        confidence=result["confidence"],
        emotions=result["emotions"],
        keywords=result["keywords"],
    )

    return AnalyzeResponse(
        text=request.text,
        sentiment=result["sentiment"],
        confidence=result["confidence"],
        emotions=[EmotionScore(**e) for e in result["emotions"]],
        keywords=result["keywords"],
        analyzed_at=datetime.now(timezone.utc),
    )


@app.get("/api/history", response_model=list[HistoryItem])
async def history():
    rows = await get_history(limit=10)
    return [
        HistoryItem(
            id=row["id"],
            text=row["text"][:200],
            sentiment=row["sentiment"],
            confidence=row["confidence"],
            analyzed_at=row["analyzed_at"],
        )
        for row in rows
    ]
