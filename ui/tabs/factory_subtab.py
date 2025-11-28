"""
Factory Equipment Sub-Tab - Conveyors, Power, and Pipelines

Displays all factory equipment with specifications and analysis.
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
    QApplication,
    QTabWidget,
    QSplitter,
    QTextEdit,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor

from core.database import get_database
from core.models import FactoryEquipment


# Factory Equipment Data - extracted from game screenshots
FACTORY_EQUIPMENT_DATA = [
    # ==================== CONVEYORS ====================
    # Straight Conveyors
    {"art_nr": 400112, "name": "Straight 2m", "category": "Conveyor", "subcategory": "Straight",
     "length_m": 2, "height_m": 2, "conveyor_speed": 30, "power_consumption_kw": 18, "price": 1500},
    {"art_nr": 400113, "name": "Straight 4m", "category": "Conveyor", "subcategory": "Straight",
     "length_m": 4, "height_m": 2, "conveyor_speed": 30, "power_consumption_kw": 26, "price": 2500},
    {"art_nr": 400114, "name": "Straight 6m", "category": "Conveyor", "subcategory": "Straight",
     "length_m": 6, "height_m": 2, "conveyor_speed": 30, "power_consumption_kw": 34, "price": 3500},
    {"art_nr": 400115, "name": "Straight 8m", "category": "Conveyor", "subcategory": "Straight",
     "length_m": 8, "height_m": 2, "conveyor_speed": 30, "power_consumption_kw": 42, "price": 4500},
    
    # Up Conveyors
    {"art_nr": 400116, "name": "Up 4x4", "category": "Conveyor", "subcategory": "Up",
     "length_m": 4, "height_m": 4, "conveyor_speed": 30, "power_consumption_kw": 42, "price": 4500},
    {"art_nr": 400117, "name": "Up 8x4", "category": "Conveyor", "subcategory": "Up",
     "length_m": 8, "height_m": 4, "conveyor_speed": 30, "power_consumption_kw": 42, "price": 4500},
    {"art_nr": 400118, "name": "Up 8x6", "category": "Conveyor", "subcategory": "Up",
     "length_m": 8, "height_m": 6, "conveyor_speed": 30, "power_consumption_kw": 42, "price": 4500},
    
    # Down Conveyors
    {"art_nr": 400119, "name": "Down 4x4", "category": "Conveyor", "subcategory": "Down",
     "length_m": 4, "height_m": 4, "conveyor_speed": 30, "power_consumption_kw": 42, "price": 4500},
    {"art_nr": 400120, "name": "Down 8x4", "category": "Conveyor", "subcategory": "Down",
     "length_m": 8, "height_m": 4, "conveyor_speed": 30, "power_consumption_kw": 42, "price": 4500},
    {"art_nr": 400121, "name": "Down 8x6", "category": "Conveyor", "subcategory": "Down",
     "length_m": 8, "height_m": 6, "conveyor_speed": 30, "power_consumption_kw": 42, "price": 4500},
    
    # Offset Conveyors
    {"art_nr": 400122, "name": "Offset Left 4m", "category": "Conveyor", "subcategory": "Offset",
     "length_m": 8, "height_m": 2, "conveyor_speed": 30, "power_consumption_kw": 42, "price": 4500},
    {"art_nr": 400123, "name": "Offset Right 4m", "category": "Conveyor", "subcategory": "Offset",
     "length_m": 8, "height_m": 2, "conveyor_speed": 30, "power_consumption_kw": 42, "price": 4500},
    
    # Turn Conveyors
    {"art_nr": 400124, "name": "Left 2x", "category": "Conveyor", "subcategory": "Turn",
     "length_m": 4, "height_m": 2, "conveyor_speed": 30, "power_consumption_kw": 34, "price": 4500},
    {"art_nr": 400125, "name": "Right 2x", "category": "Conveyor", "subcategory": "Turn",
     "length_m": 2, "height_m": 2, "conveyor_speed": 30, "power_consumption_kw": 34, "price": 4500},
    
    # Hoppers
    {"art_nr": 400127, "name": "Hopper", "category": "Conveyor", "subcategory": "Hopper",
     "length_m": 4, "height_m": 2, "conveyor_speed": 30, "power_consumption_kw": 26, "price": 4500},
    {"art_nr": 400126, "name": "Big Hopper", "category": "Conveyor", "subcategory": "Hopper",
     "length_m": 8, "height_m": 2, "conveyor_speed": 30, "power_consumption_kw": 42, "price": 4500},
    {"art_nr": 400164, "name": "Big Hopper Dual Outputs", "category": "Conveyor", "subcategory": "Hopper",
     "length_m": 8, "height_m": 2, "conveyor_speed": 60, "power_consumption_kw": 84, "price": 9800,
     "notes": "Double speed and power"},
    
    # Special Conveyors
    {"art_nr": 400128, "name": "Chute", "category": "Conveyor", "subcategory": "Special",
     "length_m": 1, "height_m": 4, "conveyor_speed": 30, "power_consumption_kw": 5, "price": 1500,
     "notes": "Gravity-fed, 320m³/h at 1x"},
    {"art_nr": 400162, "name": "Elevator 8m", "category": "Conveyor", "subcategory": "Special",
     "length_m": 2, "height_m": 8, "conveyor_speed": 30, "power_consumption_kw": 42, "price": 4500,
     "notes": "Vertical lift"},
    {"art_nr": 400135, "name": "Merger", "category": "Conveyor", "subcategory": "Flow Control",
     "length_m": 6, "height_m": 2, "conveyor_speed": 30, "power_consumption_kw": 42, "price": 5500,
     "notes": "Combines 2 inputs"},
    {"art_nr": 400136, "name": "Splitter", "category": "Conveyor", "subcategory": "Flow Control",
     "length_m": 2, "height_m": 2, "conveyor_speed": 30, "power_consumption_kw": 18, "price": 5500,
     "notes": "Splits to 2 outputs"},
    {"art_nr": 400147, "name": "Storage", "category": "Conveyor", "subcategory": "Special",
     "length_m": 6, "height_m": 2, "conveyor_speed": 30, "power_consumption_kw": 10, "price": 6500,
     "notes": "Buffer storage"},
    {"art_nr": 400156, "name": "Dump Deck", "category": "Conveyor", "subcategory": "Special",
     "length_m": 0, "height_m": 0, "conveyor_speed": 0, "power_consumption_kw": 0, "price": 2500,
     "notes": "Passive platform"},
    
    # ==================== POWER GENERATION ====================
    # Fuel Generators
    {"art_nr": 400137, "name": "Power Generator 1600kW", "category": "Power", "subcategory": "Generator",
     "power_generated_kw": 1600, "max_connections": 1, "fuel_type": "Generator Fuel", "price": 15000},
    {"art_nr": 400138, "name": "Power Generator 2200kW", "category": "Power", "subcategory": "Generator",
     "power_generated_kw": 2200, "max_connections": 1, "fuel_type": "Generator Fuel", "price": 22000},
    {"art_nr": 400139, "name": "Power Generator 2800kW", "category": "Power", "subcategory": "Generator",
     "power_generated_kw": 2800, "max_connections": 1, "fuel_type": "Generator Fuel", "price": 32000},
    
    # Coal Plants
    {"art_nr": 400190, "name": "Coal Plant 3600kW", "category": "Power", "subcategory": "Coal Plant",
     "power_generated_kw": 3600, "max_connections": 1, "fuel_type": "Coal", "price": 10000},
    {"art_nr": 400201, "name": "Coal Plant 4200kW", "category": "Power", "subcategory": "Coal Plant",
     "power_generated_kw": 4200, "max_connections": 1, "fuel_type": "Coal", "price": 17500},
    
    # Solar Panels
    {"art_nr": 400148, "name": "Solar Panel 300kW", "category": "Power", "subcategory": "Solar",
     "power_generated_kw": 300, "max_connections": 1, "fuel_type": "Sun", "price": 18900,
     "notes": "Weather dependent"},
    {"art_nr": 400149, "name": "Solar Panel 500kW", "category": "Power", "subcategory": "Solar",
     "power_generated_kw": 500, "max_connections": 1, "fuel_type": "Sun", "price": 31500,
     "notes": "Weather dependent"},
    {"art_nr": 400150, "name": "Solar Panel 700kW", "category": "Power", "subcategory": "Solar",
     "power_generated_kw": 700, "max_connections": 1, "fuel_type": "Sun", "price": 44100,
     "notes": "Weather dependent"},
    
    # Wind Turbines
    {"art_nr": 400151, "name": "Wind Turbine 800kW", "category": "Power", "subcategory": "Wind",
     "power_generated_kw": 800, "max_connections": 1, "fuel_type": "Wind", "price": 50400,
     "notes": "Weather dependent"},
    {"art_nr": 400152, "name": "Wind Turbine 1200kW", "category": "Power", "subcategory": "Wind",
     "power_generated_kw": 1200, "max_connections": 1, "fuel_type": "Wind", "price": 75600,
     "notes": "Weather dependent"},
    {"art_nr": 400153, "name": "Wind Turbine 1800kW", "category": "Power", "subcategory": "Wind",
     "power_generated_kw": 1800, "max_connections": 1, "fuel_type": "Wind", "price": 113400,
     "notes": "Weather dependent"},
    
    # ==================== POWER INPUT (Speed Boosters) ====================
    {"art_nr": 400140, "name": "Power Input 1x Speed", "category": "Power", "subcategory": "Power Input",
     "length_m": 2, "height_m": 2, "conveyor_speed": 30, "power_consumption_kw": 100,
     "power_efficiency": "1x", "price": 1500},
    {"art_nr": 400141, "name": "Power Input 2x Speed", "category": "Power", "subcategory": "Power Input",
     "length_m": 2, "height_m": 2, "conveyor_speed": 30, "power_consumption_kw": 150,
     "power_efficiency": "2x", "price": 15000},
    {"art_nr": 400142, "name": "Power Input 3x Speed", "category": "Power", "subcategory": "Power Input",
     "length_m": 2, "height_m": 2, "conveyor_speed": 30, "power_consumption_kw": 200,
     "power_efficiency": "3x", "price": 25000},
    {"art_nr": 400165, "name": "Power Input 5x Speed", "category": "Power", "subcategory": "Power Input",
     "length_m": 2, "height_m": 2, "conveyor_speed": 30, "power_consumption_kw": 300,
     "power_efficiency": "5x", "price": 55000},
    {"art_nr": 400166, "name": "Power Input 10x Speed", "category": "Power", "subcategory": "Power Input",
     "length_m": 2, "height_m": 2, "conveyor_speed": 30, "power_consumption_kw": 600,
     "power_efficiency": "10x", "price": 125000},
    
    # ==================== POWER PYLONS - Freestanding ====================
    {"art_nr": 400143, "name": "Power Pylon 600kW", "category": "Power", "subcategory": "Pylon",
     "max_capacity_kw": 600, "max_connections": 5, "price": 150},
    {"art_nr": 400144, "name": "Power Pylon 1400kW", "category": "Power", "subcategory": "Pylon",
     "max_capacity_kw": 1400, "max_connections": 5, "price": 3500},
    {"art_nr": 400145, "name": "Power Pylon 3600kW", "category": "Power", "subcategory": "Pylon",
     "max_capacity_kw": 3600, "max_connections": 5, "price": 8200},
    {"art_nr": 400200, "name": "Power Pylon 5400kW", "category": "Power", "subcategory": "Pylon",
     "max_capacity_kw": 5400, "max_connections": 5, "price": 12000},
    
    # Power Pylons - Wall Mounted
    {"art_nr": 400157, "name": "Power Pylon 600kW (Wall)", "category": "Power", "subcategory": "Pylon (Wall)",
     "max_capacity_kw": 600, "max_connections": 5, "price": 120, "notes": "Wall mounted, 20% cheaper"},
    {"art_nr": 400158, "name": "Power Pylon 1400kW (Wall)", "category": "Power", "subcategory": "Pylon (Wall)",
     "max_capacity_kw": 1400, "max_connections": 5, "price": 2800, "notes": "Wall mounted, 20% cheaper"},
    {"art_nr": 400159, "name": "Power Pylon 3600kW (Wall)", "category": "Power", "subcategory": "Pylon (Wall)",
     "max_capacity_kw": 3600, "max_connections": 5, "price": 8000, "notes": "Wall mounted"},
    {"art_nr": 400206, "name": "Power Pylon 5400kW (Wall)", "category": "Power", "subcategory": "Pylon (Wall)",
     "max_capacity_kw": 5400, "max_connections": 5, "price": 11000, "notes": "Wall mounted"},
    
    # Power Infrastructure
    {"art_nr": 400146, "name": "Power Cable", "category": "Power", "subcategory": "Infrastructure",
     "price": 10, "notes": "Connects equipment"},
    {"art_nr": 400160, "name": "Wall Mounted Light", "category": "Power", "subcategory": "Infrastructure",
     "power_consumption_kw": 10, "max_connections": 2, "price": 1500, "notes": "Lighting"},
    
    # ==================== PIPELINE ====================
    # Straight Pipes
    {"art_nr": 400167, "name": "Pipe Straight 2m", "category": "Pipeline", "subcategory": "Straight",
     "length_m": 2, "height_m": 2, "conveyor_speed": 30, "power_consumption_kw": 0, "price": 1500},
    {"art_nr": 400168, "name": "Pipe Straight 4m", "category": "Pipeline", "subcategory": "Straight",
     "length_m": 4, "height_m": 2, "conveyor_speed": 30, "power_consumption_kw": 0, "price": 2500},
    {"art_nr": 400169, "name": "Pipe Straight 6m", "category": "Pipeline", "subcategory": "Straight",
     "length_m": 6, "height_m": 2, "conveyor_speed": 30, "power_consumption_kw": 0, "price": 3500},
    {"art_nr": 400170, "name": "Pipe Straight 8m", "category": "Pipeline", "subcategory": "Straight",
     "length_m": 8, "height_m": 2, "conveyor_speed": 30, "power_consumption_kw": 0, "price": 4500},
    
    # Up Pipes
    {"art_nr": 400171, "name": "Pipe Up 4x4", "category": "Pipeline", "subcategory": "Up",
     "length_m": 4, "height_m": 4, "conveyor_speed": 30, "power_consumption_kw": 0, "price": 4500},
    {"art_nr": 400172, "name": "Pipe Up 8x4", "category": "Pipeline", "subcategory": "Up",
     "length_m": 8, "height_m": 4, "conveyor_speed": 30, "power_consumption_kw": 0, "price": 4500},
    {"art_nr": 400173, "name": "Pipe Up 8x6", "category": "Pipeline", "subcategory": "Up",
     "length_m": 8, "height_m": 6, "conveyor_speed": 30, "power_consumption_kw": 0, "price": 4500},
    
    # Down Pipes
    {"art_nr": 400174, "name": "Pipe Down 4x4", "category": "Pipeline", "subcategory": "Down",
     "length_m": 4, "height_m": 4, "conveyor_speed": 30, "power_consumption_kw": 0, "price": 4500},
    {"art_nr": 400175, "name": "Pipe Down 8x4", "category": "Pipeline", "subcategory": "Down",
     "length_m": 8, "height_m": 4, "conveyor_speed": 30, "power_consumption_kw": 0, "price": 4500},
    {"art_nr": 400176, "name": "Pipe Down 8x6", "category": "Pipeline", "subcategory": "Down",
     "length_m": 8, "height_m": 6, "conveyor_speed": 30, "power_consumption_kw": 0, "price": 4500},
    
    # Turn Pipes
    {"art_nr": 400179, "name": "Pipe Left 2m", "category": "Pipeline", "subcategory": "Turn",
     "length_m": 2, "height_m": 2, "conveyor_speed": 30, "power_consumption_kw": 0, "price": 4500},
    {"art_nr": 400180, "name": "Pipe Right 2m", "category": "Pipeline", "subcategory": "Turn",
     "length_m": 0, "height_m": 2, "conveyor_speed": 30, "power_consumption_kw": 0, "price": 4500},
    
    # Offset Pipes
    {"art_nr": 400185, "name": "Pipe Offset Left", "category": "Pipeline", "subcategory": "Offset",
     "length_m": 4, "height_m": 2, "conveyor_speed": 30, "power_consumption_kw": 0, "price": 2500},
    {"art_nr": 400184, "name": "Pipe Offset Right", "category": "Pipeline", "subcategory": "Offset",
     "length_m": 4, "height_m": 2, "conveyor_speed": 30, "power_consumption_kw": 0, "price": 2500},
    
    # Flow Control
    {"art_nr": 400177, "name": "Pipe Splitter", "category": "Pipeline", "subcategory": "Flow Control",
     "length_m": 2, "height_m": 2, "conveyor_speed": 30, "power_consumption_kw": 0, "price": 5500,
     "notes": "Split to 2 outputs"},
    {"art_nr": 400178, "name": "Pipe Merger", "category": "Pipeline", "subcategory": "Flow Control",
     "length_m": 2, "height_m": 2, "conveyor_speed": 30, "power_consumption_kw": 0, "price": 5500,
     "notes": "Merge from 2 inputs"},
    
    # Storage
    {"art_nr": 400202, "name": "Liquid Tank", "category": "Pipeline", "subcategory": "Storage",
     "length_m": 6, "height_m": 2, "conveyor_speed": 30, "power_consumption_kw": 0, "price": 6500,
     "notes": "Stores water or oil"},
]


class FactoryEquipmentSubTab(QWidget):
    """Factory Equipment sub-tab showing conveyors, power, and pipelines."""
    
    data_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = get_database()
        self.all_equipment: list[FactoryEquipment] = []
        self.filtered_equipment: list[FactoryEquipment] = []
        
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
        self.search_input.setPlaceholderText("Search equipment...")
        self.search_input.textChanged.connect(self._apply_filters)
        filter_layout.addWidget(self.search_input, stretch=2)
        
        filter_layout.addWidget(QLabel("Category:"))
        self.category_combo = QComboBox()
        self.category_combo.addItems(["All", "Conveyor", "Power", "Pipeline"])
        self.category_combo.currentTextChanged.connect(self._apply_filters)
        filter_layout.addWidget(self.category_combo)
        
        filter_layout.addWidget(QLabel("Subcategory:"))
        self.subcategory_combo = QComboBox()
        self.subcategory_combo.addItem("All")
        self.subcategory_combo.currentTextChanged.connect(self._apply_filters)
        filter_layout.addWidget(self.subcategory_combo)
        
        filter_layout.addStretch()
        
        self.count_label = QLabel("Items: 0")
        filter_layout.addWidget(self.count_label)
        
        self.load_data_btn = QPushButton("🔄 Load Default Data")
        self.load_data_btn.setToolTip("Load factory equipment data from built-in database")
        self.load_data_btn.clicked.connect(self._load_default_data)
        filter_layout.addWidget(self.load_data_btn)
        
        layout.addLayout(filter_layout)
        
        # Main content: Splitter with table and analysis
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left: Equipment Table
        self.table = self._create_table()
        splitter.addWidget(self.table)
        
        # Right: Analysis Panel
        analysis_widget = self._create_analysis_panel()
        splitter.addWidget(analysis_widget)
        
        splitter.setSizes([700, 300])
        layout.addWidget(splitter, stretch=1)
    
    def _create_table(self) -> QTableWidget:
        """Create the equipment table."""
        table = QTableWidget()
        
        self.columns = [
            "Art.Nr",
            "Name",
            "Category",
            "Subcategory",
            "Dimensions",
            "Speed",
            "Power (kW)",
            "Generated",
            "Capacity",
            "Connections",
            "Price",
            "$/kW",
        ]
        
        table.setColumnCount(len(self.columns))
        table.setHorizontalHeaderLabels(self.columns)
        
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        table.setSortingEnabled(True)
        
        header = table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Name
        for i in [0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]:
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        
        table.itemSelectionChanged.connect(self._on_selection_changed)
        
        return table
    
    def _create_analysis_panel(self) -> QWidget:
        """Create the analysis panel."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Summary Stats
        stats_group = QGroupBox("📊 Summary Statistics")
        stats_layout = QVBoxLayout(stats_group)
        
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setMaximumHeight(200)
        stats_layout.addWidget(self.stats_text)
        
        layout.addWidget(stats_group)
        
        # Selected Item Details
        details_group = QGroupBox("📋 Selected Item Details")
        details_layout = QVBoxLayout(details_group)
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        details_layout.addWidget(self.details_text)
        
        layout.addWidget(details_group)
        
        return widget
    
    def _load_data(self):
        """Load equipment from database."""
        self.all_equipment = self.db.get_all_factory_equipment()
        
        # Update subcategory dropdown
        self._update_subcategory_combo()
        
        self._apply_filters()
        self._update_stats()
    
    def _load_default_data(self):
        """Load default factory equipment data into database."""
        reply = QMessageBox.question(
            self,
            "Load Default Data",
            f"This will load {len(FACTORY_EQUIPMENT_DATA)} factory equipment items.\n\n"
            "Existing data will be replaced. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        try:
            # Clear existing data
            self.db.delete_all_factory_equipment()
            
            # Load new data
            count = 0
            for data in FACTORY_EQUIPMENT_DATA:
                equipment = FactoryEquipment(
                    art_nr=data.get("art_nr", 0),
                    name=data.get("name", ""),
                    category=data.get("category", ""),
                    subcategory=data.get("subcategory", ""),
                    length_m=data.get("length_m", 0),
                    height_m=data.get("height_m", 0),
                    conveyor_speed=data.get("conveyor_speed", 0),
                    power_consumption_kw=data.get("power_consumption_kw", 0),
                    power_generated_kw=data.get("power_generated_kw", 0),
                    max_capacity_kw=data.get("max_capacity_kw", 0),
                    max_connections=data.get("max_connections", 1),
                    power_efficiency=data.get("power_efficiency", "1x"),
                    fuel_type=data.get("fuel_type", ""),
                    price=data.get("price", 0),
                    notes=data.get("notes", ""),
                )
                self.db.add_factory_equipment(equipment)
                count += 1
            
            QMessageBox.information(
                self,
                "Data Loaded",
                f"Successfully loaded {count} factory equipment items!"
            )
            
            self._load_data()
            self.data_changed.emit()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load data:\n{str(e)}")
    
    def _update_subcategory_combo(self):
        """Update subcategory dropdown based on current category."""
        current_category = self.category_combo.currentText()
        
        self.subcategory_combo.blockSignals(True)
        self.subcategory_combo.clear()
        self.subcategory_combo.addItem("All")
        
        if current_category == "All":
            subcategories = sorted(set(e.subcategory for e in self.all_equipment if e.subcategory))
        else:
            subcategories = sorted(set(
                e.subcategory for e in self.all_equipment 
                if e.category == current_category and e.subcategory
            ))
        
        self.subcategory_combo.addItems(subcategories)
        self.subcategory_combo.blockSignals(False)
    
    def _apply_filters(self):
        """Apply filters to equipment list."""
        search_text = self.search_input.text().lower().strip()
        category_filter = self.category_combo.currentText()
        subcategory_filter = self.subcategory_combo.currentText()
        
        # Update subcategories when category changes
        if self.sender() == self.category_combo:
            self._update_subcategory_combo()
        
        self.filtered_equipment = []
        
        for equipment in self.all_equipment:
            # Search filter
            if search_text:
                if (search_text not in equipment.name.lower() and 
                    search_text not in equipment.category.lower() and
                    search_text not in equipment.subcategory.lower()):
                    continue
            
            # Category filter
            if category_filter != "All" and equipment.category != category_filter:
                continue
            
            # Subcategory filter
            if subcategory_filter != "All" and equipment.subcategory != subcategory_filter:
                continue
            
            self.filtered_equipment.append(equipment)
        
        self._populate_table()
        self._update_count()
    
    def _populate_table(self):
        """Populate table with filtered equipment."""
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(self.filtered_equipment))
        
        for row, equip in enumerate(self.filtered_equipment):
            # Art.Nr
            art_item = QTableWidgetItem(str(equip.art_nr))
            art_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 0, art_item)
            
            # Name
            name_item = QTableWidgetItem(equip.name)
            self.table.setItem(row, 1, name_item)
            
            # Category
            cat_item = QTableWidgetItem(equip.category)
            self.table.setItem(row, 2, cat_item)
            
            # Subcategory
            subcat_item = QTableWidgetItem(equip.subcategory)
            self.table.setItem(row, 3, subcat_item)
            
            # Dimensions
            dim_item = QTableWidgetItem(equip.dimensions)
            dim_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 4, dim_item)
            
            # Speed
            if equip.conveyor_speed > 0:
                speed_text = f"{equip.conveyor_speed:.0f} M/s"
            else:
                speed_text = "-"
            speed_item = QTableWidgetItem(speed_text)
            speed_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 5, speed_item)
            
            # Power Consumption
            if equip.power_consumption_kw > 0:
                power_text = f"{equip.power_consumption_kw:.0f}"
                power_item = QTableWidgetItem(power_text)
                power_item.setForeground(QColor("#c62828"))  # Red for consumption
            else:
                power_item = QTableWidgetItem("-")
            power_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 6, power_item)
            
            # Power Generated
            if equip.power_generated_kw > 0:
                gen_text = f"+{equip.power_generated_kw:.0f}"
                gen_item = QTableWidgetItem(gen_text)
                gen_item.setForeground(QColor("#2e7d32"))  # Green for generation
            else:
                gen_item = QTableWidgetItem("-")
            gen_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 7, gen_item)
            
            # Capacity
            if equip.max_capacity_kw > 0:
                cap_text = f"{equip.max_capacity_kw:.0f}"
            else:
                cap_text = "-"
            cap_item = QTableWidgetItem(cap_text)
            cap_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 8, cap_item)
            
            # Connections
            if equip.max_connections > 1:
                conn_text = str(equip.max_connections)
            else:
                conn_text = "-"
            conn_item = QTableWidgetItem(conn_text)
            conn_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 9, conn_item)
            
            # Price
            price_item = QTableWidgetItem(f"${equip.price:,.0f}")
            price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 10, price_item)
            
            # $/kW (for generators and pylons)
            if equip.power_generated_kw > 0:
                cost_per_kw = equip.price / equip.power_generated_kw
                kw_text = f"${cost_per_kw:.2f}"
            elif equip.max_capacity_kw > 0:
                cost_per_kw = equip.price / equip.max_capacity_kw
                kw_text = f"${cost_per_kw:.2f}"
            else:
                kw_text = "-"
            kw_item = QTableWidgetItem(kw_text)
            kw_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 11, kw_item)
        
        self.table.setSortingEnabled(True)
    
    def _update_count(self):
        """Update the item count label."""
        self.count_label.setText(f"Items: {len(self.filtered_equipment)} / {len(self.all_equipment)}")
    
    def _update_stats(self):
        """Update summary statistics."""
        if not self.all_equipment:
            self.stats_text.setHtml("<p>No data loaded. Click 'Load Default Data' to populate.</p>")
            return
        
        # Calculate stats
        conveyors = [e for e in self.all_equipment if e.category == "Conveyor"]
        power = [e for e in self.all_equipment if e.category == "Power"]
        pipelines = [e for e in self.all_equipment if e.category == "Pipeline"]
        
        generators = [e for e in power if e.power_generated_kw > 0]
        pylons = [e for e in power if e.max_capacity_kw > 0]
        
        # Find best value generators
        coal_plants = [e for e in generators if "Coal" in e.subcategory]
        fuel_gens = [e for e in generators if "Generator" in e.subcategory]
        renewables = [e for e in generators if e.fuel_type in ["Sun", "Wind"]]
        
        html = f"""
        <style>
            body {{ font-family: sans-serif; font-size: 11px; }}
            h3 {{ margin: 5px 0; color: #1976d2; }}
            .stat {{ margin: 2px 0; }}
            .green {{ color: #2e7d32; }}
            .red {{ color: #c62828; }}
        </style>
        <h3>📦 Equipment Count</h3>
        <div class="stat">Conveyors: {len(conveyors)}</div>
        <div class="stat">Power Equipment: {len(power)}</div>
        <div class="stat">Pipeline: {len(pipelines)}</div>
        <div class="stat"><b>Total: {len(self.all_equipment)}</b></div>
        
        <h3>⚡ Power Generation</h3>
        <div class="stat">Coal Plants: {len(coal_plants)} (${min(e.price_per_kw for e in coal_plants) if coal_plants else 0:.2f}-${max(e.price_per_kw for e in coal_plants) if coal_plants else 0:.2f}/kW)</div>
        <div class="stat">Fuel Generators: {len(fuel_gens)} (${min(e.price_per_kw for e in fuel_gens) if fuel_gens else 0:.2f}-${max(e.price_per_kw for e in fuel_gens) if fuel_gens else 0:.2f}/kW)</div>
        <div class="stat">Renewables: {len(renewables)} ($63.00/kW, no fuel)</div>
        
        <h3>💡 Key Insights</h3>
        <div class="stat green">✓ Pipelines use 0 kW power</div>
        <div class="stat green">✓ Coal plants are cheapest/kW</div>
        <div class="stat green">✓ Wall pylons are 20% cheaper</div>
        """
        
        self.stats_text.setHtml(html)
    
    def _on_selection_changed(self):
        """Handle table selection change."""
        selected = self.table.selectedItems()
        if not selected:
            self.details_text.clear()
            return
        
        row = selected[0].row()
        if row < 0 or row >= len(self.filtered_equipment):
            return
        
        equip = self.filtered_equipment[row]
        
        html = f"""
        <style>
            body {{ font-family: sans-serif; font-size: 12px; }}
            h3 {{ margin: 5px 0; color: #1976d2; }}
            .label {{ color: #666; }}
            .value {{ font-weight: bold; }}
        </style>
        <h3>{equip.name}</h3>
        <p><span class="label">Art.Nr:</span> <span class="value">{equip.art_nr}</span></p>
        <p><span class="label">Category:</span> <span class="value">{equip.category} - {equip.subcategory}</span></p>
        <p><span class="label">Dimensions:</span> <span class="value">{equip.dimensions}</span></p>
        """
        
        if equip.conveyor_speed > 0:
            html += f'<p><span class="label">Speed:</span> <span class="value">{equip.conveyor_speed:.0f} M/s</span></p>'
        
        if equip.power_consumption_kw > 0:
            html += f'<p><span class="label">Power Consumption:</span> <span class="value" style="color:#c62828">{equip.power_consumption_kw:.0f} kW</span></p>'
        
        if equip.power_generated_kw > 0:
            html += f'<p><span class="label">Power Generated:</span> <span class="value" style="color:#2e7d32">+{equip.power_generated_kw:.0f} kW</span></p>'
            html += f'<p><span class="label">Cost per kW:</span> <span class="value">${equip.price_per_kw:.2f}</span></p>'
        
        if equip.max_capacity_kw > 0:
            html += f'<p><span class="label">Max Capacity:</span> <span class="value">{equip.max_capacity_kw:.0f} kW</span></p>'
            html += f'<p><span class="label">Cost per kW Capacity:</span> <span class="value">${equip.price_per_kw_capacity:.2f}</span></p>'
        
        if equip.max_connections > 1:
            html += f'<p><span class="label">Max Connections:</span> <span class="value">{equip.max_connections}</span></p>'
        
        if equip.power_efficiency != "1x":
            html += f'<p><span class="label">Efficiency:</span> <span class="value">{equip.power_efficiency}</span></p>'
        
        if equip.fuel_type:
            html += f'<p><span class="label">Fuel Type:</span> <span class="value">{equip.fuel_type}</span></p>'
        
        html += f'<p><span class="label">Price:</span> <span class="value">${equip.price:,.0f}</span></p>'
        
        if equip.notes:
            html += f'<p><span class="label">Notes:</span> <span class="value">{equip.notes}</span></p>'
        
        self.details_text.setHtml(html)
