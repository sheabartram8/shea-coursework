"""
JS Foods Customer Portal
Customer ordering interface
"""

import customtkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import sqlite3
import subprocess
from datetime import datetime, timedelta
from jsfoods_database import db

class CustomerPortal(tk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("JS Foods - Customer Portal")
        self.geometry("1200x700")
        self.resizable(True, True)
        
        tk.set_appearance_mode("light")
        tk.set_default_color_theme("blue")
        
        # Demo customer ID (in real app, this would come from login)
        self.customer_id = 1
        self.cart = []
        self.total_amount = 0.0
        
        self.setup_ui()
        self.load_products()
        self.load_customer_orders()
    
    def setup_ui(self):
        """Setup customer portal UI"""
        # Configure grid
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Left panel - Products
        products_frame = tk.CTkFrame(self)
        products_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        products_frame.grid_columnconfigure(0, weight=1)
        products_frame.grid_rowconfigure(1, weight=1)
        
        # Products header
        header_frame = tk.CTkFrame(products_frame, height=60)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        header_frame.grid_propagate(False)
        
        tk.CTkLabel(
            header_frame,
            text="🛒 Our Products",
            font=("Helvetica", 20, "bold"),
            text_color="#2E7D32"
        ).pack(side="left", padx=20)
        
        # Category filter
        category_frame = tk.CTkFrame(header_frame, fg_color="transparent")
        category_frame.pack(side="right", padx=20)
        
        tk.CTkLabel(category_frame, text="Filter:").pack(side="left", padx=5)
        self.category_var = tk.StringVar(value="All")
        categories = ["All", "Beef", "Pork", "Poultry", "Lamb", "Other"]
        self.category_combo = tk.CTkComboBox(
            category_frame,
            values=categories,
            variable=self.category_var,
            command=self.filter_products,
            width=120
        )
        self.category_combo.pack(side="left", padx=5)
        
        # Products grid
        self.products_canvas = tk.CTkCanvas(products_frame, bg="white")
        self.products_canvas.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        
        scrollbar = ttk.Scrollbar(products_frame, orient="vertical", command=self.products_canvas.yview)
        scrollbar.grid(row=1, column=1, sticky="ns", pady=(0, 10))
        
        self.products_canvas.configure(yscrollcommand=scrollbar.set)
        
        self.products_inner_frame = tk.CTkFrame(self.products_canvas)
        self.products_canvas.create_window((0, 0), window=self.products_inner_frame, anchor="nw")
        
        # Right panel - Cart & Orders
        right_frame = tk.CTkFrame(self)
        right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        right_frame.grid_columnconfigure(0, weight=1)
        right_frame.grid_rowconfigure(0, weight=2)
        right_frame.grid_rowconfigure(1, weight=3)
        
        # Cart section
        cart_frame = tk.CTkFrame(right_frame)
        cart_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=(5, 10))
        cart_frame.grid_columnconfigure(0, weight=1)
        cart_frame.grid_rowconfigure(1, weight=1)
        
        tk.CTkLabel(
            cart_frame,
            text="🛍️ Your Cart",
            font=("Helvetica", 18, "bold")
        ).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        # Cart items
        self.cart_tree = ttk.Treeview(
            cart_frame,
            columns=("Product", "Quantity", "Price", "Total"),
            show="headings",
            height=6
        )
        self.cart_tree.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        
        self.cart_tree.heading("Product", text="Product")
        self.cart_tree.heading("Quantity", text="Qty (kg)")
        self.cart_tree.heading("Price", text="Price/kg")
        self.cart_tree.heading("Total", text="Total")
        
        self.cart_tree.column("Product", width=120)
        self.cart_tree.column("Quantity", width=80, anchor="center")
        self.cart_tree.column("Price", width=80, anchor="center")
        self.cart_tree.column("Total", width=80, anchor="center")
        
        # Cart total
        self.total_label = tk.CTkLabel(
            cart_frame,
            text="Total: £0.00",
            font=("Helvetica", 16, "bold"),
            text_color="#2E7D32"
        )
        self.total_label.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="e")
        
        # Cart buttons
        cart_btn_frame = tk.CTkFrame(cart_frame, fg_color="transparent")
        cart_btn_frame.grid(row=3, column=0, padx=10, pady=(0, 10))
        
        tk.CTkButton(
            cart_btn_frame,
            text="Clear Cart",
            command=self.clear_cart,
            width=100,
            fg_color="#757575",
            hover_color="#616161"
        ).pack(side="left", padx=5)
        
        self.checkout_btn = tk.CTkButton(
            cart_btn_frame,
            text="Checkout →",
            command=self.open_checkout,
            width=100,
            fg_color="#2E7D32",
            hover_color="#1B5E20"
        )
        self.checkout_btn.pack(side="right", padx=5)
        
        # Orders section
        orders_frame = tk.CTkFrame(right_frame)
        orders_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=(0, 5))
        orders_frame.grid_columnconfigure(0, weight=1)
        orders_frame.grid_rowconfigure(1, weight=1)
        
        tk.CTkLabel(
            orders_frame,
            text="📋 Recent Orders",
            font=("Helvetica", 18, "bold")
        ).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        # Orders table
        self.orders_tree = ttk.Treeview(
            orders_frame,
            columns=("ID", "Date", "Amount", "Status"),
            show="headings",
            height=8
        )
        self.orders_tree.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        
        self.orders_tree.heading("ID", text="Order #")
        self.orders_tree.heading("Date", text="Date")
        self.orders_tree.heading("Amount", text="Amount")
        self.orders_tree.heading("Status", text="Status")
        
        self.orders_tree.column("ID", width=80, anchor="center")
        self.orders_tree.column("Date", width=100, anchor="center")
        self.orders_tree.column("Amount", width=80, anchor="center")
        self.orders_tree.column("Status", width=100, anchor="center")
        
        self.orders_tree.bind("<Double-1>", self.view_order_details)
        
        # Navigation
        nav_frame = tk.CTkFrame(self, height=50)
        nav_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 10))
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
            text="🔄 Refresh",
            command=self.refresh_all,
            width=100
        ).pack(side="right", padx=20)
    
    def load_products(self):
        """Load products from database"""
        category = self.category_var.get()
        category = None if category == "All" else category
        
        products = db.get_products(category=category, active_only=True)
        
        # Clear existing products
        for widget in self.products_inner_frame.winfo_children():
            widget.destroy()
        
        # Display products in grid
        row, col = 0, 0
        max_cols = 3
        
        for product in products:
            product_frame = tk.CTkFrame(self.products_inner_frame, width=250, height=180)
            product_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            product_frame.grid_propagate(False)
            
            # Product name
            tk.CTkLabel(
                product_frame,
                text=product['name'],
                font=("Helvetica", 14, "bold"),
                wraplength=200
            ).pack(pady=(10, 5))
            
            # Category and stock
            info_frame = tk.CTkFrame(product_frame, fg_color="transparent")
            info_frame.pack(fill="x", padx=10, pady=5)
            
            tk.CTkLabel(
                info_frame,
                text=f"Category: {product['category']}",
                font=("Helvetica", 10),
                text_color="#666666"
            ).pack(anchor="w")
            
            stock_color = "#4CAF50" if product['current_stock_kg'] > 10 else "#FF9800"
            tk.CTkLabel(
                info_frame,
                text=f"Stock: {product['current_stock_kg']} {product['unit']}",
                font=("Helvetica", 10),
                text_color=stock_color
            ).pack(anchor="w", pady=(0, 5))
            
            # Price
            tk.CTkLabel(
                product_frame,
                text=f"£{product['price_per_kg']:.2f}/{product['unit']}",
                font=("Helvetica", 16, "bold"),
                text_color="#2E7D32"
            ).pack(pady=5)
            
            # Add to cart controls
            control_frame = tk.CTkFrame(product_frame, fg_color="transparent")
            control_frame.pack(fill="x", padx=10, pady=(0, 10))
            
            # Quantity input
            quantity_frame = tk.CTkFrame(control_frame, fg_color="transparent")
            quantity_frame.pack(side="left", fill="x", expand=True)
            
            tk.CTkLabel(quantity_frame, text="Qty (kg):").pack(side="left")
            quantity_var = tk.StringVar(value="1")
            quantity_entry = tk.CTkEntry(
                quantity_frame,
                textvariable=quantity_var,
                width=60
            )
            quantity_entry.pack(side="left", padx=5)
            
            # Add button
            add_btn = tk.CTkButton(
                control_frame,
                text="+ Add",
                command=lambda p=product, q=quantity_var: self.add_to_cart(p, q),
                width=60,
                fg_color="#2E7D32",
                hover_color="#1B5E20"
            )
            add_btn.pack(side="right")
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        # Update canvas scroll region
        self.products_inner_frame.update_idletasks()
        self.products_canvas.configure(scrollregion=self.products_canvas.bbox("all"))
    
    def filter_products(self, choice):
        """Filter products by category"""
        self.load_products()
    
    def add_to_cart(self, product, quantity_var):
        """Add product to cart"""
        try:
            quantity = float(quantity_var.get())
            if quantity <= 0:
                messagebox.showerror("Error", "Quantity must be greater than 0")
                return
            
            if quantity > product['current_stock_kg']:
                messagebox.showerror("Error", f"Only {product['current_stock_kg']} {product['unit']} available")
                return
            
            # Check if product already in cart
            for i, item in enumerate(self.cart):
                if item['product_id'] == product['product_id']:
                    self.cart[i]['quantity_kg'] += quantity
                    break
            else:
                # Add new item
                self.cart.append({
                    'product_id': product['product_id'],
                    'name': product['name'],
                    'quantity_kg': quantity,
                    'unit_price': product['price_per_kg'],
                    'category': product['category']
                })
            
            self.update_cart_display()
            messagebox.showinfo("Added to Cart", f"{quantity}kg of {product['name']} added to cart")
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid quantity")
    
    def update_cart_display(self):
        """Update cart display"""
        # Clear cart tree
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)
        
        # Add cart items
        self.total_amount = 0
        for item in self.cart:
            item_total = item['quantity_kg'] * item['unit_price']
            self.total_amount += item_total
            
            self.cart_tree.insert("", "end", values=(
                item['name'],
                f"{item['quantity_kg']:.2f}",
                f"£{item['unit_price']:.2f}",
                f"£{item_total:.2f}"
            ))
        
        # Update total
        self.total_label.configure(text=f"Total: £{self.total_amount:.2f}")
        
        # Enable/disable checkout button
        self.checkout_btn.configure(state="normal" if self.cart else "disabled")
    
    def clear_cart(self):
        """Clear shopping cart"""
        if not self.cart:
            return
        
        if messagebox.askyesno("Clear Cart", "Are you sure you want to clear your cart?"):
            self.cart = []
            self.update_cart_display()
    
    def load_customer_orders(self):
        """Load customer's recent orders"""
        orders = db.get_user_orders(self.customer_id, limit=10)
        
        # Clear orders tree
        for item in self.orders_tree.get_children():
            self.orders_tree.delete(item)
        
        # Add orders
        for order in orders:
            status_color = {
                'pending': 'orange',
                'confirmed': 'blue',
                'processing': 'purple',
                'ready': 'green',
                'delivered': '#2E7D32',
                'cancelled': 'red'
            }.get(order['status'], 'black')
            
            self.orders_tree.insert("", "end", values=(
                order['order_id'],
                order['order_date'][:10],
                f"£{order['total_amount']:.2f}",
                order['status'].title()
            ), tags=(order['status'],))
            
            self.orders_tree.tag_configure(order['status'], foreground=status_color)
    
    def view_order_details(self, event):
        """View details of selected order"""
        selection = self.orders_tree.selection()
        if not selection:
            return
        
        order_id = self.orders_tree.item(selection[0])['values'][0]
        order, items = db.get_order_details(order_id)
        
        if not order:
            return
        
        # Create details window
        details_window = tk.CTkToplevel(self)
        details_window.title(f"Order #{order_id} Details")
        details_window.geometry("500x400")
        
        # Force window to the front
        details_window.attributes('-topmost', True)
        details_window.after_idle(details_window.attributes, '-topmost', False)
        details_window.lift()
        details_window.focus_force()
        
        # Order info
        info_frame = tk.CTkFrame(details_window)
        info_frame.pack(fill="x", padx=20, pady=20)
        
        tk.CTkLabel(
            info_frame,
            text=f"Order #{order_id}",
            font=("Helvetica", 18, "bold")
        ).pack(pady=10)
        
        info_grid = tk.CTkFrame(info_frame, fg_color="transparent")
        info_grid.pack(fill="x", padx=10, pady=10)
        
        details = [
            ("Date:", order['order_date'][:19]),
            ("Status:", order['status'].title()),
            ("Total Amount:", f"£{order['total_amount']:.2f}"),
            ("Delivery Address:", order['delivery_address'] or "N/A"),
            ("Delivery Date:", order['delivery_date'] or "Not scheduled"),
            ("Payment Method:", order['payment_method'].title())
        ]
        
        for label, value in details:
            row_frame = tk.CTkFrame(info_grid, fg_color="transparent")
            row_frame.pack(fill="x", pady=2)
            
            tk.CTkLabel(
                row_frame,
                text=label,
                font=("Helvetica", 12, "bold"),
                width=120,
                anchor="w"
            ).pack(side="left")
            
            tk.CTkLabel(
                row_frame,
                text=value,
                font=("Helvetica", 12)
            ).pack(side="left")
        
        # Order items
        items_frame = tk.CTkFrame(details_window)
        items_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        tk.CTkLabel(
            items_frame,
            text="Order Items:",
            font=("Helvetica", 14, "bold")
        ).pack(pady=10)
        
        items_tree = ttk.Treeview(
            items_frame,
            columns=("Product", "Quantity", "Price", "Discount", "Total"),
            show="headings",
            height=min(len(items), 5)
        )
        items_tree.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        items_tree.heading("Product", text="Product")
        items_tree.heading("Quantity", text="Qty (kg)")
        items_tree.heading("Price", text="Price/kg")
        items_tree.heading("Discount", text="Discount %")
        items_tree.heading("Total", text="Total")
        
        for item in items:
            items_tree.insert("", "end", values=(
                item['product_name'],
                f"{item['quantity_kg']:.2f}",
                f"£{item['unit_price']:.2f}",
                f"{item['discount_percent']:.1f}%",
                f"£{item['final_price']:.2f}"
            ))
    
    def open_checkout(self):
        """Open checkout window"""
        if not self.cart:
            return
        
        # Create checkout window
        self.checkout_window = CheckoutWindow(self, self.cart, self.total_amount, self.customer_id)
        
        # Force the checkout window to the front
        self.checkout_window.attributes('-topmost', True)
        self.checkout_window.after_idle(self.checkout_window.attributes, '-topmost', False)
        self.checkout_window.lift()
        self.checkout_window.focus_force()
        
        # Make sure the main window stays behind
        self.attributes('-topmost', False)
    
    def refresh_all(self):
        """Refresh products and orders"""
        self.load_products()
        self.load_customer_orders()
    
    def go_back(self):
        """Return to main menu"""
        self.destroy()
        subprocess.Popen(["python", "jsfoods_main.py"])


class CheckoutWindow(tk.CTkToplevel):
    def __init__(self, parent, cart, total_amount, customer_id):
        super().__init__(parent)
        
        self.parent = parent
        self.cart = cart
        self.total_amount = total_amount
        self.customer_id = customer_id
        
        self.title("JS Foods - Checkout")
        self.geometry("600x700")
        self.resizable(False, False)
        
        # Set window to always appear on top when created
        self.attributes('-topmost', True)
        
        self.setup_ui()
        
        # After UI is setup, make sure window is focused
        self.after(100, self.bring_to_front)
    
    def bring_to_front(self):
        """Bring window to front after a short delay"""
        self.lift()
        self.focus_force()
        # Remove topmost after window is displayed to allow normal window management
        self.after(200, lambda: self.attributes('-topmost', False))
    
    def setup_ui(self):
        """Setup checkout interface with scrollbar"""
        # Create main container with scrollbar
        main_container = tk.CTkFrame(self)
        main_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Create a canvas for scrolling
        canvas = tk.CTkCanvas(main_container, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        
        # Create scrollable frame
        self.scrollable_frame = tk.CTkFrame(canvas, fg_color="white")
        
        # Configure canvas
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True, padx=(0, 5))
        scrollbar.pack(side="right", fill="y", padx=(0, 5))
        
        # Create window in canvas for scrollable frame
        canvas_frame = canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        # Configure scroll region
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(canvas_frame, width=canvas.winfo_width())
        
        self.scrollable_frame.bind("<Configure>", configure_scroll_region)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(canvas_frame, width=e.width))
        
        # Title
        tk.CTkLabel(
            self.scrollable_frame,
            text="Checkout",
            font=("Helvetica", 24, "bold"),
            text_color="#2E7D32"
        ).pack(pady=20)
        
        # Order summary
        summary_frame = tk.CTkFrame(self.scrollable_frame, fg_color="#F5F5F5")
        summary_frame.pack(fill="x", padx=20, pady=10)
        
        tk.CTkLabel(
            summary_frame,
            text="Order Summary",
            font=("Helvetica", 16, "bold")
        ).pack(pady=10)
        
        # Items list
        items_text = ""
        for item in self.cart:
            items_text += f"• {item['name']}: {item['quantity_kg']}kg @ £{item['unit_price']}/kg\n"
        
        tk.CTkLabel(
            summary_frame,
            text=items_text,
            font=("Helvetica", 12),
            justify="left"
        ).pack(pady=5, padx=20)
        
        tk.CTkLabel(
            summary_frame,
            text=f"Total: £{self.total_amount:.2f}",
            font=("Helvetica", 16, "bold"),
            text_color="#2E7D32"
        ).pack(pady=10)
        
        # Delivery details
        details_frame = tk.CTkFrame(self.scrollable_frame, fg_color="#F5F5F5")
        details_frame.pack(fill="x", padx=20, pady=10)
        
        tk.CTkLabel(
            details_frame,
            text="Delivery Details",
            font=("Helvetica", 16, "bold")
        ).pack(pady=10)
        
        # Delivery date
        tk.CTkLabel(
            details_frame,
            text="Preferred Delivery Date:",
            font=("Helvetica", 12)
        ).pack(anchor="w", padx=20, pady=(5, 0))
        
        self.delivery_date = tk.StringVar(value=self.get_next_business_day())
        date_entry = tk.CTkEntry(
            details_frame,
            textvariable=self.delivery_date,
            placeholder_text="YYYY-MM-DD",
            height=40
        )
        date_entry.pack(fill="x", padx=20, pady=(0, 10))
        
        # Delivery address
        tk.CTkLabel(
            details_frame,
            text="Delivery Address:",
            font=("Helvetica", 12)
        ).pack(anchor="w", padx=20, pady=(5, 0))
        
        self.address_text = tk.CTkTextbox(details_frame, height=80)
        self.address_text.pack(fill="x", padx=20, pady=(0, 10))
        
        # Payment method
        tk.CTkLabel(
            details_frame,
            text="Payment Method:",
            font=("Helvetica", 12)
        ).pack(anchor="w", padx=20, pady=(5, 0))
        
        self.payment_var = tk.StringVar(value="cash")
        payment_frame = tk.CTkFrame(details_frame, fg_color="transparent")
        payment_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        methods = [("Cash on Delivery", "cash"), ("Bank Transfer", "bank"), ("Credit Card", "card")]
        for text, value in methods:
            tk.CTkRadioButton(
                payment_frame,
                text=text,
                variable=self.payment_var,
                value=value
            ).pack(side="left", padx=10)
        
        # Notes
        tk.CTkLabel(
            details_frame,
            text="Additional Notes:",
            font=("Helvetica", 12)
        ).pack(anchor="w", padx=20, pady=(5, 0))
        
        self.notes_text = tk.CTkTextbox(details_frame, height=60)
        self.notes_text.pack(fill="x", padx=20, pady=(0, 10))
        
        # Buttons (always visible at the bottom)
        button_frame = tk.CTkFrame(self.scrollable_frame, fg_color="transparent", height=70)
        button_frame.pack(fill="x", padx=20, pady=20)
        button_frame.pack_propagate(False)
        
        tk.CTkButton(
            button_frame,
            text="← Back to Cart",
            command=self.destroy,
            width=120,
            fg_color="#757575",
            hover_color="#616161"
        ).place(x=20, y=20)
        
        tk.CTkButton(
            button_frame,
            text="Place Order →",
            command=self.place_order,
            width=120,
            fg_color="#2E7D32",
            hover_color="#1B5E20"
        ).place(x=430, y=20)
    
    def get_next_business_day(self):
        """Get next business day (skip weekends)"""
        today = datetime.now()
        next_day = today + timedelta(days=1)
        
        # Skip weekends
        while next_day.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
            next_day += timedelta(days=1)
        
        return next_day.strftime("%Y-%m-%d")
    
    def validate_checkout(self):
        """Validate checkout form"""
        errors = []
        
        # Validate delivery date
        try:
            delivery_date = datetime.strptime(self.delivery_date.get(), "%Y-%m-%d")
            if delivery_date.date() < datetime.now().date():
                errors.append("Delivery date cannot be in the past")
        except ValueError:
            errors.append("Please enter a valid date (YYYY-MM-DD)")
        
        # Validate address
        address = self.address_text.get("1.0", "end-1c").strip()
        if not address:
            errors.append("Delivery address is required")
        
        return errors
    
    def place_order(self):
        """Place the order"""
        # Validate form
        errors = self.validate_checkout()
        if errors:
            messagebox.showerror("Checkout Error", "\n".join(errors))
            return
        
        # Prepare order data
        order_data = {
            'customer_id': self.customer_id,
            'total_amount': self.total_amount,
            'delivery_date': self.delivery_date.get(),
            'delivery_address': self.address_text.get("1.0", "end-1c").strip(),
            'payment_method': self.payment_var.get(),
            'notes': self.notes_text.get("1.0", "end-1c").strip()
        }
        
        # Prepare order items
        order_items = []
        for item in self.cart:
            order_items.append({
                'product_id': item['product_id'],
                'quantity_kg': item['quantity_kg'],
                'unit_price': item['unit_price']
            })
        
        # Create order
        order_id = db.create_order(order_data, order_items)
        
        if order_id:
            messagebox.showinfo(
                "Order Placed",
                f"Your order has been placed successfully!\n\n"
                f"Order Number: #{order_id}\n"
                f"Total Amount: £{self.total_amount:.2f}\n"
                f"Delivery Date: {self.delivery_date.get()}\n\n"
                "Thank you for your business!"
            )
            
            # Clear parent cart and refresh
            self.parent.cart = []
            self.parent.update_cart_display()
            self.parent.load_customer_orders()
            
            self.destroy()
        else:
            messagebox.showerror(
                "Order Failed",
                "Could not place order. Please try again or contact support."
            )


if __name__ == "__main__":
    app = CustomerPortal()
    app.mainloop()