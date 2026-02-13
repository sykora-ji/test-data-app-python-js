import React from "react";

const MAX_LENGTH = 5000;

export default function TextInput({ text, setText }) {
  const charRatio = text.length / MAX_LENGTH;

  return (
    <div className="text-input">
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value.slice(0, MAX_LENGTH))}
        placeholder="Enter text to analyze sentiment... (review, tweet, comment)"
        rows={5}
      />
      <div className={`char-counter ${charRatio > 0.9 ? "warn" : ""}`}>
        {text.length} / {MAX_LENGTH}
      </div>
    </div>
  );
}
