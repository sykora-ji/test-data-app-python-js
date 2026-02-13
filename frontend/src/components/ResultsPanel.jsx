import React from "react";
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

const SENTIMENT_CONFIG = {
  positive: { emoji: "\uD83D\uDE0A", label: "Positive", className: "positive" },
  negative: { emoji: "\uD83D\uDE1E", label: "Negative", className: "negative" },
  neutral: { emoji: "\uD83D\uDE10", label: "Neutral", className: "neutral" },
};

const EMOTION_COLORS = {
  joy: "#facc15",
  sadness: "#60a5fa",
  anger: "#ef4444",
  fear: "#a78bfa",
  surprise: "#fb923c",
  disgust: "#84cc16",
  neutral: "#9ca3af",
};

export default function ResultsPanel({ result }) {
  if (!result) {
    return (
      <div className="results-panel empty">
        <p>Enter some text and click &quot;Analyze Sentiment&quot; to see results.</p>
      </div>
    );
  }

  const config = SENTIMENT_CONFIG[result.sentiment] || SENTIMENT_CONFIG.neutral;
  const pct = Math.round(result.confidence * 100);

  const emotionData = result.emotions.map((e) => ({
    emotion: e.emotion.charAt(0).toUpperCase() + e.emotion.slice(1),
    score: e.score,
  }));

  return (
    <div className="results-panel fade-in">
      {/* Sentiment Badge */}
      <div className={`sentiment-badge ${config.className}`}>
        <span className="sentiment-emoji">{config.emoji}</span>
        <span className="sentiment-label">{config.label}</span>
        <div className="confidence-bar-container">
          <div className="confidence-bar" style={{ width: `${pct}%` }} />
          <span className="confidence-label">{pct}%</span>
        </div>
      </div>

      {/* Emotions Chart */}
      <div className="emotions-section">
        <h3>Emotions</h3>
        <ResponsiveContainer width="100%" height={300}>
          <RadarChart data={emotionData}>
            <PolarGrid />
            <PolarAngleAxis dataKey="emotion" tick={{ fontSize: 12 }} />
            <PolarRadiusAxis domain={[0, 1]} tick={false} axisLine={false} />
            <Radar
              dataKey="score"
              fill="#6366f1"
              fillOpacity={0.5}
              stroke="#6366f1"
              strokeWidth={2}
            />
            <Tooltip
              formatter={(val) => `${(val * 100).toFixed(1)}%`}
            />
          </RadarChart>
        </ResponsiveContainer>
        <div className="emotion-tags">
          {result.emotions.map((e) => (
            <span
              key={e.emotion}
              className="emotion-tag"
              style={{
                borderColor: EMOTION_COLORS[e.emotion] || "#9ca3af",
                backgroundColor: `${EMOTION_COLORS[e.emotion] || "#9ca3af"}20`,
              }}
            >
              {e.emotion} {Math.round(e.score * 100)}%
            </span>
          ))}
        </div>
      </div>

      {/* Keywords */}
      {result.keywords.length > 0 && (
        <div className="keywords-section">
          <h3>Key Words</h3>
          <div className="keyword-pills">
            {result.keywords.map((kw) => (
              <span key={kw} className="keyword-pill">
                {kw}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
