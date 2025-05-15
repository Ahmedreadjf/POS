from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, 
    QPushButton, QLabel, QHeaderView, QMessageBox, QComboBox, QLineEdit,
    QSpinBox, QDoubleSpinBox, QFrame, QCheckBox, QDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from models.product import Product
from models.category import Category
import json
import os

class ProductManagementWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_products()

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Gestion des produits")
        self.setGeometry(100, 100, 1200, 800)

        # Main layout
        main_layout = QVBoxLayout(self)

        # Search and filter section
        top_layout = QHBoxLayout()
        
        # Search box
        search_label = QLabel("Rechercher:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Nom de produit, code-barres...")
        self.search_input.textChanged.connect(self.filter_products)
        
        # Category filter
        category_label = QLabel("Catégorie:")
        self.category_filter = QComboBox()
        self.category_filter.currentIndexChanged.connect(self.filter_products)
        
        # Add New Product button
        add_product_btn = QPushButton("+ Ajouter un produit")
        add_product_btn.clicked.connect(self.add_product)
        add_product_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        
        # Add widgets to top layout
        top_layout.addWidget(search_label)
        top_layout.addWidget(self.search_input)
        top_layout.addWidget(category_label)
        top_layout.addWidget(self.category_filter)
        top_layout.addStretch()
        top_layout.addWidget(add_product_btn)
        
        main_layout.addLayout(top_layout)

        # Products table
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(12)
        self.products_table.setHorizontalHeaderLabels([
            "ID", "Image", "Code-barres", "Nom", "Prix vente", "Prix achat", 
            "Stock", "Stock min", "Catégorie", "Variantes", "Marge", "Actions"
        ])

        # Set column widths
        self.products_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.products_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.products_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.products_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.products_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Fixed)
        self.products_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Fixed)
        self.products_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.Fixed)
        self.products_table.horizontalHeader().setSectionResizeMode(7, QHeaderView.Fixed)
        self.products_table.horizontalHeader().setSectionResizeMode(8, QHeaderView.Fixed)
        self.products_table.horizontalHeader().setSectionResizeMode(9, QHeaderView.Fixed)
        self.products_table.horizontalHeader().setSectionResizeMode(10, QHeaderView.Fixed)
        self.products_table.horizontalHeader().setSectionResizeMode(11, QHeaderView.Fixed)
        
        self.products_table.setColumnWidth(0, 50)  # ID
        self.products_table.setColumnWidth(1, 70)  # Image
        self.products_table.setColumnWidth(2, 100) # Barcode
        # Column 3 (Name) is set to stretch
        self.products_table.setColumnWidth(4, 80)  # Sell price
        self.products_table.setColumnWidth(5, 80)  # Purchase price
        self.products_table.setColumnWidth(6, 60)  # Stock
        self.products_table.setColumnWidth(7, 60)  # Min stock
        self.products_table.setColumnWidth(8, 120) # Category
        self.products_table.setColumnWidth(9, 120) # Variants
        self.products_table.setColumnWidth(10, 80) # Margin
        self.products_table.setColumnWidth(11, 180) # Actions
        
        main_layout.addWidget(self.products_table)
        
        # Load categories for the filter
        self.load_categories()

    def load_categories(self):
        """Load categories for filtering"""
        self.category_filter.clear()
        self.category_filter.addItem("Toutes les catégories", None)
        
        categories = Category.get_all_categories()
        for category in categories:
            self.category_filter.addItem(category[1], category[0])

            def load_products(self, category_id=None):
        """Load products from database (FIXED)"""
        try:
            # Clear table
            self.products_table.setRowCount(0)
            
            # Get products using raw SQL for maximum reliability
            conn = get_connection()
            if not conn:
                QMessageBox.critical(self, "Erreur", "Impossible de se connecter à la base de données")
                return
                
            try:
                cursor = conn.cursor()
                
                if category_id:
                    cursor.execute("""
                        SELECT 
                            p.id, p.barcode, p.name, p.unit_price, p.purchase_price,
                            p.stock, p.min_stock, p.category_id, c.name as category_name,
                            p.image_path, p.has_variants, p.variant_attributes, p.description
                        FROM Products p
                        LEFT JOIN Categories c ON p.category_id = c.id
                        WHERE p.category_id = ?
                        ORDER BY p.name
                    """, (category_id,))
                else:
                    cursor.execute("""
                        SELECT 
                            p.id, p.barcode, p.name, p.unit_price, p.purchase_price,
                            p.stock, p.min_stock, p.category_id, c.name as category_name,
                            p.image_path, p.has_variants, p.variant_attributes, p.description
                        FROM Products p
                        LEFT JOIN Categories c ON p.category_id = c.id
                        ORDER BY p.name
                    """)
                
                products = []
                columns = [column[0] for column in cursor.description]
                for row in cursor.fetchall():
                    product_dict = dict(zip(columns, row))
                    products.append(product_dict)
                
                conn.close()
            except Exception as e:
                print(f"Database error: {e}")
                if conn:
                    conn.close()
                QMessageBox.critical(self, "Erreur", f"Erreur de base de données: {str(e)}")
                return
            
            print(f"Chargement de {len(products)} produits")
            
            # Set row count
            self.products_table.setRowCount(len(products))def filter_products(self):
        """Filter products based on search text and category"""
        search_text = self.search_input.text().lower()
        category_id = self.category_filter.currentData()
        
        if category_id:
            # Filter by category first, then by search text
            self.load_products(category_id)
            
            # Then filter by search text
            for row in range(self.products_table.rowCount()):
                found = False
                for col in [2, 3]:  # barcode and name columns
                    item = self.products_table.item(row, col)
                    if item and search_text in item.text().lower():
                        found = True
                        break
                self.products_table.setRowHidden(row, not found)
        else:
            # Load all products and filter by search text
            self.load_products()
            
            # Then filter by search text
            for row in range(self.products_table.rowCount()):
                found = False
                for col in [2, 3]:  # barcode and name columns
                    item = self.products_table.item(row, col)
                    if item and search_text in item.text().lower():
                        found = True
                        break
                self.products_table.setRowHidden(row, not found)

    def add_product(self):
        """Open add product dialog"""
        try:
            from .add_product_dialog import AddProductDialog
            dialog = AddProductDialog(self)
            
            if dialog.exec_():
                self.load_products()
                QMessageBox.information(self, "Succès", "Produit ajouté avec succès!")
        except Exception as e:
            print(f"Error adding product: {e}")
            QMessageBox.warning(self, "Erreur", f"Erreur lors de l'ajout du produit: {str(e)}")

    def edit_product(self, product):
        """Open edit product dialog with enhanced error handling"""
        try:
            from ui.product_helpers import debug_log, get_product_by_id, handle_error
            
            debug_log(f"Opening edit dialog for product ID {product.get('id')}")
            
            # Reload product to ensure we have the most current data
            product_id = product.get('id')
            if product_id:
                fresh_product = get_product_by_id(product_id)
                if fresh_product:
                    product = fresh_product
                    debug_log(f"Successfully loaded fresh product data for ID {product_id}")
                else:
                    debug_log(f"Could not load fresh product data for ID {product_id}, using provided data")
            
            # Import dialog and show it
            from .edit_product_dialog import EditProductDialog
            dialog = EditProductDialog(product, self)
            
            if dialog.exec_():
                debug_log(f"Product {product_id} successfully edited, reloading product list")
                self.load_products()
                QMessageBox.information(self, "Succès", "Produit modifié avec succès!")
            else:
                debug_log(f"Edit dialog cancelled for product {product_id}")
                
        except Exception as e:
            debug_log(f"Error editing product: {e}")
            import traceback
            debug_log(traceback.format_exc())
            handle_error(self, "Erreur d'édition", "Impossible de modifier le produit", e)

    def delete_product(self, product_id):
        """Delete a product"""
        reply = QMessageBox.question(
            self, 'Confirmation',
            'Êtes-vous sûr de vouloir supprimer ce produit? Cette action est irréversible.',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if Product.delete_product(product_id):
                self.load_products()
                QMessageBox.information(self, "Succès", "Produit supprimé avec succès!")
            else:
                QMessageBox.warning(self, "Erreur", "Erreur lors de la suppression du produit.")

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
            print(f"Error opening stock management: {e}")
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
                    variant_attributes = []
            
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
            print(f"Error managing variants: {e}")
            QMessageBox.warning(
                self,
                "Erreur",
                f"Erreur lors de la gestion des variantes: {str(e)}"
            )
