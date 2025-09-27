#!/usr/bin/env python3

print("Testing imports...")

try:
    import scripts.weed_detection as weed
    print("✓ Weed detection import successful")
except Exception as e:
    print(f"✗ Weed detection import failed: {e}")

try:
    import scripts.disease_detection as disease
    print("✓ Disease detection import successful")
except Exception as e:
    print(f"✗ Disease detection import failed: {e}")

try:
    from PIL import Image
    print("✓ PIL import successful")
except Exception as e:
    print(f"✗ PIL import failed: {e}")

print("Import tests complete")
