"""
Inventory Tab - Track current inventory across all locations

Features:
- Summary dashboard with total value, item count, alerts
- Filterable inventory table by category/location/status
- Item details panel with value calculations
- Oil lifetime cap tracker (configurable)
- Add/Edit/Delete/Adjust quantity functionality
"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QLabel,
    QPushButton,
    QLineEdit,
    QComboBox,
    QSpinBox,
    QDoubleSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QCheckBox,
    QSplitter,
    QFormLayout,
    QMessageBox,
    QAbstractItemView,
    QDialog,
    QDialogButtonBox,
    QRadioButton,
    QButtonGroup,
    QProgressBar,
    QFrame,
    QTextEdit,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor

from core.database import get_database
from datetime import datetime


class InventoryTab(QWidget):
    """Inventory tab for tracking stock across locations."""
    
    # Signals
    data_changed = pyqtSignal()
    
    # Stock status thresholds
    STOCK_EMPTY = 0
    STOCK_LOW = 10
    STOCK_GOOD = 100
    
    # Default settings (will be configurable in Settings tab later)
    DEFAULT_OIL_CAP = 10000
    COMPANY_SPLIT = 0.90
    PERSONAL_SPLIT = 0.10
    
    def __init__(self, parent=None, main_window=None):
        super().__init__(parent)
        self.db = get_database()
        self.main_window = main_window
        
        # Inventory data
        self.inventory_items = []
        self.filtered_items = []
        
        # Oil tracking
        self.oil_cap_enabled = True
        self.oil_cap_amount = self.DEFAULT_OIL_CAP
        self.oil_lifetime_sold = 0
        
        # Reference data
        self.categories = []
        self.locations = []
        
        self._load_reference_data()
        self._setup_ui()
        self._load_inventory()
    
    def _load_reference_data(self):
        """Load categories and locations for dropdowns."""
        # Categories for inventory tracking (matching game categories exactly)
        self.categories = [
            # Resources (raw materials from mining)
            "Resources - Ore",
            "Resources - Fluids",
            "Resources - Dirt",
            "Resources - Rock",
            "Resources - Wood",        # Log (raw wood)
            # Materials (processed/crafted items)
            "Materials - Ore",        # Bars, Diamond, Ruby
            "Materials - Concrete",   # Cement
            "Materials - Sub Parts",  # Electronic Parts, Empty Barrel, Plastics, Rubber, Wearplate (craftable)
            "Materials - Fuel",       # Fuel (not vehicle fuel)
            "Materials - Metals",     # Steel Rod, Steel Sheet
            "Materials - Wood",       # Wood Beam, Wood Plank, Wood Sheet
            # Equipment (vehicle/machine parts)
            "Equipment - Batteries",
            "Equipment - ECUs",
            "Equipment - Filters",
            "Equipment - Hoses",
            "Equipment - Injectors",
            "Equipment - Pumps",
            "Equipment - Rams",
            "Equipment - Sensors",
            "Equipment - Sub Parts",  # Bearing, Bolts & Nuts, Cable, Gear, Gearbox, etc.
            "Equipment - Turbos",
            "Equipment - Wearparts",
            # Buildings (constructed elements)
            "Buildings - Steel",
            "Buildings - Steel Doors",
            "Buildings - Steel Mesh",
            "Buildings - Concrete",         # Standard concrete
            "Buildings - Rough Concrete",   # Rough concrete (cheaper)
            "Buildings - Polished Concrete", # Polished concrete (expensive)
            "Buildings - Wood",
            "Buildings - Quest buildings",
        ]
        
        # Load locations from database
        self.locations = self.db.get_locations()
        self.location_names = [""] + [loc['name'] for loc in self.locations]
        
        # Item prices (SELL prices from Reference Data - Items tab)
        # These are fallbacks; actual prices should come from Reference Data
        self.item_prices = {
            # Resources - Ore (sell prices from Reference Data)
            "Aluminium Ore": 37, "Coal": 13, "Copper Ore": 28,
            "Diamond Ore": 45, "Gold Ore": 43, "Iron Ore": 24,
            "Lithium Ore": 53, "Ruby Ore": 46, "Silicon Ore": 50,
            "Silver Ore": 41, "Platinum Ore": 55,
            # Resources - Wood
            "Tree Logs": 4,
            # Materials - Ore (Bars, Diamond, Ruby) - sell prices
            "Aluminium Bar": 105, "Copper Bar": 67, "Diamond": 186,
            "Gold Bar": 147, "Iron Bar": 46, "Lithium Bar": 175,
            "Platinum Bar": 186, "Ruby": 193, "Silicon Bar": 56,
            "Silver Bar": 123, "Steel Bar": 60,
            # Materials - Concrete
            "Cement": 11,
            # Materials - Sub Parts (sell prices from Reference Data)
            "Electronic Parts": 350, "Empty Barrel": 46, "Plastics": 98,
            "Rubber": 95, "Wearplate": 224,
            # Materials - Fuel
            "Fuel": 70,
            # Materials - Metals
            "Steel Rod": 84, "Steel Sheet": 84,
            # Materials - Wood
            "Wood Beam": 6, "Wood Plank": 6, "Wood Sheet": 6,
            # Resources - Fluids (sell prices)
            "Oil": 47, "Refined Oil": 93, "Water": 4,
            # Resources - Dirt (sell prices)
            "PayDirt": 1.50, "Dirt": 1, "Tailings": 0.50,
            # Resources - Rock (sell prices)
            "Gravel": 4, "Blasted Rock": 3, "Crushed Rock": 4, "Solid Rock": 3,
            # Equipment - Sub Parts (sell prices)
            "Bearing": 98, "Bolts & Nuts": 105, "Cable": 350, "Cam Axle": 350,
            "Chain": 350, "Drive Axle": 350, "Electric Motor": 350,
            "Engine Head": 350, "Gear": 175, "Gear Axle": 490,
            "Gearbox": 1610, "Large Drive Axle": 350, "Piston Rod": 245,
            "Small Gearbox": 350, "Stepper Motor": 350,
        }
    
    def get_item_sell_price(self, item_name, category=None):
        """Get sell price for an item from Reference Data, fallback to hardcoded.
        
        Args:
            item_name: Name of the item
            category: Optional category to match (for items with same name in different categories)
            
        Returns:
            Sell price as float, or 0 if not found
        """
        # Try to get from Reference Data first
        try:
            if self.main_window and hasattr(self.main_window, 'reference_tab'):
                ref = self.main_window.reference_tab
                # If category provided, use more specific lookup
                if category:
                    item = ref.get_item_by_name_and_category(item_name, category)
                    if item:
                        return item.sell_price
                # Fallback to name-only lookup
                item = ref.get_item_by_name(item_name)
                if item:
                    return item.sell_price
        except Exception:
            pass
        
        # Fallback to hardcoded prices
        return self.item_prices.get(item_name, 0)
    
    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Top: Summary Dashboard
        layout.addWidget(self._create_summary_panel())
        
        # Filters
        layout.addWidget(self._create_filter_panel())
        
        # Main content: Splitter with table and details
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left: Inventory Table
        table_widget = QWidget()
        table_layout = QVBoxLayout(table_widget)
        table_layout.setContentsMargins(0, 0, 0, 0)
        
        self.table = self._create_inventory_table()
        table_layout.addWidget(self.table)
        
        # Table buttons
        btn_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("➕ Add Item")
        self.add_btn.clicked.connect(self._on_add_item)
        btn_layout.addWidget(self.add_btn)
        
        self.edit_btn = QPushButton("✏️ Edit")
        self.edit_btn.clicked.connect(self._on_edit_item)
        btn_layout.addWidget(self.edit_btn)
        
        self.adjust_btn = QPushButton("📥 Adjust Qty")
        self.adjust_btn.clicked.connect(self._on_adjust_quantity)
        btn_layout.addWidget(self.adjust_btn)
        
        self.delete_btn = QPushButton("🗑️ Delete")
        self.delete_btn.clicked.connect(self._on_delete_item)
        btn_layout.addWidget(self.delete_btn)
        
        btn_layout.addStretch()
        
        # Sync from Ledger button
        self.sync_btn = QPushButton("🔄 Sync from Ledger")
        self.sync_btn.setToolTip("Scan Ledger transactions and update inventory quantities")
        self.sync_btn.clicked.connect(self._on_sync_from_ledger)
        self.sync_btn.setStyleSheet("background-color: #e3f2fd;")
        btn_layout.addWidget(self.sync_btn)
        
        table_layout.addLayout(btn_layout)
        
        splitter.addWidget(table_widget)
        
        # Right: Details Panel
        self.details_panel = self._create_details_panel()
        splitter.addWidget(self.details_panel)
        
        splitter.setSizes([600, 400])
        layout.addWidget(splitter, stretch=1)
        
        # Bottom: Oil Tracker
        layout.addWidget(self._create_oil_tracker())
    
    def _create_summary_panel(self) -> QGroupBox:
        """Create the summary dashboard."""
        group = QGroupBox("📊 Inventory Summary")
        layout = QHBoxLayout(group)
        
        # Total Value
        value_layout = QVBoxLayout()
        value_layout.addWidget(QLabel("💰 Total Value"))
        self.total_value_label = QLabel("$0")
        self.total_value_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2e7d32;")
        value_layout.addWidget(self.total_value_label)
        layout.addLayout(value_layout)
        
        layout.addWidget(self._create_separator())
        
        # Items with Stock
        items_layout = QVBoxLayout()
        items_layout.addWidget(QLabel("📦 Items with Stock"))
        self.items_count_label = QLabel("0")
        self.items_count_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        items_layout.addWidget(self.items_count_label)
        layout.addLayout(items_layout)
        
        layout.addWidget(self._create_separator())
        
        # Locations
        loc_layout = QVBoxLayout()
        loc_layout.addWidget(QLabel("📍 Active Locations"))
        self.locations_count_label = QLabel("0")
        self.locations_count_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        loc_layout.addWidget(self.locations_count_label)
        layout.addLayout(loc_layout)
        
        layout.addWidget(self._create_separator())
        
        # Low Stock Alerts
        alert_layout = QVBoxLayout()
        alert_layout.addWidget(QLabel("⚠️ Low Stock"))
        self.low_stock_label = QLabel("0")
        self.low_stock_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #f57c00;")
        alert_layout.addWidget(self.low_stock_label)
        layout.addLayout(alert_layout)
        
        layout.addWidget(self._create_separator())
        
        # Oil Status (quick view)
        oil_layout = QVBoxLayout()
        oil_layout.addWidget(QLabel("🛢️ Oil Cap"))
        self.oil_status_label = QLabel("--")
        self.oil_status_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        oil_layout.addWidget(self.oil_status_label)
        layout.addLayout(oil_layout)
        
        layout.addStretch()
        
        return group
    
    def _create_separator(self) -> QFrame:
        """Create a vertical separator line."""
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        return separator
    
    def _create_filter_panel(self) -> QGroupBox:
        """Create the filter controls."""
        group = QGroupBox("🔍 Filters")
        layout = QHBoxLayout(group)
        
        # Search
        layout.addWidget(QLabel("Search:"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Item name...")
        self.search_edit.textChanged.connect(self._apply_filters)
        self.search_edit.setMaximumWidth(150)
        layout.addWidget(self.search_edit)
        
        # Category filter
        layout.addWidget(QLabel("Category:"))
        self.category_combo = QComboBox()
        self.category_combo.addItem("All Categories")
        self.category_combo.addItems(self.categories)
        self.category_combo.currentIndexChanged.connect(self._apply_filters)
        layout.addWidget(self.category_combo)
        
        # Location filter
        layout.addWidget(QLabel("Location:"))
        self.location_combo = QComboBox()
        self.location_combo.addItem("All Locations")
        for loc in self.locations:
            self.location_combo.addItem(loc['name'])
        self.location_combo.currentIndexChanged.connect(self._apply_filters)
        layout.addWidget(self.location_combo)
        
        # Stock status filter
        layout.addWidget(QLabel("Status:"))
        self.status_combo = QComboBox()
        self.status_combo.addItems(["All", "Empty", "Low", "Good", "High"])
        self.status_combo.currentIndexChanged.connect(self._apply_filters)
        layout.addWidget(self.status_combo)
        
        # Show zero stock
        self.show_zero_check = QCheckBox("Show Zero Stock")
        self.show_zero_check.setChecked(True)
        self.show_zero_check.stateChanged.connect(self._apply_filters)
        layout.addWidget(self.show_zero_check)
        
        layout.addStretch()
        
        # Refresh button
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self._load_inventory)
        layout.addWidget(self.refresh_btn)
        
        return group
    
    def _create_inventory_table(self) -> QTableWidget:
        """Create the main inventory table."""
        table = QTableWidget()
        
        columns = ["Item Name", "Category", "Location", "Quantity", "Unit Price", "Total Value", "Status"]
        table.setColumnCount(len(columns))
        table.setHorizontalHeaderLabels(columns)
        
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        table.setSortingEnabled(True)
        
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Item Name
        for i in range(1, len(columns)):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        
        table.itemSelectionChanged.connect(self._on_selection_changed)
        
        return table
    
    def _create_details_panel(self) -> QGroupBox:
        """Create the item details panel."""
        group = QGroupBox("📋 Item Details")
        layout = QVBoxLayout(group)
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setHtml("<p style='color: #666;'>Select an item to view details</p>")
        layout.addWidget(self.details_text)
        
        return group
    
    def _create_oil_tracker(self) -> QGroupBox:
        """Create the oil lifetime cap tracker."""
        group = QGroupBox("🛢️ Oil Lifetime Cap Tracker")
        layout = QVBoxLayout(group)
        
        # Warning label
        self.oil_warning_label = QLabel("⚠️ LIFETIME CAP ACTIVE (configured in Settings → Rules Config)")
        self.oil_warning_label.setStyleSheet("color: #f57c00; font-weight: bold;")
        layout.addWidget(self.oil_warning_label)
        
        # Stats row
        stats_layout = QHBoxLayout()
        
        # Current inventory
        inv_layout = QFormLayout()
        self.oil_inventory_label = QLabel("0")
        self.oil_inventory_label.setStyleSheet("font-weight: bold;")
        inv_layout.addRow("Current Inventory:", self.oil_inventory_label)
        stats_layout.addLayout(inv_layout)
        
        # Total sold
        sold_layout = QFormLayout()
        self.oil_sold_label = QLabel("0")
        self.oil_sold_label.setStyleSheet("font-weight: bold;")
        sold_layout.addRow("Total Sold (Lifetime):", self.oil_sold_label)
        stats_layout.addLayout(sold_layout)
        
        # Remaining
        remaining_layout = QFormLayout()
        self.oil_remaining_label = QLabel("0")
        self.oil_remaining_label.setStyleSheet("font-weight: bold; color: #2e7d32;")
        remaining_layout.addRow("Remaining Cap:", self.oil_remaining_label)
        stats_layout.addLayout(remaining_layout)
        
        # Cap setting
        cap_layout = QFormLayout()
        self.oil_cap_spin = QSpinBox()
        self.oil_cap_spin.setRange(0, 9999999)
        self.oil_cap_spin.setValue(self.oil_cap_amount)
        self.oil_cap_spin.valueChanged.connect(self._on_oil_cap_changed)
        cap_layout.addRow("Cap Limit:", self.oil_cap_spin)
        stats_layout.addLayout(cap_layout)
        
        stats_layout.addStretch()
        layout.addLayout(stats_layout)
        
        # Progress bar
        progress_layout = QHBoxLayout()
        progress_layout.addWidget(QLabel("Progress:"))
        self.oil_progress = QProgressBar()
        self.oil_progress.setRange(0, 100)
        self.oil_progress.setValue(0)
        self.oil_progress.setFormat("%p% used")
        progress_layout.addWidget(self.oil_progress, stretch=1)
        self.oil_progress_text = QLabel("0 / 10,000")
        progress_layout.addWidget(self.oil_progress_text)
        layout.addLayout(progress_layout)
        
        # Revenue potential
        revenue_layout = QHBoxLayout()
        revenue_layout.addWidget(QLabel("Revenue if all remaining sold:"))
        self.oil_revenue_label = QLabel("$0")
        self.oil_revenue_label.setStyleSheet("font-weight: bold;")
        revenue_layout.addWidget(self.oil_revenue_label)
        revenue_layout.addWidget(QLabel("(Company:"))
        self.oil_company_label = QLabel("$0")
        revenue_layout.addWidget(self.oil_company_label)
        revenue_layout.addWidget(QLabel("Personal:"))
        self.oil_personal_label = QLabel("$0")
        revenue_layout.addWidget(self.oil_personal_label)
        revenue_layout.addWidget(QLabel(")"))
        revenue_layout.addStretch()
        
        # Reset button
        self.oil_reset_btn = QPushButton("🔄 Reset Lifetime Counter")
        self.oil_reset_btn.setToolTip("Use when starting a new playthrough")
        self.oil_reset_btn.clicked.connect(self._on_reset_oil_counter)
        revenue_layout.addWidget(self.oil_reset_btn)
        
        layout.addLayout(revenue_layout)
        
        return group
    
    def _load_inventory(self):
        """Load inventory from database."""
        # For now, use in-memory storage
        # Later this will load from database
        
        if not self.inventory_items:
            # Initialize with default items (empty quantities)
            self._initialize_default_items()
        
        self._apply_filters()
        self._update_summary()
        self._update_oil_tracker()
    
    def _initialize_default_items(self):
        """Initialize inventory with default items at zero quantity."""
        default_location = "ARC - Drill Site 1" if not self.locations else self.locations[0].get('name', 'ARC - Drill Site 1')
        
        default_items = [
            # Ores
            {"name": "Aluminium Ore", "category": "Resources - Ore", "location": default_location, "quantity": 0},
            {"name": "Coal", "category": "Resources - Ore", "location": default_location, "quantity": 0},
            {"name": "Copper Ore", "category": "Resources - Ore", "location": default_location, "quantity": 0},
            {"name": "Diamond Ore", "category": "Resources - Ore", "location": default_location, "quantity": 0},
            {"name": "Gold Ore", "category": "Resources - Ore", "location": default_location, "quantity": 0},
            {"name": "Iron Ore", "category": "Resources - Ore", "location": default_location, "quantity": 0},
            {"name": "Lithium Ore", "category": "Resources - Ore", "location": default_location, "quantity": 0},
            {"name": "Ruby Ore", "category": "Resources - Ore", "location": default_location, "quantity": 0},
            {"name": "Silicon Ore", "category": "Resources - Ore", "location": default_location, "quantity": 0},
            {"name": "Silver Ore", "category": "Resources - Ore", "location": default_location, "quantity": 0},
            # Fluids
            {"name": "Oil", "category": "Resources - Fluids", "location": default_location, "quantity": 0},
            {"name": "Refined Oil", "category": "Resources - Fluids", "location": default_location, "quantity": 0},
            # Dirt
            {"name": "PayDirt", "category": "Resources - Dirt", "location": default_location, "quantity": 0},
            {"name": "Dirt", "category": "Resources - Dirt", "location": default_location, "quantity": 0},
            {"name": "Tailings", "category": "Resources - Dirt", "location": default_location, "quantity": 0},
            # Rock
            {"name": "Gravel", "category": "Resources - Rock", "location": default_location, "quantity": 0},
            {"name": "Blasted Rock", "category": "Resources - Rock", "location": default_location, "quantity": 0},
            {"name": "Crushed Rock", "category": "Resources - Rock", "location": default_location, "quantity": 0},
            {"name": "Solid Rock", "category": "Resources - Rock", "location": default_location, "quantity": 0},
            # Wood (for wood production chain)
            {"name": "Tree Logs", "category": "Resources - Wood", "location": default_location, "quantity": 0},
        ]
        
        for i, item in enumerate(default_items):
            item['id'] = i + 1
            item['unit_price'] = self.get_item_sell_price(item['name'], item.get('category'))
        
        self.inventory_items = default_items
    
    def _apply_filters(self):
        """Apply filters to inventory list."""
        search_text = self.search_edit.text().lower()
        category_filter = self.category_combo.currentText()
        location_filter = self.location_combo.currentText()
        status_filter = self.status_combo.currentText()
        show_zero = self.show_zero_check.isChecked()
        
        self.filtered_items = []
        
        for item in self.inventory_items:
            # Search filter
            if search_text and search_text not in item['name'].lower():
                continue
            
            # Category filter
            if category_filter != "All Categories" and item['category'] != category_filter:
                continue
            
            # Location filter
            if location_filter != "All Locations" and item['location'] != location_filter:
                continue
            
            # Status filter
            status = self._get_stock_status(item['quantity'])
            if status_filter != "All" and status != status_filter:
                continue
            
            # Zero stock filter
            if not show_zero and item['quantity'] == 0:
                continue
            
            self.filtered_items.append(item)
        
        self._populate_table()
    
    def _get_stock_status(self, quantity: int) -> str:
        """Get stock status string based on quantity."""
        if quantity == 0:
            return "Empty"
        elif quantity <= self.STOCK_LOW:
            return "Low"
        elif quantity <= self.STOCK_GOOD:
            return "Good"
        else:
            return "High"
    
    def _get_status_color(self, status: str) -> QColor:
        """Get color for stock status."""
        colors = {
            "Empty": QColor("#ffcdd2"),  # Light red
            "Low": QColor("#fff9c4"),     # Light yellow
            "Good": QColor("#c8e6c9"),    # Light green
            "High": QColor("#bbdefb"),    # Light blue
        }
        return colors.get(status, QColor("#ffffff"))
    
    def _populate_table(self):
        """Populate the inventory table."""
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(self.filtered_items))
        
        for row, item in enumerate(self.filtered_items):
            # Item Name
            name_item = QTableWidgetItem(item['name'])
            self.table.setItem(row, 0, name_item)
            
            # Category
            cat_item = QTableWidgetItem(item['category'])
            self.table.setItem(row, 1, cat_item)
            
            # Location
            loc_item = QTableWidgetItem(item['location'])
            self.table.setItem(row, 2, loc_item)
            
            # Quantity
            qty_item = QTableWidgetItem(f"{item['quantity']:,}")
            qty_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            qty_item.setData(Qt.ItemDataRole.UserRole, item['quantity'])
            self.table.setItem(row, 3, qty_item)
            
            # Unit Price
            unit_price = item.get('unit_price', self.item_prices.get(item['name'], 0))
            price_item = QTableWidgetItem(f"${unit_price:,.2f}")
            price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 4, price_item)
            
            # Total Value
            total_value = item['quantity'] * unit_price
            total_item = QTableWidgetItem(f"${total_value:,.0f}")
            total_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            total_item.setData(Qt.ItemDataRole.UserRole, total_value)
            self.table.setItem(row, 5, total_item)
            
            # Status
            status = self._get_stock_status(item['quantity'])
            status_item = QTableWidgetItem(status)
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 6, status_item)
            
            # Row color based on status
            color = self._get_status_color(status)
            for col in range(7):
                self.table.item(row, col).setBackground(color)
        
        self.table.setSortingEnabled(True)
    
    def _update_summary(self):
        """Update summary statistics."""
        total_value = 0
        items_with_stock = 0
        active_locations = set()
        low_stock_count = 0
        
        for item in self.inventory_items:
            unit_price = item.get('unit_price', self.item_prices.get(item['name'], 0))
            total_value += item['quantity'] * unit_price
            
            if item['quantity'] > 0:
                items_with_stock += 1
                active_locations.add(item['location'])
            
            if 0 < item['quantity'] <= self.STOCK_LOW:
                low_stock_count += 1
        
        self.total_value_label.setText(f"${total_value:,.0f}")
        self.items_count_label.setText(str(items_with_stock))
        self.locations_count_label.setText(str(len(active_locations)))
        self.low_stock_label.setText(str(low_stock_count))
        
        # Update oil quick status
        remaining = self.oil_cap_amount - self.oil_lifetime_sold
        pct = (remaining / self.oil_cap_amount * 100) if self.oil_cap_amount > 0 else 0
        self.oil_status_label.setText(f"{remaining:,} left ({pct:.0f}%)")
    
    def _update_oil_tracker(self):
        """Update oil lifetime cap tracker."""
        # Find oil in inventory
        oil_inventory = 0
        for item in self.inventory_items:
            if item['name'] == "Oil":
                oil_inventory = item['quantity']
                break
        
        remaining = self.oil_cap_amount - self.oil_lifetime_sold
        pct_used = (self.oil_lifetime_sold / self.oil_cap_amount * 100) if self.oil_cap_amount > 0 else 0
        
        self.oil_inventory_label.setText(f"{oil_inventory:,}")
        self.oil_sold_label.setText(f"{self.oil_lifetime_sold:,}")
        self.oil_remaining_label.setText(f"{remaining:,}")
        
        self.oil_progress.setValue(int(pct_used))
        self.oil_progress_text.setText(f"{self.oil_lifetime_sold:,} / {self.oil_cap_amount:,}")
        
        # Revenue calculations
        oil_price = self.item_prices.get("Oil", 66.50)
        revenue = remaining * oil_price
        company = revenue * self.COMPANY_SPLIT
        personal = revenue * self.PERSONAL_SPLIT
        
        self.oil_revenue_label.setText(f"${revenue:,.0f}")
        self.oil_company_label.setText(f"${company:,.0f}")
        self.oil_personal_label.setText(f"${personal:,.0f}")
        
        # Update status color
        if pct_used >= 90:
            self.oil_warning_label.setStyleSheet("color: #c62828; font-weight: bold;")
            self.oil_warning_label.setText("🚨 CRITICAL: Less than 10% cap remaining!")
        elif pct_used >= 75:
            self.oil_warning_label.setStyleSheet("color: #f57c00; font-weight: bold;")
            self.oil_warning_label.setText("⚠️ WARNING: Less than 25% cap remaining")
        else:
            self.oil_warning_label.setStyleSheet("color: #2e7d32; font-weight: bold;")
            self.oil_warning_label.setText("✅ Oil cap in good standing")
    
    def _on_selection_changed(self):
        """Handle table selection change."""
        selected = self.table.selectedItems()
        if not selected:
            self.details_text.setHtml("<p style='color: #666;'>Select an item to view details</p>")
            return
        
        row = selected[0].row()
        if row < 0 or row >= len(self.filtered_items):
            return
        
        item = self.filtered_items[row]
        unit_price = item.get('unit_price', self.item_prices.get(item['name'], 0))
        total_value = item['quantity'] * unit_price
        status = self._get_stock_status(item['quantity'])
        
        # Revenue potential with split
        gross = total_value
        company = gross * self.COMPANY_SPLIT
        personal = gross * self.PERSONAL_SPLIT
        
        html = f"""
        <style>
            body {{ font-family: sans-serif; font-size: 12px; }}
            h2 {{ margin: 5px 0; color: #1976d2; }}
            h3 {{ margin: 10px 0 5px 0; color: #388e3c; }}
            .label {{ color: #666; }}
            .value {{ font-weight: bold; }}
            .section {{ margin-top: 15px; padding: 10px; background: #f5f5f5; border-radius: 5px; }}
        </style>
        
        <h2>{item['name']}</h2>
        <p><span class="label">Category:</span> <span class="value">{item['category']}</span></p>
        <p><span class="label">Location:</span> <span class="value">{item['location']}</span></p>
        <p><span class="label">Status:</span> <span class="value">{status}</span></p>
        
        <div class="section">
            <h3>📦 Quantities</h3>
            <p><span class="label">Current Stock:</span> <span class="value">{item['quantity']:,}</span></p>
        </div>
        
        <div class="section">
            <h3>💰 Values</h3>
            <p><span class="label">Unit Price:</span> <span class="value">${unit_price:,.2f}</span></p>
            <p><span class="label">Total Value:</span> <span class="value">${total_value:,.0f}</span></p>
        </div>
        
        <div class="section">
            <h3>📊 Revenue Potential (if sold)</h3>
            <p><span class="label">Gross:</span> <span class="value">${gross:,.0f}</span></p>
            <p><span class="label">Company (90%):</span> <span class="value">${company:,.0f}</span></p>
            <p><span class="label">Personal (10%):</span> <span class="value">${personal:,.0f}</span></p>
        </div>
        """
        
        # Special info for Oil
        if item['name'] == "Oil":
            remaining = self.oil_cap_amount - self.oil_lifetime_sold
            html += f"""
            <div class="section" style="background: #fff3e0;">
                <h3>🛢️ Lifetime Cap Info</h3>
                <p><span class="label">Lifetime Cap:</span> <span class="value">{self.oil_cap_amount:,}</span></p>
                <p><span class="label">Total Sold:</span> <span class="value">{self.oil_lifetime_sold:,}</span></p>
                <p><span class="label">Remaining:</span> <span class="value">{remaining:,}</span></p>
            </div>
            """
        
        self.details_text.setHtml(html)
    
    def _on_add_item(self):
        """Add a new inventory item."""
        dialog = InventoryItemDialog(self, self.item_prices, self.location_names, self.categories)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            item = dialog.get_item_data()
            item['id'] = len(self.inventory_items) + 1
            item['unit_price'] = self.item_prices.get(item['name'], 0)
            self.inventory_items.append(item)
            self._apply_filters()
            self._update_summary()
            self._update_oil_tracker()
    
    def _on_edit_item(self):
        """Edit selected inventory item."""
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.information(self, "Edit", "Please select an item to edit.")
            return
        
        row = selected[0].row()
        item = self.filtered_items[row]
        
        dialog = InventoryItemDialog(self, self.item_prices, self.location_names, self.categories, item)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated = dialog.get_item_data()
            
            # Find and update in main list
            for i, inv_item in enumerate(self.inventory_items):
                if inv_item['id'] == item['id']:
                    updated['id'] = item['id']
                    updated['unit_price'] = self.item_prices.get(updated['name'], 0)
                    self.inventory_items[i] = updated
                    break
            
            self._apply_filters()
            self._update_summary()
            self._update_oil_tracker()
    
    def _on_adjust_quantity(self):
        """Quick adjust quantity of selected item."""
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.information(self, "Adjust", "Please select an item to adjust.")
            return
        
        row = selected[0].row()
        item = self.filtered_items[row]
        
        dialog = AdjustQuantityDialog(self, item)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_qty = dialog.get_new_quantity()
            
            # Track oil sales
            if item['name'] == "Oil" and new_qty < item['quantity']:
                sold = item['quantity'] - new_qty
                self.oil_lifetime_sold += sold
            
            # Update quantity
            for inv_item in self.inventory_items:
                if inv_item['id'] == item['id']:
                    inv_item['quantity'] = new_qty
                    break
            
            self._apply_filters()
            self._update_summary()
            self._update_oil_tracker()
    
    def _on_delete_item(self):
        """Delete selected inventory item."""
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.information(self, "Delete", "Please select an item to delete.")
            return
        
        row = selected[0].row()
        item = self.filtered_items[row]
        
        reply = QMessageBox.question(
            self, "Delete Item",
            f"Delete '{item['name']}' from inventory?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.inventory_items = [i for i in self.inventory_items if i['id'] != item['id']]
            self._apply_filters()
            self._update_summary()
            self._update_oil_tracker()
    
    def _on_oil_cap_changed(self, value):
        """Handle oil cap value change."""
        self.oil_cap_amount = value
        self._update_summary()
        self._update_oil_tracker()
    
    def _on_reset_oil_counter(self):
        """Reset oil lifetime counter."""
        reply = QMessageBox.question(
            self, "Reset Oil Counter",
            "Reset the oil lifetime sold counter to 0?\n\nUse this when starting a new playthrough.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.oil_lifetime_sold = 0
            self._update_summary()
            self._update_oil_tracker()
            QMessageBox.information(self, "Reset", "Oil lifetime counter has been reset.")
    
    def _on_sync_from_ledger(self):
        """Sync inventory from Ledger transactions."""
        if not self.main_window or not hasattr(self.main_window, 'ledger_tab'):
            QMessageBox.warning(self, "Sync Error", "Ledger tab not available.")
            return
        
        ledger = self.main_window.ledger_tab
        
        # Scan all transactions and calculate net quantities
        changes = {}  # {(item_name, category): quantity_change}
        
        for txn in ledger.transactions:
            txn_type = txn.get('type', '')
            item_name = txn.get('item', '')
            category = txn.get('category', '')
            quantity = txn.get('quantity', 0)
            
            if txn_type == 'Opening' or not item_name or not quantity:
                continue
            
            key = (item_name, category)
            
            if txn_type == 'Purchase':
                # Purchases add to inventory
                changes[key] = changes.get(key, 0) + quantity
            elif txn_type == 'Sale':
                # Sales subtract from inventory
                changes[key] = changes.get(key, 0) - quantity
            # Fuel and Transfer don't affect item inventory
        
        if not changes:
            QMessageBox.information(self, "Sync", "No Purchase or Sale transactions found in Ledger.")
            return
        
        # Show confirmation dialog
        dialog = SyncFromLedgerDialog(self, changes, self.inventory_items)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected_changes = dialog.get_selected_changes()
            
            if not selected_changes:
                return
            
            # Apply selected changes
            applied_count = 0
            for (item_name, category), change in selected_changes.items():
                if change == 0:
                    continue
                
                # Find existing item
                found = False
                for item in self.inventory_items:
                    if item['name'] == item_name and item.get('category', '') == category:
                        item['quantity'] = max(0, item['quantity'] + change)
                        found = True
                        applied_count += 1
                        break
                
                # If not found and change is positive (net purchases), add new item
                if not found and change > 0:
                    new_item = {
                        'id': len(self.inventory_items) + 1,
                        'name': item_name,
                        'category': category,
                        'location': 'Unknown',
                        'quantity': change,
                        'unit_price': self.get_item_sell_price(item_name, category),
                    }
                    self.inventory_items.append(new_item)
                    applied_count += 1
            
            self._apply_filters()
            self._update_summary()
            self._update_oil_tracker()
            
            QMessageBox.information(
                self, "Sync Complete",
                f"Successfully updated {applied_count} inventory items from Ledger."
            )
    
    # === Public API Methods for other tabs ===
    
    def adjust_item_quantity(self, item_name: str, quantity_change: int, track_oil: bool = True) -> bool:
        """
        Adjust quantity of an item by a delta amount.
        
        Args:
            item_name: Name of the item to adjust
            quantity_change: Amount to add (positive) or subtract (negative)
            track_oil: Whether to track oil sales for cap
            
        Returns:
            True if successful, False if item not found or insufficient quantity
        """
        for item in self.inventory_items:
            if item['name'] == item_name:
                new_qty = item['quantity'] + quantity_change
                
                # Don't allow negative quantities
                if new_qty < 0:
                    return False
                
                # Track oil sales if reducing oil quantity
                if track_oil and item_name == "Oil" and quantity_change < 0:
                    self.oil_lifetime_sold += abs(quantity_change)
                
                item['quantity'] = new_qty
                self._apply_filters()
                self._update_summary()
                self._update_oil_tracker()
                return True
        
        return False
    
    def add_or_update_item(self, item_name: str, quantity: int, category: str = None, 
                          location: str = None, unit_price: float = None) -> bool:
        """
        Add a new item or update quantity of existing item.
        
        Args:
            item_name: Name of the item
            quantity: Quantity to add (will be added to existing if item exists)
            category: Category (used for matching AND creating new items)
            location: Location (only used if creating new item)
            unit_price: Unit price (used for new items, updates existing if provided)
            
        Returns:
            True if successful
        """
        # Check if item exists - match by name AND category if category provided
        for item in self.inventory_items:
            if item['name'] == item_name:
                # If category is provided, it must match too
                if category and item['category'] != category:
                    continue  # Keep looking for matching category
                
                item['quantity'] += quantity
                # Update unit price if provided
                if unit_price is not None:
                    item['unit_price'] = unit_price
                self._apply_filters()
                self._update_summary()
                self._update_oil_tracker()
                return True
        
        # Create new item (no match found by name+category)
        new_item = {
            'id': len(self.inventory_items) + 1,
            'name': item_name,
            'quantity': quantity,
            'category': category or "Unknown",
            'location': location or "Unknown",
            'unit_price': unit_price or self.item_prices.get(item_name, 0),
        }
        self.inventory_items.append(new_item)
        self._apply_filters()
        self._update_summary()
        self._update_oil_tracker()
        return True
    
    def get_item_quantity(self, item_name: str) -> int:
        """Get current quantity of an item."""
        for item in self.inventory_items:
            if item['name'] == item_name:
                return item.get('quantity', 0)
        return 0


class InventoryItemDialog(QDialog):
    """Dialog for adding/editing inventory items."""
    
    def __init__(self, parent, item_prices: dict, locations: list, categories: list, item: dict = None):
        super().__init__(parent)
        self.item_prices = item_prices
        self.locations = locations
        self.categories = categories
        self.item = item
        
        self.setWindowTitle("Edit Item" if item else "Add Item")
        self.setMinimumWidth(400)
        
        self._setup_ui()
        
        if item:
            self._populate_fields()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        form = QFormLayout()
        
        # Item name
        self.name_combo = QComboBox()
        self.name_combo.setEditable(True)
        self.name_combo.addItems(sorted(self.item_prices.keys()))
        form.addRow("Item Name:", self.name_combo)
        
        # Category
        self.category_combo = QComboBox()
        self.category_combo.addItems(self.categories)
        form.addRow("Category:", self.category_combo)
        
        # Location
        self.location_combo = QComboBox()
        self.location_combo.addItems(self.locations)
        form.addRow("Location:", self.location_combo)
        
        # Quantity
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setRange(0, 9999999)
        form.addRow("Quantity:", self.quantity_spin)
        
        layout.addLayout(form)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def _populate_fields(self):
        """Populate fields with existing item data."""
        self.name_combo.setCurrentText(self.item['name'])
        
        idx = self.category_combo.findText(self.item['category'])
        if idx >= 0:
            self.category_combo.setCurrentIndex(idx)
        
        idx = self.location_combo.findText(self.item['location'])
        if idx >= 0:
            self.location_combo.setCurrentIndex(idx)
        
        self.quantity_spin.setValue(self.item['quantity'])
    
    def get_item_data(self) -> dict:
        """Get the item data from the dialog."""
        return {
            'name': self.name_combo.currentText(),
            'category': self.category_combo.currentText(),
            'location': self.location_combo.currentText(),
            'quantity': self.quantity_spin.value(),
        }


class AdjustQuantityDialog(QDialog):
    """Dialog for quick quantity adjustment."""
    
    def __init__(self, parent, item: dict):
        super().__init__(parent)
        self.item = item
        self.current_qty = item['quantity']
        
        self.setWindowTitle("Adjust Quantity")
        self.setMinimumWidth(350)
        
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Item info
        info_group = QGroupBox("Item")
        info_layout = QFormLayout(info_group)
        info_layout.addRow("Name:", QLabel(self.item['name']))
        info_layout.addRow("Location:", QLabel(self.item['location']))
        info_layout.addRow("Current Qty:", QLabel(f"{self.current_qty:,}"))
        layout.addWidget(info_group)
        
        # Adjustment type
        type_group = QGroupBox("Adjustment Type")
        type_layout = QVBoxLayout(type_group)
        
        self.type_group = QButtonGroup()
        
        self.add_radio = QRadioButton("Add to inventory")
        self.add_radio.setChecked(True)
        self.type_group.addButton(self.add_radio, 0)
        type_layout.addWidget(self.add_radio)
        
        self.remove_radio = QRadioButton("Remove from inventory")
        self.type_group.addButton(self.remove_radio, 1)
        type_layout.addWidget(self.remove_radio)
        
        self.set_radio = QRadioButton("Set exact quantity")
        self.type_group.addButton(self.set_radio, 2)
        type_layout.addWidget(self.set_radio)
        
        layout.addWidget(type_group)
        
        # Amount
        amount_layout = QHBoxLayout()
        amount_layout.addWidget(QLabel("Amount:"))
        self.amount_spin = QSpinBox()
        self.amount_spin.setRange(0, 9999999)
        self.amount_spin.valueChanged.connect(self._update_preview)
        amount_layout.addWidget(self.amount_spin)
        layout.addLayout(amount_layout)
        
        # Connect radio buttons to update preview
        self.add_radio.toggled.connect(self._update_preview)
        self.remove_radio.toggled.connect(self._update_preview)
        self.set_radio.toggled.connect(self._update_preview)
        
        # Reason
        reason_layout = QHBoxLayout()
        reason_layout.addWidget(QLabel("Reason:"))
        self.reason_combo = QComboBox()
        self.reason_combo.addItems([
            "Processing output",
            "Sale",
            "Transfer",
            "Purchase",
            "Correction",
            "Other",
        ])
        reason_layout.addWidget(self.reason_combo)
        layout.addLayout(reason_layout)
        
        # Preview
        preview_layout = QHBoxLayout()
        preview_layout.addWidget(QLabel("New Qty:"))
        self.preview_label = QLabel(f"{self.current_qty:,}")
        self.preview_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        preview_layout.addWidget(self.preview_label)
        preview_layout.addStretch()
        layout.addLayout(preview_layout)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def _update_preview(self):
        """Update the preview of new quantity."""
        new_qty = self.get_new_quantity()
        self.preview_label.setText(f"{new_qty:,}")
        
        if new_qty < 0:
            self.preview_label.setStyleSheet("font-weight: bold; font-size: 14px; color: red;")
        else:
            self.preview_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #2e7d32;")
    
    def get_new_quantity(self) -> int:
        """Calculate the new quantity based on adjustment type."""
        amount = self.amount_spin.value()
        
        if self.add_radio.isChecked():
            return self.current_qty + amount
        elif self.remove_radio.isChecked():
            return max(0, self.current_qty - amount)
        else:  # Set exact
            return amount


class SyncFromLedgerDialog(QDialog):
    """Dialog for syncing inventory from Ledger transactions."""
    
    def __init__(self, parent, changes: dict, inventory_items: list):
        super().__init__(parent)
        self.changes = changes  # {(item_name, category): net_change}
        self.inventory_items = inventory_items
        self.checkboxes = {}  # {(item_name, category): QCheckBox}
        
        self.setWindowTitle("Sync from Ledger")
        self.setMinimumWidth(700)
        self.setMinimumHeight(500)
        
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel(
            "<b>Review Ledger Transactions</b><br>"
            "Select which changes to apply to inventory. "
            "Positive numbers = net purchases (will ADD to inventory). "
            "Negative numbers = net sales (will SUBTRACT from inventory)."
        )
        header.setWordWrap(True)
        layout.addWidget(header)
        
        # Summary
        total_purchases = sum(v for v in self.changes.values() if v > 0)
        total_sales = sum(abs(v) for v in self.changes.values() if v < 0)
        summary = QLabel(
            f"Found {len(self.changes)} items | "
            f"Net Purchases: +{total_purchases:,} units | "
            f"Net Sales: -{total_sales:,} units"
        )
        summary.setStyleSheet("color: #666; margin: 5px 0;")
        layout.addWidget(summary)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Apply", "Item Name", "Category", "Current Qty", "Change", "New Qty"
        ])
        
        self.table.setRowCount(len(self.changes))
        self.table.setAlternatingRowColors(True)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        
        for row, ((item_name, category), change) in enumerate(sorted(self.changes.items())):
            # Checkbox
            checkbox = QCheckBox()
            checkbox.setChecked(True)
            self.checkboxes[(item_name, category)] = checkbox
            
            checkbox_widget = QWidget()
            checkbox_layout = QHBoxLayout(checkbox_widget)
            checkbox_layout.addWidget(checkbox)
            checkbox_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            self.table.setCellWidget(row, 0, checkbox_widget)
            
            # Item Name
            self.table.setItem(row, 1, QTableWidgetItem(item_name))
            
            # Category
            self.table.setItem(row, 2, QTableWidgetItem(category))
            
            # Current Qty
            current_qty = 0
            for item in self.inventory_items:
                if item['name'] == item_name and item.get('category', '') == category:
                    current_qty = item['quantity']
                    break
            current_item = QTableWidgetItem(f"{current_qty:,}")
            current_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 3, current_item)
            
            # Change
            change_item = QTableWidgetItem(f"{change:+,}" if change != 0 else "0")
            change_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            if change > 0:
                change_item.setForeground(QColor("#2e7d32"))  # Green for additions
            elif change < 0:
                change_item.setForeground(QColor("#c62828"))  # Red for subtractions
            self.table.setItem(row, 4, change_item)
            
            # New Qty
            new_qty = max(0, current_qty + change)
            new_item = QTableWidgetItem(f"{new_qty:,}")
            new_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            if new_qty == 0:
                new_item.setForeground(QColor("#f57c00"))  # Orange for zero
            self.table.setItem(row, 5, new_item)
        
        layout.addWidget(self.table)
        
        # Select All / None buttons
        select_layout = QHBoxLayout()
        
        select_all_btn = QPushButton("Select All")
        select_all_btn.clicked.connect(self._select_all)
        select_layout.addWidget(select_all_btn)
        
        select_none_btn = QPushButton("Select None")
        select_none_btn.clicked.connect(self._select_none)
        select_layout.addWidget(select_none_btn)
        
        select_purchases_btn = QPushButton("Select Purchases Only")
        select_purchases_btn.clicked.connect(self._select_purchases)
        select_layout.addWidget(select_purchases_btn)
        
        select_sales_btn = QPushButton("Select Sales Only")
        select_sales_btn.clicked.connect(self._select_sales)
        select_layout.addWidget(select_sales_btn)
        
        select_layout.addStretch()
        layout.addLayout(select_layout)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Apply Selected")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def _select_all(self):
        for checkbox in self.checkboxes.values():
            checkbox.setChecked(True)
    
    def _select_none(self):
        for checkbox in self.checkboxes.values():
            checkbox.setChecked(False)
    
    def _select_purchases(self):
        """Select only items with positive changes (net purchases)."""
        for (item_name, category), checkbox in self.checkboxes.items():
            change = self.changes.get((item_name, category), 0)
            checkbox.setChecked(change > 0)
    
    def _select_sales(self):
        """Select only items with negative changes (net sales)."""
        for (item_name, category), checkbox in self.checkboxes.items():
            change = self.changes.get((item_name, category), 0)
            checkbox.setChecked(change < 0)
    
    def get_selected_changes(self) -> dict:
        """Return only the changes that were selected."""
        return {
            key: self.changes[key]
            for key, checkbox in self.checkboxes.items()
            if checkbox.isChecked()
        }
