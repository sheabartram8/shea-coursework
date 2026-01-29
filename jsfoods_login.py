"""
JS Foods Login System
Authentication and registration
"""

import customtkinter as tk
from tkinter import messagebox
import re
import sqlite3
import subprocess
from jsfoods_database import db

class LoginApp(tk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("JS Foods - Login")
        self.geometry("500x600")
        self.resizable(False, False)
        
        tk.set_appearance_mode("light")
        tk.set_default_color_theme("blue")
        
        self.current_user = None
        self.setup_ui()
    
    def setup_ui(self):
        """Setup login interface"""
        # Main frame
        main_frame = tk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=40, pady=40)
        
        # Logo/Title
        tk.CTkLabel(
            main_frame,
            text="JS FOODS",
            font=("Helvetica", 32, "bold"),
            text_color="#2E7D32"
        ).pack(pady=(0, 10))
        
        tk.CTkLabel(
            main_frame,
            text="Secure Login Portal",
            font=("Helvetica", 16),
            text_color="#666666"
        ).pack(pady=(0, 30))
        
        # Login frame
        login_frame = tk.CTkFrame(main_frame)
        login_frame.pack(fill="x", pady=10)
        
        tk.CTkLabel(
            login_frame,
            text="Login to Your Account",
            font=("Helvetica", 18, "bold")
        ).pack(pady=20)
        
        # Username
        tk.CTkLabel(
            login_frame,
            text="Username",
            font=("Helvetica", 12)
        ).pack(anchor="w", padx=20, pady=(10, 0))
        
        self.username_entry = tk.CTkEntry(
            login_frame,
            placeholder_text="Enter your username",
            height=40,
            font=("Helvetica", 14)
        )
        self.username_entry.pack(fill="x", padx=20, pady=(0, 10))
        
        # Password
        tk.CTkLabel(
            login_frame,
            text="Password",
            font=("Helvetica", 12)
        ).pack(anchor="w", padx=20, pady=(10, 0))
        
        self.password_entry = tk.CTkEntry(
            login_frame,
            placeholder_text="Enter your password",
            show="•",
            height=40,
            font=("Helvetica", 14)
        )
        self.password_entry.pack(fill="x", padx=20, pady=(0, 20))
        
        # Show password checkbox
        self.show_pass_var = tk.BooleanVar()
        tk.CTkCheckBox(
            login_frame,
            text="Show Password",
            variable=self.show_pass_var,
            command=self.toggle_password_visibility
        ).pack(anchor="w", padx=20, pady=(0, 20))
        
        # Login button
        login_btn = tk.CTkButton(
            login_frame,
            text="Login",
            command=self.login,
            height=45,
            font=("Helvetica", 14, "bold"),
            fg_color="#2E7D32",
            hover_color="#1B5E20"
        )
        login_btn.pack(fill="x", padx=20, pady=(0, 20))
        
        # Register link - FIXED: Better contrast
        register_frame = tk.CTkFrame(main_frame, fg_color="transparent")
        register_frame.pack(fill="x", pady=10)
        
        tk.CTkLabel(
            register_frame,
            text="New to JS Foods?",
            font=("Helvetica", 12)
        ).pack(side="left", padx=20)
        
        register_link = tk.CTkButton(
            register_frame,
            text="Create Account",
            command=self.open_register,
            fg_color="#E8F5E9",
            hover_color="#C8E6C9",
            text_color="#1B5E20",
            font=("Helvetica", 12, "bold"),
            border_width=1,
            border_color="#2E7D32"
        )
        register_link.pack(side="right", padx=20)
        
        # Role selection (for quick testing)
        role_frame = tk.CTkFrame(main_frame, fg_color="transparent")
        role_frame.pack(fill="x", pady=20)
        
        tk.CTkLabel(
            role_frame,
            text="Quick Login (Testing):",
            font=("Helvetica", 12)
        ).pack(anchor="w", padx=20, pady=(0, 5))
        
        role_btn_frame = tk.CTkFrame(role_frame, fg_color="transparent")
        role_btn_frame.pack(fill="x", padx=20)
        
        roles = [
            ("Customer", "customer"),
            ("Employee", "employee"),
            ("Manager", "manager"),
            ("Owner", "owner")
        ]
        
        for role_name, role_type in roles:
            btn = tk.CTkButton(
                role_btn_frame,
                text=role_name,
                command=lambda r=role_type: self.quick_login(r),
                width=100,
                height=35,
                font=("Helvetica", 11)
            )
            btn.pack(side="left", padx=5, pady=5)
    
    def toggle_password_visibility(self):
        """Toggle password visibility"""
        if self.show_pass_var.get():
            self.password_entry.configure(show="")
        else:
            self.password_entry.configure(show="•")
    
    def validate_input(self, username, password):
        """Validate login input"""
        if not username.strip():
            return "Username is required"
        if not password.strip():
            return "Password is required"
        if len(password) < 6:
            return "Password must be at least 6 characters"
        return None
    
    def login(self):
        """Handle login"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        # Validate
        error = self.validate_input(username, password)
        if error:
            messagebox.showerror("Validation Error", error)
            return
        
        print(f"\n=== Login Attempt ===")
        print(f"Username: {username}")
        print(f"Password length: {len(password)}")
        
        # Verify credentials
        user = db.verify_user(username, password)
        
        if user:
            self.current_user = user
            print(f"Login successful! User ID: {user['user_id']}, Role: {user['role']}")  # FIXED: Changed 'id' to 'user_id'
            messagebox.showinfo("Login Successful", f"Welcome, {user['first_name']}!")
            self.open_dashboard(user['role'])
        else:
            print("Login failed: Invalid credentials")
            messagebox.showerror("Login Failed", "Invalid username or password")
    
    def quick_login(self, role):
        """Quick login for testing purposes"""
        test_users = {
            "customer": ("john_customer", "password123"),
            "employee": ("jane_employee", "password123"),
            "manager": ("bob_manager", "password123"),
            "owner": ("admin", "admin123")
        }
        
        username, password = test_users.get(role, ("", ""))
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.username_entry.insert(0, username)
        self.password_entry.insert(0, password)
        self.login()
    
    def open_register(self):
        """Open registration window"""
        RegisterApp(self)
    
    def open_dashboard(self, role):
        """Open appropriate dashboard based on role"""
        self.destroy()
        
        if role == "customer":
            subprocess.Popen(["python", "jsfoods_customer.py"])
        elif role in ["employee", "manager"]:
            subprocess.Popen(["python", "jsfoods_employee.py"])
        elif role == "owner":
            subprocess.Popen(["python", "jsfoods_admin.py"])


class RegisterApp(tk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.parent = parent
        self.title("JS Foods - Register")
        self.geometry("550x600")
        self.resizable(True, True)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup registration interface with scrollbar"""
        # Create main container frame
        main_container = tk.CTkFrame(self)
        main_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Create a canvas for scrolling
        canvas = tk.CTkCanvas(main_container, bg='white', highlightthickness=0)
        scrollbar = tk.CTkScrollbar(main_container, orientation="vertical", command=canvas.yview)
        
        # Create scrollable frame
        self.scrollable_frame = tk.CTkFrame(canvas, fg_color="transparent")
        
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
            text="Create New Account",
            font=("Helvetica", 24, "bold"),
            text_color="#2E7D32"
        ).pack(pady=(10, 20))
        
        # Registration form
        form_frame = tk.CTkFrame(self.scrollable_frame)
        form_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Personal Information
        tk.CTkLabel(
            form_frame,
            text="Personal Information",
            font=("Helvetica", 16, "bold")
        ).pack(pady=(15, 10))
        
        # First Name
        tk.CTkLabel(
            form_frame,
            text="First Name *",
            font=("Helvetica", 12)
        ).pack(anchor="w", padx=20, pady=(5, 0))
        
        self.first_name_entry = tk.CTkEntry(
            form_frame,
            placeholder_text="Enter your first name",
            height=35
        )
        self.first_name_entry.pack(fill="x", padx=20, pady=(0, 5))
        
        # Last Name
        tk.CTkLabel(
            form_frame,
            text="Last Name *",
            font=("Helvetica", 12)
        ).pack(anchor="w", padx=20, pady=(5, 0))
        
        self.last_name_entry = tk.CTkEntry(
            form_frame,
            placeholder_text="Enter your last name",
            height=35
        )
        self.last_name_entry.pack(fill="x", padx=20, pady=(0, 10))
        
        # Contact Information
        tk.CTkLabel(
            form_frame,
            text="Contact Information",
            font=("Helvetica", 16, "bold")
        ).pack(pady=(10, 10))
        
        # Email
        tk.CTkLabel(
            form_frame,
            text="Email Address *",
            font=("Helvetica", 12)
        ).pack(anchor="w", padx=20, pady=(5, 0))
        
        self.email_entry = tk.CTkEntry(
            form_frame,
            placeholder_text="Enter your email",
            height=35
        )
        self.email_entry.pack(fill="x", padx=20, pady=(0, 5))
        
        # Phone
        tk.CTkLabel(
            form_frame,
            text="Phone Number",
            font=("Helvetica", 12)
        ).pack(anchor="w", padx=20, pady=(5, 0))
        
        self.phone_entry = tk.CTkEntry(
            form_frame,
            placeholder_text="Enter your phone number",
            height=35
        )
        self.phone_entry.pack(fill="x", padx=20, pady=(0, 5))
        
        # Address
        tk.CTkLabel(
            form_frame,
            text="Delivery Address",
            font=("Helvetica", 12)
        ).pack(anchor="w", padx=20, pady=(5, 0))
        
        self.address_entry = tk.CTkEntry(
            form_frame,
            placeholder_text="Enter your full address",
            height=35
        )
        self.address_entry.pack(fill="x", padx=20, pady=(0, 10))
        
        # Account Information
        tk.CTkLabel(
            form_frame,
            text="Account Information",
            font=("Helvetica", 16, "bold")
        ).pack(pady=(10, 10))
        
        # Username
        tk.CTkLabel(
            form_frame,
            text="Username *",
            font=("Helvetica", 12)
        ).pack(anchor="w", padx=20, pady=(5, 0))
        
        self.username_entry = tk.CTkEntry(
            form_frame,
            placeholder_text="Choose a username",
            height=35
        )
        self.username_entry.pack(fill="x", padx=20, pady=(0, 5))
        
        # Password
        tk.CTkLabel(
            form_frame,
            text="Password *",
            font=("Helvetica", 12)
        ).pack(anchor="w", padx=20, pady=(5, 0))
        
        self.password_entry = tk.CTkEntry(
            form_frame,
            placeholder_text="Choose a password (min. 6 chars)",
            show="•",
            height=35
        )
        self.password_entry.pack(fill="x", padx=20, pady=(0, 5))
        
        # Confirm Password
        tk.CTkLabel(
            form_frame,
            text="Confirm Password *",
            font=("Helvetica", 12)
        ).pack(anchor="w", padx=20, pady=(5, 0))
        
        self.confirm_password_entry = tk.CTkEntry(
            form_frame,
            placeholder_text="Confirm your password",
            show="•",
            height=35
        )
        self.confirm_password_entry.pack(fill="x", padx=20, pady=(0, 10))
        
        # Role selection (default customer)
        tk.CTkLabel(
            form_frame,
            text="Account Type",
            font=("Helvetica", 12)
        ).pack(anchor="w", padx=20, pady=(5, 0))
        
        self.role_var = tk.StringVar(value="customer")
        role_frame = tk.CTkFrame(form_frame, fg_color="transparent")
        role_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        roles = [("Customer", "customer")]
        
        for text, value in roles:
            tk.CTkRadioButton(
                role_frame,
                text=text,
                variable=self.role_var,
                value=value
            ).pack(side="left", padx=10)
        
        # Register button
        register_btn_frame = tk.CTkFrame(form_frame, fg_color="transparent")
        register_btn_frame.pack(fill="x", padx=20, pady=(10, 20))
        
        tk.CTkButton(
            register_btn_frame,
            text="Cancel",
            command=self.destroy,
            width=100,
            height=40,
            fg_color="#757575",
            hover_color="#616161"
        ).pack(side="left", padx=5)
        
        tk.CTkButton(
            register_btn_frame,
            text="Create Account",
            command=self.register,
            width=100,
            height=40,
            fg_color="#2E7D32",
            hover_color="#1B5E20"
        ).pack(side="right", padx=5)
    
    def validate_registration(self):
        """Validate registration form"""
        errors = []
        
        # Check required fields
        required_fields = {
            "First Name": self.first_name_entry.get().strip(),
            "Last Name": self.last_name_entry.get().strip(),
            "Email": self.email_entry.get().strip(),
            "Username": self.username_entry.get().strip(),
            "Password": self.password_entry.get()
        }
        
        for field, value in required_fields.items():
            if not value:
                errors.append(f"{field} is required")
        
        # Validate email format
        email = self.email_entry.get().strip()
        if email and not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            errors.append("Please enter a valid email address")
        
        # Validate password
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        
        if password and len(password) < 6:
            errors.append("Password must be at least 6 characters")
        
        if password != confirm_password:
            errors.append("Passwords do not match")
        
        return errors
    
    def register(self):
        """Handle registration"""
        # Validate form
        errors = self.validate_registration()
        if errors:
            messagebox.showerror("Registration Error", "\n".join(errors))
            return
        
        # Prepare user data
        user_data = {
            'username': self.username_entry.get().strip(),
            'password': self.password_entry.get(),
            'role': self.role_var.get(),
            'first_name': self.first_name_entry.get().strip(),
            'last_name': self.last_name_entry.get().strip(),
            'email': self.email_entry.get().strip(),
            'phone': self.phone_entry.get().strip(),
            'address': self.address_entry.get().strip()
        }
        
        # Create user
        if db.create_user(user_data):
            messagebox.showinfo(
                "Registration Successful",
                "Your account has been created successfully!\n\n"
                f"Username: {user_data['username']}\n"
                f"Role: {user_data['role'].title()}\n\n"
                "You can now login with your credentials."
            )
            self.destroy()
        else:
            messagebox.showerror(
                "Registration Failed",
                "Could not create account. Username or email may already exist."
            )


if __name__ == "__main__":
    app = LoginApp()
    app.mainloop()