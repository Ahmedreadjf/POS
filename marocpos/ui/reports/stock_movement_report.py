from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QDateEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QFrame, QGroupBox, QFormLayout, QComboBox, QLineEdit,
    QMessageBox, QFileDialog
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor, QPainter, QPen
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog
from models.sales_report import SalesReport
from models.product import Product
from datetime import datetime, timedelta
import os
import csv
import json

class StockMovementReport(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Rapport des mouvements de stock")
        
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Filter section
        filter_frame = QFrame()
        filter_frame.setFrameShape(QFrame.StyledPanel)
        filter_frame.setStyleSheet("background-color: #f8f9fa; padding: 10px; border-radius: 5px;")
        filter_layout = QHBoxLayout(filter_frame)
        
        # Date range
        filter_layout.addWidget(QLabel("Période:"))
        
        # Start date
        filter_layout.addWidget(QLabel("Du:"))
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addDays(-30))
        filter_layout.addWidget(self.start_date)
        
        # End date
        filter_layout.addWidget(QLabel("Au:"))
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        filter_layout.addWidget(self.end_date)
        
        # Product filter
        filter_layout.addWidget(QLabel("Produit:"))
        self.product_combo = QComboBox()
        self.product_combo.setMinimumWidth(200)
        self.product_combo.addItem("Tous les produits", None)
        filter_layout.addWidget(self.product_combo)
        
        # Movement type filter
        filter_layout.addWidget(QLabel("Type:"))
        self.movement_type_combo = QComboBox()
        self.movement_type_combo.addItem("Tous les mouvements", None)
        self.movement_type_combo.addItem("Achats", "purchase")
        self.movement_type_combo.addItem("Ventes", "sale")
        self.movement_type_combo.addItem("Ajustements +", "adjustment_in")
        self.movement_type_combo.addItem("Ajustements -", "adjustment_out")
        self.movement_type_combo.addItem("Pertes", "loss")
        self.movement_type_combo.addItem("Retours", "return")
        filter_layout.addWidget(self.movement_type_combo)
        
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
        filter_layout.addWidget(refresh_btn)
        
        # Export button
        export_btn = QPushButton("Exporter CSV")
        export_btn.setStyleSheet("""
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
        export_btn.clicked.connect(self.export_csv)
        filter_layout.addWidget(export_btn)
        
        main_layout.addWidget(filter_frame)
        
        # Summary section
        summary_group = QGroupBox("Résumé des mouvements")
        summary_layout = QHBoxLayout()
        
        # Create summary boxes
        self.total_in_box = self.create_summary_box("Entrées totales", "0", "#28a745")
        self.total_out_box = self.create_summary_box("Sorties totales", "0", "#dc3545")
        self.net_change_box = self.create_summary_box("Changement net", "0", "#007bff")
        self.movement_count_box = self.create_summary_box("Nombre de mouvements", "0", "#6c757d")
        
        summary_layout.addWidget(self.total_in_box)
        summary_layout.addWidget(self.total_out_box)
        summary_layout.addWidget(self.net_change_box)
        summary_layout.addWidget(self.movement_count_box)
        
        summary_group.setLayout(summary_layout)
        main_layout.addWidget(summary_group)
        
        # Movement types section
        types_group = QGroupBox("Mouvements par type")
        types_layout = QVBoxLayout()
        
        # Types table
        self.types_table = QTableWidget()
        self.types_table.setColumnCount(4)
        self.types_table.setHorizontalHeaderLabels([
            "Type de mouvement", "Nombre", "Quantité", "Valeur"
        ])
        
        self.types_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.types_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.types_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.types_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
        
        self.types_table.setColumnWidth(1, 100)
        self.types_table.setColumnWidth(2, 100)
        self.types_table.setColumnWidth(3, 150)
        
        types_layout.addWidget(self.types_table)
        types_group.setLayout(types_layout)
        main_layout.addWidget(types_group)
        
        # Movements section
        movements_group = QGroupBox("Détails des mouvements")
        movements_layout = QVBoxLayout()
        
        # Search filter
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Rechercher:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Produit, référence, notes...")
        self.search_input.textChanged.connect(self.filter_movements)
        search_layout.addWidget(self.search_input)
        
        movements_layout.addLayout(search_layout)
        
        # Movements table
        self.movements_table = QTableWidget()
        self.movements_table.setColumnCount(9)
        self.movements_table.setHorizontalHeaderLabels([
            "Date", "Produit", "Variante", "Type", "Quantité", 
            "Prix unitaire", "Valeur", "Référence", "Utilisateur"
        ])
        
        self.movements_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.movements_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.movements_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.movements_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
        self.movements_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Fixed)
        self.movements_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Fixed)
        self.movements_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.Fixed)
        self.movements_table.horizontalHeader().setSectionResizeMode(7, QHeaderView.Fixed)
        self.movements_table.horizontalHeader().setSectionResizeMode(8, QHeaderView.Fixed)
        
        self.movements_table.setColumnWidth(0, 150)
        self.movements_table.setColumnWidth(2, 150)
        self.movements_table.setColumnWidth(3, 100)
        self.movements_table.setColumnWidth(4, 80)
        self.movements_table.setColumnWidth(5, 100)
        self.movements_table.setColumnWidth(6, 100)
        self.movements_table.setColumnWidth(7, 100)
        self.movements_table.setColumnWidth(8, 120)
        
        movements_layout.addWidget(self.movements_table)
        movements_group.setLayout(movements_layout)
        main_layout.addWidget(movements_group)
        
        # Load products for the filter
        self.load_products()
        
        # Load initial report
        self.load_report()
        
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
        
    def load_products(self):
        """Load products for the filter dropdown"""
        try:
            products = Product.get_all_products()
            
            # Add products to combo box
            self.product_combo.clear()
            self.product_combo.addItem("Tous les produits", None)
            
            for product in products:
                self.product_combo.addItem(product['name'], product['id'])
                
        except Exception as e:
            print(f"Error loading products: {e}")
            QMessageBox.warning(
                self, "Erreur", 
                f"Erreur lors du chargement des produits: {str(e)}"
            )
    
    def load_report(self):
        """Load the stock movement report for the selected filters"""
        start_date = self.start_date.date().toString("yyyy-MM-dd")
        end_date = self.end_date.date().toString("yyyy-MM-dd")
        
        # Get product_id from combo box
        product_id = self.product_combo.currentData()
        
        try:
            # Get the report data
            report_data = SalesReport.get_stock_movement_report(
                start_date=start_date,
                end_date=end_date,
                product_id=product_id
            )
            
            if not report_data:
                self.clear_report()
                QMessageBox.information(
                    self, "Aucune donnée", 
                    f"Aucun mouvement de stock n'a été trouvé pour la période et les filtres sélectionnés."
                )
                return
                
            # Update summary boxes
            summary = report_data.get('summary', {})
            
            total_in = summary.get('total_in', 0) or 0
            self.total_in_box.value_label.setText(str(total_in))
            
            total_out = summary.get('total_out', 0) or 0
            self.total_out_box.value_label.setText(str(total_out))
            
            net_change = summary.get('net_change', 0) or 0
            self.net_change_box.value_label.setText(str(net_change))
            
            total_movements = summary.get('total_movements', 0) or 0
            self.movement_count_box.value_label.setText(str(total_movements))
            
            # Update movement types table
            movement_types = report_data.get('movement_types', [])
            self.update_types_table(movement_types)
            
            # Update movements table
            all_movements = report_data.get('movements', [])
            
            # Apply movement type filter if set
            movement_type = self.movement_type_combo.currentData()
            if movement_type:
                filtered_movements = [m for m in all_movements if m.get('movement_type') == movement_type]
            else:
                filtered_movements = all_movements
                
            # Store all movements for filtering
            self.all_movements = filtered_movements
            
            # Update table
            self.update_movements_table(filtered_movements)
            
        except Exception as e:
            print(f"Error loading stock movement report: {e}")
            QMessageBox.warning(
                self, "Erreur", 
                f"Erreur lors du chargement du rapport: {str(e)}"
            )
    
    def update_types_table(self, movement_types):
        """Update the movement types table with data"""
        self.types_table.setRowCount(len(movement_types))
        
        movement_type_names = {
            'purchase': 'Achats',
            'sale': 'Ventes',
            'adjustment_in': 'Ajustements +',
            'adjustment_out': 'Ajustements -',
            'loss': 'Pertes',
            'damage': 'Dommages',
            'return': 'Retours',
            'transfer_in': 'Transferts entrée',
            'transfer_out': 'Transferts sortie'
        }
        
        for row, movement_type in enumerate(movement_types):
            # Movement type
            type_name = movement_type_names.get(
                movement_type.get('movement_type', ''), 
                movement_type.get('movement_type', 'Inconnu')
            )
            type_item = QTableWidgetItem(type_name)
            self.types_table.setItem(row, 0, type_item)
            
            # Movement count
            count = movement_type.get('movement_count', 0) or 0
            count_item = QTableWidgetItem(str(count))
            count_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.types_table.setItem(row, 1, count_item)
            
            # Total quantity
            qty = movement_type.get('total_quantity', 0) or 0
            qty_item = QTableWidgetItem(str(qty))
            qty_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.types_table.setItem(row, 2, qty_item)
            
            # Total value
            value = movement_type.get('total_value', 0) or 0
            value_item = QTableWidgetItem(f"{value:.2f} MAD")
            value_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.types_table.setItem(row, 3, value_item)
    
    def update_movements_table(self, movements):
        """Update the movements table with data"""
        self.movements_table.setRowCount(len(movements))
        
        movement_type_names = {
            'purchase': 'Achats',
            'sale': 'Ventes',
            'adjustment_in': 'Ajustements +',
            'adjustment_out': 'Ajustements -',
            'loss': 'Pertes',
            'damage': 'Dommages',
            'return': 'Retours',
            'transfer_in': 'Transferts entrée',
            'transfer_out': 'Transferts sortie'
        }
        
        for row, movement in enumerate(movements):
            # Date & time
            date_str = movement.get('created_at', '')
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                formatted_date = date_obj.strftime("%Y-%m-%d %H:%M")
            except:
                formatted_date = date_str
                
            date_item = QTableWidgetItem(formatted_date)
            self.movements_table.setItem(row, 0, date_item)
            
            # Product name
            product_name = movement.get('product_name', 'Inconnu')
            product_item = QTableWidgetItem(product_name)
            self.movements_table.setItem(row, 1, product_item)
            
            # Variant name
            variant_name = movement.get('variant_name', '')
            variant_item = QTableWidgetItem(variant_name)
            self.movements_table.setItem(row, 2, variant_item)
            
            # Movement type
            type_name = movement_type_names.get(
                movement.get('movement_type', ''), 
                movement.get('movement_type', 'Inconnu')
            )
            type_item = QTableWidgetItem(type_name)
            
            # Color based on movement type
            if movement.get('movement_type') in ['purchase', 'adjustment_in', 'return', 'transfer_in']:
                type_item.setForeground(QColor("#28a745"))  # Green for additions
            elif movement.get('movement_type') in ['sale', 'adjustment_out', 'loss', 'damage', 'transfer_out']:
                type_item.setForeground(QColor("#dc3545"))  # Red for removals
                
            self.movements_table.setItem(row, 3, type_item)
            
            # Quantity
            qty = movement.get('quantity', 0) or 0
            qty_item = QTableWidgetItem(str(qty))
            qty_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.movements_table.setItem(row, 4, qty_item)
            
            # Unit price
            unit_price = movement.get('unit_price', 0) or 0
            price_item = QTableWidgetItem(f"{unit_price:.2f}")
            price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.movements_table.setItem(row, 5, price_item)
            
            # Total value
            value = (qty * unit_price)
            value_item = QTableWidgetItem(f"{value:.2f}")
            value_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.movements_table.setItem(row, 6, value_item)
            
            # Reference
            ref = movement.get('reference', '')
            ref_item = QTableWidgetItem(ref)
            self.movements_table.setItem(row, 7, ref_item)
            
            # User
            user = movement.get('user_name', '')
            user_item = QTableWidgetItem(user)
            self.movements_table.setItem(row, 8, user_item)
    
    def filter_movements(self):
        """Filter movements based on search text"""
        search_text = self.search_input.text().lower()
        
        if not search_text:
            # If no search text, show all movements
            self.update_movements_table(self.all_movements)
            return
            
        # Filter movements
        filtered_movements = []
        for movement in self.all_movements:
            product_name = movement.get('product_name', '').lower()
            variant_name = movement.get('variant_name', '').lower()
            reference = movement.get('reference', '').lower()
            notes = movement.get('notes', '').lower()
            user_name = movement.get('user_name', '').lower()
            
            if (search_text in product_name or 
                search_text in variant_name or
                search_text in reference or
                search_text in notes or
                search_text in user_name):
                filtered_movements.append(movement)
        
        # Update table with filtered movements
        self.update_movements_table(filtered_movements)
    
    def clear_report(self):
        """Clear all report data"""
        # Clear summary boxes
        self.total_in_box.value_label.setText("0")
        self.total_out_box.value_label.setText("0")
        self.net_change_box.value_label.setText("0")
        self.movement_count_box.value_label.setText("0")
        
        # Clear tables
        self.types_table.setRowCount(0)
        self.movements_table.setRowCount(0)
    
    def export_csv(self):
        """Export the report to CSV"""
        start_date = self.start_date.date().toString("yyyy-MM-dd")
        end_date = self.end_date.date().toString("yyyy-MM-dd")
        product_name = self.product_combo.currentText()
        
        if product_name == "Tous les produits":
            product_name = "tous_produits"
        else:
            product_name = product_name.replace(" ", "_").lower()
            
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Exporter en CSV", 
            f"mouvements_stock_{product_name}_{start_date}_a_{end_date}.csv", 
            "CSV Files (*.csv)"
        )
        
        if not file_name:
            return
            
        try:
            with open(file_name, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                writer.writerow(["Rapport des mouvements de stock"])
                writer.writerow([f"Période: {start_date} au {end_date}"])
                writer.writerow([f"Produit: {self.product_combo.currentText()}"])
                writer.writerow([])
                
                # Write summary
                writer.writerow(["Résumé"])
                writer.writerow(["Entrées totales", self.total_in_box.value_label.text()])
                writer.writerow(["Sorties totales", self.total_out_box.value_label.text()])
                writer.writerow(["Changement net", self.net_change_box.value_label.text()])
                writer.writerow(["Nombre de mouvements", self.movement_count_box.value_label.text()])
                writer.writerow([])
                
                # Write movement types
                writer.writerow(["Mouvements par type"])
                writer.writerow([
                    "Type de mouvement", "Nombre", "Quantité", "Valeur"
                ])
                
                for row in range(self.types_table.rowCount()):
                    type_row = []
                    for col in range(self.types_table.columnCount()):
                        item = self.types_table.item(row, col)
                        type_row.append(item.text() if item else "")
                    writer.writerow(type_row)
                
                writer.writerow([])
                
                # Write all movements
                writer.writerow(["Détails des mouvements"])
                writer.writerow([
                    "Date", "Produit", "Variante", "Type", "Quantité", 
                    "Prix unitaire", "Valeur", "Référence", "Utilisateur"
                ])
                
                for row in range(self.movements_table.rowCount()):
                    movement_row = []
                    for col in range(self.movements_table.columnCount()):
                        item = self.movements_table.item(row, col)
                        movement_row.append(item.text() if item else "")
                    writer.writerow(movement_row)
            
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
