import React from "react";

export default function AnalyzeButton({ onClick, loading, disabled }) {
  return (
    <button
      className="analyze-btn"
      onClick={onClick}
      disabled={disabled || loading}
    >
      {loading ? (
        <>
          <span className="spinner" />
          Analyzing...
        </>
      ) : (
        "Analyze Sentiment"
      )}
    </button>
  );
}
