# =============================================================================
# main.py — FastAPI application entry point
# =============================================================================

import io
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image, UnidentifiedImageError

import snake_classifier_backend.config as config
from snake_classifier_backend.classifier import classifier
from snake_classifier_backend.enricher import get_enrichment

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Lifespan — runs on startup / shutdown
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    if classifier.is_ready:
        logger.info("✅ Model is loaded and ready.")
    else:
        logger.warning("⚠️  Model failed to load: %s", classifier.load_error)
    yield
    # Shutdown (nothing to clean up)


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Snake Classifier API",
    description="Classifies snake images as Venomous / Non-Venomous using a PyTorch model.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/health", tags=["Meta"])
async def health():
    """
    Health check endpoint.
    Returns model status so the frontend can show a warning if the model
    failed to load (e.g. venom.pt is missing).
    """
    return {
        "status":      "ok",
        "model_ready": classifier.is_ready,
        "model_error": classifier.load_error,
        "model_arch":  config.MODEL_ARCH,
        "image_size":  config.IMAGE_SIZE,
    }


@app.post("/predict", tags=["Inference"])
async def predict(file: UploadFile = File(...)):
    """
    Accept an image upload and return:
    - classification label + confidence
    - Gemini-powered enrichment (species, fun fact, IUCN status, first aid)
    """

    # --- 1. Validate model is ready ---
    if not classifier.is_ready:
        raise HTTPException(
            status_code=503,
            detail={
                "error":   "model_not_ready",
                "message": classifier.load_error
                           or "Model is not loaded. Check that venom.pt exists in backend/models/.",
            },
        )

    # --- 2. Validate file type ---
    if file.content_type not in config.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=415,
            detail={
                "error":   "unsupported_media_type",
                "message": f"File type '{file.content_type}' is not supported. "
                           f"Accepted: {', '.join(config.ALLOWED_EXTENSIONS)}",
            },
        )

    # --- 3. Validate file size ---
    contents = await file.read()
    max_bytes = config.MAX_FILE_SIZE_MB * 1024 * 1024
    if len(contents) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail={
                "error":   "file_too_large",
                "message": f"File exceeds the {config.MAX_FILE_SIZE_MB} MB limit.",
            },
        )

    # --- 4. Decode image ---
    try:
        image = Image.open(io.BytesIO(contents))
    except UnidentifiedImageError:
        raise HTTPException(
            status_code=422,
            detail={
                "error":   "invalid_image",
                "message": "The uploaded file could not be decoded as an image. "
                           "Please upload a valid JPEG, PNG, or WebP file.",
            },
        )

    # --- 5. Run classifier ---
    try:
        prediction = classifier.predict(image)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=503,
            detail={"error": "inference_error", "message": str(exc)},
        )
    except Exception as exc:
        logger.exception("Unexpected error during inference.")
        raise HTTPException(
            status_code=500,
            detail={"error": "internal_error", "message": "Inference failed unexpectedly."},
        )

    # --- 6. Fetch enrichment (Gemini + cache) ---
    try:
        enrichment = get_enrichment(
            label=prediction["label"],
            is_venomous=prediction["is_venomous"],
            confidence=prediction["confidence"],
        )
    except Exception:
        logger.exception("Enrichment failed — returning empty enrichment.")
        enrichment = {}

    # --- 7. Build response ---
    return JSONResponse(content={
        "prediction": prediction,
        "enrichment": enrichment,
        "meta": {
            "filename":      file.filename,
            "image_size_px": config.IMAGE_SIZE,
            "model_arch":    config.MODEL_ARCH,
        },
    })


# ---------------------------------------------------------------------------
# Static file serving (production — built React app)
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent   # needed for STATIC_DIR above

STATIC_DIR = BASE_DIR / "static"

if STATIC_DIR.exists():
    # Mount assets subfolder (JS, CSS, images produced by Vite)
    app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        """
        Catch-all: serve index.html for any unknown route so React Router works.
        API routes (/health, /predict) are registered above and matched first.
        """
        index = STATIC_DIR / "index.html"
        if index.exists():
            return FileResponse(index)
        return JSONResponse({"error": "Frontend not built. Run: cd frontend && npm run build"}, status_code=404)

else:
    logger.warning(
        "Static directory '%s' not found. "
        "Run 'cd frontend && npm run build' to generate it.",
        STATIC_DIR,
    )


# ---------------------------------------------------------------------------
# Entry point (for local dev: python main.py)
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent   # needed for STATIC_DIR above

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=True,
    )
