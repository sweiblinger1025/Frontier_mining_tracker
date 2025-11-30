"""
Recipes Sub-Tab - Workbench crafting recipes

Displays all crafting recipes organized by workbench.
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
    QAbstractItemView,
    QSplitter,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor


# Recipe data from Out of Ore Production Reference
RECIPE_DATA = [
    # ==================== OIL DERRICK ====================
    {"workbench": "Oil Derrick", "output": "Water", "output_qty": 1,
     "inputs": [("Empty Barrel", 1)]},
    {"workbench": "Oil Derrick", "output": "Oil", "output_qty": 1,
     "inputs": [("Empty Barrel", 1)]},
    {"workbench": "Oil Derrick", "output": "Fuel", "output_qty": 1,
     "inputs": [("Empty Barrel", 1), ("Oil", 1)]},
    
    # ==================== WOOD WORKBENCH ====================
    {"workbench": "Wood Workbench", "output": "Wood Beam", "output_qty": 1,
     "inputs": [("Tree Logs", 1)]},
    {"workbench": "Wood Workbench", "output": "Wood Plank", "output_qty": 1,
     "inputs": [("Tree Logs", 1)]},
    {"workbench": "Wood Workbench", "output": "Wood Sheet", "output_qty": 1,
     "inputs": [("Tree Logs", 1)]},
    {"workbench": "Wood Workbench", "output": "Wood Block", "output_qty": 1,
     "inputs": [("Wood Beam", 5)]},
    {"workbench": "Wood Workbench", "output": "Wood Floor", "output_qty": 1,
     "inputs": [("Wood Beam", 2), ("Wood Plank", 2)]},
    {"workbench": "Wood Workbench", "output": "Wood Wall", "output_qty": 1,
     "inputs": [("Wood Beam", 2), ("Wood Plank", 2)]},
    {"workbench": "Wood Workbench", "output": "Wood L", "output_qty": 1,
     "inputs": [("Wood Beam", 1), ("Wood Plank", 2)]},
    {"workbench": "Wood Workbench", "output": "Wood R", "output_qty": 1,
     "inputs": [("Wood Beam", 1), ("Wood Plank", 2)]},
    {"workbench": "Wood Workbench", "output": "Wood Roof", "output_qty": 1,
     "inputs": [("Wood Beam", 2), ("Wood Plank", 2)]},
    {"workbench": "Wood Workbench", "output": "Wood Roof Corner", "output_qty": 1,
     "inputs": [("Wood Beam", 2), ("Wood Plank", 2)]},
    {"workbench": "Wood Workbench", "output": "Wood Roof Corner Inv", "output_qty": 1,
     "inputs": [("Wood Beam", 2), ("Wood Plank", 2)]},
    {"workbench": "Wood Workbench", "output": "Wood Wall Inv L", "output_qty": 1,
     "inputs": [("Wood Beam", 1), ("Wood Plank", 2)]},
    {"workbench": "Wood Workbench", "output": "Wood Wall Inv R", "output_qty": 1,
     "inputs": [("Wood Beam", 1), ("Wood Plank", 2)]},
    {"workbench": "Wood Workbench", "output": "Watchtower", "output_qty": 1,
     "inputs": [("Wood Beam", 60), ("Wood Plank", 45), ("Wood Sheet", 20)],
     "notes": "Quest item"},
    
    # ==================== SMALL WASHPLANT ====================
    {"workbench": "Small Washplant", "output": "Gold Ore", "output_qty": 1,
     "inputs": [("Paydirt", 5)], "notes": "Extraction"},
    {"workbench": "Small Washplant", "output": "Diamond Ore", "output_qty": 1,
     "inputs": [("Diamond Ore", 1)], "notes": "Purification"},
    {"workbench": "Small Washplant", "output": "Ruby Ore", "output_qty": 1,
     "inputs": [("Ruby Ore", 1)], "notes": "Purification"},
    {"workbench": "Small Washplant", "output": "Cement", "output_qty": 1,
     "inputs": [("Gravel", 10)]},
    
    # ==================== CONCRETE MIXER ====================
    # Rough Concrete Elements
    {"workbench": "Concrete Mixer", "output": "Concrete Block", "output_qty": 1,
     "inputs": [("Water", 4), ("Cement", 8)],"notes": "Rough Concrete"},
    {"workbench": "Concrete Mixer", "output": "Chamfer Concrete Block", "output_qty": 1,
     "inputs": [("Water", 4), ("Cement", 8)],"notes": "Rough Concrete"},
    {"workbench": "Concrete Mixer", "output": "Concrete Floor", "output_qty": 1,
     "inputs": [("Water", 2), ("Cement", 4)],"notes": "Rough Concrete"},
    {"workbench": "Concrete Mixer", "output": "Concrete Wall", "output_qty": 1,
     "inputs": [("Water", 2), ("Cement", 4)],"notes": "Rough Concrete"},
    {"workbench": "Concrete Mixer", "output": "Concrete Cut Wall", "output_qty": 1,
     "inputs": [("Water", 2), ("Cement", 2)],"notes": "Rough Concrete"},
    {"workbench": "Concrete Mixer", "output": "Concrete Cut Wall Inv", "output_qty": 1,
     "inputs": [("Water", 2), ("Cement", 2)],"notes": "Rough Concrete"},
    {"workbench": "Concrete Mixer", "output": "Concrete Ramp 1/4", "output_qty": 1,
     "inputs": [("Water", 3), ("Cement", 7)],"notes": "Rough Concrete"},
    {"workbench": "Concrete Mixer", "output": "Concrete Ramp 2/4", "output_qty": 1,
     "inputs": [("Water", 2), ("Cement", 6)],"notes": "Rough Concrete"},
    {"workbench": "Concrete Mixer", "output": "Concrete Ramp 3/4", "output_qty": 1,
     "inputs": [("Water", 2), ("Cement", 5)],"notes": "Rough Concrete"},
    {"workbench": "Concrete Mixer", "output": "Concrete Ramp 4/4", "output_qty": 1,
     "inputs": [("Water", 2), ("Cement", 4)],"notes": "Rough Concrete"},
    {"workbench": "Concrete Mixer", "output": "Concrete Roof", "output_qty": 1,
     "inputs": [("Water", 2), ("Cement", 4)],"notes": "Rough Concrete"},
    {"workbench": "Concrete Mixer", "output": "Concrete Roof Corner", "output_qty": 1,
     "inputs": [("Water", 2), ("Cement", 4)],"notes": "Rough Concrete"},
    {"workbench": "Concrete Mixer", "output": "Concrete Roof Corner Inv", "output_qty": 1,
     "inputs": [("Water", 2), ("Cement", 4)],"notes": "Rough Concrete"},
    # Standard Concrete Elements
        {"workbench": "Concrete Mixer", "output": "Concrete Block", "output_qty": 1,
     "inputs": [("Water", 4), ("Cement", 8)],"notes": "Standard Concrete"},
    {"workbench": "Concrete Mixer", "output": "Chamfer Concrete Block", "output_qty": 1,
     "inputs": [("Water", 4), ("Cement", 8)],"notes": "Standard Concrete"},
    {"workbench": "Concrete Mixer", "output": "Concrete Floor", "output_qty": 1,
     "inputs": [("Water", 2), ("Cement", 4)],"notes": "Standard Concrete"},
    {"workbench": "Concrete Mixer", "output": "Concrete Wall", "output_qty": 1,
     "inputs": [("Water", 2), ("Cement", 4)],"notes": "Standard Concrete"},
    {"workbench": "Concrete Mixer", "output": "Concrete Cut Wall", "output_qty": 1,
     "inputs": [("Water", 2), ("Cement", 2)],"notes": "Standard Concrete"},
    {"workbench": "Concrete Mixer", "output": "Concrete Cut Wall Inv", "output_qty": 1,
     "inputs": [("Water", 2), ("Cement", 2)],"notes": "Standard Concrete"},
    {"workbench": "Concrete Mixer", "output": "Concrete Ramp 1/4", "output_qty": 1,
     "inputs": [("Water", 3), ("Cement", 7)],"notes": "Standard Concrete"},
    {"workbench": "Concrete Mixer", "output": "Concrete Ramp 2/4", "output_qty": 1,
     "inputs": [("Water", 2), ("Cement", 6)],"notes": "Standard Concrete"},
    {"workbench": "Concrete Mixer", "output": "Concrete Ramp 3/4", "output_qty": 1,
     "inputs": [("Water", 2), ("Cement", 5)],"notes": "Standard Concrete"},
    {"workbench": "Concrete Mixer", "output": "Concrete Ramp 4/4", "output_qty": 1,
     "inputs": [("Water", 2), ("Cement", 4)],"notes": "Standard Concrete"},
    {"workbench": "Concrete Mixer", "output": "Concrete Roof", "output_qty": 1,
     "inputs": [("Water", 2), ("Cement", 4)],"notes": "Standard Concrete"},
    {"workbench": "Concrete Mixer", "output": "Concrete Roof Corner", "output_qty": 1,
     "inputs": [("Water", 2), ("Cement", 4)],"notes": "Standard Concrete"},
    {"workbench": "Concrete Mixer", "output": "Concrete Roof Corner Inv", "output_qty": 1,
     "inputs": [("Water", 2), ("Cement", 4)],"notes": "Standard Concrete"},
    # Polished Concrete Elements
        {"workbench": "Concrete Mixer", "output": "Concrete Block", "output_qty": 1,
     "inputs": [("Water", 4), ("Cement", 8)],"notes": "Polished Concrete"},
    {"workbench": "Concrete Mixer", "output": "Chamfer Concrete Block", "output_qty": 1,
     "inputs": [("Water", 4), ("Cement", 8)],"notes": "Polished Concrete"},
    {"workbench": "Concrete Mixer", "output": "Concrete Floor", "output_qty": 1,
     "inputs": [("Water", 2), ("Cement", 4)],"notes": "Polished Concrete"},
    {"workbench": "Concrete Mixer", "output": "Concrete Wall", "output_qty": 1,
     "inputs": [("Water", 2), ("Cement", 4)],"notes": "Polished Concrete"},
    {"workbench": "Concrete Mixer", "output": "Concrete Cut Wall", "output_qty": 1,
     "inputs": [("Water", 2), ("Cement", 2)],"notes": "Polished Concrete"},
    {"workbench": "Concrete Mixer", "output": "Concrete Cut Wall Inv", "output_qty": 1,
     "inputs": [("Water", 2), ("Cement", 2)],"notes": "Polished Concrete"},
    {"workbench": "Concrete Mixer", "output": "Concrete Ramp 1/4", "output_qty": 1,
     "inputs": [("Water", 3), ("Cement", 7)],"notes": "Polished Concrete"},
    {"workbench": "Concrete Mixer", "output": "Concrete Ramp 2/4", "output_qty": 1,
     "inputs": [("Water", 2), ("Cement", 6)],"notes": "Polished Concrete"},
    {"workbench": "Concrete Mixer", "output": "Concrete Ramp 3/4", "output_qty": 1,
     "inputs": [("Water", 2), ("Cement", 5)],"notes": "Polished Concrete"},
    {"workbench": "Concrete Mixer", "output": "Concrete Ramp 4/4", "output_qty": 1,
     "inputs": [("Water", 2), ("Cement", 4)],"notes": "Polished Concrete"},
    {"workbench": "Concrete Mixer", "output": "Concrete Roof", "output_qty": 1,
     "inputs": [("Water", 2), ("Cement", 4)],"notes": "Polished Concrete"},
    {"workbench": "Concrete Mixer", "output": "Concrete Roof Corner", "output_qty": 1,
     "inputs": [("Water", 2), ("Cement", 4)],"notes": "Polished Concrete"},
    {"workbench": "Concrete Mixer", "output": "Concrete Roof Corner Inv", "output_qty": 1,
     "inputs": [("Water", 2), ("Cement", 4)],"notes": "Polished Concrete"},
    
    # ==================== ORE SMELTER ====================
    {"workbench": "Ore Smelter", "output": "Iron Bar", "output_qty": 1,
     "inputs": [("Iron Ore", 1)]},
    {"workbench": "Ore Smelter", "output": "Copper Bar", "output_qty": 1,
     "inputs": [("Copper Ore", 1)]},
    {"workbench": "Ore Smelter", "output": "Aluminium Bar", "output_qty": 1,
     "inputs": [("Aluminium Ore", 1)]},
    {"workbench": "Ore Smelter", "output": "Silver Bar", "output_qty": 1,
     "inputs": [("Silver Ore", 1)]},
    {"workbench": "Ore Smelter", "output": "Gold Bar", "output_qty": 1,
     "inputs": [("Gold Ore", 1)]},
    {"workbench": "Ore Smelter", "output": "Silicon Bar", "output_qty": 1,
     "inputs": [("Silicon Ore", 1)]},
    {"workbench": "Ore Smelter", "output": "Lithium Bar", "output_qty": 1,
     "inputs": [("Lithium Ore", 1)]},
    {"workbench": "Ore Smelter", "output": "Steel Bar", "output_qty": 1,
     "inputs": [("Iron Bar", 1), ("Coal", 1)]},
    {"workbench": "Ore Smelter", "output": "Plastics", "output_qty": 1,
     "inputs": [("Oil", 1)]},
    {"workbench": "Ore Smelter", "output": "Rubber", "output_qty": 1,
     "inputs": [("Silicon Bar", 1), ("Coal", 1)]},
    
    # ==================== STEEL ROLLER ====================
    {"workbench": "Steel Roller", "output": "Steel Beam", "output_qty": 1,
     "inputs": [("Steel Bar", 1)]},
    {"workbench": "Steel Roller", "output": "Steel Plate", "output_qty": 1,
     "inputs": [("Steel Bar", 1)]},
    {"workbench": "Steel Roller", "output": "Steel Rod", "output_qty": 1,
     "inputs": [("Steel Bar", 1)]},
    {"workbench": "Steel Roller", "output": "Empty Barrel", "output_qty": 1,
     "inputs": [("Iron Bar", 1)]},
    
    # ==================== STEEL PRESS ====================
    {"workbench": "Steel Press", "output": "Wearplate", "output_qty": 1,
     "inputs": [("Steel Bar", 2)]},
    
    # ==================== CNC CUTTER ====================
    # Mesh building elements
    {"workbench": "CNC Cutter", "output": "Steel Mesh Ceiling", "output_qty": 1,
     "inputs": [("Steel Rod", 4), ("Bolts & Nuts", 4)]},
    {"workbench": "CNC Cutter", "output": "Steel Mesh Roof", "output_qty": 1,
     "inputs": [("Steel Rod", 4), ("Bolts & Nuts", 4)]},
    {"workbench": "CNC Cutter", "output": "Steel Mesh Wall", "output_qty": 1,
     "inputs": [("Steel Rod", 4), ("Bolts & Nuts", 4)]},
    {"workbench": "CNC Cutter", "output": "Steel Mesh Wall L", "output_qty": 1,
     "inputs": [("Steel Rod", 2), ("Bolts & Nuts", 3)]},
    {"workbench": "CNC Cutter", "output": "Steel Mesh Wall R", "output_qty": 1,
     "inputs": [("Steel Rod", 2), ("Bolts & Nuts", 3)]},
    # Basic building elements
    {"workbench": "CNC Cutter", "output": "Steel Block", "output_qty": 1,
     "inputs": [("Steel Beam", 8), ("Bolts & Nuts", 4)]},
    {"workbench": "CNC Cutter", "output": "Steel Ceiling", "output_qty": 1,
     "inputs": [("Steel Beam", 4), ("Steel Plate", 4), ("Bolts & Nuts", 2)]},
    {"workbench": "CNC Cutter", "output": "Steel Floor", "output_qty": 1,
     "inputs": [("Steel Beam", 4), ("Steel Plate", 4), ("Bolts & Nuts", 2)]},
    # Doors
    {"workbench": "CNC Cutter", "output": "Small Door", "output_qty": 1,
     "inputs": [("Steel Beam", 2), ("Steel Plate", 3)]},
    {"workbench": "CNC Cutter", "output": "Massive Door", "output_qty": 1,
     "inputs": [("Steel Beam", 2), ("Steel Plate", 6), ("Bolts & Nuts", 8)]},
    # Structural
    {"workbench": "CNC Cutter", "output": "Steel Staircase", "output_qty": 1,
     "inputs": [("Steel Beam", 2), ("Steel Plate", 3), ("Steel Rod", 2), ("Bolts & Nuts", 2)]},
    {"workbench": "CNC Cutter", "output": "Steel Railing", "output_qty": 1,
     "inputs": [("Steel Rod", 2)]},
    # Walls
    {"workbench": "CNC Cutter", "output": "Steel Wall", "output_qty": 1,
     "inputs": [("Steel Beam", 4), ("Steel Plate", 4), ("Bolts & Nuts", 2)]},
    {"workbench": "CNC Cutter", "output": "Steel Wall Cut", "output_qty": 1,
     "inputs": [("Steel Beam", 2), ("Steel Plate", 2), ("Bolts & Nuts", 2)]},
    {"workbench": "CNC Cutter", "output": "Steel Wall Cut Inv", "output_qty": 1,
     "inputs": [("Steel Beam", 2), ("Steel Plate", 2), ("Bolts & Nuts", 2)]},
    # Corners & Roof
    {"workbench": "CNC Cutter", "output": "Steel Roof", "output_qty": 1,
     "inputs": [("Steel Beam", 4), ("Steel Plate", 4), ("Bolts & Nuts", 2)]},
    {"workbench": "CNC Cutter", "output": "Steel Roof Corner", "output_qty": 1,
     "inputs": [("Steel Beam", 4), ("Steel Plate", 4), ("Bolts & Nuts", 2)]},
    {"workbench": "CNC Cutter", "output": "Steel Roof Corner Inv", "output_qty": 1,
     "inputs": [("Steel Beam", 4), ("Steel Plate", 4), ("Bolts & Nuts", 2)]},
    # Windows
    {"workbench": "CNC Cutter", "output": "Steel Window", "output_qty": 1,
     "inputs": [("Steel Beam", 2)]},
    # Quest
    {"workbench": "CNC Cutter", "output": "Cell Tower", "output_qty": 1,
     "inputs": [("Steel Beam", 40), ("Steel Plate", 10), ("Steel Rod", 20), ("Bolts & Nuts", 10), ("Electronic Parts", 30)],
     "notes": "Quest item"},
    
    # ==================== CNC MILL ====================
    # Built Parts
    {"workbench": "CNC Mill", "output": "Built Battery", "output_qty": 1,
     "inputs": [("Plastic", 1), ("Lithium", 3)]},
    {"workbench": "CNC Mill", "output": "Built ECU", "output_qty": 1,
     "inputs": [("Electronic Parts", 2), ("Aluminum", 1)]},
    {"workbench": "CNC Mill", "output": " Built Filter kit", "output_qty": 1,
     "inputs": [("Plastic", 1), ("Steel", 2)]},
    {"workbench": "CNC Mill", "output": "Built Hydraulic Hose", "output_qty": 1,
     "inputs": [("Rubber", 2), ("Steel", 1)]},
    {"workbench": "CNC Mill", "output": "Built Hydraulic Pump", "output_qty": 1,
     "inputs": [("Steel", 3), ("Large Drive Axle", 1), ("Gear", 2), ("Bearing", 2)]},
    {"workbench": "CNC Mill", "output": "Built Injector", "output_qty": 1,
     "inputs": [("Rubber", 2), ("Steel", 2)]},
    {"workbench": "CNC Mill", "output": "Built Turbo", "output_qty": 1,
     "inputs": [("Steel", 5), ("Aluminum", 5), ("Steel Rod", 1), ("Bearing", 2)]},
    {"workbench": "CNC Mill", "output": " Built Wearplate", "output_qty": 1,
     "inputs": [("Wearplate", 1), ("Bolts & Nuts", 1)]},
    {"workbench": "CNC Mill", "output": "Built Ram", "output_qty": 1,
     "inputs": [("Oil", 1), ("Steel", 4), ("Steel Rod", 1)]},
    {"workbench": "CNC Mill", "output": "Built Sensor", "output_qty": 1,
     "inputs": [("Plastic", 1), ("Steel", 1), ("Electronic Parts", 1)]},
    #Sub Parts
    {"workbench": "CNC Mill", "output": "Engine Head", "output_qty": 1,
     "inputs": [("Iron", 20)]},
    {"workbench": "CNC Mill", "output": "Small gearbox", "output_qty": 1,
     "inputs": [("Steel", 3), ("Gear", 4), ("Aluminum", 4)]},
    {"workbench": "CNC Mill", "output": "Electric Motor", "output_qty": 1,
     "inputs": [("Electronic Parts", 1), ("Steel", 5), ("Gear", 2)]},
    {"workbench": "CNC Mill", "output": "Gearbox", "output_qty": 1,
     "inputs": [("Gear", 2), ("Aluminum", 3)]},
    {"workbench": "CNC Mill", "output": "Stepper Motor", "output_qty": 1,
     "inputs": [("Electronic Parts", 2), ("Steel", 1), ("Gear", 1)]},
    {"workbench": "CNC Mill", "output": "Cam Axle", "output_qty": 1,
     "inputs": [("Steel", 1), ("Steel Rod", 1)]},
    {"workbench": "CNC Mill", "output": "Piston Rod", "output_qty": 1,
     "inputs": [("Steel", 2)]},
    {"workbench": "CNC Mill", "output": "Cable", "output_qty": 1,
     "inputs": [("Rubber", 2), ("Copper", 2)]},
    {"workbench": "CNC Mill", "output": "Bearing", "output_qty": 1,
     "inputs": [("Steel", 1)]},
    {"workbench": "CNC Mill", "output": "Gear", "output_qty": 1,
     "inputs": [("Steel", 1)]},
    {"workbench": "CNC Mill", "output": "Large Drive Axle", "output_qty": 1,
     "inputs": [("Steel Rod", 1)]},
    {"workbench": "CNC Mill", "output": "Chain", "output_qty": 1,
     "inputs": [("Steel", 2)]},
    {"workbench": "CNC Mill", "output": "Gear Axle", "output_qty": 1,
     "inputs": [("Gear", 1), ("Steel Rod", 1)]},
    {"workbench": "CNC Mill", "output": "Bolts & Nuts", "output_qty": 1,
     "inputs": [("Steel", 1)]},
    {"workbench": "CNC Mill", "output": "Electronic Parts", "output_qty": 1,
     "inputs": [("Plastic", 1), ("Copper", 1)]},
    # Quest
    {"workbench": "CNC Mill", "output": "Radio Array", "output_qty": 1,
     "inputs": [("Electronic Parts", 210), ("Steel Beam", 300), ("Steel Rod", 40), ("Steel Plate", 75)],
     "notes": "Quest item"},
]


class RecipesSubTab(QWidget):
    """Recipes sub-tab showing workbench crafting recipes."""
    
    data_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.all_recipes = RECIPE_DATA.copy()
        self.filtered_recipes = []
        
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
        self.search_input.setPlaceholderText("Search recipes or ingredients...")
        self.search_input.textChanged.connect(self._apply_filters)
        filter_layout.addWidget(self.search_input, stretch=2)
        
        filter_layout.addWidget(QLabel("Workbench:"))
        self.workbench_combo = QComboBox()
        self.workbench_combo.addItem("All")
        self.workbench_combo.currentTextChanged.connect(self._apply_filters)
        filter_layout.addWidget(self.workbench_combo)
        
        filter_layout.addStretch()
        
        self.count_label = QLabel("Recipes: 0")
        filter_layout.addWidget(self.count_label)
        
        layout.addLayout(filter_layout)
        
        # Main content: Splitter with table and details
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left: Recipe Table
        self.table = self._create_table()
        splitter.addWidget(self.table)
        
        # Right: Details Panel
        details_widget = self._create_details_panel()
        splitter.addWidget(details_widget)
        
        splitter.setSizes([600, 400])
        layout.addWidget(splitter, stretch=1)  # stretch=1 ensures it takes remaining space
    
    def _create_table(self) -> QTableWidget:
        """Create the recipe table."""
        table = QTableWidget()
        
        self.columns = [
            "Output",
            "Qty",
            "Workbench",
            "Ingredients",
        ]
        
        table.setColumnCount(len(self.columns))
        table.setHorizontalHeaderLabels(self.columns)
        
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        table.setSortingEnabled(True)
        
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Output
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Qty
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Workbench
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # Ingredients
        
        table.itemSelectionChanged.connect(self._on_selection_changed)
        
        return table
    
    def _create_details_panel(self) -> QWidget:
        """Create the details panel."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Workbench Summary
        stats_group = QGroupBox("📊 Workbench Summary")
        stats_layout = QVBoxLayout(stats_group)
        
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setMaximumHeight(180)
        stats_layout.addWidget(self.stats_text)
        
        layout.addWidget(stats_group)
        
        # Selected Recipe Details
        details_group = QGroupBox("📋 Recipe Details")
        details_layout = QVBoxLayout(details_group)
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        details_layout.addWidget(self.details_text)
        
        layout.addWidget(details_group)
        
        return widget
    
    def _load_data(self):
        """Load recipe data."""
        # Update workbench dropdown
        workbenches = sorted(set(r["workbench"] for r in self.all_recipes))
        self.workbench_combo.blockSignals(True)
        self.workbench_combo.clear()
        self.workbench_combo.addItem("All")
        self.workbench_combo.addItems(workbenches)
        self.workbench_combo.blockSignals(False)
        
        self._apply_filters()
        self._update_stats()
    
    def _apply_filters(self):
        """Apply filters to recipe list."""
        search_text = self.search_input.text().lower().strip()
        workbench_filter = self.workbench_combo.currentText()
        
        self.filtered_recipes = []
        
        for recipe in self.all_recipes:
            # Workbench filter
            if workbench_filter != "All" and recipe["workbench"] != workbench_filter:
                continue
            
            # Search filter - check output and all inputs
            if search_text:
                found = False
                if search_text in recipe["output"].lower():
                    found = True
                else:
                    for inp_name, _ in recipe["inputs"]:
                        if search_text in inp_name.lower():
                            found = True
                            break
                if not found:
                    continue
            
            self.filtered_recipes.append(recipe)
        
        self._populate_table()
        self._update_count()
    
    def _populate_table(self):
        """Populate table with filtered recipes."""
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(self.filtered_recipes))
        
        for row, recipe in enumerate(self.filtered_recipes):
            # Output
            output_item = QTableWidgetItem(recipe["output"])
            output_item.setForeground(QColor("#2e7d32"))
            self.table.setItem(row, 0, output_item)
            
            # Qty
            qty_item = QTableWidgetItem(str(recipe["output_qty"]))
            qty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 1, qty_item)
            
            # Workbench
            wb_item = QTableWidgetItem(recipe["workbench"])
            self.table.setItem(row, 2, wb_item)
            
            # Ingredients (formatted)
            ingredients = ", ".join([f"{qty}× {name}" for name, qty in recipe["inputs"]])
            ing_item = QTableWidgetItem(ingredients)
            ing_item.setForeground(QColor("#666"))
            self.table.setItem(row, 3, ing_item)
        
        self.table.setSortingEnabled(True)
    
    def _update_count(self):
        """Update the recipe count label."""
        self.count_label.setText(f"Recipes: {len(self.filtered_recipes)} / {len(self.all_recipes)}")
    
    def _update_stats(self):
        """Update workbench summary statistics."""
        # Count by workbench
        workbenches = {}
        for r in self.all_recipes:
            wb = r["workbench"]
            workbenches[wb] = workbenches.get(wb, 0) + 1
        
        html = """
        <style>
            body { font-family: sans-serif; font-size: 11px; }
            h3 { margin: 5px 0; color: #1976d2; }
            .stat { margin: 2px 0; }
        </style>
        <h3>🔧 Workbenches</h3>
        """
        
        for wb, count in sorted(workbenches.items()):
            html += f'<div class="stat">{wb}: {count} recipes</div>'
        
        html += f'<div class="stat"><b>Total: {len(self.all_recipes)} recipes</b></div>'
        
        self.stats_text.setHtml(html)
    
    def _on_selection_changed(self):
        """Handle table selection change."""
        selected = self.table.selectedItems()
        if not selected:
            self.details_text.clear()
            return
        
        row = selected[0].row()
        if row < 0 or row >= len(self.filtered_recipes):
            return
        
        recipe = self.filtered_recipes[row]
        
        html = f"""
        <style>
            body {{ font-family: sans-serif; font-size: 12px; }}
            h3 {{ margin: 5px 0; color: #1976d2; }}
            .label {{ color: #666; }}
            .value {{ font-weight: bold; }}
            .section {{ margin-top: 10px; }}
            .ingredient {{ background: #fff3e0; padding: 5px; margin: 3px 0; border-radius: 3px; border-left: 3px solid #ff9800; }}
            .output {{ background: #e8f5e9; padding: 8px; margin: 5px 0; border-radius: 3px; border-left: 3px solid #4caf50; font-size: 14px; }}
        </style>
        
        <h3>{recipe["workbench"]}</h3>
        
        <div class="output">
            <span class="label">Output:</span> <span class="value" style="color:#2e7d32">{recipe["output_qty"]}× {recipe["output"]}</span>
        </div>
        
        <div class="section">
        <h3>📥 Required Ingredients</h3>
        """
        
        for inp_name, inp_qty in recipe["inputs"]:
            html += f'<div class="ingredient">{inp_qty}× {inp_name}</div>'
        
        # Calculate total materials
        total_items = sum(qty for _, qty in recipe["inputs"])
        html += f'<div class="section"><span class="label">Total items needed:</span> <span class="value">{total_items}</span></div>'
        
        if recipe.get("notes"):
            html += f'<div class="section"><span class="label">Notes:</span> {recipe["notes"]}</div>'
        
        self.details_text.setHtml(html)
    
    def get_recipe_by_output(self, output_name: str) -> list:
        """Get all recipes that produce the given output."""
        return [r for r in self.all_recipes if r["output"] == output_name]
    
    def get_recipes_using_input(self, input_name: str) -> list:
        """Get all recipes that use the given input."""
        result = []
        for r in self.all_recipes:
            for inp_name, _ in r["inputs"]:
                if inp_name == input_name:
                    result.append(r)
                    break
        return result
