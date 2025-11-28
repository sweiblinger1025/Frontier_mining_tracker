"""
Vehicles Sub-Tab - Vehicle specifications database

Displays all vehicles with specs for fleet planning and material movement.
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
    QFileDialog,
    QApplication,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor

from core.database import get_database
from pathlib import Path


# Vehicle data extracted from Frontier_Mining_Dashboard Vehicle Specs sheet
VEHICLE_DATA = [
    # Rock Trucks
    {"name": "Arvik DX20E", "category": "Vehicles - Rock Trucks", "description": "All-wheel-drive haul truck for rough mining sites",
     "weight_lbs": 42439, "capacity_yd3": 30.1, "power_kw": 263.2, "fuel_use_lph": 10, "fuel_capacity_l": 150, "price": 180000,
     "notes": "Tested capacity: 4 loader buckets = 34.0 yd3 (actual working capacity with overload)"},
    {"name": "Arvik DX20E No Tailgate", "category": "Vehicles - Rock Trucks", "description": "All-wheel-drive haul truck for rough mining sites",
     "weight_lbs": 42439, "capacity_yd3": 30.1, "power_kw": 263.2, "fuel_use_lph": 10, "fuel_capacity_l": 150, "price": 180000},
    {"name": "Arvik DX40E", "category": "Vehicles - Rock Trucks", "description": "All-wheel-drive haul truck for rough mining sites",
     "weight_lbs": 53462, "capacity_yd3": 39.2, "power_kw": 331.1, "fuel_use_lph": 12, "fuel_capacity_l": 160, "price": 344000},
    {"name": "Arvik DX40E No Tailgate", "category": "Vehicles - Rock Trucks", "description": "All-wheel-drive haul truck for rough mining sites",
     "weight_lbs": 53462, "capacity_yd3": 39.2, "power_kw": 331.1, "fuel_use_lph": 12, "fuel_capacity_l": 160, "price": 344000},
    {"name": "Arvik DX60E", "category": "Vehicles - Rock Trucks", "description": "All-wheel-drive haul truck for rough mining sites",
     "weight_lbs": 64485, "capacity_yd3": 47.1, "power_kw": 399.7, "fuel_use_lph": 15, "fuel_capacity_l": 200, "price": 445000},
    {"name": "Arvik DX60E No Tailgate", "category": "Vehicles - Rock Trucks", "description": "All-wheel-drive haul truck for rough mining sites",
     "weight_lbs": 64485, "capacity_yd3": 47.1, "power_kw": 399.7, "fuel_use_lph": 15, "fuel_capacity_l": 200, "price": 445000},
    {"name": "Arvik HT200E", "category": "Vehicles - Rock Trucks", "description": "Designed to carry enormous loads essential for large-scale operations",
     "weight_lbs": 233029, "capacity_yd3": 130.8, "power_kw": 2156.6, "fuel_use_lph": 35, "fuel_capacity_l": 1500, "price": 3532000},
    {"name": "Arvik HT300E", "category": "Vehicles - Rock Trucks", "description": "Designed to carry enormous loads essential for large-scale operations",
     "weight_lbs": 310191, "capacity_yd3": 287.8, "power_kw": 2870.2, "fuel_use_lph": 42, "fuel_capacity_l": 7500, "price": 4870000},
    {"name": "Arvik HT400E", "category": "Vehicles - Rock Trucks", "description": "Designed to carry enormous loads essential for large-scale operations",
     "weight_lbs": 365306, "capacity_yd3": 418.6, "power_kw": 3380.3, "fuel_use_lph": 50, "fuel_capacity_l": 7500, "price": 6105000},
    {"name": "Emilian DX40E", "category": "Vehicles - Rock Trucks", "description": "Designed for confined underground environments",
     "weight_lbs": 49053, "capacity_yd3": 31.4, "power_kw": 304.2, "fuel_use_lph": 30, "fuel_capacity_l": 560, "price": 322710},
    
    # Excavators
    {"name": "Arvik EX500D", "category": "Vehicles - Excavators",
     "weight_lbs": 83004, "capacity_yd3": 4.8, "power_kw": 299.8, "fuel_use_lph": 30, "fuel_capacity_l": 1000, "price": 412000},
    {"name": "Attila Cable EX200A", "category": "Vehicles - Excavators",
     "weight_lbs": 43652, "capacity_yd3": 2.1, "power_kw": 155.1, "fuel_use_lph": 35, "fuel_capacity_l": 250, "price": 79000},
    {"name": "Attila Cable EX200A1", "category": "Vehicles - Excavators",
     "weight_lbs": 43321, "capacity_yd3": 1.0, "power_kw": 154.4, "fuel_use_lph": 32, "fuel_capacity_l": 250, "price": 68000},
    {"name": "Attila Cable EX300A", "category": "Vehicles - Excavators",
     "weight_lbs": 43321, "capacity_yd3": 1.8, "power_kw": 154.4, "fuel_use_lph": 35, "fuel_capacity_l": 250, "price": 104000},
    {"name": "Attila Cable EX500A", "category": "Vehicles - Excavators",
     "weight_lbs": 107034, "capacity_yd3": 2.3, "power_kw": 381.1, "fuel_use_lph": 55, "fuel_capacity_l": 450, "price": 132000},
    {"name": "Attila EW200A B100", "category": "Vehicles - Excavators", "description": "Used for drilling",
     "weight_lbs": 52029, "capacity_yd3": 0, "power_kw": 196.1, "fuel_use_lph": 20, "fuel_capacity_l": 250, "price": 132000},
    {"name": "Attila EX200A", "category": "Vehicles - Excavators",
     "weight_lbs": 45415, "capacity_yd3": 1.1, "power_kw": 161.8, "fuel_use_lph": 30, "fuel_capacity_l": 220, "price": 75000},
    {"name": "Attila EX300A", "category": "Vehicles - Excavators",
     "weight_lbs": 43211, "capacity_yd3": 3.6, "power_kw": 153.6, "fuel_use_lph": 32, "fuel_capacity_l": 220, "price": 15000},
    {"name": "Attila EX500A", "category": "Vehicles - Excavators",
     "weight_lbs": 62832, "capacity_yd3": 4.9, "power_kw": 223.7, "fuel_use_lph": 48, "fuel_capacity_l": 460, "price": 172000},
    {"name": "Bagger 681", "category": "Vehicles - Excavators", "description": "Digging large amount of material",
     "weight_lbs": 30093, "capacity_yd3": 0, "power_kw": 105.9, "fuel_use_lph": 100, "fuel_capacity_l": 4200, "price": 4250000},
    {"name": "Bagger 693", "category": "Vehicles - Excavators", "description": "Digging large amount of material",
     "weight_lbs": 485899, "capacity_yd3": 0, "power_kw": 1753.1, "fuel_use_lph": 150, "fuel_capacity_l": 6300, "price": 7250000},
    {"name": "Chariton Cable EX2000D", "category": "Vehicles - Excavators",
     "weight_lbs": 81571, "capacity_yd3": 7.2, "power_kw": 290.1, "fuel_use_lph": 40, "fuel_capacity_l": 1000, "price": 754000},
    {"name": "Chariton Cable EX4000D", "category": "Vehicles - Excavators",
     "weight_lbs": 790247, "capacity_yd3": 13.9, "power_kw": 2813.5, "fuel_use_lph": 70, "fuel_capacity_l": 250, "price": 1620000},
    {"name": "Chariton Cable EX8000D", "category": "Vehicles - Excavators",
     "weight_lbs": 922525, "capacity_yd3": 40.5, "power_kw": 3685.2, "fuel_use_lph": 90, "fuel_capacity_l": 10000, "price": 2620000},
    {"name": "Chariton EW200D", "category": "Vehicles - Excavators",
     "weight_lbs": 34392, "capacity_yd3": 2.1, "power_kw": 133.5, "fuel_use_lph": 15, "fuel_capacity_l": 250, "price": 164000},
    {"name": "Chariton EWC200D", "category": "Vehicles - Excavators",
     "weight_lbs": 34392, "capacity_yd3": 2.1, "power_kw": 123.8, "fuel_use_lph": 10, "fuel_capacity_l": 220, "price": 235000},
    {"name": "Chariton EX2000D", "category": "Vehicles - Excavators",
     "weight_lbs": 82234, "capacity_yd3": 7.2, "power_kw": 328.9, "fuel_use_lph": 50, "fuel_capacity_l": 1000, "price": 654000,
     "notes": "Mid-size excavator - bucket capacity"},
    {"name": "Chariton EX200A", "category": "Vehicles - Excavators", "description": "Medium excavator - versatile for varied operations",
     "weight_lbs": 38801, "capacity_yd3": 2.1, "power_kw": 140.2, "fuel_use_lph": 35, "fuel_capacity_l": 250, "price": 86000,
     "notes": "Mid-size excavator - bucket capacity"},
    {"name": "Chariton EX200D", "category": "Vehicles - Excavators",
     "weight_lbs": 56218, "capacity_yd3": 2.1, "power_kw": 202.8, "fuel_use_lph": 10, "fuel_capacity_l": 160, "price": 186000},
    {"name": "Chariton EX200D (Long boom)", "category": "Vehicles - Excavators",
     "weight_lbs": 58533, "capacity_yd3": 1.2, "power_kw": 211, "fuel_use_lph": 10, "fuel_capacity_l": 160, "price": 312500},
    {"name": "Chariton EX200D B100", "category": "Vehicles - Excavators",
     "weight_lbs": 38801, "capacity_yd3": 0, "power_kw": 140.2, "fuel_use_lph": 10, "fuel_capacity_l": 160, "price": 175000},
    {"name": "Chariton EX300D", "category": "Vehicles - Excavators",
     "weight_lbs": 56218, "capacity_yd3": 3.7, "power_kw": 202.8, "fuel_use_lph": 20, "fuel_capacity_l": 320, "price": 225000},
    {"name": "Chariton EX300D B120", "category": "Vehicles - Excavators",
     "weight_lbs": 50927, "capacity_yd3": 0, "power_kw": 183.4, "fuel_use_lph": 20, "fuel_capacity_l": 300, "price": 227500},
    {"name": "Chariton EX4000D", "category": "Vehicles - Excavators", "description": "Large excavator for heavy digging operations",
     "weight_lbs": 793113, "capacity_yd3": 13.9, "power_kw": 3168.5, "fuel_use_lph": 100, "fuel_capacity_l": 3000, "price": 1435000,
     "notes": "Heavy duty excavation - bucket capacity"},
    {"name": "Chariton EX4000FS", "category": "Vehicles - Excavators",
     "weight_lbs": 241957, "capacity_yd3": 19.9, "power_kw": 873.2, "fuel_use_lph": 100, "fuel_capacity_l": 3000, "price": 1795000},
    {"name": "Chariton EX400D (Long boom)", "category": "Vehicles - Excavators",
     "weight_lbs": 80359, "capacity_yd3": 2.4, "power_kw": 290.1, "fuel_use_lph": 25, "fuel_capacity_l": 1000, "price": 415000},
    {"name": "Chariton EX500B", "category": "Vehicles - Excavators",
     "weight_lbs": 106924, "capacity_yd3": 4.8, "power_kw": 385.5, "fuel_use_lph": 45, "fuel_capacity_l": 150, "price": 226000},
    {"name": "Chariton EX500D", "category": "Vehicles - Excavators", "description": "Medium excavator - versatile for varied operations",
     "weight_lbs": 83004, "capacity_yd3": 4.8, "power_kw": 299.8, "fuel_use_lph": 30, "fuel_capacity_l": 1000, "price": 367000},
    {"name": "Chariton EX500D B140", "category": "Vehicles - Excavators",
     "weight_lbs": 61509, "capacity_yd3": 0, "power_kw": 222.2, "fuel_use_lph": 30, "fuel_capacity_l": 300, "price": 341250},
    {"name": "Chariton EX500FS", "category": "Vehicles - Excavators",
     "weight_lbs": 268964, "capacity_yd3": 6.5, "power_kw": 970.9, "fuel_use_lph": 30, "fuel_capacity_l": 300, "price": 542000},
    {"name": "Chariton EX600D (Long boom)", "category": "Vehicles - Excavators",
     "weight_lbs": 106814, "capacity_yd3": 4.5, "power_kw": 385.5, "fuel_use_lph": 85, "fuel_capacity_l": 1500, "price": 421000},
    {"name": "Chariton EX8000D", "category": "Vehicles - Excavators",
     "weight_lbs": 926493, "capacity_yd3": 49.2, "power_kw": 3700.9, "fuel_use_lph": 110, "fuel_capacity_l": 10000, "price": 2435000},
    {"name": "Chariton EX8000FS", "category": "Vehicles - Excavators",
     "weight_lbs": 925391, "capacity_yd3": 54.9, "power_kw": 3339.2, "fuel_use_lph": 110, "fuel_capacity_l": 10000, "price": 2795000},
    {"name": "Legau EW200D Zero Swing", "category": "Vehicles - Excavators",
     "weight_lbs": 34392, "capacity_yd3": 2.1, "power_kw": 133.5, "fuel_use_lph": 10, "fuel_capacity_l": 220, "price": 174000},
    {"name": "Legau EW200D Zero Swing B100", "category": "Vehicles - Excavators",
     "weight_lbs": 52029, "capacity_yd3": 0, "power_kw": 202.1, "fuel_use_lph": 15, "fuel_capacity_l": 250, "price": 194000},
    {"name": "Legau EX200D Zero Swing", "category": "Vehicles - Excavators",
     "weight_lbs": 38801, "capacity_yd3": 2.1, "power_kw": 140.2, "fuel_use_lph": 10, "fuel_capacity_l": 220, "price": 186000},
    
    # Loaders
    {"name": "Arvik L10", "category": "Vehicles - Loaders",
     "weight_lbs": 54013, "capacity_yd3": 9.5, "power_kw": 334.8, "fuel_use_lph": 16, "fuel_capacity_l": 200, "price": 198000},
    {"name": "Arvik L10000", "category": "Vehicles - Loaders",
     "weight_lbs": 62281, "capacity_yd3": 9.5, "power_kw": 386.3, "fuel_use_lph": 35, "fuel_capacity_l": 350, "price": 78000},
    {"name": "Arvik L11", "category": "Vehicles - Loaders",
     "weight_lbs": 65036, "capacity_yd3": 13.1, "power_kw": 403.4, "fuel_use_lph": 17, "fuel_capacity_l": 200, "price": 234000},
    {"name": "Arvik L1665", "category": "Vehicles - Loaders",
     "weight_lbs": 319670, "capacity_yd3": 28.1, "power_kw": 1981.3, "fuel_use_lph": 70, "fuel_capacity_l": 8000, "price": 1640000},
    {"name": "Arvik L2335", "category": "Vehicles - Loaders",
     "weight_lbs": 650364, "capacity_yd3": 62.8, "power_kw": 4030.5, "fuel_use_lph": 85, "fuel_capacity_l": 8500, "price": 1940000},
    {"name": "Arvik L8", "category": "Vehicles - Loaders",
     "weight_lbs": 24582, "capacity_yd3": 8.5, "power_kw": 152.1, "fuel_use_lph": 13, "fuel_capacity_l": 200, "price": 126000},
    {"name": "Arvik L8000", "category": "Vehicles - Loaders", "description": "Front-end loader for scooping and material handling",
     "weight_lbs": 31195, "capacity_yd3": 8.5, "power_kw": 193.1, "fuel_use_lph": 27, "fuel_capacity_l": 200, "price": 46000,
     "notes": "Verified: 8.5 yd3 bucket - 4 buckets fill DX20E truck"},
    {"name": "Arvik L9", "category": "Vehicles - Loaders",
     "weight_lbs": 24802, "capacity_yd3": 8.9, "power_kw": 153.6, "fuel_use_lph": 10, "fuel_capacity_l": 200, "price": 155000},
    {"name": "Emilian L9", "category": "Vehicles - Loaders",
     "weight_lbs": 45195, "capacity_yd3": 8.8, "power_kw": 280.4, "fuel_use_lph": 20, "fuel_capacity_l": 500, "price": 420000},
    
    # Paving
    {"name": "Arvik L9 Asphalt Roller", "category": "Vehicles - Paving",
     "weight_lbs": 38581, "capacity_yd3": 0, "power_kw": 177.5, "fuel_use_lph": 10, "fuel_capacity_l": 150, "price": 63000},
    {"name": "Arvik L9 Roller", "category": "Vehicles - Paving",
     "weight_lbs": 38581, "capacity_yd3": 0, "power_kw": 177.5, "fuel_use_lph": 16, "fuel_capacity_l": 250, "price": 83000},
    {"name": "Sandvik AP310 Paver", "category": "Vehicles - Paving",
     "weight_lbs": 24172, "capacity_yd3": 6.8, "power_kw": 129, "fuel_use_lph": 8, "fuel_capacity_l": 150, "price": 262710},
    
    # Dozers
    {"name": "Chariton DX1000", "category": "Vehicles - Dozers",
     "weight_lbs": 162040, "capacity_yd3": 1.6, "power_kw": 647.3, "fuel_use_lph": 35, "fuel_capacity_l": 1300, "price": 1345000},
    {"name": "Chariton DX100A", "category": "Vehicles - Dozers",
     "weight_lbs": 139994, "capacity_yd3": 1.6, "power_kw": 559.3, "fuel_use_lph": 65, "fuel_capacity_l": 750, "price": 345000},
    {"name": "Chariton DX11000", "category": "Vehicles - Dozers",
     "weight_lbs": 206132, "capacity_yd3": 1.6, "power_kw": 823.3, "fuel_use_lph": 40, "fuel_capacity_l": 2000, "price": 1757000},
    {"name": "Chariton DX900", "category": "Vehicles - Dozers",
     "weight_lbs": 146607, "capacity_yd3": 1.6, "power_kw": 585.4, "fuel_use_lph": 30, "fuel_capacity_l": 1000, "price": 884000},
    {"name": "Chariton DX900 6-Way", "category": "Vehicles - Dozers",
     "weight_lbs": 146607, "capacity_yd3": 1.6, "power_kw": 585.4, "fuel_use_lph": 30, "fuel_capacity_l": 850, "price": 884000},
    
    # Graders
    {"name": "Chariton G150E", "category": "Vehicles - Graders",
     "weight_lbs": 20944, "capacity_yd3": 1.6, "power_kw": 129.8, "fuel_use_lph": 12, "fuel_capacity_l": 160, "price": 104000},
    {"name": "Chariton G200E", "category": "Vehicles - Graders",
     "weight_lbs": 31967, "capacity_yd3": 1.6, "power_kw": 198.4, "fuel_use_lph": 15, "fuel_capacity_l": 200, "price": 393000},
    
    # Flying
    {"name": "Drone", "category": "Vehicles - Flying",
     "weight_lbs": 992, "capacity_yd3": 0, "power_kw": 0, "fuel_use_lph": 0, "fuel_capacity_l": 0, "price": 32210},
    
    # Tunneler
    {"name": "Emilian Tunneler E200DR", "category": "Vehicles - Tunneler",
     "weight_lbs": 46848, "capacity_yd3": 13.1, "power_kw": 169.3, "fuel_use_lph": 25, "fuel_capacity_l": 500, "price": 322710},
    {"name": "Emilian Tunneler E200DS", "category": "Vehicles - Tunneler",
     "weight_lbs": 90941, "capacity_yd3": 13.1, "power_kw": 328.1, "fuel_use_lph": 25, "fuel_capacity_l": 500, "price": 322710},
    
    # Trucks
    {"name": "Petworth W389", "category": "Vehicles - Trucks",
     "weight_lbs": 30865, "capacity_yd3": 13.1, "power_kw": 484.7, "fuel_use_lph": 13, "fuel_capacity_l": 500, "price": 171000},
    {"name": "Sandvik S150 2WD", "category": "Vehicles - Trucks",
     "weight_lbs": 13228, "capacity_yd3": 0, "power_kw": 207.3, "fuel_use_lph": 3, "fuel_capacity_l": 100, "price": 32710},
    {"name": "Sandvik S150 4WD", "category": "Vehicles - Trucks",
     "weight_lbs": 13228, "capacity_yd3": 1.6, "power_kw": 207.3, "fuel_use_lph": 5, "fuel_capacity_l": 100, "price": 62710},
    {"name": "Sandvik S700NG", "category": "Vehicles - Trucks",
     "weight_lbs": 35274, "capacity_yd3": 13.1, "power_kw": 553.3, "fuel_use_lph": 12, "fuel_capacity_l": 500, "price": 184000},
    
    # Fuel Trucks
    {"name": "Sandvik S700NG Fuel", "category": "Vehicles - Fuel Trucks",
     "weight_lbs": 35274, "capacity_yd3": 0, "power_kw": 553.3, "fuel_use_lph": 10, "fuel_capacity_l": 500, "price": 197000},
]


class VehiclesSubTab(QWidget):
    """Vehicles sub-tab showing all vehicle specifications."""
    
    data_changed = pyqtSignal()
    
    # Fuel price constant
    FUEL_PRICE_PER_LITER = 0.32
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = get_database()
        self.all_vehicles = []
        self.filtered_vehicles = []
        
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
        self.search_input.setPlaceholderText("Search vehicles...")
        self.search_input.textChanged.connect(self._apply_filters)
        filter_layout.addWidget(self.search_input, stretch=2)
        
        filter_layout.addWidget(QLabel("Category:"))
        self.category_combo = QComboBox()
        self.category_combo.addItem("All")
        self.category_combo.currentTextChanged.connect(self._apply_filters)
        filter_layout.addWidget(self.category_combo)
        
        filter_layout.addStretch()
        
        self.count_label = QLabel("Vehicles: 0")
        filter_layout.addWidget(self.count_label)
        
        self.load_data_btn = QPushButton("🔄 Load Default Data")
        self.load_data_btn.setToolTip("Load vehicle data from built-in database")
        self.load_data_btn.clicked.connect(self._load_default_data)
        filter_layout.addWidget(self.load_data_btn)
        
        self.import_btn = QPushButton("📥 Import from Excel")
        self.import_btn.setToolTip("Import vehicle specs from Dashboard Excel")
        self.import_btn.clicked.connect(self._import_from_excel)
        filter_layout.addWidget(self.import_btn)
        
        layout.addLayout(filter_layout)
        
        # Main content: Splitter with table and analysis
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left: Vehicle Table
        self.table = self._create_table()
        splitter.addWidget(self.table)
        
        # Right: Analysis Panel
        analysis_widget = self._create_analysis_panel()
        splitter.addWidget(analysis_widget)
        
        splitter.setSizes([750, 250])
        layout.addWidget(splitter, stretch=1)
    
    def _create_table(self) -> QTableWidget:
        """Create the vehicle table."""
        table = QTableWidget()
        
        self.columns = [
            "Name",
            "Category",
            "Weight (lbs)",
            "Capacity (yd³)",
            "Power (kW)",
            "Fuel Use (L/hr)",
            "Fuel Tank (L)",
            "Run Time (hrs)",
            "Fuel $/hr",
            "Price",
        ]
        
        table.setColumnCount(len(self.columns))
        table.setHorizontalHeaderLabels(self.columns)
        
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        table.setSortingEnabled(True)
        
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Name
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Category
        for i in range(2, len(self.columns)):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        
        table.itemSelectionChanged.connect(self._on_selection_changed)
        
        return table
    
    def _create_analysis_panel(self) -> QWidget:
        """Create the analysis panel."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Summary Stats
        stats_group = QGroupBox("📊 Fleet Summary")
        stats_layout = QVBoxLayout(stats_group)
        
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setMaximumHeight(180)
        stats_layout.addWidget(self.stats_text)
        
        layout.addWidget(stats_group)
        
        # Selected Vehicle Details
        details_group = QGroupBox("🚛 Selected Vehicle Details")
        details_layout = QVBoxLayout(details_group)
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        details_layout.addWidget(self.details_text)
        
        layout.addWidget(details_group)
        
        return widget
    
    def _load_data(self):
        """Load vehicles from built-in data."""
        # For now, use built-in data directly
        # Later can be extended to load from database
        self.all_vehicles = VEHICLE_DATA.copy()
        
        # Update category dropdown
        categories = sorted(set(v["category"] for v in self.all_vehicles))
        self.category_combo.blockSignals(True)
        self.category_combo.clear()
        self.category_combo.addItem("All")
        self.category_combo.addItems(categories)
        self.category_combo.blockSignals(False)
        
        self._apply_filters()
        self._update_stats()
    
    def _load_default_data(self):
        """Reload default vehicle data."""
        self._load_data()
        QMessageBox.information(
            self,
            "Data Loaded",
            f"Loaded {len(self.all_vehicles)} vehicles from built-in database."
        )
    
    def _import_from_excel(self):
        """Import vehicle specs from Excel file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Dashboard Excel File",
            "",
            "Excel Files (*.xlsx *.xls);;All Files (*)"
        )
        
        if not file_path:
            return
        
        try:
            import pandas as pd
            
            df = pd.read_excel(file_path, sheet_name='Vehicle Specs')
            
            # Skip header rows and get actual data
            # The actual headers are in row 1
            df.columns = df.iloc[0]
            df = df.iloc[1:].reset_index(drop=True)
            
            vehicles = []
            for _, row in df.iterrows():
                try:
                    vehicle = {
                        "name": str(row.get("Vehicle Name", "")),
                        "category": str(row.get("Category", "")),
                        "description": str(row.get("Description", "")) if pd.notna(row.get("Description")) else "",
                        "weight_lbs": float(row.get("Weight (lbs)", 0)) if pd.notna(row.get("Weight (lbs)")) else 0,
                        "capacity_yd3": float(row.get("Capacity (yd3)", 0)) if pd.notna(row.get("Capacity (yd3)")) else 0,
                        "power_kw": float(row.get("Power (kW)", 0)) if pd.notna(row.get("Power (kW)")) else 0,
                        "fuel_use_lph": float(row.get("Fuel Use (L/Hour)", 0)) if pd.notna(row.get("Fuel Use (L/Hour)")) else 0,
                        "fuel_capacity_l": float(row.get("Fuel Capacity (L)", 0)) if pd.notna(row.get("Fuel Capacity (L)")) else 0,
                        "price": float(row.get("Purchase Price", 0)) if pd.notna(row.get("Purchase Price")) else 0,
                        "notes": str(row.get("Notes", "")) if pd.notna(row.get("Notes")) else "",
                    }
                    if vehicle["name"] and vehicle["category"]:
                        vehicles.append(vehicle)
                except Exception:
                    continue
            
            if vehicles:
                self.all_vehicles = vehicles
                self._apply_filters()
                self._update_stats()
                QMessageBox.information(
                    self,
                    "Import Complete",
                    f"Imported {len(vehicles)} vehicles from Excel."
                )
            else:
                QMessageBox.warning(self, "Import Warning", "No valid vehicle data found.")
                
        except Exception as e:
            QMessageBox.critical(self, "Import Error", f"Failed to import:\n{str(e)}")
    
    def _apply_filters(self):
        """Apply filters to vehicle list."""
        search_text = self.search_input.text().lower().strip()
        category_filter = self.category_combo.currentText()
        
        self.filtered_vehicles = []
        
        for vehicle in self.all_vehicles:
            # Search filter
            if search_text:
                if (search_text not in vehicle["name"].lower() and 
                    search_text not in vehicle["category"].lower()):
                    continue
            
            # Category filter
            if category_filter != "All" and vehicle["category"] != category_filter:
                continue
            
            self.filtered_vehicles.append(vehicle)
        
        self._populate_table()
        self._update_count()
    
    def _populate_table(self):
        """Populate table with filtered vehicles."""
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(self.filtered_vehicles))
        
        for row, vehicle in enumerate(self.filtered_vehicles):
            # Name
            name_item = QTableWidgetItem(vehicle["name"])
            self.table.setItem(row, 0, name_item)
            
            # Category (shortened)
            cat = vehicle["category"].replace("Vehicles - ", "")
            cat_item = QTableWidgetItem(cat)
            self.table.setItem(row, 1, cat_item)
            
            # Weight
            weight_item = QTableWidgetItem(f"{vehicle['weight_lbs']:,.0f}")
            weight_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 2, weight_item)
            
            # Capacity
            if vehicle["capacity_yd3"] > 0:
                cap_text = f"{vehicle['capacity_yd3']:.1f}"
            else:
                cap_text = "-"
            cap_item = QTableWidgetItem(cap_text)
            cap_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 3, cap_item)
            
            # Power
            if vehicle["power_kw"] > 0:
                power_text = f"{vehicle['power_kw']:,.0f}"
            else:
                power_text = "-"
            power_item = QTableWidgetItem(power_text)
            power_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 4, power_item)
            
            # Fuel Use
            if vehicle["fuel_use_lph"] > 0:
                fuel_text = f"{vehicle['fuel_use_lph']:.0f}"
            else:
                fuel_text = "-"
            fuel_item = QTableWidgetItem(fuel_text)
            fuel_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 5, fuel_item)
            
            # Fuel Tank
            if vehicle["fuel_capacity_l"] > 0:
                tank_text = f"{vehicle['fuel_capacity_l']:,.0f}"
            else:
                tank_text = "-"
            tank_item = QTableWidgetItem(tank_text)
            tank_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 6, tank_item)
            
            # Run Time (Fuel Tank / Fuel Use)
            if vehicle["fuel_use_lph"] > 0 and vehicle["fuel_capacity_l"] > 0:
                run_time = vehicle["fuel_capacity_l"] / vehicle["fuel_use_lph"]
                run_text = f"{run_time:.1f}"
            else:
                run_text = "-"
            run_item = QTableWidgetItem(run_text)
            run_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 7, run_item)
            
            # Fuel $/hr
            if vehicle["fuel_use_lph"] > 0:
                fuel_cost = vehicle["fuel_use_lph"] * self.FUEL_PRICE_PER_LITER
                cost_text = f"${fuel_cost:.2f}"
                cost_item = QTableWidgetItem(cost_text)
                if fuel_cost > 20:
                    cost_item.setForeground(QColor("#c62828"))  # Red for expensive
                elif fuel_cost > 10:
                    cost_item.setForeground(QColor("#f57c00"))  # Orange for moderate
            else:
                cost_item = QTableWidgetItem("-")
            cost_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 8, cost_item)
            
            # Price
            price_item = QTableWidgetItem(f"${vehicle['price']:,.0f}")
            price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 9, price_item)
        
        self.table.setSortingEnabled(True)
    
    def _update_count(self):
        """Update the vehicle count label."""
        self.count_label.setText(f"Vehicles: {len(self.filtered_vehicles)} / {len(self.all_vehicles)}")
    
    def _update_stats(self):
        """Update summary statistics."""
        if not self.all_vehicles:
            self.stats_text.setHtml("<p>No data loaded.</p>")
            return
        
        # Count by category
        categories = {}
        for v in self.all_vehicles:
            cat = v["category"].replace("Vehicles - ", "")
            categories[cat] = categories.get(cat, 0) + 1
        
        # Find extremes
        max_capacity = max((v for v in self.all_vehicles if v["capacity_yd3"] > 0), 
                           key=lambda x: x["capacity_yd3"], default=None)
        min_fuel = min((v for v in self.all_vehicles if v["fuel_use_lph"] > 0),
                       key=lambda x: x["fuel_use_lph"], default=None)
        max_fuel = max((v for v in self.all_vehicles if v["fuel_use_lph"] > 0),
                       key=lambda x: x["fuel_use_lph"], default=None)
        
        html = f"""
        <style>
            body {{ font-family: sans-serif; font-size: 11px; }}
            h3 {{ margin: 5px 0; color: #1976d2; }}
            .stat {{ margin: 2px 0; }}
            .green {{ color: #2e7d32; }}
            .red {{ color: #c62828; }}
        </style>
        <h3>🚛 Vehicle Count: {len(self.all_vehicles)}</h3>
        """
        
        for cat, count in sorted(categories.items()):
            html += f'<div class="stat">{cat}: {count}</div>'
        
        html += "<h3>⛽ Fuel Analysis</h3>"
        html += f'<div class="stat">Fuel Price: ${self.FUEL_PRICE_PER_LITER:.2f}/L</div>'
        
        if min_fuel:
            html += f'<div class="stat green">Most Efficient: {min_fuel["name"]} ({min_fuel["fuel_use_lph"]} L/hr)</div>'
        if max_fuel:
            html += f'<div class="stat red">Highest Consumption: {max_fuel["name"]} ({max_fuel["fuel_use_lph"]} L/hr)</div>'
        if max_capacity:
            html += f'<div class="stat">Largest Capacity: {max_capacity["name"]} ({max_capacity["capacity_yd3"]} yd³)</div>'
        
        self.stats_text.setHtml(html)
    
    def _on_selection_changed(self):
        """Handle table selection change."""
        selected = self.table.selectedItems()
        if not selected:
            self.details_text.clear()
            return
        
        row = selected[0].row()
        if row < 0 or row >= len(self.filtered_vehicles):
            return
        
        vehicle = self.filtered_vehicles[row]
        
        # Calculate derived values
        fuel_cost_hr = vehicle["fuel_use_lph"] * self.FUEL_PRICE_PER_LITER
        run_time = vehicle["fuel_capacity_l"] / vehicle["fuel_use_lph"] if vehicle["fuel_use_lph"] > 0 else 0
        cost_per_tank = vehicle["fuel_capacity_l"] * self.FUEL_PRICE_PER_LITER
        
        html = f"""
        <style>
            body {{ font-family: sans-serif; font-size: 12px; }}
            h3 {{ margin: 5px 0; color: #1976d2; }}
            .label {{ color: #666; }}
            .value {{ font-weight: bold; }}
            .section {{ margin-top: 10px; }}
        </style>
        <h3>{vehicle["name"]}</h3>
        <p><span class="label">Category:</span> <span class="value">{vehicle["category"]}</span></p>
        """
        
        if vehicle.get("description"):
            html += f'<p><span class="label">Description:</span> {vehicle["description"]}</p>'
        
        html += f"""
        <div class="section">
        <p><span class="label">Weight:</span> <span class="value">{vehicle["weight_lbs"]:,.0f} lbs</span> ({vehicle["weight_lbs"] * 0.453592:,.0f} kg)</p>
        <p><span class="label">Capacity:</span> <span class="value">{vehicle["capacity_yd3"]:.1f} yd³</span> ({vehicle["capacity_yd3"] * 0.764555:.1f} m³)</p>
        <p><span class="label">Power:</span> <span class="value">{vehicle["power_kw"]:,.0f} kW</span></p>
        </div>
        
        <div class="section">
        <p><span class="label">Fuel Use:</span> <span class="value">{vehicle["fuel_use_lph"]:.0f} L/hr</span></p>
        <p><span class="label">Fuel Tank:</span> <span class="value">{vehicle["fuel_capacity_l"]:,.0f} L</span></p>
        <p><span class="label">Run Time:</span> <span class="value">{run_time:.1f} hours</span> per tank</p>
        </div>
        
        <div class="section">
        <p><span class="label">Fuel Cost:</span> <span class="value" style="color:#c62828">${fuel_cost_hr:.2f}/hr</span></p>
        <p><span class="label">Cost per Tank:</span> <span class="value">${cost_per_tank:,.2f}</span></p>
        <p><span class="label">Purchase Price:</span> <span class="value">${vehicle["price"]:,.0f}</span></p>
        </div>
        """
        
        if vehicle.get("notes"):
            html += f'<div class="section"><p><span class="label">Notes:</span> {vehicle["notes"]}</p></div>'
        
        self.details_text.setHtml(html)
    
    def get_vehicle_by_name(self, name: str) -> dict:
        """Get vehicle by name."""
        for v in self.all_vehicles:
            if v["name"] == name:
                return v
        return None
    
    def get_all_vehicle_names(self) -> list[str]:
        """Get all vehicle names for autocomplete."""
        return [v["name"] for v in self.all_vehicles]
