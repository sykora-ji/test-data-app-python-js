import React, { useState, useEffect, useCallback } from "react";
import TextInput from "./components/TextInput";
import AnalyzeButton from "./components/AnalyzeButton";
import ResultsPanel from "./components/ResultsPanel";
import HistoryList from "./components/HistoryList";

export default function App() {
  const [text, setText] = useState("");
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modelsReady, setModelsReady] = useState(false);
  const [error, setError] = useState(null);

  const fetchHistory = useCallback(async () => {
    try {
      const res = await fetch("/api/history");
      if (res.ok) {
        setHistory(await res.json());
      }
    } catch {
      // ignore - history is optional
    }
  }, []);

  // Poll model status until ready
  useEffect(() => {
    let cancelled = false;

    async function poll() {
      while (!cancelled) {
        try {
          const res = await fetch("/api/status");
          if (res.ok) {
            const data = await res.json();
            if (data.models_ready) {
              setModelsReady(true);
              return;
            }
          }
        } catch {
          // server not ready yet
        }
        await new Promise((r) => setTimeout(r, 2000));
      }
    }

    poll();
    return () => { cancelled = true; };
  }, []);

  // Fetch history on mount and when models become ready
  useEffect(() => {
    if (modelsReady) fetchHistory();
  }, [modelsReady, fetchHistory]);

  const handleAnalyze = async () => {
    if (!text.trim()) return;
    setLoading(true);
    setError(null);

    try {
      const res = await fetch("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: text.trim() }),
      });

      if (!res.ok) {
        const detail = await res.json().catch(() => null);
        throw new Error(detail?.detail || `Error ${res.status}`);
      }

      const data = await res.json();
      setResult(data);
      fetchHistory();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleHistorySelect = (item) => {
    setText(item.text);
  };

  return (
    <div className="app">
      <header>
        <h1>Sentiment Analysis</h1>
        {!modelsReady && (
          <div className="models-loading">
            <span className="spinner" />
            Loading AI models...
          </div>
        )}
      </header>

      <main>
        <section className="input-section">
          <TextInput text={text} setText={setText} />
          <AnalyzeButton
            onClick={handleAnalyze}
            loading={loading}
            disabled={!modelsReady || !text.trim()}
          />
          {error && <div className="error-msg">{error}</div>}
        </section>

        <section className="results-section">
          <ResultsPanel result={result} />
        </section>

        <section className="history-section">
          <HistoryList items={history} onSelect={handleHistorySelect} />
        </section>
      </main>
    </div>
  );
}
