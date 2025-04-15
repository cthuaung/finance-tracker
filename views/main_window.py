"""
Main window for the finance tracker application
"""

from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStatusBar, QMessageBox, QSplitter,
    QSizePolicy, QComboBox, QDateEdit, QSpinBox, QDoubleSpinBox,
    QTableView, QLineEdit, QFormLayout, QDialog, QDialogButtonBox,
    QGroupBox, QScrollArea, QFrame, QToolBar, QApplication, QMenu,
    QToolButton, QCheckBox, QColorDialog
)
from PyQt6.QtCore import Qt, QDate, QDateTime, QSize, pyqtSlot, QSortFilterProxyModel
from PyQt6.QtGui import QIcon, QAction, QFont, QColor, QPalette, QStandardItemModel, QStandardItem

import sys
import os
from datetime import datetime, date, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from ..utils.visualizations import MplCanvas, create_pie_chart, create_bar_chart, create_line_chart, create_progress_bars
from ..models.database import init_db, TransactionType
from .dashboard import DashboardWidget
from .transactions import TransactionsWidget
from .categories import CategoriesWidget
from .reports import ReportsWidget
from .budgets import BudgetsWidget


class MainWindow(QMainWindow):
    """Main window of the Finance Tracker application"""

    def __init__(self):
        super().__init__()
        
        # Initialize database
        init_db()
        
        # Setup UI
        self.setWindowTitle("Finance Tracker")
        self.resize(1200, 800)
        self.setMinimumSize(800, 600)
        
        # Set up main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)
        
        # Create tabs
        self.dashboard_widget = DashboardWidget()
        self.transactions_widget = TransactionsWidget()
        self.categories_widget = CategoriesWidget()
        self.reports_widget = ReportsWidget()
        self.budgets_widget = BudgetsWidget()
        
        # Add tabs to tab widget
        self.tab_widget.addTab(self.dashboard_widget, "Dashboard")
        self.tab_widget.addTab(self.transactions_widget, "Transactions")
        self.tab_widget.addTab(self.categories_widget, "Categories")
        self.tab_widget.addTab(self.budgets_widget, "Budgets")
        self.tab_widget.addTab(self.reports_widget, "Reports")
        
        # Connect signals
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        
        # Setup status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Initialize application style
        self.setup_application_style()
    
    def setup_application_style(self):
        """Set up the application style and theme"""
        # Set the application-wide font
        font = QFont("Segoe UI", 10)
        QApplication.setFont(font)
        
        # You could set a stylesheet for the entire application here
        # For example:
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QTabWidget::pane {
                border: 1px solid #cccccc;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #e1e1e1;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom-color: white;
            }
            QTableView {
                alternate-background-color: #f9f9f9;
                selection-background-color: #0078d7;
                selection-color: white;
                gridline-color: #dcdcdc;
            }
            QPushButton {
                background-color: #0078d7;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #0063b1;
            }
            QPushButton:pressed {
                background-color: #004e8c;
            }
            QLineEdit, QComboBox, QDateEdit, QSpinBox, QDoubleSpinBox {
                padding: 6px;
                border: 1px solid #cccccc;
                border-radius: 4px;
            }
            QComboBox::drop-down, QDateEdit::drop-down {
                border: 0px;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #cccccc;
                border-radius: 4px;
                margin-top: 16px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 10px;
                padding: 0 3px;
            }
        """)
    
    @pyqtSlot(int)
    def on_tab_changed(self, index):
        """Handle tab change events"""
        # Refresh data when switching to certain tabs
        if index == 0:  # Dashboard
            self.dashboard_widget.refresh_dashboard()
        elif index == 1:  # Transactions
            self.transactions_widget.load_transactions()
        elif index == 2:  # Categories
            self.categories_widget.load_categories()
        elif index == 3:  # Budgets
            self.budgets_widget.load_budgets()
        elif index == 4:  # Reports
            self.reports_widget.update_report() 