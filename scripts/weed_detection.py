import torch
from torchvision import models
from PIL import Image
import os
import io

from scripts.utils import get_transform, DEVICE, softmax_probs

# Model path and labels
MODEL_PATH = 'models/weed_detection.pt'
LABELS = ['rice', 'weed']

# Load and prepare the model
def load_model():
    model = models.mobilenet_v2(weights=None)  # Updated syntax
    num_ftrs = model.classifier[1].in_features
    model.classifier[1] = torch.nn.Linear(num_ftrs, 2)  # 2 classes: crop and weed
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
def run_demo(uploaded_file=None):
    """
    Accepts a Streamlit uploaded file object, file path, or raw bytes.
    Returns prediction result as a dictionary.
    """
    if uploaded_file is None:
        return "Upload an image to detect crop vs weed."

    try:
        # Streamlit uploaded file (file-like object)
        if hasattr(uploaded_file, "read"):
            uploaded_file.seek(0)  # Ensure we're at the start of the file
            img = Image.open(uploaded_file).convert("RGB")

        # File path
        elif isinstance(uploaded_file, str) and os.path.exists(uploaded_file):
            img = Image.open(uploaded_file).convert("RGB")

        # Raw bytes
        elif isinstance(uploaded_file, (bytes, bytearray)):
            img = Image.open(io.BytesIO(uploaded_file)).convert("RGB")

        else:
            raise ValueError("Unsupported input type for uploaded_file.")

        return predict_pil(img)

    except Exception as e:
        raise ValueError(f"Failed to process image: {str(e)}")
