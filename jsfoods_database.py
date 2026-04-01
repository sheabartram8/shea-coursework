"""
JS Foods Database Module
Database operations and helper functions
"""

import sqlite3
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

DATABASE = 'jsfoods.db'

class DatabaseManager:
    """Manages all database operations for JS Foods"""
    
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_tables()
        self.create_default_data()
    
    def connect(self):
        """Connect to database"""
        try:
            self.conn = sqlite3.connect(DATABASE, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
            # Enable foreign keys
            self.cursor.execute("PRAGMA foreign_keys = ON")
            print("✅ Database connected successfully")
        except sqlite3.Error as e:
            print(f"❌ Database connection error: {e}")
            raise
    
    def create_tables(self):
        """Create all necessary tables if they don't exist"""
        try:
            # Users table
            self.cursor.execute('''
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
                    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Products table (with category as text, unit, description)
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    description TEXT,
                    unit TEXT DEFAULT 'kg',
                    current_stock_kg REAL DEFAULT 0,
                    min_stock_level REAL DEFAULT 10,
                    is_active INTEGER DEFAULT 1,
                    price_per_kg REAL DEFAULT 0
                )
            ''')
            
            # Orders table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_id INTEGER NOT NULL,
                    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    total_amount REAL NOT NULL,
                    status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'confirmed', 'processing', 'ready', 'delivered', 'cancelled')),
                    delivery_date DATE,
                    delivery_address TEXT,
                    payment_method TEXT DEFAULT 'cash',
                    notes TEXT,
                    FOREIGN KEY (customer_id) REFERENCES users(user_id)
                )
            ''')
            
            # Order items table
            self.cursor.execute('''
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
            
            # Stock transactions table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS stock_transactions (
                    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER NOT NULL,
                    transaction_type TEXT NOT NULL,
                    quantity_kg REAL NOT NULL,
                    notes TEXT,
                    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (product_id) REFERENCES products(product_id)
                )
            ''')
            
            # Discount rules table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS discount_rules (
                    rule_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    min_quantity_kg REAL NOT NULL,
                    discount_percent REAL NOT NULL,
                    applicable_categories TEXT,
                    is_active INTEGER DEFAULT 1,
                    start_date DATE,
                    end_date DATE
                )
            ''')
            
            # Delivery routes table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS delivery_routes (
                    route_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    route_name TEXT NOT NULL,
                    employee_id INTEGER,
                    delivery_date DATE NOT NULL,
                    status TEXT DEFAULT 'scheduled',
                    vehicle_info TEXT,
                    notes TEXT,
                    FOREIGN KEY (employee_id) REFERENCES users(user_id)
                )
            ''')
            
            # Route orders table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS route_orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    route_id INTEGER NOT NULL,
                    order_id INTEGER NOT NULL,
                    sequence_number INTEGER NOT NULL,
                    FOREIGN KEY (route_id) REFERENCES delivery_routes(route_id),
                    FOREIGN KEY (order_id) REFERENCES orders(order_id)
                )
            ''')
            
            # Inventory log table (for audit, optional)
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS inventory_log (
                    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER NOT NULL,
                    change_amount REAL NOT NULL,
                    new_stock REAL NOT NULL,
                    reason TEXT,
                    logged_by INTEGER,
                    log_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (product_id) REFERENCES products(product_id),
                    FOREIGN KEY (logged_by) REFERENCES users(user_id)
                )
            ''')
            
            self.conn.commit()
            print("✅ Database tables created successfully")
            
        except sqlite3.Error as e:
            print(f"❌ Error creating tables: {e}")
    
    def create_default_data(self):
        """Seed database with default data"""
        try:
            # Insert default admin user
            admin_pass = self.hash_password("admin123")
            self.cursor.execute('''
                INSERT OR IGNORE INTO users (username, password, role, first_name, last_name, email)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', ('admin', admin_pass, 'owner', 'System', 'Admin', 'admin@jsfoods.com'))
            
            # Insert default users
            default_users = [
                ('john_customer', 'password123', 'customer', 'John', 'Doe', 'john@example.com', '1234567890', '123 Main St'),
                ('jane_employee', 'password123', 'employee', 'Jane', 'Smith', 'jane@example.com', '9876543210', '456 Oak Ave'),
                ('bob_manager', 'password123', 'manager', 'Bob', 'Johnson', 'bob@example.com', '5551234567', '789 Pine Rd')
            ]
            for user in default_users:
                hashed = self.hash_password(user[1])
                self.cursor.execute('''
                    INSERT OR IGNORE INTO users (username, password, role, first_name, last_name, email, phone, address)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (user[0], hashed, user[2], user[3], user[4], user[5], user[6], user[7]))
            
            # Insert sample products
            sample_products = [
                ('Beef Sirloin', 'Beef', 'Premium beef sirloin', 12.50, 100, 20, 'kg'),
                ('Chicken Breast', 'Poultry', 'Boneless chicken breast', 8.50, 150, 25, 'kg'),
                ('Lamb Chops', 'Lamb', 'Fresh lamb chops', 15.00, 80, 15, 'kg'),
                ('Pork Belly', 'Pork', 'Crispy pork belly', 10.00, 120, 20, 'kg'),
                ('Whole Chicken', 'Poultry', 'Fresh whole chicken', 6.50, 200, 30, 'kg'),
                ('Ribeye Steak', 'Beef', 'Premium ribeye', 18.00, 60, 10, 'kg')
            ]
            for prod in sample_products:
                self.cursor.execute('''
                    INSERT OR IGNORE INTO products (name, category, description, price_per_kg, current_stock_kg, min_stock_level, unit)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', prod)
            
            self.conn.commit()
            print("✅ Default data inserted")
        except sqlite3.Error as e:
            print(f"⚠️ Seed data error: {e}")
    
    def hash_password(self, password: str) -> str:
        """Hash password for security"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_user(self, username: str, password: str) -> Optional[Dict]:
        """Verify user credentials"""
        try:
            self.cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            user = self.cursor.fetchone()
            if not user:
                return None
            hashed_input = self.hash_password(password)
            if hashed_input == user['password']:
                return dict(user)
            return None
        except sqlite3.Error as e:
            print(f"❌ Login error: {e}")
            return None
    
    def create_user(self, user_data: Dict) -> bool:
        """Create new user"""
        try:
            hashed_password = self.hash_password(user_data['password'])
            self.cursor.execute('''
                INSERT INTO users (username, password, role, first_name, last_name, email, phone, address)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_data['username'],
                hashed_password,
                user_data['role'],
                user_data['first_name'],
                user_data['last_name'],
                user_data['email'],
                user_data.get('phone', ''),
                user_data.get('address', '')
            ))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        except sqlite3.Error as e:
            print(f"❌ User creation error: {e}")
            return False
    
    def get_users(self, role: str = None) -> List[Dict]:
        """Get users with optional role filter"""
        try:
            if role:
                self.cursor.execute("SELECT * FROM users WHERE role = ? ORDER BY last_name, first_name", (role,))
            else:
                self.cursor.execute("SELECT * FROM users ORDER BY last_name, first_name")
            return [dict(row) for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"❌ Get users error: {e}")
            return []
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get single user by ID"""
        try:
            self.cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            user = self.cursor.fetchone()
            return dict(user) if user else None
        except sqlite3.Error as e:
            print(f"❌ Get user error: {e}")
            return None
    
    def get_user_stats(self) -> Dict:
        """Get user statistics"""
        try:
            stats = {}
            self.cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'customer'")
            stats['total_customers'] = self.cursor.fetchone()[0]
            self.cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'employee'")
            stats['total_employees'] = self.cursor.fetchone()[0]
            self.cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'manager'")
            stats['total_managers'] = self.cursor.fetchone()[0]
            month_start = datetime.now().replace(day=1).strftime("%Y-%m-%d")
            self.cursor.execute("SELECT COUNT(*) FROM users WHERE registration_date >= ?", (month_start,))
            stats['new_this_month'] = self.cursor.fetchone()[0]
            return stats
        except sqlite3.Error as e:
            print(f"❌ Get user stats error: {e}")
            return {}
    
    def get_products(self, category: str = None, active_only: bool = True) -> List[Dict]:
        """Get products with optional category filter"""
        try:
            if category:
                query = "SELECT * FROM products WHERE category = ?"
                params = (category,)
                if active_only:
                    query += " AND is_active = 1"
                self.cursor.execute(query, params)
            else:
                query = "SELECT * FROM products"
                if active_only:
                    query += " WHERE is_active = 1"
                self.cursor.execute(query)
            return [dict(row) for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"❌ Get products error: {e}")
            return []
    
    def get_product_by_id(self, product_id: int) -> Optional[Dict]:
        """Get single product by ID"""
        try:
            self.cursor.execute("SELECT * FROM products WHERE product_id = ?", (product_id,))
            product = self.cursor.fetchone()
            return dict(product) if product else None
        except sqlite3.Error as e:
            print(f"❌ Get product error: {e}")
            return None
    
    def update_stock(self, product_id: int, change_amount: float, reason: str, user_id: int) -> bool:
        """Update product stock and log transaction"""
        try:
            # Get current stock
            self.cursor.execute("SELECT current_stock_kg FROM products WHERE product_id = ?", (product_id,))
            result = self.cursor.fetchone()
            if not result:
                return False
            current_stock = result[0]
            new_stock = current_stock + change_amount
            
            # Update product stock
            self.cursor.execute("UPDATE products SET current_stock_kg = ? WHERE product_id = ?", (new_stock, product_id))
            
            # Log to stock_transactions
            transaction_type = "adjustment"
            if change_amount > 0:
                transaction_type = "receive"
            elif change_amount < 0:
                transaction_type = "sale"
            
            self.cursor.execute('''
                INSERT INTO stock_transactions (product_id, transaction_type, quantity_kg, notes)
                VALUES (?, ?, ?, ?)
            ''', (product_id, transaction_type, abs(change_amount), reason))
            
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"❌ Update stock error: {e}")
            return False
    
    def get_low_stock_items(self, threshold_percent: float = 0.2) -> List[Dict]:
        """Get items with low stock"""
        try:
            self.cursor.execute('''
                SELECT *,
                       (current_stock_kg / min_stock_level) as stock_percentage
                FROM products
                WHERE is_active = 1
                AND current_stock_kg <= min_stock_level * ?
                ORDER BY stock_percentage ASC
            ''', (threshold_percent,))
            return [dict(row) for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"❌ Low stock error: {e}")
            return []
    
    def create_order(self, order_data: Dict, items: List[Dict]) -> Optional[int]:
        """Create new order with items"""
        try:
            self.cursor.execute("BEGIN TRANSACTION")
            self.cursor.execute('''
                INSERT INTO orders (customer_id, total_amount, delivery_date, delivery_address, payment_method, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                order_data['customer_id'],
                order_data['total_amount'],
                order_data.get('delivery_date'),
                order_data.get('delivery_address'),
                order_data.get('payment_method', 'cash'),
                order_data.get('notes', '')
            ))
            order_id = self.cursor.lastrowid
            
            for item in items:
                discount = self.calculate_discount(item['product_id'], item['quantity_kg'])
                final_price = item['quantity_kg'] * item['unit_price'] * (1 - discount/100)
                self.cursor.execute('''
                    INSERT INTO order_items (order_id, product_id, quantity_kg, unit_price, discount_percent, final_price)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (order_id, item['product_id'], item['quantity_kg'], item['unit_price'], discount, final_price))
                # Update stock (negative change)
                self.update_stock(item['product_id'], -item['quantity_kg'], f"Order #{order_id}", order_data['customer_id'])
            
            self.conn.commit()
            return order_id
        except sqlite3.Error as e:
            self.conn.rollback()
            print(f"❌ Create order error: {e}")
            return None
    
    def calculate_discount(self, product_id: int, quantity: float) -> float:
        """Calculate discount based on quantity and product category"""
        try:
            # Get product category
            self.cursor.execute("SELECT category FROM products WHERE product_id = ?", (product_id,))
            row = self.cursor.fetchone()
            if not row:
                return 0.0
            category = row[0]
            # Get applicable discount rules
            self.cursor.execute('''
                SELECT discount_percent FROM discount_rules 
                WHERE min_quantity_kg <= ? 
                AND (applicable_categories IS NULL OR applicable_categories LIKE ?)
                AND is_active = 1
                AND (start_date IS NULL OR start_date <= date('now'))
                AND (end_date IS NULL OR end_date >= date('now'))
                ORDER BY min_quantity_kg DESC
                LIMIT 1
            ''', (quantity, f"%{category}%"))
            result = self.cursor.fetchone()
            return result[0] if result else 0.0
        except sqlite3.Error as e:
            print(f"❌ Discount calculation error: {e}")
            return 0.0
    
    def get_user_orders(self, user_id: int, limit: int = 50) -> List[Dict]:
        """Get orders for a specific user"""
        try:
            self.cursor.execute('''
                SELECT o.*, 
                       (SELECT COUNT(*) FROM order_items WHERE order_id = o.order_id) as item_count
                FROM orders o
                WHERE o.customer_id = ?
                ORDER BY o.order_date DESC
                LIMIT ?
            ''', (user_id, limit))
            return [dict(row) for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"❌ Get user orders error: {e}")
            return []
    
    def get_order_details(self, order_id: int) -> Tuple[Optional[Dict], List[Dict]]:
        """Get order details with items"""
        try:
            self.cursor.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,))
            order = self.cursor.fetchone()
            if not order:
                return None, []
            self.cursor.execute('''
                SELECT oi.*, p.name as product_name, p.category
                FROM order_items oi
                JOIN products p ON oi.product_id = p.product_id
                WHERE oi.order_id = ?
            ''', (order_id,))
            items = [dict(row) for row in self.cursor.fetchall()]
            return dict(order), items
        except sqlite3.Error as e:
            print(f"❌ Get order details error: {e}")
            return None, []
    
    def get_sales_report(self, start_date: str, end_date: str) -> Dict:
        """Generate sales report for date range"""
        try:
            self.cursor.execute('''
                SELECT 
                    COUNT(*) as total_orders,
                    SUM(total_amount) as total_revenue,
                    AVG(total_amount) as avg_order_value
                FROM orders 
                WHERE order_date BETWEEN ? AND ?
                AND status != 'cancelled'
            ''', (start_date, end_date))
            totals = dict(self.cursor.fetchone()) or {}
            self.cursor.execute('''
                SELECT 
                    p.category,
                    SUM(oi.quantity_kg) as total_kg,
                    SUM(oi.final_price) as total_revenue,
                    COUNT(DISTINCT o.order_id) as order_count
                FROM order_items oi
                JOIN orders o ON oi.order_id = o.order_id
                JOIN products p ON oi.product_id = p.product_id
                WHERE o.order_date BETWEEN ? AND ?
                AND o.status != 'cancelled'
                GROUP BY p.category
                ORDER BY total_revenue DESC
            ''', (start_date, end_date))
            by_category = [dict(row) for row in self.cursor.fetchall()]
            self.cursor.execute('''
                SELECT 
                    p.name,
                    p.category,
                    SUM(oi.quantity_kg) as total_kg,
                    SUM(oi.final_price) as total_revenue,
                    COUNT(*) as times_ordered
                FROM order_items oi
                JOIN orders o ON oi.order_id = o.order_id
                JOIN products p ON oi.product_id = p.product_id
                WHERE o.order_date BETWEEN ? AND ?
                AND o.status != 'cancelled'
                GROUP BY p.product_id
                ORDER BY total_revenue DESC
                LIMIT 10
            ''', (start_date, end_date))
            top_products = [dict(row) for row in self.cursor.fetchall()]
            return {
                'period': {'start': start_date, 'end': end_date},
                'totals': totals,
                'by_category': by_category,
                'top_products': top_products
            }
        except sqlite3.Error as e:
            print(f"❌ Sales report error: {e}")
            return {}
    
    def create_delivery_route(self, route_data: Dict) -> bool:
        """Create delivery route"""
        try:
            self.cursor.execute('''
                INSERT INTO delivery_routes (route_name, employee_id, delivery_date, vehicle_info, notes)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                route_data['route_name'],
                route_data.get('employee_id'),
                route_data['delivery_date'],
                route_data.get('vehicle_info', ''),
                route_data.get('notes', '')
            ))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"❌ Create route error: {e}")
            return False
    
    def assign_order_to_route(self, route_id: int, order_id: int, sequence: int) -> bool:
        """Assign order to delivery route"""
        try:
            self.cursor.execute('''
                INSERT INTO route_orders (route_id, order_id, sequence_number)
                VALUES (?, ?, ?)
            ''', (route_id, order_id, sequence))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"❌ Assign order to route error: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

# Singleton instance
db = DatabaseManager()