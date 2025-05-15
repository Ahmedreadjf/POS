from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QMessageBox, QHeaderView, QDialog, QWidget,
    QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from models.product import Product
import json
from .add_product_dialog import AddProductDialog

class ProductManagementWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Gestion des produits")
        self.setGeometry(100, 100, 1400, 600)  # Increased width for new columns

        # Main layout
        layout = QVBoxLayout()

        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("Liste des produits")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        add_button = QPushButton("Ajouter un produit")
        add_button.clicked.connect(self.add_product)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(add_button)
        layout.addLayout(header_layout)

        # Products table
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(12)  # Added columns for image, variants, and price adjustment
        self.products_table.setHorizontalHeaderLabels([
            "ID", "Image", "Code barre", "Nom", "Prix vente", "Prix achat", 
            "Stock", "Stock min", "Catégorie", "Variantes", "Prix var.", "Actions"
        ])
        
        # Set column widths
        self.products_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)  # Name column
        self.products_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.products_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.products_table.horizontalHeader().setSectionResizeMode(11, QHeaderView.Fixed)
        self.products_table.setColumnWidth(0, 50)   # ID column
        self.products_table.setColumnWidth(1, 80)   # Image column
        self.products_table.setColumnWidth(11, 100) # Actions column
        
        layout.addWidget(self.products_table)

        self.setLayout(layout)
        
        # Load products
        self.load_products()

    def load_products(self):
        products = Product.get_all_products()
        self.products_table.setRowCount(len(products))
        
        for row, product in enumerate(products):
            try:
                # Convert SQLite.Row to dictionary for easier access
                product_dict = dict(zip([
                    'id', 'barcode', 'name', 'unit_price', 'purchase_price',
                    'stock', 'min_stock', 'category_id', 'category_name',
                    'image_path', 'has_variants', 'variant_attributes',
                    'price_adjustment'
                ], product))
                
                # Clean and convert values
                try:
                    unit_price = float(str(product_dict.get('unit_price', '0')).replace('MAD', '').strip() or 0)
                except (ValueError, TypeError):
                    unit_price = 0.0
                    
                try:
                    purchase_price = float(str(product_dict.get('purchase_price', '0')).replace('MAD', '').strip() or 0)
                except (ValueError, TypeError):
                    purchase_price = 0.0
                    
                try:
                    stock = int(str(product_dict.get('stock', '0')).strip() or 0)
                except (ValueError, TypeError):
                    stock = 0
                    
                try:
                    min_stock = int(str(product_dict.get('min_stock', '0')).strip() or 0)
                except (ValueError, TypeError):
                    min_stock = 0
                
                # Create table items
                self.products_table.setItem(row, 0, QTableWidgetItem(str(product_dict.get('id', ''))))
                
                # Image cell
                if product_dict.get('image_path'):
                    image_label = QLabel()
                    pixmap = QPixmap(product_dict['image_path'])
                    if not pixmap.isNull():
                        scaled_pixmap = pixmap.scaled(
                            60, 60,
                            Qt.KeepAspectRatio,
                            Qt.SmoothTransformation
                        )
                        image_label.setPixmap(scaled_pixmap)
                        image_label.setAlignment(Qt.AlignCenter)
                        self.products_table.setCellWidget(row, 1, image_label)
                
                self.products_table.setItem(row, 2, QTableWidgetItem(str(product_dict.get('barcode', ''))))
                self.products_table.setItem(row, 3, QTableWidgetItem(str(product_dict.get('name', ''))))
                self.products_table.setItem(row, 4, QTableWidgetItem(f"{unit_price:.2f} MAD"))
                self.products_table.setItem(row, 5, QTableWidgetItem(f"{purchase_price:.2f} MAD"))
                self.products_table.setItem(row, 6, QTableWidgetItem(str(stock)))
                self.products_table.setItem(row, 7, QTableWidgetItem(str(min_stock)))
                self.products_table.setItem(row, 8, QTableWidgetItem(str(product_dict.get('category_name', ''))))
                
                # Variants info
                has_variants = product_dict.get('has_variants', False)
                variant_text = "Oui" if has_variants else "Non"
                if has_variants and product_dict.get('variant_attributes'):
                    variant_text += f"\n({', '.join(product_dict['variant_attributes'])})"
                self.products_table.setItem(row, 9, QTableWidgetItem(variant_text))
                
                # Price adjustment
                price_adj = product_dict.get('price_adjustment', 0)
                if price_adj:
                    self.products_table.setItem(row, 10, QTableWidgetItem(f"{price_adj:+.2f} MAD"))
                else:
                    self.products_table.setItem(row, 10, QTableWidgetItem("-"))

                # Actions buttons
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(0, 0, 0, 0)
                
                edit_btn = QPushButton("✏️")
                delete_btn = QPushButton("🗑️")
                variant_btn = QPushButton("🔄")  # For managing variants
                stock_btn = QPushButton("📦")   # For managing stock
                
                edit_btn.clicked.connect(lambda checked, p=product_dict: self.edit_product(p))
                delete_btn.clicked.connect(lambda checked, id=product_dict['id']: self.delete_product(id))
                variant_btn.clicked.connect(lambda checked, p=product_dict: self.manage_variants(p))
                stock_btn.clicked.connect(lambda checked, p=product_dict: self.manage_stock(p))
                
                # Set tooltips for buttons
                edit_btn.setToolTip("Modifier le produit")
                delete_btn.setToolTip("Supprimer le produit")
                variant_btn.setToolTip("Gérer les variantes")
                stock_btn.setToolTip("Gérer le stock")
                
                # Add stock management button first
                actions_layout.addWidget(stock_btn)
                
                if has_variants:
                    actions_layout.addWidget(variant_btn)
                actions_layout.addWidget(edit_btn)
                actions_layout.addWidget(delete_btn)
                
                self.products_table.setCellWidget(row, 11, actions_widget)
                
                # Highlight low stock
                if stock <= min_stock:
                    for col in range(self.products_table.columnCount()):
                        item = self.products_table.item(row, col)
                        if item:
                            item.setBackground(Qt.yellow)
                
            except Exception as e:
                print(f"Error loading product row {row}: {e}")
                print(f"Product data: {product}")
                continue

    def manage_stock(self, product):
        """Open stock management dialog for a product"""
        try:
            # Import the dialog dynamically to avoid circular imports
            from .stock_management_dialog import StockManagementDialog
            
            # Create and show the dialog
            dialog = StockManagementDialog(product, self)
            
            if dialog.exec_():
                # Refresh the product list to show updated stock levels
                self.load_products()
        except Exception as e:
            QMessageBox.warning(
                self,
                "Erreur",
                f"Erreur lors de l'ouverture du gestionnaire de stock: {str(e)}"
            )
    
    def manage_variants(self, product):
        """Open the variant management dialog for an existing product"""
        try:
            # Import the dialog dynamically to avoid circular imports
            from .variant_management_dialog import VariantManagementDialog
            
            # Parse variant attributes if they exist
            variant_attributes = []
            if product.get('variant_attributes'):
                try:
                    if isinstance(product['variant_attributes'], str):
                        variant_attributes = json.loads(product['variant_attributes'])
                    else:
                        variant_attributes = product['variant_attributes']
                except Exception as e:
                    print(f"Error parsing variant attributes: {e}")
            
            # Create and show the dialog
            dialog = VariantManagementDialog(
                product_id=product['id'],
                parent=self,
                variant_attributes=variant_attributes
            )
            
            if dialog.exec_():
                # Get the updated variant data
                variants_data = dialog.get_variants_data()
                
                # Update the product with the new variant data
                if variants_data:
                    # Update the product with new variant data
                    update_data = {
                        'has_variants': True,
                        'variant_attributes': json.dumps(dialog.get_attribute_names())
                    }
                    
                    # Update the product in the database
                    Product.update_product(product['id'], **update_data)
                    
                    # Update the variants
                    # Here we would need to add code to update/delete existing variants
                    # For now we'll just show a success message
                    self.load_products()
                    QMessageBox.information(
                        self,
                        "Succès",
                        f"{len(variants_data)} variantes configurées pour {product['name']}"
                    )
        except Exception as e:
            QMessageBox.warning(
                self,
                "Erreur",
                f"Erreur lors de la gestion des variantes: {str(e)}"
            )

    # ... (rest of the methods remain the same)
    def add_product(self):  # Added this missing method
        dialog = AddProductDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            product_data = dialog.get_product_data()
            if Product.add_product(**product_data):
                self.load_products()
                QMessageBox.information(self, "Succès", "Produit ajouté avec succès!")
            else:
                QMessageBox.warning(self, "Erreur", "Erreur lors de l'ajout du produit.")

    def edit_product(self, product):
        dialog = AddProductDialog(self, product)
        if dialog.exec_() == QDialog.Accepted:
            product_data = dialog.get_product_data()
            if Product.update_product(product['id'], **product_data):
                self.load_products()
                QMessageBox.information(self, "Succès", "Produit modifié avec succès!")
            else:
                QMessageBox.warning(self, "Erreur", "Erreur lors de la modification du produit.")

    def delete_product(self, product_id):
        reply = QMessageBox.question(
            self, 'Confirmation',
            "Êtes-vous sûr de vouloir supprimer ce produit ?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            if Product.delete_product(product_id):
                self.load_products()
                QMessageBox.information(self, "Succès", "Produit supprimé avec succès!")
            else:
                QMessageBox.warning(self, "Erreur", "Erreur lors de la suppression du produit.")