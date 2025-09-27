#!/usr/bin/env python3
"""Simple test to check if Flask server is working"""
import requests
import sys
import time

def test_server():
    base_url = "http://localhost:5000"
    
    try:
        # Test home page
        print("Testing Flask server...")
        response = requests.get(base_url, timeout=5)
        if response.status_code == 200:
            print("✓ Flask server is running!")
            print(f"✓ Home page accessible: {response.status_code}")
        else:
            print(f"✗ Home page error: {response.status_code}")
            return False
            
        # Test weed detection page
        response = requests.get(f"{base_url}/weed-detection", timeout=5)
        if response.status_code == 200:
            print("✓ Weed detection page accessible!")
        else:
            print(f"✗ Weed detection page error: {response.status_code}")
            return False
            
        return True
        
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to Flask server. Is it running?")
        return False
    except Exception as e:
        print(f"✗ Error testing server: {e}")
        return False

if __name__ == "__main__":
    if test_server():
        print("\n🎉 Flask server is working correctly!")
        print("Try accessing: http://localhost:5000/weed-detection")
    else:
        print("\n❌ Flask server is not responding properly.")
        print("Make sure to start the server with:")
        print("python app.py")
