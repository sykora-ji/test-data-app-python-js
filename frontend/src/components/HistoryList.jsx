import React from "react";

const SENTIMENT_DOT = {
  positive: "\uD83D\uDFE2",
  negative: "\uD83D\uDD34",
  neutral: "\u26AA",
};

export default function HistoryList({ items, onSelect }) {
  if (!items.length) {
    return (
      <div className="history-list empty">
        <p>No analyses yet.</p>
      </div>
    );
  }

  return (
    <div className="history-list">
      <h3>History</h3>
      <ul>
        {items.map((item) => (
          <li key={item.id} onClick={() => onSelect(item)} title="Click to re-analyze">
            <span className="history-dot">
              {SENTIMENT_DOT[item.sentiment] || "\u26AA"}
            </span>
            <span className="history-text">
              {item.text.length > 80 ? item.text.slice(0, 80) + "..." : item.text}
            </span>
            <span className="history-confidence">
              {Math.round(item.confidence * 100)}%
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
