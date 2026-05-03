# =============================================================================
# Dockerfile — VenomScan for Hugging Face Spaces
# Builds React frontend, then serves everything via FastAPI on port 7860.
# =============================================================================

# ── Stage 1: Build React frontend ─────────────────────────────────────────
FROM node:20-slim AS frontend-builder

WORKDIR /build/frontend

# Install deps first (layer cache)
COPY frontend/package*.json ./
RUN npm ci

# Copy source and build
COPY frontend/ ./
RUN npm run build
# Output lands in /build/backend/static (see vite.config.js outDir)


# ── Stage 2: Python backend + built frontend ───────────────────────────────
FROM python:3.11-slim

# System deps for PyTorch (CPU-only) and Pillow
RUN apt-get update && apt-get install -y --no-install-recommends \
        libglib2.0-0 libsm6 libxrender1 libxext6 curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:/root/.local/bin:$PATH"

WORKDIR /app

# Copy backend
COPY backend/ ./

# Copy built frontend static files
COPY --from=frontend-builder /build/backend/static ./static

# Install Python deps with uv (no venv — container is isolated)
RUN uv pip install --system --no-cache -r <(uv pip compile pyproject.toml)

# HF Spaces: non-root user for security
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Expose port 7860 (HF Spaces default)
EXPOSE 7860

# Serve frontend static files via FastAPI + uvicorn
CMD ["python", "main.py"]
