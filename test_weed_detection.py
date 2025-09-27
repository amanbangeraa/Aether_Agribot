#!/usr/bin/env python3
"""
Test script for weed detection functionality
"""

import os
import sys
from PIL import Image
import io
import base64

# Add the project root to the Python path
sys.path.append('/mnt/wwn-0x50014ee2698c2192/weeed/Aether_Agribot')

def test_weed_detection():
    try:
        print("Testing weed detection module...")
        
        # Test imports
        from scripts import weed_detection
        from scripts import utils
        print("✓ Imports successful")
        
        # Check model file exists
        model_path = weed_detection.MODEL_PATH
        if os.path.exists(model_path):
            print(f"✓ Model file exists: {model_path}")
        else:
            print(f"✗ Model file missing: {model_path}")
            return False
        
        # Try to load model
        try:
            model = weed_detection.get_model()
            print("✓ Model loaded successfully")
        except Exception as e:
            print(f"✗ Model loading failed: {str(e)}")
            return False
        
        # Create a test image (simple RGB image)
        test_image = Image.new('RGB', (224, 224), color='green')
        print("✓ Test image created")
        
        # Test prediction
        try:
            result = weed_detection.predict_pil(test_image)
            print(f"✓ Prediction successful: {result}")
            return True
        except Exception as e:
            print(f"✗ Prediction failed: {str(e)}")
            return False
            
    except Exception as e:
        print(f"✗ Test failed with error: {str(e)}")
        return False

def test_flask_weed_detection():
    """Test the Flask route specifically"""
    try:
        print("\nTesting Flask weed detection route...")
        
        # Import Flask app
        import app
        
        # Create test client
        with app.app.test_client() as client:
            print("✓ Flask test client created")
            
            # Test the weed detection page loads
            response = client.get('/weed-detection')
            if response.status_code == 200:
                print("✓ Weed detection page loads successfully")
            else:
                print(f"✗ Weed detection page failed: {response.status_code}")
                return False
            
            # Create a test image file
            test_image = Image.new('RGB', (224, 224), color='green')
            img_bytes = io.BytesIO()
            test_image.save(img_bytes, format='JPEG')
            img_bytes.seek(0)
            
            # Test the API endpoint
            response = client.post('/api/weed-detection', 
                                 data={'file': (img_bytes, 'test.jpg')},
                                 content_type='multipart/form-data')
            
            if response.status_code == 200:
                data = response.get_json()
                if data and data.get('success'):
                    print(f"✓ API endpoint working: {data}")
                    return True
                else:
                    print(f"✗ API returned error: {data}")
                    return False
            else:
                print(f"✗ API endpoint failed: {response.status_code}")
                print(f"Response: {response.get_data()}")
                return False
                
    except Exception as e:
        print(f"✗ Flask test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== Weed Detection Test Suite ===\n")
    
    # Test 1: Basic weed detection functionality
    test1_passed = test_weed_detection()
    
    # Test 2: Flask integration
    test2_passed = test_flask_weed_detection()
    
    print(f"\n=== Test Results ===")
    print(f"Basic functionality: {'✓ PASSED' if test1_passed else '✗ FAILED'}")
    print(f"Flask integration: {'✓ PASSED' if test2_passed else '✗ FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 All tests passed! Weed detection should work properly.")
    else:
        print("\n❌ Some tests failed. Check the errors above.")
