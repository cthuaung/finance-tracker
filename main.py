#!/usr/bin/env python
"""
Finance Tracker - A personal finance tracking application
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from finance_tracker.views.main_window import MainWindow
from finance_tracker.models.database import init_db


def main():
    """Main entry point for the application"""
    # Initialize database
    init_db()
    
    # Create application
    app = QApplication(sys.argv)
    
    # Set application name
    app.setApplicationName("Finance Tracker")
    
    # Set application style
    app.setStyle("Fusion")
    
    # Create main window
    window = MainWindow()
    window.show()
    
    # Run the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 