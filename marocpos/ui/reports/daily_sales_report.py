from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QDateEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QFrame, QGroupBox, QFormLayout, QComboBox, QCheckBox,
    QMessageBox, QFileDialog
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor, QPainter, QPen
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog
from models.sales_report import SalesReport
from datetime import datetime, timedelta
import os
import csv
import json

class DailySalesReport(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Rapport des ventes quotidiennes")
        
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Date selection section
        date_frame = QFrame()
        date_frame.setFrameShape(QFrame.StyledPanel)
        date_frame.setStyleSheet("background-color: #f8f9fa; padding: 10px; border-radius: 5px;")
        date_layout = QHBoxLayout(date_frame)
        
        date_label = QLabel("Date:")
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        
        self.date_edit.dateChanged.connect(self.load_report)
        
        date_layout.addWidget(date_label)
        date_layout.addWidget(self.date_edit)
        date_layout.addStretch()
        
        # Export buttons
        export_pdf_btn = QPushButton("Exporter en PDF")
        export_pdf_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        export_pdf_btn.clicked.connect(self.export_pdf)
        
        export_csv_btn = QPushButton("Exporter en CSV")
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
        
        print_btn = QPushButton("Imprimer")
        print_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #0069d9;
            }
        """)
        print_btn.clicked.connect(self.print_report)
        
        date_layout.addWidget(export_pdf_btn)
        date_layout.addWidget(export_csv_btn)
        date_layout.addWidget(print_btn)
        
        main_layout.addWidget(date_frame)
        
        # Summary section
        summary_group = QGroupBox("Résumé des ventes")
        summary_layout = QHBoxLayout()
        
        # Create summary boxes
        self.total_sales_box = self.create_summary_box("Total des ventes", "0.00 MAD", "#28a745")
        self.num_sales_box = self.create_summary_box("Nombre de ventes", "0", "#007bff")
        self.avg_sale_box = self.create_summary_box("Vente moyenne", "0.00 MAD", "#fd7e14")
        self.discount_box = self.create_summary_box("Total remises", "0.00 MAD", "#6c757d")
        
        summary_layout.addWidget(self.total_sales_box)
        summary_layout.addWidget(self.num_sales_box)
        summary_layout.addWidget(self.avg_sale_box)
        summary_layout.addWidget(self.discount_box)
        
        summary_group.setLayout(summary_layout)
        main_layout.addWidget(summary_group)
        
        # Sales details section
        details_group = QGroupBox("Détails des ventes")
        details_layout = QVBoxLayout()
        
        # Sales table
        self.sales_table = QTableWidget()
        self.sales_table.setColumnCount(7)
        self.sales_table.setHorizontalHeaderLabels([
            "ID", "Heure", "Vendeur", "Articles", "Sous-total", "Remise", "Total"
        ])
        
        self.sales_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.sales_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.sales_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.sales_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
        self.sales_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Fixed)
        self.sales_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Fixed)
        self.sales_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.Fixed)
        
        self.sales_table.setColumnWidth(0, 80)
        self.sales_table.setColumnWidth(1, 120)
        self.sales_table.setColumnWidth(3, 80)
        self.sales_table.setColumnWidth(4, 120)
        self.sales_table.setColumnWidth(5, 120)
        self.sales_table.setColumnWidth(6, 120)
        
        details_layout.addWidget(self.sales_table)
        
        details_group.setLayout(details_layout)
        main_layout.addWidget(details_group)
        
        # Payment methods section
        payment_group = QGroupBox("Méthodes de paiement")
        payment_layout = QVBoxLayout()
        
        # Payment methods table
        self.payment_table = QTableWidget()
        self.payment_table.setColumnCount(3)
        self.payment_table.setHorizontalHeaderLabels([
            "Méthode de paiement", "Nombre de transactions", "Montant"
        ])
        
        self.payment_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.payment_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.payment_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        
        self.payment_table.setColumnWidth(1, 180)
        self.payment_table.setColumnWidth(2, 120)
        
        payment_layout.addWidget(self.payment_table)
        
        payment_group.setLayout(payment_layout)
        main_layout.addWidget(payment_group)
        
        # Top products section
        products_group = QGroupBox("Produits les plus vendus")
        products_layout = QVBoxLayout()
        
        # Top products table
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(4)
        self.products_table.setHorizontalHeaderLabels([
            "Produit", "Quantité vendue", "Montant total", "% des ventes"
        ])
        
        self.products_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.products_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.products_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.products_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
        
        self.products_table.setColumnWidth(1, 120)
        self.products_table.setColumnWidth(2, 120)
        self.products_table.setColumnWidth(3, 100)
        
        products_layout.addWidget(self.products_table)
        
        products_group.setLayout(products_layout)
        main_layout.addWidget(products_group)
        
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
        
    def load_report(self):
        """Load the sales report for the selected date"""
        date_str = self.date_edit.date().toString("yyyy-MM-dd")
        
        try:
            # Get the report data
            report_data = SalesReport.get_daily_sales(date_str)
            
            if not report_data:
                self.clear_report()
                QMessageBox.information(
                    self, "Aucune donnée", 
                    f"Aucune vente n'a été trouvée pour le {date_str}."
                )
                return
                
            # Update summary boxes
            summary = report_data.get('summary', {})
            
            total_sales = summary.get('total_sales', 0) or 0
            self.total_sales_box.value_label.setText(f"{total_sales:.2f} MAD")
            
            sale_count = summary.get('sale_count', 0) or 0
            self.num_sales_box.value_label.setText(str(sale_count))
            
            avg_sale = summary.get('average_sale', 0) or 0
            self.avg_sale_box.value_label.setText(f"{avg_sale:.2f} MAD")
            
            total_discount = summary.get('total_discount', 0) or 0
            self.discount_box.value_label.setText(f"{total_discount:.2f} MAD")
            
            # Update sales table with all sales for the day
            self.update_sales_table(report_data.get('sales', []))
            
            # Update payment methods table
            self.update_payment_table(report_data.get('payment_methods', []))
            
            # Update top products table
            self.update_products_table(report_data.get('top_products', []), total_sales)
            
        except Exception as e:
            print(f"Error loading sales report: {e}")
            QMessageBox.warning(
                self, "Erreur", 
                f"Erreur lors du chargement du rapport: {str(e)}"
            )
    
    def update_sales_table(self, sales):
        """Update the sales table with data"""
        self.sales_table.setRowCount(len(sales))
        
        for row, sale in enumerate(sales):
            # Sale ID
            id_item = QTableWidgetItem(str(sale.get('id')))
            id_item.setTextAlignment(Qt.AlignCenter)
            self.sales_table.setItem(row, 0, id_item)
            
            # Time
            time_str = sale.get('created_at', '')
            if time_str:
                try:
                    # Extract time from datetime
                    time_part = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S").strftime("%H:%M:%S")
                    time_item = QTableWidgetItem(time_part)
                except:
                    time_item = QTableWidgetItem(time_str)
            else:
                time_item = QTableWidgetItem("")
                
            time_item.setTextAlignment(Qt.AlignCenter)
            self.sales_table.setItem(row, 1, time_item)
            
            # Seller
            seller_item = QTableWidgetItem(sale.get('username', 'N/A'))
            self.sales_table.setItem(row, 2, seller_item)
            
            # Item count
            item_count = sale.get('item_count', 0) or 0
            count_item = QTableWidgetItem(str(item_count))
            count_item.setTextAlignment(Qt.AlignCenter)
            self.sales_table.setItem(row, 3, count_item)
            
            # Subtotal
            subtotal = sale.get('total_amount', 0) or 0
            subtotal_item = QTableWidgetItem(f"{subtotal:.2f} MAD")
            subtotal_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.sales_table.setItem(row, 4, subtotal_item)
            
            # Discount
            discount = sale.get('discount', 0) or 0
            discount_item = QTableWidgetItem(f"{discount:.2f} MAD")
            discount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.sales_table.setItem(row, 5, discount_item)
            
            # Total
            total = sale.get('final_total', 0) or 0
            total_item = QTableWidgetItem(f"{total:.2f} MAD")
            total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.sales_table.setItem(row, 6, total_item)
    
    def update_payment_table(self, payment_methods):
        """Update the payment methods table with data"""
        self.payment_table.setRowCount(len(payment_methods))
        
        for row, payment in enumerate(payment_methods):
            # Method name
            method_item = QTableWidgetItem(payment.get('payment_method', 'N/A'))
            self.payment_table.setItem(row, 0, method_item)
            
            # Transaction count
            count = payment.get('transaction_count', 0) or 0
            count_item = QTableWidgetItem(str(count))
            count_item.setTextAlignment(Qt.AlignCenter)
            self.payment_table.setItem(row, 1, count_item)
            
            # Total amount
            amount = payment.get('total_amount', 0) or 0
            amount_item = QTableWidgetItem(f"{amount:.2f} MAD")
            amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.payment_table.setItem(row, 2, amount_item)
    
    def update_products_table(self, products, total_sales):
        """Update the top products table with data"""
        self.products_table.setRowCount(len(products))
        
        for row, product in enumerate(products):
            # Product name
            name_item = QTableWidgetItem(product.get('product_name', 'N/A'))
            self.products_table.setItem(row, 0, name_item)
            
            # Quantity sold
            qty = product.get('quantity_sold', 0) or 0
            qty_item = QTableWidgetItem(str(qty))
            qty_item.setTextAlignment(Qt.AlignCenter)
            self.products_table.setItem(row, 1, qty_item)
            
            # Total sales
            sales = product.get('total_sales', 0) or 0
            sales_item = QTableWidgetItem(f"{sales:.2f} MAD")
            sales_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.products_table.setItem(row, 2, sales_item)
            
            # Percentage of total sales
            if total_sales > 0:
                percentage = (sales / total_sales) * 100
            else:
                percentage = 0
                
            pct_item = QTableWidgetItem(f"{percentage:.2f}%")
            pct_item.setTextAlignment(Qt.AlignCenter)
            self.products_table.setItem(row, 3, pct_item)
    
    def clear_report(self):
        """Clear all report data"""
        # Clear summary boxes
        self.total_sales_box.value_label.setText("0.00 MAD")
        self.num_sales_box.value_label.setText("0")
        self.avg_sale_box.value_label.setText("0.00 MAD")
        self.discount_box.value_label.setText("0.00 MAD")
        
        # Clear tables
        self.sales_table.setRowCount(0)
        self.payment_table.setRowCount(0)
        self.products_table.setRowCount(0)
    
    def export_pdf(self):
        """Export the report to PDF"""
        date_str = self.date_edit.date().toString("yyyy-MM-dd")
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Exporter en PDF", f"rapport_ventes_{date_str}.pdf", "PDF Files (*.pdf)"
        )
        
        if not file_name:
            return
            
        try:
            printer = QPrinter(QPrinter.HighResolution)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(file_name)
            printer.setPageSize(QPrinter.A4)
            
            # Create the PDF document
            self.create_report_document(printer)
            
            QMessageBox.information(
                self, "Exportation réussie", 
                f"Le rapport a été exporté avec succès vers:\n{file_name}"
            )
        except Exception as e:
            print(f"Error exporting PDF: {e}")
            QMessageBox.warning(
                self, "Erreur d'exportation", 
                f"Erreur lors de l'exportation en PDF: {str(e)}"
            )
    
    def export_csv(self):
        """Export the report to CSV"""
        date_str = self.date_edit.date().toString("yyyy-MM-dd")
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Exporter en CSV", f"rapport_ventes_{date_str}.csv", "CSV Files (*.csv)"
        )
        
        if not file_name:
            return
            
        try:
            with open(file_name, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                writer.writerow(["Rapport des ventes quotidiennes"])
                writer.writerow([f"Date: {date_str}"])
                writer.writerow([])
                
                # Write summary
                writer.writerow(["Résumé"])
                writer.writerow(["Total des ventes", self.total_sales_box.value_label.text()])
                writer.writerow(["Nombre de ventes", self.num_sales_box.value_label.text()])
                writer.writerow(["Vente moyenne", self.avg_sale_box.value_label.text()])
                writer.writerow(["Total remises", self.discount_box.value_label.text()])
                writer.writerow([])
                
                # Write sales
                writer.writerow(["Détails des ventes"])
                writer.writerow([
                    "ID", "Heure", "Vendeur", "Articles", "Sous-total", "Remise", "Total"
                ])
                
                for row in range(self.sales_table.rowCount()):
                    sale_row = []
                    for col in range(self.sales_table.columnCount()):
                        item = self.sales_table.item(row, col)
                        sale_row.append(item.text() if item else "")
                    writer.writerow(sale_row)
                
                writer.writerow([])
                
                # Write payment methods
                writer.writerow(["Méthodes de paiement"])
                writer.writerow([
                    "Méthode de paiement", "Nombre de transactions", "Montant"
                ])
                
                for row in range(self.payment_table.rowCount()):
                    payment_row = []
                    for col in range(self.payment_table.columnCount()):
                        item = self.payment_table.item(row, col)
                        payment_row.append(item.text() if item else "")
                    writer.writerow(payment_row)
                
                writer.writerow([])
                
                # Write top products
                writer.writerow(["Produits les plus vendus"])
                writer.writerow([
                    "Produit", "Quantité vendue", "Montant total", "% des ventes"
                ])
                
                for row in range(self.products_table.rowCount()):
                    product_row = []
                    for col in range(self.products_table.columnCount()):
                        item = self.products_table.item(row, col)
                        product_row.append(item.text() if item else "")
                    writer.writerow(product_row)
            
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
    
    def print_report(self):
        """Print the report"""
        try:
            printer = QPrinter(QPrinter.HighResolution)
            dialog = QPrintDialog(printer, self)
            
            if dialog.exec_() == QPrintDialog.Accepted:
                self.create_report_document(printer)
        except Exception as e:
            print(f"Error printing report: {e}")
            QMessageBox.warning(
                self, "Erreur d'impression", 
                f"Erreur lors de l'impression du rapport: {str(e)}"
            )
    
    def create_report_document(self, printer):
        """Create the report document for printing or PDF export"""
        date_str = self.date_edit.date().toString("yyyy-MM-dd")
        
        painter = QPainter()
        painter.begin(printer)
        
        # Get the printer rect
        rect = printer.pageRect()
        painter.setViewport(rect)
        
        # Set up font and colors
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)
        
        # Draw the report
        y_pos = 100  # Starting y position
        
        # Title
        font = painter.font()
        font.setPointSize(18)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(
            0, y_pos, rect.width(), 30, 
            Qt.AlignHCenter, f"Rapport des ventes quotidiennes - {date_str}"
        )
        
        y_pos += 50
        
        # Summary section
        font.setPointSize(14)
        painter.setFont(font)
        painter.drawText(0, y_pos, rect.width(), 30, Qt.AlignLeft, "Résumé des ventes")
        
        y_pos += 40
        
        # Summary boxes
        font.setPointSize(12)
        font.setBold(False)
        painter.setFont(font)
        
        box_width = rect.width() / 4
        box_height = 80
        
        # Draw summary boxes
        painter.drawText(0, y_pos, box_width, 30, Qt.AlignCenter, "Total des ventes")
        painter.drawText(box_width, y_pos, box_width, 30, Qt.AlignCenter, "Nombre de ventes")
        painter.drawText(box_width * 2, y_pos, box_width, 30, Qt.AlignCenter, "Vente moyenne")
        painter.drawText(box_width * 3, y_pos, box_width, 30, Qt.AlignCenter, "Total remises")
        
        y_pos += 30
        
        font.setPointSize(14)
        font.setBold(True)
        painter.setFont(font)
        
        painter.drawText(0, y_pos, box_width, 30, Qt.AlignCenter, self.total_sales_box.value_label.text())
        painter.drawText(box_width, y_pos, box_width, 30, Qt.AlignCenter, self.num_sales_box.value_label.text())
        painter.drawText(box_width * 2, y_pos, box_width, 30, Qt.AlignCenter, self.avg_sale_box.value_label.text())
        painter.drawText(box_width * 3, y_pos, box_width, 30, Qt.AlignCenter, self.discount_box.value_label.text())
        
        y_pos += 60
        
        # Draw sales table
        self.draw_table(
            painter, rect, y_pos, "Détails des ventes",
            self.sales_table, 
            [80, 120, rect.width() - 680, 80, 120, 120, 120]
        )
        
        y_pos += 50 + (self.sales_table.rowCount() + 1) * 30
        
        # Check if we need a new page for payment methods
        if y_pos > rect.height() - 200:
            printer.newPage()
            y_pos = 100
        
        # Draw payment methods table
        self.draw_table(
            painter, rect, y_pos, "Méthodes de paiement",
            self.payment_table, 
            [rect.width() - 400, 150, 200]
        )
        
        y_pos += 50 + (self.payment_table.rowCount() + 1) * 30
        
        # Check if we need a new page for top products
        if y_pos > rect.height() - 200:
            printer.newPage()
            y_pos = 100
        
        # Draw top products table
        self.draw_table(
            painter, rect, y_pos, "Produits les plus vendus",
            self.products_table, 
            [rect.width() - 450, 120, 150, 120]
        )
        
        painter.end()
    
    def draw_table(self, painter, rect, y_pos, title, table, column_widths):
        """Draw a table on the report"""
        # Draw title
        font = painter.font()
        font.setPointSize(14)
        font.setBold(True)
        painter.setFont(font)
        
        painter.drawText(0, y_pos, rect.width(), 30, Qt.AlignLeft, title)
        
        y_pos += 40
        
        # Draw table header
        font.setPointSize(12)
        painter.setFont(font)
        
        x_pos = 50
        for col in range(table.columnCount()):
            header_text = table.horizontalHeaderItem(col).text()
            painter.drawText(x_pos, y_pos, column_widths[col], 30, Qt.AlignCenter, header_text)
            x_pos += column_widths[col] + 10
        
        # Draw a line under the header
        painter.save()
        pen = QPen(Qt.black, 1)
        painter.setPen(pen)
        painter.drawLine(50, y_pos + 30, rect.width() - 50, y_pos + 30)
        painter.restore()
        
        y_pos += 30
        
        # Draw table rows
        font.setBold(False)
        painter.setFont(font)
        
        for row in range(table.rowCount()):
            x_pos = 50
            for col in range(table.columnCount()):
                item = table.item(row, col)
                if item:
                    text = item.text()
                    alignment = item.textAlignment()
                    painter.drawText(x_pos, y_pos, column_widths[col], 30, alignment, text)
                x_pos += column_widths[col] + 10
            y_pos += 30
