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
        
        # Product folder management
        self.products_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "products")
        self.current_brand_folder = None
        self.current_json_path = None
        self.current_state = {
            "current_page": 0,
            "current_page_data": []
        }

        
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
        
        # Validate brand selection
        if not self.selected_brand_name:
            messagebox.showwarning("No Brand Selected", "Please select a brand before starting!")
            return
        
        self.is_running = True
        self.start_btn.config(state=tk.DISABLED, text="⏳ Starting...")
        self.update_status("● Starting...", self.warning_color)
        self.update_log("Initializing process...")
        
        # Run in separate thread to keep UI responsive
        thread = threading.Thread(target=self.run_clicker)
        thread.daemon = True
        thread.start()
    
    def run_clicker(self):
        """Run the complete process flow"""
        try:
            # Process 1: Create Folders
            self.root.after(0, lambda: self.update_status("● Creating Folders...", self.warning_color))
            folders_success = self.run_create_folders_process()
            
            if not folders_success:
                self.root.after(0, lambda: self.update_status("● Folder Creation Failed", self.highlight_color))
                self.root.after(0, lambda: self.show_retry_button())
                return
            
            # Process 2: Update Current Data
            self.root.after(0, lambda: self.update_status("● Updating Data...", self.warning_color))
            data_success = self.run_update_current_data_process()
            
            if not data_success:
                self.root.after(0, lambda: self.update_status("● Data Update Failed", self.highlight_color))
                self.root.after(0, lambda: self.show_retry_button())
                return
            
            # Process 3: Clipboard
            self.root.after(0, lambda: self.update_status("● Copying to Clipboard...", self.warning_color))
            clipboard_success = self.run_clipboard_process()
            
            if not clipboard_success:
                self.root.after(0, lambda: self.update_status("● Clipboard Failed", self.highlight_color))
                self.root.after(0, lambda: self.show_retry_button())
                return
            
            # Process 4: Submission
            self.root.after(0, lambda: self.update_status("● Submitting...", self.warning_color))
            submit_success = self.run_submission_process()
            
            if not submit_success:
                self.root.after(0, lambda: self.update_status("● Submission Failed", self.highlight_color))
                self.root.after(0, lambda: self.show_retry_button())
                return
            
            # Process 5: Confirm Submission
            self.root.after(0, lambda: self.update_status("● Confirming...", self.warning_color))
            confirm_success = self.run_confirm_submission_process()
            
            if confirm_success:
                self.root.after(0, lambda: self.update_status("● Success!", self.success_color))
                self.root.after(0, lambda: self.show_retry_button())
            else:
                self.root.after(0, lambda: self.update_status("● Confirm Failed", self.warning_color))
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
    
    # ========== HELPER METHODS ==========
    
    def ensure_brand_folder(self):
        """Create brand-specific folder if it doesn't exist"""
        try:
            # Create products folder if it doesn't exist
            if not os.path.exists(self.products_folder):
                os.makedirs(self.products_folder)
                print(f"Created products folder: {self.products_folder}")
            
            # Create brand-specific folder
            brand_folder = os.path.join(self.products_folder, self.selected_brand_name)
            if not os.path.exists(brand_folder):
                os.makedirs(brand_folder)
                print(f"Created brand folder: {brand_folder}")
            
            self.current_brand_folder = brand_folder
            return brand_folder
            
        except Exception as e:
            print(f"Error creating folder: {e}")
            raise Exception(f"Failed to create folder: {str(e)}")
    
    def initialize_current_json(self):
        """Initialize or load current.json file"""
        try:
            if not self.current_brand_folder:
                raise Exception("Brand folder not set")
            
            self.current_json_path = os.path.join(self.current_brand_folder, "current.json")
            
            # Check if file exists
            if os.path.exists(self.current_json_path):
                # Load existing file
                state = self.load_current_json()
                self.current_state = state
                print(f"Loaded existing state: {state}")
            else:
                # Create new file with default values
                default_state = {
                    "current_page": 0,
                    "current_page_data": []
                }
                
                with open(self.current_json_path, 'w') as f:
                    json.dump(default_state, f, indent=2)
                
                self.current_state = default_state
                print(f"Created new current.json with default values")
            
            return self.current_state
            
        except Exception as e:
            print(f"Error initializing JSON: {e}")
            raise Exception(f"Failed to initialize current.json: {str(e)}")
    
    def load_current_json(self):
        """Load and parse current.json file"""
        try:
            with open(self.current_json_path, 'r') as f:
                data = json.load(f)
            return data
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            # Backup corrupted file
            backup_path = self.current_json_path + ".backup"
            if os.path.exists(self.current_json_path):
                os.rename(self.current_json_path, backup_path)
                print(f"Backed up corrupted file to: {backup_path}")
            # Return default state
            return {
                "current_page": 0,
                "current_page_data": []
            }
        except Exception as e:
            print(f"Error loading JSON: {e}")
            raise
    
    def update_current_json(self, page=None, page_data=None):
        """Update current.json with new values"""
        try:
            if page is not None:
                self.current_state["current_page"] = page
            if page_data is not None:
                self.current_state["current_page_data"] = page_data
            
            # Write to file
            with open(self.current_json_path, 'w') as f:
                json.dump(self.current_state, f, indent=2)
            
            print(f"Updated current.json: page={self.current_state['current_page']}, products={len(self.current_state['current_page_data'])}")
            
        except Exception as e:
            print(f"Error updating JSON: {e}")
            raise Exception(f"Failed to update current.json: {str(e)}")
    
    def update_product_status(self, new_status):
        """Update the status of the current product in current_page_data"""
        try:
            # Find and update the product with status "current"
            for product in self.current_state["current_page_data"]:
                if product.get("status") == "current":
                    product["status"] = new_status
                    break
            
            # Save updated state to file
            with open(self.current_json_path, 'w') as f:
                json.dump(self.current_state, f, indent=2)
            
            print(f"Updated product status to: {new_status}")
            
        except Exception as e:
            print(f"Error updating product status: {e}")
            raise Exception(f"Failed to update product status: {str(e)}")
    
    # ========== PROCESS METHODS ==========
    
    def run_create_folders_process(self):
        """Process 1: Create folders and initialize current.json"""
        try:
            # Step 1: Setup folder structure
            self.root.after(0, lambda: self.update_log(f"Creating folder for '{self.selected_brand_name}'..."))
            brand_folder = self.ensure_brand_folder()
            
            # Step 2: Initialize/load current.json
            self.root.after(0, lambda: self.update_log("Loading current.json..."))
            state = self.initialize_current_json()
            
            self.root.after(0, lambda: self.update_log(
                f"✓ Folders ready!\nCurrent page: {state['current_page']}"
            ))
            
            return True
            
        except Exception as e:
            self.root.after(0, lambda: self.update_log(f"✗ Folder creation failed:\n{str(e)}"))
            return False
    
    def run_update_current_data_process(self):
        """Process 2: Update current data - fetch products if needed"""
        try:
            # Check if current_page_data is empty or needs refresh
            if not self.current_state.get("current_page_data"):
                self.root.after(0, lambda: self.update_log(
                    f"Fetching products for page {self.current_state['current_page']}..."
                ))
                
                # Update the page variable to match current_page
                self.current_page = self.current_state['current_page']
                self.page_var.set(str(self.current_page))
                
                # Fetch products synchronously
                fetch_success = self.fetch_products_sync()
                
                if not fetch_success:
                    self.root.after(0, lambda: self.update_log(
                        "✗ Failed to fetch products."
                    ))
                    return False
                
                self.root.after(0, lambda: self.update_log(
                    f"✓ Fetched {len(self.products)} products for page {self.current_page}"
                ))
            else:
                self.root.after(0, lambda: self.update_log(
                    f"✓ Current data already loaded ({len(self.current_state['current_page_data'])} products)"
                ))
            
            return True
            
        except Exception as e:
            self.root.after(0, lambda: self.update_log(f"✗ Data update failed:\n{str(e)}"))
            return False
    
    def run_submission_process(self):
        """Process 4: Submission - open browser, navigate to ChatGPT, paste and submit"""
        try:
            import time
            import pyautogui
            
            # Step 1: Open browser and navigate to ChatGPT
            self.root.after(0, lambda: self.update_log("Opening browser and navigating to ChatGPT..."))
            result = find_and_click_chrome()
            
            if not result:
                self.root.after(0, lambda: self.update_log("✗ Could not launch browser."))
                return False
            
            self.root.after(0, lambda: self.update_log("✓ Browser opened. Waiting for input field..."))
            
            # Step 2: Scan for input_field_ready.png as indicator that page is ready
            input_ready_image = os.path.join(os.path.dirname(os.path.abspath(__file__)), "input_field_ready.png")
            input_field_image = os.path.join(os.path.dirname(os.path.abspath(__file__)), "input_field.png")
            
            if not os.path.exists(input_ready_image):
                self.root.after(0, lambda: self.update_log("✗ Missing: input_field_ready.png"))
                return False
            if not os.path.exists(input_field_image):
                self.root.after(0, lambda: self.update_log("✗ Missing: input_field.png"))
                return False
            
            max_retries = 5
            wait_seconds = 2
            page_ready = False
            
            for attempt in range(1, max_retries + 1):
                self.root.after(0, lambda a=attempt: self.update_log(f"Checking if page is ready... (attempt {a}/{max_retries})"))
                
                try:
                    ready_indicator = pyautogui.locateOnScreen(input_ready_image, confidence=0.8)
                    
                    if ready_indicator:
                        self.root.after(0, lambda: self.update_log("✓ Page is ready!"))
                        page_ready = True
                        break
                except Exception as scan_err:
                    self.root.after(0, lambda: self.update_log(f"Scan attempt failed..."))
                
                if attempt < max_retries:
                    time.sleep(wait_seconds)
            
            if not page_ready:
                self.root.after(0, lambda: self.update_log(f"✗ Page not ready after {max_retries} attempts."))
                return False
            
            # Step 3: Now find and click on input_field.png
            self.root.after(0, lambda: self.update_log("Locating input field to click..."))
            input_location = pyautogui.locateOnScreen(input_field_image, confidence=0.8)
            
            if not input_location:
                self.root.after(0, lambda: self.update_log("✗ Could not locate input field to click."))
                return False
            
            center_x, center_y = pyautogui.center(input_location)
            self.root.after(0, lambda: self.update_log("Clicking input field..."))
            pyautogui.moveTo(center_x, center_y, duration=0.3)
            time.sleep(0.2)
            pyautogui.click()
            time.sleep(0.3)
            
            # Step 4: Paste clipboard content (Ctrl+V)
            self.root.after(0, lambda: self.update_log("Pasting clipboard content..."))
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.3)
            
            # Step 5: Press Enter to submit
            self.root.after(0, lambda: self.update_log("Submitting..."))
            pyautogui.press('enter')
            
            self.root.after(0, lambda: self.update_log("✓ Submitted successfully!"))
            return True
                
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda msg=error_msg: self.update_log(f"✗ Submission failed:\n{msg}"))
            return False
    
    def run_confirm_submission_process(self):
        """Process 5: Confirm Submission - scan for indicator images"""
        try:
            import time
            import pyautogui
            
            # Image paths for submission indicators
            answer_now_image = os.path.join(os.path.dirname(os.path.abspath(__file__)), "submission_indicator_answer_now.png")
            stop_image = os.path.join(os.path.dirname(os.path.abspath(__file__)), "submission_indicator_stop.png")
            
            # Check if images exist
            if not os.path.exists(answer_now_image):
                self.root.after(0, lambda: self.update_log(f"✗ Missing: submission_indicator_answer_now.png"))
                return False
            if not os.path.exists(stop_image):
                self.root.after(0, lambda: self.update_log(f"✗ Missing: submission_indicator_stop.png"))
                return False
            
            max_retries = 5
            wait_seconds = 5
            
            for attempt in range(1, max_retries + 1):
                self.root.after(0, lambda a=attempt: self.update_log(f"Checking for response... (attempt {a}/{max_retries})"))
                
                try:
                    # Check for both indicator images
                    answer_now_found = pyautogui.locateOnScreen(answer_now_image, confidence=0.8)
                    stop_found = pyautogui.locateOnScreen(stop_image, confidence=0.8)
                    
                    if answer_now_found and stop_found:
                        self.root.after(0, lambda: self.update_log("✓ Submission confirmed! Both indicators found."))
                        
                        # Update product status to "submitted"
                        self.update_product_status("submitted")
                        self.root.after(0, lambda: self.update_log("✓ Product status updated to 'submitted'"))
                        
                        return True
                    elif answer_now_found:
                        self.root.after(0, lambda: self.update_log(f"Found 'Answer Now' indicator, waiting for 'Stop'..."))
                    elif stop_found:
                        self.root.after(0, lambda: self.update_log(f"Found 'Stop' indicator, waiting for 'Answer Now'..."))
                    else:
                        self.root.after(0, lambda: self.update_log(f"No indicators found yet..."))
                        
                except Exception as scan_error:
                    error_msg = str(scan_error)
                    self.root.after(0, lambda msg=error_msg: self.update_log(f"Scan error: {msg}"))
                
                # Wait before next attempt (except on last attempt)
                if attempt < max_retries:
                    time.sleep(wait_seconds)
            
            self.root.after(0, lambda: self.update_log(f"✗ Could not confirm submission after {max_retries} attempts."))
            return False
                
        except Exception as e:
            self.root.after(0, lambda: self.update_log(f"✗ Confirm failed:\n{str(e)}"))
            return False
    
    def run_clipboard_process(self):
        """Process 3: Clipboard - copy current product data to clipboard"""
        try:
            # Step 1: Verify current_page_data exists
            if not self.current_state.get("current_page_data"):
                self.root.after(0, lambda: self.update_log("✗ No product data available."))
                return False
            
            # Step 2: Find the product with status "current"
            current_product = None
            for product in self.current_state["current_page_data"]:
                if product.get("status") == "current":
                    current_product = product
                    break
            
            if not current_product:
                self.root.after(0, lambda: self.update_log("✗ No product marked as 'current'."))
                return False
            
            # Step 3: Prepare clipboard data
            clipboard_text = f"""InventoryID: {current_product.get('InventoryID', 'N/A')}
Brand: {current_product.get('Brand', 'N/A')}
Model: {current_product.get('Model', 'N/A')}
SKU: {current_product.get('SKU', 'N/A')}"""
            
            # Step 4: Copy to clipboard
            self.root.clipboard_clear()
            self.root.clipboard_append(clipboard_text)
            self.root.update()  # Required to finalize clipboard operation
            
            self.root.after(0, lambda: self.update_log(
                f"✓ Copied to clipboard:\n{current_product.get('SKU', 'N/A')} - {current_product.get('Model', 'N/A')[:40]}"
            ))
            
            print(f"Copied to clipboard:\n{clipboard_text}")
            
            return True
            
        except Exception as e:
            self.root.after(0, lambda: self.update_log(f"✗ Clipboard failed:\n{str(e)}"))
            return False
    
    def fetch_products_sync(self):
        """Fetch products synchronously (for use in automation process)"""
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
                    
                    # Prepare page data with status field for first product
                    page_data = []
                    for i, product in enumerate(self.products):
                        product_data = {
                            "InventoryID": product.get("InventoryID", ""),
                            "Brand": product.get("Brand", ""),
                            "Model": product.get("Model", ""),
                            "SKU": product.get("SKU", "")
                        }
                        
                        # Add status "current" to the first product
                        if i == 0:
                            product_data["status"] = "current"
                        
                        page_data.append(product_data)
                    
                    # Update current.json with the fetched products
                    self.update_current_json(page_data=page_data)
                    
                    # Update product list on main thread
                    self.root.after(0, self.update_product_list)
                    return True
                else:
                    return False
            else:
                return False
                
        except Exception as e:
            print(f"Error fetching products: {e}")
            return False
    

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
