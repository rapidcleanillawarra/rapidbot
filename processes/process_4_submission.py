# Process 4: Submission - open browser, paste, and submit
import time
import pyautogui
import os
from .base import BaseProcess
from click_chrome import find_and_click_chrome
from config import INPUT_FIELD_IMAGE, INPUT_FIELD_READY_IMAGE, IMAGE_CONFIDENCE


class SubmissionProcess(BaseProcess):
    """Process 4: Submission - open browser, navigate to ChatGPT, paste and submit"""
    
    PROCESS_NUMBER = 4
    PROCESS_NAME = "SUBMISSION"
    
    def run(self) -> bool:
        """Open browser, navigate to ChatGPT, paste clipboard content, and submit."""
        try:
            self.play_beep()
            self.log_start()
            
            # Step 1: Open browser and navigate to ChatGPT
            self.update_log("Opening browser and navigating to ChatGPT...")
            result = find_and_click_chrome()
            
            print(f"Browser result: {result}", flush=True)
            
            if not result:
                self.update_log("✗ Could not launch browser.")
                self.log_failed()
                return False
            
            self.update_log("✓ Browser opened. Waiting for input field...")
            
            # Step 2: Wait for page to be ready
            if not self._wait_for_page_ready():
                self.log_failed()
                return False
            
            # Step 3: Find and click input field
            if not self._click_input_field():
                self.log_failed()
                return False
            
            # Step 4: Paste and submit
            if not self._paste_and_submit():
                self.log_failed()
                return False
            
            self.log_complete()
            return True
            
        except Exception as e:
            print(f"Process 4 exception: {e}", flush=True)
            self.update_log(f"✗ Submission failed:\n{str(e)}")
            self.log_failed()
            return False
    
    def _wait_for_page_ready(self) -> bool:
        """Wait for the input_field_ready indicator."""
        print("Checking images exist...", flush=True)
        print(f"  input_field_ready.png: {os.path.exists(INPUT_FIELD_READY_IMAGE)}", flush=True)
        print(f"  input_field.png: {os.path.exists(INPUT_FIELD_IMAGE)}", flush=True)
        
        if not os.path.exists(INPUT_FIELD_READY_IMAGE):
            self.update_log("✗ Missing: input_field_ready.png")
            return False
        if not os.path.exists(INPUT_FIELD_IMAGE):
            self.update_log("✗ Missing: input_field.png")
            return False
        
        max_retries = 5
        wait_seconds = 2
        
        print("Starting page ready scan loop...", flush=True)
        
        for attempt in range(1, max_retries + 1):
            print(f"  Attempt {attempt}/{max_retries}...", flush=True)
            self.update_log(f"Checking if page is ready... (attempt {attempt}/{max_retries})")
            
            try:
                ready_indicator = pyautogui.locateOnScreen(INPUT_FIELD_READY_IMAGE, confidence=IMAGE_CONFIDENCE)
                print(f"    Ready indicator result: {ready_indicator}", flush=True)
                
                if ready_indicator:
                    self.update_log("✓ Page is ready!")
                    print("Page ready: True", flush=True)
                    return True
            except Exception as e:
                print(f"    Scan error: {e}", flush=True)
            
            if attempt < max_retries:
                time.sleep(wait_seconds)
        
        print("Page ready: False", flush=True)
        self.update_log("✗ Page did not load in time.")
        return False
    
    def _click_input_field(self) -> bool:
        """Find and click the input field."""
        print("Looking for input_field.png to click...", flush=True)
        self.update_log("Finding input field...")
        
        try:
            input_location = pyautogui.locateOnScreen(INPUT_FIELD_IMAGE, confidence=IMAGE_CONFIDENCE)
            print(f"Input location: {input_location}", flush=True)
            
            if not input_location:
                self.update_log("✗ Could not find input field.")
                return False
            
            center = pyautogui.center(input_location)
            print(f"Clicking at: ({center.x}, {center.y})", flush=True)
            
            pyautogui.click(center.x, center.y)
            time.sleep(0.5)
            return True
            
        except Exception as e:
            print(f"Click error: {e}", flush=True)
            self.update_log(f"✗ Click failed: {str(e)}")
            return False
    
    def _paste_and_submit(self) -> bool:
        """Paste clipboard content and press Enter."""
        try:
            print("Pasting...", flush=True)
            self.update_log("Pasting content...")
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.5)
            
            print("Pressing Enter...", flush=True)
            self.update_log("Submitting...")
            pyautogui.press('enter')
            time.sleep(0.5)
            
            return True
            
        except Exception as e:
            print(f"Paste/submit error: {e}", flush=True)
            self.update_log(f"✗ Failed: {str(e)}")
            return False
