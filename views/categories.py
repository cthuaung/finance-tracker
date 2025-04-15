"""
Categories widget for the finance tracker application
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTableView, QDialog, QFormLayout, QComboBox, QLineEdit,
    QDialogButtonBox, QHeaderView, QMessageBox, QColorDialog
)
from PyQt6.QtCore import Qt, QSortFilterProxyModel, QAbstractTableModel, QModelIndex
from PyQt6.QtGui import QColor, QBrush, QPixmap

from ..models.data_manager import DataManager
from ..models.database import TransactionType


class CategoryTableModel(QAbstractTableModel):
    """Model for the categories table"""
    
    def __init__(self, categories=None):
        super().__init__()
        self.categories = categories or []
        self.headers = ["Name", "Type", "Color"]
    
    def rowCount(self, parent=QModelIndex()):
        return len(self.categories)
    
    def columnCount(self, parent=QModelIndex()):
        return len(self.headers)
    
    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < len(self.categories)):
            return None
        
        category = self.categories[index.row()]
        
        if role == Qt.ItemDataRole.DisplayRole:
            col = index.column()
            if col == 0:  # Name
                return category.name
            elif col == 1:  # Type
                return category.type.value.capitalize()
            elif col == 2:  # Color
                return category.color
        
        elif role == Qt.ItemDataRole.BackgroundRole:
            col = index.column()
            if col == 2:  # Color column
                return QBrush(QColor(category.color))
            
        # Store the actual category object for later use
        elif role == Qt.ItemDataRole.UserRole:
            return category
        
        return None
    
    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self.headers[section]
        return None
    
    def setCategories(self, categories):
        self.beginResetModel()
        self.categories = categories
        self.endResetModel()


class CategoriesWidget(QWidget):
    """Widget for managing categories"""
    
    def __init__(self):
        super().__init__()
        
        self.setup_ui()
        self.load_categories()
    
    def setup_ui(self):
        """Set up the categories UI"""
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)
        
        # Header section
        header_layout = QHBoxLayout()
        categories_title = QLabel("Categories")
        categories_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        header_layout.addWidget(categories_title)
        header_layout.addStretch()
        
        # Add new category button
        self.add_button = QPushButton("Add Category")
        self.add_button.clicked.connect(self.add_category)
        header_layout.addWidget(self.add_button)
        
        self.main_layout.addLayout(header_layout)
        
        # Type filter
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Show:"))
        
        self.type_filter = QComboBox()
        self.type_filter.addItem("All Categories", None)
        self.type_filter.addItem("Income Categories", TransactionType.INCOME)
        self.type_filter.addItem("Expense Categories", TransactionType.EXPENSE)
        self.type_filter.currentIndexChanged.connect(self.apply_filters)
        
        filter_layout.addWidget(self.type_filter)
        filter_layout.addStretch()
        
        self.main_layout.addLayout(filter_layout)
        
        # Categories table
        self.categories_table = QTableView()
        self.categories_table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.categories_table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.categories_table.setAlternatingRowColors(True)
        self.categories_table.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        
        # Create table model
        self.table_model = CategoryTableModel()
        
        # Create proxy model for sorting and filtering
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.table_model)
        
        # Set proxy model to table
        self.categories_table.setModel(self.proxy_model)
        
        # Set column properties
        header = self.categories_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Name
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Type
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Color
        
        # Add double-click handler
        self.categories_table.doubleClicked.connect(self.edit_selected_category)
        
        # Add table to layout
        self.main_layout.addWidget(self.categories_table)
    
    def load_categories(self):
        """Load categories from the database"""
        # Get categories
        categories = DataManager.get_categories()
        
        # Set categories to the model
        self.table_model.setCategories(categories)
        
        # Apply any active filters
        self.apply_filters()
    
    def apply_filters(self):
        """Apply filters to the categories table"""
        # Get filter value
        category_type = self.type_filter.currentData()
        
        # Get filtered categories
        categories = DataManager.get_categories(transaction_type=category_type)
        
        # Update the model
        self.table_model.setCategories(categories)
    
    def add_category(self):
        """Show dialog to add a new category"""
        dialog = CategoryDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_categories()
    
    def edit_selected_category(self, index):
        """Edit the selected category"""
        # Get the selected category
        category_index = self.proxy_model.mapToSource(index)
        category = self.table_model.data(category_index, Qt.ItemDataRole.UserRole)
        
        if category:
            dialog = CategoryDialog(self, category)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.load_categories()


class CategoryDialog(QDialog):
    """Dialog for adding or editing a category"""
    
    def __init__(self, parent=None, category=None):
        super().__init__(parent)
        
        self.category = category
        self.setup_ui()
        
        if category:
            self.setWindowTitle("Edit Category")
            self.name_edit.setText(category.name)
            
            # Set type
            index = 0 if category.type == TransactionType.INCOME else 1
            self.type_combo.setCurrentIndex(index)
            
            # Set color
            self.color = category.color
            self.update_color_preview()
        else:
            self.setWindowTitle("Add Category")
            self.color = "#3498db"  # Default color
    
    def setup_ui(self):
        """Set up the dialog UI"""
        self.resize(400, 200)
        
        layout = QVBoxLayout(self)
        
        # Form layout for fields
        form_layout = QFormLayout()
        
        # Category name
        self.name_edit = QLineEdit()
        form_layout.addRow("Name:", self.name_edit)
        
        # Category type
        self.type_combo = QComboBox()
        self.type_combo.addItem("Income", TransactionType.INCOME)
        self.type_combo.addItem("Expense", TransactionType.EXPENSE)
        form_layout.addRow("Type:", self.type_combo)
        
        # Category color
        color_layout = QHBoxLayout()
        
        self.color_preview = QLabel()
        self.color_preview.setFixedSize(24, 24)
        self.color_preview.setStyleSheet("border: 1px solid #cccccc;")
        color_layout.addWidget(self.color_preview)
        
        self.color_button = QPushButton("Select Color")
        self.color_button.clicked.connect(self.select_color)
        color_layout.addWidget(self.color_button)
        
        form_layout.addRow("Color:", color_layout)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Initialize color preview
        self.update_color_preview()
    
    def select_color(self):
        """Open color dialog to select a color"""
        color = QColorDialog.getColor(QColor(self.color), self, "Select Color")
        
        if color.isValid():
            self.color = color.name()
            self.update_color_preview()
    
    def update_color_preview(self):
        """Update the color preview"""
        self.color_preview.setStyleSheet(f"background-color: {self.color}; border: 1px solid #cccccc;")
    
    def accept(self):
        """Handle dialog acceptance"""
        # Validate inputs
        name = self.name_edit.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Validation Error", "Category name cannot be empty.")
            return
        
        transaction_type = self.type_combo.currentData()
        
        if self.category:  # Edit existing category
            result = DataManager.update_category(
                self.category.id,
                name=name,
                type=transaction_type,
                color=self.color
            )
            
            if result:
                super().accept()
            else:
                QMessageBox.warning(self, "Error", "Failed to update category.")
        else:  # Add new category
            category_id = DataManager.add_category(
                name=name,
                transaction_type=transaction_type,
                color=self.color
            )
            
            if category_id:
                super().accept()
            else:
                QMessageBox.warning(self, "Error", "Failed to add category.") 