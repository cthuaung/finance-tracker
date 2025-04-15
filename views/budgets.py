"""
Budgets widget for the finance tracker application
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QScrollArea, QFormLayout, QComboBox, QSpinBox, QDoubleSpinBox,
    QDialog, QDialogButtonBox, QGroupBox, QFrame, QMessageBox,
    QProgressBar
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QColor

from datetime import datetime
import calendar

from ..models.data_manager import DataManager
from ..models.database import TransactionType
from ..utils.visualizations import MplCanvas, create_progress_bars


class BudgetsWidget(QWidget):
    """Widget for managing budgets"""
    
    def __init__(self):
        super().__init__()
        
        self.setup_ui()
        self.load_budgets()
    
    def setup_ui(self):
        """Set up the budgets UI"""
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)
        
        # Header section
        header_layout = QHBoxLayout()
        budgets_title = QLabel("Budgets")
        budgets_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        header_layout.addWidget(budgets_title)
        header_layout.addStretch()
        
        # Month/Year selector
        self.month_combo = QComboBox()
        for i, month in enumerate(calendar.month_name[1:], 1):
            self.month_combo.addItem(month, i)
        
        # Set current month
        current_month = datetime.now().month
        self.month_combo.setCurrentIndex(current_month - 1)
        
        self.year_spin = QSpinBox()
        self.year_spin.setRange(2000, 2100)
        self.year_spin.setValue(datetime.now().year)
        
        header_layout.addWidget(QLabel("Month:"))
        header_layout.addWidget(self.month_combo)
        header_layout.addWidget(QLabel("Year:"))
        header_layout.addWidget(self.year_spin)
        
        # Connect signals
        self.month_combo.currentIndexChanged.connect(self.load_budgets)
        self.year_spin.valueChanged.connect(self.load_budgets)
        
        # Add new budget button
        self.add_button = QPushButton("Set Budget")
        self.add_button.clicked.connect(self.set_budget)
        header_layout.addWidget(self.add_button)
        
        self.main_layout.addLayout(header_layout)
        
        # Budget progress chart
        self.chart_frame = QFrame()
        self.chart_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.chart_frame.setStyleSheet("background-color: white; border-radius: 8px; border: 1px solid #e1e1e1;")
        self.chart_layout = QVBoxLayout(self.chart_frame)
        
        self.chart_title = QLabel("Budget Progress")
        self.chart_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.chart_layout.addWidget(self.chart_title)
        
        self.chart_container = QVBoxLayout()
        self.chart_layout.addLayout(self.chart_container)
        
        self.main_layout.addWidget(self.chart_frame)
        
        # Budget items section
        self.budget_items_container = QVBoxLayout()
        self.main_layout.addLayout(self.budget_items_container)
    
    def load_budgets(self):
        """Load budgets for the selected month and year"""
        month = self.month_combo.currentData()
        year = self.year_spin.value()
        
        # Update chart title
        month_name = calendar.month_name[month]
        self.chart_title.setText(f"Budget Progress - {month_name} {year}")
        
        # Get budget status
        budget_status = DataManager.get_budget_status(month, year)
        
        # Clear previous items
        self.clear_budget_items()
        
        # Update chart
        self.update_budget_chart(budget_status)
        
        # Create budget items
        self.create_budget_items(budget_status)
    
    def clear_budget_items(self):
        """Clear all budget items from the container"""
        # Clear the chart container
        for i in reversed(range(self.chart_container.count())):
            widget = self.chart_container.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        # Clear the budget items container
        for i in reversed(range(self.budget_items_container.count())):
            layout_item = self.budget_items_container.itemAt(i)
            if layout_item.widget():
                layout_item.widget().deleteLater()
    
    def update_budget_chart(self, budget_status):
        """Update the budget progress chart"""
        if budget_status:
            # Create chart
            fig = create_progress_bars(
                data=budget_status,
                title="Budget Progress"
            )
            
            # Create canvas for the chart
            chart_canvas = MplCanvas(fig)
            
            # Add to layout
            self.chart_container.addWidget(chart_canvas)
        else:
            # Show message when no budgets are set
            no_data_label = QLabel("No budgets set for the selected month. Use the 'Set Budget' button to create budgets.")
            no_data_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_data_label.setStyleSheet("color: #888; font-style: italic; padding: 20px;")
            self.chart_container.addWidget(no_data_label)
    
    def create_budget_items(self, budget_status):
        """Create budget item cards for each category"""
        if not budget_status:
            # Show message
            message = QLabel("No budgets have been set for this month. Click 'Set Budget' to create a budget.")
            message.setAlignment(Qt.AlignmentFlag.AlignCenter)
            message.setStyleSheet("padding: 20px; font-style: italic; color: #888;")
            self.budget_items_container.addWidget(message)
            return
        
        # Create a group for the budget items
        budget_group = QGroupBox("Budget Details")
        budget_grid = QVBoxLayout(budget_group)
        
        # Sort budget status by percentage (highest first)
        budget_status = sorted(budget_status, key=lambda x: x['percentage'], reverse=True)
        
        # Create a budget item for each category
        for item in budget_status:
            budget_item = BudgetItemWidget(item)
            budget_grid.addWidget(budget_item)
        
        self.budget_items_container.addWidget(budget_group)
    
    def set_budget(self):
        """Show dialog to set a budget for a category"""
        dialog = BudgetDialog(self, self.month_combo.currentData(), self.year_spin.value())
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_budgets()


class BudgetItemWidget(QFrame):
    """Widget for displaying a single budget item"""
    
    def __init__(self, budget_data):
        super().__init__()
        
        self.budget_data = budget_data
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the budget item UI"""
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setStyleSheet("border: 1px solid #e1e1e1; border-radius: 5px; background-color: white; margin: 5px;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Category name
        category_layout = QHBoxLayout()
        
        # Color indicator
        color_indicator = QFrame()
        color_indicator.setFixedSize(16, 16)
        color_indicator.setStyleSheet(f"background-color: {self.budget_data['color']}; border-radius: 8px;")
        category_layout.addWidget(color_indicator)
        
        # Category name
        category_name = QLabel(self.budget_data['category_name'])
        category_name.setStyleSheet("font-weight: bold; font-size: 14px;")
        category_layout.addWidget(category_name)
        category_layout.addStretch()
        
        # Budget amount
        budget_amount = QLabel(f"Budget: ${self.budget_data['budget_amount']:.2f}")
        category_layout.addWidget(budget_amount)
        
        layout.addLayout(category_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(min(int(self.budget_data['percentage']), 100))
        
        # Set color based on percentage
        percentage = self.budget_data['percentage']
        if percentage < 70:
            self.progress_bar.setStyleSheet("QProgressBar::chunk { background-color: #27ae60; }")
        elif percentage < 90:
            self.progress_bar.setStyleSheet("QProgressBar::chunk { background-color: #f39c12; }")
        else:
            self.progress_bar.setStyleSheet("QProgressBar::chunk { background-color: #e74c3c; }")
        
        layout.addWidget(self.progress_bar)
        
        # Details
        details_layout = QHBoxLayout()
        
        actual_amount = QLabel(f"Spent: ${self.budget_data['actual_amount']:.2f}")
        details_layout.addWidget(actual_amount)
        
        details_layout.addStretch()
        
        remaining = self.budget_data['remaining']
        remaining_label = QLabel(f"Remaining: ${remaining:.2f}")
        if remaining < 0:
            remaining_label.setStyleSheet("color: #e74c3c;")
        details_layout.addWidget(remaining_label)
        
        details_layout.addStretch()
        
        percentage_label = QLabel(f"{self.budget_data['percentage']:.1f}%")
        details_layout.addWidget(percentage_label)
        
        layout.addLayout(details_layout)


class BudgetDialog(QDialog):
    """Dialog for setting a budget for a category"""
    
    def __init__(self, parent=None, month=None, year=None):
        super().__init__(parent)
        
        self.month = month or datetime.now().month
        self.year = year or datetime.now().year
        
        self.setWindowTitle(f"Set Budget for {calendar.month_name[self.month]} {self.year}")
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the dialog UI"""
        self.resize(400, 200)
        
        layout = QVBoxLayout(self)
        
        # Form layout for fields
        form_layout = QFormLayout()
        
        # Category selector
        self.category_combo = QComboBox()
        self.load_categories()
        form_layout.addRow("Category:", self.category_combo)
        
        # Budget amount
        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setRange(0, 9999999.99)
        self.amount_spin.setDecimals(2)
        self.amount_spin.setSingleStep(10.0)
        self.amount_spin.setPrefix("$ ")
        form_layout.addRow("Budget Amount:", self.amount_spin)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def load_categories(self):
        """Load expense categories for the selector"""
        # Clear the combobox
        self.category_combo.clear()
        
        # Add expense categories
        categories = DataManager.get_categories(transaction_type=TransactionType.EXPENSE)
        for category in categories:
            self.category_combo.addItem(category.name, category.id)
    
    def accept(self):
        """Handle dialog acceptance"""
        # Validate inputs
        if self.category_combo.count() == 0:
            QMessageBox.warning(self, "Error", "No expense categories available. Please create some categories first.")
            return
        
        category_id = self.category_combo.currentData()
        amount = self.amount_spin.value()
        
        if amount <= 0:
            QMessageBox.warning(self, "Validation Error", "Budget amount must be greater than zero.")
            return
        
        # Set the budget
        result = DataManager.set_budget(
            category_id=category_id,
            amount=amount,
            month=self.month,
            year=self.year
        )
        
        if result:
            super().accept()
        else:
            QMessageBox.warning(self, "Error", "Failed to set budget.") 