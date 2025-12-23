# Process 7: Wait and Download - cycle through tabs, detect JSON download link via image, and click to download
import time
import os
import pyautogui
from .base import BaseProcess
from config import ACTIVE_TAB_IMAGE, IMAGE_CONFIDENCE, DOWNLOAD_JSON_IMAGE, AUTOMATE_JSON_IMAGE, ERROR_DOWNLOAD_IMAGE
from utils.image_scanner import filter_duplicate_boxes
from utils.audio import beep_success, beep_error


class WaitProcess(BaseProcess):
    """Process 7: Wait and Download - cycle through tabs, detect target via image matching, and click to download"""
    
    PROCESS_NUMBER = 7
    PROCESS_NAME = "WAIT AND DOWNLOAD"
    
    # Images to search for (in order of priority)
    TARGET_IMAGES = [
        ("download_json.png", DOWNLOAD_JSON_IMAGE),
        ("automate_json.png", AUTOMATE_JSON_IMAGE),
    ]
    
    def run(self) -> bool:
        """Cycle through tabs and detect target image, click to download."""
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
            
            # Step 3: Cycle through each tab and check for target image
            for i, tab in enumerate(tab_matches[:tabs_to_check], 1):
                print(f"\n--- Checking tab {i}/{tabs_to_check} ---", flush=True)
                self.update_log(f"Checking tab {i}/{tabs_to_check}...")
                
                if self._check_tab_for_download(tab, i):
                    print(f"\n✓ Found and clicked download in tab {i}!", flush=True)
                    self.update_log(f"✓ Downloaded from tab {i}!")
                    beep_success()
                    self.log_complete()
                    return True
            
            # No target found in any tab
            print("\n✗ Download target not found in any tab", flush=True)
            self.update_log("✗ Download target not found")
            beep_error()
            self.log_failed()
            return False
            
        except Exception as e:
            print(f"Process 7 exception: {e}", flush=True)
            self.update_log(f"✗ Wait and Download failed:\n{str(e)}")
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
    
    def _check_tab_for_download(self, tab_box, tab_index: int) -> bool:
        """Click on a tab, check for failure first, then look for download image."""
        # Click on tab to activate it
        center_x = tab_box.left + tab_box.width // 2
        center_y = tab_box.top + tab_box.height // 2
        
        print(f"  Clicking tab at ({center_x}, {center_y})", flush=True)
        pyautogui.click(center_x, center_y)
        
        # Wait for page to load
        time.sleep(1.5)
        
        # FIRST: Check for failure condition using image matching
        print("  Checking for error_download.png...", flush=True)
        if self._check_for_failure():
            print("  ✗ Failed file generation detected!", flush=True)
            self.update_log("✗ Failed generation detected")
            return False  # Skip this tab, it's a failure
        
        # SECOND: Try each target image in order (success check)
        for image_name, image_path in self.TARGET_IMAGES:
            print(f"  Scanning for {image_name}...", flush=True)
            
            try:
                if not os.path.exists(image_path):
                    print(f"    Warning: {image_path} does not exist", flush=True)
                    continue
                
                download_location = pyautogui.locateOnScreen(
                    image_path, 
                    confidence=IMAGE_CONFIDENCE
                )
                
                if download_location:
                    # Click center of the found image
                    click_x = download_location.left + download_location.width // 2
                    click_y = download_location.top + download_location.height // 2
                    
                    print(f"  ✓ Found {image_name} at ({click_x}, {click_y})", flush=True)
                    self.update_log(f"Found {image_name}, clicking...")
                    
                    pyautogui.click(click_x, click_y)
                    print(f"  ✓ Clicked to download!", flush=True)
                    time.sleep(0.5)
                    return True
                    
            except Exception as e:
                print(f"    Scan error for {image_name}: {e}", flush=True)
        
        print(f"  No download target found in tab {tab_index}", flush=True)
        return False
    
    def _check_for_failure(self) -> bool:
        """Check screen for failure image (error_download.png).
        
        Returns:
            True if failure image detected, False otherwise
        """
        try:
            if not os.path.exists(ERROR_DOWNLOAD_IMAGE):
                print(f"    Warning: {ERROR_DOWNLOAD_IMAGE} does not exist", flush=True)
                return False
            
            error_location = pyautogui.locateOnScreen(
                ERROR_DOWNLOAD_IMAGE,
                confidence=IMAGE_CONFIDENCE
            )
            
            if error_location:
                print(f"    Found error_download.png on screen", flush=True)
                return True
            
            return False
            
        except Exception as e:
            print(f"    Failure check error: {e}", flush=True)
            return False  # If check fails, assume no failure and continue


