---
title: VenomScan — Snake Identifier
emoji: 🐍
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
license: mit
app_port: 7860
---

# VenomScan

AI-powered venomous snake classifier for Indian species. Upload a snake photo to get:

- ✅ Venomous / Non-Venomous classification
- 📊 Confidence score
- 🐍 Species name guess
- 💡 Fun fact
- 🌿 IUCN conservation status
- 🚨 First aid tips (if venomous)

Built with PyTorch · FastAPI · React · Gemini AI



# VenomScan: Snake Classifier

VenomScan is an AI-powered application that classifies Indian snakes as venomous or non-venomous from images. The system provides enriched data including species identification, conservation status, and safety information using Google's Gemini API.

## Overview

The project consists of:
- PyTorch-based deep learning classifier (EfficientNet B0)
- FastAPI backend for inference and enrichment
- React + Vite frontend for image upload and results display
- Intelligent caching to minimize API calls
- Docker containerization for HuggingFace Spaces deployment

## Features

- Real-time snake classification from uploaded images
- Model confidence scoring with reliability warnings
- Cached enrichment data (species guess, fun facts, IUCN status)
- Conservation status information
- First-aid guidance for venomous snakes
- Responsive web interface with drag-and-drop upload

## Directory Structure

```
Ve-nom-nom/
├── backend/
│   ├── main.py                          # FastAPI application entry point
│   ├── pyproject.toml                   # Python dependencies
│   ├── Dockerfile                       # Container build configuration
│   ├── snake_classifier_backend/
│   │   ├── __init__.py
│   │   ├── config.py                    # Centralized configuration
│   │   ├── classifier.py                # PyTorch model inference
│   │   ├── enricher.py                  # Gemini API integration and caching
│   │   ├── models/
│   │   │   └── venom.pt                 # Trained model weights
│   │   └── cache/
│   │       └── facts_cache.json         # Cached enrichment data
│   └── static/                          # Built frontend files
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── components/
│       │   ├── ImageUploader.jsx        # File upload interface
│       │   ├── ResultCard.jsx           # Result display container
│       │   ├── ConfidenceMeter.jsx      # Confidence visualization
│       │   └── StatusBadge.jsx          # IUCN status display
│       └── styles/
├── .github/
│   └── workflows/
│       └── deploy.yml                   # CI/CD for HuggingFace Spaces
└── README.md
```

## Installation

### Prerequisites

- Python 3.11+
- Node.js 18+
- pip or uv package manager
- Google Gemini API key (with billing enabled)

### Backend Setup

```bash
cd backend

# Using uv (recommended)
uv sync

# Or using pip
pip install -e ".[dev]"
```

### Frontend Setup

```bash
cd frontend
npm install
```

## Configuration

Edit `backend/snake_classifier_backend/config.py` to adjust:

- Model architecture (default: efficientnet_b0)
- Image preprocessing settings (size, normalization)
- Confidence threshold (default: 0.65)
- Gemini model selection (default: gemini-2.0-flash)
- API host and port (default: 0.0.0.0:7860)

## Running Locally

### Start Backend Server

```bash
export GEMINI_API_KEY="your-api-key-here"
cd backend
python main.py
```

The API will be available at http://localhost:7860

### Start Frontend Development Server

In a new terminal:

```bash
cd frontend
npm run dev
```

The frontend will be available at http://localhost:5173

### Test Health Endpoint

```bash
curl http://localhost:7860/health
```

Expected response:
```json
{"status":"ready","model_loaded":true}
```

## API Endpoints

### GET /health
Returns server and model status.

**Response:**
```json
{
  "status": "ready",
  "model_loaded": true
}
```

### POST /predict
Accepts an image file and returns classification with enrichment data.

**Request:**
```bash
curl -X POST http://localhost:7860/predict \
  -F "file=@snake_image.jpg"
```

**Response:**
```json
{
  "classification": {
    "class": "Venomous",
    "confidence": 0.92
  },
  "enrichment": {
    "species_guess": "Indian Cobra",
    "fun_fact": "Can rear up to 6 feet high when threatened.",
    "iucn_status": "VU",
    "conservation_note": "Listed as Vulnerable due to habitat loss.",
    "first_aid_tip": "Seek immediate medical attention.",
    "danger_level": "Extreme"
  }
}
```

## Building Frontend

```bash
cd frontend
npm run build
```

Output files are generated in `backend/static/` for FastAPI to serve.

## Docker Deployment

Build the Docker image:

```bash
docker build -t venom-classifier .
```

Run the container:

```bash
docker run -p 7860:7860 \
  -e GEMINI_API_KEY="your-api-key" \
  venom-classifier
```

## Deployment on HuggingFace Spaces

### Prerequisites

1. Create a new Space on HuggingFace
2. Set repository secret: `GEMINI_API_KEY` with your Google Gemini API key
3. Ensure billing is enabled on your Google Cloud project

### Deploy

Push to your Space repository:

```bash
git push
```

The CI/CD pipeline (`.github/workflows/deploy.yml`) automatically builds and deploys.

## Environment Variables

Required variables:

- `GEMINI_API_KEY`: Google Gemini API key (required for enrichment)
- `MODEL_HF_ID`: HuggingFace model repository (default: Ve-nom-nom/venom_model)
- `MODEL_FILENAME`: Model weights filename (default: venom.pt)

## Model Details

- Architecture: EfficientNet B0
- Input size: 128x128 pixels
- Classes: 2 (Venomous, Non-Venomous)
- Normalization: ImageNet standard (mean: [0.485, 0.456, 0.406], std: [0.229, 0.224, 0.225])
- Confidence threshold: 0.65 (configurable)

## Caching System

Enrichment data is cached locally to minimize API calls:

- Cache file: `backend/snake_classifier_backend/cache/facts_cache.json`
- Cache key: classification label (lowercase, spaces replaced with underscores)
- First request for a label: Calls Gemini API
- Subsequent requests: Returns cached data instantly

## Troubleshooting

### Model not loading
Check that `backend/snake_classifier_backend/models/venom.pt` exists or is accessible from HuggingFace.

### Gemini API failing with 429 error
Rate limit exceeded. Ensure billing is enabled on your Google Cloud project.

### CORS errors
Update `CORS_ORIGINS` in config.py to match your frontend origin.

### Cache corruption
Delete `backend/snake_classifier_backend/cache/facts_cache.json` to reset cache.

## Performance

- Average inference time: 200-300ms per image
- Model size: 16.3 MB
- Memory usage: ~500MB (typical)
- Concurrent requests: Supported via FastAPI

## Contributing

1. Create a feature branch
2. Make changes to backend/frontend as needed
3. Test locally with `python main.py` and `npm run dev`
4. Submit pull request

## Disclaimer

This tool is for educational purposes only. Do not rely on it for medical decisions. Always contact emergency services if bitten by a snake.

## License

This project is provided as-is for research and educational purposes.

## Authors

Ve-nom-nom team

## Support

For issues or questions, please refer to the project repository on GitHub or HuggingFace.
