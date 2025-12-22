# Process 5: Confirm Submission - wait for response indicators
import time
import pyautogui
import os
from .base import BaseProcess
from config import (
    SUBMISSION_ANSWER_NOW_IMAGE, 
    SUBMISSION_STOP_IMAGE, 
    IMAGE_CONFIDENCE,
    PROCESS_5_MAX_RETRIES,
    PROCESS_5_WAIT_SECONDS
)


class ConfirmProcess(BaseProcess):
    """Process 5: Confirm Submission - scan for indicator images"""
    
    PROCESS_NUMBER = 5
    PROCESS_NAME = "CONFIRM SUBMISSION"
    
    def run(self) -> bool:
        """Wait for both Answer Now and Stop indicators to appear."""
        try:
            self.play_beep()
            self.log_start()
            
            # Check images exist
            print(f"Answer Now image: {SUBMISSION_ANSWER_NOW_IMAGE}", flush=True)
            print(f"  Exists: {os.path.exists(SUBMISSION_ANSWER_NOW_IMAGE)}", flush=True)
            print(f"Stop image: {SUBMISSION_STOP_IMAGE}", flush=True)
            print(f"  Exists: {os.path.exists(SUBMISSION_STOP_IMAGE)}", flush=True)
            
            if not os.path.exists(SUBMISSION_ANSWER_NOW_IMAGE):
                self.update_log("✗ Missing: submission_indicator_answer_now.png")
                self.log_failed()
                return False
            if not os.path.exists(SUBMISSION_STOP_IMAGE):
                self.update_log("✗ Missing: submission_indicator_stop.png")
                self.log_failed()
                return False
            
            max_retries = PROCESS_5_MAX_RETRIES
            wait_seconds = PROCESS_5_WAIT_SECONDS
            
            print(f"Starting confirmation loop: {max_retries} attempts, {wait_seconds}s wait", flush=True)
            
            for attempt in range(1, max_retries + 1):
                print(f"\n  Attempt {attempt}/{max_retries}...", flush=True)
                self.update_log(f"Checking for response... (attempt {attempt}/{max_retries})")
                
                try:
                    # Check for both indicators
                    print("    Scanning for Answer Now...", flush=True)
                    answer_now_found = pyautogui.locateOnScreen(
                        SUBMISSION_ANSWER_NOW_IMAGE, confidence=IMAGE_CONFIDENCE
                    )
                    print(f"    Answer Now result: {answer_now_found}", flush=True)
                    
                    print("    Scanning for Stop...", flush=True)
                    stop_found = pyautogui.locateOnScreen(
                        SUBMISSION_STOP_IMAGE, confidence=IMAGE_CONFIDENCE
                    )
                    print(f"    Stop result: {stop_found}", flush=True)
                    
                    if answer_now_found and stop_found:
                        print("    ✓ BOTH FOUND!", flush=True)
                        self.update_log("✓ Submission confirmed! Both indicators found.")
                        
                        # Update product status
                        self._update_product_status()
                        
                        self.log_complete()
                        return True
                    
                    elif answer_now_found:
                        self.update_log("Found 'Answer Now', waiting for 'Stop'...")
                    elif stop_found:
                        self.update_log("Found 'Stop', waiting for 'Answer Now'...")
                    else:
                        self.update_log("No indicators found yet...")
                        
                except Exception as e:
                    print(f"    Scan exception: {e}", flush=True)
                
                if attempt < max_retries:
                    print(f"    Waiting {wait_seconds} seconds...", flush=True)
                    time.sleep(wait_seconds)
            
            self.update_log(f"✗ Could not confirm after {max_retries} attempts.")
            self.log_failed()
            return False
            
        except Exception as e:
            print(f"Process 5 exception: {e}", flush=True)
            self.update_log(f"✗ Confirm failed:\n{str(e)}")
            self.log_failed()
            return False
    
    def _update_product_status(self) -> None:
        """Update the current product status to 'submitted'."""
        print("\n    === UPDATING PRODUCT STATUS ===", flush=True)
        print(f"    Brand: {self.app.selected_brand_name}", flush=True)
        print(f"    JSON Path: {self.app.json_manager.current_json_path}", flush=True)
        
        page_data = self.app.json_manager.current_state.get("current_page_data", [])
        print(f"    Products in state: {len(page_data)}", flush=True)
        
        current_index = -1
        for i, product in enumerate(page_data):
            if product.get("status") == "current":
                print(f"    Found product at [{i}]: {product.get('SKU')}", flush=True)
                product["status"] = "submitted"
                current_index = i
                print("    Status changed to: submitted", flush=True)
                break
        
        if current_index == -1:
            print("    WARNING: No product with status 'current' found!", flush=True)
        else:
            # Mark next product as "current"
            next_index = current_index + 1
            if next_index < len(page_data):
                page_data[next_index]["status"] = "current"
                print(f"    Next product [{next_index}]: {page_data[next_index].get('SKU')} → status: current", flush=True)
            else:
                print("    No more products in this page", flush=True)
        
        # Save to file
        print(f"    Saving to: {self.app.json_manager.current_json_path}", flush=True)
        self.app.json_manager.save_json()
        print("    ✓ File saved!", flush=True)
        print("    === UPDATE COMPLETE ===\n", flush=True)
        
        self.update_log("✓ Product status updated to 'submitted'")
