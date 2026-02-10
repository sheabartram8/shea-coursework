"""
JS Foods - Main Application
Advanced Ordering System for Meat Wholesaler
"""

import customtkinter as tk
import sqlite3
import subprocess
import sys

DATABASE = 'jsfoods.db'

class JSFoodsApp(tk.CTk):
    def __init__(self):
        super().__init__()
        
        # Window configuration
        self.title("JS Foods - Advanced Ordering System")
        self.geometry("1200x700")
        self.resizable(True, True)
        
        # Set appearance
        tk.set_appearance_mode("light")
        tk.set_default_color_theme("blue")
        
        # Create database tables
        self.create_tables()
        
        # Immediately open login screen
        self.open_login()
        
    def create_tables(self):
        """Create all necessary database tables"""
        try:
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL CHECK(role IN ('customer', 'employee', 'manager', 'owner')),
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    phone TEXT,
                    address TEXT,
                    registration_date TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Products table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    description TEXT,
                    price_per_kg REAL NOT NULL,
                    current_stock_kg REAL DEFAULT 0,
                    min_stock_level REAL DEFAULT 10,
                    unit TEXT DEFAULT 'kg',
                    is_active INTEGER DEFAULT 1
                )
            ''')
            
            # Orders table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_id INTEGER NOT NULL,
                    order_date TEXT DEFAULT CURRENT_TIMESTAMP,
                    total_amount REAL NOT NULL,
                    status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'confirmed', 'processing', 'ready', 'delivered', 'cancelled')),
                    delivery_date TEXT,
                    delivery_address TEXT,
                    payment_method TEXT,
                    notes TEXT,
                    FOREIGN KEY (customer_id) REFERENCES users(user_id)
                )
            ''')
            
            # Order items table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS order_items (
                    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    quantity_kg REAL NOT NULL,
                    unit_price REAL NOT NULL,
                    discount_percent REAL DEFAULT 0,
                    final_price REAL NOT NULL,
                    FOREIGN KEY (order_id) REFERENCES orders(order_id),
                    FOREIGN KEY (product_id) REFERENCES products(product_id)
                )
            ''')
            
            # Discount rules table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS discount_rules (
                    rule_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    min_quantity_kg REAL NOT NULL,
                    discount_percent REAL NOT NULL,
                    applicable_categories TEXT,
                    start_date TEXT,
                    end_date TEXT,
                    is_active INTEGER DEFAULT 1
                )
            ''')
            
            # Inventory log table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS inventory_log (
                    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER NOT NULL,
                    change_amount REAL NOT NULL,
                    new_stock REAL NOT NULL,
                    reason TEXT,
                    logged_by INTEGER,
                    log_date TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (product_id) REFERENCES products(product_id),
                    FOREIGN KEY (logged_by) REFERENCES users(user_id)
                )
            ''')
            
            # Delivery routes table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS delivery_routes (
                    route_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    route_name TEXT NOT NULL,
                    employee_id INTEGER,
                    delivery_date TEXT NOT NULL,
                    status TEXT DEFAULT 'scheduled',
                    vehicle_info TEXT,
                    notes TEXT,
                    FOREIGN KEY (employee_id) REFERENCES users(user_id)
                )
            ''')
            
            # Route orders table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS route_orders (
                    route_order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    route_id INTEGER NOT NULL,
                    order_id INTEGER NOT NULL,
                    sequence_number INTEGER,
                    estimated_arrival TEXT,
                    actual_arrival TEXT,
                    status TEXT DEFAULT 'pending',
                    FOREIGN KEY (route_id) REFERENCES delivery_routes(route_id),
                    FOREIGN KEY (order_id) REFERENCES orders(order_id)
                )
            ''')
            
            conn.commit()
            
            # Insert default admin if not exists
            cursor.execute("SELECT COUNT(*) FROM users WHERE role='owner'")
            if cursor.fetchone()[0] == 0:
                cursor.execute('''
                    INSERT INTO users (username, password, role, first_name, last_name, email)
                    VALUES ('admin', 'admin123', 'owner', 'System', 'Administrator', 'admin@jsfoods.com')
                ''')
                conn.commit()
                
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        finally:
            conn.close()
    
    def open_login(self):
        """Open login window"""
        self.destroy()  # Close the main window
        subprocess.Popen([sys.executable, "jsfoods_login.py"])

if __name__ == "__main__":
    app = JSFoodsApp()
    app.mainloop()