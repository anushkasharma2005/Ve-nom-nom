# =============================================================================
# config.py — Central configuration for the Snake Classifier backend
# Edit this file to change model settings, image preprocessing, classes, etc.
# =============================================================================

import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "venom.pt"       # Path to trained model weights
CACHE_PATH = BASE_DIR / "cache" / "facts_cache.json" # Gemini response cache

# ---------------------------------------------------------------------------
# Model Architecture
# Choose one: "efficientnet_b0", "resnet50", "resnet18", "efficientnet_b2"
# Must match the architecture used during training.
# ---------------------------------------------------------------------------
MODEL_ARCH = "efficientnet_b0"

# Number of output classes (venomous vs non-venomous = 2)
NUM_CLASSES = 2

# ---------------------------------------------------------------------------
# Image Preprocessing
# ---------------------------------------------------------------------------
IMAGE_SIZE = (128, 128)          # (width, height) — must match training size

APPLY_NORMALIZATION = True       # Set False to skip normalization
# ImageNet-style normalization values (standard for pretrained backbones)
NORMALIZE_MEAN = [0.485, 0.456, 0.406]
NORMALIZE_STD  = [0.229, 0.224, 0.225]

# ---------------------------------------------------------------------------
# Class Labels
# Index must match the class indices used during training.
# ---------------------------------------------------------------------------
CLASS_LABELS = {
    0: "Venomous",
    1: "Non-Venomous",
}

# Whether class 0 is the venomous one (used for first-aid logic)
VENOMOUS_CLASS_INDEX = 0

# ---------------------------------------------------------------------------
# Inference
# ---------------------------------------------------------------------------
# Confidence threshold below which we warn the user result may be unreliable
CONFIDENCE_THRESHOLD = 0.65

# ---------------------------------------------------------------------------
# Gemini API
# ---------------------------------------------------------------------------
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")  # Set via env / HF Secret
GEMINI_MODEL   = "gemini-1.5-flash"                    # Fast & cheap for enrichment

# ---------------------------------------------------------------------------
# FastAPI Server
# ---------------------------------------------------------------------------
API_HOST = "0.0.0.0"
API_PORT = 7860          # HF Spaces expects port 7860
CORS_ORIGINS = ["*"]    # Tighten in production if needed

# ---------------------------------------------------------------------------
# Upload Limits
# ---------------------------------------------------------------------------
MAX_FILE_SIZE_MB = 10
ALLOWED_EXTENSIONS = {"image/jpeg", "image/png", "image/webp", "image/jpg"}
