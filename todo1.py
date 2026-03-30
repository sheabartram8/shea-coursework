# Shea
'''
By moving the category to its own table and creating an addresses table, 
you will have demonstrated an understanding of Entity Relationship modeling. 
In the project report, evaluation, they should now include an Entity Relationship Diagram (ERD) 
to visually prove that the data model is normalized to 3NF

I would update these sections of jsfoods_database.py to include these tables

'''



DATABASE = 'jsfoods.db'

class DatabaseManager:
    """Manages all 3NF normalized database operations for JS Foods"""
    
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_tables()
        self.create_default_data()
    
    def connect(self):
        """Connects to the SQLite database and enables Foreign Key constraints."""
        try:
            self.conn = sqlite3.connect(DATABASE, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
            # CRITICAL: Enable Foreign Keys for 3NF integrity
            self.cursor.execute("PRAGMA foreign_keys = ON")
            print("✅ Database connected successfully with Foreign Keys enabled")
        except sqlite3.Error as e:
            print(f"❌ Database connection error: {e}")
            raise
    
    def create_tables(self):
        """
        Creates a well-structured data model normalized to 3NF.
        Separates Categories and Addresses into distinct entities to reduce redundancy.
        """
        try:
            # 1. Categories Table (Removes transitive dependency from Products)
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS categories (
                    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category_name TEXT UNIQUE NOT NULL
                )
            ''')
            
            # 2. Users Table
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
                    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # 3. Addresses Table (Normalizes User Addresses)
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS addresses (
                    address_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    address_line TEXT NOT NULL,
                    is_default INTEGER DEFAULT 1,
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
                )
            ''')
            
            # 4. Products Table (Linked to Categories via ID)
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    category_id INTEGER NOT NULL,
                    current_stock_kg REAL DEFAULT 0,
                    min_stock_level REAL DEFAULT 10,
                    is_active INTEGER DEFAULT 1,
                    price_per_kg REAL DEFAULT 0,
                    FOREIGN KEY (category_id) REFERENCES categories(category_id)
                )
            ''')
            
            # 5. Orders Table (Linked to User and specific Address)
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_id INTEGER NOT NULL,
                    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    total_amount REAL NOT NULL,
                    status TEXT DEFAULT 'pending',
                    address_id INTEGER NOT NULL,
                    payment_method TEXT DEFAULT 'cash',
                    notes TEXT,
                    FOREIGN KEY (customer_id) REFERENCES users(user_id),
                    FOREIGN KEY (address_id) REFERENCES addresses(address_id)
                )
            ''')
            
            # 6. Order Items Table
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
            
            # 7. Inventory Log Table (Audit trail)
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS inventory_log (
                    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER NOT NULL,
                    change_amount REAL NOT NULL,
                    new_stock REAL NOT NULL,
                    reason TEXT,
                    logged_by_user_id INTEGER NOT NULL,
                    log_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (product_id) REFERENCES products(product_id),
                    FOREIGN KEY (logged_by_user_id) REFERENCES users(user_id)
                )
            ''')
            
            self.conn.commit()
            print("✅ 3NF Database tables created successfully")
            
        except sqlite3.Error as e:
            print(f"❌ Error creating tables: {e}")

    def create_default_data(self):
        """Seed the database with initial categories and an admin user."""
        try:
            # Seed Categories
            categories = ['Beef', 'Lamb', 'Pork', 'Poultry']
            for cat in categories:
                self.cursor.execute("INSERT OR IGNORE INTO categories (category_name) VALUES (?)", (cat,))

            # Seed Admin User
            admin_pass = self.hash_password("admin123")
            self.cursor.execute('''
                INSERT OR IGNORE INTO users (username, password, role, first_name, last_name, email)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', ('admin', admin_pass, 'owner', 'System', 'Admin', 'admin@jsfoods.com'))
            
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"⚠️ Seed data error: {e}")

    def hash_password(self, password: str) -> str:
        """Secure hashing of passwords using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()

    def close(self):
        """Gracefully closes the database connection."""
        if self.conn:
            self.conn.close()

# Singleton instance for application-wide use
db = DatabaseManager()