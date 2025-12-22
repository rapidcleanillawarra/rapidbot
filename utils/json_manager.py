# JSON file management utilities
import json
import os
from typing import Dict, List, Optional, Any


class JsonManager:
    """Manages JSON file operations for product data."""
    
    def __init__(self, products_folder: str):
        self.products_folder = products_folder
        self.current_brand_folder: Optional[str] = None
        self.current_json_path: Optional[str] = None
        self.current_state: Dict = {
            "current_page": 0,
            "current_page_data": []
        }
    
    def ensure_brand_folder(self, brand_name: str) -> str:
        """Create brand-specific folder if it doesn't exist."""
        # Create products folder if needed
        if not os.path.exists(self.products_folder):
            os.makedirs(self.products_folder)
            print(f"Created products folder: {self.products_folder}")
        
        # Create brand folder
        brand_folder = os.path.join(self.products_folder, brand_name)
        if not os.path.exists(brand_folder):
            os.makedirs(brand_folder)
            print(f"Created brand folder: {brand_folder}")
        
        self.current_brand_folder = brand_folder
        return brand_folder
    
    def initialize_current_json(self) -> Dict:
        """Initialize or load current.json file."""
        if not self.current_brand_folder:
            raise Exception("Brand folder not set")
        
        self.current_json_path = os.path.join(self.current_brand_folder, "current.json")
        
        if os.path.exists(self.current_json_path):
            self.current_state = self.load_current_json()
            print(f"Loaded existing state: {self.current_state}")
        else:
            default_state = {
                "current_page": 0,
                "current_page_data": []
            }
            self.save_json(default_state)
            self.current_state = default_state
            print("Created new current.json with default values")
        
        return self.current_state
    
    def load_current_json(self) -> Dict:
        """Load and parse current.json file."""
        try:
            with open(self.current_json_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            # Backup corrupted file
            if os.path.exists(self.current_json_path):
                backup_path = self.current_json_path + ".backup"
                os.rename(self.current_json_path, backup_path)
                print(f"Backed up corrupted file to: {backup_path}")
            return {"current_page": 0, "current_page_data": []}
    
    def save_json(self, data: Dict = None) -> None:
        """Save data to current.json."""
        if data is None:
            data = self.current_state
        with open(self.current_json_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def update_current_json(self, page: int = None, page_data: List = None) -> None:
        """Update current.json with new values."""
        if page is not None:
            self.current_state["current_page"] = page
        if page_data is not None:
            self.current_state["current_page_data"] = page_data
        
        self.save_json()
        print(f"Updated current.json: page={self.current_state['current_page']}, products={len(self.current_state['current_page_data'])}")
    
    def update_product_status(self, new_status: str) -> bool:
        """
        Update the status of the current product and move to next.
        
        Returns:
            True if a product was updated, False otherwise
        """
        page_data = self.current_state.get("current_page_data", [])
        current_index = -1
        
        # Find and update product with status "current"
        for i, product in enumerate(page_data):
            if product.get("status") == "current":
                product["status"] = new_status
                current_index = i
                print(f"Status changed to: {new_status}")
                break
        
        if current_index == -1:
            print("WARNING: No product with status 'current' found!")
            return False
        
        # Mark next product as "current"
        next_index = current_index + 1
        if next_index < len(page_data):
            page_data[next_index]["status"] = "current"
            print(f"Next product [{next_index}]: {page_data[next_index].get('SKU')} → status: current")
        else:
            print("No more products in this page (reached end of list)")
        
        self.save_json()
        return True
    
    def get_current_product(self) -> Optional[Dict]:
        """Get the product with status 'current'."""
        page_data = self.current_state.get("current_page_data", [])
        for product in page_data:
            if product.get("status") == "current":
                return product
        return None
