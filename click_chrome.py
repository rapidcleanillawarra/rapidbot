import webbrowser
import time
import os

try:
    import win32gui
    import win32con
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False
    print("Warning: pywin32 not installed. Window activation will be limited.")

try:
    import pyautogui
    HAS_PYAUTOGUI = True
    # Set pyautogui safety settings
    pyautogui.FAILSAFE = True  # Move mouse to corner to abort
    pyautogui.PAUSE = 0.5  # Pause between actions
except ImportError:
    HAS_PYAUTOGUI = False
    print("Warning: pyautogui not installed. Image recognition will not work.")
    print("Install with: pip install pyautogui")

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CHROME_IMAGE = os.path.join(SCRIPT_DIR, "chrome_icon.png")
INPUT_FIELD_IMAGE = os.path.join(SCRIPT_DIR, "input_field.png")

# ChatGPT URL to navigate to
CHATGPT_URL = "https://chatgpt.com/g/g-69153998509481918156154b9ed0e00e-product-description-finder"

def is_chrome_active():
    """Check if the active window is Chrome"""
    if not HAS_WIN32:
        return False
    
    try:
        # Get the currently active window
        active_window = win32gui.GetForegroundWindow()
        window_text = win32gui.GetWindowText(active_window)
        
        # Common Chrome window title patterns
        chrome_patterns = ["Google Chrome", "Chrome"]
        
        # Check if any pattern matches
        for pattern in chrome_patterns:
            if pattern in window_text:
                print(f"Chrome is active! Window title: {window_text}")
                return True
        
        print(f"Chrome is not active. Active window: {window_text}")
        return False
        
    except Exception as e:
        print(f"Error checking active window: {e}")
        return False

def find_and_click_image(image_path=None, confidence=0.8, max_retries=5, wait_between_retries=1):
    """
    Find and click on an image on the screen
    
    Args:
        image_path: Path to the image to find (defaults to INPUT_FIELD_IMAGE)
        confidence: Confidence level for image matching (0.0 to 1.0)
        max_retries: Maximum number of attempts to find the image
        wait_between_retries: Seconds to wait between retry attempts
    
    Returns:
        True if image was found and clicked, False otherwise
    """
    if not HAS_PYAUTOGUI:
        print("Error: pyautogui is not installed!")
        return False
    
    if image_path is None:
        image_path = INPUT_FIELD_IMAGE
    
    if not os.path.exists(image_path):
        print(f"Error: Image not found at {image_path}")
        return False
    
    print(f"Searching for image: {os.path.basename(image_path)}")
    print(f"Confidence: {confidence}, Max retries: {max_retries}")
    
    for attempt in range(1, max_retries + 1):
        try:
            print(f"Attempt {attempt}/{max_retries}...")
            
            # Try to locate the image on screen
            location = pyautogui.locateOnScreen(image_path, confidence=confidence)
            
            if location:
                # Get the center of the found image
                center_x, center_y = pyautogui.center(location)
                print(f"✓ Image found at coordinates: ({center_x}, {center_y})")
                
                # Move mouse to the location and click
                pyautogui.moveTo(center_x, center_y, duration=0.5)
                time.sleep(0.2)
                pyautogui.click()
                
                print("✓ Clicked on the image successfully!")
                return True
            else:
                print(f"Image not found on attempt {attempt}")
                
        except pyautogui.ImageNotFoundException:
            print(f"Image not found on attempt {attempt}")
        except Exception as e:
            print(f"Error on attempt {attempt}: {e}")
        
        # Wait before retrying (except on last attempt)
        if attempt < max_retries:
            print(f"Waiting {wait_between_retries} seconds before retry...")
            time.sleep(wait_between_retries)
    
    print(f"✗ Failed to find image after {max_retries} attempts")
    return False


def bring_chrome_to_front():
    """Bring Chrome window to the front"""
    if not HAS_WIN32:
        return False
    
    try:
        # Common Chrome window title patterns
        chrome_patterns = ["Google Chrome", "Chrome"]
        
        def enum_windows_callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                window_text = win32gui.GetWindowText(hwnd)
                for pattern in chrome_patterns:
                    if pattern in window_text:
                        windows.append(hwnd)
            return True
        
        windows = []
        win32gui.EnumWindows(enum_windows_callback, windows)
        
        if windows:
            # Get the first Chrome window found
            chrome_window = windows[0]
            
            # Restore if minimized
            if win32gui.IsIconic(chrome_window):
                win32gui.ShowWindow(chrome_window, win32con.SW_RESTORE)
            
            # Bring to front
            win32gui.SetForegroundWindow(chrome_window)
            print("Chrome window brought to front!")
            return True
        else:
            print("Chrome window not found")
            return False
            
    except Exception as e:
        print(f"Error bringing Chrome to front: {e}")
        return False

def find_and_click_chrome():
    """Open browser, navigate to ChatGPT, and click on 'Ask Anything' button"""
    
    print("Opening browser...")
    
    try:
        # Open URL in default browser
        # This will use Chrome if it's your default browser
        webbrowser.open(CHATGPT_URL)
        
        print("Browser launched and navigated to ChatGPT successfully!")
        print(f"URL: {CHATGPT_URL}")
        
        # Wait a moment for the browser to open
        time.sleep(1.5)
        
        # Try to bring Chrome to front
        bring_chrome_to_front()
        
        # Wait for page to load
        print("\nWaiting for page to load...")
        time.sleep(3)
        
        # Now try to find and click the input field
        print("\n" + "="*40)
        print("Searching for input field...")
        print("="*40)
        
        click_result = find_and_click_image()
        
        if click_result:
            print("\n✓ Successfully clicked input field!")
        else:
            print("\n✗ Could not find input field")
            print("Tip: Make sure the ChatGPT page is fully loaded and visible")
        
        return True
            
    except Exception as e:
        print(f"Error launching browser: {e}")
        return False

if __name__ == "__main__":
    print("=" * 40)
    print("Chrome Clicker Script")
    print("=" * 40)
    
    # Check if the Chrome icon image exists
    if not os.path.exists(CHROME_IMAGE):
        print(f"\nERROR: Chrome icon image not found!")
        print(f"Expected location: {CHROME_IMAGE}")
        print("\nTo create the icon image:")
        print("1. Take a screenshot of your Chrome icon")
        print("2. Crop just the icon")
        print("3. Save it as 'chrome_icon.png' in the same folder as this script")
        exit(1)
    
    find_and_click_chrome()
