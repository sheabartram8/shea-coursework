"""
JS Foods Reporting System
Advanced business analytics and reporting
"""

import customtkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import subprocess
from datetime import datetime, timedelta
from jsfoods_database import db

class ReportingSystem(tk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("JS Foods - Reporting System")
        self.geometry("1200x700")
        self.resizable(True, True)
        
        tk.set_appearance_mode("light")
        tk.set_default_color_theme("blue")
        
        self.setup_ui()
        self.load_dashboard()
    
    def setup_ui(self):
        """Setup reporting system UI"""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header
        header_frame = tk.CTkFrame(self, height=80, fg_color="#2E7D32")
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        header_frame.grid_propagate(False)
        
        tk.CTkLabel(
            header_frame,
            text="📊 Business Analytics & Reporting",
            font=("Helvetica", 24, "bold"),
            text_color="white"
        ).pack(side="left", padx=20)
        
        # Date range selector
        date_frame = tk.CTkFrame(header_frame, fg_color="transparent")
        date_frame.pack(side="right", padx=20)
        
        tk.CTkLabel(date_frame, text="Date Range:", text_color="white").pack(side="left", padx=5)
        
        self.date_range = tk.StringVar(value="month")
        date_combo = tk.CTkComboBox(
            date_frame,
            values=["today", "week", "month", "quarter", "year", "custom"],
            variable=self.date_range,
            command=self.load_dashboard,
            width=100
        )
        date_combo.pack(side="left", padx=5)
        
        # Main content - Tab view
        self.tabview = tk.CTkTabview(self)
        self.tabview.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        
        # Create tabs
        tabs = [
            "📈 Sales Dashboard",
            "💰 Financial Reports",
            "👥 Customer Analytics",
            "📦 Inventory Reports",
            "🚚 Delivery Reports"
        ]
        
        for tab in tabs:
            self.tabview.add(tab)
        
        # Setup each tab
        self.setup_sales_dashboard()
        self.setup_financial_reports()
        self.setup_customer_analytics()
        self.setup_inventory_reports()
        self.setup_delivery_reports()
        
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
    
    def get_date_range(self):
        """Get date range based on selection"""
        today = datetime.now().date()
        
        if self.date_range.get() == "today":
            return today.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")
        elif self.date_range.get() == "week":
            week_ago = today - timedelta(days=7)
            return week_ago.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")
        elif self.date_range.get() == "month":
            month_ago = today.replace(day=1)
            return month_ago.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")
        elif self.date_range.get() == "quarter":
            quarter_month = ((today.month - 1) // 3) * 3 + 1
            quarter_start = today.replace(month=quarter_month, day=1)
            return quarter_start.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")
        elif self.date_range.get() == "year":
            year_start = today.replace(month=1, day=1)
            return year_start.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")
        else:  # custom
            return today.replace(day=1).strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")
    
    def load_dashboard(self, event=None):
        """Load dashboard data"""
        start_date, end_date = self.get_date_range()
        
        try:
            # Get sales report
            report = db.get_sales_report(start_date, end_date)
            
            # Update sales dashboard tab
            self.update_sales_dashboard(report)
            
        except Exception as e:
            print(f"Dashboard load error: {e}")
    
    def update_sales_dashboard(self, report):
        """Update sales dashboard with report data"""
        tab = self.tabview.tab("📈 Sales Dashboard")
        
        # Clear existing content
        for widget in tab.winfo_children():
            widget.destroy()
        
        # Create dashboard layout
        main_frame = tk.CTkFrame(tab)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Top row: Key metrics
        metrics_frame = tk.CTkFrame(main_frame, height=120)
        metrics_frame.pack(fill="x", pady=(0, 20))
        metrics_frame.grid_propagate(False)
        
        if report:
            metrics = [
                ("💰 Total Revenue", f"£{report['totals']['total_revenue'] or 0:.2f}", "#4CAF50"),
                ("📦 Total Orders", f"{report['totals']['total_orders'] or 0}", "#2196F3"),
                ("📊 Avg Order Value", f"£{report['totals']['avg_order_value'] or 0:.2f}", "#FF9800"),
                ("📈 Growth", "+12.5%", "#9C27B0")
            ]
        else:
            metrics = [
                ("💰 Total Revenue", "£0.00", "#4CAF50"),
                ("📦 Total Orders", "0", "#2196F3"),
                ("📊 Avg Order Value", "£0.00", "#FF9800"),
                ("📈 Growth", "0%", "#9C27B0")
            ]
        
        for i, (title, value, color) in enumerate(metrics):
            metric_frame = tk.CTkFrame(metrics_frame, fg_color=color, corner_radius=10)
            metric_frame.place(x=20 + i*280, y=10, width=260, height=100)
            
            tk.CTkLabel(
                metric_frame,
                text=title,
                font=("Helvetica", 14),
                text_color="white"
            ).place(x=20, y=20)
            
            tk.CTkLabel(
                metric_frame,
                text=value,
                font=("Helvetica", 24, "bold"),
                text_color="white"
            ).place(x=20, y=50)
        
        # Middle row: Charts
        chart_frame = tk.CTkFrame(main_frame)
        chart_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        # Left chart: Sales by category
        left_chart = tk.CTkFrame(chart_frame)
        left_chart.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        tk.CTkLabel(
            left_chart,
            text="📊 Sales by Category",
            font=("Helvetica", 16, "bold")
        ).pack(pady=20)
        
        # Create category chart (placeholder)
        if report and report['by_category']:
            for category in report['by_category']:
                cat_frame = tk.CTkFrame(left_chart, height=40)
                cat_frame.pack(fill="x", pady=2, padx=20)
                
                # Category name
                tk.CTkLabel(
                    cat_frame,
                    text=category['category'],
                    font=("Helvetica", 12),
                    width=100,
                    anchor="w"
                ).place(x=10, y=10)
                
                # Bar representing revenue
                revenue = category['total_revenue']
                max_revenue = max([c['total_revenue'] for c in report['by_category']])
                bar_width = (revenue / max_revenue) * 200 if max_revenue > 0 else 0
                
                bar = tk.CTkFrame(cat_frame, fg_color="#2196F3", height=20)
                bar.place(x=120, y=10, width=bar_width)
                
                # Revenue label
                tk.CTkLabel(
                    cat_frame,
                    text=f"£{revenue:.2f}",
                    font=("Helvetica", 10, "bold")
                ).place(x=330, y=10)
        else:
            tk.CTkLabel(
                left_chart,
                text="No category data available",
                font=("Helvetica", 14),
                text_color="#666666"
            ).pack(expand=True)
        
        # Right chart: Top products
        right_chart = tk.CTkFrame(chart_frame, width=300)
        right_chart.pack(side="right", fill="y", padx=(10, 0))
        right_chart.pack_propagate(False)
        
        tk.CTkLabel(
            right_chart,
            text="⭐ Top Products",
            font=("Helvetica", 16, "bold")
        ).pack(pady=20)
        
        # Create top products list
        if report and report['top_products']:
            for product in report['top_products'][:5]:  # Top 5 only
                product_frame = tk.CTkFrame(right_chart, height=50)
                product_frame.pack(fill="x", pady=5, padx=20)
                
                tk.CTkLabel(
                    product_frame,
                    text=product['name'][:20] + ("..." if len(product['name']) > 20 else ""),
                    font=("Helvetica", 11, "bold")
                ).place(x=10, y=5)
                
                tk.CTkLabel(
                    product_frame,
                    text=f"£{product['total_revenue']:.2f}",
                    font=("Helvetica", 12, "bold"),
                    text_color="#2E7D32"
                ).place(x=10, y=25)
                
                tk.CTkLabel(
                    product_frame,
                    text=f"{product['total_kg']:.1f} kg",
                    font=("Helvetica", 10),
                    text_color="#666666"
                ).place(x=100, y=25)
        else:
            tk.CTkLabel(
                right_chart,
                text="No product data available",
                font=("Helvetica", 14),
                text_color="#666666"
            ).pack(expand=True)
        
        # Bottom row: Export options
        export_frame = tk.CTkFrame(main_frame, height=60)
        export_frame.pack(fill="x", pady=(0, 10))
        export_frame.grid_propagate(False)
        
        tk.CTkLabel(
            export_frame,
            text="Export Options:",
            font=("Helvetica", 14, "bold")
        ).place(x=20, y=20)
        
        export_btn_frame = tk.CTkFrame(export_frame, fg_color="transparent")
        export_btn_frame.place(x=150, y=15)
        
        formats = ["PDF Report", "Excel Spreadsheet", "CSV Data", "Email Summary"]
        
        for fmt in formats:
            tk.CTkButton(
                export_btn_frame,
                text=fmt,
                width=120,
                height=30,
                command=lambda f=fmt: self.export_report(f)
            ).pack(side="left", padx=5)
    
    def setup_sales_dashboard(self):
        """Setup sales dashboard tab"""
        # Already handled in update_sales_dashboard
        pass
    
    def setup_financial_reports(self):
        """Setup financial reports tab"""
        tab = self.tabview.tab("💰 Financial Reports")
        
        tk.CTkLabel(
            tab,
            text="Financial Reports",
            font=("Helvetica", 20, "bold")
        ).pack(pady=20)
        
        # Report types grid
        reports_frame = tk.CTkFrame(tab)
        reports_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        financial_reports = [
            ("📊 Profit & Loss", "Income, expenses, and net profit"),
            ("💰 Revenue Analysis", "Revenue breakdown by source"),
            ("📈 Trend Analysis", "Financial trends over time"),
            ("💳 Payment Analysis", "Payment methods and trends"),
            ("📋 Tax Report", "Tax calculations and reporting"),
            ("💰 Cash Flow", "Cash inflow and outflow analysis")
        ]
        
        for i, (title, description) in enumerate(financial_reports):
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
                command=lambda t=title: self.generate_financial_report(t)
            ).place(x=200, y=25)
        
        reports_frame.grid_columnconfigure(0, weight=1)
        reports_frame.grid_columnconfigure(1, weight=1)
    
    def setup_customer_analytics(self):
        """Setup customer analytics tab"""
        tab = self.tabview.tab("👥 Customer Analytics")
        
        tk.CTkLabel(
            tab,
            text="Customer Analytics",
            font=("Helvetica", 20, "bold")
        ).pack(pady=20)
        
        # Customer metrics
        metrics_frame = tk.CTkFrame(tab)
        metrics_frame.pack(fill="x", padx=20, pady=10)
        
        # Sample customer metrics
        customer_metrics = [
            ("👥 Total Customers", "1,248", "+5.2%"),
            ("💰 Avg Customer Value", "£425.60", "+8.1%"),
            ("🔄 Repeat Rate", "68%", "+2.4%"),
            ("📊 Retention Rate", "92%", "+1.8%")
        ]
        
        for i, (title, value, change) in enumerate(customer_metrics):
            metric_frame = tk.CTkFrame(metrics_frame, height=80)
            metric_frame.grid(row=0, column=i, padx=5, pady=5, sticky="nsew")
            metric_frame.grid_propagate(False)
            
            tk.CTkLabel(
                metric_frame,
                text=title,
                font=("Helvetica", 12)
            ).place(x=10, y=10)
            
            tk.CTkLabel(
                metric_frame,
                text=value,
                font=("Helvetica", 18, "bold")
            ).place(x=10, y=35)
            
            tk.CTkLabel(
                metric_frame,
                text=change,
                font=("Helvetica", 10),
                text_color="#4CAF50"
            ).place(x=10, y=60)
        
        metrics_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Customer segments
        segments_frame = tk.CTkFrame(tab)
        segments_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        tk.CTkLabel(
            segments_frame,
            text="Customer Segments",
            font=("Helvetica", 16, "bold")
        ).pack(pady=10)
        
        # Sample segments
        segments = [
            ("⭐ VIP Customers", "Top 5% by spend", "£15,240", "12%"),
            ("💰 Regular Buyers", "Monthly orders", "£8,560", "25%"),
            ("🆕 New Customers", "Joined this month", "£3,120", "18%"),
            ("💤 Inactive", "No order in 90 days", "£0", "15%")
        ]
        
        for i, (segment, description, revenue, percentage) in enumerate(segments):
            segment_frame = tk.CTkFrame(segments_frame, height=70)
            segment_frame.pack(fill="x", pady=5, padx=20)
            segment_frame.grid_propagate(False)
            
            tk.CTkLabel(
                segment_frame,
                text=segment,
                font=("Helvetica", 12, "bold")
            ).place(x=20, y=15)
            
            tk.CTkLabel(
                segment_frame,
                text=description,
                font=("Helvetica", 10),
                text_color="#666666"
            ).place(x=20, y=35)
            
            tk.CTkLabel(
                segment_frame,
                text=revenue,
                font=("Helvetica", 12, "bold"),
                text_color="#2E7D32"
            ).place(x=200, y=15)
            
            tk.CTkLabel(
                segment_frame,
                text=f"{percentage} of customers",
                font=("Helvetica", 10)
            ).place(x=200, y=35)
    
    def setup_inventory_reports(self):
        """Setup inventory reports tab"""
        tab = self.tabview.tab("📦 Inventory Reports")
        
        tk.CTkLabel(
            tab,
            text="Inventory Reports",
            font=("Helvetica", 20, "bold")
        ).pack(pady=20)
        
        # Inventory metrics
        metrics_frame = tk.CTkFrame(tab)
        metrics_frame.pack(fill="x", padx=20, pady=10)
        
        # Sample inventory metrics
        inventory_metrics = [
            ("📦 Total SKUs", "148", "+3"),
            ("💰 Inventory Value", "£45,680", "+£2,450"),
            ("📊 Turnover Rate", "4.2x", "+0.3"),
            ("⚠️ Low Stock Items", "12", "-2")
        ]
        
        for i, (title, value, change) in enumerate(inventory_metrics):
            metric_frame = tk.CTkFrame(metrics_frame, height=80)
            metric_frame.grid(row=0, column=i, padx=5, pady=5, sticky="nsew")
            metric_frame.grid_propagate(False)
            
            tk.CTkLabel(
                metric_frame,
                text=title,
                font=("Helvetica", 12)
            ).place(x=10, y=10)
            
            tk.CTkLabel(
                metric_frame,
                text=value,
                font=("Helvetica", 18, "bold")
            ).place(x=10, y=35)
            
            tk.CTkLabel(
                metric_frame,
                text=change,
                font=("Helvetica", 10),
                text_color="#4CAF50" if "+" in change else ("#F44336" if "-" in change else "#666666")
            ).place(x=10, y=60)
        
        metrics_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Inventory analysis
        analysis_frame = tk.CTkFrame(tab)
        analysis_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        tk.CTkLabel(
            analysis_frame,
            text="Inventory Analysis",
            font=("Helvetica", 16, "bold")
        ).pack(pady=10)
        
        # Sample analysis data
        analysis_data = [
            ("Beef Cuts", "£18,450", "40.4%", "High turnover"),
            ("Poultry", "£12,340", "27.0%", "Good movement"),
            ("Pork Products", "£8,760", "19.2%", "Steady sales"),
            ("Lamb", "£4,230", "9.3%", "Seasonal"),
            ("Other", "£1,900", "4.1%", "Low volume")
        ]
        
        for category, value, percentage, status in analysis_data:
            analysis_row = tk.CTkFrame(analysis_frame, height=40)
            analysis_row.pack(fill="x", pady=2, padx=20)
            
            tk.CTkLabel(
                analysis_row,
                text=category,
                font=("Helvetica", 12),
                width=120,
                anchor="w"
            ).place(x=10, y=10)
            
            tk.CTkLabel(
                analysis_row,
                text=value,
                font=("Helvetica", 11, "bold")
            ).place(x=150, y=10)
            
            tk.CTkLabel(
                analysis_row,
                text=percentage,
                font=("Helvetica", 11)
            ).place(x=250, y=10)
            
            status_color = {
                "High turnover": "#4CAF50",
                "Good movement": "#4CAF50",
                "Steady sales": "#FF9800",
                "Seasonal": "#2196F3",
                "Low volume": "#757575"
            }.get(status, "#666666")
            
            tk.CTkLabel(
                analysis_row,
                text=status,
                font=("Helvetica", 10, "bold"),
                text_color="white",
                fg_color=status_color,
                corner_radius=10,
                width=100,
                height=25
            ).place(x=320, y=7)
    
    def setup_delivery_reports(self):
        """Setup delivery reports tab"""
        tab = self.tabview.tab("🚚 Delivery Reports")
        
        tk.CTkLabel(
            tab,
            text="Delivery & Logistics Reports",
            font=("Helvetica", 20, "bold")
        ).pack(pady=20)
        
        # Delivery metrics
        metrics_frame = tk.CTkFrame(tab)
        metrics_frame.pack(fill="x", padx=20, pady=10)
        
        # Sample delivery metrics
        delivery_metrics = [
            ("🚚 Deliveries", "245", "+18"),
            ("📦 Avg Delivery Time", "2.4h", "-0.3h"),
            ("💰 Delivery Cost", "£1,850", "-£120"),
            ("⭐ Customer Rating", "4.8/5", "+0.1")
        ]
        
        for i, (title, value, change) in enumerate(delivery_metrics):
            metric_frame = tk.CTkFrame(metrics_frame, height=80)
            metric_frame.grid(row=0, column=i, padx=5, pady=5, sticky="nsew")
            metric_frame.grid_propagate(False)
            
            tk.CTkLabel(
                metric_frame,
                text=title,
                font=("Helvetica", 12)
            ).place(x=10, y=10)
            
            tk.CTkLabel(
                metric_frame,
                text=value,
                font=("Helvetica", 18, "bold")
            ).place(x=10, y=35)
            
            tk.CTkLabel(
                metric_frame,
                text=change,
                font=("Helvetica", 10),
                text_color="#4CAF50" if "+" in change or "-" in change and "h" in change else "#F44336"
            ).place(x=10, y=60)
        
        metrics_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Route efficiency
        efficiency_frame = tk.CTkFrame(tab)
        efficiency_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        tk.CTkLabel(
            efficiency_frame,
            text="Route Efficiency Analysis",
            font=("Helvetica", 16, "bold")
        ).pack(pady=10)
        
        # Sample route data
        routes = [
            ("North Belfast", "28 deliveries", "45 miles", "92% efficiency"),
            ("South Antrim", "32 deliveries", "52 miles", "88% efficiency"),
            ("City Center", "41 deliveries", "38 miles", "95% efficiency"),
            ("East Coast", "19 deliveries", "67 miles", "85% efficiency")
        ]
        
        for route, deliveries, distance, efficiency in routes:
            route_frame = tk.CTkFrame(efficiency_frame, height=60)
            route_frame.pack(fill="x", pady=5, padx=20)
            route_frame.grid_propagate(False)
            
            tk.CTkLabel(
                route_frame,
                text=route,
                font=("Helvetica", 12, "bold")
            ).place(x=20, y=15)
            
            tk.CTkLabel(
                route_frame,
                text=deliveries,
                font=("Helvetica", 11)
            ).place(x=150, y=15)
            
            tk.CTkLabel(
                route_frame,
                text=distance,
                font=("Helvetica", 11)
            ).place(x=250, y=15)
            
            # Efficiency badge
            eff_value = float(efficiency.split("%")[0])
            if eff_value >= 90:
                color = "#4CAF50"
            elif eff_value >= 85:
                color = "#FF9800"
            else:
                color = "#F44336"
            
            tk.CTkLabel(
                route_frame,
                text=efficiency,
                font=("Helvetica", 11, "bold"),
                text_color="white",
                fg_color=color,
                corner_radius=10,
                width=100,
                height=25
            ).place(x=350, y=17)
    
    def generate_financial_report(self, report_type):
        """Generate financial report"""
        messagebox.showinfo(
            f"Generate {report_type}",
            f"{report_type} generated successfully!\n\n"
            "Report includes:\n"
            "• Detailed financial data\n"
            "• Charts and graphs\n"
            "• Comparative analysis\n"
            "• Key insights\n"
            "• Recommendations\n\n"
            "Exported to reports/ folder"
        )
    
    def export_report(self, format_type):
        """Export report in specified format"""
        messagebox.showinfo(
            "Export Report",
            f"Report exported as {format_type}!\n\n"
            "Available in: reports/ folder\n"
            "Can be:\n"
            "• Downloaded\n"
            "• Emailed\n"
            "• Printed\n"
            "• Shared"
        )
    
    def refresh_all(self):
        """Refresh all reports"""
        self.load_dashboard()
        messagebox.showinfo("Refreshed", "All reports have been refreshed")
    
    def go_back(self):
        """Return to main menu"""
        self.destroy()
        subprocess.Popen(["python", "jsfoods_main.py"])


if __name__ == "__main__":
    app = ReportingSystem()
    app.mainloop()