import sqlite3
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import webbrowser
import csv
from tkcalendar import DateEntry  # Requires pip install tkcalendar
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class EnhancedERP:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced ERP System v2.0")
        self.root.geometry("1300x850")
        self.root.minsize(1100, 750)
        
        # Enhanced theme colors
        self.theme = {
            'primary': '#3498db',
            'secondary': '#2980b9',
            'accent': '#e74c3c',
            'light': '#f5f7fa',
            'dark': '#34495e',
            'success': '#2ecc71',
            'warning': '#f39c12',
            'danger': '#e74c3c',
            'text': '#2c3e50',
            'background': '#ecf0f1'
        }
        
        # Configure enhanced styles
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_styles()
        
        # Database connection with error handling
        try:
            self.conn = sqlite3.connect('erp_advanced.db', check_same_thread=False)
            self.conn.execute("PRAGMA foreign_keys = ON")
            self.create_tables()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Cannot connect to database:\n{str(e)}")
            self.root.destroy()
            return
        
        # Application state
        self.current_user = None
        self.user_permissions = {}
        
        # Create UI
        self.create_main_frame()
        self.create_menu()
        self.create_main_content()
        self.create_status_bar()
        
        # Show login dialog
        self.show_login()
        
        # Bind keyboard shortcuts
        self.root.bind('<Control-q>', lambda e: self.on_closing())
        self.root.bind('<F5>', lambda e: self.refresh_current_tab())
    
    def configure_styles(self):
        """Enhanced style configuration with modern look"""
        self.style.configure('.', 
                           background=self.theme['background'],
                           foreground=self.theme['text'])
        
        # Frame styles
        self.style.configure('TFrame', background=self.theme['background'])
        self.style.configure('Card.TFrame', background='white', borderwidth=1, relief='solid')
        
        # Label styles
        font_small = ('Segoe UI', 9)
        font_medium = ('Segoe UI', 10)
        font_large = ('Segoe UI', 12)
        
        self.style.configure('TLabel', font=font_medium, background=self.theme['background'])
        self.style.configure('Header.TLabel', font=('Segoe UI', 11, 'bold'), foreground=self.theme['primary'])
        self.style.configure('Title.TLabel', font=('Segoe UI', 14, 'bold'), foreground=self.theme['dark'])
        
        # Button styles
        self.style.configure('TButton', font=font_medium, padding=6)
        self.style.configure('Primary.TButton', 
                           background=self.theme['primary'],
                           foreground='white',
                           font=font_medium,
                           borderwidth=0)
        self.style.map('Primary.TButton',
                      background=[('active', self.theme['secondary']), 
                                ('pressed', self.theme['secondary'])])
        
        self.style.configure('Success.TButton', 
                           background=self.theme['success'],
                           foreground='white')
        
        self.style.configure('Danger.TButton', 
                           background=self.theme['danger'],
                           foreground='white')
        
        # Entry styles
        self.style.configure('TEntry', fieldbackground='white', padding=5)
        
        # Combobox styles
        self.style.configure('TCombobox', fieldbackground='white', padding=5)
        
        # Treeview styles
        self.style.configure('Treeview', 
                           font=font_small,
                           rowheight=28,
                           background='white',
                           fieldbackground='white',
                           bordercolor=self.theme['light'])
        self.style.configure('Treeview.Heading', 
                           font=('Segoe UI', 9, 'bold'),
                           background=self.theme['light'],
                           foreground=self.theme['dark'])
        self.style.map('Treeview', 
                      background=[('selected', self.theme['primary'])],
                      foreground=[('selected', 'white')])
    
    def create_tables(self):
        """Enhanced database schema with additional tables"""
        cursor = self.conn.cursor()
        
        # Create tables if they don't exist
        tables = [
            # Users table with enhanced fields
            '''CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                role TEXT NOT NULL,
                department TEXT,
                phone TEXT,
                last_login TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT
            )''',
            
            # Permissions table
            '''CREATE TABLE IF NOT EXISTS permissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                module TEXT NOT NULL,
                can_view INTEGER DEFAULT 0,
                can_create INTEGER DEFAULT 0,
                can_edit INTEGER DEFAULT 0,
                can_delete INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )''',
            
            # Customers table with enhanced fields
            '''CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                contact_person TEXT,
                address TEXT,
                city TEXT,
                state TEXT,
                country TEXT,
                postal_code TEXT,
                phone TEXT,
                email TEXT,
                tax_id TEXT,
                payment_terms INTEGER DEFAULT 30,
                credit_limit REAL DEFAULT 0,
                currency TEXT DEFAULT 'USD',
                status TEXT CHECK(status IN ('Active', 'Inactive', 'On Hold')) DEFAULT 'Active',
                notes TEXT,
                created_by INTEGER,
                created_at TEXT NOT NULL,
                updated_at TEXT,
                FOREIGN KEY (created_by) REFERENCES users (id)
            )''',
            
            # Products table with enhanced fields
            '''CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sku TEXT UNIQUE NOT NULL,
                barcode TEXT,
                name TEXT NOT NULL,
                description TEXT,
                category TEXT,
                subcategory TEXT,
                unit TEXT DEFAULT 'pcs',
                purchase_price REAL DEFAULT 0,
                sale_price REAL DEFAULT 0,
                tax_rate REAL DEFAULT 0,
                min_stock_level REAL DEFAULT 0,
                reorder_quantity REAL DEFAULT 0,
                current_stock REAL DEFAULT 0,
                weight REAL,
                dimensions TEXT,
                supplier_id INTEGER,
                status TEXT CHECK(status IN ('Active', 'Discontinued', 'Out of Stock')) DEFAULT 'Active',
                image_path TEXT,
                notes TEXT,
                created_by INTEGER,
                created_at TEXT NOT NULL,
                updated_at TEXT,
                FOREIGN KEY (supplier_id) REFERENCES suppliers (id),
                FOREIGN KEY (created_by) REFERENCES users (id)
            )''',
            
            # Inventory movements with enhanced tracking
            '''CREATE TABLE IF NOT EXISTS inventory_movements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                movement_type TEXT CHECK(movement_type IN ('Purchase', 'Sale', 'Adjustment', 'Transfer', 'Return')),
                quantity REAL NOT NULL,
                reference_id INTEGER,
                reference_type TEXT,
                movement_date TEXT NOT NULL,
                location_from TEXT,
                location_to TEXT,
                user_id INTEGER,
                notes TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (product_id) REFERENCES products (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )''',
            
            # Audit log table
            '''CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT NOT NULL,
                table_name TEXT NOT NULL,
                record_id INTEGER,
                old_values TEXT,
                new_values TEXT,
                ip_address TEXT,
                user_agent TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )'''
        ]
        
        for table in tables:
            cursor.execute(table)
        
        # Create initial admin user if not exists
        cursor.execute("SELECT COUNT(*) FROM users WHERE username='admin'")
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
                INSERT INTO users (username, password, name, email, role, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', ('admin', self.hash_password('admin123'), 'Administrator', 'admin@erp.com', 'Admin', 
                 datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            
            # Set admin permissions
            cursor.execute('''
                INSERT INTO permissions (user_id, module, can_view, can_create, can_edit, can_delete)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (1, 'all', 1, 1, 1, 1))
        
        self.conn.commit()
    
    def hash_password(self, password):
        """Simple password hashing (in production use proper hashing like bcrypt)"""
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_main_frame(self):
        """Create the main application frame"""
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
    
    def create_menu(self):
        """Create enhanced application menu with icons"""
        menu_frame = ttk.Frame(self.main_frame, style='TFrame')
        menu_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # Application logo/name
        logo_frame = ttk.Frame(menu_frame, style='TFrame')
        logo_frame.pack(fill=tk.X, pady=(10, 20))
        
        ttk.Label(logo_frame, text="ADVANCED ERP", style='Title.TLabel', 
                 foreground=self.theme['primary']).pack(pady=10)
        
        # User info
        self.user_frame = ttk.Frame(menu_frame, style='Card.TFrame')
        self.user_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.user_label = ttk.Label(self.user_frame, text="Not logged in", style='Header.TLabel')
        self.user_label.pack(pady=5)
        
        # Menu buttons with icons (using text as icons for simplicity)
        menu_buttons = [
            ("📊 Dashboard", self.show_dashboard),
            ("👥 Customers", self.show_customers),
            ("🏭 Suppliers", self.show_suppliers),
            ("📦 Products", self.show_products),
            ("💰 Sales", self.show_sales),
            ("🛒 Purchases", self.show_purchases),
            ("📋 Inventory", self.show_inventory),
            ("🧾 Invoices", self.show_invoices),
            ("📊 Reports", self.show_reports),
            ("⚙ Settings", self.show_settings)
        ]
        
        for text, command in menu_buttons:
            btn = ttk.Button(menu_frame, text=text, command=command, style='Primary.TButton')
            btn.pack(fill=tk.X, padx=5, pady=2)
        
        # System buttons
        ttk.Button(menu_frame, text="🔄 Refresh", command=self.refresh_current_tab, 
                  style='TButton').pack(fill=tk.X, padx=5, pady=(20, 5))
        ttk.Button(menu_frame, text="🚪 Logout", command=self.logout, 
                  style='Danger.TButton').pack(fill=tk.X, padx=5, pady=5)
    
    def create_status_bar(self):
        """Create enhanced status bar"""
        status_frame = ttk.Frame(self.root, relief='sunken')
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        
        self.user_status_var = tk.StringVar()
        self.user_status_var.set("Not logged in")
        
        ttk.Label(status_frame, textvariable=self.user_status_var, 
                 anchor=tk.W, width=20).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(status_frame, textvariable=self.status_var, 
                 anchor=tk.W).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        ttk.Label(status_frame, text="Press F5 to refresh", 
                 anchor=tk.E).pack(side=tk.RIGHT, padx=5)
    
    def create_main_content(self):
        """Create the main content area with enhanced tabs"""
        self.content_frame = ttk.Frame(self.main_frame, style='TFrame')
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create a notebook for tabs with modern style
        self.notebook = ttk.Notebook(self.content_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create all tabs
        self.create_dashboard_tab()
        self.create_customers_tab()
        self.create_suppliers_tab()
        self.create_products_tab()
        self.create_sales_tab()
        self.create_purchases_tab()
        self.create_inventory_tab()
        self.create_invoices_tab()
        self.create_reports_tab()
        self.create_settings_tab()
        
        # Hide all tabs initially
        for tab in self.notebook.tabs():
            self.notebook.hide(tab)
    
    def create_dashboard_tab(self):
        """Enhanced dashboard with charts and KPIs"""
        self.dashboard_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.dashboard_tab, text="Dashboard")
        
        # Header with date range selector
        header_frame = ttk.Frame(self.dashboard_tab, style='TFrame')
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(header_frame, text="Dashboard Overview", style='Title.TLabel').pack(side=tk.LEFT)
        
        # Date range selector
        date_frame = ttk.Frame(header_frame, style='TFrame')
        date_frame.pack(side=tk.RIGHT)
        
        ttk.Label(date_frame, text="From:").pack(side=tk.LEFT)
        self.dash_start_date = DateEntry(date_frame, width=12, background='darkblue',
                                        foreground='white', borderwidth=2, date_pattern='y-mm-dd')
        self.dash_start_date.pack(side=tk.LEFT, padx=5)
        self.dash_start_date.set_date(datetime.now() - timedelta(days=30))
        
        ttk.Label(date_frame, text="To:").pack(side=tk.LEFT)
        self.dash_end_date = DateEntry(date_frame, width=12, background='darkblue',
                                      foreground='white', borderwidth=2, date_pattern='y-mm-dd')
        self.dash_end_date.pack(side=tk.LEFT, padx=5)
        self.dash_end_date.set_date(datetime.now()))
        
        ttk.Button(date_frame, text="Apply", command=self.load_dashboard_data,
                  style='Primary.TButton').pack(side=tk.LEFT, padx=5)
        
        # Dashboard widgets container
        container = ttk.Frame(self.dashboard_tab, style='TFrame')
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Top row - Summary cards with improved layout
        summary_frame = ttk.Frame(container, style='TFrame')
        summary_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Summary cards configuration
        summary_items = [
            ("Total Sales", "sales", "#3498db", "💰"),
            ("New Customers", "customers", "#2ecc71", "👥"),
            ("Inventory Value", "inventory_value", "#e74c3c", "📦"),
            ("Pending Orders", "orders", "#f39c12", "📋"),
            ("Revenue Growth", "growth", "#9b59b6", "📈"),
            ("Avg. Order Value", "aov", "#1abc9c", "💲")
        ]
        
        for i, (title, key, color, icon) in enumerate(summary_items):
            card = ttk.Frame(summary_frame, style='Card.TFrame', padding=10)
            card.grid(row=0, column=i, padx=5, sticky="nsew")
            summary_frame.columnconfigure(i, weight=1)
            
            # Card header
            header = ttk.Frame(card, style='TFrame')
            header.pack(fill=tk.X)
            
            ttk.Label(header, text=icon, font=('Segoe UI', 14)).pack(side=tk.LEFT)
            ttk.Label(header, text=title, style='Header.TLabel', foreground=color).pack(side=tk.LEFT, padx=5)
            
            # Card value
            value_label = ttk.Label(card, text="0", font=('Segoe UI', 18, 'bold'))
            value_label.pack(pady=(5, 0))
            
            # Card footer (for change indicators)
            footer = ttk.Frame(card, style='TFrame')
            footer.pack(fill=tk.X)
            
            change_label = ttk.Label(footer, text="", font=('Segoe UI', 8))
            change_label.pack(side=tk.RIGHT)
            
            # Store references
            setattr(self, f"dashboard_{key}_value", value_label)
            setattr(self, f"dashboard_{key}_change", change_label)
        
        # Middle row - Charts and recent activities
        middle_frame = ttk.Frame(container, style='TFrame')
        middle_frame.pack(fill=tk.BOTH, expand=True)
        
        # Sales chart frame
        chart_frame = ttk.LabelFrame(middle_frame, text="Sales Performance", style='TFrame')
        chart_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Create matplotlib figure
        self.sales_fig = plt.Figure(figsize=(6, 4), dpi=80)
        self.sales_ax = self.sales_fig.add_subplot(111)
        self.sales_canvas = FigureCanvasTkAgg(self.sales_fig, master=chart_frame)
        self.sales_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Recent activities frame
        activity_frame = ttk.LabelFrame(middle_frame, text="Recent Activities", style='TFrame')
        activity_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, width=350)
        
        self.activity_tree = ttk.Treeview(activity_frame, columns=("time", "activity"), show="headings", height=10)
        self.activity_tree.heading("time", text="Time")
        self.activity_tree.heading("activity", text="Activity")
        self.activity_tree.column("time", width=80)
        self.activity_tree.column("activity", width=240)
        
        scrollbar = ttk.Scrollbar(activity_frame, orient=tk.VERTICAL, command=self.activity_tree.yview)
        self.activity_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.activity_tree.pack(fill=tk.BOTH, expand=True)
        
        # Bottom row - Recent orders and stock alerts
        bottom_frame = ttk.Frame(container, style='TFrame')
        bottom_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Recent orders
        orders_frame = ttk.LabelFrame(bottom_frame, text="Recent Orders", style='TFrame')
        orders_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.orders_tree = ttk.Treeview(orders_frame, 
                                      columns=("id", "date", "customer", "amount", "status"), 
                                      show="headings")
        self.orders_tree.heading("id", text="Order #")
        self.orders_tree.heading("date", text="Date")
        self.orders_tree.heading("customer", text="Customer")
        self.orders_tree.heading("amount", text="Amount")
        self.orders_tree.heading("status", text="Status")
        self.orders_tree.column("id", width=80)
        self.orders_tree.column("date", width=100)
        self.orders_tree.column("customer", width=150)
        self.orders_tree.column("amount", width=100, anchor=tk.E)
        self.orders_tree.column("status", width=100)
        
        scrollbar = ttk.Scrollbar(orders_frame, orient=tk.VERTICAL, command=self.orders_tree.yview)
        self.orders_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.orders_tree.pack(fill=tk.BOTH, expand=True)
        
        # Stock alerts
        stock_frame = ttk.LabelFrame(bottom_frame, text="Stock Alerts", style='TFrame')
        stock_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, width=350)
        
        self.stock_tree = ttk.Treeview(stock_frame, 
                                      columns=("product", "stock", "min_level"), 
                                      show="headings")
        self.stock_tree.heading("product", text="Product")
        self.stock_tree.heading("stock", text="Current Stock")
        self.stock_tree.heading("min_level", text="Min Level")
        self.stock_tree.column("product", width=180)
        self.stock_tree.column("stock", width=80, anchor=tk.E)
        self.stock_tree.column("min_level", width=80, anchor=tk.E)
        
        scrollbar = ttk.Scrollbar(stock_frame, orient=tk.VERTICAL, command=self.stock_tree.yview)
        self.stock_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.stock_tree.pack(fill=tk.BOTH, expand=True)
        
        # Double click to view order
        self.orders_tree.bind("<Double-1>", self.view_order_from_dashboard)
    
    def load_dashboard_data(self):
        """Enhanced dashboard data loading with date range"""
        start_date = self.dash_start_date.get_date()
        end_date = self.dash_end_date.get_date()
        
        cursor = self.conn.cursor()
        try:
            # Load summary data
            # Total Sales
            cursor.execute('''
                SELECT COALESCE(SUM(total_amount), 0) 
                FROM sales_orders 
                WHERE order_date BETWEEN ? AND ?
            ''', (start_date, end_date))
            sales_total = cursor.fetchone()[0]
            self.dashboard_sales_value.config(text=f"${sales_total:,.2f}")
            
            # New Customers
            cursor.execute('''
                SELECT COUNT(*) 
                FROM customers 
                WHERE created_at BETWEEN ? AND ?
            ''', (start_date, end_date))
            self.dashboard_customers_value.config(text=cursor.fetchone()[0])
            
            # Inventory Value
            cursor.execute('''
                SELECT COALESCE(SUM(current_stock * purchase_price), 0)
                FROM products
            ''')
            inventory_value = cursor.fetchone()[0]
            self.dashboard_inventory_value_value.config(text=f"${inventory_value:,.2f}")
            
            # Pending Orders
            cursor.execute('''
                SELECT COUNT(*) 
                FROM sales_orders 
                WHERE status IN ('Draft', 'Confirmed') 
                AND order_date BETWEEN ? AND ?
            ''', (start_date, end_date))
            self.dashboard_orders_value.config(text=cursor.fetchone()[0])
            
            # Revenue Growth (compared to previous period)
            prev_start = start_date - timedelta(days=(end_date - start_date).days)
            cursor.execute('''
                SELECT COALESCE(SUM(total_amount), 0) 
                FROM sales_orders 
                WHERE order_date BETWEEN ? AND ?
            ''', (prev_start, start_date - timedelta(days=1)))
            prev_sales = cursor.fetchone()[0]
            
            growth = ((sales_total - prev_sales) / prev_sales * 100) if prev_sales > 0 else 0
            self.dashboard_growth_value.config(text=f"{growth:.1f}%")
            self.dashboard_growth_change.config(
                text=f"vs previous period",
                foreground='green' if growth >= 0 else 'red'
            )
            
            # Average Order Value
            cursor.execute('''
                SELECT COALESCE(AVG(total_amount), 0) 
                FROM sales_orders 
                WHERE order_date BETWEEN ? AND ?
            ''', (start_date, end_date))
            aov = cursor.fetchone()[0]
            self.dashboard_aov_value.config(text=f"${aov:,.2f}")
            
            # Load sales chart data
            cursor.execute('''
                SELECT date(order_date) as day, SUM(total_amount) as daily_sales
                FROM sales_orders
                WHERE order_date BETWEEN ? AND ?
                GROUP BY day
                ORDER BY day
            ''', (start_date, end_date))
            
            chart_data = cursor.fetchall()
            days = [row[0] for row in chart_data]
            sales = [row[1] for row in chart_data]
            
            # Update chart
            self.sales_ax.clear()
            if len(days) > 0:
                self.sales_ax.plot(days, sales, marker='o', color=self.theme['primary'])
                self.sales_ax.set_title('Daily Sales', fontsize=10)
                self.sales_ax.set_ylabel('Amount ($)', fontsize=8)
                self.sales_ax.grid(True, linestyle='--', alpha=0.6)
                self.sales_ax.tick_params(axis='x', rotation=45, labelsize=8)
                self.sales_ax.tick_params(axis='y', labelsize=8)
                self.sales_fig.tight_layout()
                self.sales_canvas.draw()
            
            # Load recent activities
            for item in self.activity_tree.get_children():
                self.activity_tree.delete(item)
            
            cursor.execute('''
                SELECT strftime('%H:%M', created_at), action || ' ' || table_name || ' #' || record_id
                FROM audit_log
                ORDER BY created_at DESC
                LIMIT 10
            ''')
            
            for activity in cursor.fetchall():
                self.activity_tree.insert("", tk.END, values=activity)
            
            # Load recent orders
            for item in self.orders_tree.get_children():
                self.orders_tree.delete(item)
            
            cursor.execute('''
                SELECT so.id, so.order_date, c.name, so.total_amount, so.status
                FROM sales_orders so
                JOIN customers c ON so.customer_id = c.id
                ORDER BY so.order_date DESC
                LIMIT 10
            ''')
            
            for order in cursor.fetchall():
                self.orders_tree.insert("", tk.END, values=(
                    order[0],
                    order[1],
                    order[2],
                    f"${order[3]:,.2f}",
                    order[4]
                ))
            
            # Load stock alerts
            for item in self.stock_tree.get_children():
                self.stock_tree.delete(item)
            
            cursor.execute('''
                SELECT name, current_stock, min_stock_level
                FROM products
                WHERE current_stock <= min_stock_level AND status = 'Active'
                ORDER BY (min_stock_level - current_stock) DESC
                LIMIT 10
            ''')
            
            for product in cursor.fetchall():
                self.stock_tree.insert("", tk.END, values=(
                    product[0],
                    product[1],
                    product[2]
                ))
            
            self.status_var.set(f"Dashboard data loaded from {start_date} to {end_date}")
        except Exception as e:
            self.status_var.set(f"Error loading dashboard data: {str(e)}")
            messagebox.showerror("Error", f"Failed to load dashboard data:\n{str(e)}")
    
    def view_order_from_dashboard(self, event):
        """View order details from dashboard"""
        selected_item = self.orders_tree.focus()
        if not selected_item:
            return
        
        order_id = self.orders_tree.item(selected_item)["values"][0]
        self.show_sales_order_details(order_id)
    
    def show_sales_order_details(self, order_id):
        """Show sales order details in a new window"""
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Sales Order #{order_id}")
        dialog.geometry("900x700")
        
        # Fetch order details
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT so.*, c.name as customer_name
            FROM sales_orders so
            JOIN customers c ON so.customer_id = c.id
            WHERE so.id = ?
        ''', (order_id,))
        order = cursor.fetchone()
        
        if not order:
            messagebox.showerror("Error", "Order not found")
            dialog.destroy()
            return
        
        # Order header
        header_frame = ttk.Frame(dialog, style='TFrame')
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(header_frame, text=f"Sales Order #{order[1]}", style='Title.TLabel').pack(side=tk.LEFT)
        
        status_label = ttk.Label(header_frame, text=order[5], 
                               foreground='green' if order[5] == 'Completed' else 'orange',
                               font=('Segoe UI', 10, 'bold'))
        status_label.pack(side=tk.RIGHT, padx=10)
        
        # Customer info
        info_frame = ttk.LabelFrame(dialog, text="Customer Information", style='TFrame')
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(info_frame, text=f"Customer: {order[17]}", style='Header.TLabel').pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Order Date: {order[3]}").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Expected Shipment: {order[4] or 'Not specified'}").pack(anchor=tk.W)
        
        # Order items
        items_frame = ttk.LabelFrame(dialog, text="Order Items", style='TFrame')
        items_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        columns = ("product", "quantity", "price", "discount", "tax", "total")
        self.order_items_tree = ttk.Treeview(items_frame, columns=columns, show="headings")
        
        for col in columns:
            self.order_items_tree.heading(col, text=col.capitalize())
            self.order_items_tree.column(col, width=100, anchor=tk.E if col != 'product' else tk.W)
        
        self.order_items_tree.column("product", width=200)
        
        scrollbar = ttk.Scrollbar(items_frame, orient=tk.VERTICAL, command=self.order_items_tree.yview)
        self.order_items_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.order_items_tree.pack(fill=tk.BOTH, expand=True)
        
        # Load order items
        cursor.execute('''
            SELECT p.name, soi.quantity, soi.unit_price, soi.discount_percent, soi.tax_percent, soi.line_total
            FROM sales_order_items soi
            JOIN products p ON soi.product_id = p.id
            WHERE soi.order_id = ?
        ''', (order_id,))
        
        for item in cursor.fetchall():
            self.order_items_tree.insert("", tk.END, values=(
                item[0],
                item[1],
                f"${item[2]:,.2f}",
                f"{item[3]}%" if item[3] else "-",
                f"{item[4]}%" if item[4] else "-",
                f"${item[5]:,.2f}"
            ))
        
        # Order summary
        summary_frame = ttk.Frame(dialog, style='TFrame')
        summary_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(summary_frame, text=f"Subtotal: ${order[9]:,.2f}", style='Header.TLabel').pack(side=tk.LEFT)
        ttk.Label(summary_frame, text=f"Tax: ${order[10]:,.2f}").pack(side=tk.LEFT, padx=20)
        ttk.Label(summary_frame, text=f"Discount: ${order[11]:,.2f}").pack(side=tk.LEFT, padx=20)
        
        total_frame = ttk.Frame(dialog, style='TFrame')
        total_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(total_frame, text=f"Total Amount: ${order[12]:,.2f}", 
                 font=('Segoe UI', 12, 'bold')).pack(side=tk.LEFT)
        
        # Notes
        if order[13]:
            notes_frame = ttk.LabelFrame(dialog, text="Notes", style='TFrame')
            notes_frame.pack(fill=tk.X, padx=10, pady=5)
            
            notes_text = tk.Text(notes_frame, height=4, wrap=tk.WORD)
            notes_text.insert(tk.END, order[13])
            notes_text.config(state=tk.DISABLED)
            notes_text.pack(fill=tk.BOTH, expand=True)
        
        # Action buttons
        btn_frame = ttk.Frame(dialog, style='TFrame')
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        if order[5] in ('Draft', 'Confirmed'):
            ttk.Button(btn_frame, text="Mark as Shipped", command=lambda: self.update_order_status(order_id, 'Shipped'),
                      style='Success.TButton').pack(side=tk.LEFT, padx=5)
        
        if order[5] == 'Shipped':
            ttk.Button(btn_frame, text="Mark as Completed", command=lambda: self.update_order_status(order_id, 'Completed'),
                      style='Success.TButton').pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="Print", command=lambda: self.print_order(order_id),
                  style='Primary.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Close", command=dialog.destroy,
                  style='TButton').pack(side=tk.RIGHT, padx=5)
    
    def update_order_status(self, order_id, new_status):
        """Update order status in database"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                UPDATE sales_orders
                SET status = ?, updated_at = ?
                WHERE id = ?
            ''', (new_status, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), order_id))
            
            # Log the activity
            cursor.execute('''
                INSERT INTO audit_log (user_id, action, table_name, record_id, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (self.current_user[0], 'update', 'sales_orders', order_id, 
                 datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            
            self.conn.commit()
            
            # Refresh dashboard and sales tab
            self.load_dashboard_data()
            if hasattr(self, 'sales_tree'):
                self.load_sales_orders()
            
            messagebox.showinfo("Success", f"Order status updated to {new_status}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update order status:\n{str(e)}")
    
    def print_order(self, order_id):
        """Export order to PDF (simulated)"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            initialfile=f"order_{order_id}.pdf"
        )
        
        if file_path:
            try:
                # In a real application, you would generate an actual PDF here
                # For this example, we'll just create a CSV file
                csv_path = file_path.replace('.pdf', '.csv')
                
                cursor = self.conn.cursor()
                cursor.execute('''
                    SELECT so.order_number, so.order_date, c.name as customer, 
                           p.name as product, soi.quantity, soi.unit_price, soi.line_total
                    FROM sales_orders so
                    JOIN customers c ON so.customer_id = c.id
                    JOIN sales_order_items soi ON soi.order_id = so.id
                    JOIN products p ON soi.product_id = p.id
                    WHERE so.id = ?
                ''', (order_id,))
                
                with open(csv_path, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['Order Number', 'Order Date', 'Customer', 
                                   'Product', 'Quantity', 'Unit Price', 'Total'])
                    writer.writerows(cursor.fetchall())
                
                self.status_var.set(f"Order exported to {csv_path}")
                messagebox.showinfo("Success", f"Order exported to:\n{csv_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export order:\n{str(e)}")
    
    def create_customers_tab(self):
        """Enhanced customers tab with more features"""
        self.customers_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.customers_tab, text="Customers")
        
        # Header with actions
        header_frame = ttk.Frame(self.customers_tab, style='TFrame')
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(header_frame, text="Customer Management", style='Title.TLabel').pack(side=tk.LEFT)
        
        # Action buttons
        btn_frame = ttk.Frame(header_frame, style='TFrame')
        btn_frame.pack(side=tk.RIGHT)
        
        ttk.Button(btn_frame, text="Add Customer", command=self.add_customer, 
                  style='Primary.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Export", command=self.export_customers, 
                  style='TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Refresh", command=self.load_customers, 
                  style='TButton').pack(side=tk.LEFT, padx=5)
        
        # Search and filter frame
        filter_frame = ttk.Frame(self.customers_tab, style='TFrame')
        filter_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Search field
        ttk.Label(filter_frame, text="Search:").pack(side=tk.LEFT)
        self.customer_search_entry = ttk.Entry(filter_frame, width=30)
        self.customer_search_entry.pack(side=tk.LEFT, padx=5)
        self.customer_search_entry.bind("<Return>", lambda e: self.load_customers())
        
        # Status filter
        ttk.Label(filter_frame, text="Status:").pack(side=tk.LEFT, padx=(10, 0))
        self.customer_status_filter = ttk.Combobox(filter_frame, 
                                                  values=["All", "Active", "Inactive", "On Hold"],
                                                  state="readonly", width=12)
        self.customer_status_filter.set("All")
        self.customer_status_filter.pack(side=tk.LEFT, padx=5)
        
        # Action buttons
        ttk.Button(filter_frame, text="Search", command=self.load_customers, 
                  style='Primary.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(filter_frame, text="Clear", command=self.clear_customer_filters, 
                  style='TButton').pack(side=tk.LEFT, padx=5)
        
        # Customers list with improved layout
        list_frame = ttk.Frame(self.customers_tab, style='TFrame')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Treeview with horizontal scrollbar
        tree_container = ttk.Frame(list_frame, style='TFrame')
        tree_container.pack(fill=tk.BOTH, expand=True)
        
        self.customers_tree = ttk.Treeview(tree_container, 
                                         columns=("id", "code", "name", "contact", "phone", 
                                                 "email", "status", "credit_limit", "last_order"),
                                         show="headings")
        
        # Configure columns
        columns = [
            ("id", "ID", 50, tk.CENTER),
            ("code", "Code", 80, tk.W),
            ("name", "Name", 150, tk.W),
            ("contact", "Contact", 120, tk.W),
            ("phone", "Phone", 100, tk.W),
            ("email", "Email", 150, tk.W),
            ("status", "Status", 80, tk.CENTER),
            ("credit_limit", "Credit Limit", 100, tk.E),
            ("last_order", "Last Order", 100, tk.CENTER)
        ]
        
        for col_id, heading, width, anchor in columns:
            self.customers_tree.heading(col_id, text=heading)
            self.customers_tree.column(col_id, width=width, anchor=anchor)
        
        # Add scrollbars
        y_scroll = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.customers_tree.yview)
        x_scroll = ttk.Scrollbar(tree_container, orient=tk.HORIZONTAL, command=self.customers_tree.xview)
        self.customers_tree.configure(yscroll=y_scroll.set, xscroll=x_scroll.set)
        
        # Grid layout for treeview and scrollbars
        self.customers_tree.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)
        
        # Context menu
        self.customer_context_menu = tk.Menu(self.root, tearoff=0)
        self.customer_context_menu.add_command(label="View Details", command=self.view_customer_details)
        self.customer_context_menu.add_command(label="Edit", command=self.edit_customer)
        self.customer_context_menu.add_command(label="Delete", command=self.delete_customer)
        self.customer_context_menu.add_separator()
        self.customer_context_menu.add_command(label="Create Order", command=self.create_order_for_customer)
        self.customers_tree.bind("<Button-3>", self.show_customer_context_menu)
        
        # Double click to view details
        self.customers_tree.bind("<Double-1>", lambda e: self.view_customer_details())
        
        # Load initial data
        self.load_customers()
    
    def load_customers(self):
        """Enhanced customer loading with filters"""
        search_term = self.customer_search_entry.get()
        status_filter = self.customer_status_filter.get()
        
        cursor = self.conn.cursor()
        try:
            query = '''
                SELECT c.id, c.code, c.name, c.contact_person, c.phone, c.email, 
                       c.status, c.credit_limit, MAX(so.order_date) as last_order
                FROM customers c
                LEFT JOIN sales_orders so ON c.id = so.customer_id
            '''
            where_clauses = []
            params = []
            
            if search_term:
                where_clauses.append("(c.name LIKE ? OR c.code LIKE ? OR c.contact_person LIKE ? OR c.email LIKE ?)")
                search_param = f"%{search_term}%"
                params.extend([search_param, search_param, search_param, search_param])
            
            if status_filter != "All":
                where_clauses.append("c.status = ?")
                params.append(status_filter)
            
            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)
            
            query += " GROUP BY c.id ORDER BY c.name"
            
            cursor.execute(query, params)
            
            # Clear existing data
            for item in self.customers_tree.get_children():
                self.customers_tree.delete(item)
            
            # Add new data with formatting
            for customer in cursor.fetchall():
                self.customers_tree.insert("", tk.END, values=(
                    customer[0],
                    customer[1],
                    customer[2],
                    customer[3] or "-",
                    customer[4] or "-",
                    customer[5] or "-",
                    customer[6],
                    f"${customer[7]:,.2f}" if customer[7] else "-",
                    customer[8] if customer[8] else "Never"
                ))
            
            self.status_var.set(f"Loaded {len(self.customers_tree.get_children())} customers")
        except Exception as e:
            self.status_var.set(f"Error loading customers: {str(e)}")
            messagebox.showerror("Error", f"Failed to load customers:\n{str(e)}")
    
    def clear_customer_filters(self):
        """Clear all customer filters"""
        self.customer_search_entry.delete(0, tk.END)
        self.customer_status_filter.set("All")
        self.load_customers()
    
    def show_customer_context_menu(self, event):
        """Show context menu for customer"""
        item = self.customers_tree.identify_row(event.y)
        if item:
            self.customers_tree.selection_set(item)
            self.customer_context_menu.post(event.x_root, event.y_root)
    
    def view_customer_details(self):
        """Enhanced customer details view"""
        selected_item = self.customers_tree.focus()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a customer first")
            return
        
        customer_id = self.customers_tree.item(selected_item)["values"][0]
        
        # Create details window
        details_window = tk.Toplevel(self.root)
        details_window.title("Customer Details")
        details_window.geometry("900x700")
        
        # Fetch customer details
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM customers WHERE id=?", (customer_id,))
        customer = cursor.fetchone()
        
        if not customer:
            messagebox.showerror("Error", "Customer not found")
            details_window.destroy()
            return
        
        # Create notebook for tabs
        notebook = ttk.Notebook(details_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Info tab
        info_tab = ttk.Frame(notebook)
        notebook.add(info_tab, text="Information")
        
        # Create form to display customer info
        fields = [
            ("Code:", customer[1]),
            ("Name:", customer[2]),
            ("Contact Person:", customer[3]),
            ("Address:", customer[4]),
            ("City:", customer[5]),
            ("State/Region:", customer[6]),
            ("Country:", customer[7]),
            ("Postal Code:", customer[8]),
            ("Phone:", customer[9]),
            ("Email:", customer[10]),
            ("Tax ID:", customer[11]),
            ("Payment Terms:", f"{customer[12]} days" if customer[12] else "N/A"),
            ("Credit Limit:", f"${customer[13]:,.2f}" if customer[13] else "N/A"),
            ("Currency:", customer[14]),
            ("Status:", customer[15]),
            ("Notes:", customer[16]),
            ("Created At:", customer[18]),
            ("Updated At:", customer[19] if customer[19] else "N/A")
        ]
        
        for i, (label, value) in enumerate(fields):
            row_frame = ttk.Frame(info_tab, style='TFrame')
            row_frame.pack(fill=tk.X, pady=2)
            
            ttk.Label(row_frame, text=label, style='Header.TLabel', width=15, anchor=tk.W).pack(side=tk.LEFT)
            
            if label == "Notes:" and value:
                notes_text = tk.Text(row_frame, height=4, wrap=tk.WORD, font=('Segoe UI', 9))
                notes_text.insert(tk.END, value)
                notes_text.config(state=tk.DISABLED)
                notes_text.pack(side=tk.LEFT, fill=tk.X, expand=True)
            else:
                ttk.Label(row_frame, text=value or "N/A").pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Orders tab
        orders_tab = ttk.Frame(notebook)
        notebook.add(orders_tab, text="Orders")
        
        # Create treeview for orders with more columns
        orders_tree = ttk.Treeview(orders_tab, 
                                 columns=("id", "date", "amount", "status", "payment", "items"), 
                                 show="headings")
        
        orders_tree.heading("id", text="Order #")
        orders_tree.heading("date", text="Date")
        orders_tree.heading("amount", text="Amount")
        orders_tree.heading("status", text="Status")
        orders_tree.heading("payment", text="Payment")
        orders_tree.heading("items", text="Items")
        
        orders_tree.column("id", width=80)
        orders_tree.column("date", width=100)
        orders_tree.column("amount", width=100, anchor=tk.E)
        orders_tree.column("status", width=100)
        orders_tree.column("payment", width=100)
        orders_tree.column("items", width=80, anchor=tk.CENTER)
        
        scrollbar = ttk.Scrollbar(orders_tab, orient=tk.VERTICAL, command=orders_tree.yview)
        orders_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        orders_tree.pack(fill=tk.BOTH, expand=True)
        
        # Load orders with item counts
        cursor.execute('''
            SELECT so.id, so.order_date, so.total_amount, so.status, so.payment_status, 
                   COUNT(soi.id) as item_count
            FROM sales_orders so
            LEFT JOIN sales_order_items soi ON so.id = soi.order_id
            WHERE so.customer_id=?
            GROUP BY so.id
            ORDER BY so.order_date DESC
        ''', (customer_id,))
        
        for order in cursor.fetchall():
            orders_tree.insert("", tk.END, values=(
                order[0],
                order[1],
                f"${order[2]:,.2f}",
                order[3],
                order[4],
                order[5]
            ))
        
        # Double click to view order
        orders_tree.bind("<Double-1>", lambda e: self.view_order_from_tree(orders_tree))
        
        # Financial tab
        financial_tab = ttk.Frame(notebook)
        notebook.add(financial_tab, text="Financial")
        
        # Financial summary
        ttk.Label(financial_tab, text="Financial Summary", style='Header.TLabel').pack(anchor=tk.W, pady=5)
        
        # Get financial data
        cursor.execute('''
            SELECT 
                COUNT(*) as total_orders,
                COALESCE(SUM(total_amount), 0) as total_sales,
                COALESCE(SUM(CASE WHEN status = 'Completed' THEN total_amount ELSE 0 END), 0) as completed_sales,
                COALESCE(SUM(CASE WHEN payment_status = 'Paid' THEN total_amount ELSE 0 END), 0) as paid_amount,
                COALESCE(SUM(CASE WHEN payment_status != 'Paid' THEN total_amount ELSE 0 END), 0) as outstanding_amount
            FROM sales_orders
            WHERE customer_id=?
        ''', (customer_id,))
        
        financial_data = cursor.fetchone()
        
        # Display financial metrics
        metrics = [
            ("Total Orders:", financial_data[0]),
            ("Total Sales:", f"${financial_data[1]:,.2f}"),
            ("Completed Sales:", f"${financial_data[2]:,.2f}"),
            ("Amount Paid:", f"${financial_data[3]:,.2f}"),
            ("Outstanding:", f"${financial_data[4]:,.2f}")
        ]
        
        for i, (label, value) in enumerate(metrics):
            row_frame = ttk.Frame(financial_tab, style='TFrame')
            row_frame.pack(fill=tk.X, pady=2)
            
            ttk.Label(row_frame, text=label, style='Header.TLabel', width=15, anchor=tk.W).pack(side=tk.LEFT)
            ttk.Label(row_frame, text=value).pack(side=tk.LEFT)
        
        # Payment history
        ttk.Label(financial_tab, text="Payment History", style='Header.TLabel').pack(anchor=tk.W, pady=(10, 5))
        
        payment_tree = ttk.Treeview(financial_tab, 
                                   columns=("date", "invoice", "amount", "method", "reference"), 
                                   show="headings")
        
        payment_tree.heading("date", text="Date")
        payment_tree.heading("invoice", text="Invoice #")
        payment_tree.heading("amount", text="Amount")
        payment_tree.heading("method", text="Method")
        payment_tree.heading("reference", text="Reference")
        
        payment_tree.column("date", width=100)
        payment_tree.column("invoice", width=100)
        payment_tree.column("amount", width=100, anchor=tk.E)
        payment_tree.column("method", width=100)
        payment_tree.column("reference", width=150)
        
        scrollbar = ttk.Scrollbar(financial_tab, orient=tk.VERTICAL, command=payment_tree.yview)
        payment_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        payment_tree.pack(fill=tk.BOTH, expand=True)
        
        # Load payment history
        cursor.execute('''
            SELECT p.payment_date, i.invoice_number, p.amount, p.payment_method, p.reference
            FROM payments p
            LEFT JOIN invoices i ON p.invoice_id = i.id
            WHERE p.customer_id=?
            ORDER BY p.payment_date DESC
        ''', (customer_id,))
        
        for payment in cursor.fetchall():
            payment_tree.insert("", tk.END, values=(
                payment[0],
                payment[1] or "-",
                f"${payment[2]:,.2f}",
                payment[3],
                payment[4] or "-"
            ))
        
        # Add buttons frame at bottom
        btn_frame = ttk.Frame(details_window)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(btn_frame, text="Edit", command=lambda: self.edit_customer(customer_id), 
                  style='Primary.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Create Order", command=lambda: self.create_order_for_customer(customer_id),
                  style='Success.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Close", command=details_window.destroy, 
                  style='TButton').pack(side=tk.RIGHT, padx=5)
    
    def view_order_from_tree(self, tree):
        """View order from treeview double-click"""
        selected_item = tree.focus()
        if not selected_item:
            return
        
        order_id = tree.item(selected_item)["values"][0]
        self.show_sales_order_details(order_id)
    
    def create_order_for_customer(self, customer_id=None):
        """Create new order for selected customer"""
        if not customer_id:
            selected_item = self.customers_tree.focus()
            if not selected_item:
                messagebox.showwarning("Warning", "Please select a customer first")
                return
            customer_id = self.customers_tree.item(selected_item)["values"][0]
        
        # In a complete implementation, this would open the sales order form
        # with the customer pre-selected
        self.show_sales()
        messagebox.showinfo("Info", f"Create new order for customer ID: {customer_id}")
    
    def export_customers(self):
        """Export customers to CSV"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile="customers_export.csv"
        )
        
        if file_path:
            try:
                cursor = self.conn.cursor()
                cursor.execute('''
                    SELECT code, name, contact_person, address, city, state, country,
                           postal_code, phone, email, tax_id, payment_terms, credit_limit,
                           currency, status, created_at
                    FROM customers
                    ORDER BY name
                ''')
                
                with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    # Write header
                    writer.writerow(['Code', 'Name', 'Contact Person', 'Address', 'City', 
                                   'State', 'Country', 'Postal Code', 'Phone', 'Email',
                                   'Tax ID', 'Payment Terms', 'Credit Limit', 'Currency',
                                   'Status', 'Created At'])
                    # Write data
                    writer.writerows(cursor.fetchall())
                
                self.status_var.set(f"Customers exported to {file_path}")
                messagebox.showinfo("Success", f"Customers exported to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export customers:\n{str(e)}")
    
    def add_customer(self):
        """Open add customer dialog"""
        self.customer_dialog("Add New Customer")
    
    def edit_customer(self, customer_id=None):
        """Open edit customer dialog"""
        if not customer_id:
            selected_item = self.customers_tree.focus()
            if not selected_item:
                messagebox.showwarning("Warning", "Please select a customer first")
                return
            customer_id = self.customers_tree.item(selected_item)["values"][0]
        
        self.customer_dialog("Edit Customer", customer_id)
    
    def customer_dialog(self, title, customer_id=None):
        """Enhanced customer add/edit dialog with validation"""
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("700x800")
        
        # Form frame with scrollbar
        main_frame = ttk.Frame(dialog, style='TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='TFrame')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Form fields
        fields = [
            ("Basic Information", [
                ("Code*:", "code", "entry", True),
                ("Name*:", "name", "entry", True),
                ("Status*:", "status", "combobox", ["Active", "Inactive", "On Hold"], True)
            ]),
            ("Contact Information", [
                ("Contact Person:", "contact_person", "entry", False),
                ("Phone:", "phone", "entry", False),
                ("Email:", "email", "entry", False)
            ]),
            ("Address Information", [
                ("Address:", "address", "entry", False),
                ("City:", "city", "entry", False),
                ("State/Region:", "state", "entry", False),
                ("Country:", "country", "entry", False),
                ("Postal Code:", "postal_code", "entry", False)
            ]),
            ("Financial Information", [
                ("Tax ID:", "tax_id", "entry", False),
                ("Payment Terms (days):", "payment_terms", "spinbox", (0, 365), False),
                ("Credit Limit:", "credit_limit", "entry", False),
                ("Currency:", "currency", "combobox", ["USD", "EUR", "GBP", "JPY", "CAD"], False)
            ]),
            ("Additional Information", [
                ("Notes:", "notes", "text", 4, False)
            ])
        ]
        
        self.customer_form_vars = {}
        
        for section, section_fields in fields:
            # Add section header
            section_frame = ttk.LabelFrame(scrollable_frame, text=section, style='TFrame')
            section_frame.pack(fill=tk.X, padx=10, pady=5, ipady=5)
            
            for i, (label, field, field_type, *args) in enumerate(section_fields):
                required = args[-1] if args else False
                row_frame = ttk.Frame(section_frame, style='TFrame')
                row_frame.pack(fill=tk.X, pady=2)
                
                # Label with required indicator
                lbl = ttk.Label(row_frame, text=label, width=20, anchor=tk.W,
                               style='Header.TLabel' if required else 'TLabel',
                               foreground='red' if required else None)
                lbl.pack(side=tk.LEFT)
                
                # Create appropriate input field
                if field_type == "entry":
                    var = tk.StringVar()
                    entry = ttk.Entry(row_frame, textvariable=var)
                    entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
                    self.customer_form_vars[field] = var
                
                elif field_type == "combobox":
                    var = tk.StringVar()
                    values = args[0] if args else []
                    combobox = ttk.Combobox(row_frame, textvariable=var, values=values)
                    combobox.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
                    if values:
                        combobox.set(values[0])
                    self.customer_form_vars[field] = var
                
                elif field_type == "spinbox":
                    var = tk.StringVar()
                    from_, to = args[0] if args else (0, 100)
                    spinbox = ttk.Spinbox(row_frame, textvariable=var, from_=from_, to=to)
                    spinbox.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
                    self.customer_form_vars[field] = var
                
                elif field_type == "text":
                    rows = args[0] if args else 3
                    text = tk.Text(row_frame, height=rows, wrap=tk.WORD)
                    text.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
                    self.customer_form_vars[field] = text
        
        # Load customer data if editing
        if customer_id:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM customers WHERE id=?", (customer_id,))
            customer = cursor.fetchone()
            
            if customer:
                # Map database fields to form variables
                field_mapping = [
                    ('code', 1), ('name', 2), ('contact_person', 3),
                    ('address', 4), ('city', 5), ('state', 6),
                    ('country', 7), ('postal_code', 8), ('phone', 9),
                    ('email', 10), ('tax_id', 11), ('payment_terms', 12),
                    ('credit_limit', 13), ('currency', 14), ('status', 15),
                    ('notes', 16)
                ]
                
                for field, idx in field_mapping:
                    if field in self.customer_form_vars:
                        value = customer[idx]
                        if value is not None:
                            if isinstance(self.customer_form_vars[field], tk.StringVar):
                                self.customer_form_vars[field].set(value)
                            elif isinstance(self.customer_form_vars[field], tk.Text):
                                self.customer_form_vars[field].insert(tk.END, value)
        
        # Button frame
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(btn_frame, text="Save", command=lambda: self.save_customer(customer_id, dialog), 
                  style='Primary.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy, 
                  style='TButton').pack(side=tk.RIGHT, padx=5)
    
    def save_customer(self, customer_id, dialog):
        """Save customer with validation"""
        try:
            # Validate required fields
            errors = []
            if not self.customer_form_vars["code"].get():
                errors.append("Customer code is required")
            if not self.customer_form_vars["name"].get():
                errors.append("Customer name is required")
            if not self.customer_form_vars["status"].get():
                errors.append("Status is required")
            
            if errors:
                messagebox.showerror("Validation Error", "\n".join(errors))
                return
            
            # Prepare data
            data = {
                "code": self.customer_form_vars["code"].get(),
                "name": self.customer_form_vars["name"].get(),
                "contact_person": self.customer_form_vars["contact_person"].get() or None,
                "address": self.customer_form_vars["address"].get() or None,
                "city": self.customer_form_vars["city"].get() or None,
                "state": self.customer_form_vars["state"].get() or None,
                "country": self.customer_form_vars["country"].get() or None,
                "postal_code": self.customer_form_vars["postal_code"].get() or None,
                "phone": self.customer_form_vars["phone"].get() or None,
                "email": self.customer_form_vars["email"].get() or None,
                "tax_id": self.customer_form_vars["tax_id"].get() or None,
                "payment_terms": int(self.customer_form_vars["payment_terms"].get()) if self.customer_form_vars["payment_terms"].get() else None,
                "credit_limit": float(self.customer_form_vars["credit_limit"].get()) if self.customer_form_vars["credit_limit"].get() else None,
                "currency": self.customer_form_vars["currency"].get() or None,
                "status": self.customer_form_vars["status"].get(),
                "notes": self.customer_form_vars["notes"].get("1.0", tk.END).strip() if isinstance(self.customer_form_vars["notes"], tk.Text) else None,
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "created_by": self.current_user[0] if self.current_user else None
            }
            
            cursor = self.conn.cursor()
            
            if customer_id:
                # Update existing customer
                cursor.execute('''
                    UPDATE customers 
                    SET code=?, name=?, contact_person=?, address=?, city=?, state=?,
                        country=?, postal_code=?, phone=?, email=?, tax_id=?, payment_terms=?,
                        credit_limit=?, currency=?, status=?, notes=?, updated_at=?
                    WHERE id=?
                ''', (
                    data["code"], data["name"], data["contact_person"], data["address"],
                    data["city"], data["state"], data["country"], data["postal_code"],
                    data["phone"], data["email"], data["tax_id"], data["payment_terms"],
                    data["credit_limit"], data["currency"], data["status"], data["notes"],
                    data["updated_at"], customer_id
                ))
                
                action = "update"
            else:
                # Insert new customer
                data["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute('''
                    INSERT INTO customers (
                        code, name, contact_person, address, city, state, country,
                        postal_code, phone, email, tax_id, payment_terms, credit_limit,
                        currency, status, notes, created_at, updated_at, created_by
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    data["code"], data["name"], data["contact_person"], data["address"],
                    data["city"], data["state"], data["country"], data["postal_code"],
                    data["phone"], data["email"], data["tax_id"], data["payment_terms"],
                    data["credit_limit"], data["currency"], data["status"], data["notes"],
                    data["created_at"], data["updated_at"], data["created_by"]
                ))
                
                customer_id = cursor.lastrowid
                action = "create"
            
            # Log the activity
            cursor.execute('''
                INSERT INTO audit_log (user_id, action, table_name, record_id, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (self.current_user[0], action, 'customers', customer_id, 
                 datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            
            self.conn.commit()
            
            self.load_customers()
            dialog.destroy()
            messagebox.showinfo("Success", "Customer saved successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save customer:\n{str(e)}")
    
    def delete_customer(self):
        """Delete customer with confirmation and checks"""
        selected_item = self.customers_tree.focus()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a customer first")
            return
        
        customer_id = self.customers_tree.item(selected_item)["values"][0]
        customer_name = self.customers_tree.item(selected_item)["values"][2]
        
        if not messagebox.askyesno("Confirm Delete", 
                                 f"Are you sure you want to delete customer:\n{customer_name}?"):
            return
        
        try:
            cursor = self.conn.cursor()
            
            # Check if customer has orders
            cursor.execute("SELECT COUNT(*) FROM sales_orders WHERE customer_id=?", (customer_id,))
            order_count = cursor.fetchone()[0]
            
            if order_count > 0:
                messagebox.showerror("Error", "Cannot delete customer with existing orders")
                return
            
            # Delete customer
            cursor.execute("DELETE FROM customers WHERE id=?", (customer_id,))
            
            # Log the activity
            cursor.execute('''
                INSERT INTO audit_log (user_id, action, table_name, record_id, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (self.current_user[0], 'delete', 'customers', customer_id, 
                 datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            
            self.conn.commit()
            
            self.load_customers()
            messagebox.showinfo("Success", "Customer deleted successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete customer:\n{str(e)}")
    
    def create_suppliers_tab(self):
        """Similar to customers tab but for suppliers"""
        pass
    
    def create_products_tab(self):
        """Enhanced products management tab"""
        pass
    
    def create_sales_tab(self):
        """Enhanced sales order management"""
        pass
    
    def create_purchases_tab(self):
        """Enhanced purchase order management"""
        pass
    
    def create_inventory_tab(self):
        """Enhanced inventory management"""
        pass
    
    def create_invoices_tab(self):
        """Enhanced invoice management"""
        pass
    
    def create_reports_tab(self):
        """Enhanced reporting section"""
        pass
    
    def create_settings_tab(self):
        """Enhanced system settings"""
        pass
    
    def show_login(self):
        """Show login dialog"""
        self.login_dialog = tk.Toplevel(self.root)
        self.login_dialog.title("ERP System Login")
        self.login_dialog.geometry("400x300")
        self.login_dialog.resizable(False, False)
        
        # Make the login dialog modal
        self.login_dialog.grab_set()
        self.login_dialog.focus_set()
        
        # Center the dialog
        window_width = self.login_dialog.winfo_reqwidth()
        window_height = self.login_dialog.winfo_reqheight()
        position_right = int(self.login_dialog.winfo_screenwidth()/2 - window_width/2)
        position_down = int(self.login_dialog.winfo_screenheight()/2 - window_height/2)
        self.login_dialog.geometry(f"+{position_right}+{position_down}")
        
        # Login form
        login_frame = ttk.Frame(self.login_dialog, style='TFrame')
        login_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        ttk.Label(login_frame, text="ERP System Login", style='Title.TLabel').pack(pady=10)
        
        # Username
        ttk.Label(login_frame, text="Username:", style='Header.TLabel').pack(anchor=tk.W, pady=(10, 0))
        self.username_entry = ttk.Entry(login_frame)
        self.username_entry.pack(fill=tk.X, pady=5)
        self.username_entry.focus()
        
        # Password
        ttk.Label(login_frame, text="Password:", style='Header.TLabel').pack(anchor=tk.W, pady=(10, 0))
        self.password_entry = ttk.Entry(login_frame, show="*")
        self.password_entry.pack(fill=tk.X, pady=5)
        
        # Login button
        btn_frame = ttk.Frame(login_frame, style='TFrame')
        btn_frame.pack(fill=tk.X, pady=20)
        
        ttk.Button(btn_frame, text="Login", command=self.do_login, 
                  style='Primary.TButton').pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(btn_frame, text="Cancel", command=self.on_closing, 
                  style='TButton').pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))
        
        # Bind Enter key to login
        self.password_entry.bind("<Return>", lambda e: self.do_login())
    
    def do_login(self):
        """Authenticate user"""
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
        
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
                SELECT id, username, name, email, role 
                FROM users 
                WHERE username=? AND password=? AND is_active=1
            ''', (username, self.hash_password(password)))
            
            user = cursor.fetchone()
            
            if user:
                self.current_user = user
                self.user_label.config(text=f"Welcome, {user[2]}")
                self.user_status_var.set(f"Logged in as {user[2]} ({user[4]})")
                
                # Load user permissions
                cursor.execute('''
                    SELECT module, can_view, can_create, can_edit, can_delete
                    FROM permissions
                    WHERE user_id=?
                ''', (user[0],))
                
                self.user_permissions = {}
                for row in cursor.fetchall():
                    self.user_permissions[row[0]] = {
                        'view': bool(row[1]),
                        'create': bool(row[2]),
                        'edit': bool(row[3]),
                        'delete': bool(row[4])
                    }
                
                # Show dashboard by default
                self.show_dashboard()
                self.login_dialog.destroy()
                
                # Enable all tabs for admin, others based on permissions
                if user[4] == 'Admin':
                    for tab in self.notebook.tabs():
                        self.notebook.tab(tab, state='normal')
                else:
                    # Implement permission-based tab enabling
                    pass
                
                # Log the login
                cursor.execute('''
                    UPDATE users SET last_login=? WHERE id=?
                ''', (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user[0]))
                
                cursor.execute('''
                    INSERT INTO audit_log (user_id, action, table_name, record_id, created_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (user[0], 'login', 'users', user[0], 
                     datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                
                self.conn.commit()
                
                self.status_var.set("Login successful")
            else:
                messagebox.showerror("Error", "Invalid username or password")
        except Exception as e:
            messagebox.showerror("Error", f"Login failed:\n{str(e)}")
    
    def refresh_current_tab(self):
        """Refresh the currently selected tab"""
        current_tab = self.notebook.select()
        if current_tab == self.dashboard_tab:
            self.load_dashboard_data()
        elif current_tab == self.customers_tab:
            self.load_customers()
        # Add other tabs as needed
    
    def logout(self):
        """Logout from the application"""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            # Log the logout
            if self.current_user:
                cursor = self.conn.cursor()
                cursor.execute('''
                    INSERT INTO audit_log (user_id, action, table_name, record_id, created_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (self.current_user[0], 'logout', 'users', self.current_user[0], 
                     datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                self.conn.commit()
            
            # Reset UI
            self.current_user = None
            self.user_permissions = {}
            self.user_label.config(text="Not logged in")
            self.user_status_var.set("Not logged in")
            
            # Hide all tabs
            for tab in self.notebook.tabs():
                self.notebook.hide(tab)
            
            # Show login dialog
            self.show_login()
    
    def on_closing(self):
        """Handle window closing event"""
        if messagebox.askokcancel("Quit", "Do you want to quit the application?"):
            if self.current_user:
                # Log the logout if user was logged in
                cursor = self.conn.cursor()
                cursor.execute('''
                    INSERT INTO audit_log (user_id, action, table_name, record_id, created_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (self.current_user[0], 'logout', 'users', self.current_user[0], 
                     datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                self.conn.commit()
            
            self.conn.close()
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = EnhancedERP(root)
    root.mainloop()