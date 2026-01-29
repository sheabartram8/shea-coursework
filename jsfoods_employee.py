"""
JS Foods Employee Portal
Employee and manager interface
"""

import customtkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import subprocess
from datetime import datetime, timedelta
from jsfoods_database import db

class EmployeePortal(tk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("JS Foods - Employee Portal")
        self.geometry("1400x800")
        self.resizable(True, True)
        
        tk.set_appearance_mode("light")
        tk.set_default_color_theme("blue")
        
        # Demo employee ID
        self.employee_id = 2
        self.is_manager = True  # Demo: this employee is a manager
        
        self.setup_ui()
        self.load_dashboard_data()
    
    def setup_ui(self):
        """Setup employee portal UI"""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header
        header_frame = tk.CTkFrame(self, height=80)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        header_frame.grid_propagate(False)
        
        # Left side: Logo and title
        title_frame = tk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.pack(side="left", padx=20)
        
        tk.CTkLabel(
            title_frame,
            text="👨‍💼 Employee Portal",
            font=("Helvetica", 24, "bold"),
            text_color="#2E7D32"
        ).pack(side="left")
        
        if self.is_manager:
            tk.CTkLabel(
                title_frame,
                text="(Manager)",
                font=("Helvetica", 14),
                text_color="#FF9800"
            ).pack(side="left", padx=10)
        
        # Right side: Stats
        stats_frame = tk.CTkFrame(header_frame, fg_color="transparent")
        stats_frame.pack(side="right", padx=20)
        
        self.stats_labels = {}
        stats = [
            ("📦", "pending_orders", "Pending Orders"),
            ("⚠️", "low_stock", "Low Stock Items"),
            ("💰", "today_sales", "Today's Sales")
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
        
        # Tab view for different sections
        self.tabview = tk.CTkTabview(self)
        self.tabview.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        
        # Create tabs
        self.tabview.add("📋 Orders")
        self.tabview.add("🚚 Deliveries")
        self.tabview.add("📦 Inventory")
        if self.is_manager:
            self.tabview.add("👥 Customers")
            self.tabview.add("⚙️ Discount Rules")
        
        # Setup each tab
        self.setup_orders_tab()
        self.setup_deliveries_tab()
        self.setup_inventory_tab()
        
        if self.is_manager:
            self.setup_customers_tab()
            self.setup_discounts_tab()
        
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
        
        # Add Inventory Manager button to navigation
        tk.CTkButton(
            nav_frame,
            text="📦 Open Inventory Manager",
            command=self.open_inventory_manager,
            width=180,
            fg_color="#4CAF50",
            hover_color="#2E7D32",
            font=("Helvetica", 12)
        ).pack(side="right", padx=20)
        
        tk.CTkButton(
            nav_frame,
            text="🔄 Refresh All",
            command=self.refresh_all,
            width=120
        ).pack(side="right", padx=20)
    
    def load_dashboard_data(self):
        """Load dashboard statistics"""
        try:
            # Get pending orders count
            conn = sqlite3.connect('jsfoods.db')
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM orders WHERE status IN ('pending', 'confirmed')")
            pending = cursor.fetchone()[0]
            self.stats_labels['pending_orders'].configure(text=str(pending))
            
            # Get low stock items
            low_stock = db.get_low_stock_items()
            self.stats_labels['low_stock'].configure(text=str(len(low_stock)))
            
            # Get today's sales
            today = datetime.now().strftime("%Y-%m-%d")
            cursor.execute(
                "SELECT SUM(total_amount) FROM orders WHERE DATE(order_date) = ? AND status != 'cancelled'",
                (today,)
            )
            sales = cursor.fetchone()[0] or 0
            self.stats_labels['today_sales'].configure(text=f"£{sales:.2f}")
            
        except sqlite3.Error as e:
            print(f"Dashboard data error: {e}")
    
    def setup_orders_tab(self):
        """Setup orders management tab"""
        tab = self.tabview.tab("📋 Orders")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)
        
        # Orders frame
        orders_frame = tk.CTkFrame(tab)
        orders_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        orders_frame.grid_columnconfigure(0, weight=1)
        orders_frame.grid_rowconfigure(1, weight=1)
        
        # Filters
        filter_frame = tk.CTkFrame(orders_frame)
        filter_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        tk.CTkLabel(filter_frame, text="Filter:").pack(side="left", padx=5)
        
        self.order_status_var = tk.StringVar(value="All")
        status_combo = tk.CTkComboBox(
            filter_frame,
            values=["All", "pending", "confirmed", "processing", "ready", "delivered", "cancelled"],
            variable=self.order_status_var,
            command=self.load_orders,
            width=120
        )
        status_combo.pack(side="left", padx=5)
        
        tk.CTkButton(
            filter_frame,
            text="Apply Filter",
            command=self.load_orders,
            width=100
        ).pack(side="right", padx=5)
        
        # Orders table
        self.orders_tree = ttk.Treeview(
            orders_frame,
            columns=("ID", "Customer", "Date", "Amount", "Status", "Delivery"),
            show="headings",
            height=15
        )
        self.orders_tree.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        
        # Configure scrollbar
        scrollbar = ttk.Scrollbar(orders_frame, orient="vertical", command=self.orders_tree.yview)
        scrollbar.grid(row=1, column=1, sticky="ns", pady=(0, 10))
        self.orders_tree.configure(yscrollcommand=scrollbar.set)
        
        # Configure columns
        columns = [
            ("ID", 80, "center"),
            ("Customer", 150, "center"),
            ("Date", 120, "center"),
            ("Amount", 100, "center"),
            ("Status", 100, "center"),
            ("Delivery", 120, "center")
        ]
        
        for col, width, anchor in columns:
            self.orders_tree.heading(col, text=col)
            self.orders_tree.column(col, width=width, anchor=anchor)
        
        self.orders_tree.bind("<Double-1>", self.view_order_details)
        
        # Action buttons
        action_frame = tk.CTkFrame(orders_frame)
        action_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
        
        self.update_status_btn = tk.CTkButton(
            action_frame,
            text="Update Status",
            command=self.update_order_status,
            width=120
        )
        self.update_status_btn.pack(side="left", padx=5)
        
        self.assign_delivery_btn = tk.CTkButton(
            action_frame,
            text="Assign to Delivery",
            command=self.assign_to_delivery,
            width=120
        )
        self.assign_delivery_btn.pack(side="left", padx=5)
        
        tk.CTkButton(
            action_frame,
            text="View Details",
            command=lambda: self.view_order_details(None),
            width=120
        ).pack(side="right", padx=5)
        
        # Load initial orders
        self.load_orders()
    
    def load_orders(self, event=None):
        """Load orders based on filter"""
        try:
            conn = sqlite3.connect('jsfoods.db')
            cursor = conn.cursor()
            
            status_filter = self.order_status_var.get()
            
            if status_filter == "All":
                query = """
                    SELECT o.order_id, u.first_name || ' ' || u.last_name as customer,
                           o.order_date, o.total_amount, o.status, o.delivery_date
                    FROM orders o
                    JOIN users u ON o.customer_id = u.user_id
                    ORDER BY o.order_date DESC
                    LIMIT 100
                """
                cursor.execute(query)
            else:
                query = """
                    SELECT o.order_id, u.first_name || ' ' || u.last_name as customer,
                           o.order_date, o.total_amount, o.status, o.delivery_date
                    FROM orders o
                    JOIN users u ON o.customer_id = u.user_id
                    WHERE o.status = ?
                    ORDER BY o.order_date DESC
                """
                cursor.execute(query, (status_filter,))
            
            # Clear existing items
            for item in self.orders_tree.get_children():
                self.orders_tree.delete(item)
            
            # Add orders
            for order in cursor.fetchall():
                status_color = {
                    'pending': 'orange',
                    'confirmed': 'blue',
                    'processing': 'purple',
                    'ready': 'green',
                    'delivered': '#2E7D32',
                    'cancelled': 'red'
                }.get(order[4], 'black')
                
                self.orders_tree.insert("", "end", values=order, tags=(order[4],))
                self.orders_tree.tag_configure(order[4], foreground=status_color)
                
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Could not load orders: {e}")
    
    def view_order_details(self, event):
        """View order details"""
        selection = self.orders_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an order first")
            return
        
        order_id = self.orders_tree.item(selection[0])['values'][0]
        order, items = db.get_order_details(order_id)
        
        if not order:
            return
        
        # Create details window
        details_window = tk.CTkToplevel(self)
        details_window.title(f"Order #{order_id} - Details")
        details_window.geometry("600x500")
        details_window.transient(self)  # Set as transient to main window
        details_window.grab_set()  # Make it modal
        details_window.lift()  # Bring to front
        
        # Order info
        info_frame = tk.CTkFrame(details_window)
        info_frame.pack(fill="x", padx=20, pady=20)
        
        tk.CTkLabel(
            info_frame,
            text=f"Order #{order_id}",
            font=("Helvetica", 20, "bold")
        ).pack(pady=10)
        
        # Customer info
        cust_frame = tk.CTkFrame(info_frame)
        cust_frame.pack(fill="x", padx=10, pady=10)
        
        try:
            conn = sqlite3.connect('jsfoods.db')
            cursor = conn.cursor()
            cursor.execute(
                "SELECT first_name, last_name, email, phone FROM users WHERE user_id = ?",
                (order['customer_id'],)
            )
            customer = cursor.fetchone()
            
            if customer:
                tk.CTkLabel(
                    cust_frame,
                    text=f"Customer: {customer[0]} {customer[1]}",
                    font=("Helvetica", 12, "bold")
                ).pack(anchor="w")
                
                tk.CTkLabel(
                    cust_frame,
                    text=f"Email: {customer[2]} | Phone: {customer[3] or 'N/A'}",
                    font=("Helvetica", 11)
                ).pack(anchor="w", pady=2)
        except sqlite3.Error:
            pass
        
        # Order details
        details_grid = tk.CTkFrame(info_frame, fg_color="transparent")
        details_grid.pack(fill="x", padx=10, pady=10)
        
        order_details = [
            ("Order Date:", order['order_date'][:19]),
            ("Status:", order['status'].title()),
            ("Total Amount:", f"£{order['total_amount']:.2f}"),
            ("Delivery Address:", order['delivery_address'] or "N/A"),
            ("Delivery Date:", order['delivery_date'] or "Not scheduled"),
            ("Payment Method:", order['payment_method'].title()),
            ("Notes:", order['notes'] or "None")
        ]
        
        for label, value in order_details:
            row_frame = tk.CTkFrame(details_grid, fg_color="transparent")
            row_frame.pack(fill="x", pady=2)
            
            tk.CTkLabel(
                row_frame,
                text=label,
                font=("Helvetica", 11, "bold"),
                width=120,
                anchor="w"
            ).pack(side="left")
            
            tk.CTkLabel(
                row_frame,
                text=value,
                font=("Helvetica", 11),
                wraplength=400
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
            columns=("Product", "Category", "Quantity", "Price", "Discount", "Total"),
            show="headings",
            height=min(len(items), 6)
        )
        items_tree.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        columns = [
            ("Product", 150),
            ("Category", 100),
            ("Quantity", 80),
            ("Price", 80),
            ("Discount", 80),
            ("Total", 80)
        ]
        
        for col, width in columns:
            items_tree.heading(col, text=col)
            items_tree.column(col, width=width, anchor="center")
        
        for item in items:
            items_tree.insert("", "end", values=(
                item['product_name'],
                item['category'],
                f"{item['quantity_kg']:.2f} kg",
                f"£{item['unit_price']:.2f}",
                f"{item['discount_percent']:.1f}%",
                f"£{item['final_price']:.2f}"
            ))
    
    def update_order_status(self):
        """Update selected order status"""
        selection = self.orders_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an order first")
            return
        
        order_id = self.orders_tree.item(selection[0])['values'][0]
        current_status = self.orders_tree.item(selection[0])['values'][4]
        
        # Create status update window
        status_window = tk.CTkToplevel(self)
        status_window.title(f"Update Order #{order_id} Status")
        status_window.geometry("400x300")
        status_window.transient(self)  # Set as transient to main window
        status_window.grab_set()  # Make it modal
        status_window.lift()  # Bring to front
        
        tk.CTkLabel(
            status_window,
            text=f"Update Order #{order_id} Status",
            font=("Helvetica", 16, "bold")
        ).pack(pady=20)
        
        tk.CTkLabel(
            status_window,
            text=f"Current Status: {current_status.title()}",
            font=("Helvetica", 12)
        ).pack(pady=10)
        
        # Status selection
        status_var = tk.StringVar(value=current_status)
        status_frame = tk.CTkFrame(status_window, fg_color="transparent")
        status_frame.pack(pady=20)
        
        statuses = ["pending", "confirmed", "processing", "ready", "delivered", "cancelled"]
        
        for status in statuses:
            tk.CTkRadioButton(
                status_frame,
                text=status.title(),
                variable=status_var,
                value=status
            ).pack(pady=5)
        
        # Update button
        def update_status():
            new_status = status_var.get()
            try:
                conn = sqlite3.connect('jsfoods.db')
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE orders SET status = ? WHERE order_id = ?",
                    (new_status, order_id)
                )
                conn.commit()
                
                messagebox.showinfo("Success", f"Order status updated to {new_status}")
                status_window.destroy()
                self.load_orders()
                
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"Could not update status: {e}")
        
        tk.CTkButton(
            status_window,
            text="Update Status",
            command=update_status,
            fg_color="#2E7D32",
            hover_color="#1B5E20"
        ).pack(pady=20)
    
    def assign_to_delivery(self):
        """Assign order to delivery route"""
        selection = self.orders_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an order first")
            return
        
        order_id = self.orders_tree.item(selection[0])['values'][0]
        
        # In a full implementation, this would open a window to select/creat delivery route
        messagebox.showinfo(
            "Assign to Delivery",
            f"Order #{order_id} selected for delivery assignment.\n\n"
            "This feature would allow you to:\n"
            "1. Select existing delivery route\n"
            "2. Create new delivery route\n"
            "3. Assign sequence number\n"
            "4. Set estimated arrival time"
        )
    
    def setup_deliveries_tab(self):
        """Setup deliveries management tab"""
        tab = self.tabview.tab("🚚 Deliveries")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)
        
        tk.CTkLabel(
            tab,
            text="Delivery Management",
            font=("Helvetica", 20, "bold")
        ).pack(pady=20)
        
        # Delivery routes frame
        routes_frame = tk.CTkFrame(tab)
        routes_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Create new route button
        tk.CTkButton(
            routes_frame,
            text="+ Create New Delivery Route",
            command=self.create_delivery_route,
            height=40,
            font=("Helvetica", 14),
            fg_color="#2E7D32",
            hover_color="#1B5E20"
        ).pack(pady=20)
        
        # Routes list
        routes_list_frame = tk.CTkFrame(routes_frame)
        routes_list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Sample routes (in full implementation, load from database)
        sample_routes = [
            {"id": 1, "name": "North Belfast Route", "date": "2024-01-15", "status": "scheduled", "orders": 3},
            {"id": 2, "name": "South Antrim Route", "date": "2024-01-14", "status": "in_progress", "orders": 5},
            {"id": 3, "name": "City Center", "date": "2024-01-13", "status": "completed", "orders": 8}
        ]
        
        for route in sample_routes:
            route_frame = tk.CTkFrame(routes_list_frame, height=60)
            route_frame.pack(fill="x", pady=5, padx=10)
            route_frame.grid_propagate(False)
            
            # Route info
            info_frame = tk.CTkFrame(route_frame, fg_color="transparent")
            info_frame.pack(side="left", fill="both", expand=True, padx=10)
            
            tk.CTkLabel(
                info_frame,
                text=route['name'],
                font=("Helvetica", 12, "bold")
            ).pack(anchor="w")
            
            tk.CTkLabel(
                info_frame,
                text=f"Date: {route['date']} | Orders: {route['orders']}",
                font=("Helvetica", 10),
                text_color="#666666"
            ).pack(anchor="w")
            
            # Status badge
            status_color = {
                'scheduled': '#2196F3',
                'in_progress': '#FF9800',
                'completed': '#4CAF50'
            }.get(route['status'], '#757575')
            
            status_frame = tk.CTkFrame(route_frame, fg_color="transparent")
            status_frame.pack(side="right", padx=10)
            
            tk.CTkLabel(
                status_frame,
                text=route['status'].replace('_', ' ').title(),
                font=("Helvetica", 10, "bold"),
                text_color="white",
                fg_color=status_color,
                corner_radius=10,
                width=100,
                height=25
            ).pack(pady=17)
    
    def create_delivery_route(self):
        """Create new delivery route with scrollable form"""
        route_window = tk.CTkToplevel(self)
        route_window.title("Create Delivery Route")
        route_window.geometry("550x500")  # Allow resizing
        route_window.resizable(True, True)
        route_window.transient(self)  # Set as transient to main window
        route_window.grab_set()  # Make it modal
        route_window.lift()  # Bring to front
        
        # Create main container frame
        main_container = tk.CTkFrame(route_window)
        main_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Create a canvas for scrolling
        canvas = tk.CTkCanvas(main_container, bg='white', highlightthickness=0)
        scrollbar = tk.CTkScrollbar(main_container, orientation="vertical", command=canvas.yview)
        
        # Create scrollable frame
        scrollable_frame = tk.CTkFrame(canvas, fg_color="transparent")
        
        # Configure canvas
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True, padx=(0, 5))
        scrollbar.pack(side="right", fill="y", padx=(0, 5))
        
        # Create window in canvas for scrollable frame
        canvas_frame = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        # Configure scroll region
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            # Keep the canvas window width the same as the canvas
            canvas.itemconfig(canvas_frame, width=canvas.winfo_width())
        
        scrollable_frame.bind("<Configure>", configure_scroll_region)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(canvas_frame, width=e.width))
        
        tk.CTkLabel(
            scrollable_frame,
            text="Create New Delivery Route",
            font=("Helvetica", 18, "bold")
        ).pack(pady=20)
        
        # Form
        form_frame = tk.CTkFrame(scrollable_frame)
        form_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Route name
        tk.CTkLabel(
            form_frame,
            text="Route Name:",
            font=("Helvetica", 12)
        ).pack(anchor="w", pady=(10, 0))
        
        name_entry = tk.CTkEntry(form_frame, height=35)
        name_entry.pack(fill="x", pady=(0, 10))
        
        # Delivery date
        tk.CTkLabel(
            form_frame,
            text="Delivery Date:",
            font=("Helvetica", 12)
        ).pack(anchor="w", pady=(10, 0))
        
        date_entry = tk.CTkEntry(form_frame, height=35, placeholder_text="YYYY-MM-DD")
        date_entry.pack(fill="x", pady=(0, 10))
        
        # Driver selection
        tk.CTkLabel(
            form_frame,
            text="Select Driver:",
            font=("Helvetica", 12)
        ).pack(anchor="w", pady=(10, 0))
        
        # Get employees for dropdown
        try:
            conn = sqlite3.connect('jsfoods.db')
            cursor = conn.cursor()
            cursor.execute("SELECT user_id, first_name, last_name FROM users WHERE role IN ('employee', 'manager')")
            employees = cursor.fetchall()
            driver_options = ["None"] + [f"{emp[0]}: {emp[1]} {emp[2]}" for emp in employees]
        except:
            driver_options = ["None"]
        
        driver_combo = tk.CTkComboBox(form_frame, values=driver_options)
        driver_combo.set("None")
        driver_combo.pack(fill="x", pady=(0, 10))
        
        # Vehicle info
        tk.CTkLabel(
            form_frame,
            text="Vehicle Information:",
            font=("Helvetica", 12)
        ).pack(anchor="w", pady=(10, 0))
        
        vehicle_entry = tk.CTkEntry(form_frame, height=35, placeholder_text="e.g., Van #5 - Ford Transit")
        vehicle_entry.pack(fill="x", pady=(0, 10))
        
        # Start time
        tk.CTkLabel(
            form_frame,
            text="Start Time:",
            font=("Helvetica", 12)
        ).pack(anchor="w", pady=(10, 0))
        
        time_frame = tk.CTkFrame(form_frame, fg_color="transparent")
        time_frame.pack(fill="x", pady=(0, 10))
        
        hour_var = tk.StringVar(value="08")
        minute_var = tk.StringVar(value="00")
        
        tk.CTkLabel(time_frame, text="Hour:").pack(side="left", padx=(0, 5))
        hour_combo = tk.CTkComboBox(
            time_frame,
            values=[f"{h:02d}" for h in range(6, 20)],
            variable=hour_var,
            width=60
        )
        hour_combo.pack(side="left", padx=(0, 10))
        
        tk.CTkLabel(time_frame, text="Minute:").pack(side="left", padx=(0, 5))
        minute_combo = tk.CTkComboBox(
            time_frame,
            values=["00", "15", "30", "45"],
            variable=minute_var,
            width=60
        )
        minute_combo.pack(side="left")
        
        # Estimated duration
        tk.CTkLabel(
            form_frame,
            text="Estimated Duration (hours):",
            font=("Helvetica", 12)
        ).pack(anchor="w", pady=(10, 0))
        
        duration_entry = tk.CTkEntry(form_frame, height=35, placeholder_text="e.g., 4.5")
        duration_entry.pack(fill="x", pady=(0, 10))
        
        # Route description
        tk.CTkLabel(
            form_frame,
            text="Route Description:",
            font=("Helvetica", 12)
        ).pack(anchor="w", pady=(10, 0))
        
        description_text = tk.CTkTextbox(form_frame, height=80)
        description_text.pack(fill="x", pady=(0, 10))
        
        # Notes
        tk.CTkLabel(
            form_frame,
            text="Additional Notes:",
            font=("Helvetica", 12)
        ).pack(anchor="w", pady=(10, 0))
        
        notes_text = tk.CTkTextbox(form_frame, height=60)
        notes_text.pack(fill="x", pady=(0, 20))
        
        # Button frame
        button_frame = tk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(0, 10))
        
        # Create button
        def create_route():
            route_name = name_entry.get().strip()
            delivery_date = date_entry.get().strip()
            
            if not route_name:
                messagebox.showerror("Error", "Route name is required")
                return
            
            if not delivery_date:
                messagebox.showerror("Error", "Delivery date is required")
                return
            
            # Extract driver ID if selected
            driver_text = driver_combo.get()
            driver_id = None
            if driver_text != "None":
                try:
                    driver_id = int(driver_text.split(":")[0])
                except:
                    pass
            
            messagebox.showinfo(
                "Route Created",
                f"Delivery route '{route_name}' created successfully!\n\n"
                f"Date: {delivery_date}\n"
                f"Driver: {driver_text}\n"
                f"Vehicle: {vehicle_entry.get()}\n\n"
                "Route has been saved to the system."
            )
            route_window.destroy()
        
        # Cancel button
        tk.CTkButton(
            button_frame,
            text="Cancel",
            command=route_window.destroy,
            width=100,
            height=40,
            fg_color="#757575",
            hover_color="#616161"
        ).pack(side="left", padx=5)
        
        # Create button
        tk.CTkButton(
            button_frame,
            text="Create Route",
            command=create_route,
            width=100,
            height=40,
            fg_color="#2E7D32",
            hover_color="#1B5E20"
        ).pack(side="right", padx=5)
    
    def setup_inventory_tab(self):
        """Setup inventory management tab - Now replaced with button to open Inventory Manager"""
        tab = self.tabview.tab("📦 Inventory")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)
        
        # Create a frame for the button
        frame = tk.CTkFrame(tab)
        frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)
        
        # Center content frame
        center_frame = tk.CTkFrame(frame, fg_color="transparent")
        center_frame.grid(row=0, column=0, sticky="nsew")
        center_frame.grid_columnconfigure(0, weight=1)
        center_frame.grid_rowconfigure(0, weight=1)
        
        tk.CTkLabel(
            center_frame,
            text="📦 Inventory Management",
            font=("Helvetica", 20, "bold"),
            text_color="#2E7D32"
        ).pack(pady=20)
        
        tk.CTkLabel(
            center_frame,
            text="Click the button below to open the full Inventory Management System",
            font=("Helvetica", 14),
            text_color="#666666"
        ).pack(pady=10)
        
        tk.CTkButton(
            center_frame,
            text="Open Inventory Manager",
            command=self.open_inventory_manager,
            height=60,
            width=250,
            font=("Helvetica", 16, "bold"),
            fg_color="#4CAF50",
            hover_color="#2E7D32"
        ).pack(pady=30)
        
        tk.CTkLabel(
            center_frame,
            text="Features include:\n• Complete inventory tracking\n• Stock receiving and adjustment\n• Low stock alerts\n• Inventory reports",
            font=("Helvetica", 12),
            text_color="#666666"
        ).pack(pady=20)
    
    def setup_customers_tab(self):
        """Setup customers management tab (manager only)"""
        tab = self.tabview.tab("👥 Customers")
        
        tk.CTkLabel(
            tab,
            text="Customer Management",
            font=("Helvetica", 20, "bold")
        ).pack(pady=20)
        
        # Customer search
        search_frame = tk.CTkFrame(tab)
        search_frame.pack(fill="x", padx=20, pady=10)
        
        tk.CTkLabel(search_frame, text="Search:").pack(side="left", padx=10)
        search_entry = tk.CTkEntry(search_frame, placeholder_text="Search by name, email, or phone")
        search_entry.pack(side="left", fill="x", expand=True, padx=10)
        
        tk.CTkButton(
            search_frame,
            text="Search",
            width=80
        ).pack(side="right", padx=10)
        
        # Customer list
        list_frame = tk.CTkFrame(tab)
        list_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Sample customers
        sample_customers = [
            {"id": 1, "name": "John Smith", "email": "john@example.com", "phone": "028 1234 5678", "orders": 12},
            {"id": 2, "name": "Sarah Johnson", "email": "sarah@example.com", "phone": "028 8765 4321", "orders": 8},
            {"id": 3, "name": "Mike Wilson", "email": "mike@example.com", "phone": "028 5555 1234", "orders": 15},
            {"id": 4, "name": "Emma Brown", "email": "emma@example.com", "phone": "028 9999 8888", "orders": 5}
        ]
        
        for customer in sample_customers:
            cust_frame = tk.CTkFrame(list_frame, height=50)
            cust_frame.pack(fill="x", pady=2, padx=5)
            cust_frame.grid_propagate(False)
            
            # Customer info
            tk.CTkLabel(
                cust_frame,
                text=customer['name'],
                font=("Helvetica", 12, "bold")
            ).place(x=10, y=15)
            
            tk.CTkLabel(
                cust_frame,
                text=f"{customer['email']} | {customer['phone']}",
                font=("Helvetica", 10),
                text_color="#666666"
            ).place(x=150, y=15)
            
            tk.CTkLabel(
                cust_frame,
                text=f"Orders: {customer['orders']}",
                font=("Helvetica", 10, "bold"),
                text_color="#2E7D32"
            ).place(x=350, y=15)
            
            # Action buttons
            btn_frame = tk.CTkFrame(cust_frame, fg_color="transparent")
            btn_frame.place(x=450, y=10)
            
            tk.CTkButton(
                btn_frame,
                text="View",
                width=60,
                height=30
            ).pack(side="left", padx=2)
            
            tk.CTkButton(
                btn_frame,
                text="Edit",
                width=60,
                height=30
            ).pack(side="left", padx=2)
    
    def setup_discounts_tab(self):
        """Setup discount rules tab (manager only)"""
        tab = self.tabview.tab("⚙️ Discount Rules")
        
        tk.CTkLabel(
            tab,
            text="Discount Rules Management",
            font=("Helvetica", 20, "bold")
        ).pack(pady=20)
        
        # Create new rule button
        tk.CTkButton(
            tab,
            text="+ Add New Discount Rule",
            command=self.add_discount_rule,
            height=40,
            font=("Helvetica", 14),
            fg_color="#2E7D32",
            hover_color="#1B5E20"
        ).pack(pady=10)
        
        # Rules list
        rules_frame = tk.CTkFrame(tab)
        rules_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Sample rules
        sample_rules = [
            {"min_qty": 50, "discount": 5, "category": "All", "status": "Active"},
            {"min_qty": 100, "discount": 10, "category": "Beef", "status": "Active"},
            {"min_qty": 200, "discount": 15, "category": "All", "status": "Active"},
            {"min_qty": 20, "discount": 3, "category": "Poultry", "status": "Expired"}
        ]
        
        for rule in sample_rules:
            rule_frame = tk.CTkFrame(rules_frame, height=60)
            rule_frame.pack(fill="x", pady=5, padx=10)
            rule_frame.grid_propagate(False)
            
            # Rule info
            tk.CTkLabel(
                rule_frame,
                text=f"Min Quantity: {rule['min_qty']}kg → Discount: {rule['discount']}%",
                font=("Helvetica", 12, "bold")
            ).place(x=10, y=15)
            
            tk.CTkLabel(
                rule_frame,
                text=f"Category: {rule['category']}",
                font=("Helvetica", 10),
                text_color="#666666"
            ).place(x=250, y=15)
            
            # Status badge
            status_color = "#4CAF50" if rule['status'] == "Active" else "#757575"
            tk.CTkLabel(
                rule_frame,
                text=rule['status'],
                font=("Helvetica", 10, "bold"),
                text_color="white",
                fg_color=status_color,
                corner_radius=10,
                width=70,
                height=25
            ).place(x=400, y=17)
    
    def add_discount_rule(self):
        """Add new discount rule"""
        # In full implementation, open discount rule form
        messagebox.showinfo(
            "Add Discount Rule",
            "This would open a form to:\n\n"
            "1. Set minimum quantity threshold\n"
            "2. Set discount percentage\n"
            "3. Select applicable categories\n"
            "4. Set start and end dates\n"
            "5. Configure rule priority"
        )
    
    def open_inventory_manager(self):
        """Open the Inventory Manager"""
        self.destroy()
        subprocess.Popen(["python", "jsfoods_inventory.py"])
    
    def refresh_all(self):
        """Refresh all data"""
        self.load_dashboard_data()
        self.load_orders()
        messagebox.showinfo("Refreshed", "All data has been refreshed")
    
    def go_back(self):
        """Return to main menu"""
        self.destroy()
        subprocess.Popen(["python", "jsfoods_main.py"])


if __name__ == "__main__":
    app = EmployeePortal()
    app.mainloop()