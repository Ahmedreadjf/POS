from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QDateEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QFrame, QGroupBox, QFormLayout, QComboBox, QTabWidget,
    QMessageBox, QFileDialog, QSpinBox
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor, QPainter, QPen, QBrush
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog
from models.sales_report import SalesReport
from datetime import datetime, timedelta
import os
import csv
import json

class ProfitMarginReport(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Rapport de Marge Bénéficiaire")
        
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Date range selection section
        date_frame = QFrame()
        date_frame.setFrameShape(QFrame.StyledPanel)
        date_frame.setStyleSheet("background-color: #f8f9fa; padding: 10px; border-radius: 5px;")
        date_layout = QHBoxLayout(date_frame)
        
        # Set up date range selector
        date_layout.addWidget(QLabel("Du:"))
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addMonths(-1))
        date_layout.addWidget(self.start_date)
        
        date_layout.addWidget(QLabel("Au:"))
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        date_layout.addWidget(self.end_date)
        
        # Period selector
        self.period_combo = QComboBox()
        self.period_combo.addItems([
            "Personnalisé", 
            "Aujourd'hui", 
            "Hier", 
            "7 derniers jours", 
            "30 derniers jours",
            "Ce mois",
            "Mois dernier",
            "Cette année"
        ])
        self.period_combo.currentIndexChanged.connect(self.on_period_changed)
        date_layout.addWidget(QLabel("Période:"))
        date_layout.addWidget(self.period_combo)
        
        # Refresh button
        refresh_btn = QPushButton("Actualiser")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        refresh_btn.clicked.connect(self.load_report)
        date_layout.addWidget(refresh_btn)
        
        # Export buttons
        export_csv_btn = QPushButton("Exporter CSV")
        export_csv_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        export_csv_btn.clicked.connect(self.export_csv)
        date_layout.addWidget(export_csv_btn)
        
        main_layout.addWidget(date_frame)
        
        # Summary section
        summary_group = QGroupBox("Résumé de la marge")
        summary_layout = QHBoxLayout()
        
        # Create summary boxes
        self.revenue_box = self.create_summary_box("Chiffre d'affaires", "0.00 MAD", "#28a745")
        self.cost_box = self.create_summary_box("Coût des ventes", "0.00 MAD", "#dc3545")
        self.profit_box = self.create_summary_box("Bénéfice brut", "0.00 MAD", "#007bff")
        self.margin_box = self.create_summary_box("Marge brute", "0.00%", "#fd7e14")
        
        summary_layout.addWidget(self.revenue_box)
        summary_layout.addWidget(self.cost_box)
        summary_layout.addWidget(self.profit_box)
        summary_layout.addWidget(self.margin_box)
        
        summary_group.setLayout(summary_layout)
        main_layout.addWidget(summary_group)
        
        # Tab widget for detailed views
        self.tabs = QTabWidget()
        
        # Product tab
        self.products_tab = QWidget()
        self.setup_products_tab()
        self.tabs.addTab(self.products_tab, "Marge par Produit")
        
        # Category tab
        self.categories_tab = QWidget()
        self.setup_categories_tab()
        self.tabs.addTab(self.categories_tab, "Marge par Catégorie")
        
        # Monthly tab
        self.monthly_tab = QWidget()
        self.setup_monthly_tab()
        self.tabs.addTab(self.monthly_tab, "Évolution Mensuelle")
        
        main_layout.addWidget(self.tabs)
        
        # Load initial report
        self.load_report()
        
    def setup_products_tab(self):
        """Setup the products tab"""
        layout = QVBoxLayout(self.products_tab)
        
        # Filter section
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Filtrer:"))
        self.product_filter = QLineEdit()
        self.product_filter.setPlaceholderText("Nom du produit...")
        self.product_filter.textChanged.connect(self.filter_products_table)
        filter_layout.addWidget(self.product_filter)
        
        filter_layout.addWidget(QLabel("Montrer:"))
        self.top_products = QSpinBox()
        self.top_products.setMinimum(5)
        self.top_products.setMaximum(100)
        self.top_products.setValue(20)
        self.top_products.setToolTip("Nombre maximum de produits à afficher")
        self.top_products.valueChanged.connect(self.filter_products_table)
        filter_layout.addWidget(self.top_products)
        
        filter_layout.addStretch()
        
        layout.addLayout(filter_layout)
        
        # Products table
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(8)
        self.products_table.setHorizontalHeaderLabels([
            "Produit", "Catégorie", "Qté vendue", "CA (MAD)", "Coût (MAD)", 
            "Bénéfice (MAD)", "Marge (%)", "% du CA total"
        ])
        
        self.products_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.products_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.products_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.products_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
        self.products_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Fixed)
        self.products_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Fixed)
        self.products_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.Fixed)
        self.products_table.horizontalHeader().setSectionResizeMode(7, QHeaderView.Fixed)
        
        self.products_table.setColumnWidth(1, 120)
        self.products_table.setColumnWidth(2, 80)
        self.products_table.setColumnWidth(3, 100)
        self.products_table.setColumnWidth(4, 100)
        self.products_table.setColumnWidth(5, 100)
        self.products_table.setColumnWidth(6, 80)
        self.products_table.setColumnWidth(7, 100)
        
        layout.addWidget(self.products_table)
    
    def setup_categories_tab(self):
        """Setup the categories tab"""
        layout = QVBoxLayout(self.categories_tab)
        
        # Categories table
        self.categories_table = QTableWidget()
        self.categories_table.setColumnCount(7)
        self.categories_table.setHorizontalHeaderLabels([
            "Catégorie", "Nb produits", "Qté vendue", "CA (MAD)", 
            "Coût (MAD)", "Bénéfice (MAD)", "Marge (%)"
        ])
        
        self.categories_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.categories_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.categories_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.categories_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
        self.categories_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Fixed)
        self.categories_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Fixed)
        self.categories_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.Fixed)
        
        self.categories_table.setColumnWidth(1, 100)
        self.categories_table.setColumnWidth(2, 100)
        self.categories_table.setColumnWidth(3, 120)
        self.categories_table.setColumnWidth(4, 120)
        self.categories_table.setColumnWidth(5, 120)
        self.categories_table.setColumnWidth(6, 100)
        
        layout.addWidget(self.categories_table)
    
    def setup_monthly_tab(self):
        """Setup the monthly trend tab"""
        layout = QVBoxLayout(self.monthly_tab)
        
        # Monthly table
        self.monthly_table = QTableWidget()
        self.monthly_table.setColumnCount(5)
        self.monthly_table.setHorizontalHeaderLabels([
            "Mois", "CA (MAD)", "Coût (MAD)", "Bénéfice (MAD)", "Marge (%)"
        ])
        
        self.monthly_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.monthly_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.monthly_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.monthly_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.monthly_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Fixed)
        
        self.monthly_table.setColumnWidth(0, 120)
        self.monthly_table.setColumnWidth(4, 100)
        
        layout.addWidget(self.monthly_table)
        
    def create_summary_box(self, title, value, color):
        """Create a summary info box"""
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
        
        # Store reference to value label for later updates
        frame.value_label = value_label
        
        return frame
    
    def on_period_changed(self, index):
        """Handle period selection change"""
        today = QDate.currentDate()
        
        if index == 0:  # Custom
            # Keep current dates, just enable editing
            self.start_date.setEnabled(True)
            self.end_date.setEnabled(True)
        else:
            # Disable manual date editing
            self.start_date.setEnabled(False)
            self.end_date.setEnabled(False)
            
            if index == 1:  # Today
                self.start_date.setDate(today)
                self.end_date.setDate(today)
            elif index == 2:  # Yesterday
                yesterday = today.addDays(-1)
                self.start_date.setDate(yesterday)
                self.end_date.setDate(yesterday)
            elif index == 3:  # Last 7 days
                self.start_date.setDate(today.addDays(-6))
                self.end_date.setDate(today)
            elif index == 4:  # Last 30 days
                self.start_date.setDate(today.addDays(-29))
                self.end_date.setDate(today)
            elif index == 5:  # This month
                self.start_date.setDate(QDate(today.year(), today.month(), 1))
                self.end_date.setDate(today)
            elif index == 6:  # Last month
                last_month = today.addMonths(-1)
                self.start_date.setDate(QDate(last_month.year(), last_month.month(), 1))
                # Last day of last month
                last_day = QDate(today.year(), today.month(), 1).addDays(-1)
                self.end_date.setDate(last_day)
            elif index == 7:  # This year
                self.start_date.setDate(QDate(today.year(), 1, 1))
                self.end_date.setDate(today)
        
        # Reload the report with new dates
        self.load_report()
        
    def load_report(self):
        """Load the profit margin report for the selected date range"""
        start_date = self.start_date.date().toString("yyyy-MM-dd")
        end_date = self.end_date.date().toString("yyyy-MM-dd")
        
        try:
            # Get the report data
            report_data = SalesReport.get_profit_margin_report(start_date, end_date)
            
            if not report_data:
                self.clear_report()
                QMessageBox.information(
                    self, "Aucune donnée", 
                    f"Aucune vente avec marge calculable n'a été trouvée pour la période sélectionnée."
                )
                return
                
            # Update summary boxes
            summary = report_data.get('summary', {})
            
            total_revenue = summary.get('total_revenue', 0) or 0
            self.revenue_box.value_label.setText(f"{total_revenue:.2f} MAD")
            
            total_cost = summary.get('total_cost', 0) or 0
            self.cost_box.value_label.setText(f"{total_cost:.2f} MAD")
            
            total_profit = summary.get('total_profit', 0) or 0
            self.profit_box.value_label.setText(f"{total_profit:.2f} MAD")
            
            margin_pct = summary.get('margin_percentage', 0) or 0
            self.margin_box.value_label.setText(f"{margin_pct:.2f}%")
            
            # Update products table
            self.update_products_table(report_data.get('products', []), total_revenue)
            
            # Update categories table
            self.update_categories_table(report_data.get('categories', []))
            
            # Update monthly trend table
            self.update_monthly_table(report_data.get('monthly_trend', []))
            
        except Exception as e:
            print(f"Error loading profit margin report: {e}")
            QMessageBox.warning(
                self, "Erreur", 
                f"Erreur lors du chargement du rapport: {str(e)}"
            )
    
    def update_products_table(self, products, total_revenue):
        """Update the products table with data"""
        self.products_table.setRowCount(len(products))
        self.all_products = products  # Store for filtering
        
        for row, product in enumerate(products):
            # Product name
            name_item = QTableWidgetItem(product.get('product_name', '-'))
            self.products_table.setItem(row, 0, name_item)
            
            # Category
            category_item = QTableWidgetItem(product.get('category_name', '-'))
            self.products_table.setItem(row, 1, category_item)
            
            # Quantity sold
            qty = product.get('quantity_sold', 0) or 0
            qty_item = QTableWidgetItem(str(qty))
            qty_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.products_table.setItem(row, 2, qty_item)
            
            # Revenue
            revenue = product.get('revenue', 0) or 0
            revenue_item = QTableWidgetItem(f"{revenue:.2f}")
            revenue_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.products_table.setItem(row, 3, revenue_item)
            
            # Cost
            cost = product.get('cost', 0) or 0
            cost_item = QTableWidgetItem(f"{cost:.2f}")
            cost_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.products_table.setItem(row, 4, cost_item)
            
            # Profit
            profit = product.get('profit', 0) or 0
            profit_item = QTableWidgetItem(f"{profit:.2f}")
            profit_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.products_table.setItem(row, 5, profit_item)
            
            # Margin percentage
            margin = product.get('margin_percentage', 0) or 0
            margin_item = QTableWidgetItem(f"{margin:.2f}%")
            margin_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            # Color code based on margin
            if margin < 0:
                margin_item.setForeground(QColor("red"))
            elif margin < 15:
                margin_item.setForeground(QColor("orange"))
            elif margin > 50:
                margin_item.setForeground(QColor("darkgreen"))
                
            self.products_table.setItem(row, 6, margin_item)
            
            # Percentage of total revenue
            if total_revenue > 0:
                revenue_pct = (revenue / total_revenue) * 100
            else:
                revenue_pct = 0
                
            pct_item = QTableWidgetItem(f"{revenue_pct:.2f}%")
            pct_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.products_table.setItem(row, 7, pct_item)
    
    def update_categories_table(self, categories):
        """Update the categories table with data"""
        self.categories_table.setRowCount(len(categories))
        
        for row, category in enumerate(categories):
            # Category name
            name_item = QTableWidgetItem(category.get('category_name', '-'))
            self.categories_table.setItem(row, 0, name_item)
            
            # Product count
            count = category.get('product_count', 0) or 0
            count_item = QTableWidgetItem(str(count))
            count_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.categories_table.setItem(row, 1, count_item)
            
            # Quantity sold
            qty = category.get('quantity_sold', 0) or 0
            qty_item = QTableWidgetItem(str(qty))
            qty_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.categories_table.setItem(row, 2, qty_item)
            
            # Revenue
            revenue = category.get('revenue', 0) or 0
            revenue_item = QTableWidgetItem(f"{revenue:.2f}")
            revenue_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.categories_table.setItem(row, 3, revenue_item)
            
            # Cost
            cost = category.get('cost', 0) or 0
            cost_item = QTableWidgetItem(f"{cost:.2f}")
            cost_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.categories_table.setItem(row, 4, cost_item)
            
            # Profit
            profit = category.get('profit', 0) or 0
            profit_item = QTableWidgetItem(f"{profit:.2f}")
            profit_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.categories_table.setItem(row, 5, profit_item)
            
            # Margin percentage
            margin = category.get('margin_percentage', 0) or 0
            margin_item = QTableWidgetItem(f"{margin:.2f}%")
            margin_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            # Color code based on margin
            if margin < 0:
                margin_item.setForeground(QColor("red"))
            elif margin < 15:
                margin_item.setForeground(QColor("orange"))
            elif margin > 50:
                margin_item.setForeground(QColor("darkgreen"))
                
            self.categories_table.setItem(row, 6, margin_item)
    
    def update_monthly_table(self, monthly_data):
        """Update the monthly trend table with data"""
        self.monthly_table.setRowCount(len(monthly_data))
        
        for row, month_data in enumerate(monthly_data):
            # Month
            month_str = month_data.get('month', '-')
            try:
                # Try to format as "Month Year"
                date_obj = datetime.strptime(month_str, "%Y-%m")
                month_display = date_obj.strftime("%B %Y")
            except:
                month_display = month_str
                
            month_item = QTableWidgetItem(month_display)
            self.monthly_table.setItem(row, 0, month_item)
            
            # Revenue
            revenue = month_data.get('revenue', 0) or 0
            revenue_item = QTableWidgetItem(f"{revenue:.2f}")
            revenue_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.monthly_table.setItem(row, 1, revenue_item)
            
            # Cost
            cost = month_data.get('cost', 0) or 0
            cost_item = QTableWidgetItem(f"{cost:.2f}")
            cost_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.monthly_table.setItem(row, 2, cost_item)
            
            # Profit
            profit = month_data.get('profit', 0) or 0
            profit_item = QTableWidgetItem(f"{profit:.2f}")
            profit_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.monthly_table.setItem(row, 3, profit_item)
            
            # Margin percentage
            margin = month_data.get('margin_percentage', 0) or 0
            margin_item = QTableWidgetItem(f"{margin:.2f}%")
            margin_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            # Color code based on margin
            if margin < 0:
                margin_item.setForeground(QColor("red"))
            elif margin < 15:
                margin_item.setForeground(QColor("orange"))
            elif margin > 50:
                margin_item.setForeground(QColor("darkgreen"))
                
            self.monthly_table.setItem(row, 4, margin_item)
    
    def filter_products_table(self):
        """Filter the products table based on search text and limit"""
        search_text = self.product_filter.text().lower()
        limit = self.top_products.value()
        
        # Make a copy of all products for filtering
        filtered_products = []
        
        for product in self.all_products:
            if search_text:
                product_name = product.get('product_name', '').lower()
                category_name = product.get('category_name', '').lower()
                
                if search_text in product_name or search_text in category_name:
                    filtered_products.append(product)
            else:
                filtered_products.append(product)
        
        # Apply limit
        filtered_products = filtered_products[:limit]
        
        # Update table
        self.products_table.setRowCount(0)  # Clear table
        total_revenue = sum(p.get('revenue', 0) or 0 for p in self.all_products)
        self.update_products_table(filtered_products, total_revenue)
    
    def clear_report(self):
        """Clear all report data"""
        # Clear summary boxes
        self.revenue_box.value_label.setText("0.00 MAD")
        self.cost_box.value_label.setText("0.00 MAD")
        self.profit_box.value_label.setText("0.00 MAD")
        self.margin_box.value_label.setText("0.00%")
        
        # Clear tables
        self.products_table.setRowCount(0)
        self.categories_table.setRowCount(0)
        self.monthly_table.setRowCount(0)
    
    def export_csv(self):
        """Export the report to CSV"""
        start_date = self.start_date.date().toString("yyyy-MM-dd")
        end_date = self.end_date.date().toString("yyyy-MM-dd")
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Exporter en CSV", f"rapport_marge_{start_date}_a_{end_date}.csv", "CSV Files (*.csv)"
        )
        
        if not file_name:
            return
            
        try:
            with open(file_name, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                writer.writerow(["Rapport de Marge Bénéficiaire"])
                writer.writerow([f"Période: {start_date} au {end_date}"])
                writer.writerow([])
                
                # Write summary
                writer.writerow(["Résumé"])
                writer.writerow(["Chiffre d'affaires", self.revenue_box.value_label.text()])
                writer.writerow(["Coût des ventes", self.cost_box.value_label.text()])
                writer.writerow(["Bénéfice brut", self.profit_box.value_label.text()])
                writer.writerow(["Marge brute", self.margin_box.value_label.text()])
                writer.writerow([])
                
                # Write products table
                writer.writerow(["Marge par Produit"])
                writer.writerow([
                    "Produit", "Catégorie", "Qté vendue", "CA (MAD)", "Coût (MAD)", 
                    "Bénéfice (MAD)", "Marge (%)", "% du CA total"
                ])
                
                for row in range(self.products_table.rowCount()):
                    product_row = []
                    for col in range(self.products_table.columnCount()):
                        item = self.products_table.item(row, col)
                        product_row.append(item.text() if item else "")
                    writer.writerow(product_row)
                
                writer.writerow([])
                
                # Write categories table
                writer.writerow(["Marge par Catégorie"])
                writer.writerow([
                    "Catégorie", "Nb produits", "Qté vendue", "CA (MAD)", 
                    "Coût (MAD)", "Bénéfice (MAD)", "Marge (%)"
                ])
                
                for row in range(self.categories_table.rowCount()):
                    cat_row = []
                    for col in range(self.categories_table.columnCount()):
                        item = self.categories_table.item(row, col)
                        cat_row.append(item.text() if item else "")
                    writer.writerow(cat_row)
                
                writer.writerow([])
                
                # Write monthly table
                writer.writerow(["Évolution Mensuelle"])
                writer.writerow([
                    "Mois", "CA (MAD)", "Coût (MAD)", "Bénéfice (MAD)", "Marge (%)"
                ])
                
                for row in range(self.monthly_table.rowCount()):
                    month_row = []
                    for col in range(self.monthly_table.columnCount()):
                        item = self.monthly_table.item(row, col)
                        month_row.append(item.text() if item else "")
                    writer.writerow(month_row)
            
            QMessageBox.information(
                self, "Exportation réussie", 
                f"Le rapport a été exporté avec succès vers:\n{file_name}"
            )
        except Exception as e:
            print(f"Error exporting CSV: {e}")
            QMessageBox.warning(
                self, "Erreur d'exportation", 
                f"Erreur lors de l'exportation en CSV: {str(e)}"
            )
