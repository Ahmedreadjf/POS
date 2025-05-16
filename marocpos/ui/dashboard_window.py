from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QWidget, QGridLayout, QFrame, QSizePolicy, QSpacerItem
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QPixmap, QFont, QColor
import os

class DashboardWindow(QMainWindow):
    def __init__(self, user=None):
        super().__init__()
        self.user = user
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("MarocPOS - Tableau de bord")
        self.setMinimumSize(1200, 800)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Create header section
        header_layout = QHBoxLayout()
        logo_label = QLabel()
        logo_path = os.path.join(os.path.dirname(__file__), '..', 'logo.png')
        if os.path.exists(logo_path):
            logo_pixmap = QPixmap(logo_path).scaled(QSize(150, 70), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(logo_pixmap)
        else:
            logo_label.setText("MarocPOS")
            logo_label.setStyleSheet("font-size: 24pt; font-weight: bold; color: #24786d;")
            
        header_layout.addWidget(logo_label)
        
        # Add welcome message with user name
        welcome_msg = "Bienvenue, "
        if self.user and hasattr(self.user, 'full_name') and self.user.full_name:
            welcome_msg += self.user.full_name
        elif self.user and hasattr(self.user, 'username') and self.user.username:
            welcome_msg += self.user.username
        else:
            welcome_msg += "Utilisateur"
            
        welcome_label = QLabel(welcome_msg)
        welcome_label.setStyleSheet("font-size: 18pt; color: #333;")
        welcome_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        header_layout.addWidget(welcome_label)
        
        main_layout.addLayout(header_layout)
        
        # Create quick stats section
        stats_frame = QFrame()
        stats_frame.setFrameShape(QFrame.StyledPanel)
        stats_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        
        stats_layout = QHBoxLayout(stats_frame)
        
        # Add quick stat boxes
        stats_layout.addWidget(self.create_stat_box("Chiffre d'affaires aujourd'hui", self.get_sales_today(), "#28a745"))
        stats_layout.addWidget(self.create_stat_box("Transactions aujourd'hui", self.get_transactions_today(), "#007bff"))
        stats_layout.addWidget(self.create_stat_box("Panier moyen", self.get_avg_transaction(), "#fd7e14"))
        stats_layout.addWidget(self.create_stat_box("Produits stocks faibles", self.get_low_stock_count(), "#dc3545"))
        
        main_layout.addWidget(stats_frame)
        
        # Create main menu grid
        menu_layout = QGridLayout()
        menu_layout.setSpacing(15)
        
        # Create and add menu cards
        menu_layout.addWidget(self.create_menu_card("Ventes", "images/sales.png", self.open_sales), 0, 0)
        menu_layout.addWidget(self.create_menu_card("Produits", "images/products.png", self.open_products), 0, 1)
        menu_layout.addWidget(self.create_menu_card("Clients", "images/customers.png", self.open_customers), 0, 2)
        menu_layout.addWidget(self.create_menu_card("Rapports", "images/reports.png", self.open_reports), 1, 0)
        menu_layout.addWidget(self.create_menu_card("Utilisateurs", "images/users.png", self.open_users), 1, 1)
        menu_layout.addWidget(self.create_menu_card("Paramètres", "images/settings.png", self.open_settings), 1, 2)
        
        main_layout.addLayout(menu_layout)
        
        # Add a logout button
        logout_button = QPushButton("Déconnexion")
        logout_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 14pt;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        logout_button.clicked.connect(self.logout)
        
        # Add spacer and logout button
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        bottom_layout.addWidget(logout_button)
        
        main_layout.addLayout(bottom_layout)
        
    def create_stat_box(self, title, value, color):
        """Create a statistics box"""
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 8px;
                padding: 15px;
            }}
        """)
        
        layout = QVBoxLayout(frame)
        
        # Title label
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.8);
            font-size: 14px;
        """)
        
        # Value label
        value_label = QLabel(value)
        value_label.setStyleSheet("""
            color: white;
            font-size: 24px;
            font-weight: bold;
        """)
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addStretch()
        
        return frame
        
    def create_menu_card(self, title, icon_path, callback):
        """Create a menu card button"""
        card = QPushButton()
        card.setMinimumSize(320, 180)
        card.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 10px;
                text-align: left;
                padding: 20px;
            }
            QPushButton:hover {
                background-color: #f8f9fa;
                border: 1px solid #24786d;
            }
        """)
        
        # Create layout for the card
        layout = QVBoxLayout(card)
        
        # Add icon if exists
        if os.path.exists(icon_path):
            icon_label = QLabel()
            icon_pixmap = QPixmap(icon_path).scaled(QSize(64, 64), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon_label.setPixmap(icon_pixmap)
            layout.addWidget(icon_label)
        
        # Add title
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 18pt; color: #24786d; font-weight: bold;")
        
        layout.addWidget(title_label)
        layout.addStretch()
        
        # Connect callback
        card.clicked.connect(callback)
        
        return card
    
    # Methods to retrieve stat values
    def get_sales_today(self):
        try:
            from models.sales_report import SalesReport
            import datetime
            
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            report_data = SalesReport.get_daily_sales(today)
            
            if report_data and 'summary' in report_data:
                total_sales = report_data['summary'].get('total_sales', 0) or 0
                return f"{total_sales:.2f} MAD"
            else:
                return "0.00 MAD"
        except Exception as e:
            print(f"Error getting today's sales: {e}")
            return "0.00 MAD"
    
    def get_transactions_today(self):
        try:
            from models.sales_report import SalesReport
            import datetime
            
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            report_data = SalesReport.get_daily_sales(today)
            
            if report_data and 'summary' in report_data:
                sale_count = report_data['summary'].get('sale_count', 0) or 0
                return str(sale_count)
            else:
                return "0"
        except Exception as e:
            print(f"Error getting transaction count: {e}")
            return "0"
    
    def get_avg_transaction(self):
        try:
            from models.sales_report import SalesReport
            import datetime
            
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            report_data = SalesReport.get_daily_sales(today)
            
            if report_data and 'summary' in report_data:
                avg_sale = report_data['summary'].get('average_sale', 0) or 0
                return f"{avg_sale:.2f} MAD"
            else:
                return "0.00 MAD"
        except Exception as e:
            print(f"Error getting average transaction: {e}")
            return "0.00 MAD"
    
    def get_low_stock_count(self):
        try:
            from models.sales_report import SalesReport
            
            report_data = SalesReport.get_inventory_report()
            
            if report_data and 'summary' in report_data:
                low_stock = report_data['summary'].get('low_stock_products', 0) or 0
                return str(low_stock)
            else:
                return "0"
        except Exception as e:
            print(f"Error getting low stock count: {e}")
            return "0"
    
    # Menu card callback methods
    def open_sales(self):
        """Open sales window"""
        try:
            from .sales_management_windows import SalesManagementWindow
            self.sales_window = SalesManagementWindow()
            self.sales_window.show()
        except Exception as e:
            print(f"Error opening sales window: {e}")
    
    def open_products(self):
        """Open products window"""
        try:
            from .product_management_window import ProductManagementWindow
            self.products_window = ProductManagementWindow()
            self.products_window.show()
        except Exception as e:
            print(f"Error opening products window: {e}")
    
    def open_customers(self):
        """Open customers window"""
        print("Customers window not implemented yet")
    
    def open_reports(self):
        """Open reports window"""
        try:
            from .reports_dashboard import ReportsDashboard
            self.reports_window = ReportsDashboard(self.user)
            self.reports_window.show()
        except Exception as e:
            print(f"Error opening reports window: {e}")
    
    def open_users(self):
        """Open users window"""
        try:
            from .user_management_window import UserManagementWindow
            self.users_window = UserManagementWindow()
            self.users_window.show()
        except Exception as e:
            print(f"Error opening users window: {e}")
    
    def open_settings(self):
        """Open settings window"""
        try:
            from .settings_window import SettingsWindow
            self.settings_window = SettingsWindow()
            self.settings_window.show()
        except Exception as e:
            print(f"Error opening settings window: {e}")
    
    def logout(self):
        """Logout and close window"""
        self.close()
        
        # Show login window again
        from .login_window import LoginWindow
        from controllers.auth_controller import AuthController
        
        self.login_window = LoginWindow(auth_controller=AuthController())
        self.login_window.show()
