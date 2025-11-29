"""
Budget Planner Tab - Plan equipment and facility purchases with power calculations

Features:
- Budget Overview: Aggregated totals, priority queue, funding progress
- Equipment Planner: Vehicles and equipment purchases with templates
- Facility Planner: Factory buildings with Power Calculator and Setup Groups
"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QLabel,
    QPushButton,
    QComboBox,
    QSpinBox,
    QDoubleSpinBox,
    QGroupBox,
    QSplitter,
    QFrame,
    QScrollArea,
    QCheckBox,
    QMessageBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QTextEdit,
    QProgressBar,
    QAbstractItemView,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont

from core.database import get_database
from ui.tabs.factory_subtab import FACTORY_EQUIPMENT_DATA
from ui.tabs.buildings_subtab import BUILDING_DATA


class BudgetPlannerTab(QWidget):
    """Budget Planner tab with sub-tabs for equipment and facility planning."""
    
    data_changed = pyqtSignal()
    
    # Priority levels
    PRIORITY_LEVELS = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    PRIORITY_COLORS = {
        "CRITICAL": QColor(255, 200, 200),  # Light red
        "HIGH": QColor(255, 230, 200),       # Light orange
        "MEDIUM": QColor(255, 255, 200),     # Light yellow
        "LOW": QColor(200, 255, 200),        # Light green
    }
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = get_database()
        self.main_window = None
        
        # Planned items storage
        self.equipment_items = []  # List of dicts
        self.power_setups = []     # List of power setup groups
        
        # Reference data caches
        self._generators = []
        self._pylons = []
        self._buildings = []
        self._conveyors = []
        
        self._load_reference_data()
        self._setup_ui()
        self._update_overview()
    
    def set_main_window(self, main_window):
        """Store reference to main window for accessing settings."""
        self.main_window = main_window
    
    def _load_reference_data(self):
        """Load and categorize factory equipment data."""
        # Categorize factory equipment
        self._power_inputs = []
        
        for item in FACTORY_EQUIPMENT_DATA:
            cat = item.get("category", "")
            subcat = item.get("subcategory", "")
            
            if cat == "Power":
                if subcat in ["Generator", "Coal Plant", "Solar", "Wind"]:
                    self._generators.append(item)
                elif "Pylon" in subcat:
                    self._pylons.append(item)
                elif subcat == "Power Input":
                    # Store power inputs separately
                    self._power_inputs.append({
                        "name": item.get("name", ""),
                        "category": "Power Input",
                        "price": item.get("price", 0),
                        "power_kw": item.get("power_consumption_kw", 0),
                    })
            elif cat == "Conveyor":
                # Only include conveyors that use power (skip pipelines which are 0 kW)
                power = item.get("power_consumption_kw", 0)
                if power > 0:
                    self._conveyors.append(item)
        
        # Load buildings (without power inputs - they go in Distribution now)
        self._buildings = list(BUILDING_DATA)
        
        # Sort generators by $/kW (best value first)
        def gen_cost_per_kw(g):
            power = g.get("power_generated_kw", 0)
            if power > 0:
                return g.get("price", 0) / power
            return float('inf')
        self._generators.sort(key=gen_cost_per_kw)
    
    def _setup_ui(self):
        """Set up the user interface with sub-tabs."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Create sub-tab widget
        self.sub_tabs = QTabWidget()
        self.sub_tabs.setTabPosition(QTabWidget.TabPosition.North)
        
        # Budget Overview Sub-Tab
        self.overview_tab = BudgetOverviewSubTab(self)
        self.sub_tabs.addTab(self.overview_tab, "📊 Budget Overview")
        
        # Equipment Planner Sub-Tab
        self.equipment_tab = EquipmentPlannerSubTab(self)
        self.equipment_tab.items_changed.connect(self._on_items_changed)
        self.sub_tabs.addTab(self.equipment_tab, "🛠️ Equipment Planner")
        
        # Facility Planner Sub-Tab
        self.facility_tab = FacilityPlannerSubTab(self)
        self.facility_tab.setups_changed.connect(self._on_items_changed)
        self.sub_tabs.addTab(self.facility_tab, "🏭 Facility Planner")
        
        layout.addWidget(self.sub_tabs)
    
    def _on_items_changed(self):
        """Handle changes to planned items."""
        self._update_overview()
        self.data_changed.emit()
    
    def _update_overview(self):
        """Update the overview tab with current totals."""
        # Calculate equipment totals
        equipment_total = sum(
            item.get("price", 0) * item.get("quantity", 1)
            for item in self.equipment_items
            if isinstance(item, dict) and item.get("include", True)
        )
        
        # Calculate facility totals
        facility_total = 0
        power_total = 0
        power_required = 0
        distribution_total = 0
        
        for setup in self.power_setups:
            # Skip non-dict entries
            if not isinstance(setup, dict):
                continue
            if not setup.get("include", True):
                continue
            # Buildings
            for bld in setup.get("buildings", []):
                if isinstance(bld, dict):
                    facility_total += bld.get("price", 0) * bld.get("quantity", 1)
                    power_required += bld.get("power_kw", 0) * bld.get("quantity", 1)
            # Power source
            power_total += setup.get("power_cost", 0)
            # Distribution (includes power inputs and conveyors)
            distribution_total += setup.get("distribution_cost", 0)
            # Add distribution power (from power inputs and conveyors)
            power_required += setup.get("distribution_power", 0)
        
        # Update overview tab
        self.overview_tab.update_totals(
            equipment_total=equipment_total,
            facility_total=facility_total,
            power_total=power_total,
            power_required=power_required,
            distribution_total=distribution_total,
            equipment_items=self.equipment_items,
            power_setups=self.power_setups,
        )
    
    def get_settings(self):
        """Get current settings from Settings tab and balances from Ledger tab."""
        settings_data = {
            "personal_balance": 0,
            "company_balance": 0,
            "personal_split": 10,
            "company_split": 90,
            "vn_level": 0,
            "if_level": 0,
        }
        
        # Get balances from Ledger tab
        if self.main_window and hasattr(self.main_window, 'ledger_tab'):
            ledger = self.main_window.ledger_tab
            balances = ledger.get_current_balances()
            settings_data["personal_balance"] = balances.get("personal", 0)
            settings_data["company_balance"] = balances.get("company", 0)
        
        # Get settings from Settings tab
        if self.main_window and hasattr(self.main_window, 'settings_tab'):
            settings = self.main_window.settings_tab
            # Get splits (stored as decimal, e.g., 0.10 = 10%)
            personal_split = settings.get_personal_split()
            company_split = settings.get_company_split()
            settings_data["personal_split"] = personal_split * 100  # Convert to percentage
            settings_data["company_split"] = company_split * 100
            
            # Get skill levels
            settings_data["vn_level"] = settings.settings.get("vendor_negotiation_level", 0)
            settings_data["if_level"] = settings.settings.get("investment_forecasting_level", 0)
        
        return settings_data


class BudgetOverviewSubTab(QWidget):
    """Budget Overview showing aggregated totals and priority queue."""
    
    def __init__(self, parent_tab):
        super().__init__()
        self.parent_tab = parent_tab
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the overview interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # === Budget Status Banner ===
        self.status_frame = QFrame()
        self.status_frame.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        self.status_frame.setLineWidth(2)
        status_layout = QHBoxLayout(self.status_frame)
        
        self.status_icon = QLabel("✅")
        self.status_icon.setFont(QFont("", 24))
        status_layout.addWidget(self.status_icon)
        
        self.status_label = QLabel("CAN AFFORD ALL PLANNED ITEMS")
        self.status_label.setFont(QFont("", 14, QFont.Weight.Bold))
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        
        layout.addWidget(self.status_frame)
        
        # === Summary Cards ===
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(15)  # Add spacing between cards
        
        # Equipment Card
        equip_group = QGroupBox("🛠️ Equipment")
        equip_layout = QFormLayout(equip_group)
        self.equip_total_label = QLabel("$0")
        self.equip_total_label.setFont(QFont("", 12, QFont.Weight.Bold))
        equip_layout.addRow("Total:", self.equip_total_label)
        self.equip_count_label = QLabel("0 items")
        equip_layout.addRow("Items:", self.equip_count_label)
        cards_layout.addWidget(equip_group, 1)  # stretch factor 1
        
        # Facility Card
        facility_group = QGroupBox("🏭 Facility")
        facility_layout = QFormLayout(facility_group)
        self.facility_total_label = QLabel("$0")
        self.facility_total_label.setFont(QFont("", 12, QFont.Weight.Bold))
        facility_layout.addRow("Buildings:", self.facility_total_label)
        self.power_total_label = QLabel("$0")
        facility_layout.addRow("Power:", self.power_total_label)
        self.distribution_label = QLabel("$0")
        facility_layout.addRow("Distribution:", self.distribution_label)
        cards_layout.addWidget(facility_group, 1)  # stretch factor 1
        
        # Power Summary Card
        power_group = QGroupBox("⚡ Power Summary")
        power_layout = QFormLayout(power_group)
        self.power_required_label = QLabel("0 kW")
        self.power_required_label.setFont(QFont("", 12, QFont.Weight.Bold))
        power_layout.addRow("Required:", self.power_required_label)
        self.power_capacity_label = QLabel("0 kW")
        power_layout.addRow("Capacity:", self.power_capacity_label)
        self.power_headroom_label = QLabel("0 kW (0%)")
        power_layout.addRow("Headroom:", self.power_headroom_label)
        cards_layout.addWidget(power_group, 1)  # stretch factor 1
        
        # Grand Total Card
        total_group = QGroupBox("💰 Grand Total")
        total_layout = QFormLayout(total_group)
        self.grand_total_label = QLabel("$0")
        self.grand_total_label.setFont(QFont("", 16, QFont.Weight.Bold))
        self.grand_total_label.setStyleSheet("color: #0066cc;")
        total_layout.addRow("", self.grand_total_label)
        
        # Available with refresh button
        available_row = QHBoxLayout()
        self.available_label = QLabel("$0")
        available_row.addWidget(self.available_label)
        self.refresh_balance_btn = QPushButton("🔄")
        self.refresh_balance_btn.setToolTip("Refresh balance from Ledger")
        self.refresh_balance_btn.setMaximumWidth(30)
        self.refresh_balance_btn.clicked.connect(lambda: self._refresh_balance())
        available_row.addWidget(self.refresh_balance_btn)
        available_row.addStretch()
        total_layout.addRow("Available:", available_row)
        
        self.shortfall_label = QLabel("$0")
        total_layout.addRow("Shortfall:", self.shortfall_label)
        cards_layout.addWidget(total_group, 1)  # stretch factor 1
        
        layout.addLayout(cards_layout)
        
        # === Funding Progress ===
        progress_group = QGroupBox("📈 Funding Progress")
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p% funded")
        progress_layout.addWidget(self.progress_bar)
        
        self.revenue_needed_label = QLabel("Revenue needed: $0 gross (at 10% split)")
        progress_layout.addWidget(self.revenue_needed_label)
        
        layout.addWidget(progress_group)
        
        # === Priority Queue ===
        queue_group = QGroupBox("🎯 Priority Queue")
        queue_layout = QVBoxLayout(queue_group)
        
        self.queue_table = QTableWidget()
        self.queue_table.setColumnCount(6)
        self.queue_table.setHorizontalHeaderLabels([
            "Priority", "Type", "Name", "Qty", "Cost", "Cumulative"
        ])
        self.queue_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.queue_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.queue_table.setAlternatingRowColors(True)
        queue_layout.addWidget(self.queue_table)
        
        layout.addWidget(queue_group)
    
    def update_totals(self, equipment_total, facility_total, power_total,
                      power_required, distribution_total, equipment_items, power_setups):
        """Update all overview displays."""
        # Get available funds
        settings = self.parent_tab.get_settings()
        available = settings["personal_balance"]
        personal_split = settings["personal_split"]
        
        # Calculate totals
        grand_total = equipment_total + facility_total + power_total + distribution_total
        shortfall = max(0, grand_total - available)
        
        # Calculate power capacity from setups
        power_capacity = 0
        for setup in power_setups:
            if not isinstance(setup, dict):
                continue
            if setup.get("include", True):
                power_capacity += setup.get("power_capacity", 0)
        
        # Update labels
        self.equip_total_label.setText(f"${equipment_total:,.0f}")
        included_count = sum(1 for i in equipment_items if isinstance(i, dict) and i.get("include", True))
        self.equip_count_label.setText(f"{included_count} items")
        
        self.facility_total_label.setText(f"${facility_total:,.0f}")
        self.power_total_label.setText(f"${power_total:,.0f}")
        self.distribution_label.setText(f"${distribution_total:,.0f}")
        
        self.power_required_label.setText(f"{power_required:,.0f} kW")
        self.power_capacity_label.setText(f"{power_capacity:,.0f} kW")
        headroom = power_capacity - power_required
        headroom_pct = (headroom / power_capacity * 100) if power_capacity > 0 else 0
        self.power_headroom_label.setText(f"{headroom:,.0f} kW ({headroom_pct:.0f}%)")
        
        self.grand_total_label.setText(f"${grand_total:,.0f}")
        self.available_label.setText(f"${available:,.0f}")
        
        # Shortfall styling
        if shortfall > 0:
            self.shortfall_label.setText(f"-${shortfall:,.0f}")
            self.shortfall_label.setStyleSheet("color: red; font-weight: bold;")
        else:
            surplus = available - grand_total
            self.shortfall_label.setText(f"+${surplus:,.0f}")
            self.shortfall_label.setStyleSheet("color: green; font-weight: bold;")
        
        # Update status banner
        if shortfall > 0:
            self.status_icon.setText("⚠️")
            self.status_label.setText("OVER BUDGET")
            self.status_frame.setStyleSheet("background-color: #ffcccc;")
        else:
            self.status_icon.setText("✅")
            self.status_label.setText("CAN AFFORD ALL PLANNED ITEMS")
            self.status_frame.setStyleSheet("background-color: #ccffcc;")
        
        # Update progress bar
        if grand_total > 0:
            progress = min(100, int(available / grand_total * 100))
            self.progress_bar.setValue(progress)
        else:
            self.progress_bar.setValue(100)
        
        # Revenue needed calculation
        if shortfall > 0 and personal_split > 0:
            revenue_needed = shortfall / (personal_split / 100)
            self.revenue_needed_label.setText(
                f"Revenue needed: ${revenue_needed:,.0f} gross (at {personal_split}% split)"
            )
        else:
            self.revenue_needed_label.setText("Fully funded!")
        
        # Update priority queue
        self._update_queue(equipment_items, power_setups)
    
    def _update_queue(self, equipment_items, power_setups):
        """Build and display the priority queue."""
        # Collect all items with priorities
        all_items = []
        
        for item in equipment_items:
            if not isinstance(item, dict):
                continue
            if item.get("include", True):
                all_items.append({
                    "priority": item.get("priority", "MEDIUM"),
                    "type": "Equipment",
                    "name": item.get("name", "Unknown"),
                    "quantity": item.get("quantity", 1),
                    "cost": item.get("price", 0) * item.get("quantity", 1),
                })
        
        for setup in power_setups:
            if not isinstance(setup, dict):
                continue
            if setup.get("include", True):
                setup_cost = setup.get("total_cost", 0)
                all_items.append({
                    "priority": setup.get("priority", "MEDIUM"),
                    "type": "Facility Setup",
                    "name": setup.get("name", "Unnamed Setup"),
                    "quantity": 1,
                    "cost": setup_cost,
                })
        
        # Sort by priority
        priority_order = {p: i for i, p in enumerate(self.parent_tab.PRIORITY_LEVELS)}
        all_items.sort(key=lambda x: priority_order.get(x["priority"], 99))
        
        # Populate table
        self.queue_table.setRowCount(len(all_items))
        cumulative = 0
        
        for row, item in enumerate(all_items):
            cumulative += item["cost"]
            
            priority_item = QTableWidgetItem(item["priority"])
            priority_color = self.parent_tab.PRIORITY_COLORS.get(item["priority"])
            if priority_color:
                priority_item.setBackground(priority_color)
            self.queue_table.setItem(row, 0, priority_item)
            
            self.queue_table.setItem(row, 1, QTableWidgetItem(item["type"]))
            self.queue_table.setItem(row, 2, QTableWidgetItem(item["name"]))
            self.queue_table.setItem(row, 3, QTableWidgetItem(str(item["quantity"])))
            
            cost_item = QTableWidgetItem(f"${item['cost']:,.0f}")
            cost_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.queue_table.setItem(row, 4, cost_item)
            
            cum_item = QTableWidgetItem(f"${cumulative:,.0f}")
            cum_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.queue_table.setItem(row, 5, cum_item)
    
    def _refresh_balance(self):
        """Refresh the available balance from the Ledger."""
        # Get fresh balance from Ledger
        settings = self.parent_tab.get_settings()
        available = settings["personal_balance"]
        
        # Update the label
        self.available_label.setText(f"${available:,.0f}")
        
        # Recalculate shortfall with current grand total
        grand_total_text = self.grand_total_label.text().replace("$", "").replace(",", "")
        try:
            grand_total = float(grand_total_text)
        except ValueError:
            grand_total = 0
        
        shortfall = max(0, grand_total - available)
        
        # Update shortfall styling
        if shortfall > 0:
            self.shortfall_label.setText(f"-${shortfall:,.0f}")
            self.shortfall_label.setStyleSheet("color: red; font-weight: bold;")
            self.status_icon.setText("⚠️")
            self.status_label.setText("OVER BUDGET")
            self.status_frame.setStyleSheet("background-color: #ffcccc;")
        else:
            surplus = available - grand_total
            self.shortfall_label.setText(f"+${surplus:,.0f}")
            self.shortfall_label.setStyleSheet("color: green; font-weight: bold;")
            self.status_icon.setText("✅")
            self.status_label.setText("CAN AFFORD ALL PLANNED ITEMS")
            self.status_frame.setStyleSheet("background-color: #ccffcc;")
        
        # Update progress bar
        if grand_total > 0:
            progress = min(100, int(available / grand_total * 100))
            self.progress_bar.setValue(progress)
        else:
            self.progress_bar.setValue(100)
        
        # Update revenue needed
        personal_split = settings["personal_split"]
        if shortfall > 0 and personal_split > 0:
            revenue_needed = shortfall / (personal_split / 100)
            self.revenue_needed_label.setText(
                f"Revenue needed: ${revenue_needed:,.0f} gross (at {personal_split}% split)"
            )
        else:
            self.revenue_needed_label.setText("Fully funded!")


class EquipmentPlannerSubTab(QWidget):
    """Equipment Planner for vehicles and equipment."""
    
    items_changed = pyqtSignal()
    
    def __init__(self, parent_tab):
        super().__init__()
        self.parent_tab = parent_tab
        self._items_cache = []  # Cache of purchasable items
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the equipment planner interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # === Quick Add Section ===
        add_group = QGroupBox("➕ Add Equipment")
        add_main_layout = QVBoxLayout(add_group)
        
        # Row 1: Search and Category Filter
        filter_row = QHBoxLayout()
        
        filter_row.addWidget(QLabel("Search:"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Type to search items...")
        self.search_edit.setClearButtonEnabled(True)
        self.search_edit.textChanged.connect(self._filter_items)
        self.search_edit.setMinimumWidth(200)
        filter_row.addWidget(self.search_edit)
        
        filter_row.addWidget(QLabel("Category:"))
        self.category_combo = QComboBox()
        self.category_combo.setMinimumWidth(180)
        self.category_combo.currentTextChanged.connect(self._filter_items)
        filter_row.addWidget(self.category_combo)
        
        filter_row.addStretch()
        add_main_layout.addLayout(filter_row)
        
        # Row 2: Item Selection
        item_row = QHBoxLayout()
        
        item_row.addWidget(QLabel("Item:"))
        self.item_combo = QComboBox()
        self.item_combo.setMinimumWidth(350)
        item_row.addWidget(self.item_combo)
        
        item_row.addWidget(QLabel("Qty:"))
        self.qty_spin = QSpinBox()
        self.qty_spin.setRange(1, 100)
        self.qty_spin.setValue(1)
        item_row.addWidget(self.qty_spin)
        
        item_row.addWidget(QLabel("Priority:"))
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(self.parent_tab.PRIORITY_LEVELS)
        self.priority_combo.setCurrentText("MEDIUM")
        item_row.addWidget(self.priority_combo)
        
        self.add_btn = QPushButton("Add")
        self.add_btn.clicked.connect(self._add_item)
        item_row.addWidget(self.add_btn)
        
        item_row.addStretch()
        add_main_layout.addLayout(item_row)
        
        layout.addWidget(add_group)
        
        # Populate items after UI is set up
        self._populate_items()
        
        # === Equipment Table ===
        table_group = QGroupBox("📋 Planned Equipment")
        table_layout = QVBoxLayout(table_group)
        
        # Table toolbar
        toolbar = QHBoxLayout()
        self.remove_btn = QPushButton("🗑️ Remove Selected")
        self.remove_btn.clicked.connect(self._remove_selected)
        toolbar.addWidget(self.remove_btn)
        
        self.clear_btn = QPushButton("🧹 Clear All")
        self.clear_btn.clicked.connect(self._clear_all)
        toolbar.addWidget(self.clear_btn)
        
        toolbar.addStretch()
        
        self.total_label = QLabel("Total: $0")
        self.total_label.setFont(QFont("", 12, QFont.Weight.Bold))
        toolbar.addWidget(self.total_label)
        
        table_layout.addLayout(toolbar)
        
        # Main table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Include", "Priority", "Name", "Unit Price", "Qty", "Total", "Notes"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(0, 60)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        table_layout.addWidget(self.table)
        
        layout.addWidget(table_group)
    
    def _populate_items(self):
        """Populate items dropdown from importer."""
        self.item_combo.clear()
        self._items_cache = []
        self._categories = set()
        
        # Get items from importer
        from importers.excel_importer import ExcelImporter
        importer = ExcelImporter(self.parent_tab.db)
        items = importer.get_all_items()
        
        # Filter to items that can be purchased and sort by name
        purchasable = [item for item in items if item.can_purchase]
        purchasable.sort(key=lambda x: x.name)
        
        self._items_cache = purchasable
        
        # Collect categories
        for item in purchasable:
            if item.category:
                self._categories.add(item.category)
        
        # Populate category dropdown
        self.category_combo.clear()
        self.category_combo.addItem("All Categories")
        for cat in sorted(self._categories):
            self.category_combo.addItem(cat)
        
        # Populate item dropdown
        self._update_item_combo(purchasable)
    
    def _update_item_combo(self, items):
        """Update the item combo with the given items."""
        self.item_combo.clear()
        for item in items:
            name = item.name
            price = item.buy_price or 0
            category = item.category or ""
            self.item_combo.addItem(f"{name} (${price:,.0f}) [{category}]", item)
    
    def _filter_items(self):
        """Filter items based on search text and category."""
        search_text = self.search_edit.text().lower().strip()
        selected_category = self.category_combo.currentText()
        
        filtered = []
        for item in self._items_cache:
            # Category filter
            if selected_category != "All Categories":
                if item.category != selected_category:
                    continue
            
            # Search filter
            if search_text:
                name_match = search_text in item.name.lower()
                cat_match = search_text in (item.category or "").lower()
                if not (name_match or cat_match):
                    continue
            
            filtered.append(item)
        
        self._update_item_combo(filtered)
    
    def _add_item(self):
        """Add item to the planned list."""
        idx = self.item_combo.currentIndex()
        if idx < 0:
            return
        
        item_data = self.item_combo.itemData(idx)
        if not item_data:
            return
        
        # Create planned item from Item object
        planned = {
            "name": item_data.name,
            "price": item_data.buy_price or 0,
            "quantity": self.qty_spin.value(),
            "priority": self.priority_combo.currentText(),
            "include": True,
            "notes": "",
            "category": item_data.category or "",
        }
        
        self.parent_tab.equipment_items.append(planned)
        self._refresh_table()
        self.items_changed.emit()
    
    def _refresh_table(self):
        """Refresh the equipment table."""
        items = self.parent_tab.equipment_items
        self.table.setRowCount(len(items))
        
        total = 0
        
        for row, item in enumerate(items):
            # Skip non-dict entries
            if not isinstance(item, dict):
                continue
                
            # Include checkbox
            include_check = QCheckBox()
            include_check.setChecked(item.get("include", True))
            include_check.stateChanged.connect(lambda state, r=row: self._toggle_include(r, state))
            cell_widget = QWidget()
            cell_layout = QHBoxLayout(cell_widget)
            cell_layout.addWidget(include_check)
            cell_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cell_layout.setContentsMargins(0, 0, 0, 0)
            self.table.setCellWidget(row, 0, cell_widget)
            
            # Priority
            priority_item = QTableWidgetItem(item.get("priority", "MEDIUM"))
            priority_color = self.parent_tab.PRIORITY_COLORS.get(item.get("priority"))
            if priority_color:
                priority_item.setBackground(priority_color)
            self.table.setItem(row, 1, priority_item)
            
            # Name
            self.table.setItem(row, 2, QTableWidgetItem(item.get("name", "")))
            
            # Unit Price
            price = item.get("price", 0)
            price_item = QTableWidgetItem(f"${price:,.0f}")
            price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 3, price_item)
            
            # Quantity
            qty = item.get("quantity", 1)
            self.table.setItem(row, 4, QTableWidgetItem(str(qty)))
            
            # Total
            item_total = price * qty
            total_item = QTableWidgetItem(f"${item_total:,.0f}")
            total_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 5, total_item)
            
            if item.get("include", True):
                total += item_total
            
            # Notes
            self.table.setItem(row, 6, QTableWidgetItem(item.get("notes", "")))
        
        self.total_label.setText(f"Total: ${total:,.0f}")
    
    def _toggle_include(self, row, state):
        """Toggle item inclusion."""
        if row < len(self.parent_tab.equipment_items):
            self.parent_tab.equipment_items[row]["include"] = (state == Qt.CheckState.Checked.value)
            self._refresh_table()
            self.items_changed.emit()
    
    def _remove_selected(self):
        """Remove selected items."""
        rows = set(item.row() for item in self.table.selectedItems())
        for row in sorted(rows, reverse=True):
            if row < len(self.parent_tab.equipment_items):
                del self.parent_tab.equipment_items[row]
        self._refresh_table()
        self.items_changed.emit()
    
    def _clear_all(self):
        """Clear all planned equipment."""
        if self.parent_tab.equipment_items:
            reply = QMessageBox.question(
                self, "Clear All",
                "Are you sure you want to clear all planned equipment?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.parent_tab.equipment_items.clear()
                self._refresh_table()
                self.items_changed.emit()


class FacilityPlannerSubTab(QWidget):
    """Facility Planner with Power Setup Groups."""
    
    setups_changed = pyqtSignal()
    
    def __init__(self, parent_tab):
        super().__init__()
        self.parent_tab = parent_tab
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the facility planner interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # === Power Setups Header ===
        header = QHBoxLayout()
        header.addWidget(QLabel("⚡ Power Setup Groups"))
        header.addStretch()
        
        self.add_setup_btn = QPushButton("➕ Add Power Setup")
        self.add_setup_btn.clicked.connect(lambda checked: self._add_setup())
        header.addWidget(self.add_setup_btn)
        
        layout.addLayout(header)
        
        # === Setups Scroll Area ===
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.setups_container = QWidget()
        self.setups_layout = QVBoxLayout(self.setups_container)
        self.setups_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setups_layout.setSpacing(10)
        
        scroll.setWidget(self.setups_container)
        layout.addWidget(scroll)
        
        # === Summary Bar ===
        summary_frame = QFrame()
        summary_frame.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Sunken)
        summary_layout = QHBoxLayout(summary_frame)
        
        self.total_buildings_label = QLabel("Buildings: $0")
        summary_layout.addWidget(self.total_buildings_label)
        
        self.total_power_equip_label = QLabel("Power Equipment: $0")
        summary_layout.addWidget(self.total_power_equip_label)
        
        self.total_distribution_label = QLabel("Distribution: $0")
        summary_layout.addWidget(self.total_distribution_label)
        
        summary_layout.addStretch()
        
        self.power_summary_label = QLabel("⚡ 0 kW required / 0 kW capacity")
        self.power_summary_label.setFont(QFont("", 10, QFont.Weight.Bold))
        summary_layout.addWidget(self.power_summary_label)
        
        self.grand_total_label = QLabel("Total: $0")
        self.grand_total_label.setFont(QFont("", 12, QFont.Weight.Bold))
        self.grand_total_label.setStyleSheet("color: #0066cc;")
        summary_layout.addWidget(self.grand_total_label)
        
        layout.addWidget(summary_frame)
    
    def _add_setup(self, setup_data=None):
        """Add a new power setup group."""
        # Create default setup
        if setup_data is None:
            setup_num = len(self.parent_tab.power_setups) + 1
            setup_data = {
                "name": f"Power Setup {setup_num}",
                "priority": "MEDIUM",
                "include": True,
                "buildings": [],
                "power_source": None,
                "power_cost": 0,
                "power_capacity": 0,
                "distribution_cost": 0,
                "total_cost": 0,
            }
        
        self.parent_tab.power_setups.append(setup_data)
        
        # Create widget
        widget = PowerSetupWidget(self, setup_data, len(self.parent_tab.power_setups) - 1)
        widget.changed.connect(self._on_setup_changed)
        widget.delete_requested.connect(self._delete_setup)
        self.setups_layout.addWidget(widget)
        
        self._update_summary()
        self.setups_changed.emit()
    
    def _on_setup_changed(self):
        """Handle setup changes."""
        self._update_summary()
        self.setups_changed.emit()
    
    def _delete_setup(self, index):
        """Delete a power setup."""
        if 0 <= index < len(self.parent_tab.power_setups):
            del self.parent_tab.power_setups[index]
            
            # Remove widget
            item = self.setups_layout.itemAt(index)
            if item:
                widget = item.widget()
                if widget:
                    widget.deleteLater()
            
            # Reindex remaining widgets
            for i in range(self.setups_layout.count()):
                item = self.setups_layout.itemAt(i)
                if item and item.widget():
                    item.widget().index = i
            
            self._update_summary()
            self.setups_changed.emit()
    
    def _update_summary(self):
        """Update the summary bar."""
        total_buildings = 0
        total_power_equip = 0
        total_distribution = 0
        total_required = 0
        total_capacity = 0
        
        for setup in self.parent_tab.power_setups:
            # Skip non-dict entries
            if not isinstance(setup, dict):
                continue
            if not setup.get("include", True):
                continue
            
            # Buildings cost and power
            for bld in setup.get("buildings", []):
                if isinstance(bld, dict):
                    total_buildings += bld.get("price", 0) * bld.get("quantity", 1)
                    total_required += bld.get("power_kw", 0) * bld.get("quantity", 1)
            
            total_power_equip += setup.get("power_cost", 0)
            total_capacity += setup.get("power_capacity", 0)
            total_distribution += setup.get("distribution_cost", 0)
            # Add distribution power (from power inputs and conveyors)
            total_required += setup.get("distribution_power", 0)
        
        grand_total = total_buildings + total_power_equip + total_distribution
        
        self.total_buildings_label.setText(f"Buildings: ${total_buildings:,.0f}")
        self.total_power_equip_label.setText(f"Power Equipment: ${total_power_equip:,.0f}")
        self.total_distribution_label.setText(f"Distribution: ${total_distribution:,.0f}")
        self.power_summary_label.setText(
            f"⚡ {total_required:,.0f} kW required / {total_capacity:,.0f} kW capacity"
        )
        self.grand_total_label.setText(f"Total: ${grand_total:,.0f}")


class PowerSetupWidget(QFrame):
    """Widget representing a single power setup group."""
    
    changed = pyqtSignal()
    delete_requested = pyqtSignal(int)
    
    def __init__(self, parent_subtab, setup_data, index):
        super().__init__()
        self.parent_subtab = parent_subtab
        # Ensure setup_data is a dict
        if not isinstance(setup_data, dict):
            setup_data = {
                "name": f"Power Setup {index + 1}",
                "priority": "MEDIUM",
                "include": True,
                "buildings": [],
                "power_source": None,
                "power_cost": 0,
                "power_capacity": 0,
                "distribution_cost": 0,
                "total_cost": 0,
            }
        self.setup_data = setup_data
        self.index = index
        
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        self._setup_ui()
        self._refresh()
    
    def _setup_ui(self):
        """Set up the widget interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        
        # === Header ===
        header = QHBoxLayout()
        
        self.include_check = QCheckBox()
        self.include_check.setChecked(self.setup_data.get("include", True))
        self.include_check.stateChanged.connect(self._on_include_changed)
        header.addWidget(self.include_check)
        
        self.name_edit = QLineEdit(self.setup_data.get("name", ""))
        self.name_edit.setPlaceholderText("Setup Name")
        self.name_edit.textChanged.connect(self._on_name_changed)
        self.name_edit.setMaximumWidth(200)
        header.addWidget(self.name_edit)
        
        header.addWidget(QLabel("Priority:"))
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(self.parent_subtab.parent_tab.PRIORITY_LEVELS)
        self.priority_combo.setCurrentText(self.setup_data.get("priority", "MEDIUM"))
        self.priority_combo.currentTextChanged.connect(self._on_priority_changed)
        header.addWidget(self.priority_combo)
        
        header.addStretch()
        
        self.power_label = QLabel("⚡ 0 kW")
        self.power_label.setFont(QFont("", 10, QFont.Weight.Bold))
        header.addWidget(self.power_label)
        
        self.cost_label = QLabel("$0")
        self.cost_label.setFont(QFont("", 10, QFont.Weight.Bold))
        self.cost_label.setStyleSheet("color: #0066cc;")
        header.addWidget(self.cost_label)
        
        self.delete_btn = QPushButton("🗑️")
        self.delete_btn.setMaximumWidth(30)
        self.delete_btn.clicked.connect(lambda: self.delete_requested.emit(self.index))
        header.addWidget(self.delete_btn)
        
        layout.addLayout(header)
        
        # === Buildings Section ===
        buildings_header = QHBoxLayout()
        buildings_header.addWidget(QLabel("🏭 Buildings:"))
        
        self.add_building_btn = QPushButton("+ Add")
        self.add_building_btn.setMaximumWidth(60)
        self.add_building_btn.clicked.connect(self._add_building)
        buildings_header.addWidget(self.add_building_btn)
        buildings_header.addStretch()
        
        layout.addLayout(buildings_header)
        
        # Buildings table
        self.buildings_table = QTableWidget()
        self.buildings_table.setColumnCount(5)
        self.buildings_table.setHorizontalHeaderLabels(["Name", "Power", "Price", "Qty", ""])
        self.buildings_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.buildings_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.buildings_table.setColumnWidth(4, 30)
        self.buildings_table.setMaximumHeight(120)
        layout.addWidget(self.buildings_table)
        
        # === Power Source Section ===
        power_group = QGroupBox("⚡ Power Source")
        power_layout = QHBoxLayout(power_group)
        
        power_layout.addWidget(QLabel("Generator:"))
        self.generator_combo = QComboBox()
        self._populate_generators()
        self.generator_combo.currentIndexChanged.connect(self._on_generator_changed)
        power_layout.addWidget(self.generator_combo)
        
        power_layout.addWidget(QLabel("Qty:"))
        self.generator_qty = QSpinBox()
        self.generator_qty.setRange(0, 20)
        self.generator_qty.setValue(1)
        self.generator_qty.valueChanged.connect(self._on_generator_qty_changed)
        power_layout.addWidget(self.generator_qty)
        
        self.generator_info = QLabel("")
        power_layout.addWidget(self.generator_info)
        power_layout.addStretch()
        
        layout.addWidget(power_group)
        
        # === Distribution Section ===
        dist_group = QGroupBox("🔌 Power Distribution")
        dist_main_layout = QVBoxLayout(dist_group)
        
        # Row 1: Power Input (Speed Booster)
        power_input_row = QHBoxLayout()
        power_input_row.addWidget(QLabel("Speed Booster:"))
        self.power_input_combo = QComboBox()
        self._populate_power_inputs()
        self.power_input_combo.currentIndexChanged.connect(self._on_distribution_changed)
        self.power_input_combo.setMinimumWidth(280)
        power_input_row.addWidget(self.power_input_combo)
        
        power_input_row.addWidget(QLabel("Qty:"))
        self.power_input_qty = QSpinBox()
        self.power_input_qty.setRange(0, 20)
        self.power_input_qty.setValue(0)
        self.power_input_qty.valueChanged.connect(self._on_distribution_changed)
        power_input_row.addWidget(self.power_input_qty)
        
        self.power_input_info = QLabel("")
        power_input_row.addWidget(self.power_input_info)
        power_input_row.addStretch()
        dist_main_layout.addLayout(power_input_row)
        
        # Row 2: Conveyors
        conveyor_row = QHBoxLayout()
        conveyor_row.addWidget(QLabel("Conveyors:"))
        self.conveyor_combo = QComboBox()
        self._populate_conveyors()
        self.conveyor_combo.currentIndexChanged.connect(self._on_distribution_changed)
        self.conveyor_combo.setMinimumWidth(280)
        conveyor_row.addWidget(self.conveyor_combo)
        
        conveyor_row.addWidget(QLabel("Qty:"))
        self.conveyor_qty = QSpinBox()
        self.conveyor_qty.setRange(0, 100)
        self.conveyor_qty.setValue(0)
        self.conveyor_qty.valueChanged.connect(self._on_distribution_changed)
        conveyor_row.addWidget(self.conveyor_qty)
        
        self.conveyor_info = QLabel("")
        conveyor_row.addWidget(self.conveyor_info)
        conveyor_row.addStretch()
        dist_main_layout.addLayout(conveyor_row)
        
        # Row 3: Pylons and Cables
        pylon_row = QHBoxLayout()
        pylon_row.addWidget(QLabel("Pylons:"))
        self.pylon_combo = QComboBox()
        self._populate_pylons()
        self.pylon_combo.currentIndexChanged.connect(self._on_distribution_changed)
        self.pylon_combo.setMinimumWidth(200)
        pylon_row.addWidget(self.pylon_combo)
        
        pylon_row.addWidget(QLabel("Qty:"))
        self.pylon_qty = QSpinBox()
        self.pylon_qty.setRange(0, 50)
        self.pylon_qty.setValue(0)
        self.pylon_qty.valueChanged.connect(self._on_distribution_changed)
        pylon_row.addWidget(self.pylon_qty)
        
        pylon_row.addWidget(QLabel("Cables:"))
        self.cable_qty = QSpinBox()
        self.cable_qty.setRange(0, 200)
        self.cable_qty.setValue(0)
        self.cable_qty.valueChanged.connect(self._on_distribution_changed)
        pylon_row.addWidget(self.cable_qty)
        
        self.dist_cost_label = QLabel("$0")
        pylon_row.addWidget(self.dist_cost_label)
        pylon_row.addStretch()
        dist_main_layout.addLayout(pylon_row)
        
        layout.addWidget(dist_group)
    
    def _populate_generators(self):
        """Populate generator dropdown."""
        self.generator_combo.clear()
        self.generator_combo.addItem("None", None)
        
        for gen in self.parent_subtab.parent_tab._generators:
            power = gen.get("power_generated_kw", 0)
            price = gen.get("price", 0)
            name = gen.get("name", "Unknown")
            cost_per_kw = price / power if power > 0 else 0
            self.generator_combo.addItem(
                f"{name} ({power:,} kW) - ${price:,} (${cost_per_kw:.2f}/kW)",
                gen
            )
    
    def _populate_power_inputs(self):
        """Populate power input (speed booster) dropdown."""
        self.power_input_combo.clear()
        self.power_input_combo.addItem("None", None)
        
        for pi in self.parent_subtab.parent_tab._power_inputs:
            power = pi.get("power_kw", 0)
            price = pi.get("price", 0)
            name = pi.get("name", "Unknown")
            self.power_input_combo.addItem(f"{name} ({power} kW) - ${price:,}", pi)
    
    def _populate_conveyors(self):
        """Populate conveyor dropdown."""
        self.conveyor_combo.clear()
        self.conveyor_combo.addItem("None", None)
        
        for conv in self.parent_subtab.parent_tab._conveyors:
            power = conv.get("power_consumption_kw", 0)
            price = conv.get("price", 0)
            name = conv.get("name", "Unknown")
            self.conveyor_combo.addItem(f"{name} ({power} kW) - ${price:,}", conv)
    
    def _populate_pylons(self):
        """Populate pylon dropdown."""
        self.pylon_combo.clear()
        self.pylon_combo.addItem("None", None)
        
        for pylon in self.parent_subtab.parent_tab._pylons:
            capacity = pylon.get("max_capacity_kw", 0)
            price = pylon.get("price", 0)
            name = pylon.get("name", "Unknown")
            self.pylon_combo.addItem(f"{name} ({capacity:,} kW) - ${price:,}", pylon)
    
    def _add_building(self):
        """Add a building to this setup."""
        dialog = AddBuildingDialog(self, self.parent_subtab.parent_tab._buildings)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            building = dialog.get_building()
            if building:
                self.setup_data["buildings"].append(building)
                self._refresh()
                self.changed.emit()
    
    def _refresh(self):
        """Refresh the widget display."""
        # Refresh buildings table
        buildings = self.setup_data.get("buildings", [])
        self.buildings_table.setRowCount(len(buildings))
        
        total_power = 0
        total_cost = 0
        
        for row, bld in enumerate(buildings):
            self.buildings_table.setItem(row, 0, QTableWidgetItem(bld.get("name", "")))
            
            power = bld.get("power_kw", 0)
            qty = bld.get("quantity", 1)
            total_power += power * qty
            self.buildings_table.setItem(row, 1, QTableWidgetItem(f"{power * qty} kW"))
            
            price = bld.get("price", 0)
            total_cost += price * qty
            self.buildings_table.setItem(row, 2, QTableWidgetItem(f"${price * qty:,}"))
            
            self.buildings_table.setItem(row, 3, QTableWidgetItem(str(qty)))
            
            # Delete button
            del_btn = QPushButton("×")
            del_btn.setMaximumWidth(25)
            del_btn.clicked.connect(lambda checked, r=row: self._remove_building(r))
            self.buildings_table.setCellWidget(row, 4, del_btn)
        
        # Update power cost
        gen_data = self.generator_combo.currentData()
        gen_qty = self.generator_qty.value()
        if gen_data and gen_qty > 0:
            power_cost = gen_data.get("price", 0) * gen_qty
            power_capacity = gen_data.get("power_generated_kw", 0) * gen_qty
            self.setup_data["power_cost"] = power_cost
            self.setup_data["power_capacity"] = power_capacity
            self.generator_info.setText(f"= {power_capacity:,} kW, ${power_cost:,}")
        else:
            self.setup_data["power_cost"] = 0
            self.setup_data["power_capacity"] = 0
            self.generator_info.setText("")
        
        # Update distribution cost and power
        dist_cost = 0
        dist_power = 0
        
        # Power Input (Speed Booster)
        pi_data = self.power_input_combo.currentData()
        pi_qty = self.power_input_qty.value()
        if pi_data and pi_qty > 0:
            pi_cost = pi_data.get("price", 0) * pi_qty
            pi_power = pi_data.get("power_kw", 0) * pi_qty
            dist_cost += pi_cost
            dist_power += pi_power
            self.power_input_info.setText(f"= {pi_power:,} kW, ${pi_cost:,}")
        else:
            self.power_input_info.setText("")
        
        # Conveyors
        conv_data = self.conveyor_combo.currentData()
        conv_qty = self.conveyor_qty.value()
        if conv_data and conv_qty > 0:
            conv_cost = conv_data.get("price", 0) * conv_qty
            conv_power = conv_data.get("power_consumption_kw", 0) * conv_qty
            dist_cost += conv_cost
            dist_power += conv_power
            self.conveyor_info.setText(f"= {conv_power:,} kW, ${conv_cost:,}")
        else:
            self.conveyor_info.setText("")
        
        # Pylons
        pylon_data = self.pylon_combo.currentData()
        pylon_qty = self.pylon_qty.value()
        if pylon_data and pylon_qty > 0:
            dist_cost += pylon_data.get("price", 0) * pylon_qty
        
        # Cables
        cable_qty = self.cable_qty.value()
        dist_cost += cable_qty * 10  # $10 per cable
        
        self.setup_data["distribution_cost"] = dist_cost
        self.setup_data["distribution_power"] = dist_power
        self.dist_cost_label.setText(f"${dist_cost:,}")
        
        # Add distribution power to total power required
        total_power += dist_power
        
        # Update totals
        total_with_power = total_cost + self.setup_data["power_cost"] + dist_cost
        self.setup_data["total_cost"] = total_with_power
        
        self.power_label.setText(f"⚡ {total_power:,} kW")
        self.cost_label.setText(f"${total_with_power:,}")
    
    def _remove_building(self, row):
        """Remove a building from this setup."""
        if row < len(self.setup_data["buildings"]):
            del self.setup_data["buildings"][row]
            self._refresh()
            self.changed.emit()
    
    def _on_include_changed(self, state):
        self.setup_data["include"] = (state == Qt.CheckState.Checked.value)
        self.changed.emit()
    
    def _on_name_changed(self, text):
        self.setup_data["name"] = text
    
    def _on_priority_changed(self, text):
        self.setup_data["priority"] = text
        self.changed.emit()
    
    def _on_generator_changed(self, index):
        self._refresh()
        self.changed.emit()
    
    def _on_generator_qty_changed(self, value):
        self._refresh()
        self.changed.emit()
    
    def _on_distribution_changed(self):
        self._refresh()
        self.changed.emit()


class AddBuildingDialog(QDialog):
    """Dialog for adding a building to a power setup."""
    
    def __init__(self, parent, buildings):
        super().__init__(parent)
        self.buildings = buildings
        self.setWindowTitle("Add Building")
        self.setMinimumWidth(400)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        form = QFormLayout()
        
        # Building dropdown
        self.building_combo = QComboBox()
        for bld in self.buildings:
            name = bld.get("name", "Unknown")
            power = bld.get("power_kw", 0)
            price = bld.get("price", 0)
            self.building_combo.addItem(f"{name} ({power} kW, ${price:,})", bld)
        form.addRow("Building:", self.building_combo)
        
        # Quantity
        self.qty_spin = QSpinBox()
        self.qty_spin.setRange(1, 50)
        self.qty_spin.setValue(1)
        form.addRow("Quantity:", self.qty_spin)
        
        layout.addLayout(form)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def get_building(self):
        """Return the selected building data."""
        bld_data = self.building_combo.currentData()
        if bld_data:
            return {
                "name": bld_data.get("name", "Unknown"),
                "power_kw": bld_data.get("power_kw", 0),
                "price": bld_data.get("price", 0),
                "quantity": self.qty_spin.value(),
            }
        return None
