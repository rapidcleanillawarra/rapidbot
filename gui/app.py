# Main GUI Application
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import os

from config import COLORS, PRODUCTS_FOLDER, DEFAULT_ACTIVE_TABS
from utils.json_manager import JsonManager
from utils.api_client import ApiClient
from processes import (
    FoldersProcess,
    DataProcess,
    ClipboardProcess,
    SubmissionProcess,
    ConfirmProcess,
    TabsProcess
)


class ChromeClickerApp:
    """Main application GUI for RapidBot automation."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("RapidBot - Chrome Clicker")
        self.root.geometry("900x750")
        self.root.resizable(True, True)
        
        # Colors
        self.bg_color = COLORS["bg"]
        self.card_color = COLORS["card"]
        self.accent_color = COLORS["accent"]
        self.highlight_color = COLORS["highlight"]
        self.text_color = COLORS["text"]
        self.success_color = COLORS["success"]
        self.warning_color = COLORS["warning"]
        
        self.root.configure(bg=self.bg_color)
        
        # State
        self.is_running = False
        self.brands = []
        self.selected_brand_id = None
        self.selected_brand_name = None
        self.products = []
        self.current_page = 0
        self.products_per_page = 10
        
        # Managers
        self.json_manager = JsonManager(PRODUCTS_FOLDER)
        self.api_client = ApiClient()
        
        # Initialize processes
        self._init_processes()
        
        # Create UI
        self.create_widgets()
        self.check_image_status()
        
        # Fetch brands on startup
        self.fetch_brands_async()
    
    def _init_processes(self):
        """Initialize all process instances."""
        self.process_1 = FoldersProcess(self)
        self.process_2 = DataProcess(self)
        self.process_3 = ClipboardProcess(self)
        self.process_4 = SubmissionProcess(self)
        self.process_5 = ConfirmProcess(self)
        self.process_6 = TabsProcess(self)
    
    def create_widgets(self):
        """Create all GUI widgets."""
        # Main container
        main_frame = tk.Frame(self.root, bg=self.bg_color, padx=30, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        self._create_title(main_frame)
        
        # Two-column layout
        columns_frame = tk.Frame(main_frame, bg=self.bg_color)
        columns_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left column - Controls
        left_column = tk.Frame(columns_frame, bg=self.bg_color)
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self._create_brand_section(left_column)
        self._create_fetch_section(left_column)
        self._create_status_section(left_column)
        self._create_log_section(left_column)
        self._create_buttons_section(left_column)
        self._create_footer(left_column)
        
        # Right column - Product list
        right_column = tk.Frame(columns_frame, bg=self.bg_color)
        right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        self._create_product_section(right_column)
    
    def _create_title(self, parent):
        """Create title section."""
        tk.Label(
            parent, text="🤖 RapidBot",
            font=("Segoe UI", 24, "bold"),
            fg=self.highlight_color, bg=self.bg_color
        ).pack(pady=(0, 5))
        
        tk.Label(
            parent, text="ChatGPT Auto-Navigator",
            font=("Segoe UI", 12),
            fg=self.text_color, bg=self.bg_color
        ).pack(pady=(0, 20))
    
    def _create_brand_section(self, parent):
        """Create brand selection section."""
        frame = tk.Frame(parent, bg=self.card_color, padx=20, pady=15)
        frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(
            frame, text="Select Brand",
            font=("Segoe UI", 10, "bold"),
            fg="#888", bg=self.card_color
        ).pack(anchor=tk.W, pady=(0, 5))
        
        controls = tk.Frame(frame, bg=self.card_color)
        controls.pack(fill=tk.X)
        
        self.brand_var = tk.StringVar()
        self.brand_dropdown = ttk.Combobox(
            controls, textvariable=self.brand_var,
            state="readonly", font=("Segoe UI", 10), width=20
        )
        self.brand_dropdown.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.brand_dropdown.bind("<<ComboboxSelected>>", self.on_brand_selected)
        
        tk.Button(
            controls, text="🔄", font=("Segoe UI", 12),
            fg="white", bg=self.accent_color,
            relief=tk.FLAT, cursor="hand2", padx=10,
            command=self.fetch_brands_async
        ).pack(side=tk.LEFT, padx=(5, 0))
        
        self.brand_status = tk.Label(
            frame, text="Loading brands...",
            font=("Segoe UI", 8), fg="#888", bg=self.card_color
        )
        self.brand_status.pack(anchor=tk.W, pady=(5, 0))
    
    def _create_fetch_section(self, parent):
        """Create product fetch section."""
        frame = tk.Frame(parent, bg=self.card_color, padx=20, pady=15)
        frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(
            frame, text="Fetch Products",
            font=("Segoe UI", 10, "bold"),
            fg="#888", bg=self.card_color
        ).pack(anchor=tk.W, pady=(0, 5))
        
        controls = tk.Frame(frame, bg=self.card_color)
        controls.pack(fill=tk.X)
        
        tk.Label(
            controls, text="Page:",
            font=("Segoe UI", 9), fg=self.text_color, bg=self.card_color
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        self.page_var = tk.StringVar(value="0")
        self.page_entry = tk.Entry(
            controls, textvariable=self.page_var,
            font=("Segoe UI", 10), width=5,
            bg="#0f3460", fg=self.text_color,
            insertbackground=self.text_color, relief=tk.FLAT
        )
        self.page_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(
            controls, text="🔍 Fetch Products",
            font=("Segoe UI", 10, "bold"),
            fg="white", bg="#2196F3",
            relief=tk.FLAT, cursor="hand2", padx=15, pady=5,
            command=self.fetch_products_button_click
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def _create_status_section(self, parent):
        """Create status section."""
        frame = tk.Frame(parent, bg=self.card_color, padx=20, pady=15)
        frame.pack(fill=tk.X, pady=(0, 20))
        
        header = tk.Frame(frame, bg=self.card_color)
        header.pack(fill=tk.X)
        
        tk.Label(
            header, text="Status",
            font=("Segoe UI", 10, "bold"),
            fg="#888", bg=self.card_color
        ).pack(side=tk.LEFT)
        
        self.status_indicator = tk.Label(
            header, text="● Ready",
            font=("Segoe UI", 10, "bold"),
            fg=self.success_color, bg=self.card_color
        )
        self.status_indicator.pack(side=tk.RIGHT)
        
        self.image_status = tk.Label(
            frame, text="Ready to launch browser",
            font=("Segoe UI", 9), fg=self.success_color,
            bg=self.card_color, wraplength=250, justify=tk.LEFT
        )
        self.image_status.pack(fill=tk.X, pady=(10, 0))
        
        # Active tabs
        tabs_frame = tk.Frame(frame, bg=self.card_color)
        tabs_frame.pack(fill=tk.X, pady=(10, 0))
        
        tk.Label(
            tabs_frame, text="Active Tabs:",
            font=("Segoe UI", 9, "bold"),
            fg="#888", bg=self.card_color
        ).pack(side=tk.LEFT)
        
        self.active_tabs_var = tk.StringVar(value=str(DEFAULT_ACTIVE_TABS))
        self.active_tabs_entry = tk.Entry(
            tabs_frame, textvariable=self.active_tabs_var,
            font=("Segoe UI", 10), width=5,
            bg="#0f3460", fg=self.text_color,
            insertbackground=self.text_color, relief=tk.FLAT
        )
        self.active_tabs_entry.pack(side=tk.LEFT, padx=(5, 0))
    
    def _create_log_section(self, parent):
        """Create log section."""
        frame = tk.Frame(parent, bg=self.accent_color, padx=10, pady=10)
        frame.pack(fill=tk.X, pady=(0, 20))
        
        self.log_label = tk.Label(
            frame, text="Click 'Start' to open ChatGPT in your browser",
            font=("Consolas", 9), fg=self.text_color,
            bg=self.accent_color, wraplength=280, justify=tk.LEFT
        )
        self.log_label.pack(fill=tk.X)
    
    def _create_buttons_section(self, parent):
        """Create buttons section."""
        frame = tk.Frame(parent, bg=self.bg_color)
        frame.pack(fill=tk.X)
        
        self.start_btn = tk.Button(
            frame, text="▶  Start",
            font=("Segoe UI", 12, "bold"),
            fg="white", bg=self.highlight_color,
            relief=tk.FLAT, cursor="hand2", padx=30, pady=10,
            command=self.start_clicking
        )
        self.start_btn.pack(fill=tk.X, pady=(0, 5))
        
        self.retry_btn = tk.Button(
            frame, text="🔄  Try Again",
            font=("Segoe UI", 12, "bold"),
            fg="white", bg="#ff9800",
            relief=tk.FLAT, cursor="hand2", padx=30, pady=10,
            command=self.start_clicking
        )
        # Hidden initially
        
        self.scan_btn = tk.Button(
            frame, text="🔍  Scan & Click Input Field",
            font=("Segoe UI", 11, "bold"),
            fg="white", bg="#2196F3",
            relief=tk.FLAT, cursor="hand2", padx=20, pady=8,
            command=self.scan_and_click
        )
        self.scan_btn.pack(fill=tk.X, pady=(0, 5))
        
        tk.Button(
            frame, text="✕  Exit",
            font=("Segoe UI", 11),
            fg=self.text_color, bg=self.accent_color,
            relief=tk.FLAT, cursor="hand2", padx=20, pady=8,
            command=self.root.quit
        ).pack(fill=tk.X)
    
    def _create_footer(self, parent):
        """Create footer."""
        tk.Label(
            parent, text="Browser Auto-Navigator",
            font=("Segoe UI", 8), fg="#666", bg=self.bg_color
        ).pack(pady=(15, 0))
    
    def _create_product_section(self, parent):
        """Create product list section."""
        frame = tk.Frame(parent, bg=self.card_color, padx=20, pady=15)
        frame.pack(fill=tk.BOTH, expand=True)
        
        header = tk.Frame(frame, bg=self.card_color)
        header.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            header, text="Products",
            font=("Segoe UI", 14, "bold"),
            fg=self.text_color, bg=self.card_color
        ).pack(side=tk.LEFT)
        
        self.product_count_label = tk.Label(
            header, text="",
            font=("Segoe UI", 10), fg="#888", bg=self.card_color
        )
        self.product_count_label.pack(side=tk.RIGHT)
        
        container = tk.Frame(frame, bg=self.card_color)
        container.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.product_listbox = tk.Listbox(
            container, font=("Consolas", 9),
            bg="#0f3460", fg=self.text_color,
            selectbackground=self.highlight_color,
            selectforeground="white", relief=tk.FLAT,
            yscrollcommand=scrollbar.set
        )
        self.product_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.product_listbox.yview)
        
        self.product_status_label = tk.Label(
            frame, text="Select a brand and click 'Fetch Products'",
            font=("Segoe UI", 9), fg="#888", bg=self.card_color
        )
        self.product_status_label.pack(anchor=tk.W, pady=(10, 0))
    
    # === Status Methods ===
    
    def check_image_status(self):
        """Check browser availability."""
        self.image_status.config(
            text="✓ Ready to navigate to ChatGPT",
            fg=self.success_color
        )
    
    def update_log(self, message):
        """Update the log label."""
        self.log_label.config(text=message)
        self.root.update()
    
    def update_status(self, status, color):
        """Update the status indicator."""
        self.status_indicator.config(text=status, fg=color)
        self.root.update()
    
    def update_active_tabs(self, count):
        """Update the active tabs counter."""
        self.active_tabs_var.set(str(count))
        self.root.update()
    
    def show_retry_button(self):
        """Show the retry button."""
        self.start_btn.pack_forget()
        self.retry_btn.pack(fill=tk.X, pady=(0, 5))
    
    # === Main Process Flow ===
    
    def start_clicking(self):
        """Start the clicking process."""
        if self.is_running:
            return
        
        if not self.selected_brand_name:
            messagebox.showwarning("No Brand Selected", "Please select a brand before starting!")
            return
        
        self.is_running = True
        self.start_btn.config(state=tk.DISABLED, text="⏳ Starting...")
        self.update_status("● Starting...", self.warning_color)
        self.update_log("Initializing process...")
        
        thread = threading.Thread(target=self.run_clicker)
        thread.daemon = True
        thread.start()
    
    def run_clicker(self):
        """Run the complete process flow."""
        try:
            # Process 1: Create Folders
            self.update_status("● Creating Folders...", self.warning_color)
            if not self.process_1.run():
                self.update_status("● Folder Creation Failed", self.highlight_color)
                self.root.after(0, self.show_retry_button)
                return
            
            # Process 2: Update Current Data
            self.update_status("● Updating Data...", self.warning_color)
            if not self.process_2.run():
                self.update_status("● Data Update Failed", self.highlight_color)
                self.root.after(0, self.show_retry_button)
                return
            
            # Process 3: Clipboard
            self.update_status("● Copying to Clipboard...", self.warning_color)
            if not self.process_3.run():
                self.update_status("● Clipboard Failed", self.highlight_color)
                self.root.after(0, self.show_retry_button)
                return
            
            # Process 4: Submission
            self.update_status("● Submitting...", self.warning_color)
            if not self.process_4.run():
                self.update_status("● Submission Failed", self.highlight_color)
                self.root.after(0, self.show_retry_button)
                return
            
            # Process 5: Confirm Submission
            self.update_status("● Confirming...", self.warning_color)
            if not self.process_5.run():
                self.update_status("● Confirm Failed", self.warning_color)
                self.root.after(0, self.show_retry_button)
                return
            
            # Process 6: Check Tabs
            self.update_status("● Checking Tabs...", self.warning_color)
            if self.process_6.run():
                self.update_status("● Success!", self.success_color)
            else:
                self.update_status("● Tab Check Failed", self.warning_color)
            
            self.root.after(0, self.show_retry_button)
            
        except Exception as e:
            self.update_status("● Error", self.highlight_color)
            self.update_log(f"Error: {str(e)}")
            self.root.after(0, self.show_retry_button)
        finally:
            self.is_running = False
            self.root.after(0, lambda: self.start_btn.config(state=tk.NORMAL, text="▶  Start"))
    
    def scan_and_click(self):
        """Scan for and click the input field."""
        if self.is_running:
            return
        
        self.is_running = True
        self.scan_btn.config(state=tk.DISABLED, text="🔍 Scanning...")
        
        thread = threading.Thread(target=self._run_scan_and_click)
        thread.daemon = True
        thread.start()
    
    def _run_scan_and_click(self):
        """Run the scan and click operation."""
        try:
            from click_chrome import is_chrome_active, bring_chrome_to_front, find_and_click_image
            import time
            
            self.update_status("● Checking Chrome...", self.warning_color)
            
            if not is_chrome_active():
                self.update_log("Chrome not active. Bringing to front...")
                bring_chrome_to_front()
                time.sleep(1)
            else:
                bring_chrome_to_front()
                time.sleep(0.5)
            
            self.update_status("● Scanning...", self.warning_color)
            self.update_log("Scanning for input field...")
            
            if find_and_click_image():
                self.update_status("● Success!", self.success_color)
                self.update_log("✓ Successfully found and clicked input field!")
            else:
                self.update_status("● Not Found", self.warning_color)
                self.update_log("✗ Could not find input field.")
                
        except Exception as e:
            self.update_status("● Error", self.highlight_color)
            self.update_log(f"Error: {str(e)}")
        finally:
            self.is_running = False
            self.root.after(0, lambda: self.scan_btn.config(
                state=tk.NORMAL, text="🔍  Scan & Click Input Field"
            ))
    
    # === Brand Methods ===
    
    def fetch_brands_async(self):
        """Fetch brands asynchronously."""
        self.brand_status.config(text="Loading brands...")
        thread = threading.Thread(target=self._fetch_brands)
        thread.daemon = True
        thread.start()
    
    def _fetch_brands(self):
        """Fetch brands from API."""
        brands = self.api_client.fetch_brands()
        
        if brands:
            self.brands = brands
            self.root.after(0, self._update_brand_dropdown)
            self.root.after(0, lambda: self.brand_status.config(
                text=f"✓ {len(brands)} brands loaded"
            ))
        else:
            self.root.after(0, lambda: self.brand_status.config(
                text="✗ Could not load brands"
            ))
    
    def _update_brand_dropdown(self):
        """Update brand dropdown with fetched brands."""
        brand_names = [b.get("name", "Unknown") for b in self.brands]
        self.brand_dropdown["values"] = brand_names
        if brand_names:
            self.brand_dropdown.current(0)
            self.on_brand_selected(None)
    
    def on_brand_selected(self, event):
        """Handle brand selection."""
        selected = self.brand_var.get()
        for brand in self.brands:
            if brand.get("name") == selected:
                self.selected_brand_id = brand.get("id")
                self.selected_brand_name = brand.get("name")
                print(f"Selected Brand: {self.selected_brand_name} (ID: {self.selected_brand_id})")
                break
    
    # === Product Methods ===
    
    def fetch_products_button_click(self):
        """Handle fetch products button click."""
        if not self.selected_brand_name:
            messagebox.showwarning("No Brand", "Please select a brand first!")
            return
        
        try:
            self.current_page = int(self.page_var.get())
        except ValueError:
            self.current_page = 0
            self.page_var.set("0")
        
        self.product_status_label.config(text="Fetching products...")
        
        thread = threading.Thread(target=self._fetch_products)
        thread.daemon = True
        thread.start()
    
    def _fetch_products(self):
        """Fetch products from API."""
        products = self.api_client.fetch_products(
            self.selected_brand_name,
            self.current_page,
            self.products_per_page
        )
        
        if products:
            self.products = products
            self.root.after(0, self._update_product_list)
            self.root.after(0, lambda: self.product_status_label.config(
                text=f"✓ {len(products)} products loaded"
            ))
        else:
            self.root.after(0, lambda: self.product_status_label.config(
                text="✗ No products found"
            ))
    
    def _update_product_list(self):
        """Update product listbox."""
        self.product_listbox.delete(0, tk.END)
        
        for product in self.products:
            sku = product.get('SKU', 'N/A')
            model = product.get('Model', 'N/A')[:50]
            inv_id = product.get('InventoryID', 'N/A')
            
            text = f"{sku:20} | {model:50} | ID: {inv_id}"
            self.product_listbox.insert(tk.END, text)
        
        self.product_count_label.config(text=f"({len(self.products)} items)")
    
    def fetch_products_sync(self):
        """Fetch products synchronously for automation."""
        products = self.api_client.fetch_products(
            self.selected_brand_name,
            self.current_page,
            self.products_per_page
        )
        
        if products:
            self.products = products
            
            # Add status to products and save to JSON
            page_data = []
            for i, product in enumerate(products):
                product_with_status = {
                    "InventoryID": product.get("InventoryID"),
                    "Brand": product.get("Brand"),
                    "Model": product.get("Model"),
                    "SKU": product.get("SKU"),
                    "status": "current" if i == 0 else None
                }
                page_data.append(product_with_status)
            
            self.json_manager.update_current_json(
                page=self.current_page,
                page_data=page_data
            )
            
            self.root.after(0, self._update_product_list)
            return True
        
        return False
