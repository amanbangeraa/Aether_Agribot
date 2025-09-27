
import torch
from torchvision import models
from PIL import Image
import os
import io

from scripts.utils import get_transform, DEVICE, softmax_probs

# Model path and labels
MODEL_PATH = 'models/disease_detection.pt'

# Dynamically load class labels from training folder
DATA_DIR = 'datasets/diseases/train'
LABELS = sorted([
    d for d in os.listdir(DATA_DIR)
    if os.path.isdir(os.path.join(DATA_DIR, d))
])

# Load and prepare the model
def load_model():
    model = models.mobilenet_v2(pretrained=False)
    num_ftrs = model.classifier[1].in_features
    model.classifier[1] = torch.nn.Linear(num_ftrs, len(LABELS))
    model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
    model.to(DEVICE)
    model.eval()
    return model

# Cache the model instance
_model = None
def get_model():
    global _model
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model file not found: {MODEL_PATH}. Train and save the model first.")
        _model = load_model()
    return _model

# Predict from a PIL image
def predict_pil(img_pil):
    model = get_model()
    transform = get_transform()
    img_t = transform(img_pil).unsqueeze(0).to(DEVICE)
    with torch.no_grad():
        out = model(img_t)
    probs = softmax_probs(out)
    cls = int(probs.argmax())
    return {'label': LABELS[cls], 'prob': float(probs[0, cls])}

# Main demo function for dashboard
def run_demo(uploaded_file):
    """
    Main function to process an uploaded file and return disease prediction results.
    """
    try:
        # Handle different input types
        if hasattr(uploaded_file, 'read'):  # File-like object
            img = Image.open(uploaded_file).convert("RGB")
        elif isinstance(uploaded_file, str) and os.path.exists(uploaded_file):
            img = Image.open(uploaded_file).convert("RGB")
        elif isinstance(uploaded_file, (bytes, bytearray)):
            img = Image.open(io.BytesIO(uploaded_file)).convert("RGB")
        else:
            raise ValueError("Unsupported input type for uploaded_file.")

        # Proceed with disease prediction
        return predict_pil(img)

    except Exception as e:
        raise ValueError(f"Failed to process image: {str(e)}")

