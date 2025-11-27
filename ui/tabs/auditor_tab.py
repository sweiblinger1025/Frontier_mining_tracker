"""
Auditor Tab - Save file verification and validation

Features:
- Load and parse Out of Ore save files (.sav)
- Load and parse Company XML files (.xml) for skills and company funds
- Compare save data against ledger records
- Identify discrepancies in money, transactions, and skill settings
- Future: Rule violation checking via Story Templates
"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QLabel,
    QPushButton,
    QFileDialog,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
    QTextEdit,
    QSplitter,
    QAbstractItemView,
    QFrame,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont

from pathlib import Path
from typing import Optional
import os
import xml.etree.ElementTree as ET

from core.database import Database, get_database
from auditor.save_parser import SaveFileParser, SaveFileData, parse_save_file


# Skill Row Mapping from XML
SKILL_ROWS = {
    26: "Skill Tree Unlock",
    8: "Vendor Negotiation (VN)",
    4: "Investment Forecasting (IF)",
    22: "Ore Sorting Technology",
    29: "Increase Run Speed",
    30: "Increase Jump Force",
    31: "More Rewards from Quests",
    33: "Better Credit Score",
}

# Key skill rows for discount calculations
VN_ROW = 8
IF_ROW = 4


class CompanyXMLData:
    """Parsed data from company XML file."""
    
    def __init__(self):
        self.company_name: str = ""
        self.company_money: int = 0
        self.company_debt: int = 0
        self.company_experience: float = 0.0
        self.skill_points: int = 0
        self.interest_rate: int = 0
        self.fuel_price: int = 0
        self.skills: dict = {}  # row_id -> level
        self.vn_level: int = 0
        self.if_level: int = 0
    
    @property
    def vn_discount(self) -> float:
        """Calculate VN discount percentage."""
        return self.vn_level * 0.5
    
    @property
    def if_discount(self) -> float:
        """Calculate IF discount percentage."""
        return self.if_level * 0.5
    
    @property
    def total_vehicle_discount(self) -> float:
        """Calculate total vehicle discount (VN + IF)."""
        return self.vn_discount + self.if_discount


def parse_company_xml(file_path: Path) -> CompanyXMLData:
    """Parse company XML file and extract data."""
    data = CompanyXMLData()
    
    # Read and fix unescaped ampersands
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix common XML issues (unescaped &)
    content = content.replace('&', '&amp;').replace('&amp;amp;', '&amp;')
    
    root = ET.fromstring(content)
    
    # Basic company info
    data.company_name = root.find('companyName').text or ""
    data.company_money = int(root.find('companyMoney').text or 0)
    data.company_debt = int(root.find('companyDebt').text or 0)
    data.company_experience = float(root.find('companyExperience').text or 0)
    data.skill_points = int(root.find('skillPoints').text or 0)
    data.interest_rate = int(root.find('interestRate').text or 0)
    data.fuel_price = int(root.find('fuelPrice').text or 0)
    
    # Parse unlocked skills
    unlocked_skills = root.find('unlockedSkills')
    if unlocked_skills is not None:
        for entry in unlocked_skills.findall('entry'):
            row = int(entry.get('rowName', 0))
            stage = int(entry.get('stage', 0))
            level = stage + 1  # Level = Stage + 1
            data.skills[row] = level
            
            # Extract VN and IF specifically
            if row == VN_ROW:
                data.vn_level = level
            elif row == IF_ROW:
                data.if_level = level
    
    return data


class AuditorTab(QWidget):
    """Auditor tab for save file verification."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = get_database()
        self.save_data: Optional[SaveFileData] = None
        self.xml_data: Optional[CompanyXMLData] = None
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the UI components."""
        layout = QVBoxLayout(self)
        
        # Top section: File selection
        layout.addWidget(self._create_file_section())
        
        # Main section: Splitter with save info and comparison
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left: Save file info
        splitter.addWidget(self._create_save_info_panel())
        
        # Right: Comparison results
        splitter.addWidget(self._create_comparison_panel())
        
        splitter.setSizes([400, 600])
        layout.addWidget(splitter)
        
        # Bottom: Audit log
        layout.addWidget(self._create_audit_log())
    
    def _create_file_section(self) -> QGroupBox:
        """Create the file selection section."""
        group = QGroupBox("📁 Game Files")
        layout = QVBoxLayout(group)
        
        # SAV file row
        sav_row = QHBoxLayout()
        sav_row.addWidget(QLabel("Save File (.sav):"))
        self.sav_path_label = QLabel("No save file loaded")
        self.sav_path_label.setStyleSheet("color: #666; font-style: italic;")
        sav_row.addWidget(self.sav_path_label, stretch=1)
        
        self.browse_sav_btn = QPushButton("📂 Browse...")
        self.browse_sav_btn.clicked.connect(self._on_browse_sav)
        sav_row.addWidget(self.browse_sav_btn)
        layout.addLayout(sav_row)
        
        # XML file row
        xml_row = QHBoxLayout()
        xml_row.addWidget(QLabel("Company XML (optional):"))
        self.xml_path_label = QLabel("No XML file loaded")
        self.xml_path_label.setStyleSheet("color: #666; font-style: italic;")
        xml_row.addWidget(self.xml_path_label, stretch=1)
        
        self.browse_xml_btn = QPushButton("📂 Browse...")
        self.browse_xml_btn.clicked.connect(self._on_browse_xml)
        xml_row.addWidget(self.browse_xml_btn)
        
        self.clear_xml_btn = QPushButton("✕ Clear")
        self.clear_xml_btn.clicked.connect(self._on_clear_xml)
        self.clear_xml_btn.setEnabled(False)
        self.clear_xml_btn.setFixedWidth(60)
        xml_row.addWidget(self.clear_xml_btn)
        layout.addLayout(xml_row)
        
        # Buttons row
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        
        self.default_path_btn = QPushButton("🎮 Game Saves Folder")
        self.default_path_btn.clicked.connect(self._on_open_game_folder)
        btn_row.addWidget(self.default_path_btn)
        
        self.reload_btn = QPushButton("🔄 Reload")
        self.reload_btn.clicked.connect(self._on_reload)
        self.reload_btn.setEnabled(False)
        btn_row.addWidget(self.reload_btn)
        
        layout.addLayout(btn_row)
        
        return group
    
    def _create_save_info_panel(self) -> QGroupBox:
        """Create the save file information panel."""
        group = QGroupBox("💾 Game Data")
        layout = QVBoxLayout(group)
        
        # SAV file info section
        layout.addWidget(QLabel("📄 Save File (.sav):"))
        
        self.sav_info_labels = {}
        sav_items = [
            ("file_name", "File Name:"),
            ("file_size", "File Size:"),
            ("map_name", "Map:"),
            ("current_money", "Personal Money:"),
            ("total_transactions", "Transactions:"),
            ("total_sales", "Total Sales:"),
            ("total_purchases", "Total Purchases:"),
        ]
        
        for key, label_text in sav_items:
            row = QHBoxLayout()
            label = QLabel(label_text)
            label.setFixedWidth(120)
            label.setStyleSheet("font-weight: bold;")
            row.addWidget(label)
            
            value_label = QLabel("-")
            value_label.setStyleSheet("color: #333;")
            self.sav_info_labels[key] = value_label
            row.addWidget(value_label, stretch=1)
            
            layout.addLayout(row)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)
        
        # XML file info section
        layout.addWidget(QLabel("📄 Company XML (optional):"))
        
        self.xml_info_labels = {}
        xml_items = [
            ("company_name", "Company:"),
            ("company_money", "Company Funds:"),
            ("vn_level", "VN Level:"),
            ("if_level", "IF Level:"),
            ("vn_discount", "VN Discount:"),
            ("if_discount", "IF Discount:"),
            ("total_vehicle_discount", "Vehicle Discount:"),
            ("skill_points", "Skill Points:"),
        ]
        
        for key, label_text in xml_items:
            row = QHBoxLayout()
            label = QLabel(label_text)
            label.setFixedWidth(120)
            label.setStyleSheet("font-weight: bold;")
            row.addWidget(label)
            
            value_label = QLabel("-")
            value_label.setStyleSheet("color: #333;")
            self.xml_info_labels[key] = value_label
            row.addWidget(value_label, stretch=1)
            
            layout.addLayout(row)
        
        layout.addStretch()
        
        # Transaction list from save
        layout.addWidget(QLabel("Save File Transactions:"))
        self.save_transactions_table = QTableWidget()
        self.save_transactions_table.setColumnCount(4)
        self.save_transactions_table.setHorizontalHeaderLabels(["Code", "Category", "Amount", "Type"])
        self.save_transactions_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.save_transactions_table.setMaximumHeight(150)
        layout.addWidget(self.save_transactions_table)
        
        return group
    
    def _create_comparison_panel(self) -> QGroupBox:
        """Create the comparison results panel."""
        group = QGroupBox("🔍 Verification Results")
        layout = QVBoxLayout(group)
        
        # Summary section
        summary_frame = QFrame()
        summary_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        summary_layout = QHBoxLayout(summary_frame)
        
        # Status indicator
        self.status_label = QLabel("⏳ No save file loaded")
        self.status_label.setStyleSheet("font-size: 14px; padding: 10px;")
        summary_layout.addWidget(self.status_label)
        
        summary_layout.addStretch()
        
        # Run comparison button
        self.compare_btn = QPushButton("▶️ Run Verification")
        self.compare_btn.clicked.connect(self._on_run_comparison)
        self.compare_btn.setEnabled(False)
        summary_layout.addWidget(self.compare_btn)
        
        layout.addWidget(summary_frame)
        
        # Discrepancies table
        layout.addWidget(QLabel("Discrepancies Found:"))
        self.discrepancies_table = QTableWidget()
        self.discrepancies_table.setColumnCount(4)
        self.discrepancies_table.setHorizontalHeaderLabels(["Field", "Ledger Value", "Save Value", "Difference"])
        self.discrepancies_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.discrepancies_table.setAlternatingRowColors(True)
        layout.addWidget(self.discrepancies_table)
        
        return group
    
    def _create_audit_log(self) -> QGroupBox:
        """Create the audit log section."""
        group = QGroupBox("📋 Audit Log")
        layout = QVBoxLayout(group)
        
        self.audit_log = QTextEdit()
        self.audit_log.setReadOnly(True)
        self.audit_log.setMaximumHeight(150)
        self.audit_log.setStyleSheet("font-family: monospace; font-size: 11px;")
        layout.addWidget(self.audit_log)
        
        # Clear button
        clear_btn = QPushButton("Clear Log")
        clear_btn.clicked.connect(lambda: self.audit_log.clear())
        layout.addWidget(clear_btn, alignment=Qt.AlignmentFlag.AlignRight)
        
        return group
    
    def _log(self, message: str, level: str = "INFO"):
        """Add a message to the audit log."""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        color = {
            "INFO": "#333",
            "SUCCESS": "#2e7d32",
            "WARNING": "#f57c00",
            "ERROR": "#c62828",
        }.get(level, "#333")
        
        self.audit_log.append(f'<span style="color: #999;">[{timestamp}]</span> '
                             f'<span style="color: {color};">{message}</span>')
    
    def _on_browse_sav(self):
        """Browse for a save file."""
        default_path = self._get_game_saves_folder()
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Save File",
            str(default_path),
            "Save Files (*.sav);;All Files (*)"
        )
        
        if file_path:
            self._load_save_file(Path(file_path))
    
    def _on_browse_xml(self):
        """Browse for a company XML file."""
        # Default to AppData folder where XML is stored
        default_path = self._get_appdata_folder()
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Company XML File",
            str(default_path),
            "XML Files (*.xml);;All Files (*)"
        )
        
        if file_path:
            self._load_xml_file(Path(file_path))
    
    def _on_clear_xml(self):
        """Clear the loaded XML file."""
        self.xml_data = None
        self.xml_path_label.setText("No XML file loaded")
        self.xml_path_label.setStyleSheet("color: #666; font-style: italic;")
        self.clear_xml_btn.setEnabled(False)
        self._clear_xml_info()
        self._log("XML file cleared", "INFO")
    
    def _on_open_game_folder(self):
        """Open the game saves folder."""
        folder = self._get_game_saves_folder()
        
        if folder.exists():
            import subprocess
            import sys
            
            if sys.platform == 'win32':
                subprocess.run(['explorer', str(folder)])
            elif sys.platform == 'darwin':
                subprocess.run(['open', str(folder)])
            else:
                subprocess.run(['xdg-open', str(folder)])
            
            self._log(f"Opened folder: {folder}")
        else:
            QMessageBox.warning(
                self, 
                "Folder Not Found",
                f"Game saves folder not found at:\n{folder}\n\n"
                "Please browse manually for your save file."
            )
    
    def _get_game_saves_folder(self) -> Path:
        """Get the default game saves folder path."""
        local_appdata = os.environ.get('LOCALAPPDATA', '')
        if local_appdata:
            return Path(local_appdata) / "OutOfOre" / "Saved" / "SaveGames"
        return Path.home()
    
    def _get_appdata_folder(self) -> Path:
        """Get the AppData folder where company XML is stored."""
        appdata = os.environ.get('APPDATA', '')
        if appdata:
            return Path(appdata)
        return Path.home()
    
    def _on_reload(self):
        """Reload the current files."""
        if self.save_data and self.save_data.file_path.exists():
            self._load_save_file(self.save_data.file_path)
        if self.xml_data:
            # Try to reload XML if we have a path stored
            pass
    
    def _load_save_file(self, file_path: Path):
        """Load and parse a save file."""
        self._log(f"Loading save file: {file_path.name}")
        
        try:
            self.save_data = parse_save_file(file_path)
            self._update_sav_info()
            self._populate_save_transactions()
            
            self.sav_path_label.setText(str(file_path))
            self.sav_path_label.setStyleSheet("color: #333;")
            self.reload_btn.setEnabled(True)
            self.compare_btn.setEnabled(True)
            
            self.status_label.setText("✅ Save file loaded - Ready for verification")
            self.status_label.setStyleSheet("font-size: 14px; padding: 10px; color: #2e7d32;")
            
            self._log(f"Successfully loaded save file", "SUCCESS")
            self._log(f"  Personal Money: ${self.save_data.current_money:,.0f}")
            self._log(f"  Transactions: {len(self.save_data.transactions)}")
            
        except Exception as e:
            self._log(f"Error loading save file: {e}", "ERROR")
            QMessageBox.critical(self, "Error", f"Failed to load save file:\n{e}")
    
    def _load_xml_file(self, file_path: Path):
        """Load and parse a company XML file."""
        self._log(f"Loading XML file: {file_path.name}")
        
        try:
            self.xml_data = parse_company_xml(file_path)
            self._update_xml_info()
            
            self.xml_path_label.setText(str(file_path))
            self.xml_path_label.setStyleSheet("color: #333;")
            self.clear_xml_btn.setEnabled(True)
            
            self._log(f"Successfully loaded XML file", "SUCCESS")
            self._log(f"  Company: {self.xml_data.company_name}")
            self._log(f"  Company Funds: ${self.xml_data.company_money:,}")
            self._log(f"  VN Level: {self.xml_data.vn_level} ({self.xml_data.vn_discount}%)")
            self._log(f"  IF Level: {self.xml_data.if_level} ({self.xml_data.if_discount}%)")
            
        except Exception as e:
            self._log(f"Error loading XML file: {e}", "ERROR")
            QMessageBox.critical(self, "Error", f"Failed to load XML file:\n{e}")
    
    def _update_sav_info(self):
        """Update the save file info labels."""
        if not self.save_data:
            return
        
        self.sav_info_labels["file_name"].setText(self.save_data.file_path.name)
        self.sav_info_labels["file_size"].setText(f"{self.save_data.file_size:,} bytes")
        self.sav_info_labels["map_name"].setText(self.save_data.map_name or "Unknown")
        self.sav_info_labels["current_money"].setText(f"${self.save_data.current_money:,.0f}")
        self.sav_info_labels["total_transactions"].setText(str(len(self.save_data.transactions)))
        self.sav_info_labels["total_sales"].setText(f"${self.save_data.total_sales:,.0f}")
        self.sav_info_labels["total_purchases"].setText(f"${abs(self.save_data.total_purchases):,.0f}")
    
    def _update_xml_info(self):
        """Update the XML file info labels."""
        if not self.xml_data:
            return
        
        self.xml_info_labels["company_name"].setText(self.xml_data.company_name or "Unknown")
        self.xml_info_labels["company_money"].setText(f"${self.xml_data.company_money:,}")
        self.xml_info_labels["vn_level"].setText(f"{self.xml_data.vn_level} / 7")
        self.xml_info_labels["if_level"].setText(f"{self.xml_data.if_level} / 6")
        self.xml_info_labels["vn_discount"].setText(f"{self.xml_data.vn_discount:.1f}%")
        self.xml_info_labels["if_discount"].setText(f"{self.xml_data.if_discount:.1f}%")
        self.xml_info_labels["total_vehicle_discount"].setText(f"{self.xml_data.total_vehicle_discount:.1f}%")
        self.xml_info_labels["skill_points"].setText(f"{self.xml_data.skill_points:,}")
    
    def _clear_xml_info(self):
        """Clear the XML info labels."""
        for label in self.xml_info_labels.values():
            label.setText("-")
    
    def _populate_save_transactions(self):
        """Populate the save transactions table."""
        if not self.save_data:
            return
        
        transactions = self.save_data.transactions
        self.save_transactions_table.setRowCount(len(transactions))
        
        for row, txn in enumerate(transactions):
            # Code
            code_item = QTableWidgetItem(txn.item_code)
            self.save_transactions_table.setItem(row, 0, code_item)
            
            # Category
            cat_item = QTableWidgetItem(txn.category)
            self.save_transactions_table.setItem(row, 1, cat_item)
            
            # Amount
            amount_item = QTableWidgetItem(f"${txn.amount:,.0f}")
            amount_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            if txn.amount < 0:
                amount_item.setForeground(QColor("#c62828"))
            else:
                amount_item.setForeground(QColor("#2e7d32"))
            self.save_transactions_table.setItem(row, 2, amount_item)
            
            # Type
            type_item = QTableWidgetItem("Purchase" if txn.is_purchase else "Sale")
            self.save_transactions_table.setItem(row, 3, type_item)
    
    def _on_run_comparison(self):
        """Run comparison between save file and ledger."""
        if not self.save_data:
            return
        
        self._log("Starting verification...", "INFO")
        self.discrepancies_table.setRowCount(0)
        
        discrepancies = []
        
        # Get ledger data
        ledger_data = self._get_ledger_summary()
        
        # Compare current money (Personal balance)
        save_money = self.save_data.current_money
        ledger_money = ledger_data.get('current_personal_balance', 0)
        
        if abs(save_money - ledger_money) > 1:  # Allow $1 rounding tolerance
            discrepancies.append({
                'field': 'Personal Money',
                'ledger': f"${ledger_money:,.0f}",
                'save': f"${save_money:,.0f}",
                'diff': f"${save_money - ledger_money:+,.0f}"
            })
        
        # Compare transaction counts
        save_txn_count = len(self.save_data.transactions)
        ledger_txn_count = ledger_data.get('transaction_count', 0)
        
        if save_txn_count != ledger_txn_count:
            discrepancies.append({
                'field': 'Transaction Count',
                'ledger': str(ledger_txn_count),
                'save': str(save_txn_count),
                'diff': f"{save_txn_count - ledger_txn_count:+d}"
            })
        
        # Compare totals
        save_total_sales = self.save_data.total_sales
        ledger_total_sales = ledger_data.get('total_sales', 0)
        
        if abs(save_total_sales - ledger_total_sales) > 1:
            discrepancies.append({
                'field': 'Total Sales',
                'ledger': f"${ledger_total_sales:,.0f}",
                'save': f"${save_total_sales:,.0f}",
                'diff': f"${save_total_sales - ledger_total_sales:+,.0f}"
            })
        
        save_total_purchases = abs(self.save_data.total_purchases)
        ledger_total_purchases = ledger_data.get('total_purchases', 0)
        
        if abs(save_total_purchases - ledger_total_purchases) > 1:
            discrepancies.append({
                'field': 'Total Purchases',
                'ledger': f"${ledger_total_purchases:,.0f}",
                'save': f"${save_total_purchases:,.0f}",
                'diff': f"${save_total_purchases - ledger_total_purchases:+,.0f}"
            })
        
        # If XML is loaded, compare company funds and skill settings
        if self.xml_data:
            # Compare Company Funds
            xml_company_money = self.xml_data.company_money
            ledger_company_balance = ledger_data.get('current_company_balance', 0)
            
            if abs(xml_company_money - ledger_company_balance) > 1:
                discrepancies.append({
                    'field': 'Company Funds',
                    'ledger': f"${ledger_company_balance:,.0f}",
                    'save': f"${xml_company_money:,}",
                    'diff': f"${xml_company_money - ledger_company_balance:+,.0f}"
                })
            
            # Compare VN Level with app settings
            app_vn_level = self._get_app_vn_level()
            if app_vn_level is not None and app_vn_level != self.xml_data.vn_level:
                discrepancies.append({
                    'field': 'VN Level',
                    'ledger': f"Level {app_vn_level}",
                    'save': f"Level {self.xml_data.vn_level}",
                    'diff': f"{self.xml_data.vn_level - app_vn_level:+d}"
                })
            
            # Compare IF Level with app settings
            app_if_level = self._get_app_if_level()
            if app_if_level is not None and app_if_level != self.xml_data.if_level:
                discrepancies.append({
                    'field': 'IF Level',
                    'ledger': f"Level {app_if_level}",
                    'save': f"Level {self.xml_data.if_level}",
                    'diff': f"{self.xml_data.if_level - app_if_level:+d}"
                })
        
        # Populate discrepancies table
        self.discrepancies_table.setRowCount(len(discrepancies))
        
        for row, disc in enumerate(discrepancies):
            self.discrepancies_table.setItem(row, 0, QTableWidgetItem(disc['field']))
            self.discrepancies_table.setItem(row, 1, QTableWidgetItem(disc['ledger']))
            self.discrepancies_table.setItem(row, 2, QTableWidgetItem(disc['save']))
            
            diff_item = QTableWidgetItem(disc['diff'])
            diff_item.setForeground(QColor("#c62828"))  # Red for discrepancy
            self.discrepancies_table.setItem(row, 3, diff_item)
        
        # Update status
        if discrepancies:
            self.status_label.setText(f"⚠️ Found {len(discrepancies)} discrepancies")
            self.status_label.setStyleSheet("font-size: 14px; padding: 10px; color: #f57c00;")
            self._log(f"Verification complete: {len(discrepancies)} discrepancies found", "WARNING")
        else:
            self.status_label.setText("✅ Verification passed - No discrepancies found")
            self.status_label.setStyleSheet("font-size: 14px; padding: 10px; color: #2e7d32;")
            self._log("Verification complete: All values match!", "SUCCESS")
    
    def _get_app_vn_level(self) -> Optional[int]:
        """Get the VN level configured in the app (from game_info table)."""
        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT value FROM game_info WHERE key = 'vn_level'")
                row = cursor.fetchone()
                if row:
                    return int(row[0])
        except Exception:
            pass
        return None
    
    def _get_app_if_level(self) -> Optional[int]:
        """Get the IF level configured in the app (from game_info table)."""
        try:
            with self.db._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT value FROM game_info WHERE key = 'if_level'")
                row = cursor.fetchone()
                if row:
                    return int(row[0])
        except Exception:
            pass
        return None
    
    def _get_ledger_summary(self) -> dict:
        """Get summary data from the ledger."""
        summary = {
            'current_personal_balance': 0,
            'current_company_balance': 0,
            'transaction_count': 0,
            'total_sales': 0,
            'total_purchases': 0,
        }
        
        with self.db._get_connection() as conn:
            cursor = conn.cursor()
            
            # Get the most recent balance
            cursor.execute("""
                SELECT personal_balance, company_balance 
                FROM transactions 
                WHERE type != 'Opening'
                ORDER BY id DESC 
                LIMIT 1
            """)
            row = cursor.fetchone()
            if row:
                summary['current_personal_balance'] = row['personal_balance'] or 0
                summary['current_company_balance'] = row['company_balance'] or 0
            
            # Get transaction count (excluding Opening)
            cursor.execute("SELECT COUNT(*) FROM transactions WHERE type != 'Opening'")
            summary['transaction_count'] = cursor.fetchone()[0]
            
            # Get total sales
            cursor.execute("""
                SELECT COALESCE(SUM(total), 0) 
                FROM transactions 
                WHERE type = 'Sale'
            """)
            summary['total_sales'] = cursor.fetchone()[0]
            
            # Get total purchases
            cursor.execute("""
                SELECT COALESCE(SUM(total), 0) 
                FROM transactions 
                WHERE type = 'Purchase'
            """)
            summary['total_purchases'] = cursor.fetchone()[0]
        
        return summary
