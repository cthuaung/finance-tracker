"""
Transactions widget for the finance tracker application
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTableView, QDialog, QFormLayout, QComboBox, QDateEdit,
    QDoubleSpinBox, QLineEdit, QDialogButtonBox, QHeaderView,
    QFrame, QMessageBox
)
from PyQt6.QtCore import Qt, QDate, QSortFilterProxyModel, QAbstractTableModel, QModelIndex
from PyQt6.QtGui import QColor

from datetime import datetime

from ..models.data_manager import DataManager
from ..models.database import TransactionType


class TransactionTableModel(QAbstractTableModel):
    """Model for the transactions table"""
    
    def __init__(self, transactions=None):
        super().__init__()
        self.transactions = transactions or []
        self.headers = ["Date", "Type", "Category", "Amount", "Description"]
        # Pre-fetch category information to avoid detached instance errors
        self.category_names = {}
        self.populate_category_names()
    
    def populate_category_names(self):
        """Populate category names for all transactions"""
        if not self.transactions:
            return
            
        # Get all category IDs that are in our transactions
        category_ids = set()
        for t in self.transactions:
            if t.category_id:
                category_ids.add(t.category_id)
                
        # If we have no categories, we're done
        if not category_ids:
            return
            
        # Fetch all categories in a single query
        from ..models.database import Session, Category
        session = Session()
        try:
            categories = session.query(Category).filter(Category.id.in_(category_ids)).all()
            category_map = {cat.id: cat.name for cat in categories}
            
            # Map category names to transactions
            for t in self.transactions:
                if t.category_id:
                    self.category_names[t.id] = category_map.get(t.category_id, "N/A")
                else:
                    self.category_names[t.id] = "N/A"
        finally:
            session.close()
    
    def rowCount(self, parent=QModelIndex()):
        return len(self.transactions)
    
    def columnCount(self, parent=QModelIndex()):
        return len(self.headers)
    
    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < len(self.transactions)):
            return None
        
        transaction = self.transactions[index.row()]
        
        if role == Qt.ItemDataRole.DisplayRole:
            col = index.column()
            if col == 0:  # Date
                return transaction.date.strftime("%Y-%m-%d")
            elif col == 1:  # Type
                return transaction.type.value.capitalize()
            elif col == 2:  # Category
                return self.category_names.get(transaction.id, "N/A")
            elif col == 3:  # Amount
                return f"${transaction.amount:.2f}"
            elif col == 4:  # Description
                return transaction.description or ""
        
        elif role == Qt.ItemDataRole.ForegroundRole:
            col = index.column()
            if col == 3:  # Amount
                if transaction.type == TransactionType.INCOME:
                    return QColor("#27ae60")  # Green for income
                else:
                    return QColor("#e74c3c")  # Red for expenses
        
        # Store the actual transaction object for later use
        elif role == Qt.ItemDataRole.UserRole:
            return transaction
        
        return None
    
    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self.headers[section]
        return None
    
    def setTransactions(self, transactions):
        self.beginResetModel()
        self.transactions = transactions
        # Refresh category names
        self.category_names = {}
        self.populate_category_names()
        self.endResetModel()


class TransactionsWidget(QWidget):
    """Widget for managing transactions"""
    
    def __init__(self):
        super().__init__()
        
        self.setup_ui()
        self.load_transactions()
    
    def setup_ui(self):
        """Set up the transactions UI"""
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)
        
        # Header section
        header_layout = QHBoxLayout()
        transactions_title = QLabel("Transactions")
        transactions_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        header_layout.addWidget(transactions_title)
        header_layout.addStretch()
        
        # Add new transaction button
        self.add_button = QPushButton("Add Transaction")
        self.add_button.clicked.connect(self.add_transaction)
        header_layout.addWidget(self.add_button)
        
        self.main_layout.addLayout(header_layout)
        
        # Filter section
        filter_frame = QFrame()
        filter_frame.setFrameShape(QFrame.Shape.StyledPanel)
        filter_frame.setStyleSheet("background-color: #f9f9f9; border-radius: 5px; padding: 5px;")
        
        filter_layout = QHBoxLayout(filter_frame)
        
        # Add filter by type
        filter_layout.addWidget(QLabel("Type:"))
        self.type_filter = QComboBox()
        self.type_filter.addItem("All", None)
        self.type_filter.addItem("Income", TransactionType.INCOME)
        self.type_filter.addItem("Expense", TransactionType.EXPENSE)
        self.type_filter.currentIndexChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.type_filter)
        
        # Add filter by category
        filter_layout.addWidget(QLabel("Category:"))
        self.category_filter = QComboBox()
        self.category_filter.addItem("All", None)
        self.category_filter.currentIndexChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.category_filter)
        
        # Add date range filters
        filter_layout.addWidget(QLabel("From:"))
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate().addMonths(-1))
        self.date_from.dateChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.date_from)
        
        filter_layout.addWidget(QLabel("To:"))
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())
        self.date_to.dateChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.date_to)
        
        # Reset filters button
        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset_filters)
        filter_layout.addWidget(self.reset_button)
        
        self.main_layout.addWidget(filter_frame)
        
        # Transactions table
        self.transactions_table = QTableView()
        self.transactions_table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.transactions_table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.transactions_table.setAlternatingRowColors(True)
        self.transactions_table.setSortingEnabled(True)
        self.transactions_table.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        
        # Create table model
        self.table_model = TransactionTableModel()
        
        # Create proxy model for sorting and filtering
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.table_model)
        
        # Set proxy model to table
        self.transactions_table.setModel(self.proxy_model)
        
        # Set column properties
        header = self.transactions_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Date
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Type
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Category
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Amount
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)  # Description
        
        # Add table to layout
        self.main_layout.addWidget(self.transactions_table)
    
    def load_transactions(self):
        """Load transactions from the database"""
        # Get transactions
        transactions = DataManager.get_transactions()
        
        # Set transactions to the model
        self.table_model.setTransactions(transactions)
        
        # Load categories for filter
        self.load_categories()
        
        # Apply any active filters
        self.apply_filters()
    
    def load_categories(self):
        """Load categories for the filter dropdown"""
        # Clear and repopulate the combobox
        self.category_filter.clear()
        self.category_filter.addItem("All", None)
        
        # Add categories to the filter
        categories = DataManager.get_categories()
        for category in categories:
            self.category_filter.addItem(category.name, category.id)
    
    def apply_filters(self):
        """Apply filters to the transaction table"""
        # Get filter values
        transaction_type = self.type_filter.currentData()
        category_id = self.category_filter.currentData()
        date_from = self.date_from.date().toPyDate()
        date_to = self.date_to.date().toPyDate()
        
        # Get filtered transactions
        transactions = DataManager.get_transactions(
            start_date=date_from,
            end_date=date_to,
            category_id=category_id,
            transaction_type=transaction_type
        )
        
        # Update the model
        self.table_model.setTransactions(transactions)
    
    def reset_filters(self):
        """Reset all filters to their defaults"""
        self.type_filter.setCurrentIndex(0)
        self.category_filter.setCurrentIndex(0)
        self.date_from.setDate(QDate.currentDate().addMonths(-1))
        self.date_to.setDate(QDate.currentDate())
        
        self.apply_filters()
    
    def add_transaction(self):
        """Show dialog to add a new transaction"""
        dialog = TransactionDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_transactions()


class TransactionDialog(QDialog):
    """Dialog for adding or editing a transaction"""
    
    def __init__(self, parent=None, transaction=None):
        super().__init__(parent)
        
        self.transaction = transaction
        self.setWindowTitle("Add Transaction")
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the dialog UI"""
        self.resize(400, 300)
        
        layout = QVBoxLayout(self)
        
        # Form layout for fields
        form_layout = QFormLayout()
        
        # Transaction type
        self.type_combo = QComboBox()
        self.type_combo.addItem("Income", TransactionType.INCOME)
        self.type_combo.addItem("Expense", TransactionType.EXPENSE)
        self.type_combo.currentIndexChanged.connect(self.on_type_changed)
        form_layout.addRow("Type:", self.type_combo)
        
        # Amount
        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setRange(0.01, 9999999.99)
        self.amount_spin.setDecimals(2)
        self.amount_spin.setSingleStep(1.0)
        self.amount_spin.setPrefix("$ ")
        form_layout.addRow("Amount:", self.amount_spin)
        
        # Date
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        form_layout.addRow("Date:", self.date_edit)
        
        # Category
        self.category_combo = QComboBox()
        form_layout.addRow("Category:", self.category_combo)
        
        # Description
        self.description_edit = QLineEdit()
        form_layout.addRow("Description:", self.description_edit)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Load categories initially
        self.load_categories()
    
    def load_categories(self):
        """Load categories based on the selected transaction type"""
        # Get the current transaction type
        transaction_type = self.type_combo.currentData()
        
        # Clear and reload categories
        self.category_combo.clear()
        
        # Add categories based on type
        categories = DataManager.get_categories(transaction_type=transaction_type)
        for category in categories:
            self.category_combo.addItem(category.name, category.id)
    
    def on_type_changed(self, index):
        """Handle transaction type change"""
        self.load_categories()
    
    def accept(self):
        """Handle dialog acceptance"""
        # Validate inputs
        amount = self.amount_spin.value()
        if amount <= 0:
            QMessageBox.warning(self, "Validation Error", "Amount must be greater than zero.")
            return
        
        transaction_type = self.type_combo.currentData()
        category_id = self.category_combo.currentData()
        date_value = self.date_edit.date().toPyDate()
        description = self.description_edit.text().strip()
        
        # Add new transaction
        transaction_id = DataManager.add_transaction(
            amount=amount,
            description=description,
            date=date_value,
            transaction_type=transaction_type,
            category_id=category_id
        )
        
        if transaction_id:
            super().accept()
        else:
            QMessageBox.warning(self, "Error", "Failed to add transaction.") 