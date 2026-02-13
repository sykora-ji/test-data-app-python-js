import json
import os

import aiosqlite

DB_PATH = os.environ.get("DB_PATH", "/tmp/sentiment_history.db")


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS analysis_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                sentiment TEXT NOT NULL,
                confidence REAL NOT NULL,
                emotions_json TEXT NOT NULL,
                keywords_json TEXT NOT NULL,
                analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()


async def save_analysis(
    text: str,
    sentiment: str,
    confidence: float,
    emotions: list[dict],
    keywords: list[str],
):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO analysis_history (text, sentiment, confidence, emotions_json, keywords_json) VALUES (?, ?, ?, ?, ?)",
            (text, sentiment, confidence, json.dumps(emotions), json.dumps(keywords)),
        )
        await db.commit()


async def get_history(limit: int = 10) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT id, text, sentiment, confidence, analyzed_at FROM analysis_history ORDER BY analyzed_at DESC LIMIT ?",
            (limit,),
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
