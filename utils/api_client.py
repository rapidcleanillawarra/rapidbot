# API client for fetching brands and products
import requests
from typing import List, Dict, Optional
from config import BRANDS_API_URL


class ApiClient:
    """Client for Power Automate API calls."""
    
    def __init__(self, api_url: str = BRANDS_API_URL):
        self.api_url = api_url
        self.timeout = 10
    
    def fetch_brands(self) -> List[Dict]:
        """
        Fetch list of brands from the API.
        
        Returns:
            List of brand dictionaries with 'id' and 'name' keys
        """
        try:
            payload = {
                "Filter": {
                    "Active": True,
                    "ContentType": 10,
                    "OutputSelector": [
                        "ContentID",
                        "ContentName"
                    ]
                },
                "action": "GetContent"
            }
            headers = {"Content-Type": "application/json"}
            
            response = requests.post(
                self.api_url,
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("Ack") == "Success" and "Content" in data:
                    # Convert to standard format with 'id' and 'name' keys
                    brands = []
                    for content in data["Content"]:
                        brands.append({
                            "id": content.get("ContentID"),
                            "name": content.get("ContentName")
                        })
                    return brands
            
            return []
            
        except requests.exceptions.Timeout:
            print("Brand fetch timeout")
            return []
        except requests.exceptions.RequestException as e:
            print(f"Brand fetch error: {e}")
            return []
    
    def fetch_products(
        self, 
        brand_name: str, 
        page: int = 0, 
        limit: int = 10
    ) -> List[Dict]:
        """
        Fetch products for a specific brand.
        
        Args:
            brand_name: Name of the brand
            page: Page number (0-indexed)
            limit: Number of products per page
        
        Returns:
            List of product dictionaries
        """
        try:
            payload = {
                "Filter": {
                    "Brand": [brand_name],
                    "IsActive": True,
                    "Page": page,
                    "Limit": limit,
                    "OutputSelector": [
                        "SKU",
                        "Model",
                        "InventoryID",
                        "Brand"
                    ]
                },
                "action": "GetItem"
            }
            headers = {"Content-Type": "application/json"}
            
            response = requests.post(
                self.api_url,
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("Ack") == "Success" and "Item" in data:
                    return data["Item"]
            
            return []
            
        except requests.exceptions.Timeout:
            print("Product fetch timeout")
            return []
        except requests.exceptions.RequestException as e:
            print(f"Product fetch error: {e}")
            return []
