from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QComboBox, QPushButton, QFileDialog, QMessageBox
)
from models.product import Product, Category

class EditProductDialog(QDialog):
    def __init__(self, product):
        super().__init__()
        self.product = product
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Modifier le produit")
        layout = QVBoxLayout()

        # Name
        self.name_input = QLineEdit(self.product[1])
        layout.addWidget(QLabel("Nom:"))
        layout.addWidget(self.name_input)

        # Price
        self.price_input = QLineEdit(str(self.product[2]))
        layout.addWidget(QLabel("Prix:"))
        layout.addWidget(self.price_input)

        # Stock
        self.stock_input = QLineEdit(str(self.product[3]))
        layout.addWidget(QLabel("Stock:"))
        layout.addWidget(self.stock_input)

        # Category
        self.category_combo = QComboBox()
        self.load_categories()
        layout.addWidget(QLabel("Catégorie:"))
        layout.addWidget(self.category_combo)

        # Image
        image_layout = QHBoxLayout()
        self.image_path = self.product[4]
        self.image_label = QLabel(self.image_path or "Aucune image sélectionnée")
        self.browse_button = QPushButton("Parcourir...")
        self.browse_button.clicked.connect(self.browse_image)
        image_layout.addWidget(self.image_label)
        image_layout.addWidget(self.browse_button)
        layout.addLayout(image_layout)

        # Buttons
        buttons_layout = QHBoxLayout()
        save_button = QPushButton("Enregistrer")
        cancel_button = QPushButton("Annuler")
        save_button.clicked.connect(self.save_product)
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(save_button)
        buttons_layout.addWidget(cancel_button)
        layout.addLayout(buttons_layout)

        self.setLayout(layout)

    def load_categories(self):
        categories = Category.get_all_categories()
        current_category = None
        for category in categories:
            self.category_combo.addItem(category[1], category[0])
            if category[1] == self.product[5]:  # Match with current category name
                current_category = category[1]
        if current_category:
            self.category_combo.setCurrentText(current_category)

    def browse_image(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Sélectionner une image", "",
            "Image Files (*.png *.jpg *.jpeg)"
        )
        if file_name:
            self.image_path = file_name
            self.image_label.setText(file_name)

    def save_product(self):
        try:
            name = self.name_input.text()
            price = float(self.price_input.text())
            stock = int(self.stock_input.text())
            category_id = self.category_combo.currentData()

            if Product.update_product(self.product[0], name, price, category_id, stock, self.image_path):
                self.accept()
            else:
                QMessageBox.warning(self, "Erreur", "Erreur lors de la modification du produit.")
        except ValueError:
            QMessageBox.warning(self, "Erreur", "Veuillez vérifier les valeurs saisies.")