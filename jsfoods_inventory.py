"""
JS Foods Inventory Management
Advanced inventory tracking and management
"""

import customtkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import subprocess
from datetime import datetime
from jsfoods_database import db

class InventoryManager(tk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("JS Foods - Inventory Management")
        self.geometry("1200x700")
        self.resizable(True, True)
        
        tk.set_appearance_mode("light")
        tk.set_default_color_theme("blue")
        
        self.setup_ui()
        self.load_inventory()
        self.load_low_stock()
    
    def setup_ui(self):
        """Setup inventory management UI"""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header
        header_frame = tk.CTkFrame(self, height=80)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        header_frame.grid_propagate(False)
        
        tk.CTkLabel(
            header_frame,
            text="📦 Inventory Management",
            font=("Helvetica", 24, "bold"),
            text_color="#2E7D32"
        ).pack(side="left", padx=20)
        
        # Quick stats
        stats_frame = tk.CTkFrame(header_frame, fg_color="transparent")
        stats_frame.pack(side="right", padx=20)
        
        self.stats_labels = {}
        stats = [
            ("📊", "total_value", "Total Value"),
            ("📈", "total_items", "Total Items"),
            ("⚠️", "low_stock", "Low Stock")
        ]
        
        for icon, key, label in stats:
            stat_frame = tk.CTkFrame(stats_frame, fg_color="transparent")
            stat_frame.pack(side="left", padx=15)
            
            tk.CTkLabel(
                stat_frame,
                text=icon,
                font=("Helvetica", 20)
            ).pack()
            
            self.stats_labels[key] = tk.CTkLabel(
                stat_frame,
                text="0",
                font=("Helvetica", 16, "bold")
            )
            self.stats_labels[key].pack()
            
            tk.CTkLabel(
                stat_frame,
                text=label,
                font=("Helvetica", 10),
                text_color="#666666"
            ).pack()
        
        # Main content - Tab view
        self.tabview = tk.CTkTabview(self)
        self.tabview.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        
        # Create tabs
        tabs = [
            "📋 All Inventory",
            "⚠️ Low Stock Alerts",
            "📥 Receive Stock",
            "📤 Adjust Stock",
            "📊 Stock Reports"
        ]
        
        for tab in tabs:
            self.tabview.add(tab)
        
        # Setup each tab
        self.setup_inventory_tab()
        self.setup_alerts_tab()
        self.setup_receive_tab()
        self.setup_adjust_tab()
        self.setup_reports_tab()
        
        # Navigation
        nav_frame = tk.CTkFrame(self, height=50)
        nav_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
        nav_frame.grid_propagate(False)
        
        tk.CTkButton(
            nav_frame,
            text="← Back to Main Menu",
            command=self.go_back,
            fg_color="transparent",
            hover_color="#E8F5E9",
            text_color="#2E7D32",
            font=("Helvetica", 12)
        ).pack(side="left", padx=20)
        
        tk.CTkButton(
            nav_frame,
            text="🔄 Refresh All",
            command=self.refresh_all,
            width=120
        ).pack(side="right", padx=20)
    
    def load_inventory(self):
        """Load inventory data and statistics"""
        try:
            conn = sqlite3.connect('jsfoods.db')
            cursor = conn.cursor()
            
            # Get total inventory value
            cursor.execute("""
                SELECT SUM(p.current_stock_kg * p.price_per_kg) as total_value,
                       COUNT(*) as total_items
                FROM products p
                WHERE p.is_active = 1
            """)
            
            result = cursor.fetchone()
            total_value = result[0] or 0
            total_items = result[1] or 0
            
            # Get low stock count
            low_stock = db.get_low_stock_items()
            low_count = len(low_stock)
            
            # Update stats
            self.stats_labels['total_value'].configure(text=f"£{total_value:.2f}")
            self.stats_labels['total_items'].configure(text=str(total_items))
            self.stats_labels['low_stock'].configure(text=str(low_count))
            
        except sqlite3.Error as e:
            print(f"Inventory stats error: {e}")
    
    def load_low_stock(self):
        """Load low stock items"""
        try:
            low_stock = db.get_low_stock_items()
            
            # Update low stock tab
            tab = self.tabview.tab("⚠️ Low Stock Alerts")
            
            # Clear existing content
            for widget in tab.winfo_children():
                widget.destroy()
            
            if not low_stock:
                tk.CTkLabel(
                    tab,
                    text="✅ No low stock alerts! All inventory levels are good.",
                    font=("Helvetica", 16),
                    text_color="#4CAF50"
                ).pack(expand=True)
                return
            
            # Create scrollable frame for alerts
            canvas = tk.CTkCanvas(tab, bg="white")
            canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
            
            scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
            scrollbar.pack(side="right", fill="y")
            
            canvas.configure(yscrollcommand=scrollbar.set)
            
            alerts_frame = tk.CTkFrame(canvas)
            canvas.create_window((0, 0), window=alerts_frame, anchor="nw")
            
            # Add alert cards
            for item in low_stock:
                alert_frame = tk.CTkFrame(alerts_frame, height=100)
                alert_frame.pack(fill="x", pady=5, padx=10)
                alert_frame.grid_propagate(False)
                
                # Severity color
                stock_percent = item['current_stock_kg'] / item['min_stock_level']
                if stock_percent <= 0.2:
                    severity_color = "#F44336"
                    severity_text = "CRITICAL"
                elif stock_percent <= 0.5:
                    severity_color = "#FF9800"
                    severity_text = "HIGH"
                else:
                    severity_color = "#FFC107"
                    severity_text = "MEDIUM"
                
                # Product info
                tk.CTkLabel(
                    alert_frame,
                    text=item['name'],
                    font=("Helvetica", 14, "bold")
                ).place(x=20, y=15)
                
                tk.CTkLabel(
                    alert_frame,
                    text=f"Category: {item['category']}",
                    font=("Helvetica", 11),
                    text_color="#666666"
                ).place(x=20, y=40)
                
                # Stock info
                tk.CTkLabel(
                    alert_frame,
                    text=f"Current: {item['current_stock_kg']} {item['unit']}",
                    font=("Helvetica", 11, "bold")
                ).place(x=200, y=15)
                
                tk.CTkLabel(
                    alert_frame,
                    text=f"Minimum: {item['min_stock_level']} {item['unit']}",
                    font=("Helvetica", 11)
                ).place(x=200, y=40)
                
                # Severity badge
                tk.CTkLabel(
                    alert_frame,
                    text=severity_text,
                    font=("Helvetica", 10, "bold"),
                    text_color="white",
                    fg_color=severity_color,
                    corner_radius=10,
                    width=80,
                    height=25
                ).place(x=350, y=15)
                
                # Reorder button
                tk.CTkButton(
                    alert_frame,
                    text="Reorder",
                    command=lambda p=item: self.reorder_product(p),
                    width=80,
                    height=30,
                    fg_color="#2E7D32",
                    hover_color="#1B5E20"
                ).place(x=450, y=35)
            
            # Update canvas scroll region
            alerts_frame.update_idletasks()
            canvas.configure(scrollregion=canvas.bbox("all"))
            
        except sqlite3.Error as e:
            print(f"Low stock load error: {e}")
    
    def setup_inventory_tab(self):
        """Setup main inventory tab"""
        tab = self.tabview.tab("📋 All Inventory")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)
        
        # Inventory frame
        inv_frame = tk.CTkFrame(tab)
        inv_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        inv_frame.grid_columnconfigure(0, weight=1)
        inv_frame.grid_rowconfigure(1, weight=1)
        
        # Controls
        controls_frame = tk.CTkFrame(inv_frame)
        controls_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        tk.CTkButton(
            controls_frame,
            text="+ Add Product",
            command=self.add_product,
            width=120,
            fg_color="#2E7D32",
            hover_color="#1B5E20"
        ).pack(side="left", padx=5)
        
        tk.CTkButton(
            controls_frame,
            text="📥 Receive Stock",
            command=lambda: self.tabview.set("📥 Receive Stock"),
            width=120
        ).pack(side="left", padx=5)
        
        tk.CTkButton(
            controls_frame,
            text="📤 Adjust Stock",
            command=lambda: self.tabview.set("📤 Adjust Stock"),
            width=120
        ).pack(side="left", padx=5)
        
        # Search and filter
        filter_frame = tk.CTkFrame(controls_frame, fg_color="transparent")
        filter_frame.pack(side="right", padx=20)
        
        tk.CTkLabel(filter_frame, text="Category:").pack(side="left", padx=5)
        self.category_filter = tk.StringVar(value="All")
        categories = ["All", "Beef", "Pork", "Poultry", "Lamb", "Other"]
        category_combo = tk.CTkComboBox(
            filter_frame,
            values=categories,
            variable=self.category_filter,
            command=self.filter_inventory,
            width=100
        )
        category_combo.pack(side="left", padx=5)
        
        # Inventory table
        self.inv_tree = ttk.Treeview(
            inv_frame,
            columns=("ID", "Name", "Category", "Stock", "Unit", "Price", "Value", "Status"),
            show="headings",
            height=15
        )
        self.inv_tree.grid(row=1, column=0, sticky="nsew")
        
        # Configure scrollbar
        scrollbar = ttk.Scrollbar(inv_frame, orient="vertical", command=self.inv_tree.yview)
        scrollbar.grid(row=1, column=1, sticky="ns")
        self.inv_tree.configure(yscrollcommand=scrollbar.set)
        
        # Configure columns
        columns = [
            ("ID", 60, "center"),
            ("Name", 150, "w"),
            ("Category", 100, "center"),
            ("Stock", 80, "center"),
            ("Unit", 60, "center"),
            ("Price", 80, "center"),
            ("Value", 90, "center"),
            ("Status", 100, "center")
        ]
        
        for col, width, anchor in columns:
            self.inv_tree.heading(col, text=col)
            self.inv_tree.column(col, width=width, anchor=anchor)
        
        # Load initial inventory
        self.filter_inventory()
    
    def filter_inventory(self, event=None):
        """Filter inventory by category"""
        try:
            category = self.category_filter.get()
            category = None if category == "All" else category
            
            products = db.get_products(category=category, active_only=False)
            
            # Clear existing items
            for item in self.inv_tree.get_children():
                self.inv_tree.delete(item)
            
            # Add products
            for product in products:
                stock = product['current_stock_kg']
                min_stock = product['min_stock_level']
                stock_value = stock * product['price_per_kg']
                
                # Determine status
                if stock <= 0:
                    status = "Out of Stock"
                    status_color = "red"
                elif stock <= min_stock * 0.2:
                    status = "Very Low"
                    status_color = "red"
                elif stock <= min_stock * 0.5:
                    status = "Low"
                    status_color = "orange"
                elif stock <= min_stock:
                    status = "Warning"
                    status_color = "#FFC107"
                else:
                    status = "Good"
                    status_color = "#4CAF50"
                
                # Determine active status
                if not product['is_active']:
                    status = "Inactive"
                    status_color = "#757575"
                
                self.inv_tree.insert("", "end", values=(
                    product['product_id'],
                    product['name'],
                    product['category'],
                    f"{stock:.1f}",
                    product['unit'],
                    f"£{product['price_per_kg']:.2f}",
                    f"£{stock_value:.2f}",
                    status
                ), tags=(status,))
                
                self.inv_tree.tag_configure(status, foreground=status_color)
                
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Could not load inventory: {e}")
    
    def add_product(self):
        """Add new product"""
        add_window = tk.CTkToplevel(self)
        add_window.title("Add New Product")
        add_window.geometry("500x600")
        add_window.transient(self)  # Set as transient to main window
        add_window.grab_set()  # Make it modal
        add_window.lift()  # Bring to front
        
        # Create main container with scrollbar
        main_container = tk.CTkFrame(add_window)
        main_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Create canvas and scrollbar
        canvas = tk.CTkCanvas(main_container, bg="white")
        canvas.pack(side="left", fill="both", expand=True, padx=(5, 0))
        
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Create frame inside canvas
        content_frame = tk.CTkFrame(canvas)
        canvas.create_window((0, 0), window=content_frame, anchor="nw")
        
        tk.CTkLabel(
            content_frame,
            text="Add New Product",
            font=("Helvetica", 20, "bold")
        ).pack(pady=20)
        
        # Form
        form_frame = tk.CTkFrame(content_frame)
        form_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Product name
        tk.CTkLabel(form_frame, text="Product Name:").pack(anchor="w", pady=(10, 0))
        name_entry = tk.CTkEntry(form_frame, height=35)
        name_entry.pack(fill="x", pady=(0, 10))
        
        # Category
        tk.CTkLabel(form_frame, text="Category:").pack(anchor="w", pady=(10, 0))
        category_var = tk.StringVar(value="Beef")
        category_combo = tk.CTkComboBox(
            form_frame,
            values=["Beef", "Pork", "Poultry", "Lamb", "Other"],
            variable=category_var
        )
        category_combo.pack(fill="x", pady=(0, 10))
        
        # Price
        tk.CTkLabel(form_frame, text="Price per kg:").pack(anchor="w", pady=(10, 0))
        price_entry = tk.CTkEntry(form_frame, height=35, placeholder_text="e.g., 12.50")
        price_entry.pack(fill="x", pady=(0, 10))
        
        # Initial stock
        tk.CTkLabel(form_frame, text="Initial Stock (kg):").pack(anchor="w", pady=(10, 0))
        stock_entry = tk.CTkEntry(form_frame, height=35, placeholder_text="e.g., 100")
        stock_entry.pack(fill="x", pady=(0, 10))
        
        # Minimum stock level
        tk.CTkLabel(form_frame, text="Minimum Stock Level (kg):").pack(anchor="w", pady=(10, 0))
        min_stock_entry = tk.CTkEntry(form_frame, height=35, placeholder_text="e.g., 20")
        min_stock_entry.pack(fill="x", pady=(0, 20))
        
        # Description (optional)
        tk.CTkLabel(form_frame, text="Description (optional):").pack(anchor="w", pady=(10, 0))
        desc_text = tk.CTkTextbox(form_frame, height=60)
        desc_text.pack(fill="x", pady=(0, 20))
        
        # Add button
        def create_product():
            try:
                # Validate inputs
                name = name_entry.get().strip()
                price_str = price_entry.get().strip()
                stock_str = stock_entry.get().strip()
                min_stock_str = min_stock_entry.get().strip()
                description = desc_text.get("1.0", "end-1c").strip()
                
                if not name:
                    messagebox.showerror("Error", "Product name is required")
                    return
                
                # Check if fields are empty
                if not price_str:
                    messagebox.showerror("Error", "Price is required")
                    return
                if not stock_str:
                    messagebox.showerror("Error", "Initial stock is required")
                    return
                if not min_stock_str:
                    messagebox.showerror("Error", "Minimum stock level is required")
                    return
                
                # Convert to numbers
                price = float(price_str)
                stock = float(stock_str)
                min_stock = float(min_stock_str)
                
                if price <= 0 or stock < 0 or min_stock < 0:
                    messagebox.showerror("Error", "Please enter valid positive numbers")
                    return
                
                # Save to database using direct SQL
                try:
                    conn = sqlite3.connect('jsfoods.db')
                    cursor = conn.cursor()
                    
                    # Insert new product
                    cursor.execute('''
                        INSERT INTO products 
                        (name, category, price_per_kg, current_stock_kg, min_stock_level, unit, description, is_active)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (name, category_var.get(), price, stock, min_stock, "kg", description, 1))
                    
                    conn.commit()
                    product_id = cursor.lastrowid
                    
                    # Record initial stock transaction
                    cursor.execute('''
                        INSERT INTO stock_transactions 
                        (product_id, transaction_type, quantity_kg, notes)
                        VALUES (?, ?, ?, ?)
                    ''', (product_id, "initial", stock, f"Initial stock for new product '{name}'"))
                    
                    conn.commit()
                    conn.close()
                    
                    messagebox.showinfo(
                        "Product Added",
                        f"Product '{name}' added successfully!\n\n"
                        f"Product ID: {product_id}\n"
                        f"Category: {category_var.get()}\n"
                        f"Price: £{price:.2f}/kg\n"
                        f"Initial Stock: {stock} kg\n"
                        f"Minimum Stock: {min_stock} kg"
                    )
                    
                    add_window.destroy()
                    self.filter_inventory()
                    self.load_inventory()
                    
                except sqlite3.Error as e:
                    messagebox.showerror("Database Error", f"Could not save product: {e}")
                    print(f"Database error: {e}")
                
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers for price and stock")
        
        tk.CTkButton(
            form_frame,
            text="Add Product",
            command=create_product,
            height=45,
            fg_color="#2E7D32",
            hover_color="#1B5E20"
        ).pack(fill="x", pady=(0, 20))
        
        # Update canvas scroll region
        content_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))
        
        # Bind mouse wheel for scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    def setup_alerts_tab(self):
        """Setup low stock alerts tab"""
        # Already handled in load_low_stock()
        pass
    
    def setup_receive_tab(self):
        """Setup receive stock tab"""
        tab = self.tabview.tab("📥 Receive Stock")
        
        # Create main container with scrollbar
        main_container = tk.CTkFrame(tab)
        main_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Create canvas and scrollbar
        canvas = tk.CTkCanvas(main_container, bg="white")
        canvas.pack(side="left", fill="both", expand=True, padx=(5, 0))
        
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Create frame inside canvas
        content_frame = tk.CTkFrame(canvas)
        canvas.create_window((0, 0), window=content_frame, anchor="nw")
        
        tk.CTkLabel(
            content_frame,
            text="Receive New Stock",
            font=("Helvetica", 20, "bold")
        ).pack(pady=20)
        
        # Receive form
        form_frame = tk.CTkFrame(content_frame)
        form_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Product selection
        tk.CTkLabel(form_frame, text="Select Product:").pack(anchor="w", pady=(10, 0))
        
        # Get products for dropdown
        try:
            products = db.get_products(active_only=True)
            product_names = [f"{p['product_id']}: {p['name']} ({p['category']})" for p in products]
            product_ids = [p['product_id'] for p in products]
        except:
            product_names = ["No products available"]
            product_ids = []
        
        # Create StringVar for combo box
        self.receive_product_var = tk.StringVar(value="Select a product..." if product_names else "No products available")
        product_combo = tk.CTkComboBox(
            form_frame, 
            values=product_names,
            variable=self.receive_product_var,
            state="readonly"
        )
        product_combo.pack(fill="x", pady=(0, 10))
        
        # Store product info for later use
        self.product_data = {pid: p for pid, p in zip(product_ids, products)}
        
        # Quantity
        tk.CTkLabel(form_frame, text="Quantity Received (kg):").pack(anchor="w", pady=(10, 0))
        quantity_entry = tk.CTkEntry(form_frame, height=35, placeholder_text="e.g., 50")
        quantity_entry.pack(fill="x", pady=(0, 10))
        
        # Supplier info
        tk.CTkLabel(form_frame, text="Supplier:").pack(anchor="w", pady=(10, 0))
        supplier_entry = tk.CTkEntry(form_frame, height=35, placeholder_text="Supplier name")
        supplier_entry.pack(fill="x", pady=(0, 10))
        
        # Batch/Lot number
        tk.CTkLabel(form_frame, text="Batch/Lot Number:").pack(anchor="w", pady=(10, 0))
        batch_entry = tk.CTkEntry(form_frame, height=35, placeholder_text="Optional")
        batch_entry.pack(fill="x", pady=(0, 10))
        
        # Notes
        tk.CTkLabel(form_frame, text="Notes:").pack(anchor="w", pady=(10, 0))
        notes_text = tk.CTkTextbox(form_frame, height=80)
        notes_text.pack(fill="x", pady=(0, 20))
        
        # Receive button
        def receive_stock():
            try:
                # Validate inputs
                product_text = product_combo.get()
                quantity_str = quantity_entry.get().strip()
                supplier = supplier_entry.get().strip()
                batch = batch_entry.get().strip()
                notes = notes_text.get("1.0", "end-1c").strip()
                
                if not product_text or product_text in ["Select a product...", "No products available"]:
                    messagebox.showerror("Error", "Please select a product")
                    return
                
                if not quantity_str:
                    messagebox.showerror("Error", "Quantity is required")
                    return
                
                try:
                    quantity = float(quantity_str)
                except ValueError:
                    messagebox.showerror("Error", "Please enter a valid number for quantity (e.g., 50)")
                    return
                
                if quantity <= 0:
                    messagebox.showerror("Error", "Quantity must be greater than 0")
                    return
                
                if not supplier:
                    messagebox.showerror("Error", "Supplier information is required")
                    return
                
                # Extract product ID
                product_id = int(product_text.split(":")[0])
                
                # Update database
                try:
                    conn = sqlite3.connect('jsfoods.db')
                    cursor = conn.cursor()
                    
                    # Get current stock
                    cursor.execute('SELECT current_stock_kg FROM products WHERE product_id = ?', (product_id,))
                    result = cursor.fetchone()
                    if not result:
                        messagebox.showerror("Error", "Product not found in database")
                        return
                    
                    current_stock = result[0]
                    new_stock = current_stock + quantity
                    
                    # Update product stock
                    cursor.execute('''
                        UPDATE products 
                        SET current_stock_kg = ?
                        WHERE product_id = ?
                    ''', (new_stock, product_id))
                    
                    # Record transaction
                    cursor.execute('''
                        INSERT INTO stock_transactions 
                        (product_id, transaction_type, quantity_kg, notes)
                        VALUES (?, ?, ?, ?)
                    ''', (product_id, "receive", quantity, f"Received from {supplier}. Batch: {batch}. {notes}"))
                    
                    conn.commit()
                    conn.close()
                    
                    messagebox.showinfo(
                        "Stock Received",
                        f"Stock received successfully!\n\n"
                        f"Product: {product_text}\n"
                        f"Quantity: {quantity} kg\n"
                        f"Supplier: {supplier}\n"
                        f"New Stock Level: {new_stock} kg\n\n"
                        "Stock levels have been updated."
                    )
                    
                    # Clear form
                    quantity_entry.delete(0, tk.END)
                    supplier_entry.delete(0, tk.END)
                    batch_entry.delete(0, tk.END)
                    notes_text.delete("1.0", tk.END)
                    
                    # Refresh inventory
                    self.filter_inventory()
                    self.load_inventory()
                    self.load_low_stock()
                    
                except sqlite3.Error as e:
                    messagebox.showerror("Database Error", f"Could not update stock: {e}")
                
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {str(e)}")
        
        tk.CTkButton(
            form_frame,
            text="Receive Stock",
            command=receive_stock,
            height=45,
            fg_color="#2E7D32",
            hover_color="#1B5E20"
        ).pack(fill="x", pady=(0, 20))
        
        # Update canvas scroll region
        content_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))
        
        # Bind mouse wheel for scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    def setup_adjust_tab(self):
        """Setup adjust stock tab"""
        tab = self.tabview.tab("📤 Adjust Stock")
        
        # Create main container with scrollbar
        main_container = tk.CTkFrame(tab)
        main_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Create canvas and scrollbar
        canvas = tk.CTkCanvas(main_container, bg="white")
        canvas.pack(side="left", fill="both", expand=True, padx=(5, 0))
        
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Create frame inside canvas
        content_frame = tk.CTkFrame(canvas)
        canvas.create_window((0, 0), window=content_frame, anchor="nw")
        
        tk.CTkLabel(
            content_frame,
            text="Adjust Stock Levels",
            font=("Helvetica", 20, "bold")
        ).pack(pady=20)
        
        # Adjust form
        form_frame = tk.CTkFrame(content_frame)
        form_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Product selection
        tk.CTkLabel(form_frame, text="Select Product:").pack(anchor="w", pady=(10, 0))
        
        # Get products for dropdown
        try:
            products = db.get_products(active_only=True)
            product_names = [f"{p['product_id']}: {p['name']} (Current: {p['current_stock_kg']} kg)" for p in products]
            product_ids = [p['product_id'] for p in products]
        except:
            product_names = ["No products available"]
            product_ids = []
        
        # Create StringVar for combo box
        self.adjust_product_var = tk.StringVar(value="Select a product..." if product_names else "No products available")
        product_combo = tk.CTkComboBox(
            form_frame, 
            values=product_names,
            variable=self.adjust_product_var,
            state="readonly"
        )
        product_combo.pack(fill="x", pady=(0, 10))
        
        # Store product info for later use
        self.adjust_product_data = {pid: p for pid, p in zip(product_ids, products)}
        
        # Adjustment type
        tk.CTkLabel(form_frame, text="Adjustment Type:").pack(anchor="w", pady=(10, 0))
        
        adjust_type = tk.StringVar(value="add")
        type_frame = tk.CTkFrame(form_frame, fg_color="transparent")
        type_frame.pack(fill="x", pady=(0, 10))
        
        tk.CTkRadioButton(
            type_frame,
            text="Add Stock (+)",
            variable=adjust_type,
            value="add"
        ).pack(side="left", padx=10)
        
        tk.CTkRadioButton(
            type_frame,
            text="Remove Stock (-)",
            variable=adjust_type,
            value="remove"
        ).pack(side="left", padx=10)
        
        # Quantity
        tk.CTkLabel(form_frame, text="Adjustment Amount (kg):").pack(anchor="w", pady=(10, 0))
        amount_entry = tk.CTkEntry(form_frame, height=35, placeholder_text="e.g., 10")
        amount_entry.pack(fill="x", pady=(0, 10))
        
        # Reason
        tk.CTkLabel(form_frame, text="Reason for Adjustment:").pack(anchor="w", pady=(10, 0))
        reason_var = tk.StringVar(value="correction")
        reason_combo = tk.CTkComboBox(
            form_frame,
            values=["correction", "waste", "damage", "theft", "other"],
            variable=reason_var,
            state="readonly"
        )
        reason_combo.pack(fill="x", pady=(0, 10))
        
        # Notes
        tk.CTkLabel(form_frame, text="Notes:").pack(anchor="w", pady=(10, 0))
        notes_text = tk.CTkTextbox(form_frame, height=80)
        notes_text.pack(fill="x", pady=(0, 20))
        
        # Adjust button
        def adjust_stock():
            try:
                # Validate inputs
                product_text = product_combo.get()
                amount_str = amount_entry.get().strip()
                reason = reason_var.get()
                notes = notes_text.get("1.0", "end-1c").strip()
                
                if not product_text or product_text in ["Select a product...", "No products available"]:
                    messagebox.showerror("Error", "Please select a product")
                    return
                
                if not amount_str:
                    messagebox.showerror("Error", "Adjustment amount is required")
                    return
                
                try:
                    amount = float(amount_str)
                except ValueError:
                    messagebox.showerror("Error", "Please enter a valid number for amount (e.g., 10)")
                    return
                
                if amount <= 0:
                    messagebox.showerror("Error", "Amount must be greater than 0")
                    return
                
                # Extract product ID
                product_id = int(product_text.split(":")[0])
                
                # Update database
                try:
                    conn = sqlite3.connect('jsfoods.db')
                    cursor = conn.cursor()
                    
                    # Get current stock
                    cursor.execute('SELECT current_stock_kg FROM products WHERE product_id = ?', (product_id,))
                    result = cursor.fetchone()
                    if not result:
                        messagebox.showerror("Error", "Product not found in database")
                        return
                    
                    current_stock = result[0]
                    
                    # Check if removing more than available
                    if adjust_type.get() == "remove" and amount > current_stock:
                        messagebox.showerror("Error", f"Cannot remove {amount} kg. Only {current_stock} kg available.")
                        return
                    
                    # Calculate new stock
                    if adjust_type.get() == "add":
                        new_stock = current_stock + amount
                        action = "added"
                        transaction_type = "adjustment_add"
                    else:
                        new_stock = current_stock - amount
                        action = "removed"
                        transaction_type = "adjustment_remove"
                    
                    # Update product stock
                    cursor.execute('''
                        UPDATE products 
                        SET current_stock_kg = ?
                        WHERE product_id = ?
                    ''', (new_stock, product_id))
                    
                    # Record transaction
                    cursor.execute('''
                        INSERT INTO stock_transactions 
                        (product_id, transaction_type, quantity_kg, notes)
                        VALUES (?, ?, ?, ?)
                    ''', (product_id, transaction_type, amount, f"Stock adjustment - Reason: {reason}. {notes}"))
                    
                    conn.commit()
                    conn.close()
                    
                    messagebox.showinfo(
                        "Stock Adjusted",
                        f"Stock adjustment successful!\n\n"
                        f"Product: {product_text.split(':')[1].split('(')[0].strip()}\n"
                        f"Amount {action}: {amount} kg\n"
                        f"New Stock Level: {new_stock} kg\n"
                        f"Reason: {reason}"
                    )
                    
                    # Clear form
                    amount_entry.delete(0, tk.END)
                    notes_text.delete("1.0", tk.END)
                    
                    # Refresh inventory
                    self.filter_inventory()
                    self.load_inventory()
                    self.load_low_stock()
                    
                except sqlite3.Error as e:
                    messagebox.showerror("Database Error", f"Could not update stock: {e}")
                
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {str(e)}")
        
        tk.CTkButton(
            form_frame,
            text="Adjust Stock",
            command=adjust_stock,
            height=45,
            fg_color="#2E7D32",
            hover_color="#1B5E20"
        ).pack(fill="x", pady=(0, 20))
        
        # Update canvas scroll region
        content_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))
        
        # Bind mouse wheel for scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    def setup_reports_tab(self):
        """Setup stock reports tab"""
        tab = self.tabview.tab("📊 Stock Reports")
        
        # Create main container with scrollbar
        main_container = tk.CTkFrame(tab)
        main_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Create canvas and scrollbar
        canvas = tk.CTkCanvas(main_container, bg="white")
        canvas.pack(side="left", fill="both", expand=True, padx=(5, 0))
        
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Create frame inside canvas
        content_frame = tk.CTkFrame(canvas)
        canvas.create_window((0, 0), window=content_frame, anchor="nw")
        
        tk.CTkLabel(
            content_frame,
            text="Inventory Reports",
            font=("Helvetica", 20, "bold")
        ).pack(pady=20)
        
        # Report options
        reports_frame = tk.CTkFrame(content_frame)
        reports_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        reports = [
            ("📋 Stock Summary", "Overview of all inventory items"),
            ("📈 Stock Movement", "Stock changes over time"),
            ("💰 Stock Value", "Total inventory value by category"),
            ("⚠️ Low Stock Report", "Items below minimum levels"),
            ("📊 Turnover Rate", "Inventory turnover analysis"),
            ("📋 Supplier Report", "Stock received by supplier")
        ]
        
        for i, (title, description) in enumerate(reports):
            report_frame = tk.CTkFrame(reports_frame, height=80)
            report_frame.grid(row=i//2, column=i%2, padx=10, pady=10, sticky="nsew")
            report_frame.grid_propagate(False)
            
            tk.CTkLabel(
                report_frame,
                text=title,
                font=("Helvetica", 14, "bold")
            ).place(x=20, y=15)
            
            tk.CTkLabel(
                report_frame,
                text=description,
                font=("Helvetica", 11),
                text_color="#666666"
            ).place(x=20, y=40)
            
            tk.CTkButton(
                report_frame,
                text="Generate",
                width=80,
                height=30,
                command=lambda t=title: self.generate_stock_report(t)
            ).place(x=200, y=25)
        
        reports_frame.grid_columnconfigure(0, weight=1)
        reports_frame.grid_columnconfigure(1, weight=1)
        
        # Update canvas scroll region
        content_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))
        
        # Bind mouse wheel for scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    def generate_stock_report(self, report_type):
        """Generate stock report"""
        messagebox.showinfo(
            f"Generate {report_type}",
            f"{report_type} generated successfully!\n\n"
            "Report would include:\n"
            "• Current stock levels\n"
            "• Stock values\n"
            "• Movement history\n"
            "• Low stock alerts\n"
            "• Turnover rates\n\n"
            "Export options: PDF, Excel, CSV"
        )
    
    def reorder_product(self, product):
        """Reorder low stock product"""
        messagebox.showinfo(
            f"Reorder {product['name']}",
            f"Reorder request created for:\n\n"
            f"Product: {product['name']}\n"
            f"Current Stock: {product['current_stock_kg']} kg\n"
            f"Minimum Required: {product['min_stock_level']} kg\n"
            f"Category: {product['category']}\n\n"
            "Reorder would:\n"
            "1. Calculate reorder quantity\n"
            "2. Generate purchase order\n"
            "3. Notify supplier\n"
            "4. Track delivery"
        )
    
    def refresh_all(self):
        """Refresh all inventory data"""
        self.load_inventory()
        self.filter_inventory()
        self.load_low_stock()
        messagebox.showinfo("Refreshed", "All inventory data has been refreshed")
    
    def go_back(self):
        """Return to main menu"""
        self.destroy()
        subprocess.Popen(["python", "jsfoods_main.py"])


if __name__ == "__main__":
    app = InventoryManager()
    app.mainloop()