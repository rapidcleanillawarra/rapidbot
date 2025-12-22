import tkinter as tk
from tkinter import ttk, messagebox
import threading
import os
import sys
import requests
import json

# Import the click function from your existing script
from click_chrome import find_and_click_chrome, find_and_click_image, CHROME_IMAGE

class ChromeClickerApp:
    # API Configuration
    BRANDS_API_URL = "https://default61576f99244849ec8803974b47673f.57.environment.api.powerplatform.com:443/powerautomate/automations/direct/workflows/ef89e5969a8f45778307f167f435253c/triggers/manual/paths/invoke?api-version=1&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=pPhk80gODQOi843ixLjZtPPWqTeXIbIt9ifWZP6CJfY"
    
    def __init__(self, root):
        self.root = root
        self.root.title("RapidBot - Chrome Clicker")
        self.root.geometry("900x750")
        self.root.resizable(True, True)
        
        # Set window icon if available
        try:
            if os.path.exists(CHROME_IMAGE):
                icon = tk.PhotoImage(file=CHROME_IMAGE)
                self.root.iconphoto(True, icon)
        except:
            pass
        
        # Configure colors - Modern dark theme
        self.bg_color = "#1a1a2e"
        self.card_color = "#16213e"
        self.accent_color = "#0f3460"
        self.highlight_color = "#e94560"
        self.text_color = "#eaeaea"
        self.success_color = "#00d26a"
        self.warning_color = "#ffc107"
        
        self.root.configure(bg=self.bg_color)
        
        # Running state
        self.is_running = False
        
        # Brand data
        self.brands = []
        self.selected_brand_id = None
        self.selected_brand_name = None
        
        # Product data
        self.products = []
        self.current_page = 0
        self.products_per_page = 10
        
        self.create_widgets()
        self.check_image_status()
        
        # Fetch brands on startup
        self.fetch_brands_async()
    
    def create_widgets(self):
        # Main container
        main_frame = tk.Frame(self.root, bg=self.bg_color, padx=30, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="🤖 RapidBot",
            font=("Segoe UI", 24, "bold"),
            fg=self.highlight_color,
            bg=self.bg_color
        )
        title_label.pack(pady=(0, 5))
        
        # Subtitle
        subtitle_label = tk.Label(
            main_frame,
            text="ChatGPT Auto-Navigator",
            font=("Segoe UI", 12),
            fg=self.text_color,
            bg=self.bg_color
        )
        subtitle_label.pack(pady=(0, 20))
        
        # Two-column layout
        columns_frame = tk.Frame(main_frame, bg=self.bg_color)
        columns_frame.pack(fill=tk.BOTH, expand=True)
        
        # LEFT COLUMN - Controls
        left_column = tk.Frame(columns_frame, bg=self.bg_color)
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Brand selection frame
        brand_frame = tk.Frame(left_column, bg=self.card_color, padx=20, pady=15)
        brand_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Brand label
        tk.Label(
            brand_frame,
            text="Select Brand",
            font=("Segoe UI", 10, "bold"),
            fg="#888",
            bg=self.card_color
        ).pack(anchor=tk.W, pady=(0, 5))
        
        # Brand dropdown and refresh button container
        brand_controls = tk.Frame(brand_frame, bg=self.card_color)
        brand_controls.pack(fill=tk.X)
        
        # Brand dropdown
        self.brand_var = tk.StringVar()
        self.brand_dropdown = ttk.Combobox(
            brand_controls,
            textvariable=self.brand_var,
            state="readonly",
            font=("Segoe UI", 10),
            width=20
        )
        self.brand_dropdown.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.brand_dropdown.bind("<<ComboboxSelected>>", self.on_brand_selected)
        
        # Refresh button
        self.refresh_btn = tk.Button(
            brand_controls,
            text="🔄",
            font=("Segoe UI", 12),
            fg="white",
            bg=self.accent_color,
            activebackground="#1a4a7a",
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            padx=10,
            pady=2,
            command=self.fetch_brands_async
        )
        self.refresh_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        # Brand status label
        self.brand_status = tk.Label(
            brand_frame,
            text="Loading brands...",
            font=("Segoe UI", 8),
            fg="#888",
            bg=self.card_color
        )
        self.brand_status.pack(anchor=tk.W, pady=(5, 0))
        
        # Product fetch controls frame
        fetch_frame = tk.Frame(left_column, bg=self.card_color, padx=20, pady=15)
        fetch_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(
            fetch_frame,
            text="Fetch Products",
            font=("Segoe UI", 10, "bold"),
            fg="#888",
            bg=self.card_color
        ).pack(anchor=tk.W, pady=(0, 5))
        
        # Page input and fetch button
        fetch_controls = tk.Frame(fetch_frame, bg=self.card_color)
        fetch_controls.pack(fill=tk.X)
        
        tk.Label(
            fetch_controls,
            text="Page:",
            font=("Segoe UI", 9),
            fg=self.text_color,
            bg=self.card_color
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        self.page_var = tk.StringVar(value="0")
        self.page_entry = tk.Entry(
            fetch_controls,
            textvariable=self.page_var,
            font=("Segoe UI", 10),
            width=5,
            bg="#0f3460",
            fg=self.text_color,
            insertbackground=self.text_color,
            relief=tk.FLAT
        )
        self.page_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        self.fetch_products_btn = tk.Button(
            fetch_controls,
            text="🔍 Fetch Products",
            font=("Segoe UI", 10, "bold"),
            fg="white",
            bg="#2196F3",
            activebackground="#1976D2",
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            padx=15,
            pady=5,
            command=self.fetch_products_button_click
        )
        self.fetch_products_btn.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Status card
        status_frame = tk.Frame(left_column, bg=self.card_color, padx=20, pady=15)
        status_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Status indicator
        status_header = tk.Frame(status_frame, bg=self.card_color)
        status_header.pack(fill=tk.X)
        
        tk.Label(
            status_header,
            text="Status",
            font=("Segoe UI", 10, "bold"),
            fg="#888",
            bg=self.card_color
        ).pack(side=tk.LEFT)
        
        self.status_indicator = tk.Label(
            status_header,
            text="● Ready",
            font=("Segoe UI", 10, "bold"),
            fg=self.success_color,
            bg=self.card_color
        )
        self.status_indicator.pack(side=tk.RIGHT)
        
        # Browser status
        self.image_status = tk.Label(
            status_frame,
            text="Ready to launch browser",
            font=("Segoe UI", 9),
            fg=self.success_color,
            bg=self.card_color,
            wraplength=250,
            justify=tk.LEFT
        )
        self.image_status.pack(fill=tk.X, pady=(10, 0))
        
        # Progress/Log area
        log_frame = tk.Frame(left_column, bg=self.accent_color, padx=10, pady=10)
        log_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.log_label = tk.Label(
            log_frame,
            text="Click 'Start' to open ChatGPT in your browser",
            font=("Consolas", 9),
            fg=self.text_color,
            bg=self.accent_color,
            wraplength=280,
            justify=tk.LEFT
        )
        self.log_label.pack(fill=tk.X)
        
        # Buttons frame
        buttons_frame = tk.Frame(left_column, bg=self.bg_color)
        buttons_frame.pack(fill=tk.X)
        
        # Start button
        self.start_btn = tk.Button(
            buttons_frame,
            text="▶  Start",
            font=("Segoe UI", 12, "bold"),
            fg="white",
            bg=self.highlight_color,
            activebackground="#c73e54",
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            padx=30,
            pady=10,
            command=self.start_clicking
        )
        self.start_btn.pack(fill=tk.X, pady=(0, 5))
        
        # Try Again button (hidden initially)
        self.retry_btn = tk.Button(
            buttons_frame,
            text="🔄  Try Again",
            font=("Segoe UI", 12, "bold"),
            fg="white",
            bg="#ff9800",
            activebackground="#e68900",
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            padx=30,
            pady=10,
            command=self.start_clicking
        )
        # Don't pack it yet - will show after first attempt
        
        # Scan & Click button
        self.scan_btn = tk.Button(
            buttons_frame,
            text="🔍  Scan & Click Input Field",
            font=("Segoe UI", 11, "bold"),
            fg="white",
            bg="#2196F3",
            activebackground="#1976D2",
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            padx=20,
            pady=8,
            command=self.scan_and_click
        )
        self.scan_btn.pack(fill=tk.X, pady=(0, 5))
        
        # Exit button
        exit_btn = tk.Button(
            buttons_frame,
            text="✕  Exit",
            font=("Segoe UI", 11),
            fg=self.text_color,
            bg=self.accent_color,
            activebackground="#1a4a7a",
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            padx=20,
            pady=8,
            command=self.root.quit
        )
        exit_btn.pack(fill=tk.X)
        
        # Footer
        footer = tk.Label(
            left_column,
            text="Browser Auto-Navigator",
            font=("Segoe UI", 8),
            fg="#666",
            bg=self.bg_color
        )
        footer.pack(pady=(15, 0))
        
        # RIGHT COLUMN - Product List
        right_column = tk.Frame(columns_frame, bg=self.bg_color)
        right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Product list frame
        product_frame = tk.Frame(right_column, bg=self.card_color, padx=20, pady=15)
        product_frame.pack(fill=tk.BOTH, expand=True)
        
        # Product label
        product_header = tk.Frame(product_frame, bg=self.card_color)
        product_header.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            product_header,
            text="Products",
            font=("Segoe UI", 14, "bold"),
            fg=self.text_color,
            bg=self.card_color
        ).pack(side=tk.LEFT)
        
        self.product_count_label = tk.Label(
            product_header,
            text="",
            font=("Segoe UI", 10),
            fg="#888",
            bg=self.card_color
        )
        self.product_count_label.pack(side=tk.RIGHT)
        
        # Product listbox with scrollbar
        list_container = tk.Frame(product_frame, bg=self.card_color)
        list_container.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(list_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.product_listbox = tk.Listbox(
            list_container,
            font=("Consolas", 9),
            bg="#0f3460",
            fg=self.text_color,
            selectbackground=self.highlight_color,
            selectforeground="white",
            relief=tk.FLAT,
            yscrollcommand=scrollbar.set
        )
        self.product_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.product_listbox.yview)
        
        # Product status label
        self.product_status = tk.Label(
            product_frame,
            text="Select a brand and click 'Fetch Products'",
            font=("Segoe UI", 9),
            fg="#888",
            bg=self.card_color
        )
        self.product_status.pack(anchor=tk.W, pady=(10, 0))
    
    def check_image_status(self):
        """Check browser availability"""
        # Browser launching doesn't require any setup, so always ready
        self.image_status.config(
            text="✓ Ready to navigate to ChatGPT",
            fg=self.success_color
        )
    
    def update_log(self, message):
        """Update the log label"""
        self.log_label.config(text=message)
        self.root.update()
    
    def update_status(self, status, color):
        """Update the status indicator"""
        self.status_indicator.config(text=status, fg=color)
        self.root.update()
    
    def start_clicking(self):
        """Start the clicking process in a separate thread"""
        if self.is_running:
            return
        
        self.is_running = True
        self.start_btn.config(state=tk.DISABLED, text="⏳ Launching...")
        self.update_status("● Launching...", self.warning_color)
        self.update_log("Opening browser and navigating to ChatGPT...")
        
        # Run in separate thread to keep UI responsive
        thread = threading.Thread(target=self.run_clicker)
        thread.daemon = True
        thread.start()
    
    def run_clicker(self):
        """Run the clicker function"""
        try:
            result = find_and_click_chrome()
            
            if result:
                self.root.after(0, lambda: self.update_status("● Success!", self.success_color))
                self.root.after(0, lambda: self.update_log("✓ Browser opened and navigated to ChatGPT!"))
                self.root.after(0, lambda: self.show_retry_button())
            else:
                self.root.after(0, lambda: self.update_status("● Failed", self.warning_color))
                self.root.after(0, lambda: self.update_log("✗ Could not launch browser.\nPlease check your default browser settings."))
                self.root.after(0, lambda: self.show_retry_button())
        except Exception as e:
            self.root.after(0, lambda: self.update_status("● Error", self.highlight_color))
            self.root.after(0, lambda: self.update_log(f"Error: {str(e)}"))
            self.root.after(0, lambda: self.show_retry_button())
        finally:
            self.is_running = False
            self.root.after(0, lambda: self.start_btn.config(state=tk.NORMAL, text="▶  Start"))
    
    def scan_and_click(self):
        """Scan for and click the input field"""
        if self.is_running:
            return
        
        self.is_running = True
        self.scan_btn.config(state=tk.DISABLED, text="🔍 Scanning...")
        
        # Run in separate thread
        thread = threading.Thread(target=self.run_scan_and_click)
        thread.daemon = True
        thread.start()
    
    def run_scan_and_click(self):
        """Run the scan and click operation"""
        try:
            # Import the necessary functions
            from click_chrome import is_chrome_active, bring_chrome_to_front, find_and_click_image
            import time
            
            self.root.after(0, lambda: self.update_status("● Checking Chrome...", self.warning_color))
            self.root.after(0, lambda: self.update_log("Checking if Chrome is active..."))
            
            # Check if Chrome is active
            if not is_chrome_active():
                self.root.after(0, lambda: self.update_log("Chrome not active. Bringing Chrome to front..."))
                bring_chrome_to_front()
                time.sleep(1)
            else:
                self.root.after(0, lambda: self.update_log("Chrome is active. Bringing to front..."))
                bring_chrome_to_front()
                time.sleep(0.5)
            
            # Now scan for the image
            self.root.after(0, lambda: self.update_status("● Scanning...", self.warning_color))
            self.root.after(0, lambda: self.update_log("Scanning for input field..."))
            
            result = find_and_click_image()
            
            if result:
                self.root.after(0, lambda: self.update_status("● Success!", self.success_color))
                self.root.after(0, lambda: self.update_log("✓ Successfully found and clicked input field!"))
            else:
                self.root.after(0, lambda: self.update_status("● Not Found", self.warning_color))
                self.root.after(0, lambda: self.update_log("✗ Could not find input field.\nMake sure Chrome is open with ChatGPT page loaded."))
                
        except Exception as e:
            self.root.after(0, lambda: self.update_status("● Error", self.highlight_color))
            self.root.after(0, lambda: self.update_log(f"Error: {str(e)}"))
        finally:
            self.is_running = False
            self.root.after(0, lambda: self.scan_btn.config(state=tk.NORMAL, text="🔍  Scan & Click Input Field"))
    
    def show_retry_button(self):
        """Show the Try Again button and hide the Start button"""
        self.start_btn.pack_forget()
        self.retry_btn.pack(fill=tk.X, pady=(0, 5))
    
    def fetch_brands_async(self):
        """Fetch brands in a separate thread"""
        self.refresh_btn.config(state=tk.DISABLED)
        self.update_brand_status("Loading brands...")
        
        thread = threading.Thread(target=self.fetch_brands)
        thread.daemon = True
        thread.start()
    
    def fetch_brands(self):
        """Fetch brands from the API"""
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
            
            headers = {
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                self.BRANDS_API_URL,
                json=payload,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("Ack") == "Success" and "Content" in data:
                    self.brands = data["Content"]
                    
                    # Update dropdown on main thread
                    self.root.after(0, self.update_brand_dropdown)
                    self.root.after(0, lambda: self.update_brand_status(f"✓ {len(self.brands)} brands loaded"))
                else:
                    self.root.after(0, lambda: self.update_brand_status("✗ Failed to load brands"))
            else:
                self.root.after(0, lambda: self.update_brand_status(f"✗ Error: {response.status_code}"))
                
        except requests.exceptions.Timeout:
            self.root.after(0, lambda: self.update_brand_status("✗ Request timeout"))
        except requests.exceptions.RequestException as e:
            self.root.after(0, lambda: self.update_brand_status(f"✗ Network error"))
        except Exception as e:
            self.root.after(0, lambda: self.update_brand_status(f"✗ Error: {str(e)}"))
        finally:
            self.root.after(0, lambda: self.refresh_btn.config(state=tk.NORMAL))
    
    def update_brand_dropdown(self):
        """Update the brand dropdown with fetched brands"""
        brand_names = [brand["ContentName"] for brand in self.brands]
        self.brand_dropdown['values'] = brand_names
        
        # Select first brand by default if available
        if brand_names:
            self.brand_dropdown.current(0)
            self.on_brand_selected(None)
    
    def on_brand_selected(self, event):
        """Handle brand selection"""
        selected_name = self.brand_var.get()
        
        # Find the selected brand
        for brand in self.brands:
            if brand["ContentName"] == selected_name:
                self.selected_brand_id = brand["ContentID"]
                self.selected_brand_name = brand["ContentName"]
                print(f"Selected Brand: {self.selected_brand_name} (ID: {self.selected_brand_id})")
                break
    
    def update_brand_status(self, message):
        """Update the brand status label"""
        self.brand_status.config(text=message)
        self.root.update()
    
    def fetch_products_button_click(self):
        """Handle fetch products button click"""
        if not self.selected_brand_name:
            messagebox.showwarning("No Brand Selected", "Please select a brand first!")
            return
        
        try:
            page = int(self.page_var.get())
            if page < 0:
                messagebox.showerror("Invalid Page", "Page number must be 0 or greater!")
                return
            self.current_page = page
        except ValueError:
            messagebox.showerror("Invalid Page", "Please enter a valid page number!")
            return
        
        self.fetch_products_async()

    
    def fetch_products_async(self):
        """Fetch products in a separate thread"""
        if not self.selected_brand_name:
            return
        
        self.update_product_status("Loading products...")
        self.product_listbox.delete(0, tk.END)
        
        thread = threading.Thread(target=self.fetch_products)
        thread.daemon = True
        thread.start()
    
    def fetch_products(self):
        """Fetch products from the API based on selected brand"""
        try:
            payload = {
                "Filter": {
                    "Brand": [self.selected_brand_name],
                    "IsActive": True,
                    "Page": self.current_page,
                    "Limit": self.products_per_page,
                    "OutputSelector": [
                        "SKU",
                        "Model",
                        "InventoryID",
                        "Brand"
                    ]
                },
                "action": "GetItem"
            }
            
            headers = {
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                self.BRANDS_API_URL,
                json=payload,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("Ack") == "Success" and "Item" in data:
                    self.products = data["Item"]
                    
                    # Update product list on main thread
                    self.root.after(0, self.update_product_list)
                    self.root.after(0, lambda: self.update_product_status(f"✓ {len(self.products)} products loaded"))
                else:
                    self.root.after(0, lambda: self.update_product_status("✗ No products found"))
            else:
                self.root.after(0, lambda: self.update_product_status(f"✗ Error: {response.status_code}"))
                
        except requests.exceptions.Timeout:
            self.root.after(0, lambda: self.update_product_status("✗ Request timeout"))
        except requests.exceptions.RequestException as e:
            self.root.after(0, lambda: self.update_product_status(f"✗ Network error"))
        except Exception as e:
            self.root.after(0, lambda: self.update_product_status(f"✗ Error: {str(e)}"))
    
    def update_product_list(self):
        """Update the product listbox with fetched products"""
        self.product_listbox.delete(0, tk.END)
        
        for product in self.products:
            # Format: SKU | Model | InventoryID
            sku = product.get('SKU', 'N/A')
            model = product.get('Model', 'N/A')[:50]
            inventory_id = product.get('InventoryID', 'N/A')
            
            display_text = f"{sku:20} | {model:50} | ID: {inventory_id}"
            self.product_listbox.insert(tk.END, display_text)
            
            # Debug: Print to console
            print(f"Product: SKU={sku}, Model={model}, InventoryID={inventory_id}")
        
        # Update count label
        self.product_count_label.config(text=f"({len(self.products)} items)")
    
    def update_product_status(self, message):
        """Update the product status label"""
        self.product_status.config(text=message)
        self.root.update()



def main():
    root = tk.Tk()
    app = ChromeClickerApp(root)
    
    # Center window on screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()


if __name__ == "__main__":
    main()
