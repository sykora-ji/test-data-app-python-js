# Sentiment Analysis App

Web application for analyzing sentiment of text input. Enter any text (review, tweet, comment) and get:

- **Sentiment classification** — positive, negative, or neutral with confidence score
- **Emotion estimation** — joy, surprise, anger, sadness, fear derived from sentiment distribution
- **Keyword extraction** — key words that characterize the input text
- **Analysis history** — last 10 analyses stored in SQLite

## Architecture

```
Nginx (port 8888)
  ├── /          → React static files (frontend/dist)
  └── /api/*     → FastAPI backend (port 8050)
```

The app runs on the [Keboola data-app-python-js](https://github.com/keboola/data-app-python-js) base Docker image with Nginx + Supervisord.

## Tech Stack

### Backend
- **Python 3.11+**
- **FastAPI** + **Uvicorn** — async REST API
- **Hugging Face Transformers** — pre-trained sentiment model
- **PyTorch** — model inference (CPU)
- **aiosqlite** — async SQLite for history storage

### Frontend
- **React 18** + **Vite** — UI framework and build tool
- **Recharts** — radar chart for emotion visualization

### Infrastructure
- **Nginx** — static file serving + reverse proxy
- **Supervisord** — process management
- **uv** — Python package manager
- **Yarn** — Node.js package manager

## AI Model

**[cardiffnlp/twitter-roberta-base-sentiment-latest](https://huggingface.co/cardiffnlp/twitter-roberta-base-sentiment-latest)**

- RoBERTa base model fine-tuned on ~124M tweets for sentiment analysis
- Outputs: positive, negative, neutral with confidence scores
- Runs locally, no API keys needed
- RAM usage: ~500 MB for the model, ~700 MB total

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/status` | Model readiness check |
| `POST` | `/api/analyze` | Analyze text sentiment |
| `GET` | `/api/history` | Last 10 analyses |

### Example

```bash
curl -X POST http://localhost:8888/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "This product is absolutely amazing! Best purchase ever!"}'
```

```json
{
  "text": "This product is absolutely amazing! Best purchase ever!",
  "sentiment": "positive",
  "confidence": 0.9754,
  "emotions": [
    {"emotion": "joy", "score": 0.8291},
    {"emotion": "surprise", "score": 0.1489},
    {"emotion": "anger", "score": 0.0039},
    {"emotion": "sadness", "score": 0.0034},
    {"emotion": "fear", "score": 0.0015}
  ],
  "keywords": ["product", "absolutely", "amazing", "best", "purchase"],
  "analyzed_at": "2026-02-13T14:00:00Z"
}
```

## Project Structure

```
├── backend/
│   ├── main.py            # FastAPI app, endpoints
│   ├── analyzer.py         # HuggingFace model wrapper
│   ├── database.py         # SQLite history (aiosqlite)
│   └── models.py           # Pydantic schemas
├── frontend/
│   ├── src/
│   │   ├── App.jsx         # Main component
│   │   ├── App.css         # Styling
│   │   └── components/
│   │       ├── TextInput.jsx
│   │       ├── AnalyzeButton.jsx
│   │       ├── ResultsPanel.jsx
│   │       └── HistoryList.jsx
│   ├── package.json
│   └── vite.config.js
├── keboola-config/
│   ├── nginx/sites/app.conf
│   ├── supervisord/app.conf
│   └── setup.sh
└── pyproject.toml
```

## How It Works

1. **Setup** (`setup.sh`): installs Python + Node dependencies, builds React frontend, pre-downloads the ML model
2. **Runtime**: Supervisord starts Uvicorn with FastAPI; model loads in background thread
3. **Frontend**: polls `/api/status` until model is ready, then enables the analyze button
4. **Analysis**: text is sent to `/api/analyze`, model runs inference (~1s), results are stored and returned
