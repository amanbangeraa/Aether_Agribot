#!/usr/bin/env python3
"""
Simple test for upload functionality
"""
import sys
sys.path.append('.')

import requests
import io
from PIL import Image

def test_upload_endpoint():
    """Test the upload functionality with a real HTTP request"""
    print("=== Testing Upload Functionality ===\n")
    
    # Create a test image
    test_image = Image.new('RGB', (224, 224), color=(0, 255, 0))  # Green image
    
    # Save to bytes
    img_buffer = io.BytesIO()
    test_image.save(img_buffer, format='JPEG')
    img_buffer.seek(0)
    
    try:
        # Test with the test server (port 5001)
        print("Testing upload to test server (port 5001)...")
        files = {'file': ('test_weed.jpg', img_buffer, 'image/jpeg')}
        response = requests.post('http://localhost:5001/api/test-weed-detection', files=files, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Upload successful: {data}")
            if data.get('success'):
                print(f"  - Label: {data['label']}")
                print(f"  - Confidence: {data['confidence']:.2%}")
            return True
        else:
            print(f"✗ Upload failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to test server. Make sure it's running on port 5001")
        return False
    except Exception as e:
        print(f"✗ Upload test failed: {e}")
        return False

def test_main_app_upload():
    """Test the main app upload (if running on port 5000)"""
    print("\nTesting upload to main app (port 5000)...")
    
    # Create a test image
    test_image = Image.new('RGB', (224, 224), color=(255, 0, 0))  # Red image
    
    # Save to bytes  
    img_buffer = io.BytesIO()
    test_image.save(img_buffer, format='JPEG')
    img_buffer.seek(0)
    
    try:
        files = {'file': ('test_weed.jpg', img_buffer, 'image/jpeg')}
        response = requests.post('http://localhost:5000/api/weed-detection', files=files, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Main app upload successful: {data}")
            if data.get('success'):
                print(f"  - Label: {data['label']}")
                print(f"  - Confidence: {data['confidence']:.2%}")
            return True
        else:
            print(f"✗ Main app upload failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to main app. It may not be running on port 5000")
        return False
    except Exception as e:
        print(f"✗ Main app upload test failed: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing Upload Functionality\n")
    
    test1_passed = test_upload_endpoint()
    test2_passed = test_main_app_upload()
    
    print(f"\n=== Results ===")
    print(f"Test Server Upload: {'✓ PASSED' if test1_passed else '✗ FAILED'}")  
    print(f"Main App Upload: {'✓ PASSED' if test2_passed else '✗ FAILED'}")
    
    if test1_passed:
        print(f"\n✅ Upload functionality is working!")
        print(f"🌐 You can test it manually at: http://localhost:5001/test-weed")
    
    if test2_passed:
        print(f"🌐 Main app is also working at: http://localhost:5000/weed-detection")
    elif not test1_passed and not test2_passed:
        print(f"\n❌ Upload functionality needs debugging")
    else:
        print(f"\n⚠️ Start the main app with: python app.py")
