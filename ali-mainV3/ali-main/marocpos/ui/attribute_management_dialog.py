from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QMessageBox,
    QHeaderView, QWidget, QSplitter, QListWidget, QListWidgetItem,
    QTextEdit, QDialogButtonBox, QInputDialog
)
from PyQt5.QtCore import Qt
from models.product_attribute import ProductAttribute

class AttributeManagementDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_attribute_id = None
        self.init_ui()
        self.load_attributes()

    def init_ui(self):
        self.setWindowTitle("Gestion des attributs de produit")
        self.setMinimumSize(800, 500)

        # Main layout
        main_layout = QVBoxLayout(self)

        # Create splitter for attribute list and value management
        splitter = QSplitter(Qt.Horizontal)
        
        # Left side: Attribute list
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # Attribute list header
        left_header = QHBoxLayout()
        left_title = QLabel("Attributs")
        left_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        add_attr_btn = QPushButton("Ajouter")
        add_attr_btn.clicked.connect(self.add_attribute)
        
        left_header.addWidget(left_title)
        left_header.addStretch()
        left_header.addWidget(add_attr_btn)
        left_layout.addLayout(left_header)
        
        # Attribute list
        self.attribute_list = QListWidget()
        self.attribute_list.currentItemChanged.connect(self.on_attribute_selected)
        left_layout.addWidget(self.attribute_list)
        
        # Attribute buttons
        attr_btn_layout = QHBoxLayout()
        self.edit_attr_btn = QPushButton("Modifier")
        self.delete_attr_btn = QPushButton("Supprimer")
        
        self.edit_attr_btn.clicked.connect(self.edit_attribute)
        self.delete_attr_btn.clicked.connect(self.delete_attribute)
        
        attr_btn_layout.addWidget(self.edit_attr_btn)
        attr_btn_layout.addWidget(self.delete_attr_btn)
        left_layout.addLayout(attr_btn_layout)
        
        # Right side: Value management
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Value list header
        right_header = QHBoxLayout()
        self.values_title = QLabel("Valeurs de l'attribut")
        self.values_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.add_value_btn = QPushButton("Ajouter")
        self.add_value_btn.clicked.connect(self.add_attribute_value)
        
        right_header.addWidget(self.values_title)
        right_header.addStretch()
        right_header.addWidget(self.add_value_btn)
        right_layout.addLayout(right_header)
        
        # Value list
        self.value_table = QTableWidget()
        self.value_table.setColumnCount(2)
        self.value_table.setHorizontalHeaderLabels(["Valeur", "Actions"])
        self.value_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.value_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.value_table.setColumnWidth(1, 100)
        right_layout.addWidget(self.value_table)
        
        # Add widgets to splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        
        # Set default sizes
        splitter.setSizes([300, 500])
        
        main_layout.addWidget(splitter)
        
        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)
        
        # Initialize buttons as disabled until an attribute is selected
        self.edit_attr_btn.setEnabled(False)
        self.delete_attr_btn.setEnabled(False)
        self.add_value_btn.setEnabled(False)
        self.value_table.setEnabled(False)

    def load_attributes(self):
        """Load all attributes into the list"""
        self.attribute_list.clear()
        attributes = ProductAttribute.get_all_attributes()
        
        for attr in attributes:
            item = QListWidgetItem(attr['name'])
            item.setData(Qt.UserRole, attr)
            self.attribute_list.addItem(item)

    def on_attribute_selected(self, current, previous):
        """Handle attribute selection"""
        if current:
            attr_data = current.data(Qt.UserRole)
            self.selected_attribute_id = attr_data['id']
            self.values_title.setText(f"Valeurs de '{attr_data['name']}'")
            
            # Enable buttons
            self.edit_attr_btn.setEnabled(True)
            self.delete_attr_btn.setEnabled(True)
            self.add_value_btn.setEnabled(True)
            self.value_table.setEnabled(True)
            
            # Load values
            self.load_attribute_values()
        else:
            self.selected_attribute_id = None
            self.values_title.setText("Valeurs de l'attribut")
            
            # Disable buttons
            self.edit_attr_btn.setEnabled(False)
            self.delete_attr_btn.setEnabled(False)
            self.add_value_btn.setEnabled(False)
            self.value_table.setEnabled(False)
            
            # Clear values
            self.value_table.setRowCount(0)

    def load_attribute_values(self):
        """Load values for the selected attribute"""
        if not self.selected_attribute_id:
            return
            
        values = ProductAttribute.get_attribute_values(self.selected_attribute_id)
        self.value_table.setRowCount(len(values))
        
        for row, value in enumerate(values):
            # Value
            self.value_table.setItem(row, 0, QTableWidgetItem(value['value']))
            
            # Action button
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            
            delete_btn = QPushButton("🗑️")
            delete_btn.setMaximumWidth(30)
            delete_btn.clicked.connect(lambda checked, v=value['id']: self.delete_attribute_value(v))
            
            actions_layout.addWidget(delete_btn)
            actions_layout.addStretch()
            
            self.value_table.setCellWidget(row, 1, actions_widget)

    def add_attribute(self):
        """Add a new attribute"""
        name, ok = QInputDialog.getText(self, "Nouvel attribut", "Nom de l'attribut:", QLineEdit.Normal)
        if ok and name:
            description, ok = QInputDialog.getText(self, "Nouvel attribut", "Description (optionnelle):", QLineEdit.Normal)
            if ok:  # User might cancel the description but we still add
                attribute_id = ProductAttribute.add_attribute(name, description if description else None)
                if attribute_id:
                    self.load_attributes()
                    # Select the new attribute
                    for i in range(self.attribute_list.count()):
                        item = self.attribute_list.item(i)
                        if item.data(Qt.UserRole)['id'] == attribute_id:
                            self.attribute_list.setCurrentItem(item)
                            break
                else:
                    QMessageBox.warning(self, "Erreur", "Impossible d'ajouter cet attribut.")

    def edit_attribute(self):
        """Edit the selected attribute"""
        if not self.selected_attribute_id:
            return
            
        current_item = self.attribute_list.currentItem()
        if current_item:
            attr_data = current_item.data(Qt.UserRole)
            
            name, ok = QInputDialog.getText(
                self, "Modifier attribut", 
                "Nom de l'attribut:", 
                QLineEdit.Normal, 
                attr_data['name']
            )
            
            if ok and name:
                description, ok = QInputDialog.getText(
                    self, "Modifier attribut", 
                    "Description:", 
                    QLineEdit.Normal, 
                    attr_data['description'] or ""
                )
                
                if ok and ProductAttribute.update_attribute(
                    self.selected_attribute_id, 
                    name, 
                    description if description else None
                ):
                    self.load_attributes()
                else:
                    QMessageBox.warning(self, "Erreur", "Impossible de modifier cet attribut.")

    def delete_attribute(self):
        """Delete the selected attribute"""
        if not self.selected_attribute_id:
            return
            
        reply = QMessageBox.question(
            self, 'Confirmation',
            "Êtes-vous sûr de vouloir supprimer cet attribut et toutes ses valeurs ?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if ProductAttribute.delete_attribute(self.selected_attribute_id):
                self.selected_attribute_id = None
                self.load_attributes()
            else:
                QMessageBox.warning(self, "Erreur", "Impossible de supprimer cet attribut.")

    def add_attribute_value(self):
        """Add a new value to the selected attribute"""
        if not self.selected_attribute_id:
            return
            
        value, ok = QInputDialog.getText(self, "Nouvelle valeur", "Valeur:", QLineEdit.Normal)
        if ok and value:
            if ProductAttribute.add_attribute_value(self.selected_attribute_id, value):
                self.load_attribute_values()
            else:
                QMessageBox.warning(self, "Erreur", "Impossible d'ajouter cette valeur.")

    def delete_attribute_value(self, value_id):
        """Delete an attribute value"""
        reply = QMessageBox.question(
            self, 'Confirmation',
            "Êtes-vous sûr de vouloir supprimer cette valeur ?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if ProductAttribute.delete_attribute_value(value_id):
                self.load_attribute_values()
            else:
                QMessageBox.warning(self, "Erreur", "Impossible de supprimer cette valeur.")
