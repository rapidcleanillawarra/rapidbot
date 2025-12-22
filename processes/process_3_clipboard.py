# Process 3: Copy current product to clipboard
from .base import BaseProcess


class ClipboardProcess(BaseProcess):
    """Process 3: Clipboard - copy current product data to clipboard"""
    
    PROCESS_NUMBER = 3
    PROCESS_NAME = "CLIPBOARD"
    
    def run(self) -> bool:
        """Copy current product data to clipboard."""
        try:
            self.play_beep()
            self.log_start()
            
            print(f"Selected Brand: {self.app.selected_brand_name}", flush=True)
            print(f"JSON Path: {self.app.json_manager.current_json_path}", flush=True)
            
            state = self.app.json_manager.current_state
            
            # Verify current_page_data exists
            if not state.get("current_page_data"):
                self.update_log("✗ No products in current page data")
                self.log_failed()
                return False
            
            page_data = state["current_page_data"]
            print(f"Products in current_page_data: {len(page_data)}", flush=True)
            
            # Print product status
            for i, p in enumerate(page_data):
                status = p.get("status", "NO STATUS")
                print(f"  [{i}] SKU: {p.get('SKU')}, Status: {status}", flush=True)
            
            # Find product with status "current"
            current_product = self.app.json_manager.get_current_product()
            
            if not current_product:
                self.update_log("✗ No product with status 'current' found")
                self.log_failed()
                return False
            
            print("\n>>> CURRENT PRODUCT <<<", flush=True)
            print(f"  InventoryID: {current_product.get('InventoryID')}", flush=True)
            print(f"  Brand: {current_product.get('Brand')}", flush=True)
            print(f"  Model: {current_product.get('Model')}", flush=True)
            print(f"  SKU: {current_product.get('SKU')}", flush=True)
            print(f"  Status: {current_product.get('status')}", flush=True)
            
            # Format clipboard content
            clipboard_content = (
                f"InventoryID: {current_product.get('InventoryID')}\n"
                f"Brand: {current_product.get('Brand')}\n"
                f"Model: {current_product.get('Model')}\n"
                f"SKU: {current_product.get('SKU')}"
            )
            
            print(f"\nClipboard content:\n{clipboard_content}", flush=True)
            
            # Copy to clipboard
            self.app.root.clipboard_clear()
            self.app.root.clipboard_append(clipboard_content)
            self.app.root.update()
            
            self.update_log(f"✓ Copied to clipboard:\n{current_product.get('Model')[:50]}...")
            self.log_complete()
            return True
            
        except Exception as e:
            print(f"Process 3 exception: {e}", flush=True)
            self.update_log(f"✗ Clipboard failed:\n{str(e)}")
            self.log_failed()
            return False
