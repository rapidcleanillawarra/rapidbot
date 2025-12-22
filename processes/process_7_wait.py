# Process 7: Wait - cycle through tabs and detect JSON download text via OCR
import time
import os
import pyautogui
import pytesseract
from PIL import ImageGrab
from .base import BaseProcess
from config import ACTIVE_TAB_IMAGE, IMAGE_CONFIDENCE
from utils.image_scanner import filter_duplicate_boxes
from utils.audio import beep_success, beep_error

# Configure Tesseract path for Windows
TESSERACT_PATHS = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    r"C:\Users\{}\AppData\Local\Programs\Tesseract-OCR\tesseract.exe".format(os.getenv("USERNAME", "")),
]

for path in TESSERACT_PATHS:
    if os.path.exists(path):
        pytesseract.pytesseract.tesseract_cmd = path
        print(f"Tesseract found at: {path}", flush=True)
        break


class WaitProcess(BaseProcess):
    """Process 7: Wait - cycle through tabs and detect target text via OCR"""
    
    PROCESS_NUMBER = 7
    PROCESS_NAME = "WAIT"
    
    # Target text patterns to search for
    TARGET_PATTERNS = ["Download the JSON", "_automate.json"]
    
    def run(self) -> bool:
        """Cycle through tabs and detect target text via OCR."""
        try:
            self.play_beep()
            self.log_start()
            
            # Step 1: Get current active tabs count from GUI
            try:
                allowed_tabs = int(self.app.active_tabs_var.get())
            except ValueError:
                allowed_tabs = 2
            
            print(f"Allowed tabs from GUI: {allowed_tabs}", flush=True)
            self.update_log(f"Scanning up to {allowed_tabs} tab(s)...")
            
            # Step 2: Scan for tab locations
            tab_matches = self._scan_for_tabs()
            
            if not tab_matches:
                print("No tabs found on screen", flush=True)
                self.update_log("✗ No active tabs found")
                beep_error()
                self.log_failed()
                return False
            
            # Limit to allowed number of tabs
            tabs_to_check = min(len(tab_matches), allowed_tabs)
            print(f"Will check {tabs_to_check} tab(s)", flush=True)
            
            # Step 3: Cycle through each tab and check for target text
            for i, tab in enumerate(tab_matches[:tabs_to_check], 1):
                print(f"\n--- Checking tab {i}/{tabs_to_check} ---", flush=True)
                self.update_log(f"Checking tab {i}/{tabs_to_check}...")
                
                if self._check_tab_for_text(tab, i):
                    print(f"\n✓ Found target text in tab {i}!", flush=True)
                    self.update_log(f"✓ Found target text in tab {i}!")
                    beep_success()
                    self.log_complete()
                    return True
            
            # No target text found in any tab
            print("\n✗ Target text not found in any tab", flush=True)
            self.update_log("✗ Target text not found")
            beep_error()
            self.log_failed()
            return False
            
        except Exception as e:
            print(f"Process 7 exception: {e}", flush=True)
            self.update_log(f"✗ Wait process failed:\n{str(e)}")
            beep_error()
            self.log_failed()
            return False
    
    def _scan_for_tabs(self):
        """Scan screen for all tab instances."""
        print("Scanning for active tabs...", flush=True)
        
        try:
            all_matches = list(pyautogui.locateAllOnScreen(
                ACTIVE_TAB_IMAGE, 
                confidence=IMAGE_CONFIDENCE
            ))
            
            # Filter duplicates
            unique_matches = filter_duplicate_boxes(all_matches, threshold=0.5)
            
            # Sort by left position (leftmost first)
            sorted_matches = sorted(unique_matches, key=lambda m: m.left)
            
            print(f"Found {len(sorted_matches)} unique tab(s)", flush=True)
            return sorted_matches
            
        except Exception as e:
            print(f"Tab scan error: {e}", flush=True)
            return []
    
    def _check_tab_for_text(self, tab_box, tab_index: int) -> bool:
        """Click on a tab and check for target text via OCR."""
        # Click on tab to activate it
        center_x = tab_box.left + tab_box.width // 2
        center_y = tab_box.top + tab_box.height // 2
        
        print(f"  Clicking tab at ({center_x}, {center_y})", flush=True)
        pyautogui.click(center_x, center_y)
        
        # Wait for page to load
        time.sleep(1.5)
        
        # Capture screen for OCR
        print("  Capturing screen for OCR...", flush=True)
        screenshot = ImageGrab.grab()
        
        # Run OCR on the screenshot
        print("  Running OCR...", flush=True)
        try:
            text = pytesseract.image_to_string(screenshot)
            
            # Search for target patterns
            for pattern in self.TARGET_PATTERNS:
                if pattern.lower() in text.lower():
                    print(f"  ✓ Found pattern: '{pattern}'", flush=True)
                    return True
            
            print(f"  Target patterns not found in tab {tab_index}", flush=True)
            return False
            
        except Exception as e:
            print(f"  OCR error: {e}", flush=True)
            return False
