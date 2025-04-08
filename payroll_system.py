import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import datetime, date
import os


def initialize_database():
    try:
        # Connect to SQLite database (creates if doesn't exist)
        connection = sqlite3.connect('employee.db')
        cursor = connection.cursor()

        # Create tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT,
                address TEXT,
                city TEXT,
                state TEXT,
                postal_code TEXT,
                country TEXT,
                hire_date TEXT NOT NULL,
                status TEXT DEFAULT 'active' CHECK(status IN ('active', 'on_leave', 'terminated'))
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS payroll (
                payroll_id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER NOT NULL,
                employee_name TEXT NOT NULL,
                leaves INTEGER DEFAULT 0,
                deducted_salary REAL DEFAULT 0,
                bonus REAL DEFAULT 0,
                income_tax REAL DEFAULT 0,
                final_pay REAL NOT NULL,
                payment_date TEXT NOT NULL,
                FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS leave_register (
                leave_id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER NOT NULL,
                employee_name TEXT NOT NULL,
                date_from TEXT NOT NULL,
                date_to TEXT NOT NULL,
                reason TEXT,
                leaves INTEGER NOT NULL,
                current_leaves INTEGER NOT NULL,
                FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS employee_salary (
                salary_id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER NOT NULL,
                base_salary REAL NOT NULL,
                hra REAL NOT NULL,
                da REAL NOT NULL,
                bonus REAL DEFAULT 0,
                effective_date TEXT NOT NULL,
                FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
            )
        """)
        connection.commit()
        messagebox.showinfo("Success", "Database initialized successfully")

    except sqlite3.Error as err:
        messagebox.showerror("Database Error", f"Error initializing database:\n{err}")
    finally:
        if connection:
            connection.close()


def create_db_connection():
    try:
        # Check if database exists, if not initialize it
        if not os.path.exists('employee.db'):
            initialize_database()

        connection = sqlite3.connect('employee.db')
        connection.row_factory = sqlite3.Row  # To access columns by name
        return connection
    except sqlite3.Error as err:
        messagebox.showerror("Database Error", f"Failed to connect to database:\n{err}")
        return None


# Main application code
class PayrollSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Payroll Management System")
        self.root.geometry("1000x700")
        self.root.configure(bg="#f5f7fa")

        # Initialize database connection
        self.connection = create_db_connection()
        if not self.connection:
            return
        self.cursor = self.connection.cursor()

        # User credentials
        self.user_pass_data_set = {
            'admin': 'password',
            'manager': 'manager123',
            'hr': 'hr123'
        }

        # UI Setup
        self.setup_styles()
        self.show_login_screen()

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Color scheme
        self.primary_color = "#4e73df"
        self.secondary_color = "#1cc88a"
        self.danger_color = "#e74a3b"
        self.light_bg = "#f8f9fc"
        self.dark_text = "#5a5c69"

        # Configure styles
        self.style.configure("TFrame", background=self.light_bg)
        self.style.configure("TLabel", background=self.light_bg, foreground=self.dark_text, font=("Segoe UI", 10))
        self.style.configure("Title.TLabel", font=("Segoe UI", 24, "bold"), foreground=self.primary_color)
        self.style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), foreground=self.dark_text)
        self.style.configure("TButton", font=("Segoe UI", 10), padding=8)
        self.style.configure("Primary.TButton", background=self.primary_color, foreground="white")
        self.style.map("Primary.TButton", background=[("active", "#2e59d9")])
        self.style.configure("Success.TButton", background=self.secondary_color, foreground="white")
        self.style.map("Success.TButton", background=[("active", "#17a673")])
        self.style.configure("Danger.TButton", background=self.danger_color, foreground="white")
        self.style.map("Danger.TButton", background=[("active", "#be2617")])
        self.style.configure("TEntry", font=("Segoe UI", 10), padding=5)
        self.style.configure("Treeview", font=("Segoe UI", 10), rowheight=25)
        self.style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        self.style.map("Treeview", background=[("selected", self.primary_color)])

    def show_login_screen(self):
        self.login_frame = ttk.Frame(self.root, style="TFrame")
        self.login_frame.pack(expand=True, padx=50, pady=50)

        # Logo and title
        logo_frame = ttk.Frame(self.login_frame, style="TFrame")
        logo_frame.pack(pady=(0, 30))

        ttk.Label(logo_frame, text="💰", font=("Segoe UI", 48)).pack()
        ttk.Label(logo_frame, text="Payroll System", style="Title.TLabel").pack()

        # Login form
        form_frame = ttk.Frame(self.login_frame, style="TFrame", padding=20)
        form_frame.pack()

        ttk.Label(form_frame, text="Username:").grid(row=0, column=0, padx=5, pady=10, sticky="e")
        self.user_name_var = tk.StringVar()
        user_name_entry = ttk.Entry(form_frame, textvariable=self.user_name_var, font=("Segoe UI", 10), width=25)
        user_name_entry.grid(row=0, column=1, padx=5, pady=10)

        ttk.Label(form_frame, text="Password:").grid(row=1, column=0, padx=5, pady=10, sticky="e")
        self.password_var = tk.StringVar()
        password_entry = ttk.Entry(form_frame, textvariable=self.password_var, show='*', font=("Segoe UI", 10),
                                   width=25)
        password_entry.grid(row=1, column=1, padx=5, pady=10)

        self.error_label = ttk.Label(form_frame, text="", foreground=self.danger_color)
        self.error_label.grid(row=2, column=0, columnspan=2, pady=5)

        login_button = ttk.Button(form_frame, text="Login", style="Primary.TButton",
                                  command=self.attempt_login, width=20)
        login_button.grid(row=3, column=0, columnspan=2, pady=15)

        # Bind Enter key to login
        password_entry.bind("<Return>", lambda e: self.attempt_login())

        # Footer
        footer_frame = ttk.Frame(self.login_frame, style="TFrame")
        footer_frame.pack(pady=(20, 0))

        ttk.Label(footer_frame, text="© 2025 Payroll Management System", font=("Segoe UI", 8)).pack()

        # Add database initialization button for admin
        init_db_btn = ttk.Button(footer_frame, text="Initialize Database",
                                 command=initialize_database)
        init_db_btn.pack(pady=10)

    def attempt_login(self):
        username = self.user_name_var.get()
        password = self.password_var.get()

        if username in self.user_pass_data_set and self.user_pass_data_set[username] == password:
            self.logged_in_user = username
            self.user_role = "admin" if username == "admin" else "user"
            self.user_name_var.set("")
            self.password_var.set("")
            self.show_main_window()
        else:
            self.error_label.config(text="Invalid username or password. Please try again.")

    def show_main_window(self):
        self.login_frame.destroy()

        # Create main window components
        self.setup_main_window()

    def setup_main_window(self):
        # Header frame
        self.header_frame = ttk.Frame(self.root, style="TFrame")
        self.header_frame.pack(fill="x", padx=20, pady=10)

        # App title and user info
        title_frame = ttk.Frame(self.header_frame, style="TFrame")
        title_frame.pack(side="left", fill="x", expand=True)

        ttk.Label(title_frame, text="Payroll Management System", style="Title.TLabel").pack(anchor="w")
        ttk.Label(title_frame,
                  text=f"Welcome, {self.logged_in_user} ({self.user_role.capitalize()}) | {datetime.now().strftime('%A, %B %d, %Y')}",
                  font=("Segoe UI", 10)).pack(anchor="w")

        # Logout button
        logout_btn = ttk.Button(self.header_frame, text="Logout", style="Danger.TButton",
                                command=self.logout)
        logout_btn.pack(side="right", padx=5)

        # Navigation sidebar
        self.sidebar_frame = ttk.Frame(self.root, style="TFrame", width=200)
        self.sidebar_frame.pack(side="left", fill="y", padx=10, pady=10)

        # Main content area
        self.content_frame = ttk.Frame(self.root, style="TFrame")
        self.content_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # Navigation buttons
        self.setup_navigation()

        # Show dashboard by default
        self.show_dashboard()

    def setup_navigation(self):
        nav_buttons = [
            ("Dashboard", "📊", self.show_dashboard),
            ("Employees", "👥", self.show_employee_list),
            ("Salary Management", "💵", self.show_salary_management),
            ("Payroll", "💰", self.show_payroll),
            ("Leave Management", "📅", self.show_leave_management),
            ("Reports", "📈", self.show_reports),
        ]

        for text, icon, command in nav_buttons:
            btn = ttk.Button(self.sidebar_frame, text=f"{icon} {text}", style="TButton",
                             command=lambda cmd=command: cmd())
            btn.pack(fill="x", pady=5, ipady=5)

        # Admin-only buttons
        if self.user_role == "admin":
            ttk.Separator(self.sidebar_frame, orient="horizontal").pack(fill="x", pady=10)
            admin_label = ttk.Label(self.sidebar_frame, text="Admin Tools", font=("Segoe UI", 10, "bold"))
            admin_label.pack(anchor="w", pady=5)

            admin_buttons = [
                ("Add Employee", "➕", self.add_employee),
                ("System Settings", "⚙️", self.show_settings),
            ]

            for text, icon, command in admin_buttons:
                btn = ttk.Button(self.sidebar_frame, text=f"{icon} {text}", style="TButton",
                                 command=lambda cmd=command: cmd())
                btn.pack(fill="x", pady=5, ipady=5)

    def logout(self):
        # Clear main window
        for widget in self.root.winfo_children():
            widget.destroy()

        # Show login screen again
        self.show_login_screen()

    def show_dashboard(self):
        # Clear previous content
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Dashboard header
        header = ttk.Frame(self.content_frame, style="TFrame")
        header.pack(fill="x", pady=(0, 20))

        ttk.Label(header, text="Dashboard", style="Header.TLabel").pack(side="left")

        # Refresh button
        refresh_btn = ttk.Button(header, text="🔄 Refresh", style="TButton",
                                 command=self.show_dashboard)
        refresh_btn.pack(side="right")

        # Dashboard metrics
        metrics_frame = ttk.Frame(self.content_frame, style="TFrame")
        metrics_frame.pack(fill="x", pady=10)

        # Get metrics from database
        self.cursor.execute("SELECT COUNT(*) as total FROM employees")
        total_employees = self.cursor.fetchone()[0]

        current_month = datetime.now().strftime("%Y-%m")
        self.cursor.execute("SELECT COUNT(*) as total FROM payroll WHERE strftime('%Y-%m', payment_date) = ?",
                            (current_month,))
        current_month_payroll = self.cursor.fetchone()[0]

        self.cursor.execute("""
            SELECT COUNT(*) as total 
            FROM leave_register 
            WHERE date_from <= date('now', 'start of month', '+1 month', '-1 day')
            AND date_to >= date('now', 'start of month')
        """)
        active_leaves = self.cursor.fetchone()[0]

        # Metric cards
        metric_cards = [
            ("Total Employees", total_employees, self.primary_color),
            ("This Month's Payroll", current_month_payroll, self.secondary_color),
            ("Active Leave Requests", active_leaves, "#36b9cc"),
        ]

        for text, value, color in metric_cards:
            card = ttk.Frame(metrics_frame, style="TFrame", relief="groove", borderwidth=1)
            card.pack(side="left", expand=True, fill="both", padx=5, ipady=10)

            ttk.Label(card, text=text, font=("Segoe UI", 10, "bold")).pack(pady=(10, 5))
            ttk.Label(card, text=str(value), font=("Segoe UI", 24, "bold"), foreground=color).pack(pady=(0, 10))

        # Recent activities
        ttk.Label(self.content_frame, text="Recent Activities", style="Header.TLabel").pack(anchor="w", pady=(20, 5))

        activities_frame = ttk.Frame(self.content_frame, style="TFrame")
        activities_frame.pack(fill="both", expand=True)

        # Recent payroll
        payroll_frame = ttk.Frame(activities_frame, style="TFrame")
        payroll_frame.pack(side="left", fill="both", expand=True, padx=5)

        ttk.Label(payroll_frame, text="Recent Payroll", font=("Segoe UI", 10, "bold")).pack(anchor="w")

        self.cursor.execute("""
            SELECT employee_name, final_pay, payment_date 
            FROM payroll 
            ORDER BY payment_date DESC 
            LIMIT 5
        """)
        recent_payroll = self.cursor.fetchall()

        columns = ("Name", "Amount", "Date")
        tree = ttk.Treeview(payroll_frame, columns=columns, show="headings", height=5)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        tree.pack(fill="both", expand=True, pady=5)

        for item in recent_payroll:
            tree.insert("", "end", values=(
                item['employee_name'], f"₹{item['final_pay']:,}", item['payment_date']))

        # Recent leaves
        leaves_frame = ttk.Frame(activities_frame, style="TFrame")
        leaves_frame.pack(side="left", fill="both", expand=True, padx=5)

        ttk.Label(leaves_frame, text="Recent Leave Requests", font=("Segoe UI", 10, "bold")).pack(anchor="w")

        self.cursor.execute("""
            SELECT employee_name, date_from, date_to, leaves 
            FROM leave_register 
            ORDER BY date_from DESC 
            LIMIT 5
        """)
        recent_leaves = self.cursor.fetchall()

        columns = ("Name", "From", "To", "Days")
        tree = ttk.Treeview(leaves_frame, columns=columns, show="headings", height=5)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        tree.pack(fill="both", expand=True, pady=5)

        for item in recent_leaves:
            tree.insert("", "end", values=(
                item['employee_name'],
                item['date_from'],
                item['date_to'],
                item['leaves']
            ))

    def show_employee_list(self):
        # Clear previous content
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Header and controls
        header = ttk.Frame(self.content_frame, style="TFrame")
        header.pack(fill="x", pady=(0, 20))

        ttk.Label(header, text="Employee Management", style="Header.TLabel").pack(side="left")

        # Search and filter controls
        controls_frame = ttk.Frame(header, style="TFrame")
        controls_frame.pack(side="right")

        search_var = tk.StringVar()
        search_entry = ttk.Entry(controls_frame, textvariable=search_var, width=30)
        search_entry.pack(side="left", padx=5)
        search_entry.bind("<Return>", lambda e: self.refresh_employee_list(search_var.get()))

        search_btn = ttk.Button(controls_frame, text="🔍 Search", style="TButton",
                                command=lambda: self.refresh_employee_list(search_var.get()))
        search_btn.pack(side="left", padx=5)

        refresh_btn = ttk.Button(controls_frame, text="🔄 Refresh", style="TButton",
                                 command=lambda: self.refresh_employee_list())
        refresh_btn.pack(side="left")

        # Action buttons
        actions_frame = ttk.Frame(self.content_frame, style="TFrame")
        actions_frame.pack(fill="x", pady=(0, 10))

        if self.user_role == "admin":
            add_btn = ttk.Button(actions_frame, text="➕ Add Employee", style="Success.TButton",
                                 command=self.add_employee)
            add_btn.pack(side="left", padx=5)

        export_btn = ttk.Button(actions_frame, text="📁 Export to CSV", style="Primary.TButton",
                                command=self.export_employees_to_csv)
        export_btn.pack(side="left", padx=5)

        # Employee list
        list_frame = ttk.Frame(self.content_frame, style="TFrame")
        list_frame.pack(fill="both", expand=True)

        # Create treeview with scrollbars
        tree_scroll = ttk.Frame(list_frame)
        tree_scroll.pack(fill="both", expand=True)

        vsb = ttk.Scrollbar(tree_scroll, orient="vertical")
        hsb = ttk.Scrollbar(tree_scroll, orient="horizontal")

        columns = ("ID", "Name", "Email", "Phone", "Hire Date", "Status")
        self.employee_tree = ttk.Treeview(tree_scroll, columns=columns, show="headings",
                                          yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        vsb.config(command=self.employee_tree.yview)
        hsb.config(command=self.employee_tree.xview)

        self.employee_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        # Configure columns
        col_widths = {
            "ID": 50, "Name": 150, "Email": 200,
            "Phone": 100, "Hire Date": 100, "Status": 80
        }

        for col in columns:
            self.employee_tree.heading(col, text=col)
            self.employee_tree.column(col, width=col_widths.get(col, 100), anchor="center")

        # Initial data load
        self.refresh_employee_list()

        # Add double-click event for editing
        self.employee_tree.bind("<Double-1>", lambda e: self.edit_employee())

    def refresh_employee_list(self, search_term=None):
        query = "SELECT employee_id, first_name, last_name, email, phone, hire_date, status FROM employees"
        params = ()

        if search_term:
            query += " WHERE first_name LIKE ? OR last_name LIKE ? OR email LIKE ?"
            params = (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%")

        self.cursor.execute(query, params)
        employees = self.cursor.fetchall()

        # Clear existing data
        for item in self.employee_tree.get_children():
            self.employee_tree.delete(item)

        # Add new data
        for emp in employees:
            self.employee_tree.insert("", "end", values=(
                emp['employee_id'],
                f"{emp['first_name']} {emp['last_name']}",
                emp['email'],
                emp['phone'],
                emp['hire_date'],
                emp['status'].capitalize()
            ))

    def add_employee(self):
        add_window = tk.Toplevel(self.root)
        add_window.title("Add New Employee")
        add_window.geometry("500x600")
        add_window.configure(bg=self.light_bg)

        # Form fields
        fields = [
            ("First Name", "first_name"),
            ("Last Name", "last_name"),
            ("Email", "email"),
            ("Phone", "phone"),
            ("Address", "address"),
            ("City", "city"),
            ("State", "state"),
            ("Postal Code", "postal_code"),
            ("Country", "country"),
            ("Hire Date (YYYY-MM-DD)", "hire_date"),
        ]

        entries = {}
        for i, (label, field) in enumerate(fields):
            frame = ttk.Frame(add_window, style="TFrame")
            frame.pack(fill="x", padx=10, pady=5)

            ttk.Label(frame, text=label).pack(side="left")
            entry = ttk.Entry(frame)
            entry.pack(side="right", expand=True, fill="x")
            entries[field] = entry

        # Status selection
        status_frame = ttk.Frame(add_window, style="TFrame")
        status_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(status_frame, text="Status").pack(side="left")
        status_var = tk.StringVar(value="active")
        status_menu = ttk.OptionMenu(status_frame, status_var, "active", "active", "on_leave", "terminated")
        status_menu.pack(side="right", expand=True, fill="x")

        # Submit button
        def submit_employee():
            try:
                # Get all values from entries
                employee_data = {field: entry.get() for field, entry in entries.items()}
                employee_data['status'] = status_var.get()

                # Basic validation
                if not all(employee_data.values()):
                    messagebox.showerror("Error", "All fields are required")
                    return

                # Insert into database
                self.cursor.execute("""
                    INSERT INTO employees (first_name, last_name, email, phone, address, 
                                         city, state, postal_code, country, hire_date, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    employee_data['first_name'],
                    employee_data['last_name'],
                    employee_data['email'],
                    employee_data['phone'],
                    employee_data['address'],
                    employee_data['city'],
                    employee_data['state'],
                    employee_data['postal_code'],
                    employee_data['country'],
                    employee_data['hire_date'],
                    employee_data['status']
                ))

                self.connection.commit()
                messagebox.showinfo("Success", "Employee added successfully")
                add_window.destroy()
                self.refresh_employee_list()

            except sqlite3.Error as err:
                messagebox.showerror("Database Error", f"Failed to add employee:\n{err}")

        submit_btn = ttk.Button(add_window, text="Add Employee", style="Success.TButton",
                                command=submit_employee)
        submit_btn.pack(pady=20)

    def show_salary_management(self):
        # Clear previous content
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Header and controls
        header = ttk.Frame(self.content_frame, style="TFrame")
        header.pack(fill="x", pady=(0, 20))

        ttk.Label(header, text="Salary Management", style="Header.TLabel").pack(side="left")

        # Action buttons
        actions_frame = ttk.Frame(header, style="TFrame")
        actions_frame.pack(side="right")

        add_btn = ttk.Button(actions_frame, text="➕ Add Salary Record", style="Success.TButton",
                             command=self.add_salary_record)
        add_btn.pack(side="left", padx=5)

        refresh_btn = ttk.Button(actions_frame, text="🔄 Refresh", style="Primary.TButton",
                                 command=self.refresh_salary_list)
        refresh_btn.pack(side="left")

        # Salary list
        list_frame = ttk.Frame(self.content_frame, style="TFrame")
        list_frame.pack(fill="both", expand=True)

        # Create treeview with scrollbars
        tree_scroll = ttk.Frame(list_frame)
        tree_scroll.pack(fill="both", expand=True)

        vsb = ttk.Scrollbar(tree_scroll, orient="vertical")
        hsb = ttk.Scrollbar(tree_scroll, orient="horizontal")

        columns = ("Salary ID", "Employee", "Base Salary", "HRA", "DA", "Bonus", "Effective Date")
        self.salary_tree = ttk.Treeview(tree_scroll, columns=columns, show="headings",
                                        yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        vsb.config(command=self.salary_tree.yview)
        hsb.config(command=self.salary_tree.xview)

        self.salary_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        # Configure columns
        col_widths = {
            "Salary ID": 80, "Employee": 150, "Base Salary": 100,
            "HRA": 80, "DA": 80, "Bonus": 80, "Effective Date": 100
        }

        for col in columns:
            self.salary_tree.heading(col, text=col)
            self.salary_tree.column(col, width=col_widths.get(col, 100), anchor="center")

        # Add double-click event for editing
        self.salary_tree.bind("<Double-1>", lambda e: self.edit_salary_record())

        # Initial data load
        self.refresh_salary_list()

    def refresh_salary_list(self):
        try:
            # Check if the columns exist
            self.cursor.execute("PRAGMA table_info(employee_salary)")
            columns = [column[1] for column in self.cursor.fetchall()]

            if not all(col in columns for col in ['hra', 'da', 'bonus']):
                messagebox.showwarning("Warning",
                                       "Salary table structure is incomplete. Please initialize database.")
                return

            self.cursor.execute("""
                SELECT s.salary_id, e.first_name, e.last_name, 
                       s.base_salary, s.hra, s.da, s.bonus, s.effective_date
                FROM employee_salary s
                JOIN employees e ON s.employee_id = e.employee_id
                ORDER BY s.effective_date DESC
            """)
            salaries = self.cursor.fetchall()

            # Clear existing data
            for item in self.salary_tree.get_children():
                self.salary_tree.delete(item)

            # Add new data
            for salary in salaries:
                self.salary_tree.insert("", "end", values=(
                    salary['salary_id'],
                    f"{salary['first_name']} {salary['last_name']}",
                    f"₹{salary['base_salary']:,}",
                    f"₹{salary['hra']:,}",
                    f"₹{salary['da']:,}",
                    f"₹{salary['bonus']:,}",
                    salary['effective_date']
                ))

        except sqlite3.Error as err:
            messagebox.showerror("Database Error", f"Failed to load salary data:\n{err}")

    def add_salary_record(self):
        add_window = tk.Toplevel(self.root)
        add_window.title("Add Salary Record")
        add_window.geometry("500x400")
        add_window.configure(bg=self.light_bg)

        # Employee selection
        employee_frame = ttk.Frame(add_window, style="TFrame")
        employee_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(employee_frame, text="Employee").pack(side="left")
        self.employee_var = tk.StringVar()

        self.cursor.execute("SELECT employee_id, first_name || ' ' || last_name AS name FROM employees")
        employees = {row['name']: row['employee_id'] for row in self.cursor.fetchall()}

        employee_dropdown = ttk.Combobox(employee_frame, textvariable=self.employee_var,
                                         values=list(employees.keys()))
        employee_dropdown.pack(side="right", expand=True, fill="x")

        # Salary components
        salary_fields = [
            ("Base Salary", "base_salary"),
            ("HRA", "hra"),
            ("DA", "da"),
            ("Bonus", "bonus"),
            ("Effective Date (YYYY-MM-DD)", "effective_date")
        ]

        self.salary_entries = {}
        for label, field in salary_fields:
            frame = ttk.Frame(add_window, style="TFrame")
            frame.pack(fill="x", padx=10, pady=5)

            ttk.Label(frame, text=label).pack(side="left")
            entry = ttk.Entry(frame)
            entry.pack(side="right", expand=True, fill="x")
            self.salary_entries[field] = entry

        # Submit button
        def submit_salary():
            try:
                employee_name = self.employee_var.get()
                if not employee_name or employee_name not in employees:
                    messagebox.showerror("Error", "Please select a valid employee")
                    return

                salary_data = {
                    'employee_id': employees[employee_name],
                    'base_salary': float(self.salary_entries['base_salary'].get()),
                    'hra': float(self.salary_entries['hra'].get()),
                    'da': float(self.salary_entries['da'].get()),
                    'bonus': float(self.salary_entries['bonus'].get()),
                    'effective_date': self.salary_entries['effective_date'].get()
                }

                if not all(salary_data.values()):
                    messagebox.showerror("Error", "All fields are required")
                    return

                # Insert into database
                self.cursor.execute("""
                    INSERT INTO employee_salary 
                    (employee_id, base_salary, hra, da, bonus, effective_date)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    salary_data['employee_id'],
                    salary_data['base_salary'],
                    salary_data['hra'],
                    salary_data['da'],
                    salary_data['bonus'],
                    salary_data['effective_date']
                ))

                self.connection.commit()
                messagebox.showinfo("Success", "Salary record added successfully")
                add_window.destroy()
                self.refresh_salary_list()

            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers for salary components")
            except sqlite3.Error as err:
                messagebox.showerror("Database Error", f"Failed to add salary record:\n{err}")

        submit_btn = ttk.Button(add_window, text="Add Salary Record", style="Success.TButton",
                                command=submit_salary)
        submit_btn.pack(pady=20)

    def edit_salary_record(self):
        selected_item = self.salary_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a salary record to edit")
            return

        salary_id = self.salary_tree.item(selected_item[0], "values")[0]

        edit_window = tk.Toplevel(self.root)
        edit_window.title(f"Edit Salary Record {salary_id}")
        edit_window.geometry("500x400")
        edit_window.configure(bg=self.light_bg)

        # Fetch salary data
        self.cursor.execute("""
            SELECT s.*, e.first_name || ' ' || e.last_name AS employee_name
            FROM employee_salary s
            JOIN employees e ON s.employee_id = e.employee_id
            WHERE s.salary_id = ?
        """, (salary_id,))
        salary = self.cursor.fetchone()

        if not salary:
            messagebox.showerror("Error", "Salary record not found")
            edit_window.destroy()
            return

        # Employee display (read-only)
        employee_frame = ttk.Frame(edit_window, style="TFrame")
        employee_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(employee_frame, text="Employee").pack(side="left")
        employee_label = ttk.Label(employee_frame, text=salary['employee_name'])
        employee_label.pack(side="right")

        # Salary components
        salary_fields = [
            ("Base Salary", "base_salary"),
            ("HRA", "hra"),
            ("DA", "da"),
            ("Bonus", "bonus"),
            ("Effective Date", "effective_date")
        ]

        self.salary_entries = {}
        for label, field in salary_fields:
            frame = ttk.Frame(edit_window, style="TFrame")
            frame.pack(fill="x", padx=10, pady=5)

            ttk.Label(frame, text=label).pack(side="left")
            entry = ttk.Entry(frame)
            entry.insert(0, str(salary[field]))
            entry.pack(side="right", expand=True, fill="x")
            self.salary_entries[field] = entry

        # Submit button
        def update_salary():
            try:
                salary_data = {
                    'salary_id': salary_id,
                    'base_salary': float(self.salary_entries['base_salary'].get()),
                    'hra': float(self.salary_entries['hra'].get()),
                    'da': float(self.salary_entries['da'].get()),
                    'bonus': float(self.salary_entries['bonus'].get()),
                    'effective_date': self.salary_entries['effective_date'].get()
                }

                if not all(salary_data.values()):
                    messagebox.showerror("Error", "All fields are required")
                    return

                # Update in database
                self.cursor.execute("""
                    UPDATE employee_salary 
                    SET base_salary = ?, 
                        hra = ?, 
                        da = ?, 
                        bonus = ?, 
                        effective_date = ?
                    WHERE salary_id = ?
                """, (
                    salary_data['base_salary'],
                    salary_data['hra'],
                    salary_data['da'],
                    salary_data['bonus'],
                    salary_data['effective_date'],
                    salary_data['salary_id']
                ))

                self.connection.commit()
                messagebox.showinfo("Success", "Salary record updated successfully")
                edit_window.destroy()
                self.refresh_salary_list()

            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers for salary components")
            except sqlite3.Error as err:
                messagebox.showerror("Database Error", f"Failed to update salary record:\n{err}")

        update_btn = ttk.Button(edit_window, text="Update Salary Record", style="Success.TButton",
                                command=update_salary)
        update_btn.pack(pady=20)

    def edit_employee(self):
        try:
            selected_item = self.employee_tree.selection()
            if not selected_item:
                messagebox.showwarning("Warning", "Please select an employee to edit")
                return

            # Get employee ID from the first column of selected item
            employee_id = self.employee_tree.item(selected_item[0])['values'][0]

            edit_window = tk.Toplevel(self.root)
            edit_window.title(f"Edit Employee {employee_id}")
            edit_window.geometry("500x600")
            edit_window.configure(bg=self.light_bg)

            # Fetch employee data
            self.cursor.execute("SELECT * FROM employees WHERE employee_id = ?", (employee_id,))
            employee = self.cursor.fetchone()

            if not employee:
                messagebox.showerror("Error", "Employee not found in database")
                edit_window.destroy()
                return

            # Form fields with proper data binding
            fields = [
                ("First Name", "first_name", employee['first_name']),
                ("Last Name", "last_name", employee['last_name']),
                ("Email", "email", employee['email']),
                ("Phone", "phone", employee['phone']),
                ("Address", "address", employee['address']),
                ("City", "city", employee['city']),
                ("State", "state", employee['state']),
                ("Postal Code", "postal_code", employee['postal_code']),
                ("Country", "country", employee['country']),
                ("Hire Date", "hire_date", employee['hire_date']),
            ]

            entries = {}
            for i, (label, field, default_value) in enumerate(fields):
                frame = ttk.Frame(edit_window, style="TFrame")
                frame.pack(fill="x", padx=10, pady=5)

                ttk.Label(frame, text=label).pack(side="left")
                entry = ttk.Entry(frame)
                entry.insert(0, default_value if default_value else "")
                entry.pack(side="right", expand=True, fill="x")
                entries[field] = entry

            # Status selection with current value
            status_frame = ttk.Frame(edit_window, style="TFrame")
            status_frame.pack(fill="x", padx=10, pady=5)

            ttk.Label(status_frame, text="Status").pack(side="left")
            current_status = employee['status'] if employee['status'] else "active"
            status_var = tk.StringVar(value=current_status)
            status_menu = ttk.OptionMenu(status_frame, status_var, "active", "active", "on_leave", "terminated")
            status_menu.pack(side="right", expand=True, fill="x")

            # Action buttons frame
            button_frame = ttk.Frame(edit_window, style="TFrame")
            button_frame.pack(fill="x", pady=10)

            # Update button
            update_btn = ttk.Button(button_frame, text="Update Employee", style="Success.TButton",
                                    command=lambda: self.update_employee_data(
                                        employee_id, entries, status_var, edit_window))
            update_btn.pack(side="left", padx=10, expand=True)

            # Delete button
            delete_btn = ttk.Button(button_frame, text="Delete Employee", style="Danger.TButton",
                                    command=lambda: self.delete_employee(employee_id, edit_window))
            delete_btn.pack(side="left", padx=10, expand=True)

        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")

    def update_employee_data(self, employee_id, entries, status_var, window):
        try:
            # Get all values from entries
            employee_data = {field: entry.get() for field, entry in entries.items()}
            employee_data['status'] = status_var.get()
            employee_data['employee_id'] = employee_id

            # Basic validation
            required_fields = ['first_name', 'last_name', 'email', 'hire_date']
            for field in required_fields:
                if not employee_data[field]:
                    messagebox.showerror("Error", f"{field.replace('_', ' ').title()} is required")
                    return

            # Update in database
            self.cursor.execute("""
                UPDATE employees 
                SET first_name = ?, last_name = ?, email = ?, 
                    phone = ?, address = ?, city = ?, state = ?, 
                    postal_code = ?, country = ?, hire_date = ?, 
                    status = ?
                WHERE employee_id = ?
            """, (
                employee_data['first_name'],
                employee_data['last_name'],
                employee_data['email'],
                employee_data['phone'],
                employee_data['address'],
                employee_data['city'],
                employee_data['state'],
                employee_data['postal_code'],
                employee_data['country'],
                employee_data['hire_date'],
                employee_data['status'],
                employee_data['employee_id']
            ))

            self.connection.commit()
            messagebox.showinfo("Success", "Employee updated successfully")
            window.destroy()
            self.refresh_employee_list()

        except sqlite3.Error as err:
            messagebox.showerror("Database Error", f"Failed to update employee:\n{err}")
            self.connection.rollback()

    def delete_employee(self, employee_id, window):
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this employee?"):
            try:
                # First check if employee has any related records
                self.cursor.execute("SELECT COUNT(*) FROM payroll WHERE employee_id = ?", (employee_id,))
                payroll_count = self.cursor.fetchone()[0]

                self.cursor.execute("SELECT COUNT(*) FROM leave_register WHERE employee_id = ?", (employee_id,))
                leave_count = self.cursor.fetchone()[0]

                self.cursor.execute("SELECT COUNT(*) FROM employee_salary WHERE employee_id = ?", (employee_id,))
                salary_count = self.cursor.fetchone()[0]

                if payroll_count > 0 or leave_count > 0 or salary_count > 0:
                    messagebox.showwarning("Warning",
                                           "Cannot delete employee with associated records. "
                                           "Consider changing status to 'Terminated' instead.")
                    return

                # Delete employee if no related records exist
                self.cursor.execute("DELETE FROM employees WHERE employee_id = ?", (employee_id,))
                self.connection.commit()
                messagebox.showinfo("Success", "Employee deleted successfully")
                window.destroy()
                self.refresh_employee_list()

            except sqlite3.Error as err:
                messagebox.showerror("Database Error", f"Failed to delete employee:\n{err}")
                self.connection.rollback()

    def export_employees_to_csv(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                 filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return

        self.cursor.execute("SELECT * FROM employees")
        employees = self.cursor.fetchall()

        import csv
        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["ID", "First Name", "Last Name", "Email", "Phone", "Hire Date", "Status"])

            for emp in employees:
                writer.writerow([
                    emp['employee_id'],
                    emp['first_name'],
                    emp['last_name'],
                    emp['email'],
                    emp['phone'],
                    emp['hire_date'],
                    emp['status']
                ])

        messagebox.showinfo("Success", f"Employee data exported to {file_path}")

    def show_payroll(self):
        # Clear previous content
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Header and controls
        header = ttk.Frame(self.content_frame, style="TFrame")
        header.pack(fill="x", pady=(0, 20))

        ttk.Label(header, text="Payroll Management", style="Header.TLabel").pack(side="left")

        # Month selection
        controls_frame = ttk.Frame(header, style="TFrame")
        controls_frame.pack(side="right")

        self.month_var = tk.StringVar(value=datetime.now().strftime("%Y-%m"))
        month_entry = ttk.Entry(controls_frame, textvariable=self.month_var, width=7)
        month_entry.pack(side="left", padx=5)

        view_btn = ttk.Button(controls_frame, text="View", style="Primary.TButton",
                              command=lambda: self.refresh_payroll_list())
        view_btn.pack(side="left", padx=5)

        if self.user_role in ["admin", "hr"]:
            gen_btn = ttk.Button(controls_frame, text="Generate Payroll", style="Success.TButton",
                                 command=self.generate_payroll)
            gen_btn.pack(side="left", padx=5)

        # Payroll list
        list_frame = ttk.Frame(self.content_frame, style="TFrame")
        list_frame.pack(fill="both", expand=True)

        # Create treeview with scrollbars
        tree_scroll = ttk.Frame(list_frame)
        tree_scroll.pack(fill="both", expand=True)

        vsb = ttk.Scrollbar(tree_scroll, orient="vertical")
        hsb = ttk.Scrollbar(tree_scroll, orient="horizontal")

        columns = ("ID", "Employee", "Leaves", "Deductions", "Bonus", "Tax", "Net Pay", "Payment Date")
        self.payroll_tree = ttk.Treeview(tree_scroll, columns=columns, show="headings",
                                         yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        vsb.config(command=self.payroll_tree.yview)
        hsb.config(command=self.payroll_tree.xview)

        self.payroll_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        # Configure columns
        col_widths = {
            "ID": 50, "Employee": 150, "Leaves": 60,
            "Deductions": 90, "Bonus": 80, "Tax": 80,
            "Net Pay": 100, "Payment Date": 100
        }

        for col in columns:
            self.payroll_tree.heading(col, text=col)
            self.payroll_tree.column(col, width=col_widths.get(col, 100), anchor="center")

        # Initial data load
        self.refresh_payroll_list()

    def refresh_payroll_list(self):
        try:
            # Get the selected month or show all if not specified
            if hasattr(self, 'month_var'):
                month_filter = self.month_var.get()
                if month_filter:
                    year, month = month_filter.split("-")
                    self.cursor.execute("""
                        SELECT * FROM payroll 
                        WHERE strftime('%Y', payment_date) = ? 
                        AND strftime('%m', payment_date) = ?
                        ORDER BY payment_date DESC
                    """, (year, month))
                else:
                    self.cursor.execute("SELECT * FROM payroll ORDER BY payment_date DESC")
            else:
                self.cursor.execute("SELECT * FROM payroll ORDER BY payment_date DESC")

            payrolls = self.cursor.fetchall()

            # Clear existing data
            for item in self.payroll_tree.get_children():
                self.payroll_tree.delete(item)

            # Add new data
            for pay in payrolls:
                self.payroll_tree.insert("", "end", values=(
                    pay['payroll_id'],
                    pay['employee_name'],
                    pay['leaves'],
                    f"₹{pay['deducted_salary']:,.2f}",
                    f"₹{pay['bonus']:,.2f}",
                    f"₹{pay['income_tax']:,.2f}",
                    f"₹{pay['final_pay']:,.2f}",
                    pay['payment_date']
                ))

        except sqlite3.Error as err:
            messagebox.showerror("Database Error", f"Failed to load payroll data:\n{err}")

    def generate_payroll(self):
        # Check if payroll has already been generated this month
        current_month = datetime.now().strftime("%Y-%m")
        self.cursor.execute("SELECT * FROM payroll WHERE strftime('%Y-%m', payment_date) = ?", (current_month,))
        if self.cursor.fetchone():
            messagebox.showwarning("Warning", "Payroll has already been generated for this month!")
            return

        # Show estimated payroll preview
        preview_window = tk.Toplevel(self.root)
        preview_window.title('Payroll Generation Preview')
        preview_window.geometry("900x600")
        preview_window.configure(bg=self.light_bg)

        ttk.Label(preview_window,
                  text=f"Payroll Preview for {datetime.now().strftime('%B %Y')}",
                  style="Header.TLabel").pack(pady=10)

        # Calculate estimated payroll using employee_salary table
        self.cursor.execute("""
            SELECT 
                e.employee_id, 
                e.first_name || ' ' || e.last_name AS employee_name,
                IFNULL(l.leaves, 0) AS leaves,
                s.base_salary AS gross_salary,
                s.hra,
                s.da,
                s.bonus
            FROM 
                employees e
            JOIN 
                employee_salary s ON e.employee_id = s.employee_id
            LEFT JOIN 
                (SELECT employee_id, SUM(leaves) AS leaves 
                 FROM leave_register 
                 WHERE date_from <= date('now', 'start of month', '+1 month', '-1 day')
                 AND date_to >= date('now', 'start of month')
                 GROUP BY employee_id) l 
            ON e.employee_id = l.employee_id
            WHERE e.status = 'active'
            AND s.effective_date = (
                SELECT MAX(effective_date) 
                FROM employee_salary 
                WHERE employee_id = e.employee_id
            )
        """)

        estimated_data = self.cursor.fetchall()

        # Create treeview
        tree_frame = ttk.Frame(preview_window)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")

        columns = ["ID", "Employee", "Leaves", "Basic", "HRA", "DA", "Bonus", "Gross", "Tax", "Net Pay"]
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings",
                            yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        vsb.config(command=tree.yview)
        hsb.config(command=tree.xview)

        tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=80, anchor="center")

        for record in estimated_data:
            # Convert all values to float for calculations
            base = float(record['gross_salary'])
            hra = float(record['hra'])
            da = float(record['da'])
            bonus = float(record['bonus'])
            leaves = int(record['leaves'])

            gross = base + hra + da + bonus
            tax = gross * 0.1  # 10% tax

            # Deduct for leaves (assuming 1 day = basic/30)
            leave_deduction = (base / 30) * leaves if leaves > 0 else 0
            net = gross - tax - leave_deduction

            tree.insert("", "end", values=(
                record['employee_id'],
                record['employee_name'],
                leaves,
                f"₹{base:,.2f}",
                f"₹{hra:,.2f}",
                f"₹{da:,.2f}",
                f"₹{bonus:,.2f}",
                f"₹{gross:,.2f}",
                f"₹{tax:,.2f}",
                f"₹{net:,.2f}"
            ))

        # Action buttons
        btn_frame = ttk.Frame(preview_window)
        btn_frame.pack(pady=10)

        def on_confirm():
            try:
                # Generate actual payroll
                payment_date = datetime.now().date().isoformat()

                for emp in estimated_data:
                    # Convert all values to float for calculations
                    base = float(emp['gross_salary'])
                    hra = float(emp['hra'])
                    da = float(emp['da'])
                    bonus = float(emp['bonus'])
                    leaves = int(emp['leaves'])

                    gross = base + hra + da + bonus
                    tax = gross * 0.1
                    leave_deduction = (base / 30) * leaves if leaves > 0 else 0
                    net = gross - tax - leave_deduction

                    self.cursor.execute("""
                        INSERT INTO payroll (
                            employee_id, employee_name, leaves, deducted_salary, 
                            bonus, income_tax, final_pay, payment_date
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        emp['employee_id'],
                        emp['employee_name'],
                        leaves,
                        leave_deduction,
                        bonus,
                        tax,
                        net,
                        payment_date
                    ))

                self.connection.commit()
                messagebox.showinfo("Success", "Payroll generated successfully!")
                preview_window.destroy()
                self.refresh_payroll_list()

            except sqlite3.Error as err:
                messagebox.showerror("Database Error", f"Failed to generate payroll:\n{err}")

        confirm_btn = ttk.Button(btn_frame, text="Confirm and Generate",
                                 style="Success.TButton", command=on_confirm)
        confirm_btn.pack(side="left", padx=10)

        cancel_btn = ttk.Button(btn_frame, text="Cancel",
                                style="Danger.TButton", command=preview_window.destroy)
        cancel_btn.pack(side="left", padx=10)

    def show_leave_management(self):
        # Clear previous content
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Header and controls
        header = ttk.Frame(self.content_frame, style="TFrame")
        header.pack(fill="x", pady=(0, 20))

        ttk.Label(header, text="Leave Management", style="Header.TLabel").pack(side="left")

        # Action buttons
        actions_frame = ttk.Frame(header, style="TFrame")
        actions_frame.pack(side="right")

        apply_btn = ttk.Button(actions_frame, text="➕ Apply Leave", style="Success.TButton",
                               command=self.apply_leave)
        apply_btn.pack(side="left", padx=5)

        refresh_btn = ttk.Button(actions_frame, text="🔄 Refresh", style="Primary.TButton",
                                 command=self.refresh_leave_list)
        refresh_btn.pack(side="left")

        # Leave list
        list_frame = ttk.Frame(self.content_frame, style="TFrame")
        list_frame.pack(fill="both", expand=True)

        # Create treeview with scrollbars
        tree_scroll = ttk.Frame(list_frame)
        tree_scroll.pack(fill="both", expand=True)

        vsb = ttk.Scrollbar(tree_scroll, orient="vertical")
        hsb = ttk.Scrollbar(tree_scroll, orient="horizontal")

        columns = ("Leave ID", "Employee", "From", "To", "Days", "Reason", "Status")
        self.leave_tree = ttk.Treeview(tree_scroll, columns=columns, show="headings",
                                       yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        vsb.config(command=self.leave_tree.yview)
        hsb.config(command=self.leave_tree.xview)

        self.leave_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        # Configure columns
        col_widths = {
            "Leave ID": 80, "Employee": 150, "From": 100,
            "To": 100, "Days": 60, "Reason": 200, "Status": 100
        }

        for col in columns:
            self.leave_tree.heading(col, text=col)
            self.leave_tree.column(col, width=col_widths.get(col, 100), anchor="center")

        # Initial data load
        self.refresh_leave_list()

    def refresh_leave_list(self):
        self.cursor.execute("""
            SELECT l.leave_id, e.first_name, e.last_name, l.date_from, l.date_to, 
                   l.leaves, l.reason, l.current_leaves
            FROM leave_register l
            JOIN employees e ON l.employee_id = e.employee_id
            ORDER BY l.date_from DESC
        """)
        leaves = self.cursor.fetchall()

        # Clear existing data
        for item in self.leave_tree.get_children():
            self.leave_tree.delete(item)

        # Add new data
        for leave in leaves:
            status = "Approved" if leave['leaves'] == leave['current_leaves'] else "Pending"
            self.leave_tree.insert("", "end", values=(
                leave['leave_id'],
                f"{leave['first_name']} {leave['last_name']}",
                leave['date_from'],
                leave['date_to'],
                leave['leaves'],
                leave['reason'][:50] + "..." if leave['reason'] and len(leave['reason']) > 50 else leave['reason'],
                status
            ))

    def apply_leave(self):
        apply_window = tk.Toplevel(self.root)
        apply_window.title("Apply for Leave")
        apply_window.geometry("500x400")
        apply_window.configure(bg=self.light_bg)

        # Employee selection
        employee_frame = ttk.Frame(apply_window, style="TFrame")
        employee_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(employee_frame, text="Employee").pack(side="left")
        employee_var = tk.StringVar()

        self.cursor.execute("SELECT employee_id, first_name || ' ' || last_name AS name FROM employees")
        employees = {row['name']: row['employee_id'] for row in self.cursor.fetchall()}

        employee_dropdown = ttk.Combobox(employee_frame, textvariable=employee_var,
                                         values=list(employees.keys()))
        employee_dropdown.pack(side="right", expand=True, fill="x")

        # Leave dates
        date_frame = ttk.Frame(apply_window, style="TFrame")
        date_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(date_frame, text="From Date (YYYY-MM-DD)").pack(side="left")
        from_date_entry = ttk.Entry(date_frame)
        from_date_entry.pack(side="right", expand=True, fill="x")

        to_date_frame = ttk.Frame(apply_window, style="TFrame")
        to_date_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(to_date_frame, text="To Date (YYYY-MM-DD)").pack(side="left")
        to_date_entry = ttk.Entry(to_date_frame)
        to_date_entry.pack(side="right", expand=True, fill="x")

        # Reason
        reason_frame = ttk.Frame(apply_window, style="TFrame")
        reason_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(reason_frame, text="Reason").pack(side="left")
        reason_entry = ttk.Entry(reason_frame)
        reason_entry.pack(side="right", expand=True, fill="x")

        # Submit button
        def submit_leave():
            try:
                employee_name = employee_var.get()
                if not employee_name or employee_name not in employees:
                    messagebox.showerror("Error", "Please select a valid employee")
                    return

                from_date = from_date_entry.get()
                to_date = to_date_entry.get()
                reason = reason_entry.get()

                if not all([from_date, to_date, reason]):
                    messagebox.showerror("Error", "All fields are required")
                    return

                # Calculate number of leave days
                from_date_dt = datetime.strptime(from_date, "%Y-%m-%d").date()
                to_date_dt = datetime.strptime(to_date, "%Y-%m-%d").date()
                leave_days = (to_date_dt - from_date_dt).days + 1

                # Insert leave application
                self.cursor.execute("""
                    INSERT INTO leave_register (
                        employee_id, employee_name, date_from, date_to, 
                        reason, leaves, current_leaves
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    employees[employee_name],
                    employee_name,
                    from_date,
                    to_date,
                    reason,
                    leave_days,
                    leave_days  # Initially current_leaves = total leaves
                ))

                self.connection.commit()
                messagebox.showinfo("Success", "Leave application submitted successfully")
                apply_window.destroy()
                self.refresh_leave_list()

            except ValueError:
                messagebox.showerror("Error", "Please enter dates in YYYY-MM-DD format")
            except sqlite3.Error as err:
                messagebox.showerror("Database Error", f"Failed to submit leave:\n{err}")

        submit_btn = ttk.Button(apply_window, text="Submit Leave Application",
                                style="Success.TButton", command=submit_leave)
        submit_btn.pack(pady=20)

    def show_reports(self):
        # Clear previous content
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Header
        ttk.Label(self.content_frame, text="Reports", style="Header.TLabel").pack(anchor="w", pady=(0, 20))

        # Report options
        report_frame = ttk.Frame(self.content_frame, style="TFrame")
        report_frame.pack(fill="both", expand=True)

        # Monthly payroll report
        payroll_report_btn = ttk.Button(report_frame, text="📊 Monthly Payroll Report",
                                        style="Primary.TButton",
                                        command=self.generate_payroll_report)
        payroll_report_btn.pack(fill="x", pady=5)

        # Employee leave report
        leave_report_btn = ttk.Button(report_frame, text="📅 Employee Leave Report",
                                      style="Primary.TButton",
                                      command=self.generate_leave_report)
        leave_report_btn.pack(fill="x", pady=5)

        # Tax deduction report
        tax_report_btn = ttk.Button(report_frame, text="💰 Tax Deduction Report",
                                    style="Primary.TButton",
                                    command=self.generate_tax_report)
        tax_report_btn.pack(fill="x", pady=5)

    def generate_payroll_report(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf",
                                                 filetypes=[("PDF files", "*.pdf")])
        if not file_path:
            return

        # In a real application, you would generate an actual report here
        # This is just a placeholder implementation
        messagebox.showinfo("Info", f"Payroll report would be generated and saved to {file_path}")

    def generate_leave_report(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf",
                                                 filetypes=[("PDF files", "*.pdf")])
        if not file_path:
            return

        # In a real application, you would generate an actual report here
        messagebox.showinfo("Info", f"Leave report would be generated and saved to {file_path}")

    def generate_tax_report(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf",
                                                 filetypes=[("PDF files", "*.pdf")])
        if not file_path:
            return

        # In a real application, you would generate an actual report here
        messagebox.showinfo("Info", f"Tax report would be generated and saved to {file_path}")

    def show_settings(self):
        # Clear previous content
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Header
        ttk.Label(self.content_frame, text="System Settings", style="Header.TLabel").pack(anchor="w", pady=(0, 20))

        # Settings form
        settings_frame = ttk.Frame(self.content_frame, style="TFrame")
        settings_frame.pack(fill="both", expand=True)

        # Company name
        ttk.Label(settings_frame, text="Company Name:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        company_entry = ttk.Entry(settings_frame)
        company_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        # Payroll day
        ttk.Label(settings_frame, text="Payroll Day:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        payroll_day_entry = ttk.Entry(settings_frame)
        payroll_day_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        # Save button
        def save_settings():
            # In a real application, you would save these settings to database
            messagebox.showinfo("Success", "Settings saved successfully")

        save_btn = ttk.Button(settings_frame, text="Save Settings", style="Success.TButton",
                              command=save_settings)
        save_btn.grid(row=2, column=0, columnspan=2, pady=20)


# Initialize and run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = PayrollSystem(root)
    root.mainloop()