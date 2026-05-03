# =============================================================================
# classifier.py — PyTorch model loader and image inference
# =============================================================================

import logging
from pathlib import Path

import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image
import os
import shutil
from huggingface_hub import hf_hub_download
import snake_classifier_backend.config as config

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_model(arch: str, num_classes: int) -> nn.Module:
    """
    Instantiate a model backbone by name and replace the final classifier
    head to match num_classes.  Add new architectures here as needed.
    """
    arch = arch.lower()

    if arch == "efficientnet_b0":
        model = models.efficientnet_b0(weights=None)
        model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)

    elif arch == "efficientnet_b2":
        model = models.efficientnet_b2(weights=None)
        model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)

    elif arch == "resnet50":
        model = models.resnet50(weights=None)
        model.fc = nn.Linear(model.fc.in_features, num_classes)

    elif arch == "resnet18":
        model = models.resnet18(weights=None)
        model.fc = nn.Linear(model.fc.in_features, num_classes)

    else:
        raise ValueError(
            f"Unknown MODEL_ARCH '{arch}'. "
            "Supported: efficientnet_b0, efficientnet_b2, resnet50, resnet18"
        )

    return model


def _build_transform() -> transforms.Compose:
    """Build the inference transform pipeline from config values."""
    steps = [
        transforms.Resize(config.IMAGE_SIZE),
        transforms.ToTensor(),
    ]
    if config.APPLY_NORMALIZATION:
        steps.append(
            transforms.Normalize(
                mean=config.NORMALIZE_MEAN,
                std=config.NORMALIZE_STD,
            )
        )
    return transforms.Compose(steps)


# ---------------------------------------------------------------------------
# Classifier class
# ---------------------------------------------------------------------------

class SnakeClassifier:
    """
    Loads venom.pt once at startup and exposes a predict() method.
    Thread-safe for read-only inference.
    """

    def __init__(self):
        self._model: nn.Module | None = None
        self._transform = _build_transform()
        self._device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self._loaded = False
        self._load_error: str | None = None

        self._try_load()

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _try_load(self) -> None:
        model_path: Path = config.MODEL_PATH
        
        if not model_path.exists() and config.MODEL_HF_ID:
            token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_HUB_TOKEN")
            try:
                hf_file = hf_hub_download(repo_id=config.MODEL_HF_ID, filename=config.MODEL_FILENAME, token=token)
                model_path.parent.mkdir(parent=True, exist_ok=True)
                shutil.copy(hf_file,model_path)
                logger.infor("Downloaded model from HF repo %s to %s", config.MODEL_HF_ID, model_path)
            except Exception as exc:
                logger.warning("Could not download model from HF repo %s:%s", config.MODEL_HF_ID, exc)

        
        if not model_path.exists():
            msg = f"Model file not found at '{model_path}'. Place venom.pt in backend/models/."
            logger.error(msg)
            self._load_error = msg
            return

        try:
            model = _build_model(config.MODEL_ARCH, config.NUM_CLASSES)
            state_dict = torch.load(model_path, map_location=self._device)

            # Support both raw state_dict and checkpoint dicts
            if isinstance(state_dict, dict) and "model_state_dict" in state_dict:
                state_dict = state_dict["model_state_dict"]

            model.load_state_dict(state_dict)
            model.to(self._device)
            model.eval()

            self._model = model
            self._loaded = True
            logger.info(
                "Model '%s' loaded from '%s' on %s.",
                config.MODEL_ARCH, model_path, self._device,
            )

        except Exception as exc:
            msg = f"Failed to load model: {exc}"
            logger.exception(msg)
            self._load_error = msg

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    @property
    def is_ready(self) -> bool:
        return self._loaded

    @property
    def load_error(self) -> str | None:
        return self._load_error

    def predict(self, image: Image.Image) -> dict:
        """
        Run inference on a PIL Image.

        Returns:
            {
                "label":       str,   e.g. "Venomous"
                "class_index": int,   raw class index
                "confidence":  float, 0–1
                "is_venomous": bool,
                "low_confidence": bool,
            }

        Raises:
            RuntimeError if the model is not loaded.
        """
        if not self._loaded or self._model is None:
            raise RuntimeError(self._load_error or "Model is not loaded.")

        # Convert to RGB (handles RGBA / grayscale uploads)
        image = image.convert("RGB")
        tensor = self._transform(image).unsqueeze(0).to(self._device)  # (1, C, H, W)

        with torch.no_grad():
            logits = self._model(tensor)                          # (1, num_classes)
            probs  = torch.softmax(logits, dim=1)[0]              # (num_classes,)

        class_index = int(probs.argmax().item())
        confidence  = float(probs[class_index].item())
        label       = config.CLASS_LABELS.get(class_index, f"Class {class_index}")
        is_venomous = class_index == config.VENOMOUS_CLASS_INDEX

        return {
            "label":          label,
            "class_index":    class_index,
            "confidence":     round(confidence, 4),
            "is_venomous":    is_venomous,
            "low_confidence": confidence < config.CONFIDENCE_THRESHOLD,
        }


# ---------------------------------------------------------------------------
# Module-level singleton — imported by main.py
# ---------------------------------------------------------------------------
classifier = SnakeClassifier()
