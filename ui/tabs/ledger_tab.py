"""
Ledger Tab - Transaction tracking with Opening Balance and auto-calculations

Features:
- Row 1: Opening Balance (editable Personal/Company balances)
- Rows 2+: Transactions (Purchase/Sale/Transfer)
- Auto-calculation of income/expense based on Account + Category
- 10%/90% split for Personal account selling Resources (Ore/Fluids)
- Running balance calculations
- Import/Export CSV/Excel
"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QLineEdit,
    QComboBox,
    QLabel,
    QPushButton,
    QSpinBox,
    QDoubleSpinBox,
    QDateEdit,
    QGroupBox,
    QFileDialog,
    QMessageBox,
    QAbstractItemView,
    QApplication,
    QCompleter,
    QDialog,
    QFormLayout,
    QDialogButtonBox,
)
from PyQt6.QtCore import Qt, pyqtSignal, QDate
from PyQt6.QtGui import QColor

from pathlib import Path
from datetime import date, datetime
from typing import Optional

from core.database import Database, get_database
from core.models import Transaction, TransactionType, AccountType, Item
from importers.excel_importer import ExcelImporter


class LedgerTab(QWidget):
    """Ledger tab for tracking all transactions."""
    
    # Signal emitted when data changes (for other tabs to update)
    data_changed = pyqtSignal()
    
    # Categories that trigger the 10%/90% split when sold via Personal account
    SPLIT_CATEGORIES = ["Resources - Ore", "Resources - Fluids"]
    PERSONAL_SPLIT = 0.10  # 10% to Personal
    COMPANY_SPLIT = 0.90   # 90% to Company
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = get_database()
        self.importer = ExcelImporter(self.db)
        
        # Cache for items (for autocomplete)
        self.all_items: list[Item] = []
        self.item_names: list[str] = []
        self.categories: list[str] = []
        self.locations: list[str] = []
        
        # Transaction data
        self.transactions: list[dict] = []
        
        # Opening balance
        self.opening_personal = 100000.0
        self.opening_company = 0.0
        
        self._setup_ui()
        self._load_reference_data()
        self._load_transactions()
    
    def _setup_ui(self):
        """Setup the UI components."""
        layout = QVBoxLayout(self)
        
        # Top section: Opening Balance
        layout.addWidget(self._create_opening_balance_group())
        
        # Middle section: Action buttons
        layout.addLayout(self._create_button_bar())
        
        # Main section: Transaction table
        self.table = self._create_table()
        layout.addWidget(self.table)
        
        # Bottom section: Transaction count
        self.status_label = QLabel("Transactions: 0")
        layout.addWidget(self.status_label)
    
    def _create_opening_balance_group(self) -> QGroupBox:
        """Create the opening balance controls."""
        group = QGroupBox("💰 Opening Balance (Row 1)")
        layout = QHBoxLayout(group)
        
        # Personal Balance (whole numbers only)
        layout.addWidget(QLabel("Personal Balance:"))
        self.personal_balance_spin = QDoubleSpinBox()
        self.personal_balance_spin.setRange(0, 999999999)
        self.personal_balance_spin.setDecimals(0)  # Whole numbers only
        self.personal_balance_spin.setPrefix("$")
        self.personal_balance_spin.setValue(100000)
        self.personal_balance_spin.setSingleStep(1000)
        self.personal_balance_spin.valueChanged.connect(self._on_opening_balance_changed)
        layout.addWidget(self.personal_balance_spin)
        
        layout.addSpacing(30)
        
        # Company Balance (whole numbers only)
        layout.addWidget(QLabel("Company Balance:"))
        self.company_balance_spin = QDoubleSpinBox()
        self.company_balance_spin.setRange(0, 999999999)
        self.company_balance_spin.setDecimals(0)  # Whole numbers only
        self.company_balance_spin.setPrefix("$")
        self.company_balance_spin.setValue(0)
        self.company_balance_spin.setSingleStep(1000)
        self.company_balance_spin.valueChanged.connect(self._on_opening_balance_changed)
        layout.addWidget(self.company_balance_spin)
        
        layout.addStretch()
        
        # Info label
        info_label = QLabel("Hardcore: $100,000 | Standard: Any amount | Creative: N/A")
        info_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(info_label)
        
        return group
    
    def _create_button_bar(self) -> QHBoxLayout:
        """Create the action button bar."""
        layout = QHBoxLayout()
        
        # Add Transaction button
        self.add_btn = QPushButton("➕ Add Transaction")
        self.add_btn.clicked.connect(self._on_add_transaction)
        layout.addWidget(self.add_btn)
        
        # Edit Transaction button
        self.edit_btn = QPushButton("✏️ Edit Selected")
        self.edit_btn.clicked.connect(self._on_edit_transaction)
        layout.addWidget(self.edit_btn)
        
        # Delete Transaction button
        self.delete_btn = QPushButton("🗑️ Delete Selected")
        self.delete_btn.clicked.connect(self._on_delete_transaction)
        layout.addWidget(self.delete_btn)
        
        layout.addSpacing(20)
        
        # Import button
        self.import_btn = QPushButton("📥 Import")
        self.import_btn.clicked.connect(self._on_import)
        layout.addWidget(self.import_btn)
        
        # Export button
        self.export_btn = QPushButton("📤 Export")
        self.export_btn.clicked.connect(self._on_export)
        layout.addWidget(self.export_btn)
        
        layout.addStretch()
        
        # Recalculate button
        self.recalc_btn = QPushButton("🔄 Recalculate Balances")
        self.recalc_btn.clicked.connect(self._recalculate_all_balances)
        layout.addWidget(self.recalc_btn)
        
        return layout
    
    def _create_table(self) -> QTableWidget:
        """Create the transaction table."""
        table = QTableWidget()
        
        # Define columns (matching Excel structure)
        self.columns = [
            "Date",
            "Type",
            "Item",
            "Category",
            "Qty",
            "Unit Price",
            "Subtotal",
            "Discount",
            "Total",
            "Personal Income",
            "Company Income",
            "Personal Expense",
            "Company Expense",
            "Account",
            "Location",
            "Company Balance",
            "Personal Balance",
            "Notes",
        ]
        
        table.setColumnCount(len(self.columns))
        table.setHorizontalHeaderLabels(self.columns)
        
        # Configure table
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        table.setSortingEnabled(False)  # Keep chronological order
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)  # Edit via dialog
        
        # Double-click to edit
        table.doubleClicked.connect(self._on_edit_transaction)
        
        # Configure header
        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Item column stretches
        
        return table
    
    def _load_reference_data(self):
        """Load items, categories, and locations for autocomplete."""
        self.all_items = self.importer.get_all_items()
        self.item_names = list(set(item.name for item in self.all_items))
        self.item_names.sort()
        
        self.categories = self.db.get_category_names()
        self.locations = self.db.get_location_names()
    
    def _load_transactions(self):
        """Load transactions from database."""
        self.transactions = []
        
        with self.db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM transactions ORDER BY id
            """)
            rows = cursor.fetchall()
            
            for row in rows:
                self.transactions.append(dict(row))
        
        # Load opening balance from first transaction or game settings
        if self.transactions and self.transactions[0].get('type') == 'Opening':
            self.opening_personal = self.transactions[0].get('personal_balance', 100000)
            self.opening_company = self.transactions[0].get('company_balance', 0)
        else:
            # Try to get from game settings
            settings = self.db.get_game_settings()
            self.opening_personal = settings.starting_capital
            self.opening_company = 0
        
        # Update spinboxes
        self.personal_balance_spin.blockSignals(True)
        self.company_balance_spin.blockSignals(True)
        self.personal_balance_spin.setValue(self.opening_personal)
        self.company_balance_spin.setValue(self.opening_company)
        self.personal_balance_spin.blockSignals(False)
        self.company_balance_spin.blockSignals(False)
        
        self._populate_table()
    
    def _populate_table(self):
        """Populate the table with transactions."""
        # Add opening balance as row 0, then all transactions
        total_rows = 1 + len([t for t in self.transactions if t.get('type') != 'Opening'])
        self.table.setRowCount(total_rows)
        
        # Row 0: Opening Balance
        self._populate_opening_row()
        
        # Rows 1+: Transactions
        row = 1
        for txn in self.transactions:
            if txn.get('type') == 'Opening':
                continue  # Skip opening balance in transaction list
            self._populate_transaction_row(row, txn)
            row += 1
        
        self._update_status()
    
    def _populate_opening_row(self):
        """Populate the opening balance row (row 0)."""
        row = 0
        
        # Get game start date
        settings = self.db.get_game_settings()
        start_date = settings.game_start_date.strftime("%Y-%m-%d") if settings.game_start_date else ""
        
        data = [
            start_date,  # Date
            "Opening",   # Type
            "Opening Balance",  # Item
            "",  # Category
            "",  # Qty
            "",  # Unit Price
            "",  # Subtotal
            "",  # Discount
            "",  # Total
            "",  # Personal Income
            "",  # Company Income
            "",  # Personal Expense
            "",  # Company Expense
            "",  # Account
            "",  # Location
            f"${self.opening_company:,.0f}",  # Company Balance (whole number)
            f"${self.opening_personal:,.0f}",  # Personal Balance (whole number)
            "",  # Notes
        ]
        
        for col, value in enumerate(data):
            item = QTableWidgetItem(str(value))
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            
            # Style opening row differently
            item.setBackground(QColor("#e3f2fd"))  # Light blue background
            
            # Right-align currency columns
            if col in [4, 5, 6, 7, 8, 9, 10, 11, 12, 15, 16]:
                item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            
            self.table.setItem(row, col, item)
    
    def _populate_transaction_row(self, row: int, txn: dict):
        """Populate a transaction row."""
        # Format currency values - whole numbers for totals/balances
        def fmt_currency(val):
            if val is None or val == 0:
                return ""
            return f"${val:,.0f}"
        
        # Unit price can have decimals (for bulk pricing like $66.50)
        def fmt_unit_price(val):
            if val is None or val == 0:
                return ""
            # Show decimals only if needed
            if val == int(val):
                return f"${val:,.0f}"
            return f"${val:,.2f}"
        
        def fmt_qty(val):
            if val is None:
                return ""
            return str(int(val)) if val == int(val) else str(val)
        
        data = [
            txn.get('date', ''),
            txn.get('type', ''),
            txn.get('item', ''),
            txn.get('category', ''),
            fmt_qty(txn.get('quantity')),
            fmt_unit_price(txn.get('unit_price')),  # Can have decimals
            fmt_currency(txn.get('subtotal')),
            fmt_currency(txn.get('discount')),
            fmt_currency(txn.get('total')),
            fmt_currency(txn.get('personal_income')),
            fmt_currency(txn.get('company_income')),
            fmt_currency(txn.get('personal_expense')),
            fmt_currency(txn.get('company_expense')),
            txn.get('account', ''),
            txn.get('location', ''),
            fmt_currency(txn.get('company_balance')),
            fmt_currency(txn.get('personal_balance')),
            txn.get('notes', ''),
        ]
        
        for col, value in enumerate(data):
            item = QTableWidgetItem(str(value) if value else "")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            
            # Store transaction ID for reference
            if col == 0:
                item.setData(Qt.ItemDataRole.UserRole, txn.get('id'))
            
            # Right-align numeric columns
            if col in [4, 5, 6, 7, 8, 9, 10, 11, 12, 15, 16]:
                item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            
            # Color income green, expense red
            if col == 9 and txn.get('personal_income', 0) > 0:  # Personal Income
                item.setForeground(QColor("#2e7d32"))
            elif col == 10 and txn.get('company_income', 0) > 0:  # Company Income
                item.setForeground(QColor("#2e7d32"))
            elif col == 11 and txn.get('personal_expense', 0) < 0:  # Personal Expense
                item.setForeground(QColor("#c62828"))
            elif col == 12 and txn.get('company_expense', 0) < 0:  # Company Expense
                item.setForeground(QColor("#c62828"))
            
            self.table.setItem(row, col, item)
    
    def _update_status(self):
        """Update the status label."""
        count = len([t for t in self.transactions if t.get('type') != 'Opening'])
        self.status_label.setText(f"Transactions: {count}")
    
    def _on_opening_balance_changed(self):
        """Handle opening balance changes."""
        self.opening_personal = self.personal_balance_spin.value()
        self.opening_company = self.company_balance_spin.value()
        
        # Update the opening row in table
        self._populate_opening_row()
        
        # Recalculate all running balances
        self._recalculate_all_balances()
        
        # Save to database (as first transaction or update game settings)
        self._save_opening_balance()
    
    def _save_opening_balance(self):
        """Save opening balance to database."""
        settings = self.db.get_game_settings()
        settings.starting_capital = self.opening_personal
        self.db.save_game_settings(settings)
        
        # Also save/update Opening transaction
        with self.db._get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if opening transaction exists
            cursor.execute("SELECT id FROM transactions WHERE type = 'Opening' LIMIT 1")
            existing = cursor.fetchone()
            
            if existing:
                cursor.execute("""
                    UPDATE transactions 
                    SET personal_balance = ?, company_balance = ?
                    WHERE type = 'Opening'
                """, (self.opening_personal, self.opening_company))
            else:
                cursor.execute("""
                    INSERT INTO transactions 
                    (date, type, item, personal_balance, company_balance)
                    VALUES (?, 'Opening', 'Opening Balance', ?, ?)
                """, (
                    settings.game_start_date.isoformat() if settings.game_start_date else date.today().isoformat(),
                    self.opening_personal,
                    self.opening_company
                ))
    
    def _on_add_transaction(self):
        """Show dialog to add a new transaction."""
        dialog = TransactionDialog(
            self,
            items=self.all_items,
            item_names=self.item_names,
            categories=self.categories,
            locations=self.locations,
        )
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            txn_data = dialog.get_transaction_data()
            self._add_transaction(txn_data)
    
    def _add_transaction(self, txn_data: dict):
        """Add a new transaction to the database."""
        # Calculate income/expense based on type, account, and category
        txn_data = self._calculate_income_expense(txn_data)
        
        with self.db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO transactions 
                (date, type, item, category, quantity, unit_price, subtotal, discount, total,
                 personal_income, company_income, personal_expense, company_expense,
                 account, location, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                txn_data.get('date'),
                txn_data.get('type'),
                txn_data.get('item'),
                txn_data.get('category'),
                txn_data.get('quantity'),
                txn_data.get('unit_price'),
                txn_data.get('subtotal'),
                txn_data.get('discount'),
                txn_data.get('total'),
                txn_data.get('personal_income'),
                txn_data.get('company_income'),
                txn_data.get('personal_expense'),
                txn_data.get('company_expense'),
                txn_data.get('account'),
                txn_data.get('location'),
                txn_data.get('notes'),
            ))
            txn_data['id'] = cursor.lastrowid
        
        self.transactions.append(txn_data)
        self._recalculate_all_balances()
        self._populate_table()
        self.data_changed.emit()
    
    def _calculate_income_expense(self, txn_data: dict) -> dict:
        """Calculate income/expense fields based on transaction type and account."""
        txn_type = txn_data.get('type')
        account = txn_data.get('account')
        category = txn_data.get('category', '')
        total = txn_data.get('total', 0)
        
        # Initialize
        txn_data['personal_income'] = 0
        txn_data['company_income'] = 0
        txn_data['personal_expense'] = 0
        txn_data['company_expense'] = 0
        
        if txn_type == 'Sale':
            if account == 'Personal':
                # Check if this triggers the split (Resources - Ore or Fluids)
                if any(category.startswith(split_cat) for split_cat in self.SPLIT_CATEGORIES):
                    # 10% Personal, 90% Company
                    txn_data['personal_income'] = total * self.PERSONAL_SPLIT
                    txn_data['company_income'] = total * self.COMPANY_SPLIT
                else:
                    # 100% Personal
                    txn_data['personal_income'] = total
            else:  # Company account
                # 100% Company
                txn_data['company_income'] = total
        
        elif txn_type == 'Purchase':
            if account == 'Personal':
                txn_data['personal_expense'] = -total  # Negative for expense
            else:  # Company account
                txn_data['company_expense'] = -total
        
        elif txn_type == 'Transfer':
            # Transfer between accounts - handled specially
            # Positive = receiving, Negative = sending
            pass  # Will need more info about transfer direction
        
        return txn_data
    
    def _recalculate_all_balances(self):
        """Recalculate running balances for all transactions."""
        personal_balance = self.opening_personal
        company_balance = self.opening_company
        
        with self.db._get_connection() as conn:
            cursor = conn.cursor()
            
            for txn in self.transactions:
                if txn.get('type') == 'Opening':
                    continue
                
                # Add income, subtract expenses
                personal_balance += txn.get('personal_income', 0)
                personal_balance += txn.get('personal_expense', 0)  # Already negative
                company_balance += txn.get('company_income', 0)
                company_balance += txn.get('company_expense', 0)  # Already negative
                
                # Update transaction
                txn['personal_balance'] = personal_balance
                txn['company_balance'] = company_balance
                
                # Update in database
                cursor.execute("""
                    UPDATE transactions 
                    SET personal_balance = ?, company_balance = ?
                    WHERE id = ?
                """, (personal_balance, company_balance, txn.get('id')))
        
        self._populate_table()
    
    def _on_edit_transaction(self):
        """Edit the selected transaction."""
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.information(self, "Edit", "Please select a transaction to edit.")
            return
        
        row = selected[0].row()
        
        # Can't edit opening balance row via this method
        if row == 0:
            QMessageBox.information(
                self, "Edit", 
                "Use the Opening Balance fields above to edit the starting balances."
            )
            return
        
        # Get transaction ID from row
        txn_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        
        # Find transaction
        txn = None
        for t in self.transactions:
            if t.get('id') == txn_id:
                txn = t
                break
        
        if not txn:
            return
        
        dialog = TransactionDialog(
            self,
            items=self.all_items,
            item_names=self.item_names,
            categories=self.categories,
            locations=self.locations,
            existing_data=txn,
        )
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            txn_data = dialog.get_transaction_data()
            txn_data['id'] = txn_id
            self._update_transaction(txn_data)
    
    def _update_transaction(self, txn_data: dict):
        """Update an existing transaction."""
        txn_data = self._calculate_income_expense(txn_data)
        
        with self.db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE transactions SET
                    date = ?, type = ?, item = ?, category = ?,
                    quantity = ?, unit_price = ?, subtotal = ?, discount = ?, total = ?,
                    personal_income = ?, company_income = ?,
                    personal_expense = ?, company_expense = ?,
                    account = ?, location = ?, notes = ?
                WHERE id = ?
            """, (
                txn_data.get('date'),
                txn_data.get('type'),
                txn_data.get('item'),
                txn_data.get('category'),
                txn_data.get('quantity'),
                txn_data.get('unit_price'),
                txn_data.get('subtotal'),
                txn_data.get('discount'),
                txn_data.get('total'),
                txn_data.get('personal_income'),
                txn_data.get('company_income'),
                txn_data.get('personal_expense'),
                txn_data.get('company_expense'),
                txn_data.get('account'),
                txn_data.get('location'),
                txn_data.get('notes'),
                txn_data.get('id'),
            ))
        
        # Update in memory
        for i, t in enumerate(self.transactions):
            if t.get('id') == txn_data.get('id'):
                self.transactions[i] = txn_data
                break
        
        self._recalculate_all_balances()
        self.data_changed.emit()
    
    def _on_delete_transaction(self):
        """Delete the selected transaction."""
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.information(self, "Delete", "Please select a transaction to delete.")
            return
        
        row = selected[0].row()
        
        # Can't delete opening balance
        if row == 0:
            QMessageBox.warning(self, "Delete", "Cannot delete the Opening Balance row.")
            return
        
        # Confirm
        reply = QMessageBox.question(
            self, "Confirm Delete",
            "Are you sure you want to delete this transaction?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # Get transaction ID
        txn_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        
        # Delete from database
        with self.db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM transactions WHERE id = ?", (txn_id,))
        
        # Remove from memory
        self.transactions = [t for t in self.transactions if t.get('id') != txn_id]
        
        self._recalculate_all_balances()
        self.data_changed.emit()
    
    def _on_import(self):
        """Import transactions from file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Ledger",
            "",
            "Excel/CSV Files (*.xlsx *.xls *.csv);;All Files (*)"
        )
        
        if not file_path:
            return
        
        try:
            results = self.importer.import_ledger(Path(file_path))
            
            msg = f"Import Complete!\n\n"
            msg += f"✓ Transactions: {results['transactions']}"
            
            if results['errors']:
                msg += f"\n\n⚠ Errors:\n" + "\n".join(results['errors'][:5])
            
            QMessageBox.information(self, "Import Results", msg)
            
            self._load_transactions()
            self.data_changed.emit()
            
        except Exception as e:
            QMessageBox.critical(self, "Import Error", f"Failed to import:\n{str(e)}")
    
    def _on_export(self):
        """Export transactions to file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Ledger",
            "ledger_export.csv",
            "CSV Files (*.csv);;Excel Files (*.xlsx)"
        )
        
        if not file_path:
            return
        
        try:
            import pandas as pd
            
            # Build data for export
            data = []
            
            # Add opening balance
            settings = self.db.get_game_settings()
            data.append({
                'Date': settings.game_start_date.isoformat() if settings.game_start_date else '',
                'Type': 'Opening',
                'Item': 'Opening Balance',
                'Category': '',
                'Qty': '',
                'Unit Price': '',
                'Subtotal': '',
                'Discount': '',
                'Total': '',
                'Personal Income': '',
                'Company Income': '',
                'Personal Expense': '',
                'Company Expense': '',
                'Account': '',
                'Location': '',
                'Company Balance': self.opening_company,
                'Personal Balance': self.opening_personal,
                'Notes': '',
            })
            
            # Add transactions
            for txn in self.transactions:
                if txn.get('type') == 'Opening':
                    continue
                data.append({
                    'Date': txn.get('date', ''),
                    'Type': txn.get('type', ''),
                    'Item': txn.get('item', ''),
                    'Category': txn.get('category', ''),
                    'Qty': txn.get('quantity', ''),
                    'Unit Price': txn.get('unit_price', ''),
                    'Subtotal': txn.get('subtotal', ''),
                    'Discount': txn.get('discount', ''),
                    'Total': txn.get('total', ''),
                    'Personal Income': txn.get('personal_income', ''),
                    'Company Income': txn.get('company_income', ''),
                    'Personal Expense': txn.get('personal_expense', ''),
                    'Company Expense': txn.get('company_expense', ''),
                    'Account': txn.get('account', ''),
                    'Location': txn.get('location', ''),
                    'Company Balance': txn.get('company_balance', ''),
                    'Personal Balance': txn.get('personal_balance', ''),
                    'Notes': txn.get('notes', ''),
                })
            
            df = pd.DataFrame(data)
            
            if file_path.endswith('.xlsx'):
                df.to_excel(file_path, index=False)
            else:
                df.to_csv(file_path, index=False)
            
            QMessageBox.information(self, "Export", f"Ledger exported to:\n{file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export:\n{str(e)}")


class TransactionDialog(QDialog):
    """Dialog for adding/editing a transaction."""
    
    def __init__(
        self, 
        parent=None, 
        items: list[Item] = None,
        item_names: list[str] = None,
        categories: list[str] = None,
        locations: list[str] = None,
        existing_data: dict = None
    ):
        super().__init__(parent)
        self.items = items or []
        self.item_names = item_names or []
        self.categories = categories or []
        self.locations = locations or []
        self.existing_data = existing_data
        
        self.setWindowTitle("Edit Transaction" if existing_data else "Add Transaction")
        self.setMinimumWidth(500)
        
        self._setup_ui()
        
        if existing_data:
            self._populate_from_data(existing_data)
    
    def _setup_ui(self):
        """Setup the dialog UI."""
        layout = QFormLayout(self)
        
        # Date
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        layout.addRow("Date:", self.date_edit)
        
        # Type
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Purchase", "Sale", "Transfer"])
        self.type_combo.currentTextChanged.connect(self._on_type_changed)
        layout.addRow("Type:", self.type_combo)
        
        # Item (with autocomplete)
        self.item_edit = QLineEdit()
        completer = QCompleter(self.item_names)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.item_edit.setCompleter(completer)
        self.item_edit.textChanged.connect(self._on_item_changed)
        layout.addRow("Item:", self.item_edit)
        
        # Category (auto-filled from item, but editable)
        self.category_combo = QComboBox()
        self.category_combo.setEditable(True)
        self.category_combo.addItem("")
        self.category_combo.addItems(self.categories)
        layout.addRow("Category:", self.category_combo)
        
        # Quantity
        self.qty_spin = QSpinBox()
        self.qty_spin.setRange(1, 99999)
        self.qty_spin.setValue(1)
        self.qty_spin.valueChanged.connect(self._calculate_totals)
        layout.addRow("Quantity:", self.qty_spin)
        
        # Unit Price (can have decimals for bulk pricing)
        self.unit_price_spin = QDoubleSpinBox()
        self.unit_price_spin.setRange(0, 99999999)
        self.unit_price_spin.setDecimals(2)  # Allow decimals like $66.50
        self.unit_price_spin.setPrefix("$")
        self.unit_price_spin.valueChanged.connect(self._calculate_totals)
        layout.addRow("Unit Price:", self.unit_price_spin)
        
        # Subtotal (calculated, whole number)
        self.subtotal_label = QLabel("$0")
        layout.addRow("Subtotal:", self.subtotal_label)
        
        # Discount (whole number)
        self.discount_spin = QDoubleSpinBox()
        self.discount_spin.setRange(0, 99999999)
        self.discount_spin.setDecimals(0)  # Whole numbers
        self.discount_spin.setPrefix("$")
        self.discount_spin.valueChanged.connect(self._calculate_totals)
        layout.addRow("Discount:", self.discount_spin)
        
        # Total (calculated, whole number)
        self.total_label = QLabel("$0")
        self.total_label.setStyleSheet("font-weight: bold;")
        layout.addRow("Total:", self.total_label)
        
        # Account
        self.account_combo = QComboBox()
        self.account_combo.addItems(["Personal", "Company"])
        layout.addRow("Account:", self.account_combo)
        
        # Location
        self.location_combo = QComboBox()
        self.location_combo.setEditable(True)
        self.location_combo.addItem("")
        self.location_combo.addItems(self.locations)
        layout.addRow("Location:", self.location_combo)
        
        # Notes
        self.notes_edit = QLineEdit()
        layout.addRow("Notes:", self.notes_edit)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
    
    def _on_type_changed(self, txn_type: str):
        """Handle transaction type change."""
        # Could adjust UI based on type (e.g., Transfer has different fields)
        pass
    
    def _on_item_changed(self, item_name: str):
        """Handle item selection - auto-fill category and price."""
        # Find item in list
        for item in self.items:
            if item.name.lower() == item_name.lower():
                # Set category
                idx = self.category_combo.findText(item.category)
                if idx >= 0:
                    self.category_combo.setCurrentIndex(idx)
                else:
                    self.category_combo.setCurrentText(item.category)
                
                # Set price based on transaction type
                if self.type_combo.currentText() == "Sale":
                    self.unit_price_spin.setValue(item.sell_price)
                else:
                    # Use current buy price (with discounts) - would need reference to parent tab
                    self.unit_price_spin.setValue(item.buy_price)
                
                break
    
    def _calculate_totals(self):
        """Calculate subtotal and total (matching game rounding behavior)."""
        import math
        
        qty = self.qty_spin.value()
        unit_price = self.unit_price_spin.value()
        discount = self.discount_spin.value()
        
        # Game rounds UP for single unit, exact for bulk (qty >= 2)
        if qty == 1:
            subtotal = math.ceil(unit_price)  # Round up for single unit
        else:
            subtotal = round(qty * unit_price)  # Bulk pricing is exact, round to nearest
        
        total = round(subtotal - discount)  # Round to whole number
        
        self.subtotal_label.setText(f"${subtotal:,.0f}")
        self.total_label.setText(f"${total:,.0f}")
    
    def _populate_from_data(self, data: dict):
        """Populate form from existing transaction data."""
        if data.get('date'):
            try:
                d = datetime.fromisoformat(str(data['date'])[:10])
                self.date_edit.setDate(QDate(d.year, d.month, d.day))
            except:
                pass
        
        if data.get('type'):
            idx = self.type_combo.findText(data['type'])
            if idx >= 0:
                self.type_combo.setCurrentIndex(idx)
        
        if data.get('item'):
            self.item_edit.setText(data['item'])
        
        if data.get('category'):
            self.category_combo.setCurrentText(data['category'])
        
        if data.get('quantity'):
            self.qty_spin.setValue(int(data['quantity']))
        
        if data.get('unit_price'):
            self.unit_price_spin.setValue(float(data['unit_price']))
        
        if data.get('discount'):
            self.discount_spin.setValue(float(data['discount']))
        
        if data.get('account'):
            idx = self.account_combo.findText(data['account'])
            if idx >= 0:
                self.account_combo.setCurrentIndex(idx)
        
        if data.get('location'):
            self.location_combo.setCurrentText(data['location'])
        
        if data.get('notes'):
            self.notes_edit.setText(data['notes'])
        
        self._calculate_totals()
    
    def get_transaction_data(self) -> dict:
        """Get the transaction data from the form."""
        import math
        
        qty = self.qty_spin.value()
        unit_price = self.unit_price_spin.value()
        discount = round(self.discount_spin.value())  # Whole number
        
        # Game rounds UP for single unit, exact for bulk (qty >= 2)
        if qty == 1:
            subtotal = math.ceil(unit_price)  # Round up for single unit
        else:
            subtotal = round(qty * unit_price)  # Bulk pricing is exact, round to nearest
        
        total = round(subtotal - discount)  # Whole number
        
        return {
            'date': self.date_edit.date().toString("yyyy-MM-dd"),
            'type': self.type_combo.currentText(),
            'item': self.item_edit.text(),
            'category': self.category_combo.currentText(),
            'quantity': qty,
            'unit_price': unit_price,  # Keep decimals for bulk pricing reference
            'subtotal': subtotal,
            'discount': discount,
            'total': total,
            'account': self.account_combo.currentText(),
            'location': self.location_combo.currentText(),
            'notes': self.notes_edit.text(),
        }
