from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFrame, QGridLayout, QTabWidget, QScrollArea,
    QMessageBox, QSplitter, QGroupBox, QDialog
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QPixmap, QFont
import os
import sys

class ReportsDashboard(QMainWindow):
    def __init__(self, user=None):
        super().__init__()
        self.user = user
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Tableau de bord des rapports")
        self.resize(1200, 800)
        
        # Create central widget with main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Create header section
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #24786d;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        header_layout = QHBoxLayout(header_frame)
        
        # Add header title
        header_title = QLabel("Rapports et Analyses")
        header_title.setStyleSheet("""
            color: white;
            font-size: 24px;
            font-weight: bold;
        """)
        header_layout.addWidget(header_title)
        
        # Add back button
        back_button = QPushButton("Retour au tableau de bord")
        back_button.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #24786d;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
        """)
        back_button.clicked.connect(self.close)
        header_layout.addWidget(back_button)
        
        main_layout.addWidget(header_frame)
        
        # Create tabbed interface
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #cccccc;
                border-radius: 5px;
                padding: 10px;
            }
            QTabBar::tab {
                background-color: #f0f0f0;
                border: 1px solid #cccccc;
                border-bottom: none;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                min-width: 100px;
                padding: 8px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 1px solid white;
            }
        """)
        
        # Add tabs for different report categories
        self.create_sales_tab()
        self.create_inventory_tab()
        self.create_financial_tab()
        self.create_customer_tab()
        
        main_layout.addWidget(self.tabs)
    
    def create_sales_tab(self):
        """Create the sales reports tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Quick stats section
        stats_group = QGroupBox("Aperçu des ventes")
        stats_layout = QHBoxLayout()
        
        # Current day total
        day_box = self.create_stat_box("Ventes aujourd'hui", "...MAD", "calendar-day", "#4e73df")
        # Update with actual data
        self.update_day_sales(day_box)
        
        # Current month total
        month_box = self.create_stat_box("Ventes ce mois", "...MAD", "calendar", "#1cc88a")
        # Update with actual data
        self.update_month_sales(month_box)
        
        # Total items sold today
        items_box = self.create_stat_box("Articles vendus aujourd'hui", "...", "shopping-cart", "#36b9cc")
        # Update with actual data
        self.update_items_sold(items_box)
        
        stats_layout.addWidget(day_box)
        stats_layout.addWidget(month_box)
        stats_layout.addWidget(items_box)
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # Sales reports grid
        reports_grid = QGridLayout()
        
        # Daily sales report
        daily_sales_btn = self.create_report_button(
            "Ventes quotidiennes",
            "Rapport détaillé des ventes par jour avec ventilation par produit et méthode de paiement",
            "reports/daily_sales_report.py"
        )
        reports_grid.addWidget(daily_sales_btn, 0, 0)
        
        # Sales by product
        product_sales_btn = self.create_report_button(
            "Ventes par produit",
            "Analyse des performances de vente par produit et variante",
            "reports/sales_products_report.py"
        )
        reports_grid.addWidget(product_sales_btn, 0, 1)
        
        # Sales by customer
        customer_sales_btn = self.create_report_button(
            "Ventes par client",
            "Analyse des achats et habitudes des clients",
            "reports/customer_sales_report.py"
        )
        reports_grid.addWidget(customer_sales_btn, 0, 2)
        
        # Sales by payment method
        payment_sales_btn = self.create_report_button(
            "Méthodes de paiement",
            "Répartition des ventes par moyen de paiement",
            "reports/payment_methods_report.py"
        )
        reports_grid.addWidget(payment_sales_btn, 1, 0)
        
        # Sales discounts
        discounts_btn = self.create_report_button(
            "Remises",
            "Analyse des remises accordées et impact sur les ventes",
            "reports/discounts_report.py"
        )
        reports_grid.addWidget(discounts_btn, 1, 1)
        
        # Sales by user
        user_sales_btn = self.create_report_button(
            "Ventes par utilisateur",
            "Performance de vente par utilisateur/vendeur",
            "reports/user_sales_report.py"
        )
        reports_grid.addWidget(user_sales_btn, 1, 2)
        
        # Add grid to layout
        layout.addLayout(reports_grid)
        
        # Document templates section
        documents_group = QGroupBox("Documents")
        documents_layout = QHBoxLayout()
        
        # Invoice button
        invoice_btn = QPushButton("Facture")
        invoice_btn.setIcon(QIcon.fromTheme("document"))
        invoice_btn.clicked.connect(lambda: self.open_report("reports/invoice.py"))
        documents_layout.addWidget(invoice_btn)
        
        # Receipt button
        receipt_btn = QPushButton("Reçu")
        receipt_btn.setIcon(QIcon.fromTheme("document"))
        receipt_btn.clicked.connect(lambda: self.open_report("reports/receipt.py"))
        documents_layout.addWidget(receipt_btn)
        
        # Z-Report button
        zreport_btn = QPushButton("Rapport Z")
        zreport_btn.setIcon(QIcon.fromTheme("document"))
        zreport_btn.clicked.connect(lambda: self.open_report("reports/zreport.py"))
        documents_layout.addWidget(zreport_btn)
        
        documents_group.setLayout(documents_layout)
        layout.addWidget(documents_group)
        
        # Add tab
        self.tabs.addTab(tab, "Ventes")
    
    def create_inventory_tab(self):
        """Create the inventory reports tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Inventory stats section
        stats_group = QGroupBox("Aperçu du stock")
        stats_layout = QHBoxLayout()
        
        # Total products
        products_box = self.create_stat_box("Total produits", "...", "boxes", "#fd7e14")
        # Update with actual data
        self.update_product_count(products_box)
        
        # Low stock items
        low_stock_box = self.create_stat_box("Stock faible", "...", "exclamation-triangle", "#e74a3b")
        # Update with actual data
        self.update_low_stock_count(low_stock_box)
        
        # Inventory value
        value_box = self.create_stat_box("Valeur du stock", "...MAD", "dollar-sign", "#1cc88a")
        # Update with actual data
        self.update_inventory_value(value_box)
        
        stats_layout.addWidget(products_box)
        stats_layout.addWidget(low_stock_box)
        stats_layout.addWidget(value_box)
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # Inventory reports grid
        reports_grid = QGridLayout()
        
        # Stock movement report
        stock_movement_btn = self.create_report_button(
            "Mouvements de stock",
            "Suivi des entrées et sorties d'inventaire",
            "reports/stock_movement_report.py"
        )
        reports_grid.addWidget(stock_movement_btn, 0, 0)
        
        # Inventory count report
        inventory_count_btn = self.create_report_button(
            "État du stock",
            "Inventaire complet avec niveaux de stock actuels",
            "reports/inventory_count_report.py"
        )
        reports_grid.addWidget(inventory_count_btn, 0, 1)
        
        # Loss and damage report
        loss_damage_btn = self.create_report_button(
            "Pertes et dommages",
            "Suivi des pertes et dommages affectant le stock",
            "reports/loss_damage_report.py"
        )
        reports_grid.addWidget(loss_damage_btn, 0, 2)
        
        # Stock history
        stock_history_btn = self.create_report_button(
            "Historique de stock",
            "Évolution des niveaux de stock dans le temps",
            "reports/stock_history_report.py"
        )
        reports_grid.addWidget(stock_history_btn, 1, 0)
        
        # Stock return report
        stock_return_btn = self.create_report_button(
            "Retours",
            "Analyse des retours de marchandises",
            "reports/stock_return_report.py"
        )
        reports_grid.addWidget(stock_return_btn, 1, 1)
        
        # Stock value report
        stock_value_btn = self.create_report_button(
            "Valeur d'inventaire",
            "Analyse détaillée de la valeur du stock",
            "reports/stock_value_report.py"
        )
        reports_grid.addWidget(stock_value_btn, 1, 2)
        
        # Add grid to layout
        layout.addLayout(reports_grid)
        
        # Add tab
        self.tabs.addTab(tab, "Inventaire")
    
    def create_financial_tab(self):
        """Create the financial reports tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Financial stats section
        stats_group = QGroupBox("Aperçu financier")
        stats_layout = QHBoxLayout()
        
        # Profit margin
        margin_box = self.create_stat_box("Marge brute", "...%", "chart-line", "#4e73df")
        # Update with actual data
        self.update_profit_margin(margin_box)
        
        # Revenue this month
        revenue_box = self.create_stat_box("CA du mois", "...MAD", "money-bill", "#1cc88a")
        # Update with actual data
        self.update_monthly_revenue(revenue_box)
        
        # Average transaction value
        avg_box = self.create_stat_box("Panier moyen", "...MAD", "shopping-basket", "#f6c23e")
        # Update with actual data
        self.update_avg_transaction(avg_box)
        
        stats_layout.addWidget(margin_box)
        stats_layout.addWidget(revenue_box)
        stats_layout.addWidget(avg_box)
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # Financial reports grid
        reports_grid = QGridLayout()
        
        # Profit margin report
        profit_margin_btn = self.create_report_button(
            "Marge bénéficiaire",
            "Analyse détaillée des marges par produit et catégorie",
            "reports/profit_margin_report.py"
        )
        reports_grid.addWidget(profit_margin_btn, 0, 0)
        
        # Sales discounts report
        discounts_btn = self.create_report_button(
            "Remises accordées",
            "Impact des remises sur le chiffre d'affaires",
            "reports/sales_discounts_report.py"
        )
        reports_grid.addWidget(discounts_btn, 0, 1)
        
        # Purchase invoice list
        purchase_invoice_btn = self.create_report_button(
            "Factures d'achat",
            "Liste des factures fournisseurs",
            "reports/purchase_invoice_report.py"
        )
        reports_grid.addWidget(purchase_invoice_btn, 0, 2)
        
        # Sales invoice list
        sales_invoice_btn = self.create_report_button(
            "Factures de vente",
            "Liste des factures clients",
            "reports/sales_invoice_report.py"
        )
        reports_grid.addWidget(sales_invoice_btn, 1, 0)
        
        # Purchase supplier report
        supplier_btn = self.create_report_button(
            "Fournisseurs",
            "Analyse des achats par fournisseur",
            "reports/purchase_supplier_report.py"
        )
        reports_grid.addWidget(supplier_btn, 1, 1)
        
        # Cash flow report
        cash_flow_btn = self.create_report_button(
            "Caisse",
            "Mouvements de trésorerie et état de la caisse",
            "reports/cash_flow_report.py"
        )
        reports_grid.addWidget(cash_flow_btn, 1, 2)
        
        # Add grid to layout
        layout.addLayout(reports_grid)
        
        # Add tab
        self.tabs.addTab(tab, "Finances")
    
    def create_customer_tab(self):
        """Create the customer reports tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Customer stats section
        stats_group = QGroupBox("Aperçu clients")
        stats_layout = QHBoxLayout()
        
        # Total customers
        customers_box = self.create_stat_box("Total clients", "...", "users", "#4e73df")
        # Update with actual data
        self.update_customer_count(customers_box)
        
        # Average value per customer
        avg_customer_box = self.create_stat_box("Valeur moyenne", "...MAD", "user-tag", "#1cc88a")
        # Update with actual data
        self.update_avg_customer_value(avg_customer_box)
        
        # Top customer value
        top_customer_box = self.create_stat_box("Client principal", "...MAD", "crown", "#f6c23e")
        # Update with actual data
        self.update_top_customer_value(top_customer_box)
        
        stats_layout.addWidget(customers_box)
        stats_layout.addWidget(avg_customer_box)
        stats_layout.addWidget(top_customer_box)
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # Customer reports grid
        reports_grid = QGridLayout()
        
        # Sales by customer
        customer_sales_btn = self.create_report_button(
            "Ventes par client",
            "Analyse des ventes par client",
            "reports/customer_sales_report.py"
        )
        reports_grid.addWidget(customer_sales_btn, 0, 0)
        
        # Customer payment types
        payment_types_btn = self.create_report_button(
            "Moyens de paiement des clients",
            "Préférences de paiement par client",
            "reports/customer_payment_report.py"
        )
        reports_grid.addWidget(payment_types_btn, 0, 1)
        
        # Customer discounts
        customer_discount_btn = self.create_report_button(
            "Remises par client",
            "Analyse des remises accordées aux clients",
            "reports/customer_discount_report.py"
        )
        reports_grid.addWidget(customer_discount_btn, 0, 2)
        
        # Add grid to layout
        layout.addLayout(reports_grid)
        
        # Add tab
        self.tabs.addTab(tab, "Clients")
    
    def create_stat_box(self, title, value, icon=None, color="#4e73df"):
        """Create a statistics box for the dashboard"""
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 8px;
                padding: 15px;
                min-height: 120px;
            }}
        """)
        
        layout = QHBoxLayout(frame)
        
        # Value section
        value_layout = QVBoxLayout()
        value_layout.setAlignment(Qt.AlignLeft)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.8);
            font-size: 14px;
        """)
        
        # Value
        value_label = QLabel(value)
        value_label.setStyleSheet("""
            color: white;
            font-size: 24px;
            font-weight: bold;
        """)
        
        value_layout.addWidget(title_label)
        value_layout.addWidget(value_label)
        layout.addLayout(value_layout)
        
        # Icon (placeholder for now)
        icon_label = QLabel()
        icon_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.5);
            font-size: 36px;
        """)
        icon_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(icon_label)
        
        # Store reference to value label for updates
        frame.value_label = value_label
        
        return frame
    
    def create_report_button(self, title, description, report_path):
        """Create a button for opening a report"""
        btn = QPushButton()
        btn.setMinimumHeight(100)
        
        # Create layout for button content
        content_layout = QVBoxLayout(btn)
        content_layout.setAlignment(Qt.AlignLeft)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #333;
        """)
        
        # Description
        desc_label = QLabel(description)
        desc_label.setStyleSheet("""
            font-size: 12px;
            color: #666;
        """)
        desc_label.setWordWrap(True)
        
        content_layout.addWidget(title_label)
        content_layout.addWidget(desc_label)
        
        # Set button style
        btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                text-align: left;
                padding: 15px;
            }
            QPushButton:hover {
                background-color: #f8f9fa;
                border: 1px solid #bbb;
            }
        """)
        
        # Connect to report open method
        btn.clicked.connect(lambda: self.open_report(report_path))
        
        return btn
    
    def open_report(self, report_path):
        """Open a specific report window"""
        try:
            # Attempt to dynamically import the report class
            import importlib
            
            # Convert path to module format (replace .py with empty string and / with .)
            module_path = report_path.replace('.py', '').replace('/', '.')
            
            # Import the module
            module = importlib.import_module(f"ui.{module_path}")
            
            # Get the class name from the module name
            class_name = ''.join(word.capitalize() for word in module_path.split('.')[-1].split('_'))
            
            # Get the class from the module
            report_class = getattr(module, class_name)
            
            # Create an instance of the report class
            report_window = report_class(self.user)
            
            # Show the report window
            report_window.show()
            
        except ImportError as e:
            QMessageBox.warning(
                self,
                "Rapport non disponible",
                f"Ce rapport n'est pas encore disponible.\nErreur: {str(e)}"
            )
        except Exception as e:
            QMessageBox.warning(
                self,
                "Erreur",
                f"Erreur lors de l'ouverture du rapport: {str(e)}"
            )
    
    # Methods to update statistics boxes with real data
    def update_day_sales(self, stat_box):
        try:
            from models.sales_report import SalesReport
            import datetime
            
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            report_data = SalesReport.get_daily_sales(today)
            
            if report_data and 'summary' in report_data:
                total_sales = report_data['summary'].get('total_sales', 0) or 0
                stat_box.value_label.setText(f"{total_sales:.2f} MAD")
            else:
                stat_box.value_label.setText("0.00 MAD")
        except Exception as e:
            print(f"Error updating day sales: {e}")
            stat_box.value_label.setText("Erreur")
    
    def update_month_sales(self, stat_box):
        try:
            from models.sales_report import SalesReport
            import datetime
            
            today = datetime.datetime.now()
            first_day = datetime.datetime(today.year, today.month, 1).strftime("%Y-%m-%d")
            last_day = today.strftime("%Y-%m-%d")
            
            report_data = SalesReport.get_sales_range(first_day, last_day)
            
            if report_data and 'summary' in report_data:
                total_sales = report_data['summary'].get('total_sales', 0) or 0
                stat_box.value_label.setText(f"{total_sales:.2f} MAD")
            else:
                stat_box.value_label.setText("0.00 MAD")
        except Exception as e:
            print(f"Error updating month sales: {e}")
            stat_box.value_label.setText("Erreur")
    
    def update_items_sold(self, stat_box):
        try:
            from models.sales_report import SalesReport
            import datetime
            
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            report_data = SalesReport.get_daily_sales(today)
            
            if report_data and 'top_products' in report_data:
                total_items = sum(p.get('quantity_sold', 0) or 0 for p in report_data['top_products'])
                stat_box.value_label.setText(str(total_items))
            else:
                stat_box.value_label.setText("0")
        except Exception as e:
            print(f"Error updating items sold: {e}")
            stat_box.value_label.setText("Erreur")
    
    def update_product_count(self, stat_box):
        try:
            from models.product import Product
            
            products = Product.get_all_products()
            stat_box.value_label.setText(str(len(products)))
        except Exception as e:
            print(f"Error updating product count: {e}")
            stat_box.value_label.setText("Erreur")
    
    def update_low_stock_count(self, stat_box):
        try:
            from models.sales_report import SalesReport
            
            report_data = SalesReport.get_inventory_report()
            
            if report_data and 'summary' in report_data:
                low_stock = report_data['summary'].get('low_stock_products', 0) or 0
                stat_box.value_label.setText(str(low_stock))
            else:
                stat_box.value_label.setText("0")
        except Exception as e:
            print(f"Error updating low stock count: {e}")
            stat_box.value_label.setText("Erreur")
    
    def update_inventory_value(self, stat_box):
        try:
            from models.sales_report import SalesReport
            
            report_data = SalesReport.get_inventory_report()
            
            if report_data and 'summary' in report_data:
                stock_value = report_data['summary'].get('total_stock_value', 0) or 0
                stat_box.value_label.setText(f"{stock_value:.2f} MAD")
            else:
                stat_box.value_label.setText("0.00 MAD")
        except Exception as e:
            print(f"Error updating inventory value: {e}")
            stat_box.value_label.setText("Erreur")
    
    def update_profit_margin(self, stat_box):
        try:
            from models.sales_report import SalesReport
            import datetime
            
            # Get last 30 days report
            today = datetime.datetime.now()
            start_date = (today - datetime.timedelta(days=30)).strftime("%Y-%m-%d")
            end_date = today.strftime("%Y-%m-%d")
            
            report_data = SalesReport.get_profit_margin_report(start_date, end_date)
            
            if report_data and 'summary' in report_data:
                margin = report_data['summary'].get('margin_percentage', 0) or 0
                stat_box.value_label.setText(f"{margin:.2f}%")
            else:
                stat_box.value_label.setText("0.00%")
        except Exception as e:
            print(f"Error updating profit margin: {e}")
            stat_box.value_label.setText("Erreur")
    
    def update_monthly_revenue(self, stat_box):
        try:
            from models.sales_report import SalesReport
            import datetime
            
            today = datetime.datetime.now()
            first_day = datetime.datetime(today.year, today.month, 1).strftime("%Y-%m-%d")
            last_day = today.strftime("%Y-%m-%d")
            
            report_data = SalesReport.get_sales_range(first_day, last_day)
            
            if report_data and 'summary' in report_data:
                total_sales = report_data['summary'].get('total_sales', 0) or 0
                stat_box.value_label.setText(f"{total_sales:.2f} MAD")
            else:
                stat_box.value_label.setText("0.00 MAD")
        except Exception as e:
            print(f"Error updating monthly revenue: {e}")
            stat_box.value_label.setText("Erreur")
    
    def update_avg_transaction(self, stat_box):
        try:
            from models.sales_report import SalesReport
            import datetime
            
            today = datetime.datetime.now()
            start_date = (today - datetime.timedelta(days=30)).strftime("%Y-%m-%d")
            end_date = today.strftime("%Y-%m-%d")
            
            report_data = SalesReport.get_sales_range(start_date, end_date)
            
            if report_data and 'summary' in report_data:
                avg_sale = report_data['summary'].get('average_sale', 0) or 0
                stat_box.value_label.setText(f"{avg_sale:.2f} MAD")
            else:
                stat_box.value_label.setText("0.00 MAD")
        except Exception as e:
            print(f"Error updating average transaction: {e}")
            stat_box.value_label.setText("Erreur")
    
    def update_customer_count(self, stat_box):
        try:
            from models.sales_report import SalesReport
            import datetime
            
            today = datetime.datetime.now()
            report_data = SalesReport.get_customer_sales_report()
            
            if report_data and 'summary' in report_data:
                customer_count = report_data['summary'].get('total_customers', 0) or 0
                stat_box.value_label.setText(str(customer_count))
            else:
                stat_box.value_label.setText("0")
        except Exception as e:
            print(f"Error updating customer count: {e}")
            stat_box.value_label.setText("Erreur")
    
    def update_avg_customer_value(self, stat_box):
        try:
            from models.sales_report import SalesReport
            import datetime
            
            report_data = SalesReport.get_customer_sales_report()
            
            if report_data and 'summary' in report_data:
                avg_value = report_data['summary'].get('average_per_customer', 0) or 0
                stat_box.value_label.setText(f"{avg_value:.2f} MAD")
            else:
                stat_box.value_label.setText("0.00 MAD")
        except Exception as e:
            print(f"Error updating average customer value: {e}")
            stat_box.value_label.setText("Erreur")
    
    def update_top_customer_value(self, stat_box):
        try:
            from models.sales_report import SalesReport
            
            report_data = SalesReport.get_customer_sales_report()
            
            if report_data and 'customers' in report_data and report_data['customers']:
                # Sort customers by total_spent and get the highest
                top_customer = max(report_data['customers'], key=lambda x: x.get('total_spent', 0) or 0)
                top_value = top_customer.get('total_spent', 0) or 0
                stat_box.value_label.setText(f"{top_value:.2f} MAD")
            else:
                stat_box.value_label.setText("0.00 MAD")
        except Exception as e:
            print(f"Error updating top customer value: {e}")
            stat_box.value_label.setText("Erreur")
