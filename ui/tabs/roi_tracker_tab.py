"""
ROI Tracker Tab - Track investment performance and returns.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QFormLayout, QComboBox, QSpinBox, QDoubleSpinBox, QLineEdit,
    QDateEdit, QDialog, QDialogButtonBox, QRadioButton, QButtonGroup,
    QMessageBox, QAbstractItemView, QFrame, QTextEdit, QTabWidget
)
from PyQt6.QtCore import Qt, pyqtSignal, QDate
from PyQt6.QtGui import QFont, QColor
from datetime import datetime, date


class ROITrackerTab(QWidget):
    """ROI Tracker for investment performance tracking."""
    
    data_changed = pyqtSignal()
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        
        # Get database
        from core.database import get_database
        self.db = get_database()
        
        # Investment data storage
        self.investments = []
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the ROI Tracker interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(6)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # === Summary Dashboard ===
        self._create_summary_section(layout)
        
        # === Middle Section: Fuel/Maintenance (left) + Add Investment & Table (right) ===
        middle_layout = QHBoxLayout()
        middle_layout.setSpacing(8)
        middle_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Left: Fuel Tracking + Maintenance Tracking in tabs
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(4)
        
        self.ops_tabs = QTabWidget()
        self.ops_tabs.setMaximumHeight(220)
        
        # Fuel tab
        fuel_widget = QWidget()
        self._create_fuel_content(fuel_widget)
        self.ops_tabs.addTab(fuel_widget, "⛽ Fuel")
        
        # Maintenance tab
        maint_widget = QWidget()
        self._create_maintenance_content(maint_widget)
        self.ops_tabs.addTab(maint_widget, "🔧 Maintenance")
        
        left_layout.addWidget(self.ops_tabs)
        left_layout.addStretch()  # Push tabs to top
        middle_layout.addWidget(left_widget, 1)
        
        # Right: Add Investment + Investment Table stacked vertically
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(6)
        
        self._create_add_investment_section(right_layout)
        self._create_investment_table(right_layout)
        
        middle_layout.addWidget(right_widget, 2)  # Right side gets more space
        
        layout.addLayout(middle_layout, 1)  # Takes remaining space
        
        # Initial update
        self._update_summary()
        self._update_fuel_summary()
    
    def _create_summary_section(self, parent_layout):
        """Create the summary dashboard cards."""
        summary_group = QGroupBox("📊 ROI Summary Dashboard")
        summary_layout = QVBoxLayout(summary_group)
        summary_layout.setContentsMargins(8, 8, 8, 8)
        summary_layout.setSpacing(8)
        
        # Row 1: 3 cards
        row1 = QHBoxLayout()
        row1.setSpacing(10)
        
        # Total Invested Card
        invested_card = self._create_summary_card(
            "💰 TOTAL INVESTED", "$0", "0 items tracked"
        )
        self.invested_value = invested_card.findChild(QLabel, "value_label")
        self.invested_subtitle = invested_card.findChild(QLabel, "subtitle_label")
        row1.addWidget(invested_card, 1)
        
        # Total Revenue Card
        revenue_card = self._create_summary_card(
            "📈 TOTAL REVENUE", "$0", "Auto + Manual"
        )
        self.revenue_value = revenue_card.findChild(QLabel, "value_label")
        row1.addWidget(revenue_card, 1)
        
        # Net Profit Card
        profit_card = self._create_summary_card(
            "💵 NET PROFIT", "$0", "0% overall ROI"
        )
        self.profit_value = profit_card.findChild(QLabel, "value_label")
        self.profit_subtitle = profit_card.findChild(QLabel, "subtitle_label")
        row1.addWidget(profit_card, 1)
        
        summary_layout.addLayout(row1)
        
        # Row 2: 3 cards
        row2 = QHBoxLayout()
        row2.setSpacing(10)
        
        # Success Rate Card
        success_card = self._create_summary_card(
            "✅ SUCCESS RATE", "0%", "0 of 0 profitable"
        )
        self.success_value = success_card.findChild(QLabel, "value_label")
        self.success_subtitle = success_card.findChild(QLabel, "subtitle_label")
        row2.addWidget(success_card, 1)
        
        # Best ROI Card
        best_card = self._create_summary_card(
            "🌟 BEST ROI", "-", "+0% ROI"
        )
        self.best_value = best_card.findChild(QLabel, "value_label")
        self.best_subtitle = best_card.findChild(QLabel, "subtitle_label")
        row2.addWidget(best_card, 1)
        
        # Daily Profit Card
        daily_card = self._create_summary_card(
            "💰 DAILY PROFIT", "$0/day", "Average across all"
        )
        self.daily_value = daily_card.findChild(QLabel, "value_label")
        row2.addWidget(daily_card, 1)
        
        summary_layout.addLayout(row2)
        parent_layout.addWidget(summary_group)
    
    def _create_summary_card(self, title, value, subtitle):
        """Create a summary card widget."""
        card = QFrame()
        card.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        card.setStyleSheet("background-color: #E8F4FD; border-radius: 5px;")
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(2)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("", 9, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setObjectName("value_label")
        value_label.setFont(QFont("", 14, QFont.Weight.Bold))
        value_label.setStyleSheet("color: #1F4E79;")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(value_label)
        
        subtitle_label = QLabel(subtitle)
        subtitle_label.setObjectName("subtitle_label")
        subtitle_label.setStyleSheet("color: #666666; font-size: 9px;")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle_label)
        
        return card
    
    def _create_fuel_section(self, parent_layout):
        """Create the fuel tracking summary section - DEPRECATED, use _create_fuel_content."""
        pass  # Kept for compatibility, actual content in _create_fuel_content
    
    def _create_fuel_content(self, parent_widget):
        """Create fuel tracking content for tab."""
        fuel_layout = QVBoxLayout(parent_widget)
        fuel_layout.setContentsMargins(6, 6, 6, 6)
        fuel_layout.setSpacing(4)
        
        # Summary row
        summary_layout = QHBoxLayout()
        summary_layout.setSpacing(10)
        
        self.fuel_total_label = QLabel("Total Fuel: 0 L")
        self.fuel_total_label.setFont(QFont("", 9, QFont.Weight.Bold))
        summary_layout.addWidget(self.fuel_total_label)
        
        self.fuel_cost_label = QLabel("Total Cost: $0")
        self.fuel_cost_label.setFont(QFont("", 9, QFont.Weight.Bold))
        self.fuel_cost_label.setStyleSheet("color: #c62828;")
        summary_layout.addWidget(self.fuel_cost_label)
        
        summary_layout.addStretch()
        
        refresh_btn = QPushButton("🔄")
        refresh_btn.setFixedSize(24, 24)
        refresh_btn.setToolTip("Refresh fuel data from Ledger")
        refresh_btn.clicked.connect(self._update_fuel_summary)
        summary_layout.addWidget(refresh_btn)
        
        fuel_layout.addLayout(summary_layout)
        
        # Fuel table by vehicle
        self.fuel_table = QTableWidget()
        self.fuel_table.setColumnCount(4)
        self.fuel_table.setHorizontalHeaderLabels(["Vehicle", "Liters", "Cost", "Txns"])
        self.fuel_table.setAlternatingRowColors(True)
        self.fuel_table.verticalHeader().setDefaultSectionSize(22)
        
        header = self.fuel_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        
        fuel_layout.addWidget(self.fuel_table, 1)
    
    def _create_maintenance_content(self, parent_widget):
        """Create maintenance tracking content for tab."""
        maint_layout = QVBoxLayout(parent_widget)
        maint_layout.setContentsMargins(6, 6, 6, 6)
        maint_layout.setSpacing(4)
        
        # Summary row
        summary_layout = QHBoxLayout()
        summary_layout.setSpacing(10)
        
        self.maint_total_label = QLabel("Total: $0")
        self.maint_total_label.setFont(QFont("", 9, QFont.Weight.Bold))
        self.maint_total_label.setStyleSheet("color: #c62828;")
        summary_layout.addWidget(self.maint_total_label)
        
        self.maint_count_label = QLabel("0 records")
        summary_layout.addWidget(self.maint_count_label)
        
        summary_layout.addStretch()
        
        add_maint_btn = QPushButton("➕ Add")
        add_maint_btn.setFixedWidth(50)
        add_maint_btn.clicked.connect(self._add_maintenance)
        summary_layout.addWidget(add_maint_btn)
        
        maint_layout.addLayout(summary_layout)
        
        # Maintenance table
        self.maint_table = QTableWidget()
        self.maint_table.setColumnCount(5)
        self.maint_table.setHorizontalHeaderLabels(["Date", "Equipment", "Type", "Cost", "Notes"])
        self.maint_table.setAlternatingRowColors(True)
        self.maint_table.verticalHeader().setDefaultSectionSize(22)
        self.maint_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        
        header = self.maint_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        
        maint_layout.addWidget(self.maint_table, 1)
        
        # Storage for maintenance records
        self.maintenance_records = []
    
    def _add_maintenance(self):
        """Show dialog to add maintenance record."""
        dialog = MaintenanceDialog(self, self._get_current_game_date())
        if dialog.exec() == QDialog.DialogCode.Accepted:
            record = dialog.get_record()
            if record:
                self.maintenance_records.append(record)
                self._update_maintenance_table()
                self.data_changed.emit()
    
    def _update_maintenance_table(self):
        """Update the maintenance table."""
        self.maint_table.setRowCount(len(self.maintenance_records))
        total_cost = 0
        
        for row, record in enumerate(self.maintenance_records):
            # Date
            date_str = record.get('date', '')
            self.maint_table.setItem(row, 0, QTableWidgetItem(date_str))
            
            # Equipment
            self.maint_table.setItem(row, 1, QTableWidgetItem(record.get('equipment', '')))
            
            # Type
            self.maint_table.setItem(row, 2, QTableWidgetItem(record.get('type', '')))
            
            # Cost
            cost = record.get('cost', 0)
            total_cost += cost
            cost_item = QTableWidgetItem(f"${cost:,.0f}")
            cost_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            cost_item.setForeground(QColor("#c62828"))
            self.maint_table.setItem(row, 3, cost_item)
            
            # Notes
            self.maint_table.setItem(row, 4, QTableWidgetItem(record.get('notes', '')))
        
        self.maint_total_label.setText(f"Total: ${total_cost:,.0f}")
        self.maint_count_label.setText(f"{len(self.maintenance_records)} records")
    
    def _update_fuel_summary(self):
        """Update the fuel summary from Ledger data."""
        try:
            if not hasattr(self.main_window, 'ledger_tab'):
                return
            
            ledger = self.main_window.ledger_tab
            fuel_data = ledger.get_fuel_by_vehicle()
            
            # Calculate totals
            total_liters = sum(v['liters'] for v in fuel_data.values())
            total_cost = sum(v['cost'] for v in fuel_data.values())
            
            self.fuel_total_label.setText(f"Total Fuel: {total_liters:,} L")
            self.fuel_cost_label.setText(f"Total Cost: ${total_cost:,.0f}")
            
            # Populate table
            self.fuel_table.setRowCount(len(fuel_data))
            
            for row, (vehicle, data) in enumerate(sorted(fuel_data.items())):
                # Vehicle name
                self.fuel_table.setItem(row, 0, QTableWidgetItem(vehicle))
                
                # Liters
                liters_item = QTableWidgetItem(f"{data['liters']:,}")
                liters_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.fuel_table.setItem(row, 1, liters_item)
                
                # Cost
                cost_item = QTableWidgetItem(f"${data['cost']:,.0f}")
                cost_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                cost_item.setForeground(QColor("#c62828"))
                self.fuel_table.setItem(row, 2, cost_item)
                
                # Transactions
                txn_item = QTableWidgetItem(str(data['transactions']))
                txn_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.fuel_table.setItem(row, 3, txn_item)
                
        except Exception as e:
            print(f"Error updating fuel summary: {e}")
    
    def _create_add_investment_section(self, parent_layout):
        """Create the add investment form."""
        add_group = QGroupBox("➕ Add Investment")
        add_layout = QVBoxLayout(add_group)
        add_layout.setContentsMargins(6, 2, 6, 6)
        add_layout.setSpacing(4)
        
        # Row 1: Item and Category
        row1 = QHBoxLayout()
        row1.setSpacing(4)
        item_label = QLabel("Item:")
        item_label.setFixedWidth(35)
        row1.addWidget(item_label)
        self.item_combo = QComboBox()
        self.item_combo.setEditable(True)
        self._populate_items()
        row1.addWidget(self.item_combo, 1)
        
        cat_label = QLabel("Cat:")
        cat_label.setFixedWidth(25)
        row1.addWidget(cat_label)
        self.category_label = QLabel("-")
        self.category_label.setMinimumWidth(100)
        row1.addWidget(self.category_label)
        add_layout.addLayout(row1)
        
        # Connect item change to update category
        self.item_combo.currentIndexChanged.connect(self._on_item_changed)
        
        # Row 2: Cost, Date, and Buttons
        row2 = QHBoxLayout()
        row2.setSpacing(4)
        cost_label = QLabel("Cost:")
        cost_label.setFixedWidth(35)
        row2.addWidget(cost_label)
        self.cost_spin = QDoubleSpinBox()
        self.cost_spin.setRange(0, 10000000)
        self.cost_spin.setDecimals(0)
        self.cost_spin.setPrefix("$")
        self.cost_spin.setMinimumWidth(90)
        row2.addWidget(self.cost_spin)
        
        date_label = QLabel("Date:")
        date_label.setFixedWidth(35)
        row2.addWidget(date_label)
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self._set_investment_date_to_game_date()
        row2.addWidget(self.date_edit)
        
        self.utility_check = QPushButton("🎮")
        self.utility_check.setCheckable(True)
        self.utility_check.setFixedWidth(28)
        self.utility_check.setToolTip("Mark as utility item")
        row2.addWidget(self.utility_check)
        
        self.add_btn = QPushButton("➕ Add")
        self.add_btn.clicked.connect(self._add_investment)
        row2.addWidget(self.add_btn)
        
        add_layout.addLayout(row2)
        
        parent_layout.addWidget(add_group)
    
    def _set_investment_date_to_game_date(self):
        """Set the date edit to the current in-game date from Settings."""
        try:
            if self.main_window and hasattr(self.main_window, 'settings_tab'):
                settings = self.main_window.settings_tab
                if hasattr(settings, 'current_game_date'):
                    self.date_edit.setDate(settings.current_game_date.date())
                    return
        except Exception:
            pass
        # Fallback to game default date
        self.date_edit.setDate(QDate(2021, 4, 22))
    
    def _create_investment_table(self, parent_layout):
        """Create the investment tracking table."""
        table_group = QGroupBox("📋 Investment Tracking")
        table_layout = QVBoxLayout(table_group)
        table_layout.setContentsMargins(6, 2, 6, 6)
        table_layout.setSpacing(4)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        self.remove_btn = QPushButton("🗑️ Remove Selected")
        self.remove_btn.clicked.connect(self._remove_selected)
        toolbar.addWidget(self.remove_btn)
        
        toolbar.addStretch()
        
        self.total_label = QLabel("Total Invested: $0")
        self.total_label.setFont(QFont("", 10, QFont.Weight.Bold))
        toolbar.addWidget(self.total_label)
        
        table_layout.addLayout(toolbar)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "Item Name", "Category", "Cost", "Revenue", 
            "Profit", "ROI %", "Status", "$/Day", "Days", "Actions"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        self.table.setColumnWidth(0, 150)
        self.table.horizontalHeader().setSectionResizeMode(9, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(9, 100)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setDefaultSectionSize(22)
        table_layout.addWidget(self.table, 1)  # stretch to fill
        
        parent_layout.addWidget(table_group, 1)  # stretch to fill remaining space
    
    def _populate_items(self):
        """Populate items dropdown from reference data."""
        self.item_combo.clear()
        self.item_combo.addItem("-- Select or type item name --", None)
        
        # Get items from importer
        try:
            from importers.excel_importer import ExcelImporter
            importer = ExcelImporter(self.db)
            items = importer.get_all_items()
            
            # Filter to purchasable items
            purchasable = [item for item in items if item.can_purchase]
            purchasable.sort(key=lambda x: x.name)
            
            for item in purchasable:
                display = f"{item.name} (${item.buy_price or 0:,.0f})"
                self.item_combo.addItem(display, item)
        except Exception as e:
            print(f"Error loading items: {e}")
    
    def _on_item_changed(self, index):
        """Handle item selection change."""
        item_data = self.item_combo.itemData(index)
        if item_data:
            self.category_label.setText(item_data.category or "-")
            self.cost_spin.setValue(item_data.buy_price or 0)
        else:
            self.category_label.setText("-")
    
    def _add_investment(self):
        """Add a new investment."""
        # Get item name
        item_data = self.item_combo.itemData(self.item_combo.currentIndex())
        if item_data:
            item_name = item_data.name
            category = item_data.category or ""
        else:
            # Manual entry
            item_name = self.item_combo.currentText().strip()
            if not item_name or item_name == "-- Select or type item name --":
                QMessageBox.warning(self, "Error", "Please select or enter an item name.")
                return
            category = ""
        
        cost = self.cost_spin.value()
        if cost <= 0:
            QMessageBox.warning(self, "Error", "Please enter a valid cost.")
            return
        
        purchase_date = self.date_edit.date().toPyDate()
        is_utility = self.utility_check.isChecked()
        
        # Create investment record
        investment = {
            "id": len(self.investments) + 1,
            "name": item_name,
            "category": category,
            "cost": cost,
            "purchase_date": purchase_date,
            "is_utility": is_utility,
            "revenues": [],  # List of {amount, date, type, notes}
            "notes": "",
        }
        
        self.investments.append(investment)
        self._refresh_table()
        self._update_summary()
        self.data_changed.emit()
        
        # Reset form
        self.item_combo.setCurrentIndex(0)
        self.cost_spin.setValue(0)
        self.utility_check.setChecked(False)
    
    def _refresh_table(self):
        """Refresh the investment table."""
        self.table.setRowCount(len(self.investments))
        
        total_invested = 0
        
        for row, inv in enumerate(self.investments):
            # Calculate metrics
            cost = inv.get("cost", 0)
            total_revenue = sum(r.get("amount", 0) for r in inv.get("revenues", []))
            profit = total_revenue - cost
            roi_pct = (profit / cost * 100) if cost > 0 else 0
            
            # Days owned
            purchase_date = inv.get("purchase_date", date.today())
            if isinstance(purchase_date, str):
                purchase_date = datetime.strptime(purchase_date, "%Y-%m-%d").date()
            days_owned = (date.today() - purchase_date).days
            if days_owned < 1:
                days_owned = 1
            
            profit_per_day = profit / days_owned
            
            # Status
            is_utility = inv.get("is_utility", False)
            if total_revenue >= cost:
                status = "✓ PAID"
                status_color = QColor("#D5F5D5")
            elif is_utility:
                status = "⏳ UTILITY"
                status_color = QColor("#FFF2CC")
            elif total_revenue > 0:
                status = "⏳ PENDING"
                status_color = QColor("#FFF2CC")
            else:
                status = "✗ LOSS"
                status_color = QColor("#F8D6D6")
            
            total_invested += cost
            
            # Populate row
            self.table.setItem(row, 0, QTableWidgetItem(inv.get("name", "")))
            self.table.setItem(row, 1, QTableWidgetItem(inv.get("category", "")))
            
            cost_item = QTableWidgetItem(f"${cost:,.0f}")
            cost_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 2, cost_item)
            
            rev_item = QTableWidgetItem(f"${total_revenue:,.0f}")
            rev_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 3, rev_item)
            
            profit_item = QTableWidgetItem(f"${profit:+,.0f}")
            profit_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            if profit >= 0:
                profit_item.setForeground(QColor("#008800"))
            else:
                profit_item.setForeground(QColor("#CC0000"))
            self.table.setItem(row, 4, profit_item)
            
            roi_item = QTableWidgetItem(f"{roi_pct:+.1f}%")
            roi_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            if roi_pct >= 0:
                roi_item.setForeground(QColor("#008800"))
            else:
                roi_item.setForeground(QColor("#CC0000"))
            self.table.setItem(row, 5, roi_item)
            
            status_item = QTableWidgetItem(status)
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            status_item.setBackground(status_color)
            self.table.setItem(row, 6, status_item)
            
            daily_item = QTableWidgetItem(f"${profit_per_day:+,.0f}")
            daily_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            if profit_per_day >= 0:
                daily_item.setForeground(QColor("#008800"))
            else:
                daily_item.setForeground(QColor("#CC0000"))
            self.table.setItem(row, 7, daily_item)
            
            days_item = QTableWidgetItem(str(days_owned))
            days_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 8, days_item)
            
            # Actions cell with buttons
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(2, 2, 2, 2)
            actions_layout.setSpacing(2)
            
            add_rev_btn = QPushButton("+Rev")
            add_rev_btn.setMaximumWidth(45)
            add_rev_btn.clicked.connect(lambda checked, r=row: self._add_revenue_dialog(r))
            actions_layout.addWidget(add_rev_btn)
            
            edit_btn = QPushButton("Edit")
            edit_btn.setMaximumWidth(40)
            edit_btn.clicked.connect(lambda checked, r=row: self._edit_investment(r))
            actions_layout.addWidget(edit_btn)
            
            self.table.setCellWidget(row, 9, actions_widget)
        
        self.total_label.setText(f"Total Invested: ${total_invested:,.0f}")
    
    def _update_summary(self):
        """Update the summary dashboard cards."""
        if not self.investments:
            self.invested_value.setText("$0")
            self.invested_subtitle.setText("0 items tracked")
            self.revenue_value.setText("$0")
            self.profit_value.setText("$0")
            self.profit_subtitle.setText("0% overall ROI")
            self.success_value.setText("0%")
            self.success_subtitle.setText("0 of 0 profitable")
            self.best_value.setText("-")
            self.best_subtitle.setText("+0% ROI")
            self.daily_value.setText("$0/day")
            return
        
        # Calculate totals
        total_invested = 0
        total_revenue = 0
        profitable_count = 0
        best_roi = -999999
        best_roi_name = "-"
        total_daily = 0
        
        for inv in self.investments:
            cost = inv.get("cost", 0)
            revenue = sum(r.get("amount", 0) for r in inv.get("revenues", []))
            profit = revenue - cost
            roi = (profit / cost * 100) if cost > 0 else 0
            
            # Days owned
            purchase_date = inv.get("purchase_date", date.today())
            if isinstance(purchase_date, str):
                purchase_date = datetime.strptime(purchase_date, "%Y-%m-%d").date()
            days = max(1, (date.today() - purchase_date).days)
            daily = profit / days
            
            total_invested += cost
            total_revenue += revenue
            total_daily += daily
            
            if profit > 0:
                profitable_count += 1
            
            if roi > best_roi:
                best_roi = roi
                best_roi_name = inv.get("name", "Unknown")
        
        net_profit = total_revenue - total_invested
        overall_roi = (net_profit / total_invested * 100) if total_invested > 0 else 0
        success_rate = (profitable_count / len(self.investments) * 100) if self.investments else 0
        
        # Update cards
        self.invested_value.setText(f"${total_invested:,.0f}")
        self.invested_subtitle.setText(f"{len(self.investments)} items tracked")
        
        self.revenue_value.setText(f"${total_revenue:,.0f}")
        
        self.profit_value.setText(f"${net_profit:+,.0f}")
        if net_profit >= 0:
            self.profit_value.setStyleSheet("color: #008800;")
        else:
            self.profit_value.setStyleSheet("color: #CC0000;")
        self.profit_subtitle.setText(f"{overall_roi:+.1f}% overall ROI")
        
        self.success_value.setText(f"{success_rate:.0f}%")
        self.success_subtitle.setText(f"{profitable_count} of {len(self.investments)} profitable")
        
        self.best_value.setText(best_roi_name)
        self.best_subtitle.setText(f"{best_roi:+.1f}% ROI")
        
        self.daily_value.setText(f"${total_daily:+,.0f}/day")
    
    def _add_revenue_dialog(self, row):
        """Show dialog to add revenue to an investment."""
        if row < 0 or row >= len(self.investments):
            return
        
        inv = self.investments[row]
        game_date = self._get_current_game_date()
        dialog = AddRevenueDialog(self, inv.get("name", "Unknown"), default_date=game_date)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            revenue = dialog.get_revenue()
            if revenue:
                inv.setdefault("revenues", []).append(revenue)
                self._refresh_table()
                self._update_summary()
                self.data_changed.emit()
    
    def _get_current_game_date(self):
        """Get the current in-game date from Settings."""
        try:
            if self.main_window and hasattr(self.main_window, 'settings_tab'):
                settings = self.main_window.settings_tab
                if hasattr(settings, 'current_game_date'):
                    return settings.current_game_date.date()
        except Exception:
            pass
        return QDate(2021, 4, 22)
    
    def _edit_investment(self, row):
        """Edit an investment."""
        if row < 0 or row >= len(self.investments):
            return
        
        inv = self.investments[row]
        dialog = EditInvestmentDialog(self, inv)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated = dialog.get_investment()
            if updated:
                self.investments[row] = updated
                self._refresh_table()
                self._update_summary()
                self.data_changed.emit()
    
    def _remove_selected(self):
        """Remove selected investments."""
        selected_rows = set()
        for item in self.table.selectedItems():
            selected_rows.add(item.row())
        
        if not selected_rows:
            QMessageBox.information(self, "Info", "Please select investments to remove.")
            return
        
        reply = QMessageBox.question(
            self, "Confirm Remove",
            f"Remove {len(selected_rows)} selected investment(s)?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Remove in reverse order to maintain indices
            for row in sorted(selected_rows, reverse=True):
                if row < len(self.investments):
                    del self.investments[row]
            
            self._refresh_table()
            self._update_summary()
            self.data_changed.emit()
    
    def get_summary_data(self):
        """Get summary data for Dashboard integration."""
        if not self.investments:
            return {
                "total_invested": 0,
                "total_revenue": 0,
                "net_profit": 0,
                "overall_roi": 0,
                "success_rate": 0,
                "profitable_count": 0,
                "total_count": 0,
                "best_performer": None,
                "best_roi": 0,
                "daily_profit": 0,
            }
        
        total_invested = 0
        total_revenue = 0
        profitable_count = 0
        best_roi = -999999
        best_name = None
        total_daily = 0
        
        for inv in self.investments:
            cost = inv.get("cost", 0)
            revenue = sum(r.get("amount", 0) for r in inv.get("revenues", []))
            profit = revenue - cost
            roi = (profit / cost * 100) if cost > 0 else 0
            
            purchase_date = inv.get("purchase_date", date.today())
            if isinstance(purchase_date, str):
                purchase_date = datetime.strptime(purchase_date, "%Y-%m-%d").date()
            days = max(1, (date.today() - purchase_date).days)
            
            total_invested += cost
            total_revenue += revenue
            total_daily += profit / days
            
            if profit > 0:
                profitable_count += 1
            
            if roi > best_roi:
                best_roi = roi
                best_name = inv.get("name")
        
        net_profit = total_revenue - total_invested
        overall_roi = (net_profit / total_invested * 100) if total_invested > 0 else 0
        success_rate = (profitable_count / len(self.investments) * 100) if self.investments else 0
        
        return {
            "total_invested": total_invested,
            "total_revenue": total_revenue,
            "net_profit": net_profit,
            "overall_roi": overall_roi,
            "success_rate": success_rate,
            "profitable_count": profitable_count,
            "total_count": len(self.investments),
            "best_performer": best_name,
            "best_roi": best_roi,
            "daily_profit": total_daily,
        }


class AddRevenueDialog(QDialog):
    """Dialog to add revenue to an investment."""
    
    def __init__(self, parent, item_name, default_date=None):
        super().__init__(parent)
        self.setWindowTitle(f"Add Revenue - {item_name}")
        self.setMinimumWidth(400)
        self.default_date = default_date or QDate(2021, 4, 22)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Revenue Type
        type_group = QGroupBox("Revenue Type")
        type_layout = QHBoxLayout(type_group)
        
        self.type_group = QButtonGroup()
        self.auto_radio = QRadioButton("Auto (passive income)")
        self.manual_radio = QRadioButton("Manual (sales/usage)")
        self.manual_radio.setChecked(True)
        
        self.type_group.addButton(self.auto_radio, 0)
        self.type_group.addButton(self.manual_radio, 1)
        
        type_layout.addWidget(self.auto_radio)
        type_layout.addWidget(self.manual_radio)
        layout.addWidget(type_group)
        
        # Amount and Date
        form = QFormLayout()
        
        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setRange(0, 10000000)
        self.amount_spin.setDecimals(2)
        self.amount_spin.setPrefix("$")
        form.addRow("Amount:", self.amount_spin)
        
        self.date_edit = QDateEdit()
        self.date_edit.setDate(self.default_date)
        self.date_edit.setCalendarPopup(True)
        form.addRow("Date:", self.date_edit)
        
        self.notes_edit = QLineEdit()
        self.notes_edit.setPlaceholderText("Optional notes...")
        form.addRow("Notes:", self.notes_edit)
        
        layout.addLayout(form)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def get_revenue(self):
        """Get the revenue data."""
        amount = self.amount_spin.value()
        if amount <= 0:
            return None
        
        return {
            "amount": amount,
            "date": self.date_edit.date().toPyDate(),
            "type": "auto" if self.auto_radio.isChecked() else "manual",
            "notes": self.notes_edit.text().strip(),
        }


class EditInvestmentDialog(QDialog):
    """Dialog to edit an investment."""
    
    def __init__(self, parent, investment):
        super().__init__(parent)
        self.investment = investment.copy()
        self.investment["revenues"] = list(investment.get("revenues", []))
        
        self.setWindowTitle(f"Edit Investment - {investment.get('name', 'Unknown')}")
        self.setMinimumWidth(500)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Basic Info
        form = QFormLayout()
        
        self.name_edit = QLineEdit(self.investment.get("name", ""))
        form.addRow("Item Name:", self.name_edit)
        
        self.category_edit = QLineEdit(self.investment.get("category", ""))
        form.addRow("Category:", self.category_edit)
        
        self.cost_spin = QDoubleSpinBox()
        self.cost_spin.setRange(0, 10000000)
        self.cost_spin.setDecimals(2)
        self.cost_spin.setPrefix("$")
        self.cost_spin.setValue(self.investment.get("cost", 0))
        form.addRow("Initial Cost:", self.cost_spin)
        
        self.date_edit = QDateEdit()
        purchase_date = self.investment.get("purchase_date", date.today())
        if isinstance(purchase_date, str):
            purchase_date = datetime.strptime(purchase_date, "%Y-%m-%d").date()
        self.date_edit.setDate(QDate(purchase_date.year, purchase_date.month, purchase_date.day))
        self.date_edit.setCalendarPopup(True)
        form.addRow("Purchase Date:", self.date_edit)
        
        self.utility_check = QPushButton("🎮 Utility Item")
        self.utility_check.setCheckable(True)
        self.utility_check.setChecked(self.investment.get("is_utility", False))
        form.addRow("", self.utility_check)
        
        layout.addLayout(form)
        
        # Revenue History
        rev_group = QGroupBox(f"Revenue History ({len(self.investment.get('revenues', []))} entries)")
        rev_layout = QVBoxLayout(rev_group)
        
        total_rev = sum(r.get("amount", 0) for r in self.investment.get("revenues", []))
        rev_label = QLabel(f"Total Revenue: ${total_rev:,.2f}")
        rev_label.setFont(QFont("", 10, QFont.Weight.Bold))
        rev_layout.addWidget(rev_label)
        
        # Simple text display of revenues
        if self.investment.get("revenues"):
            rev_text = QTextEdit()
            rev_text.setReadOnly(True)
            rev_text.setMaximumHeight(100)
            lines = []
            for r in self.investment.get("revenues", []):
                rev_date = r.get("date", "")
                if isinstance(rev_date, date):
                    rev_date = rev_date.strftime("%Y-%m-%d")
                lines.append(f"${r.get('amount', 0):,.2f} - {r.get('type', 'manual')} - {rev_date}")
            rev_text.setPlainText("\n".join(lines))
            rev_layout.addWidget(rev_text)
        
        layout.addWidget(rev_group)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def get_investment(self):
        """Get the updated investment data."""
        name = self.name_edit.text().strip()
        if not name:
            return None
        
        self.investment["name"] = name
        self.investment["category"] = self.category_edit.text().strip()
        self.investment["cost"] = self.cost_spin.value()
        self.investment["purchase_date"] = self.date_edit.date().toPyDate()
        self.investment["is_utility"] = self.utility_check.isChecked()
        
        return self.investment


class MaintenanceDialog(QDialog):
    """Dialog to add a maintenance record."""
    
    MAINTENANCE_TYPES = [
        "Repair",
        "Parts Replacement", 
        "Scheduled Service",
        "Inspection",
        "Upgrade",
        "Other"
    ]
    
    def __init__(self, parent, default_date=None):
        super().__init__(parent)
        self.setWindowTitle("Add Maintenance Record")
        self.setMinimumWidth(400)
        self.default_date = default_date or QDate(2021, 4, 22)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        form = QFormLayout()
        
        # Date
        self.date_edit = QDateEdit()
        self.date_edit.setDate(self.default_date)
        self.date_edit.setCalendarPopup(True)
        form.addRow("Date:", self.date_edit)
        
        # Equipment (with autocomplete from vehicles)
        self.equipment_combo = QComboBox()
        self.equipment_combo.setEditable(True)
        self._populate_equipment()
        form.addRow("Equipment:", self.equipment_combo)
        
        # Maintenance Type
        self.type_combo = QComboBox()
        self.type_combo.addItems(self.MAINTENANCE_TYPES)
        form.addRow("Type:", self.type_combo)
        
        # Cost
        self.cost_spin = QDoubleSpinBox()
        self.cost_spin.setRange(0, 10000000)
        self.cost_spin.setDecimals(0)
        self.cost_spin.setPrefix("$")
        form.addRow("Cost:", self.cost_spin)
        
        # Notes
        self.notes_edit = QLineEdit()
        self.notes_edit.setPlaceholderText("Parts replaced, work done, etc.")
        form.addRow("Notes:", self.notes_edit)
        
        layout.addLayout(form)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def _populate_equipment(self):
        """Populate equipment dropdown with vehicles."""
        self.equipment_combo.addItem("-- Select Equipment --")
        
        try:
            from ui.tabs.vehicles_subtab import VEHICLE_DATA
            vehicles = sorted(set(v.get('name', '') for v in VEHICLE_DATA if v.get('name')))
            for v in vehicles:
                # Exclude attachments
                if not any(v.endswith(s) for s in ['B100', 'B120', 'B140']):
                    self.equipment_combo.addItem(v)
        except Exception:
            pass
    
    def get_record(self):
        """Get the maintenance record data."""
        equipment = self.equipment_combo.currentText()
        if equipment == "-- Select Equipment --":
            equipment = ""
        
        cost = self.cost_spin.value()
        if cost <= 0:
            return None
        
        return {
            "date": self.date_edit.date().toString("yyyy-MM-dd"),
            "equipment": equipment,
            "type": self.type_combo.currentText(),
            "cost": cost,
            "notes": self.notes_edit.text().strip()
        }

