# 🐍 VenomScan — Snake Classifier

AI-powered venomous snake classifier for Indian species. Upload a photo →
get a **Venomous / Non-Venomous** verdict, confidence score, species name,
IUCN conservation status, fun fact, and first-aid tip — powered by PyTorch
and Google Gemini.

---

## Project Structure

```
snake-classifier/
├── backend/
│   ├── main.py          # FastAPI app — routes, startup, static serving
│   ├── classifier.py    # PyTorch model load + inference
│   ├── enricher.py      # Gemini API calls + JSON cache
│   ├── config.py        # ★ All tuneable settings live here
│   ├── models/
│   │   └── venom.pt     # Your trained weights (gitignored — add manually)
│   ├── cache/           # Auto-created — Gemini response cache
│   └── pyproject.toml   # uv-managed Python deps
├── frontend/
│   ├── src/
│   │   ├── App.jsx               # Main app shell + API calls
│   │   ├── config.js             # Frontend config (API URL, IUCN colours)
│   │   ├── index.css             # All styles (dark blue theme)
│   │   └── components/
│   │       ├── ImageUploader.jsx # Drag-and-drop upload zone
│   │       ├── ResultCard.jsx    # Full result display
│   │       ├── ConfidenceMeter.jsx # Animated confidence bar
│   │       └── StatusBadge.jsx  # IUCN status pill
│   ├── index.html
│   ├── vite.config.js   # Dev proxy → backend; build → backend/static
│   └── package.json
├── .github/
│   └── workflows/
│       └── deploy.yml   # CI/CD → Hugging Face Spaces on push to main
├── Dockerfile           # HF Spaces (Node build + Python serve)
├── README.md            # HF Spaces metadata + description
└── .gitignore
```

---

## Quick Start — Local Development

### Prerequisites

- Python 3.11+
- Node.js 20+
- [uv](https://docs.astral.sh/uv/) — install with:
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

---

### 1 — Backend

```bash
cd backend

# Create virtual env and install deps (uv handles everything)
uv venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

uv pip install -e ".[dev]"

# Add your trained model
cp /path/to/your/venom.pt models/venom.pt

# Set your Gemini API key
export GEMINI_API_KEY="your-key-here"

# Start the FastAPI dev server
python main.py
# → API available at http://localhost:7860
# → Docs at         http://localhost:7860/docs
```

---

### 2 — Frontend

```bash
cd frontend
npm install
npm run dev
# → App at http://localhost:5173
# → /health and /predict are proxied to :7860 automatically
```

---

## Configuration

All settings are in **`backend/config.py`**. Change them without touching
any other file:

| Setting | Default | Description |
|---|---|---|
| `MODEL_ARCH` | `"efficientnet_b0"` | Architecture: `efficientnet_b0/b2`, `resnet50/18` |
| `IMAGE_SIZE` | `(128, 128)` | Input resolution — must match training |
| `APPLY_NORMALIZATION` | `True` | Toggle ImageNet normalisation |
| `NORMALIZE_MEAN/STD` | ImageNet | Override if trained with custom stats |
| `CLASS_LABELS` | `{0: "Venomous", 1: "Non-Venomous"}` | Class index → label map |
| `VENOMOUS_CLASS_INDEX` | `0` | Which class index is the venomous one |
| `CONFIDENCE_THRESHOLD` | `0.65` | Below this → low-confidence warning |
| `GEMINI_MODEL` | `"gemini-1.5-flash"` | Gemini model for enrichment |
| `MAX_FILE_SIZE_MB` | `10` | Upload size limit |

---

## Training Notes

- Dataset: [Snake Dataset India (Kaggle)](https://www.kaggle.com/datasets/adityasharma01/snake-dataset-india)
  - 1060 venomous / 715 non-venomous training images
- Recommended base: **EfficientNet-B0** from `timm` or `torchvision`
- Train at `128×128` with ImageNet normalisation
- Save weights as a state dict:
  ```python
  torch.save(model.state_dict(), "venom.pt")
  ```
  Then drop `venom.pt` into `backend/models/`.

---

## Deployment — Hugging Face Spaces (CI/CD)

### One-time setup

1. Create a Space at [huggingface.co/new-space](https://huggingface.co/new-space)
   - SDK: **Docker**
   - Visibility: Public (free tier)

2. Add GitHub Secrets (repo → Settings → Secrets → Actions):
   | Secret | Value |
   |--------|-------|
   | `HF_TOKEN` | Your HF write token from [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) |
   | `HF_SPACE` | `yourusername/your-space-name` |

3. Add your **Gemini API key** as an HF Space Secret:
   - Space → Settings → Repository secrets → Add `GEMINI_API_KEY`

4. Upload `venom.pt` to your Space via the HF web UI or:
   ```bash
   pip install huggingface_hub
   huggingface-cli upload yourusername/your-space-name \
       backend/models/venom.pt backend/models/venom.pt
   ```

### Auto-deploy

Every `git push` to `main` triggers `.github/workflows/deploy.yml`,
which force-pushes your code to the HF Space. The Space rebuilds its
Docker container automatically — usually takes 2–4 minutes.

---

## API Reference

### `GET /health`
Returns model status. Check this first.

```json
{
  "status": "ok",
  "model_ready": true,
  "model_error": null,
  "model_arch": "efficientnet_b0",
  "image_size": [128, 128]
}
```

### `POST /predict`
Upload an image → get classification + enrichment.

```bash
curl -X POST http://localhost:7860/predict \
  -F "file=@snake.jpg"
```

```json
{
  "prediction": {
    "label": "Venomous",
    "class_index": 0,
    "confidence": 0.9312,
    "is_venomous": true,
    "low_confidence": false
  },
  "enrichment": {
    "species_guess": "Indian Cobra",
    "fun_fact": "The Indian cobra can spread its hood up to 30 cm wide.",
    "iucn_status": "LC",
    "conservation_note": "Listed as Least Concern but declining due to habitat loss.",
    "first_aid_tip": "Keep the victim still, immobilise the limb, seek emergency care immediately.",
    "danger_level": "Extreme"
  },
  "meta": {
    "filename": "snake.jpg",
    "image_size_px": [128, 128],
    "model_arch": "efficientnet_b0"
  }
}
```

---

## Edge Cases Handled

| Scenario | Behaviour |
|---|---|
| `venom.pt` missing | `/health` reports error; `/predict` returns 503 with clear message |
| Wrong file type | 415 Unsupported Media Type |
| File > 10 MB | 413 Request Entity Too Large |
| Corrupt image | 422 Unprocessable Entity |
| Gemini API down | Falls back to placeholder enrichment silently |
| Low model confidence | Yellow warning shown in UI |
| Frontend not built | 404 with instructions to run `npm run build` |
