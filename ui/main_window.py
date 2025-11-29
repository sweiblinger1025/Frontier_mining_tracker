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
        from ui.tabs.dashboard_tab import DashboardTab
        from ui.tabs.reference_tab import ReferenceDataTab
        from ui.tabs.ledger_tab import LedgerTab
        from ui.tabs.auditor_tab import AuditorTab
        from ui.tabs.material_movement_tab import MaterialMovementTab
        from ui.tabs.inventory_tab import InventoryTab
        from ui.tabs.settings_tab import SettingsTab
        from ui.tabs.budget_planner_tab import BudgetPlannerTab
        from ui.tabs.roi_tracker_tab import ROITrackerTab
        
        # Create tabs
        for tab_name, tab_id in TABS:
            if tab_id == "dashboard":
                tab = DashboardTab(self)
                self.dashboard_tab = tab
            elif tab_id == "reference":
                tab = ReferenceDataTab()
                self.reference_tab = tab
            elif tab_id == "ledger":
                tab = LedgerTab()
                self.ledger_tab = tab
            elif tab_id == "auditor":
                tab = AuditorTab()
                self.auditor_tab = tab
            elif tab_id == "roi_tracker":
                tab = ROITrackerTab(self)
                self.roi_tracker_tab = tab
            elif tab_id == "material":
                tab = MaterialMovementTab()
                self.material_movement_tab = tab
            elif tab_id == "inventory":
                tab = InventoryTab()
                self.inventory_tab = tab
            elif tab_id == "budget_planner":
                tab = BudgetPlannerTab()
                tab.set_main_window(self)
                self.budget_planner_tab = tab
            elif tab_id == "settings":
                tab = SettingsTab()
                tab.set_main_window(self)
                self.settings_tab = tab
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
        
        # Session management
        new_session_action = QAction("📄 &New Session...", self)
        new_session_action.setShortcut("Ctrl+Shift+N")
        new_session_action.triggered.connect(self._on_new_session)
        file_menu.addAction(new_session_action)
        
        save_session_action = QAction("💾 &Save Session...", self)
        save_session_action.setShortcut("Ctrl+S")
        save_session_action.triggered.connect(self._on_save_session)
        file_menu.addAction(save_session_action)
        
        load_session_action = QAction("📂 &Load Session...", self)
        load_session_action.setShortcut("Ctrl+O")
        load_session_action.triggered.connect(self._on_load_session)
        file_menu.addAction(load_session_action)
        
        session_manager_action = QAction("🗂️ Session &Manager...", self)
        session_manager_action.triggered.connect(self._on_session_manager)
        file_menu.addAction(session_manager_action)
        
        file_menu.addSeparator()
        
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
        
        # Calculators
        fuel_calc_action = QAction("⛽ &Fuel Calculator...", self)
        fuel_calc_action.triggered.connect(self._on_fuel_calculator)
        tools_menu.addAction(fuel_calc_action)
        
        discount_calc_action = QAction("💰 &Discount Calculator...", self)
        discount_calc_action.triggered.connect(self._on_discount_calculator)
        tools_menu.addAction(discount_calc_action)
        
        split_calc_action = QAction("💵 &Split Calculator...", self)
        split_calc_action.triggered.connect(self._on_split_calculator)
        tools_menu.addAction(split_calc_action)
        
        tools_menu.addSeparator()
        
        # Import/Export
        import_action2 = QAction("📥 &Import from Excel...", self)
        import_action2.setShortcut("Ctrl+Shift+I")
        import_action2.triggered.connect(self._on_import_excel)
        tools_menu.addAction(import_action2)
        
        export_action2 = QAction("📤 &Export to Excel...", self)
        export_action2.setShortcut("Ctrl+Shift+E")
        export_action2.triggered.connect(self._on_export_excel)
        tools_menu.addAction(export_action2)
        
        tools_menu.addSeparator()
        
        # Game Tools
        advance_day_action = QAction("📅 &Advance Game Day...", self)
        advance_day_action.triggered.connect(self._on_advance_game_day)
        tools_menu.addAction(advance_day_action)
        
        challenge_status_action = QAction("🎯 C&hallenge Status...", self)
        challenge_status_action.triggered.connect(self._on_challenge_status)
        tools_menu.addAction(challenge_status_action)
        
        tools_menu.addSeparator()
        
        # Audit
        audit_action = QAction("🔍 &Audit Save File...", self)
        audit_action.triggered.connect(self._on_audit_save)
        tools_menu.addAction(audit_action)
        
        recalc_action = QAction("🔄 &Recalculate Balances", self)
        recalc_action.triggered.connect(self._on_recalculate)
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
    
    def _on_new_session(self):
        """Handle new session action."""
        from PyQt6.QtWidgets import QMessageBox
        from core.session_manager import SessionManager
        
        reply = QMessageBox.question(
            self, "New Session",
            "This will clear all current data.\n\nDo you want to save the current session first?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
        )
        
        if reply == QMessageBox.StandardButton.Cancel:
            return
        
        session_mgr = SessionManager(self)
        
        if reply == QMessageBox.StandardButton.Yes:
            # Quick save first
            from datetime import datetime
            import os
            name = f"autosave_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            filepath = os.path.join(session_mgr.SESSIONS_DIR, f"{name}.json")
            if session_mgr.save_session(filepath):
                self.status_bar.showMessage(f"Session auto-saved as {name}")
            else:
                QMessageBox.warning(self, "Warning", "Failed to auto-save current session.")
        
        if session_mgr.new_session():
            self.status_bar.showMessage("New session started")
            QMessageBox.information(self, "Success", "New session started successfully.")
        else:
            QMessageBox.warning(self, "Error", "Failed to create new session.")
    
    def _on_save_session(self):
        """Handle save session action."""
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        from core.session_manager import SessionManager
        
        session_mgr = SessionManager(self)
        
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Save Session",
            session_mgr.SESSIONS_DIR,
            "JSON Files (*.json);;All Files (*)"
        )
        
        if filepath:
            if not filepath.endswith('.json'):
                filepath += '.json'
            
            if session_mgr.save_session(filepath):
                import os
                self.status_bar.showMessage(f"Session saved: {os.path.basename(filepath)}")
                QMessageBox.information(self, "Success", "Session saved successfully.")
            else:
                QMessageBox.warning(self, "Error", "Failed to save session.")
    
    def _on_load_session(self):
        """Handle load session action."""
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        from core.session_manager import SessionManager
        
        session_mgr = SessionManager(self)
        
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Load Session",
            session_mgr.SESSIONS_DIR,
            "JSON Files (*.json);;All Files (*)"
        )
        
        if filepath:
            reply = QMessageBox.question(
                self, "Load Session",
                "This will replace all current data.\n\nContinue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                if session_mgr.load_session(filepath):
                    import os
                    self.status_bar.showMessage(f"Session loaded: {os.path.basename(filepath)}")
                    QMessageBox.information(self, "Success", "Session loaded successfully.")
                else:
                    QMessageBox.warning(self, "Error", "Failed to load session.")
    
    def _on_session_manager(self):
        """Open Session Manager dialog."""
        from core.session_manager import SessionDialog
        dialog = SessionDialog(self, parent=self)
        dialog.exec()
    
    def _on_fuel_calculator(self):
        """Open Fuel Calculator dialog."""
        from ui.dialogs.tools_dialogs import FuelCalculatorDialog
        
        # Get fuel price from settings if available
        fuel_price = 0.32
        if hasattr(self, 'settings_tab'):
            fuel_price = self.settings_tab.get_fuel_price()
        
        dialog = FuelCalculatorDialog(fuel_price=fuel_price, parent=self)
        dialog.exec()
    
    def _on_discount_calculator(self):
        """Open Discount Calculator dialog."""
        from ui.dialogs.tools_dialogs import DiscountCalculatorDialog
        
        # Get skill levels from settings if available
        vn_level = 0
        if_level = 0
        if hasattr(self, 'settings_tab'):
            vn_level = self.settings_tab.get_setting("vendor_negotiation_level") or 0
            if_level = self.settings_tab.get_setting("investment_forecasting_level") or 0
        
        dialog = DiscountCalculatorDialog(vn_level=vn_level, if_level=if_level, parent=self)
        dialog.exec()
    
    def _on_split_calculator(self):
        """Open Split Calculator dialog."""
        from ui.dialogs.tools_dialogs import SplitCalculatorDialog
        
        # Get split percentages from settings if available
        personal_pct = 0.10
        company_pct = 0.90
        if hasattr(self, 'settings_tab'):
            personal_pct = self.settings_tab.get_personal_split()
            company_pct = self.settings_tab.get_company_split()
        
        dialog = SplitCalculatorDialog(personal_pct=personal_pct, company_pct=company_pct, parent=self)
        dialog.exec()
    
    def _on_import_excel(self):
        """Open Import from Excel dialog."""
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import from Excel",
            "",
            "Excel Files (*.xlsx *.xls);;All Files (*)"
        )
        
        if file_path:
            QMessageBox.information(
                self,
                "Import",
                f"Import from: {file_path}\n\n"
                "Full import functionality coming soon!"
            )
    
    def _on_export_excel(self):
        """Open Export to Excel dialog."""
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export to Excel",
            "frontier_mining_export.xlsx",
            "Excel Files (*.xlsx);;All Files (*)"
        )
        
        if file_path:
            QMessageBox.information(
                self,
                "Export",
                f"Export to: {file_path}\n\n"
                "Full export functionality coming soon!"
            )
    
    def _on_advance_game_day(self):
        """Open Advance Game Day dialog."""
        from ui.dialogs.tools_dialogs import AdvanceGameDayDialog
        from PyQt6.QtWidgets import QMessageBox
        
        # Get current date from settings if available
        current_date = "04/23/2021"
        days_played = 1
        if hasattr(self, 'settings_tab'):
            game_date = self.settings_tab.get_setting("current_game_date")
            if game_date:
                current_date = game_date.strftime("%m/%d/%Y")
            start_date = self.settings_tab.get_setting("game_start_date")
            if start_date and game_date:
                days_played = (game_date - start_date).days + 1
        
        dialog = AdvanceGameDayDialog(current_date=current_date, days_played=days_played, parent=self)
        if dialog.exec():
            days = dialog.get_days_to_advance()
            if days > 0 and hasattr(self, 'settings_tab'):
                # Update the date in settings
                from datetime import timedelta
                current = self.settings_tab.get_setting("current_game_date")
                if current:
                    new_date = current + timedelta(days=days)
                    from PyQt6.QtCore import QDate
                    self.settings_tab.current_game_date.setDate(
                        QDate(new_date.year, new_date.month, new_date.day)
                    )
                    QMessageBox.information(
                        self,
                        "Day Advanced",
                        f"Game day advanced by {days} day(s).\n\n"
                        f"New date: {new_date.strftime('%m/%d/%Y')}"
                    )
    
    def _on_challenge_status(self):
        """Open Challenge Status dialog."""
        from ui.dialogs.tools_dialogs import ChallengeStatusDialog
        
        dialog = ChallengeStatusDialog(parent=self)
        
        # Update with current settings if available
        if hasattr(self, 'settings_tab'):
            settings = self.settings_tab.settings
            oil_enabled, oil_cap, oil_sold = self.settings_tab.get_oil_cap()
            
            # Get difficulty description
            difficulty = settings.get("difficulty_level", "Easy")
            presets = self.settings_tab.DIFFICULTY_PRESETS
            description = presets.get(difficulty, {}).get("description", "")
            
            dialog.update_status(
                difficulty=difficulty,
                description=description,
                oil_sold=oil_sold,
                oil_cap=oil_cap,
                oil_enabled=oil_enabled,
                daily_enabled=settings.get("daily_limit_enabled", False),
                daily_limit=settings.get("daily_limit_amount", 0),
                daily_spent=0,  # Would need to calculate from ledger
                bar_threshold=settings.get("bar_threshold", 5000),
                current_balance=0,  # Would need to get from ledger
            )
        
        dialog.exec()
    
    def _on_recalculate(self):
        """Recalculate all balances."""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(
            self,
            "Recalculate",
            "Recalculate balances functionality coming soon!"
        )
