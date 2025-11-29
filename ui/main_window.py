"""
Main Window - Primary application window with tab navigation
"""

from PyQt6.QtWidgets import (
    QMainWindow, 
    QTabWidget, 
    QWidget, 
    QVBoxLayout,
    QLabel,
    QStatusBar,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction

from config.settings import (
    APP_NAME, 
    APP_VERSION,
    WINDOW_MIN_WIDTH,
    WINDOW_MIN_HEIGHT,
    WINDOW_DEFAULT_WIDTH,
    WINDOW_DEFAULT_HEIGHT,
    TABS,
)


class MainWindow(QMainWindow):
    """Main application window containing the tab widget."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setMinimumSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.resize(WINDOW_DEFAULT_WIDTH, WINDOW_DEFAULT_HEIGHT)
        
        # Initialize UI components
        self._setup_central_widget()
        self._setup_tabs()
        self._setup_menubar()
        self._setup_statusbar()
    
    def _setup_central_widget(self):
        """Create the central widget and main layout."""
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
    
    def _setup_tabs(self):
        """Create the tab widget and add all tabs."""
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        self.tab_widget.setMovable(False)  # Keep tabs in fixed order
        
        # Store references to tab widgets
        self.tabs = {}
        
        # Import actual tab implementations
        from ui.tabs.reference_tab import ReferenceDataTab
        from ui.tabs.ledger_tab import LedgerTab
        from ui.tabs.auditor_tab import AuditorTab
        from ui.tabs.material_movement_tab import MaterialMovementTab
        from ui.tabs.inventory_tab import InventoryTab
        
        # Create tabs
        for tab_name, tab_id in TABS:
            if tab_id == "reference":
                tab = ReferenceDataTab()
                self.reference_tab = tab
            elif tab_id == "ledger":
                tab = LedgerTab()
                self.ledger_tab = tab
            elif tab_id == "auditor":
                tab = AuditorTab()
                self.auditor_tab = tab
            elif tab_id == "material":
                tab = MaterialMovementTab()
                self.material_movement_tab = tab
            elif tab_id == "inventory":
                tab = InventoryTab()
                self.inventory_tab = tab
            else:
                # Placeholder for other tabs
                tab = self._create_placeholder_tab(tab_name)
            
            self.tab_widget.addTab(tab, tab_name)
            self.tabs[tab_id] = tab
        
        # Connect tabs that need references to each other
        if hasattr(self, 'material_movement_tab') and hasattr(self, 'ledger_tab'):
            self.material_movement_tab.set_ledger_tab(self.ledger_tab)
        
        self.main_layout.addWidget(self.tab_widget)
    
    def _create_placeholder_tab(self, name: str) -> QWidget:
        """Create a placeholder tab widget (to be replaced later)."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        label = QLabel(f"{name}\n\n(Coming Soon)")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                color: #666;
            }
        """)
        layout.addWidget(label)
        
        return widget
    
    def _setup_menubar(self):
        """Create the application menu bar."""
        menubar = self.menuBar()
        
        # File Menu
        file_menu = menubar.addMenu("&File")
        
        new_action = QAction("&New Transaction", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self._on_new_transaction)
        file_menu.addAction(new_action)
        
        file_menu.addSeparator()
        
        import_action = QAction("&Import from Excel...", self)
        import_action.setShortcut("Ctrl+I")
        file_menu.addAction(import_action)
        
        export_action = QAction("&Export to Excel...", self)
        export_action.setShortcut("Ctrl+E")
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit Menu
        edit_menu = menubar.addMenu("&Edit")
        
        undo_action = QAction("&Undo", self)
        undo_action.setShortcut("Ctrl+Z")
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("&Redo", self)
        redo_action.setShortcut("Ctrl+Y")
        edit_menu.addAction(redo_action)
        
        # Tools Menu
        tools_menu = menubar.addMenu("&Tools")
        
        audit_action = QAction("&Audit Save File...", self)
        audit_action.triggered.connect(self._on_audit_save)
        tools_menu.addAction(audit_action)
        
        recalc_action = QAction("&Recalculate Balances", self)
        tools_menu.addAction(recalc_action)
        
        # Help Menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self._on_about)
        help_menu.addAction(about_action)
    
    def _setup_statusbar(self):
        """Create the status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    # --- Menu Action Handlers ---
    
    def _on_new_transaction(self):
        """Handle new transaction action."""
        # Switch to Ledger tab
        ledger_index = [tab_id for _, tab_id in TABS].index("ledger")
        self.tab_widget.setCurrentIndex(ledger_index)
        self.status_bar.showMessage("New transaction - Ledger tab selected")
    
    def _on_audit_save(self):
        """Handle audit save file action."""
        # Switch to Auditor tab
        auditor_index = [tab_id for _, tab_id in TABS].index("auditor")
        self.tab_widget.setCurrentIndex(auditor_index)
        self.status_bar.showMessage("Auditor tab selected")
    
    def _on_about(self):
        """Show about dialog."""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.about(
            self,
            f"About {APP_NAME}",
            f"{APP_NAME} v{APP_VERSION}\n\n"
            "A mining operations tracker for Out of Ore.\n\n"
            "Track transactions, manage inventory, and audit save files."
        )
