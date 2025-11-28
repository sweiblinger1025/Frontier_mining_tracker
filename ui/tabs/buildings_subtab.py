"""
Buildings Sub-Tab - Factory production buildings with specs and I/O

Displays all factory buildings used for processing materials.
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
    QGroupBox,
    QMessageBox,
    QAbstractItemView,
    QSplitter,
    QTextEdit,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor


# Building data from Out of Ore Production Reference
BUILDING_DATA = [
    # ==================== EXTRACTION ====================
    {"art_nr": 400187, "name": "Oil Pump", "category": "Extraction",
     "price": 1500, "power_kw": 100, "length_m": 2, "height_m": 2,
     "conveyor_speed": 30, "max_connections": 1, "efficiency": "1x",
     "inputs": ["(Oil Deposit)"], "outputs": ["Crude Oil"],
     "notes": "Place on oil deposit"},
    {"art_nr": 400181, "name": "Water Pump", "category": "Extraction",
     "price": 1500, "power_kw": 100, "length_m": 4, "height_m": 2,
     "conveyor_speed": 30, "max_connections": 1, "efficiency": "1x",
     "inputs": ["(Ground)"], "outputs": ["Unfiltered Water"],
     "notes": "Only works on Grass or Snow"},
    
    # ==================== CRUSHING ====================
    {"art_nr": 400129, "name": "Jaw Crusher", "category": "Crushing",
     "price": 45000, "power_kw": 65, "length_m": 4, "height_m": 4,
     "conveyor_speed": 30, "max_connections": 1, "efficiency": "1x",
     "inputs": ["Blasted Rock", "Solid Rock"], "outputs": ["Crushed Rock"],
     "notes": "Primary crusher"},
    {"art_nr": 400130, "name": "Cone Crusher", "category": "Crushing",
     "price": 55000, "power_kw": 75, "length_m": 4, "height_m": 4,
     "conveyor_speed": 30, "max_connections": 1, "efficiency": "1x",
     "inputs": ["Crushed Rock"], "outputs": ["Gravel"],
     "notes": "Secondary crusher"},
    
    # ==================== SORTING ====================
    {"art_nr": 400131, "name": "Trommel", "category": "Sorting",
     "price": 7500, "power_kw": 55, "length_m": 8, "height_m": 4,
     "conveyor_speed": 30, "max_connections": 1, "efficiency": "1x",
     "inputs": ["Any Material"],
     "outputs": ["Ores (Primary)", "Dirt/PayDirt (Secondary)"],
     "notes": "Separates dirt and paydirt from ores"},
    {"art_nr": 400132, "name": "Shaker Screen", "category": "Sorting",
     "price": 7500, "power_kw": 55, "length_m": 6, "height_m": 4,
     "conveyor_speed": 30, "max_connections": 1, "efficiency": "1x",
     "inputs": ["Any Material"],
     "outputs": ["Rock (Primary)", "Ores/Fines (Secondary)"],
     "notes": "Separates large rock from fine materials"},
    {"art_nr": 400155, "name": "Coal Screen", "category": "Sorting",
     "price": 7500, "power_kw": 55, "length_m": 6, "height_m": 4,
     "conveyor_speed": 30, "max_connections": 1, "efficiency": "1x",
     "inputs": ["Any Material"],
     "outputs": ["Everything Else (Primary)", "Coal (Secondary)"],
     "notes": "Extracts coal from mixed materials"},
    {"art_nr": 400203, "name": "High Temp Sorter", "category": "Sorting",
     "price": 8200, "power_kw": 55, "length_m": 6, "height_m": 4,
     "conveyor_speed": 30, "max_connections": 1, "efficiency": "1x",
     "inputs": ["Any Material"],
     "outputs": ["Everything Else (Primary)", "Iron/Aluminium/Silicon Ore (Secondary)"],
     "notes": "Sorts high-temp metals"},
    {"art_nr": 400209, "name": "Metal Ore Sorter", "category": "Sorting",
     "price": 8200, "power_kw": 55, "length_m": 6, "height_m": 4,
     "conveyor_speed": 30, "max_connections": 1, "efficiency": "1x",
     "inputs": ["Any Material"],
     "outputs": ["Everything Else (Primary)", "Iron/Copper/Aluminium/Silver/Lithium Ore (Secondary)"],
     "notes": "Sorts metal ores"},
    
    # ==================== WASHING ====================
    {"art_nr": 400134, "name": "Washplant", "category": "Washing",
     "price": 7500, "power_kw": 0, "length_m": 8, "height_m": 4,
     "conveyor_speed": 30, "max_connections": 1, "efficiency": "1x",
     "inputs": ["PayDirt", "Water/Unfiltered Water"],
     "outputs": ["Dirt", "Gold/Diamond/Ruby/Silicon Ore"],
     "notes": "Extracts precious ores from paydirt"},
    {"art_nr": 400163, "name": "Sluice Box", "category": "Washing",
     "price": 7500, "power_kw": 0, "length_m": 8, "height_m": 4,
     "conveyor_speed": 30, "max_connections": 1, "efficiency": "1x",
     "inputs": ["PayDirt", "Water/Unfiltered Water"],
     "outputs": ["Dirt (Primary)", "Gold/Diamond/Ruby/Silicon Ore (Secondary)"],
     "notes": "Alternative paydirt processor"},
    {"art_nr": 400133, "name": "Froth Floater", "category": "Washing",
     "price": 7500, "power_kw": 55, "length_m": 8, "height_m": 4,
     "conveyor_speed": 30, "max_connections": 1, "efficiency": "1x",
     "inputs": ["Gravel", "Water"],
     "outputs": ["Metal Ores (Primary)", "Tailings (Secondary)"],
     "notes": "Extracts ore from gravel using flotation"},
    
    # ==================== REFINING ====================
    {"art_nr": 400205, "name": "Water Refinery", "category": "Refining",
     "price": 7800, "power_kw": 55, "length_m": 6, "height_m": 2,
     "conveyor_speed": 30, "max_connections": 1, "efficiency": "1x",
     "inputs": ["Unfiltered Water"], "outputs": ["Water"],
     "notes": "Purifies water"},
    {"art_nr": 400204, "name": "Oil Refinery", "category": "Refining",
     "price": 8400, "power_kw": 55, "length_m": 6, "height_m": 2,
     "conveyor_speed": 30, "max_connections": 1, "efficiency": "1x",
     "inputs": ["Crude Oil", "Oil", "Fuel"],
     "outputs": ["Oil", "Fuel", "Generator Fuel"],
     "notes": "Multi-stage oil processing"},
    {"art_nr": 400111, "name": "Asphalt Plant", "category": "Refining",
     "price": 7500, "power_kw": 10, "length_m": 8, "height_m": 4,
     "conveyor_speed": 30, "max_connections": 1, "efficiency": "1x",
     "inputs": ["Gravel", "Oil/Crude Oil"], "outputs": ["Asphalt"],
     "notes": "Makes asphalt for road construction"},
    
    # ==================== SMELTING ====================
    {"art_nr": 400188, "name": "Smelter", "category": "Smelting",
     "price": 10000, "power_kw": 102, "length_m": 10, "height_m": 2,
     "conveyor_speed": 30, "max_connections": 1, "efficiency": "1x",
     "inputs": ["Iron/Copper/Silver/Gold/Platinum/Lithium Ore"],
     "outputs": ["Melted Iron/Copper/Silver/Gold/Platinum/Lithium"],
     "notes": "Standard ore smelting"},
    {"art_nr": 400199, "name": "High Temp Smelter", "category": "Smelting",
     "price": 10000, "power_kw": 102, "length_m": 10, "height_m": 2,
     "conveyor_speed": 30, "max_connections": 1, "efficiency": "1x",
     "inputs": ["Iron Ore", "Aluminium Ore", "Silicon Ore"],
     "outputs": ["Melted Steel", "Melted Aluminium", "Melted Silicon"],
     "notes": "Iron → Steel (not Iron)"},
    
    # ==================== ROLLING ====================
    {"art_nr": 400189, "name": "Bar Roller", "category": "Rolling",
     "price": 10000, "power_kw": 32, "length_m": 6, "height_m": 2,
     "conveyor_speed": 30, "max_connections": 1, "efficiency": "1x",
     "inputs": ["Melted Metals"], "outputs": ["Metal Bars"],
     "notes": "All metals → bars (1:1)"},
    {"art_nr": 400193, "name": "Bloom Roller", "category": "Rolling",
     "price": 10000, "power_kw": 32, "length_m": 10, "height_m": 2,
     "conveyor_speed": 30, "max_connections": 1, "efficiency": "1x",
     "inputs": ["Melted Iron/Copper/Aluminium/Steel"],
     "outputs": ["Iron/Copper/Aluminium/Steel Bloom"],
     "notes": "For beam production"},
    {"art_nr": 400192, "name": "Coil Roller", "category": "Rolling",
     "price": 10000, "power_kw": 32, "length_m": 10, "height_m": 2,
     "conveyor_speed": 30, "max_connections": 1, "efficiency": "1x",
     "inputs": ["Melted Iron/Copper/Aluminium/Steel"],
     "outputs": ["Iron/Copper/Aluminium/Steel Coil"],
     "notes": "For sheet production"},
    {"art_nr": 400194, "name": "Rod Roller", "category": "Rolling",
     "price": 10000, "power_kw": 35, "length_m": 10, "height_m": 2,
     "conveyor_speed": 30, "max_connections": 1, "efficiency": "1x",
     "inputs": ["Melted Iron/Copper/Aluminium/Steel"],
     "outputs": ["Iron/Copper/Aluminium/Steel Rod"],
     "notes": "For rod products"},
    {"art_nr": 400196, "name": "Beam Roller", "category": "Rolling",
     "price": 8200, "power_kw": 35, "length_m": 10, "height_m": 2,
     "conveyor_speed": 30, "max_connections": 1, "efficiency": "1x",
     "inputs": ["Steel Bloom"], "outputs": ["Steel Beam"],
     "notes": "Bloom → Beam"},
    {"art_nr": 400195, "name": "Plate Shear", "category": "Rolling",
     "price": 8200, "power_kw": 35, "length_m": 10, "height_m": 2,
     "conveyor_speed": 30, "max_connections": 1, "efficiency": "1x",
     "inputs": ["Iron/Copper/Aluminium/Steel Coil"],
     "outputs": ["Iron/Copper/Aluminium/Steel Sheet"],
     "notes": "Coil → Sheet"},
]


class BuildingsSubTab(QWidget):
    """Buildings sub-tab showing factory production buildings."""
    
    data_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.all_buildings = BUILDING_DATA.copy()
        self.filtered_buildings = []
        
        self._setup_ui()
        self._load_data()
    
    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Top: Filters
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search buildings...")
        self.search_input.textChanged.connect(self._apply_filters)
        filter_layout.addWidget(self.search_input, stretch=2)
        
        filter_layout.addWidget(QLabel("Category:"))
        self.category_combo = QComboBox()
        self.category_combo.addItem("All")
        self.category_combo.currentTextChanged.connect(self._apply_filters)
        filter_layout.addWidget(self.category_combo)
        
        filter_layout.addStretch()
        
        self.count_label = QLabel("Buildings: 0")
        filter_layout.addWidget(self.count_label)
        
        layout.addLayout(filter_layout)
        
        # Main content: Splitter with table and details
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left: Building Table
        self.table = self._create_table()
        splitter.addWidget(self.table)
        
        # Right: Details Panel
        details_widget = self._create_details_panel()
        splitter.addWidget(details_widget)
        
        splitter.setSizes([650, 350])
        layout.addWidget(splitter, stretch=1)  # stretch=1 ensures it takes remaining space
    
    def _create_table(self) -> QTableWidget:
        """Create the building table."""
        table = QTableWidget()
        
        self.columns = [
            "Art.Nr",
            "Name",
            "Category",
            "Power (kW)",
            "Dimensions",
            "Price",
        ]
        
        table.setColumnCount(len(self.columns))
        table.setHorizontalHeaderLabels(self.columns)
        
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        table.setSortingEnabled(True)
        
        header = table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Name
        for i in [0, 2, 3, 4, 5]:
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        
        table.itemSelectionChanged.connect(self._on_selection_changed)
        
        return table
    
    def _create_details_panel(self) -> QWidget:
        """Create the details panel."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Summary Stats
        stats_group = QGroupBox("📊 Category Summary")
        stats_layout = QVBoxLayout(stats_group)
        
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setMaximumHeight(150)
        stats_layout.addWidget(self.stats_text)
        
        layout.addWidget(stats_group)
        
        # Selected Building Details
        details_group = QGroupBox("🏗️ Building Details & I/O")
        details_layout = QVBoxLayout(details_group)
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        details_layout.addWidget(self.details_text)
        
        layout.addWidget(details_group)
        
        return widget
    
    def _load_data(self):
        """Load buildings data."""
        # Update category dropdown
        categories = sorted(set(b["category"] for b in self.all_buildings))
        self.category_combo.blockSignals(True)
        self.category_combo.clear()
        self.category_combo.addItem("All")
        self.category_combo.addItems(categories)
        self.category_combo.blockSignals(False)
        
        self._apply_filters()
        self._update_stats()
    
    def _apply_filters(self):
        """Apply filters to building list."""
        search_text = self.search_input.text().lower().strip()
        category_filter = self.category_combo.currentText()
        
        self.filtered_buildings = []
        
        for building in self.all_buildings:
            # Search filter
            if search_text:
                if (search_text not in building["name"].lower() and 
                    search_text not in building["category"].lower()):
                    continue
            
            # Category filter
            if category_filter != "All" and building["category"] != category_filter:
                continue
            
            self.filtered_buildings.append(building)
        
        self._populate_table()
        self._update_count()
    
    def _populate_table(self):
        """Populate table with filtered buildings."""
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(self.filtered_buildings))
        
        for row, building in enumerate(self.filtered_buildings):
            # Art.Nr
            art_item = QTableWidgetItem(str(building["art_nr"]))
            art_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 0, art_item)
            
            # Name
            name_item = QTableWidgetItem(building["name"])
            self.table.setItem(row, 1, name_item)
            
            # Category
            cat_item = QTableWidgetItem(building["category"])
            self.table.setItem(row, 2, cat_item)
            
            # Power
            power = building["power_kw"]
            if power > 0:
                power_text = f"{power:.0f}"
                power_item = QTableWidgetItem(power_text)
                power_item.setForeground(QColor("#c62828"))
            else:
                power_item = QTableWidgetItem("0")
                power_item.setForeground(QColor("#2e7d32"))  # Green for no power
            power_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 3, power_item)
            
            # Dimensions
            dim_text = f"{building['length_m']:.0f}m × {building['height_m']:.0f}m"
            dim_item = QTableWidgetItem(dim_text)
            dim_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 4, dim_item)
            
            # Price
            price_item = QTableWidgetItem(f"${building['price']:,.0f}")
            price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 5, price_item)
        
        self.table.setSortingEnabled(True)
    
    def _update_count(self):
        """Update the building count label."""
        self.count_label.setText(f"Buildings: {len(self.filtered_buildings)} / {len(self.all_buildings)}")
    
    def _update_stats(self):
        """Update summary statistics."""
        # Count by category
        categories = {}
        total_power = 0
        for b in self.all_buildings:
            cat = b["category"]
            categories[cat] = categories.get(cat, 0) + 1
            total_power += b["power_kw"]
        
        html = """
        <style>
            body { font-family: sans-serif; font-size: 11px; }
            h3 { margin: 5px 0; color: #1976d2; }
            .stat { margin: 2px 0; }
        </style>
        <h3>🏭 Building Categories</h3>
        """
        
        for cat, count in sorted(categories.items()):
            html += f'<div class="stat">{cat}: {count}</div>'
        
        html += f'<div class="stat"><b>Total: {len(self.all_buildings)}</b></div>'
        html += f'<div class="stat">Total Power: {total_power:,.0f} kW</div>'
        
        self.stats_text.setHtml(html)
    
    def _on_selection_changed(self):
        """Handle table selection change."""
        selected = self.table.selectedItems()
        if not selected:
            self.details_text.clear()
            return
        
        row = selected[0].row()
        if row < 0 or row >= len(self.filtered_buildings):
            return
        
        building = self.filtered_buildings[row]
        
        html = f"""
        <style>
            body {{ font-family: sans-serif; font-size: 12px; }}
            h3 {{ margin: 5px 0; color: #1976d2; }}
            .label {{ color: #666; }}
            .value {{ font-weight: bold; }}
            .section {{ margin-top: 10px; }}
            .io {{ background: #f5f5f5; padding: 5px; margin: 3px 0; border-radius: 3px; }}
            .input {{ color: #c62828; }}
            .output {{ color: #2e7d32; }}
        </style>
        <h3>{building["name"]}</h3>
        <p><span class="label">Art.Nr:</span> <span class="value">{building["art_nr"]}</span></p>
        <p><span class="label">Category:</span> <span class="value">{building["category"]}</span></p>
        <p><span class="label">Price:</span> <span class="value">${building["price"]:,.0f}</span></p>
        <p><span class="label">Power:</span> <span class="value" style="color:{'#c62828' if building['power_kw'] > 0 else '#2e7d32'}">{building["power_kw"]} kW</span></p>
        <p><span class="label">Dimensions:</span> <span class="value">{building["length_m"]}m × {building["height_m"]}m</span></p>
        
        <div class="section">
        <h3>⬇️ Inputs</h3>
        """
        
        for inp in building.get("inputs", []):
            html += f'<div class="io input">• {inp}</div>'
        
        html += """
        <h3>⬆️ Outputs</h3>
        """
        
        for out in building.get("outputs", []):
            html += f'<div class="io output">• {out}</div>'
        
        if building.get("notes"):
            html += f'<div class="section"><p><span class="label">Notes:</span> {building["notes"]}</p></div>'
        
        self.details_text.setHtml(html)
    
    def get_building_by_name(self, name: str) -> dict:
        """Get building by name."""
        for b in self.all_buildings:
            if b["name"] == name:
                return b
        return None
