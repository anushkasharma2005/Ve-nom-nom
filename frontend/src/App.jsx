// =============================================================================
// App.jsx — Main application shell
// =============================================================================

import { useState, useEffect, useCallback } from "react";
import ImageUploader from "./components/ImageUploader";
import ResultCard from "./components/ResultCard";
import config from "./config";

// ---------------------------------------------------------------------------
// API helpers
// ---------------------------------------------------------------------------

async function checkHealth() {
  const res = await fetch(`${config.API_BASE_URL}${config.ENDPOINTS.health}`);
  if (!res.ok) throw new Error("Backend unreachable");
  return res.json();
}

async function classifyImage(file) {
  const form = new FormData();
  form.append("file", file);

  const res = await fetch(`${config.API_BASE_URL}${config.ENDPOINTS.predict}`, {
    method: "POST",
    body: form,
  });

  const data = await res.json();

  if (!res.ok) {
    // Propagate structured backend error
    throw new Error(data?.detail?.message || "Classification failed.");
  }
  return data;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function App() {
  // Health / model status
  const [modelReady, setModelReady]   = useState(null);   // null = checking
  const [modelError, setModelError]   = useState("");

  // Upload / preview
  const [imageFile, setImageFile]     = useState(null);
  const [imageURL, setImageURL]       = useState("");

  // Inference state
  const [loading, setLoading]         = useState(false);
  const [result, setResult]           = useState(null);
  const [error, setError]             = useState("");

  // -------------------------------------------------------------------------
  // Health check on mount
  // -------------------------------------------------------------------------

  useEffect(() => {
    checkHealth()
      .then((data) => {
        setModelReady(data.model_ready);
        if (!data.model_ready) setModelError(data.model_error || "Model not loaded.");
      })
      .catch(() => {
        setModelReady(false);
        setModelError("Cannot reach the backend server.");
      });
  }, []);

  // -------------------------------------------------------------------------
  // File selection
  // -------------------------------------------------------------------------

  const handleFile = useCallback((file) => {
    setImageFile(file);
    setImageURL(URL.createObjectURL(file));
    setResult(null);
    setError("");
  }, []);

  // -------------------------------------------------------------------------
  // Classify
  // -------------------------------------------------------------------------

  const handleClassify = useCallback(async () => {
    if (!imageFile) return;

    setLoading(true);
    setResult(null);
    setError("");

    try {
      const data = await classifyImage(imageFile);
      setResult(data);
    } catch (err) {
      setError(err.message || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }, [imageFile]);

  // -------------------------------------------------------------------------
  // Reset
  // -------------------------------------------------------------------------

  const handleReset = () => {
    setImageFile(null);
    setImageURL("");
    setResult(null);
    setError("");
  };

  // -------------------------------------------------------------------------
  // Render
  // -------------------------------------------------------------------------

  return (
    <div className="app">
      {/* Ambient background blobs */}
      <div className="bg-blob blob-1" aria-hidden="true" />
      <div className="bg-blob blob-2" aria-hidden="true" />
      <div className="bg-blob blob-3" aria-hidden="true" />

      {/* ── Header ─────────────────────────────────────────────────── */}
      <header className="app-header">
        <div className="header-inner">
          <div className="logo">
            <span className="logo-icon">🐍</span>
            <span className="logo-text">VenomScan</span>
          </div>
          <p className="header-tagline">
            AI-powered venomous snake detection · Indian species
          </p>
        </div>
      </header>

      {/* ── Model-not-ready banner ──────────────────────────────────── */}
      {modelReady === false && (
        <div className="banner banner-error" role="alert">
          <strong>⚠ Model Unavailable</strong> — {modelError}
        </div>
      )}

      {/* ── Main content ───────────────────────────────────────────── */}
      <main className="app-main">
        <div className="card upload-card">
          <h1 className="card-title">Identify a Snake</h1>
          <p className="card-sub">
            Upload a clear photo of the snake. We'll tell you if it's venomous, its
            species, conservation status, and what to do if bitten.
          </p>

          {/* Uploader */}
          <ImageUploader onFile={handleFile} disabled={loading || modelReady === false} />

          {/* Image preview */}
          {imageURL && (
            <div className="preview-wrapper">
              <img
                src={imageURL}
                alt="Selected snake"
                className="preview-img"
              />
              <button
                className="btn-ghost preview-clear"
                onClick={handleReset}
                aria-label="Clear image"
              >
                ✕ Clear
              </button>
            </div>
          )}

          {/* Classify button */}
          {imageFile && !result && (
            <button
              className="btn-primary classify-btn"
              onClick={handleClassify}
              disabled={loading || modelReady === false}
            >
              {loading ? (
                <span className="btn-loading">
                  <span className="spinner" /> Analysing…
                </span>
              ) : (
                "🔍 Classify Snake"
              )}
            </button>
          )}

          {/* Inference error */}
          {error && (
            <div className="banner banner-error" role="alert">
              ⚠ {error}
            </div>
          )}
        </div>

        {/* ── Result ───────────────────────────────────────────────── */}
        {result && (
          <div className="result-wrapper">
            <ResultCard result={result} />
            <button className="btn-ghost try-again" onClick={handleReset}>
              ← Try another image
            </button>
          </div>
        )}
      </main>

      {/* ── Footer ─────────────────────────────────────────────────── */}
      <footer className="app-footer">
        <p>
          Built with PyTorch · FastAPI · React · Gemini &nbsp;|&nbsp; Dataset:{" "}
          <a
            href="https://www.kaggle.com/datasets/adityasharma01/snake-dataset-india"
            target="_blank"
            rel="noreferrer"
          >
            Snake Dataset India
          </a>
        </p>
      </footer>
    </div>
  );
}
