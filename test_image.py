"""Quick test to see if the image can be found on screen"""
import pyautogui
import os

# Get the image path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FIELD_IMAGE = os.path.join(SCRIPT_DIR, "input_field.png")

print("Testing image recognition...")
print(f"Looking for: {INPUT_FIELD_IMAGE}")
print(f"Image exists: {os.path.exists(INPUT_FIELD_IMAGE)}")
print("\nMake sure ChatGPT is open and visible on your screen!")
print("Searching in 3 seconds...")

import time
time.sleep(3)

# Try different confidence levels
confidence_levels = [0.9, 0.8, 0.7, 0.6]

for confidence in confidence_levels:
    print(f"\nTrying confidence: {confidence}")
    try:
        location = pyautogui.locateOnScreen(INPUT_FIELD_IMAGE, confidence=confidence)
        if location:
            center_x, center_y = pyautogui.center(location)
            print(f"✓ FOUND at ({center_x}, {center_y}) with confidence {confidence}")
            print(f"  Location: {location}")
            break
        else:
            print(f"✗ Not found with confidence {confidence}")
    except Exception as e:
        print(f"✗ Error with confidence {confidence}: {e}")

print("\nTest complete!")
