import re
import threading
from collections import Counter

from transformers import pipeline

STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "as", "is", "was", "are", "were", "been",
    "be", "have", "has", "had", "do", "does", "did", "will", "would",
    "could", "should", "may", "might", "shall", "can", "need", "dare",
    "ought", "used", "it", "its", "this", "that", "these", "those",
    "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you",
    "your", "yours", "yourself", "yourselves", "he", "him", "his",
    "himself", "she", "her", "hers", "herself", "they", "them", "their",
    "theirs", "themselves", "what", "which", "who", "whom", "when",
    "where", "why", "how", "all", "each", "every", "both", "few", "more",
    "most", "other", "some", "such", "no", "nor", "not", "only", "own",
    "same", "so", "than", "too", "very", "just", "because", "about",
    "into", "through", "during", "before", "after", "above", "below",
    "between", "out", "off", "over", "under", "again", "further", "then",
    "once", "here", "there", "any", "also", "been", "being", "having",
    "doing", "get", "got", "getting", "make", "made", "making", "going",
    "come", "came", "take", "took", "give", "gave", "say", "said",
    "tell", "told", "ask", "asked", "work", "seem", "feel", "try",
    "leave", "call", "keep", "let", "begin", "show", "hear", "play",
    "run", "move", "like", "live", "believe", "hold", "bring", "happen",
    "write", "provide", "sit", "stand", "lose", "pay", "meet", "include",
    "continue", "set", "learn", "change", "lead", "understand", "watch",
    "follow", "stop", "create", "speak", "read", "allow", "add", "spend",
    "grow", "open", "walk", "win", "offer", "remember", "consider",
    "appear", "buy", "wait", "serve", "die", "send", "expect", "build",
    "stay", "fall", "cut", "reach", "kill", "remain", "really", "much",
    "even", "still", "well", "now", "back", "down", "up", "long", "way",
    "thing", "man", "day", "time", "year", "people", "part", "place",
    "case", "week", "company", "system", "program", "question", "home",
    "government", "number", "night", "point", "world", "house", "area",
}

SENTIMENT_MODEL = "cardiffnlp/twitter-roberta-base-sentiment-latest"


class SentimentAnalyzer:
    def __init__(self):
        self._sentiment_pipeline = None
        self._loading = False
        self._loaded = False
        self._lock = threading.Lock()

    @property
    def is_ready(self) -> bool:
        return self._loaded

    @property
    def is_loading(self) -> bool:
        return self._loading

    def load_models(self):
        with self._lock:
            if self._loaded:
                return
            self._loading = True
        try:
            self._sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model=SENTIMENT_MODEL,
                top_k=None,
            )
            self._loaded = True
        finally:
            self._loading = False

    def analyze(self, text: str) -> dict:
        if not self._loaded:
            self.load_models()

        truncated = text[:512]

        # Sentiment model returns scores for positive, negative, neutral
        sentiment_results = self._sentiment_pipeline(truncated)[0]
        top_sentiment = max(sentiment_results, key=lambda x: x["score"])

        # Derive emotions from sentiment scores
        scores_by_label = {r["label"]: r["score"] for r in sentiment_results}
        pos = scores_by_label.get("positive", 0)
        neg = scores_by_label.get("negative", 0)
        neu = scores_by_label.get("neutral", 0)

        emotions = self._derive_emotions(pos, neg, neu)
        keywords = self._extract_keywords(text)

        return {
            "sentiment": top_sentiment["label"],
            "confidence": round(top_sentiment["score"], 4),
            "emotions": emotions,
            "keywords": keywords,
        }

    def _derive_emotions(
        self, pos: float, neg: float, neu: float
    ) -> list[dict]:
        """Derive approximate emotion scores from sentiment distribution."""
        emotions = [
            {"emotion": "joy", "score": round(pos * 0.85, 4)},
            {"emotion": "surprise", "score": round(pos * 0.15 + neg * 0.10, 4)},
            {"emotion": "anger", "score": round(neg * 0.40, 4)},
            {"emotion": "sadness", "score": round(neg * 0.35, 4)},
            {"emotion": "fear", "score": round(neg * 0.15, 4)},
        ]
        return sorted(emotions, key=lambda x: -x["score"])

    def _extract_keywords(self, text: str, top_n: int = 8) -> list[str]:
        words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
        filtered = [w for w in words if w not in STOPWORDS]
        if not filtered:
            return []
        counts = Counter(filtered)
        return [word for word, _ in counts.most_common(top_n)]


analyzer = SentimentAnalyzer()
