# Process 6: Check Tabs - detect and manage active browser tabs
import time
import pyautogui
import os
from .base import BaseProcess
from config import ACTIVE_TAB_IMAGE, IMAGE_CONFIDENCE
from utils.image_scanner import filter_duplicate_boxes


class TabsProcess(BaseProcess):
    """Process 6: Check Tabs - detect and count active browser tabs"""
    
    PROCESS_NUMBER = 6
    PROCESS_NAME = "CHECK TABS"
    
    def run(self) -> bool:
        """Detect active tabs and close excess if needed."""
        try:
            self.play_beep()
            self.log_start()
            
            # Step 1: Check image exists
            self.update_log("Loading active tab image...")
            
            print(f"Active tab image: {ACTIVE_TAB_IMAGE}", flush=True)
            print(f"  Exists: {os.path.exists(ACTIVE_TAB_IMAGE)}", flush=True)
            
            if not os.path.exists(ACTIVE_TAB_IMAGE):
                print("✗ Image file not found!", flush=True)
                self.update_log("✗ Missing: active_tab.png")
                self.log_failed()
                return False
            
            print("✓ Image file loaded successfully", flush=True)
            self.update_log("Scanning screen for active tabs...")
            
            # Step 2: Scan for tabs
            tab_count = self._scan_for_tabs()
            
            if tab_count is None:
                self.log_failed()
                return False
            
            # Step 3: Check if we need to close tabs
            self._manage_tab_count(tab_count)
            
            self.log_complete()
            return True
            
        except Exception as e:
            print(f"Process 6 exception: {e}", flush=True)
            self.update_log(f"✗ Check tabs failed:\n{str(e)}")
            self.log_failed()
            return False
    
    def _scan_for_tabs(self):
        """Scan screen for all tab instances."""
        print("Starting screen scan...", flush=True)
        print("  Confidence: 0.8", flush=True)
        print("  Scanning entire screen area...", flush=True)
        
        try:
            print("  Executing locateAllOnScreen...", flush=True)
            all_matches = list(pyautogui.locateAllOnScreen(ACTIVE_TAB_IMAGE, confidence=IMAGE_CONFIDENCE))
            
            print(f"  Raw matches found: {len(all_matches)}", flush=True)
            
            # Filter duplicates
            unique_matches = filter_duplicate_boxes(all_matches, threshold=0.5)
            print(f"  Unique matches after filtering: {len(unique_matches)}", flush=True)
            
            self.matches = unique_matches
            tab_count = len(unique_matches)
            
            print(f"\n✓ Scan complete!", flush=True)
            print(f"  Found {tab_count} active tab(s) (after filtering duplicates)", flush=True)
            
            if tab_count > 0:
                print("  Match locations:", flush=True)
                for i, match in enumerate(unique_matches, 1):
                    print(f"    [{i}] {match}", flush=True)
            else:
                print("  No tabs detected on screen", flush=True)
            
            return tab_count
            
        except Exception as e:
            print(f"\n✗ Scan error: {e}", flush=True)
            self.update_log(f"✗ Tab scan failed: {str(e)}")
            return None
    
    def _manage_tab_count(self, detected_count: int) -> None:
        """Close excess tabs if detected count exceeds desired count."""
        try:
            desired_tabs = int(self.app.active_tabs_var.get())
            print(f"\nDesired tabs (from GUI): {desired_tabs}", flush=True)
            print(f"Detected tabs: {detected_count}", flush=True)
            
            if detected_count > desired_tabs:
                tabs_to_close = detected_count - desired_tabs
                print(f"\n⚠ Too many tabs! Need to close {tabs_to_close} tab(s)", flush=True)
                self.update_log(f"Closing {tabs_to_close} excess tab(s)...")
                
                # Sort by left position (leftmost first)
                sorted_matches = sorted(self.matches, key=lambda m: m.left)
                
                for i in range(tabs_to_close):
                    self._close_tab(sorted_matches[i], i + 1, tabs_to_close)
                
                print(f"\n✓ Closed {tabs_to_close} tab(s) successfully", flush=True)
                self.update_log(f"✓ Closed {tabs_to_close} excess tab(s)")
                
                detected_count = desired_tabs
            else:
                print("\n✓ Tab count is within limit", flush=True)
                
        except ValueError:
            print("\n⚠ Invalid Active Tabs value in GUI field", flush=True)
        
        # Update GUI
        print(f"\nUpdating Active Tabs field to: {detected_count}", flush=True)
        self.app.root.after(0, lambda: self.app.update_active_tabs(detected_count))
        self.update_log(f"✓ Detected {detected_count} active tab(s)")
    
    def _close_tab(self, tab_box, index: int, total: int) -> None:
        """Close a single tab by clicking and pressing Ctrl+W."""
        center_x = tab_box.left + tab_box.width // 2
        center_y = tab_box.top + tab_box.height // 2
        
        print(f"\n  Closing tab {index}/{total}:", flush=True)
        print(f"    Position: ({center_x}, {center_y})", flush=True)
        
        pyautogui.click(center_x, center_y)
        time.sleep(0.3)
        
        print("    Pressing Ctrl+W...", flush=True)
        pyautogui.hotkey('ctrl', 'w')
        time.sleep(0.5)
        
        print("    ✓ Tab closed", flush=True)
