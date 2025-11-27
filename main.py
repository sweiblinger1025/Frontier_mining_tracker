#!/usr/bin/env python3
"""
Frontier Mining Tracker
=======================
A PyQt6 application for tracking mining operations in Out of Ore.

Features:
- Transaction ledger with running balances
- ROI tracking and analysis
- Inventory management
- Save file auditing for validation

Usage:
    python main.py
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from config.settings import APP_NAME, ensure_directories
from ui.main_window import MainWindow


def main():
    """Application entry point."""
    # Ensure necessary directories exist
    ensure_directories()
    
    # Create the application
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    
    # Optional: Set application-wide style
    app.setStyle("Fusion")  # Consistent look across platforms
    
    # Create and show the main window
    window = MainWindow()
    window.show()
    
    # Run the event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
