# Process 2: Update current data (fetch products if needed)
from .base import BaseProcess


class DataProcess(BaseProcess):
    """Process 2: Update current data - fetch products if needed"""
    
    PROCESS_NUMBER = 2
    PROCESS_NAME = "UPDATE DATA"
    
    def run(self) -> bool:
        """Fetch products if current_page_data is empty."""
        try:
            self.play_beep()
            self.log_start()
            
            state = self.app.json_manager.current_state
            
            # Check if current_page_data is empty
            if not state.get("current_page_data"):
                self.update_log(f"Fetching products for page {state['current_page']}...")
                
                # Update page variable
                self.app.current_page = state['current_page']
                self.app.page_var.set(str(self.app.current_page))
                
                # Fetch products synchronously
                fetch_success = self.app.fetch_products_sync()
                
                if not fetch_success:
                    self.update_log("✗ Failed to fetch products.")
                    self.log_failed()
                    return False
                
                self.update_log(f"✓ Fetched {len(self.app.products)} products for page {self.app.current_page}")
            else:
                self.update_log(f"✓ Current data already loaded ({len(state['current_page_data'])} products)")
            
            self.log_complete()
            return True
            
        except Exception as e:
            print(f"Process 2 exception: {e}", flush=True)
            self.update_log(f"✗ Data update failed:\n{str(e)}")
            self.log_failed()
            return False
