#!/usr/bin/env python3
"""
Comprehensive debugging for weed detection
"""
import os
import sys
import traceback
from PIL import Image
import torch
from torchvision import models, transforms
import io

def test_basic_pytorch():
    """Test basic PyTorch functionality"""
    print("=== Testing PyTorch ===")
    try:
        print(f"PyTorch version: {torch.__version__}")
        print(f"CUDA available: {torch.cuda.is_available()}")
        
        # Test basic tensor operations
        x = torch.randn(1, 3, 224, 224)
        print(f"✓ Created test tensor: {x.shape}")
        return True
    except Exception as e:
        print(f"✗ PyTorch test failed: {e}")
        return False

def test_model_loading():
    """Test model loading step by step"""
    print("\n=== Testing Model Loading ===")
    try:
        model_path = 'models/weed_detection.pt'
        
        # Check file exists
        if not os.path.exists(model_path):
            print(f"✗ Model file doesn't exist: {model_path}")
            return False
        print(f"✓ Model file exists: {model_path}")
        
        # Try to load the model state dict
        try:
            state_dict = torch.load(model_path, map_location='cpu')
            print("✓ Model state dict loaded")
            print(f"  Keys in state dict: {len(state_dict.keys())} keys")
            print(f"  First few keys: {list(state_dict.keys())[:3]}")
        except Exception as e:
            print(f"✗ Failed to load state dict: {e}")
            traceback.print_exc()
            return False
        
        # Create MobileNetV2 model
        try:
            model = models.mobilenet_v2(weights=None)  # Updated syntax
            num_ftrs = model.classifier[1].in_features
            model.classifier[1] = torch.nn.Linear(num_ftrs, 2)
            print("✓ MobileNetV2 model created")
        except Exception as e:
            print(f"✗ Failed to create model: {e}")
            traceback.print_exc()
            return False
        
        # Load state dict into model
        try:
            model.load_state_dict(state_dict)
            model.eval()
            print("✓ Model loaded and set to eval mode")
        except Exception as e:
            print(f"✗ Failed to load state dict into model: {e}")
            traceback.print_exc()
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Model loading test failed: {e}")
        traceback.print_exc()
        return False

def test_prediction():
    """Test the full prediction pipeline"""
    print("\n=== Testing Prediction Pipeline ===")
    try:
        # Load model
        model_path = 'models/weed_detection.pt'
        state_dict = torch.load(model_path, map_location='cpu')
        
        model = models.mobilenet_v2(weights=None)
        num_ftrs = model.classifier[1].in_features
        model.classifier[1] = torch.nn.Linear(num_ftrs, 2)
        model.load_state_dict(state_dict)
        model.eval()
        
        # Create test image
        test_image = Image.new('RGB', (224, 224), color=(0, 255, 0))  # Green image
        print("✓ Test image created")
        
        # Create transforms
        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                               std=[0.229, 0.224, 0.225])
        ])
        print("✓ Transforms created")
        
        # Apply transforms
        img_tensor = transform(test_image).unsqueeze(0)
        print(f"✓ Image transformed to tensor: {img_tensor.shape}")
        
        # Run prediction
        with torch.no_grad():
            outputs = model(img_tensor)
            probs = torch.nn.functional.softmax(outputs, dim=1)
            prediction = probs.argmax().item()
            confidence = probs.max().item()
        
        labels = ['rice', 'weed']
        result = {
            'label': labels[prediction],
            'confidence': confidence,
            'raw_outputs': outputs.numpy().tolist()
        }
        
        print(f"✓ Prediction successful: {result}")
        return True
        
    except Exception as e:
        print(f"✗ Prediction test failed: {e}")
        traceback.print_exc()
        return False

def test_weed_detection_module():
    """Test the actual weed detection module"""
    print("\n=== Testing Weed Detection Module ===")
    try:
        sys.path.append('.')
        from scripts import weed_detection
        
        # Test model loading
        model = weed_detection.get_model()
        print("✓ Weed detection model loaded")
        
        # Test prediction
        test_image = Image.new('RGB', (224, 224), color=(0, 255, 0))
        result = weed_detection.predict_pil(test_image)
        print(f"✓ Weed detection prediction: {result}")
        
        return True
        
    except Exception as e:
        print(f"✗ Weed detection module test failed: {e}")
        traceback.print_exc()
        return False

def main():
    print("=== Weed Detection Comprehensive Debug ===\n")
    
    tests = [
        ("PyTorch Basic", test_basic_pytorch),
        ("Model Loading", test_model_loading),
        ("Prediction Pipeline", test_prediction),
        ("Weed Detection Module", test_weed_detection_module)
    ]
    
    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"✗ {name} crashed: {e}")
            results[name] = False
    
    print("\n=== SUMMARY ===")
    all_passed = True
    for name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{name}: {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All tests passed! The weed detection should work.")
    else:
        print("\n❌ Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main()
