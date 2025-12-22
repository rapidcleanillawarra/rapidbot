"""Test script to verify image scanning works correctly"""
import pyautogui
import os
import time

def test_image_scan(image_name, confidence=0.8):
    """Test if an image can be found on screen"""
    image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), image_name)
    
    print(f"\n=== Testing: {image_name} ===")
    print(f"Path: {image_path}")
    print(f"Exists: {os.path.exists(image_path)}")
    
    if not os.path.exists(image_path):
        print("✗ File not found!")
        return False
    
    print(f"Confidence: {confidence}")
    print("Scanning screen...")
    
    try:
        location = pyautogui.locateOnScreen(image_path, confidence=confidence)
        
        if location:
            print(f"✓ FOUND at: {location}")
            center = pyautogui.center(location)
            print(f"  Center: ({center.x}, {center.y})")
            return True
        else:
            print("✗ NOT FOUND on screen")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("IMAGE SCAN TEST")
    print("=" * 50)
    
    # Give user time to prepare the screen
    print("\nYou have 3 seconds to prepare the screen...")
    time.sleep(3)
    
    # Test the submission indicators
    print("\n--- Testing submission_indicator_stop.png ---")
    test_image_scan("submission_indicator_stop.png")
    
    print("\n--- Testing submission_indicator_answer_now.png ---")
    test_image_scan("submission_indicator_answer_now.png")
    
    print("\n--- Testing input_field_ready.png ---")
    test_image_scan("input_field_ready.png")
    
    print("\n--- Testing input_field.png ---")
    test_image_scan("input_field.png")
    
    print("\n" + "=" * 50)
    print("TEST COMPLETE")
    print("=" * 50)
