"""
Session Manager - Handle saving and loading of application sessions.

Saves all user data across tabs to JSON files for persistence.
"""
import json
import os
from datetime import datetime, date
from pathlib import Path
from typing import Dict, Any, Optional

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QMessageBox, QFileDialog,
    QLineEdit, QFormLayout, QGroupBox, QDialogButtonBox
)
from PyQt6.QtCore import Qt


class SessionManager:
    """Manages saving and loading of session data."""
    
    # Default sessions directory
    SESSIONS_DIR = "sessions"
    
    def __init__(self, main_window):
        self.main_window = main_window
        self._ensure_sessions_dir()
    
    def _ensure_sessions_dir(self):
        """Ensure the sessions directory exists."""
        sessions_path = Path(self.SESSIONS_DIR)
        if not sessions_path.exists():
            sessions_path.mkdir(parents=True)
    
    def _serialize_date(self, obj):
        """Convert date objects to strings for JSON serialization."""
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
    
    def _deserialize_dates(self, data: Dict) -> Dict:
        """Convert date strings back to date objects where appropriate."""
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, str):
                    # Try to parse as date
                    try:
                        if 'T' in value:
                            data[key] = datetime.fromisoformat(value)
                        elif '-' in value and len(value) == 10:
                            data[key] = datetime.strptime(value, "%Y-%m-%d").date()
                    except (ValueError, TypeError):
                        pass
                elif isinstance(value, dict):
                    data[key] = self._deserialize_dates(value)
                elif isinstance(value, list):
                    data[key] = [self._deserialize_dates(item) if isinstance(item, dict) else item for item in value]
        return data
    
    def collect_session_data(self) -> Dict[str, Any]:
        """Collect all session data from tabs."""
        data = {
            "version": "1.0",
            "saved_at": datetime.now().isoformat(),
            "ledger": self._collect_ledger_data(),
            "inventory": self._collect_inventory_data(),
            "roi_tracker": self._collect_roi_data(),
            "budget_planner": self._collect_budget_data(),
            "material_movement": self._collect_material_movement_data(),
            "settings": self._collect_settings_data(),
        }
        return data
    
    def _collect_ledger_data(self) -> Dict:
        """Collect data from Ledger tab."""
        try:
            ledger = self.main_window.ledger_tab
            transactions = []
            
            for row in range(ledger.table.rowCount()):
                transaction = {}
                # Get all columns
                for col in range(ledger.table.columnCount()):
                    item = ledger.table.item(row, col)
                    header = ledger.table.horizontalHeaderItem(col)
                    if item and header:
                        transaction[header.text()] = item.text()
                transactions.append(transaction)
            
            return {
                "transactions": transactions,
                "starting_personal": getattr(ledger, 'starting_personal', 10000),
                "starting_company": getattr(ledger, 'starting_company', 90000),
            }
        except Exception as e:
            print(f"Error collecting ledger data: {e}")
            return {"transactions": []}
    
    def _collect_inventory_data(self) -> Dict:
        """Collect data from Inventory tab."""
        try:
            inv = self.main_window.inventory_tab
            return {
                "inventory_items": inv.inventory_items,
                "oil_cap_enabled": inv.oil_cap_enabled,
                "oil_cap_amount": inv.oil_cap_amount,
                "oil_lifetime_sold": inv.oil_lifetime_sold,
            }
        except Exception as e:
            print(f"Error collecting inventory data: {e}")
            return {}
    
    def _collect_roi_data(self) -> Dict:
        """Collect data from ROI Tracker tab."""
        try:
            roi = self.main_window.roi_tracker_tab
            # Deep copy investments with serializable dates
            investments = []
            for inv in roi.investments:
                inv_copy = dict(inv)
                # Convert date to string
                if "purchase_date" in inv_copy and isinstance(inv_copy["purchase_date"], (date, datetime)):
                    inv_copy["purchase_date"] = inv_copy["purchase_date"].isoformat()
                # Convert revenue dates
                if "revenues" in inv_copy:
                    revenues = []
                    for rev in inv_copy["revenues"]:
                        rev_copy = dict(rev)
                        if "date" in rev_copy and isinstance(rev_copy["date"], (date, datetime)):
                            rev_copy["date"] = rev_copy["date"].isoformat()
                        revenues.append(rev_copy)
                    inv_copy["revenues"] = revenues
                investments.append(inv_copy)
            
            return {"investments": investments}
        except Exception as e:
            print(f"Error collecting ROI data: {e}")
            return {"investments": []}
    
    def _collect_budget_data(self) -> Dict:
        """Collect data from Budget Planner tab."""
        try:
            bp = self.main_window.budget_planner_tab
            return {
                "equipment_items": bp.equipment_items,
                "power_setups": bp.power_setups,
            }
        except Exception as e:
            print(f"Error collecting budget data: {e}")
            return {}
    
    def _collect_material_movement_data(self) -> Dict:
        """Collect data from Material Movement tab."""
        try:
            mm = self.main_window.material_movement_tab
            return {
                "hauling_sessions": mm.hauling_sessions,
                "processing_sessions": mm.processing_sessions,
            }
        except Exception as e:
            print(f"Error collecting material movement data: {e}")
            return {}
    
    def _collect_settings_data(self) -> Dict:
        """Collect data from Settings tab."""
        try:
            settings = self.main_window.settings_tab
            return settings.get_settings()
        except Exception as e:
            print(f"Error collecting settings data: {e}")
            return {}
    
    def save_session(self, filepath: str) -> bool:
        """Save session to a file."""
        try:
            data = self.collect_session_data()
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2, default=self._serialize_date)
            return True
        except Exception as e:
            print(f"Error saving session: {e}")
            return False
    
    def load_session(self, filepath: str) -> bool:
        """Load session from a file."""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Restore each tab's data
            self._restore_ledger_data(data.get("ledger", {}))
            self._restore_inventory_data(data.get("inventory", {}))
            self._restore_roi_data(data.get("roi_tracker", {}))
            self._restore_budget_data(data.get("budget_planner", {}))
            self._restore_material_movement_data(data.get("material_movement", {}))
            self._restore_settings_data(data.get("settings", {}))
            
            # Refresh dashboard
            if hasattr(self.main_window, 'dashboard_tab'):
                self.main_window.dashboard_tab.refresh_dashboard()
            
            return True
        except Exception as e:
            print(f"Error loading session: {e}")
            return False
    
    def _restore_ledger_data(self, data: Dict):
        """Restore Ledger tab data."""
        try:
            ledger = self.main_window.ledger_tab
            
            # Clear existing
            ledger.table.setRowCount(0)
            
            transactions = data.get("transactions", [])
            for trans in transactions:
                row = ledger.table.rowCount()
                ledger.table.insertRow(row)
                
                # Map column names to indices
                headers = []
                for col in range(ledger.table.columnCount()):
                    header = ledger.table.horizontalHeaderItem(col)
                    headers.append(header.text() if header else "")
                
                for col, header_text in enumerate(headers):
                    if header_text in trans:
                        item = QListWidgetItem(str(trans[header_text]))
                        ledger.table.setItem(row, col, QTableWidgetItem(str(trans[header_text])))
            
            # Restore starting balances
            if hasattr(ledger, 'starting_personal'):
                ledger.starting_personal = data.get("starting_personal", 10000)
            if hasattr(ledger, 'starting_company'):
                ledger.starting_company = data.get("starting_company", 90000)
                
        except Exception as e:
            print(f"Error restoring ledger data: {e}")
    
    def _restore_inventory_data(self, data: Dict):
        """Restore Inventory tab data."""
        try:
            inv = self.main_window.inventory_tab
            
            inv.inventory_items = data.get("inventory_items", [])
            inv.oil_cap_enabled = data.get("oil_cap_enabled", True)
            inv.oil_cap_amount = data.get("oil_cap_amount", 10000)
            inv.oil_lifetime_sold = data.get("oil_lifetime_sold", 0)
            
            # Refresh display
            if hasattr(inv, '_refresh_table'):
                inv._refresh_table()
            if hasattr(inv, '_update_oil_tracker'):
                inv._update_oil_tracker()
                
        except Exception as e:
            print(f"Error restoring inventory data: {e}")
    
    def _restore_roi_data(self, data: Dict):
        """Restore ROI Tracker tab data."""
        try:
            roi = self.main_window.roi_tracker_tab
            
            investments = data.get("investments", [])
            # Convert date strings back to date objects
            for inv in investments:
                if "purchase_date" in inv and isinstance(inv["purchase_date"], str):
                    try:
                        inv["purchase_date"] = datetime.fromisoformat(inv["purchase_date"]).date()
                    except ValueError:
                        inv["purchase_date"] = datetime.strptime(inv["purchase_date"], "%Y-%m-%d").date()
                
                if "revenues" in inv:
                    for rev in inv["revenues"]:
                        if "date" in rev and isinstance(rev["date"], str):
                            try:
                                rev["date"] = datetime.fromisoformat(rev["date"]).date()
                            except ValueError:
                                rev["date"] = datetime.strptime(rev["date"], "%Y-%m-%d").date()
            
            roi.investments = investments
            roi._refresh_table()
            roi._update_summary()
            
        except Exception as e:
            print(f"Error restoring ROI data: {e}")
    
    def _restore_budget_data(self, data: Dict):
        """Restore Budget Planner tab data."""
        try:
            bp = self.main_window.budget_planner_tab
            
            bp.equipment_items = data.get("equipment_items", [])
            bp.power_setups = data.get("power_setups", [])
            
            # Refresh displays
            if hasattr(bp, '_refresh_equipment_table'):
                bp._refresh_equipment_table()
            if hasattr(bp, '_refresh_facility_display'):
                bp._refresh_facility_display()
            if hasattr(bp, '_update_summary'):
                bp._update_summary()
                
        except Exception as e:
            print(f"Error restoring budget data: {e}")
    
    def _restore_material_movement_data(self, data: Dict):
        """Restore Material Movement tab data."""
        try:
            mm = self.main_window.material_movement_tab
            
            mm.hauling_sessions = data.get("hauling_sessions", [])
            mm.processing_sessions = data.get("processing_sessions", [])
            
            # Refresh displays
            if hasattr(mm, '_refresh_hauling_table'):
                mm._refresh_hauling_table()
            if hasattr(mm, '_refresh_processing_table'):
                mm._refresh_processing_table()
                
        except Exception as e:
            print(f"Error restoring material movement data: {e}")
    
    def _restore_settings_data(self, data: Dict):
        """Restore Settings tab data."""
        try:
            settings = self.main_window.settings_tab
            if hasattr(settings, 'load_settings'):
                settings.load_settings(data)
        except Exception as e:
            print(f"Error restoring settings data: {e}")
    
    def new_session(self) -> bool:
        """Clear all data for a new session."""
        try:
            # Clear Ledger
            ledger = self.main_window.ledger_tab
            ledger.table.setRowCount(0)
            
            # Clear Inventory
            inv = self.main_window.inventory_tab
            inv.inventory_items = []
            inv.oil_lifetime_sold = 0
            if hasattr(inv, '_refresh_table'):
                inv._refresh_table()
            if hasattr(inv, '_update_oil_tracker'):
                inv._update_oil_tracker()
            
            # Clear ROI Tracker
            roi = self.main_window.roi_tracker_tab
            roi.investments = []
            roi._refresh_table()
            roi._update_summary()
            
            # Clear Budget Planner
            bp = self.main_window.budget_planner_tab
            bp.equipment_items = []
            bp.power_setups = []
            if hasattr(bp, '_refresh_equipment_table'):
                bp._refresh_equipment_table()
            if hasattr(bp, '_update_summary'):
                bp._update_summary()
            
            # Clear Material Movement
            mm = self.main_window.material_movement_tab
            mm.hauling_sessions = []
            mm.processing_sessions = []
            if hasattr(mm, '_refresh_hauling_table'):
                mm._refresh_hauling_table()
            if hasattr(mm, '_refresh_processing_table'):
                mm._refresh_processing_table()
            
            # Refresh Dashboard
            if hasattr(self.main_window, 'dashboard_tab'):
                self.main_window.dashboard_tab.refresh_dashboard()
            
            return True
        except Exception as e:
            print(f"Error creating new session: {e}")
            return False
    
    def get_saved_sessions(self) -> list:
        """Get list of saved session files."""
        sessions = []
        sessions_path = Path(self.SESSIONS_DIR)
        
        if sessions_path.exists():
            for file in sessions_path.glob("*.json"):
                try:
                    with open(file, 'r') as f:
                        data = json.load(f)
                    sessions.append({
                        "filename": file.name,
                        "filepath": str(file),
                        "saved_at": data.get("saved_at", "Unknown"),
                        "version": data.get("version", "1.0"),
                    })
                except Exception:
                    sessions.append({
                        "filename": file.name,
                        "filepath": str(file),
                        "saved_at": "Error reading file",
                    })
        
        # Sort by saved_at descending
        sessions.sort(key=lambda x: x.get("saved_at", ""), reverse=True)
        return sessions


# Need to import QTableWidgetItem for restore
from PyQt6.QtWidgets import QTableWidgetItem


class SessionDialog(QDialog):
    """Dialog for managing sessions (save/load/new)."""
    
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.session_manager = SessionManager(main_window)
        self.selected_action = None
        self.selected_filepath = None
        
        self.setWindowTitle("Session Manager")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # New Session section
        new_group = QGroupBox("📄 New Session")
        new_layout = QHBoxLayout(new_group)
        
        new_label = QLabel("Start fresh with empty data")
        new_layout.addWidget(new_label)
        new_layout.addStretch()
        
        self.new_btn = QPushButton("New Session")
        self.new_btn.clicked.connect(self._on_new_session)
        new_layout.addWidget(self.new_btn)
        
        layout.addWidget(new_group)
        
        # Save Session section
        save_group = QGroupBox("💾 Save Current Session")
        save_layout = QVBoxLayout(save_group)
        
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Session Name:"))
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter a name for this session...")
        self.name_edit.setText(f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        name_layout.addWidget(self.name_edit)
        
        self.save_btn = QPushButton("Save Session")
        self.save_btn.clicked.connect(self._on_save_session)
        name_layout.addWidget(self.save_btn)
        
        save_layout.addLayout(name_layout)
        layout.addWidget(save_group)
        
        # Load Session section
        load_group = QGroupBox("📂 Load Saved Session")
        load_layout = QVBoxLayout(load_group)
        
        self.sessions_list = QListWidget()
        self.sessions_list.itemDoubleClicked.connect(self._on_load_session)
        self._refresh_sessions_list()
        load_layout.addWidget(self.sessions_list)
        
        load_buttons = QHBoxLayout()
        
        self.load_btn = QPushButton("Load Selected")
        self.load_btn.clicked.connect(self._on_load_session)
        load_buttons.addWidget(self.load_btn)
        
        self.delete_btn = QPushButton("Delete Selected")
        self.delete_btn.clicked.connect(self._on_delete_session)
        load_buttons.addWidget(self.delete_btn)
        
        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.clicked.connect(self._on_browse_session)
        load_buttons.addWidget(self.browse_btn)
        
        load_buttons.addStretch()
        load_layout.addLayout(load_buttons)
        
        layout.addWidget(load_group)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.reject)
        layout.addWidget(close_btn)
    
    def _refresh_sessions_list(self):
        """Refresh the list of saved sessions."""
        self.sessions_list.clear()
        
        sessions = self.session_manager.get_saved_sessions()
        
        if not sessions:
            item = QListWidgetItem("No saved sessions found")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
            self.sessions_list.addItem(item)
        else:
            for session in sessions:
                saved_at = session.get("saved_at", "Unknown")
                if saved_at != "Unknown" and saved_at != "Error reading file":
                    try:
                        dt = datetime.fromisoformat(saved_at)
                        saved_at = dt.strftime("%Y-%m-%d %H:%M:%S")
                    except:
                        pass
                
                item = QListWidgetItem(f"{session['filename']} - {saved_at}")
                item.setData(Qt.ItemDataRole.UserRole, session['filepath'])
                self.sessions_list.addItem(item)
    
    def _on_new_session(self):
        """Handle new session button."""
        reply = QMessageBox.question(
            self, "New Session",
            "This will clear all current data.\n\nDo you want to save the current session first?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
        )
        
        if reply == QMessageBox.StandardButton.Cancel:
            return
        
        if reply == QMessageBox.StandardButton.Yes:
            # Save first
            name = f"autosave_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            filepath = os.path.join(self.session_manager.SESSIONS_DIR, f"{name}.json")
            if not self.session_manager.save_session(filepath):
                QMessageBox.warning(self, "Error", "Failed to save current session.")
                return
        
        # Create new session
        if self.session_manager.new_session():
            QMessageBox.information(self, "Success", "New session started.")
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Failed to create new session.")
    
    def _on_save_session(self):
        """Handle save session button."""
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Please enter a session name.")
            return
        
        # Sanitize filename
        safe_name = "".join(c for c in name if c.isalnum() or c in "._- ")
        if not safe_name:
            safe_name = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        filepath = os.path.join(self.session_manager.SESSIONS_DIR, f"{safe_name}.json")
        
        # Check if exists
        if os.path.exists(filepath):
            reply = QMessageBox.question(
                self, "Overwrite?",
                f"Session '{safe_name}' already exists. Overwrite?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        
        if self.session_manager.save_session(filepath):
            QMessageBox.information(self, "Success", f"Session saved as '{safe_name}'")
            self._refresh_sessions_list()
        else:
            QMessageBox.warning(self, "Error", "Failed to save session.")
    
    def _on_load_session(self):
        """Handle load session button."""
        item = self.sessions_list.currentItem()
        if not item:
            QMessageBox.warning(self, "Error", "Please select a session to load.")
            return
        
        filepath = item.data(Qt.ItemDataRole.UserRole)
        if not filepath:
            return
        
        reply = QMessageBox.question(
            self, "Load Session",
            "This will replace all current data with the saved session.\n\nContinue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        if self.session_manager.load_session(filepath):
            QMessageBox.information(self, "Success", "Session loaded successfully.")
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Failed to load session.")
    
    def _on_delete_session(self):
        """Handle delete session button."""
        item = self.sessions_list.currentItem()
        if not item:
            QMessageBox.warning(self, "Error", "Please select a session to delete.")
            return
        
        filepath = item.data(Qt.ItemDataRole.UserRole)
        if not filepath:
            return
        
        reply = QMessageBox.question(
            self, "Delete Session",
            f"Are you sure you want to delete this session?\n\n{item.text()}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                os.remove(filepath)
                self._refresh_sessions_list()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to delete session: {e}")
    
    def _on_browse_session(self):
        """Handle browse for session file."""
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Open Session File",
            self.session_manager.SESSIONS_DIR,
            "JSON Files (*.json);;All Files (*)"
        )
        
        if filepath:
            reply = QMessageBox.question(
                self, "Load Session",
                "This will replace all current data with the saved session.\n\nContinue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                if self.session_manager.load_session(filepath):
                    QMessageBox.information(self, "Success", "Session loaded successfully.")
                    self.accept()
                else:
                    QMessageBox.warning(self, "Error", "Failed to load session.")
