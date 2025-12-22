# Process 1: Create folders and initialize JSON
from .base import BaseProcess


class FoldersProcess(BaseProcess):
    """Process 1: Create folders and initialize current.json"""
    
    PROCESS_NUMBER = 1
    PROCESS_NAME = "CREATE FOLDERS"
    
    def run(self) -> bool:
        """Create brand folder and initialize current.json."""
        try:
            self.play_beep()
            self.log_start()
            
            # Step 1: Setup folder structure
            self.update_log(f"Creating folder for '{self.app.selected_brand_name}'...")
            brand_folder = self.app.json_manager.ensure_brand_folder(self.app.selected_brand_name)
            
            # Step 2: Initialize/load current.json
            self.update_log("Loading current.json...")
            state = self.app.json_manager.initialize_current_json()
            
            self.update_log(f"✓ Folders ready!\nCurrent page: {state['current_page']}")
            self.log_complete()
            return True
            
        except Exception as e:
            print(f"Process 1 exception: {e}", flush=True)
            self.update_log(f"✗ Folder creation failed:\n{str(e)}")
            self.log_failed()
            return False
