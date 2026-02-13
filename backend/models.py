from pydantic import BaseModel, Field
from datetime import datetime


class AnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)


class EmotionScore(BaseModel):
    emotion: str
    score: float


class AnalyzeResponse(BaseModel):
    text: str
    sentiment: str
    confidence: float
    emotions: list[EmotionScore]
    keywords: list[str]
    analyzed_at: datetime


class HistoryItem(BaseModel):
    id: int
    text: str
    sentiment: str
    confidence: float
    analyzed_at: str
