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
        from ui.tabs.production_tab import ProductionTab
        
        # Create tabs
        for tab_name, tab_id in TABS:
            if tab_id == "dashboard":
                tab = DashboardTab(self)
                self.dashboard_tab = tab
            elif tab_id == "reference":
                tab = ReferenceDataTab()
                self.reference_tab = tab
            elif tab_id == "ledger":
                tab = LedgerTab(main_window=self)
                self.ledger_tab = tab
            elif tab_id == "auditor":
                tab = AuditorTab()
                self.auditor_tab = tab
            elif tab_id == "roi_tracker":
                tab = ROITrackerTab(self)
                self.roi_tracker_tab = tab
            elif tab_id == "production":
                tab = ProductionTab(self)
                self.production_tab = tab
            elif tab_id == "material":
                tab = MaterialMovementTab()
                self.material_movement_tab = tab
            elif tab_id == "inventory":
                tab = InventoryTab(main_window=self)
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
        
        # Refresh ledger opening row now that settings_tab exists
        if hasattr(self, 'ledger_tab'):
            self.ledger_tab._populate_opening_row()
        
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
        
        # ========== FILE MENU ==========
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
        
        # Quick actions
        new_transaction_action = QAction("➕ &New Transaction", self)
        new_transaction_action.setShortcut("Ctrl+N")
        new_transaction_action.triggered.connect(self._on_new_transaction)
        file_menu.addAction(new_transaction_action)
        
        new_investment_action = QAction("📈 New &Investment", self)
        new_investment_action.setShortcut("Ctrl+Shift+I")
        new_investment_action.triggered.connect(self._on_new_investment)
        file_menu.addAction(new_investment_action)
        
        file_menu.addSeparator()
        
        # Import/Export
        import_action = QAction("📥 &Import from Excel...", self)
        import_action.setShortcut("Ctrl+I")
        import_action.triggered.connect(self._on_import_excel)
        file_menu.addAction(import_action)
        
        export_action = QAction("📤 &Export to Excel...", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self._on_export_excel)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("❌ E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # ========== EDIT MENU ==========
        edit_menu = menubar.addMenu("&Edit")
        
        undo_action = QAction("↩️ &Undo", self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.setEnabled(False)  # Placeholder for future
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("↪️ &Redo", self)
        redo_action.setShortcut("Ctrl+Y")
        redo_action.setEnabled(False)  # Placeholder for future
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        delete_selected_action = QAction("🗑️ &Delete Selected", self)
        delete_selected_action.setShortcut("Delete")
        delete_selected_action.triggered.connect(self._on_delete_selected)
        edit_menu.addAction(delete_selected_action)
        
        edit_menu.addSeparator()
        
        preferences_action = QAction("⚙️ &Preferences...", self)
        preferences_action.setShortcut("Ctrl+,")
        preferences_action.triggered.connect(self._on_preferences)
        edit_menu.addAction(preferences_action)
        
        # ========== VIEW MENU ==========
        view_menu = menubar.addMenu("&View")
        
        # Tab navigation
        dashboard_action = QAction("📊 &Dashboard", self)
        dashboard_action.setShortcut("Ctrl+1")
        dashboard_action.triggered.connect(lambda: self._go_to_tab("dashboard"))
        view_menu.addAction(dashboard_action)
        
        ledger_action = QAction("📒 &Ledger", self)
        ledger_action.setShortcut("Ctrl+2")
        ledger_action.triggered.connect(lambda: self._go_to_tab("ledger"))
        view_menu.addAction(ledger_action)
        
        reference_action = QAction("📚 &Reference Data", self)
        reference_action.setShortcut("Ctrl+3")
        reference_action.triggered.connect(lambda: self._go_to_tab("reference"))
        view_menu.addAction(reference_action)
        
        auditor_action = QAction("🔍 &Auditor", self)
        auditor_action.setShortcut("Ctrl+4")
        auditor_action.triggered.connect(lambda: self._go_to_tab("auditor"))
        view_menu.addAction(auditor_action)
        
        roi_action = QAction("📈 &ROI Tracker", self)
        roi_action.setShortcut("Ctrl+5")
        roi_action.triggered.connect(lambda: self._go_to_tab("roi_tracker"))
        view_menu.addAction(roi_action)
        
        inventory_action = QAction("📦 &Inventory", self)
        inventory_action.setShortcut("Ctrl+6")
        inventory_action.triggered.connect(lambda: self._go_to_tab("inventory"))
        view_menu.addAction(inventory_action)
        
        material_action = QAction("🚛 &Material Movement", self)
        material_action.setShortcut("Ctrl+7")
        material_action.triggered.connect(lambda: self._go_to_tab("material"))
        view_menu.addAction(material_action)
        
        budget_action = QAction("💰 &Budget Planner", self)
        budget_action.setShortcut("Ctrl+8")
        budget_action.triggered.connect(lambda: self._go_to_tab("budget_planner"))
        view_menu.addAction(budget_action)
        
        settings_action = QAction("⚙️ &Settings", self)
        settings_action.setShortcut("Ctrl+9")
        settings_action.triggered.connect(lambda: self._go_to_tab("settings"))
        view_menu.addAction(settings_action)
        
        view_menu.addSeparator()
        
        refresh_action = QAction("🔄 &Refresh Dashboard", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self._on_refresh_dashboard)
        view_menu.addAction(refresh_action)
        
        # ========== TOOLS MENU ==========
        tools_menu = menubar.addMenu("&Tools")
        
        # Calculators submenu
        calc_menu = tools_menu.addMenu("🧮 &Calculators")
        
        fuel_calc_action = QAction("⛽ &Fuel Calculator...", self)
        fuel_calc_action.triggered.connect(self._on_fuel_calculator)
        calc_menu.addAction(fuel_calc_action)
        
        discount_calc_action = QAction("💰 &Discount Calculator...", self)
        discount_calc_action.triggered.connect(self._on_discount_calculator)
        calc_menu.addAction(discount_calc_action)
        
        split_calc_action = QAction("💵 &Split Calculator...", self)
        split_calc_action.triggered.connect(self._on_split_calculator)
        calc_menu.addAction(split_calc_action)
        
        tools_menu.addSeparator()
        
        # Game Tools
        advance_day_action = QAction("📅 &Advance Game Day...", self)
        advance_day_action.triggered.connect(self._on_advance_game_day)
        tools_menu.addAction(advance_day_action)
        
        challenge_status_action = QAction("🎯 C&hallenge Status...", self)
        challenge_status_action.triggered.connect(self._on_challenge_status)
        tools_menu.addAction(challenge_status_action)
        
        tools_menu.addSeparator()
        
        # Audit/Validation
        audit_action = QAction("🔍 &Audit Save File...", self)
        audit_action.triggered.connect(self._on_audit_save)
        tools_menu.addAction(audit_action)
        
        recalc_action = QAction("🔄 &Recalculate Balances", self)
        recalc_action.triggered.connect(self._on_recalculate)
        tools_menu.addAction(recalc_action)
        
        validate_action = QAction("✅ &Validate Data...", self)
        validate_action.triggered.connect(self._on_validate_data)
        tools_menu.addAction(validate_action)
        
        # ========== HELP MENU ==========
        help_menu = menubar.addMenu("&Help")
        
        quick_start_action = QAction("🚀 &Quick Start Guide", self)
        quick_start_action.setShortcut("F1")
        quick_start_action.triggered.connect(self._on_quick_start)
        help_menu.addAction(quick_start_action)
        
        shortcuts_action = QAction("⌨️ &Keyboard Shortcuts...", self)
        shortcuts_action.triggered.connect(self._on_keyboard_shortcuts)
        help_menu.addAction(shortcuts_action)
        
        help_menu.addSeparator()
        
        game_reference_action = QAction("🎮 &Game Reference...", self)
        game_reference_action.triggered.connect(self._on_game_reference)
        help_menu.addAction(game_reference_action)
        
        help_menu.addSeparator()
        
        check_updates_action = QAction("🔄 Check for &Updates...", self)
        check_updates_action.triggered.connect(self._on_check_updates)
        help_menu.addAction(check_updates_action)
        
        help_menu.addSeparator()
        
        about_action = QAction("ℹ️ &About", self)
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
        
        try:
            # Recalculate ledger balances
            if hasattr(self, 'ledger_tab'):
                self.ledger_tab._recalculate_balances()
            
            # Refresh dashboard
            if hasattr(self, 'dashboard_tab'):
                self.dashboard_tab.refresh_dashboard()
            
            self.status_bar.showMessage("Balances recalculated")
            QMessageBox.information(
                self,
                "Recalculate",
                "All balances have been recalculated successfully."
            )
        except Exception as e:
            QMessageBox.warning(
                self,
                "Error",
                f"Error recalculating balances: {e}"
            )
    
    # --- New Menu Handlers ---
    
    def _on_new_investment(self):
        """Navigate to ROI Tracker to add new investment."""
        self._go_to_tab("roi_tracker")
        self.status_bar.showMessage("ROI Tracker - Add a new investment")
    
    def _on_delete_selected(self):
        """Delete selected item in current tab."""
        current_tab = self.tab_widget.currentWidget()
        
        # List of possible delete method names used across tabs
        delete_methods = [
            '_remove_selected',           # ROI Tracker, Budget Planner
            '_on_delete_transaction',     # Ledger
            '_on_delete_item',            # Inventory
            '_on_delete',                 # Generic
            'remove_selected',            # Generic
        ]
        
        # Try each method name
        for method_name in delete_methods:
            if hasattr(current_tab, method_name):
                method = getattr(current_tab, method_name)
                if callable(method):
                    method()
                    return
        
        # No delete method found
        self.status_bar.showMessage("No deletable selection in current tab")
    
    def _on_preferences(self):
        """Open Settings tab (preferences)."""
        self._go_to_tab("settings")
        self.status_bar.showMessage("Settings - Configure preferences")
    
    def _go_to_tab(self, tab_id: str):
        """Navigate to a specific tab by ID."""
        try:
            tab_ids = [tid for _, tid in TABS]
            if tab_id in tab_ids:
                index = tab_ids.index(tab_id)
                self.tab_widget.setCurrentIndex(index)
        except Exception as e:
            print(f"Error navigating to tab {tab_id}: {e}")
    
    def _on_refresh_dashboard(self):
        """Refresh the dashboard."""
        if hasattr(self, 'dashboard_tab'):
            self.dashboard_tab.refresh_dashboard()
            self.status_bar.showMessage("Dashboard refreshed")
    
    def _on_validate_data(self):
        """Validate all data for consistency."""
        from PyQt6.QtWidgets import QMessageBox
        
        issues = []
        
        # Check ledger balances
        try:
            if hasattr(self, 'ledger_tab'):
                balances = self.ledger_tab.get_current_balances()
                if balances.get("personal", 0) < 0:
                    issues.append("⚠️ Personal balance is negative")
                if balances.get("company", 0) < 0:
                    issues.append("⚠️ Company balance is negative")
        except:
            issues.append("❌ Could not validate Ledger data")
        
        # Check inventory
        try:
            if hasattr(self, 'inventory_tab'):
                inv = self.inventory_tab
                if inv.oil_lifetime_sold > inv.oil_cap_amount and inv.oil_cap_enabled:
                    issues.append("🚨 Oil sold exceeds lifetime cap!")
        except:
            issues.append("❌ Could not validate Inventory data")
        
        # Check ROI Tracker
        try:
            if hasattr(self, 'roi_tracker_tab'):
                roi = self.roi_tracker_tab
                for inv in roi.investments:
                    if inv.get("cost", 0) <= 0:
                        issues.append(f"⚠️ ROI item '{inv.get('name', 'Unknown')}' has zero cost")
        except:
            issues.append("❌ Could not validate ROI Tracker data")
        
        if issues:
            QMessageBox.warning(
                self,
                "Data Validation",
                "Issues found:\n\n" + "\n".join(issues)
            )
        else:
            QMessageBox.information(
                self,
                "Data Validation",
                "✅ All data validated successfully!\n\nNo issues found."
            )
        
        self.status_bar.showMessage(f"Validation complete: {len(issues)} issue(s) found")
    
    def _on_quick_start(self):
        """Show Quick Start Guide."""
        from PyQt6.QtWidgets import QMessageBox
        
        guide = """
<h2>🚀 Quick Start Guide</h2>

<h3>Getting Started</h3>
<p>1. <b>Dashboard</b> - Overview of your mining operations</p>
<p>2. <b>Ledger</b> - Track all income and expenses</p>
<p>3. <b>ROI Tracker</b> - Monitor investment returns</p>
<p>4. <b>Inventory</b> - Track ore and resources</p>
<p>5. <b>Budget Planner</b> - Plan equipment purchases</p>

<h3>Key Shortcuts</h3>
<p><b>Ctrl+N</b> - New Transaction</p>
<p><b>Ctrl+S</b> - Save Session</p>
<p><b>Ctrl+1-9</b> - Navigate to tabs</p>
<p><b>F5</b> - Refresh Dashboard</p>

<h3>Tips</h3>
<p>• Save your session regularly (Ctrl+S)</p>
<p>• Check the Dashboard for oil cap status</p>
<p>• Use the Budget Planner before big purchases</p>
"""
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Quick Start Guide")
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText(guide)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.exec()
    
    def _on_keyboard_shortcuts(self):
        """Show keyboard shortcuts dialog."""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QPushButton
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Keyboard Shortcuts")
        dialog.setMinimumWidth(450)
        dialog.setMinimumHeight(400)
        
        layout = QVBoxLayout(dialog)
        
        shortcuts = [
            ("Ctrl+Shift+N", "New Session"),
            ("Ctrl+S", "Save Session"),
            ("Ctrl+O", "Load Session"),
            ("Ctrl+N", "New Transaction"),
            ("Ctrl+I", "Import from Excel"),
            ("Ctrl+E", "Export to Excel"),
            ("Ctrl+Q", "Exit"),
            ("", ""),
            ("Ctrl+1", "Dashboard"),
            ("Ctrl+2", "Ledger"),
            ("Ctrl+3", "Reference Data"),
            ("Ctrl+4", "Auditor"),
            ("Ctrl+5", "ROI Tracker"),
            ("Ctrl+6", "Inventory"),
            ("Ctrl+7", "Material Movement"),
            ("Ctrl+8", "Budget Planner"),
            ("Ctrl+9", "Settings"),
            ("", ""),
            ("F5", "Refresh Dashboard"),
            ("F1", "Quick Start Guide"),
            ("Delete", "Delete Selected"),
        ]
        
        table = QTableWidget(len(shortcuts), 2)
        table.setHorizontalHeaderLabels(["Shortcut", "Action"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setVisible(False)
        
        for row, (shortcut, action) in enumerate(shortcuts):
            table.setItem(row, 0, QTableWidgetItem(shortcut))
            table.setItem(row, 1, QTableWidgetItem(action))
        
        layout.addWidget(table)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.exec()
    
    def _on_game_reference(self):
        """Show game reference information."""
        from PyQt6.QtWidgets import QMessageBox
        
        reference = """
<h2>🎮 Out of Ore - Game Reference</h2>

<h3>Hardcore Mode Starting Capital</h3>
<p>• Personal: $10,000 (10%)</p>
<p>• Company: $90,000 (90%)</p>
<p>• Total: $100,000</p>

<h3>Income Split (Ore/Oil Sales)</h3>
<p>• Company receives: 90%</p>
<p>• Personal receives: 10%</p>

<h3>Skill Discounts</h3>
<p>• Vendor Negotiation: 0.5% per level (max 7)</p>
<p>• Investment Forecasting: 0.5% per level (max 6)</p>

<h3>Bulk Pricing</h3>
<p>• 2+ units sold together = bulk rate applies</p>
<p>• Single units round up to nearest dollar</p>

<h3>Challenge Mode Oil Cap</h3>
<p>• Default lifetime cap: 10,000 units</p>
<p>• Configure in Settings tab</p>
"""
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Game Reference")
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText(reference)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.exec()
    
    def _on_check_updates(self):
        """Check for updates (placeholder)."""
        from PyQt6.QtWidgets import QMessageBox
        
        QMessageBox.information(
            self,
            "Check for Updates",
            f"You are running {APP_NAME} v{APP_VERSION}\n\n"
            "This is the latest version.\n\n"
            "Check GitHub for updates:\n"
            "https://github.com/your-repo/frontier-mining-tracker"
        )
