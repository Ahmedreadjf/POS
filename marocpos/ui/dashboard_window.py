from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFrame, QScrollArea, QGridLayout
)
from PyQt5.QtCore import Qt, QDateTime
from models.category import Category
from models.user import User
from controllers.auth_controller import AuthController

# Use lazy imports instead of top-level imports to avoid circular dependencies
# These will be imported when needed in the respective methods
# from ui.user_management_window import UserManagementWindow
# from ui.store_management_windows import StoreManagementWindow
# from ui.sales_management_windows import SalesManagementWindow
# from ui.product_management_window import ProductManagementWindow
# from ui.category_management_window import CategoryManagementWindow

class DashboardWindow(QMainWindow):
    def __init__(self, user=None):
        super().__init__()
        self.user = user
        self.current_datetime = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
        # Track open windows to prevent duplicates and memory leaks
        self.open_windows = {}
        self.init_ui()

    def init_ui(self):
        # Set window properties
        self.setWindowTitle("MarocPOS")
        self.setGeometry(0, 0, 1200, 800)
        self.showMaximized()

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create sidebar
        sidebar = self.create_sidebar()
        main_layout.addWidget(sidebar)

        # Create content area
        content = self.create_content_area()
        main_layout.addWidget(content, stretch=1)

    def create_sidebar(self):
        sidebar = QFrame()
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #1a4c7c;
                min-width: 200px;
                max-width: 200px;
                padding: 10px;
            }
        """)

        layout = QVBoxLayout(sidebar)
        layout.setSpacing(5)

        # Add navigation buttons
        buttons = [
            ("🛒 Vente", self.open_sales_window),
            ("📦 Stock", self.open_product_management),
            ("🏷️ Catégories", self.open_category_management),
            ("👥 Clients", self.open_store_management),
            ("📊 Rapports", lambda: None),
            ("👤 Utilisateurs", self.open_user_management),
            ("⚙️ Paramètres", lambda: None),
            ("🚪 Déconnexion", self.logout)
        ]

        for text, handler in buttons:
            btn = QPushButton(text)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    color: #adb5bd;
                    border: none;
                    text-align: left;
                    padding: 12px;
                    font-size: 16px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: rgba(255,255,255,0.1);
                    color: white;
                }
            """)
            btn.clicked.connect(handler)
            layout.addWidget(btn)

        layout.addStretch()
        return sidebar

    def create_content_area(self):
        content = QWidget()
        content.setStyleSheet("background-color: white;")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header with user info and datetime
        header = QHBoxLayout()
        
        store_label = QLabel("Boutique Casablanca")
        store_label.setStyleSheet("color: #333; font-size: 14px; font-weight: bold;")
        
        username = self.user.get('username', 'MAFPOS') if self.user else 'MAFPOS'
        username_label = QLabel(username)
        username_label.setStyleSheet("color: #6c757d; font-size: 14px;")
        
        datetime_label = QLabel(self.current_datetime)
        datetime_label.setStyleSheet("color: #6c757d; font-size: 14px;")

        header.addWidget(store_label)
        header.addWidget(QLabel(" | "))
        header.addWidget(username_label)
        header.addWidget(QLabel(" | "))
        header.addWidget(datetime_label)
        header.addStretch()

        layout.addLayout(header)

        # Category buttons area
        category_scroll = QScrollArea()
        category_scroll.setWidgetResizable(True)
        category_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        category_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)

        category_widget = QWidget()
        self.category_layout = QGridLayout(category_widget)
        self.category_layout.setSpacing(10)
        
        category_scroll.setWidget(category_widget)
        layout.addWidget(category_scroll)

        # Setup category buttons
        self.setup_category_buttons()

        # Create the embedded sales management window
        self.sales_mgmt_area = QWidget()
        self.sales_mgmt_layout = QVBoxLayout(self.sales_mgmt_area)
        self.sales_mgmt_layout.setContentsMargins(0, 0, 0, 0)
        
        # Initially show sales management
        try:
            # Dynamically import sales management window
            module = __import__('ui.sales_management_windows', fromlist=['SalesManagementWindow'])
            SalesManagementWindow = module.SalesManagementWindow
            
            self.sales_mgmt_window = SalesManagementWindow()
            self.sales_mgmt_layout.addWidget(self.sales_mgmt_window)
            layout.addWidget(self.sales_mgmt_area)
        except Exception as e:
            print(f"Error loading sales management window: {e}")
            # Create a placeholder label if cannot load the sales window
            error_label = QLabel("Could not load sales management")
            error_label.setStyleSheet("color: red; font-size: 16px;")
            self.sales_mgmt_layout.addWidget(error_label)
            layout.addWidget(self.sales_mgmt_area)

        return content

    def setup_category_buttons(self):
        categories = Category.get_all_categories()
        
        # Clear existing buttons
        while self.category_layout.count():
            item = self.category_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Add "Tous" button
        all_btn = QPushButton("Tous")
        all_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        all_btn.clicked.connect(lambda: self.filter_by_category(None))
        self.category_layout.addWidget(all_btn, 0, 0)

        # Add category buttons in a grid
        row = 0
        col = 1
        for category in categories:
            if col > 5:  # Start new row after 6 buttons
                row += 1
                col = 0

            btn = QPushButton(category[1])  # category name
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #007bff;
                    color: white;
                    border: none;
                    padding: 10px;
                    border-radius: 5px;
                    min-width: 100px;
                }
                QPushButton:hover {
                    background-color: #0056b3;
                }
            """)
            btn.clicked.connect(lambda checked, cat_id=category[0]: self.filter_by_category(cat_id))
            self.category_layout.addWidget(btn, row, col)
            col += 1

    def filter_by_category(self, category_id):
        # Pass the category filter to the sales management window
        if hasattr(self, 'sales_mgmt_window') and self.sales_mgmt_window is not None:
            try:
                # Only call if the method exists
                if hasattr(self.sales_mgmt_window, 'filter_by_category'):
                    self.sales_mgmt_window.filter_by_category(category_id)
            except Exception as e:
                print(f"Error filtering by category: {e}")
        else:
            print("Cannot filter categories: Sales management window not loaded")

    def open_window(self, window_class_name, window_name):
        """Open a window and track it to prevent duplicates."""
        # Check if window is already open
        if window_name in self.open_windows and self.open_windows[window_name].isVisible():
            # Window already exists, just activate it
            self.open_windows[window_name].activateWindow()
            self.open_windows[window_name].raise_()
            return
        
        # Dynamically import the window class to avoid circular dependencies
        module_name = f"ui.{window_class_name}"
        try:
            module = __import__(module_name, fromlist=[''])
            
            # Get the class from the module by converting snake_case to CamelCase
            # Example: product_management_window -> ProductManagementWindow
            words = window_class_name.split('_')
            class_name = ''.join(word.capitalize() for word in words)
            
            # If the filename ends with 's' (windows), make sure class doesn't
            if class_name.endswith('Windows') and window_class_name.endswith('windows'):
                class_name = class_name[:-1]  # Remove the 's' to get singular form
                
            # Try to get the class from the module
            if hasattr(module, class_name):
                window_class = getattr(module, class_name)
            else:
                # Try alternative naming conventions
                alt_class_names = [
                    class_name,                          # ProductManagementWindow
                    class_name.replace('Windows', 'Window'), # SalesManagementWindow
                    window_class_name.title().replace('_', ''), # ProductManagementWindow
                    window_class_name.replace('_windows', 'Windows').replace('_window', 'Window'), # StoreManagementWindow
                ]
                
                for alt_name in alt_class_names:
                    if hasattr(module, alt_name):
                        window_class = getattr(module, alt_name)
                        break
                else:
                    # If we get here, none of the alternatives worked
                    print(f"Could not find a window class in {module_name}. Available classes:")
                    for item in dir(module):
                        if not item.startswith('__'):
                            print(f"  - {item}")
                    raise AttributeError(f"Could not find window class in module")
            
            # Create a new window
            new_window = window_class()
            self.open_windows[window_name] = new_window
            new_window.show()
        except Exception as e:
            print(f"Error opening window {window_name}: {e}")

    def open_sales_window(self):
        """Open the Sales window."""
        try:
            self._directly_open_window('ui.sales_management_windows', 'SalesManagementWindow', 'sales')
        except Exception as e:
            print(f"Error opening sales window: {e}")

    def open_product_management(self):
        """Open the Product Management window."""
        try:
            self._directly_open_window('ui.product_management_window', 'ProductManagementWindow', 'product')
        except Exception as e:
            print(f"Error opening product window: {e}")

    def open_category_management(self):
        """Open the Category Management window."""
        try:
            self._directly_open_window('ui.category_management_window', 'CategoryManagementWindow', 'category')
        except Exception as e:
            print(f"Error opening category window: {e}")

    def open_store_management(self):
        """Open the Store Management window."""
        try:
            self._directly_open_window('ui.store_management_windows', 'StoreManagementWindow', 'store')
        except Exception as e:
            print(f"Error opening store window: {e}")

    def open_user_management(self):
        """Open the User Management window."""
        try:
            self._directly_open_window('ui.user_management_window', 'UserManagementWindow', 'user')
        except Exception as e:
            print(f"Error opening user window: {e}")
            
    def _directly_open_window(self, module_name, class_name, window_key):
        """Open a window by directly specifying module and class name."""
        # Check if window is already open
        if window_key in self.open_windows and self.open_windows[window_key].isVisible():
            # Window already exists, just activate it
            self.open_windows[window_key].activateWindow()
            self.open_windows[window_key].raise_()
            return
            
        try:
            # Import the module
            module = __import__(module_name, fromlist=[class_name])
            
            # Print available classes in module for debugging
            if not hasattr(module, class_name):
                print(f"Available classes in {module_name}:")
                for item in dir(module):
                    if not item.startswith('__'):
                        print(f"  - {item}")
                raise AttributeError(f"Module {module_name} has no attribute {class_name}")
                
            # Get the window class
            window_class = getattr(module, class_name)
            
            # Create a new window
            new_window = window_class()
            self.open_windows[window_key] = new_window
            new_window.show()
        except Exception as e:
            print(f"Error in _directly_open_window: {e}")
            raise
        
    def closeEvent(self, event):
        """Close all child windows when main window is closed."""
        for window in self.open_windows.values():
            if window and window.isVisible():
                window.close()
        event.accept()

    def logout(self):
        """Logout the user and show login window."""
        # Import LoginWindow and create auth controller here to avoid circular imports
        import importlib
        login_module = importlib.import_module('ui.login_window')
        LoginWindow = login_module.LoginWindow
        
        # First close all open windows
        for window in self.open_windows.values():
            if window:
                window.close()
        
        # Create a new login window
        auth_controller = AuthController()
        login_window = LoginWindow(auth_controller=auth_controller)
        login_window.show()
        
        # Close the dashboard
        self.close()