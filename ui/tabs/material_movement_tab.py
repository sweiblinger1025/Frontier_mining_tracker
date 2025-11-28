"""
Material Movement Tab - Track Mining Sessions: Hauling Operations & Material Processing

Features:
- Active Session Tracker with real-time stats
- Hauling Session logging (vehicle, loads, fuel)
- Processing Session logging (ores extracted, revenue)
- Session History with filtering
- Cumulative Totals and Best Performance tracking
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
    QTextEdit,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QTabWidget,
    QDateEdit,
    QTimeEdit,
    QSplitter,
    QFormLayout,
    QMessageBox,
    QAbstractItemView,
    QScrollArea,
    QFrame,
)
from PyQt6.QtCore import Qt, pyqtSignal, QDate, QTime, QTimer
from PyQt6.QtGui import QColor, QFont

from core.database import get_database
from datetime import datetime, timedelta


class MaterialMovementTab(QWidget):
    """Material Movement tab for tracking hauling and processing sessions."""
    
    # Signals
    data_changed = pyqtSignal()
    
    # Constants
    FUEL_PRICE_PER_LITER = 0.32  # Confirmed game fuel price
    COMPANY_SPLIT = 0.90  # 90% company
    PERSONAL_SPLIT = 0.10  # 10% personal
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = get_database()
        
        # Reference to ledger tab (will be set by main window)
        self.ledger_tab = None
        
        # Session tracking
        self.session_active = False
        self.session_start_time = None
        self.session_start_balance = 0
        
        # Data storage
        self.hauling_sessions = []
        self.processing_sessions = []
        
        # Load vehicle and location data
        self._load_reference_data()
        
        self._setup_ui()
        self._setup_timer()
    
    def _load_reference_data(self):
        """Load vehicles and locations from reference data."""
        # Import vehicle data from vehicles_subtab
        from ui.tabs.vehicles_subtab import VEHICLE_DATA
        self.vehicles = VEHICLE_DATA
        
        # Load locations from database
        self.locations = self.db.get_locations()
        
        # Filter stockpile locations
        self.stockpiles = [loc for loc in self.locations if loc.get('type') == 'Stockpile']
        
        # Get processor types from buildings
        self.processor_types = [
            "Washplant",
            "Sluice Box", 
            "Froth Floater",
            "Smelter",
            "High Temp Smelter",
            "Trommel",
            "Shaker Screen",
            "Coal Screen",
        ]
        
        # Get ore items (would come from Items table)
        self.ore_types = [
            "Aluminium Ore", "Coal", "Copper Ore", "Diamond Ore", "Gold Ore",
            "Iron Ore", "Lithium Ore", "Ruby Ore", "Silicon Ore", "Silver Ore",
        ]
        
        # Base prices from Items table (Resources - Ore category)
        self.ore_prices = {
            "Aluminium Ore": 37,
            "Coal": 13,
            "Copper Ore": 28,
            "Diamond Ore": 45,
            "Gold Ore": 43,
            "Iron Ore": 24,
            "Lithium Ore": 53,
            "Ruby Ore": 46,
            "Silicon Ore": 50,
            "Silver Ore": 41,
        }
    
    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Create scroll area for the entire tab
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        # Main content widget
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(10)
        
        # Active Session Tracker (top)
        content_layout.addWidget(self._create_session_tracker())
        
        # Session Type Selector
        content_layout.addWidget(self._create_session_type_selector())
        
        # Main splitter: Entry forms on left, History on right
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side: Entry forms
        forms_widget = QWidget()
        forms_layout = QVBoxLayout(forms_widget)
        forms_layout.setContentsMargins(0, 0, 0, 0)
        
        # Hauling Session Form
        self.hauling_group = self._create_hauling_form()
        forms_layout.addWidget(self.hauling_group)
        
        # Processing Session Form
        self.processing_group = self._create_processing_form()
        forms_layout.addWidget(self.processing_group)
        
        forms_layout.addStretch()
        main_splitter.addWidget(forms_widget)
        
        # Right side: History and Totals
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Session History
        right_layout.addWidget(self._create_history_section(), stretch=2)
        
        # Cumulative Totals
        right_layout.addWidget(self._create_totals_section(), stretch=1)
        
        main_splitter.addWidget(right_widget)
        main_splitter.setSizes([500, 600])
        
        content_layout.addWidget(main_splitter, stretch=1)
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        # Initial visibility
        self._update_form_visibility()
    
    def _setup_timer(self):
        """Set up timer for active session tracking."""
        self.session_timer = QTimer()
        self.session_timer.timeout.connect(self._update_session_display)
        self.session_timer.setInterval(1000)  # Update every second
    
    def _create_session_tracker(self) -> QGroupBox:
        """Create the active session tracker panel."""
        group = QGroupBox("🕐 Active Session Tracker")
        layout = QHBoxLayout(group)
        
        # Left side: Time tracking
        time_layout = QFormLayout()
        
        self.session_start_label = QLabel("--:--:--")
        self.session_start_label.setStyleSheet("font-weight: bold;")
        time_layout.addRow("Session Start:", self.session_start_label)
        
        self.session_duration_label = QLabel("00:00:00")
        self.session_duration_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        time_layout.addRow("Duration:", self.session_duration_label)
        
        # Starting balance - manual entry
        self.starting_balance_spin = QDoubleSpinBox()
        self.starting_balance_spin.setRange(0, 999999999)
        self.starting_balance_spin.setPrefix("$")
        self.starting_balance_spin.setDecimals(0)
        self.starting_balance_spin.valueChanged.connect(self._update_session_profit)
        time_layout.addRow("Starting Balance:", self.starting_balance_spin)
        
        layout.addLayout(time_layout)
        
        # Middle: Current stats
        stats_layout = QFormLayout()
        
        # Current balance with refresh button to read from ledger
        current_balance_layout = QHBoxLayout()
        self.current_balance_spin = QDoubleSpinBox()
        self.current_balance_spin.setRange(0, 999999999)
        self.current_balance_spin.setPrefix("$")
        self.current_balance_spin.setDecimals(0)
        self.current_balance_spin.valueChanged.connect(self._update_session_profit)
        current_balance_layout.addWidget(self.current_balance_spin)
        
        self.refresh_balance_btn = QPushButton("📖")
        self.refresh_balance_btn.setToolTip("Read current balance from Ledger")
        self.refresh_balance_btn.setMaximumWidth(30)
        self.refresh_balance_btn.clicked.connect(self._read_balance_from_ledger)
        current_balance_layout.addWidget(self.refresh_balance_btn)
        
        stats_layout.addRow("Current Balance:", current_balance_layout)
        
        self.session_profit_label = QLabel("$0")
        self.session_profit_label.setStyleSheet("font-weight: bold; color: #2e7d32;")
        stats_layout.addRow("Session Profit:", self.session_profit_label)
        
        self.profit_per_hour_label = QLabel("$0/hr")
        stats_layout.addRow("Profit/Hour:", self.profit_per_hour_label)
        
        layout.addLayout(stats_layout)
        
        # Right side: Material stats
        material_layout = QFormLayout()
        
        self.material_tons_label = QLabel("0")
        material_layout.addRow("Material (yd³):", self.material_tons_label)
        
        self.dollars_per_ton_label = QLabel("$0")
        material_layout.addRow("$/yd³ Average:", self.dollars_per_ton_label)
        
        layout.addLayout(material_layout)
        
        # Session control buttons
        btn_layout = QVBoxLayout()
        
        self.start_session_btn = QPushButton("▶️ Start Session")
        self.start_session_btn.clicked.connect(self._start_session)
        btn_layout.addWidget(self.start_session_btn)
        
        self.end_session_btn = QPushButton("⏹️ End Session")
        self.end_session_btn.clicked.connect(self._end_session)
        self.end_session_btn.setEnabled(False)
        btn_layout.addWidget(self.end_session_btn)
        
        layout.addLayout(btn_layout)
        
        return group
    
    def _create_session_type_selector(self) -> QGroupBox:
        """Create the session type selector."""
        group = QGroupBox("📋 Session Type")
        layout = QHBoxLayout(group)
        
        self.session_type_combo = QComboBox()
        self.session_type_combo.addItems([
            "Hauling - Mining/transport operations",
            "Processing - Wash plant/refining operations",
            "Infrastructure - Roads, ramps, site prep",
            "Mixed Operations - Combined revenue + prep",
            "Equipment Testing - Vehicle trials",
            "Exploration - Site surveying",
        ])
        self.session_type_combo.currentIndexChanged.connect(self._update_form_visibility)
        layout.addWidget(self.session_type_combo)
        
        return group
    
    def _create_hauling_form(self) -> QGroupBox:
        """Create the hauling session entry form."""
        group = QGroupBox("🚚 Hauling Session")
        layout = QVBoxLayout(group)
        
        # Top row: Date and Location
        row1 = QHBoxLayout()
        
        row1.addWidget(QLabel("Date:"))
        self.hauling_date = QDateEdit()
        self.hauling_date.setDate(QDate.currentDate())
        self.hauling_date.setCalendarPopup(True)
        row1.addWidget(self.hauling_date)
        
        row1.addWidget(QLabel("Location:"))
        self.hauling_location = QComboBox()
        self.hauling_location.addItem("-- Select Location --")
        for loc in self.locations:
            self.hauling_location.addItem(loc['name'])
        row1.addWidget(self.hauling_location, stretch=1)
        
        layout.addLayout(row1)
        
        # Vehicle selection with auto-fill specs
        row2 = QHBoxLayout()
        
        row2.addWidget(QLabel("Vehicle:"))
        self.hauling_vehicle = QComboBox()
        self.hauling_vehicle.addItem("-- Select Vehicle --")
        for v in self.vehicles:
            self.hauling_vehicle.addItem(v['name'])
        self.hauling_vehicle.currentIndexChanged.connect(self._on_vehicle_selected)
        row2.addWidget(self.hauling_vehicle, stretch=1)
        
        layout.addLayout(row2)
        
        # Vehicle specs display (auto-filled)
        specs_frame = QFrame()
        specs_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        specs_frame.setStyleSheet("background-color: #f5f5f5; padding: 5px;")
        specs_layout = QHBoxLayout(specs_frame)
        specs_layout.setContentsMargins(10, 5, 10, 5)
        
        self.vehicle_capacity_label = QLabel("Capacity: -- yd³")
        specs_layout.addWidget(self.vehicle_capacity_label)
        
        self.vehicle_fuel_use_label = QLabel("Fuel Use: -- L/hr")
        specs_layout.addWidget(self.vehicle_fuel_use_label)
        
        self.vehicle_tank_label = QLabel("Tank: -- L")
        specs_layout.addWidget(self.vehicle_tank_label)
        
        specs_layout.addStretch()
        layout.addWidget(specs_frame)
        
        # Loads and volume
        row3 = QHBoxLayout()
        
        row3.addWidget(QLabel("Truck Loads:"))
        self.hauling_loads = QSpinBox()
        self.hauling_loads.setRange(0, 9999)
        self.hauling_loads.valueChanged.connect(self._calc_hauling_volume)
        row3.addWidget(self.hauling_loads)
        
        row3.addWidget(QLabel("Volume Moved:"))
        self.hauling_volume_label = QLabel("0 yd³")
        self.hauling_volume_label.setStyleSheet("font-weight: bold;")
        row3.addWidget(self.hauling_volume_label)
        
        row3.addStretch()
        layout.addLayout(row3)
        
        # Stockpile
        row4 = QHBoxLayout()
        
        row4.addWidget(QLabel("Stockpile:"))
        self.hauling_stockpile = QComboBox()
        self.hauling_stockpile.addItem("-- Select Stockpile --")
        for loc in self.stockpiles:
            self.hauling_stockpile.addItem(loc['name'])
        row4.addWidget(self.hauling_stockpile, stretch=1)
        
        layout.addLayout(row4)
        
        # Duration and fuel
        row5 = QHBoxLayout()
        
        row5.addWidget(QLabel("Duration (hrs):"))
        self.hauling_duration = QDoubleSpinBox()
        self.hauling_duration.setRange(0, 24)
        self.hauling_duration.setDecimals(2)
        self.hauling_duration.setSingleStep(0.25)
        self.hauling_duration.valueChanged.connect(self._calc_hauling_fuel)
        row5.addWidget(self.hauling_duration)
        
        row5.addWidget(QLabel("Fuel Used:"))
        self.hauling_fuel_label = QLabel("0 L")
        row5.addWidget(self.hauling_fuel_label)
        
        row5.addWidget(QLabel("Fuel Cost:"))
        self.hauling_fuel_cost_label = QLabel("$0.00")
        self.hauling_fuel_cost_label.setStyleSheet("color: #c62828;")
        row5.addWidget(self.hauling_fuel_cost_label)
        
        row5.addStretch()
        layout.addLayout(row5)
        
        # Notes
        row6 = QHBoxLayout()
        row6.addWidget(QLabel("Notes:"))
        self.hauling_notes = QLineEdit()
        self.hauling_notes.setPlaceholderText("Optional notes...")
        row6.addWidget(self.hauling_notes, stretch=1)
        layout.addLayout(row6)
        
        # Save button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.save_hauling_btn = QPushButton("💾 Save Hauling Session")
        self.save_hauling_btn.clicked.connect(self._save_hauling_session)
        btn_layout.addWidget(self.save_hauling_btn)
        layout.addLayout(btn_layout)
        
        return group
    
    def _create_processing_form(self) -> QGroupBox:
        """Create the processing session entry form."""
        group = QGroupBox("🏭 Processing Session")
        layout = QVBoxLayout(group)
        
        # Top row: Date and Processor
        row1 = QHBoxLayout()
        
        row1.addWidget(QLabel("Date:"))
        self.processing_date = QDateEdit()
        self.processing_date.setDate(QDate.currentDate())
        self.processing_date.setCalendarPopup(True)
        row1.addWidget(self.processing_date)
        
        row1.addWidget(QLabel("Processor:"))
        self.processor_type = QComboBox()
        self.processor_type.addItems(self.processor_types)
        row1.addWidget(self.processor_type)
        
        row1.addStretch()
        layout.addLayout(row1)
        
        # Material and volume
        row2 = QHBoxLayout()
        
        row2.addWidget(QLabel("Material:"))
        self.processing_material = QLineEdit()
        self.processing_material.setPlaceholderText("e.g., PayDirt, Gravel, Crushed Rock")
        row2.addWidget(self.processing_material, stretch=1)
        
        row2.addWidget(QLabel("Input Volume:"))
        self.processing_volume = QDoubleSpinBox()
        self.processing_volume.setRange(0, 99999)
        self.processing_volume.setDecimals(1)
        self.processing_volume.setSuffix(" yd³")
        self.processing_volume.valueChanged.connect(self._calc_processing_totals)
        row2.addWidget(self.processing_volume)
        
        layout.addLayout(row2)
        
        # Ores extracted table
        ores_group = QGroupBox("💎 Ores Extracted")
        ores_layout = QVBoxLayout(ores_group)
        
        self.ores_table = QTableWidget()
        self.ores_table.setColumnCount(4)
        self.ores_table.setHorizontalHeaderLabels(["Ore Type", "Quantity", "Unit Price", "Subtotal"])
        self.ores_table.setRowCount(5)
        self.ores_table.setMaximumHeight(180)
        
        header = self.ores_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        
        # Initialize ore rows
        for row in range(5):
            # Ore type dropdown
            ore_combo = QComboBox()
            ore_combo.addItem("-- Select --")
            ore_combo.addItems(self.ore_types)
            ore_combo.currentIndexChanged.connect(self._on_ore_selected)
            self.ores_table.setCellWidget(row, 0, ore_combo)
            
            # Quantity spinbox
            qty_spin = QSpinBox()
            qty_spin.setRange(0, 99999)
            qty_spin.valueChanged.connect(self._calc_processing_totals)
            self.ores_table.setCellWidget(row, 1, qty_spin)
            
            # Unit price (auto-filled, editable)
            price_spin = QDoubleSpinBox()
            price_spin.setRange(0, 999999)
            price_spin.setPrefix("$")
            price_spin.setDecimals(0)
            price_spin.valueChanged.connect(self._calc_processing_totals)
            self.ores_table.setCellWidget(row, 2, price_spin)
            
            # Subtotal (display only)
            subtotal_item = QTableWidgetItem("$0")
            subtotal_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            subtotal_item.setFlags(subtotal_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.ores_table.setItem(row, 3, subtotal_item)
        
        ores_layout.addWidget(self.ores_table)
        
        # Ores total
        total_row = QHBoxLayout()
        total_row.addStretch()
        total_row.addWidget(QLabel("Total Ores:"))
        self.total_ores_label = QLabel("0")
        self.total_ores_label.setStyleSheet("font-weight: bold;")
        total_row.addWidget(self.total_ores_label)
        total_row.addWidget(QLabel("="))
        self.total_ores_value_label = QLabel("$0")
        self.total_ores_value_label.setStyleSheet("font-weight: bold; color: #2e7d32;")
        total_row.addWidget(self.total_ores_value_label)
        ores_layout.addLayout(total_row)
        
        layout.addWidget(ores_group)
        
        # Processing cost
        cost_row = QHBoxLayout()
        cost_row.addWidget(QLabel("Processing Cost:"))
        self.processing_cost = QDoubleSpinBox()
        self.processing_cost.setRange(0, 999999)
        self.processing_cost.setPrefix("$")
        self.processing_cost.setDecimals(0)
        self.processing_cost.valueChanged.connect(self._calc_processing_totals)
        cost_row.addWidget(self.processing_cost)
        cost_row.addWidget(QLabel("(fuel, electricity, labor)"))
        cost_row.addStretch()
        layout.addLayout(cost_row)
        
        # Session summary
        summary_group = QGroupBox("📊 Session Summary")
        summary_layout = QFormLayout(summary_group)
        
        self.gross_revenue_label = QLabel("$0")
        self.gross_revenue_label.setStyleSheet("font-weight: bold;")
        summary_layout.addRow("Gross Revenue:", self.gross_revenue_label)
        
        self.net_revenue_label = QLabel("$0")
        self.net_revenue_label.setStyleSheet("font-weight: bold; color: #2e7d32;")
        summary_layout.addRow("Net Revenue:", self.net_revenue_label)
        
        self.revenue_per_yd3_label = QLabel("$0")
        summary_layout.addRow("Revenue per yd³:", self.revenue_per_yd3_label)
        
        self.company_share_label = QLabel("$0 (90%)")
        summary_layout.addRow("Company Share:", self.company_share_label)
        
        self.personal_share_label = QLabel("$0 (10%)")
        summary_layout.addRow("Personal Share:", self.personal_share_label)
        
        layout.addWidget(summary_group)
        
        # Save button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.save_processing_btn = QPushButton("💾 Save Processing Session")
        self.save_processing_btn.clicked.connect(self._save_processing_session)
        btn_layout.addWidget(self.save_processing_btn)
        layout.addLayout(btn_layout)
        
        return group
    
    def _create_history_section(self) -> QGroupBox:
        """Create the session history section."""
        group = QGroupBox("📜 Session History")
        layout = QVBoxLayout(group)
        
        # Tab widget for hauling/processing history
        self.history_tabs = QTabWidget()
        
        # Hauling History Tab
        hauling_widget = QWidget()
        hauling_layout = QVBoxLayout(hauling_widget)
        
        self.hauling_history_table = QTableWidget()
        self.hauling_history_table.setColumnCount(9)
        self.hauling_history_table.setHorizontalHeaderLabels([
            "Date", "Location", "Vehicle", "Loads", "Volume", 
            "Stockpile", "Duration", "Fuel Cost", "Notes"
        ])
        self.hauling_history_table.setAlternatingRowColors(True)
        self.hauling_history_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        
        header = self.hauling_history_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(8, QHeaderView.ResizeMode.Stretch)  # Notes stretch
        
        hauling_layout.addWidget(self.hauling_history_table)
        
        # Hauling history buttons
        h_btn_layout = QHBoxLayout()
        self.delete_hauling_btn = QPushButton("🗑️ Delete Selected")
        self.delete_hauling_btn.clicked.connect(self._delete_hauling_session)
        h_btn_layout.addWidget(self.delete_hauling_btn)
        h_btn_layout.addStretch()
        hauling_layout.addLayout(h_btn_layout)
        
        self.history_tabs.addTab(hauling_widget, "🚚 Hauling History")
        
        # Processing History Tab
        processing_widget = QWidget()
        processing_layout = QVBoxLayout(processing_widget)
        
        self.processing_history_table = QTableWidget()
        self.processing_history_table.setColumnCount(8)
        self.processing_history_table.setHorizontalHeaderLabels([
            "Date", "Processor", "Material", "Input (yd³)", 
            "Ores", "Gross", "Net", "$/yd³"
        ])
        self.processing_history_table.setAlternatingRowColors(True)
        self.processing_history_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        
        header = self.processing_history_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Material stretch
        
        processing_layout.addWidget(self.processing_history_table)
        
        # Processing history buttons
        p_btn_layout = QHBoxLayout()
        self.delete_processing_btn = QPushButton("🗑️ Delete Selected")
        self.delete_processing_btn.clicked.connect(self._delete_processing_session)
        p_btn_layout.addWidget(self.delete_processing_btn)
        p_btn_layout.addStretch()
        processing_layout.addLayout(p_btn_layout)
        
        self.history_tabs.addTab(processing_widget, "🏭 Processing History")
        
        layout.addWidget(self.history_tabs)
        
        return group
    
    def _create_totals_section(self) -> QGroupBox:
        """Create the cumulative totals section."""
        group = QGroupBox("📈 Cumulative Totals")
        layout = QHBoxLayout(group)
        
        # Hauling totals
        hauling_group = QGroupBox("🚚 Hauling Operations")
        hauling_layout = QFormLayout(hauling_group)
        
        self.total_hauling_sessions_label = QLabel("0")
        hauling_layout.addRow("Sessions:", self.total_hauling_sessions_label)
        
        self.total_material_moved_label = QLabel("0 yd³")
        hauling_layout.addRow("Material Moved:", self.total_material_moved_label)
        
        self.total_fuel_used_label = QLabel("0 L")
        hauling_layout.addRow("Fuel Used:", self.total_fuel_used_label)
        
        self.total_fuel_cost_label = QLabel("$0")
        self.total_fuel_cost_label.setStyleSheet("color: #c62828;")
        hauling_layout.addRow("Fuel Cost:", self.total_fuel_cost_label)
        
        layout.addWidget(hauling_group)
        
        # Processing totals
        processing_group = QGroupBox("🏭 Processing Operations")
        processing_layout = QFormLayout(processing_group)
        
        self.total_processing_sessions_label = QLabel("0")
        processing_layout.addRow("Sessions:", self.total_processing_sessions_label)
        
        self.total_material_processed_label = QLabel("0 yd³")
        processing_layout.addRow("Processed:", self.total_material_processed_label)
        
        self.total_ores_extracted_label = QLabel("0")
        processing_layout.addRow("Ores Extracted:", self.total_ores_extracted_label)
        
        self.total_revenue_label = QLabel("$0")
        self.total_revenue_label.setStyleSheet("color: #2e7d32; font-weight: bold;")
        processing_layout.addRow("Total Revenue:", self.total_revenue_label)
        
        layout.addWidget(processing_group)
        
        return group
    
    def _update_form_visibility(self):
        """Show/hide forms based on session type selection."""
        session_type = self.session_type_combo.currentIndex()
        
        # 0 = Hauling, 1 = Processing
        self.hauling_group.setVisible(session_type in [0, 3])  # Hauling or Mixed
        self.processing_group.setVisible(session_type in [1, 3])  # Processing or Mixed
    
    def _on_vehicle_selected(self, index):
        """Handle vehicle selection - auto-fill specs."""
        if index <= 0:  # "Select" option
            self.vehicle_capacity_label.setText("Capacity: -- yd³")
            self.vehicle_fuel_use_label.setText("Fuel Use: -- L/hr")
            self.vehicle_tank_label.setText("Tank: -- L")
            return
        
        vehicle = self.vehicles[index - 1]  # -1 for "Select" option
        
        self.vehicle_capacity_label.setText(f"Capacity: {vehicle['capacity_yd3']:.1f} yd³")
        self.vehicle_fuel_use_label.setText(f"Fuel Use: {vehicle['fuel_use_lph']:.0f} L/hr")
        self.vehicle_tank_label.setText(f"Tank: {vehicle['fuel_capacity_l']:,.0f} L")
        
        # Recalculate if loads already entered
        self._calc_hauling_volume()
        self._calc_hauling_fuel()
    
    def _on_ore_selected(self, index):
        """Handle ore selection - auto-fill price."""
        # Get the combo box that triggered this
        sender = self.sender()
        if not sender:
            return
        
        # Find the row
        for row in range(self.ores_table.rowCount()):
            if self.ores_table.cellWidget(row, 0) == sender:
                if index <= 0:
                    # Clear price
                    price_spin = self.ores_table.cellWidget(row, 2)
                    price_spin.setValue(0)
                else:
                    # Get price from ore_prices dictionary
                    ore_name = sender.currentText()
                    price = self.ore_prices.get(ore_name, 0)
                    price_spin = self.ores_table.cellWidget(row, 2)
                    price_spin.setValue(price)
                break
        
        self._calc_processing_totals()
    
    def _calc_hauling_volume(self):
        """Calculate volume moved based on loads and vehicle capacity."""
        vehicle_idx = self.hauling_vehicle.currentIndex()
        if vehicle_idx <= 0:
            self.hauling_volume_label.setText("0 yd³")
            return
        
        vehicle = self.vehicles[vehicle_idx - 1]
        loads = self.hauling_loads.value()
        volume = loads * vehicle['capacity_yd3']
        
        self.hauling_volume_label.setText(f"{volume:,.1f} yd³")
    
    def _calc_hauling_fuel(self):
        """Calculate fuel used and cost based on duration."""
        vehicle_idx = self.hauling_vehicle.currentIndex()
        if vehicle_idx <= 0:
            self.hauling_fuel_label.setText("0 L")
            self.hauling_fuel_cost_label.setText("$0.00")
            return
        
        vehicle = self.vehicles[vehicle_idx - 1]
        duration = self.hauling_duration.value()
        
        fuel_used = duration * vehicle['fuel_use_lph']
        fuel_cost = fuel_used * self.FUEL_PRICE_PER_LITER
        
        self.hauling_fuel_label.setText(f"{fuel_used:,.0f} L")
        self.hauling_fuel_cost_label.setText(f"${fuel_cost:,.2f}")
    
    def _calc_processing_totals(self):
        """Calculate processing session totals."""
        total_ores = 0
        total_value = 0
        
        for row in range(self.ores_table.rowCount()):
            qty_spin = self.ores_table.cellWidget(row, 1)
            price_spin = self.ores_table.cellWidget(row, 2)
            
            qty = qty_spin.value()
            price = price_spin.value()
            subtotal = qty * price
            
            total_ores += qty
            total_value += subtotal
            
            # Update subtotal cell
            item = self.ores_table.item(row, 3)
            if item:
                item.setText(f"${subtotal:,.0f}")
        
        # Update totals
        self.total_ores_label.setText(str(total_ores))
        self.total_ores_value_label.setText(f"${total_value:,.0f}")
        
        # Calculate net
        gross = total_value
        cost = self.processing_cost.value()
        net = gross - cost
        
        volume = self.processing_volume.value()
        per_yd3 = net / volume if volume > 0 else 0
        
        company_share = net * self.COMPANY_SPLIT
        personal_share = net * self.PERSONAL_SPLIT
        
        self.gross_revenue_label.setText(f"${gross:,.0f}")
        self.net_revenue_label.setText(f"${net:,.0f}")
        self.revenue_per_yd3_label.setText(f"${per_yd3:,.2f}")
        self.company_share_label.setText(f"${company_share:,.0f} (90%)")
        self.personal_share_label.setText(f"${personal_share:,.0f} (10%)")
    
    def _read_balance_from_ledger(self):
        """Read the current balance from the Ledger tab."""
        if self.ledger_tab is None:
            QMessageBox.warning(
                self, "Ledger Not Available",
                "Could not access the Ledger tab. Please enter balance manually."
            )
            return
        
        try:
            balances = self.ledger_tab.get_current_balances()
            # Use personal balance only (ore/oil sales go through Personal account)
            personal_balance = balances.get('personal', 0)
            
            # Update current balance from ledger
            self.current_balance_spin.setValue(personal_balance)
            
        except Exception as e:
            QMessageBox.warning(
                self, "Error",
                f"Could not read balance from Ledger:\n{str(e)}"
            )
    
    def set_ledger_tab(self, ledger_tab):
        """Set reference to the Ledger tab for balance reading."""
        self.ledger_tab = ledger_tab
    
    def _start_session(self):
        """Start a new tracking session."""
        self.session_active = True
        self.session_start_time = datetime.now()
        self.session_start_balance = self.starting_balance_spin.value()
        
        self.session_start_label.setText(self.session_start_time.strftime("%H:%M:%S"))
        self.start_session_btn.setEnabled(False)
        self.end_session_btn.setEnabled(True)
        
        self.session_timer.start()
    
    def _end_session(self):
        """End the current tracking session."""
        self.session_active = False
        self.session_timer.stop()
        
        self.start_session_btn.setEnabled(True)
        self.end_session_btn.setEnabled(False)
        
        # Calculate session duration in decimal hours
        if self.session_start_time:
            elapsed = datetime.now() - self.session_start_time
            duration_hours = elapsed.total_seconds() / 3600
            
            # Auto-fill the hauling duration field
            self.hauling_duration.setValue(round(duration_hours, 2))
        
        # Calculate final stats
        self._update_session_profit()
    
    def _update_session_display(self):
        """Update the session timer display."""
        if not self.session_active or not self.session_start_time:
            return
        
        elapsed = datetime.now() - self.session_start_time
        hours, remainder = divmod(int(elapsed.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        
        self.session_duration_label.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")
        
        # Update profit/hour
        self._update_session_profit()
    
    def _update_session_profit(self):
        """Update session profit calculations."""
        current = self.current_balance_spin.value()
        start = self.starting_balance_spin.value()
        profit = current - start
        
        self.session_profit_label.setText(f"${profit:,.0f}")
        
        if profit >= 0:
            self.session_profit_label.setStyleSheet("font-weight: bold; color: #2e7d32;")
        else:
            self.session_profit_label.setStyleSheet("font-weight: bold; color: #c62828;")
        
        # Calculate profit per hour
        if self.session_active and self.session_start_time:
            elapsed = (datetime.now() - self.session_start_time).total_seconds() / 3600
            if elapsed > 0:
                per_hour = profit / elapsed
                self.profit_per_hour_label.setText(f"${per_hour:,.0f}/hr")
    
    def _save_hauling_session(self):
        """Save the current hauling session."""
        # Validate
        if self.hauling_vehicle.currentIndex() <= 0:
            QMessageBox.warning(self, "Validation", "Please select a vehicle.")
            return
        
        if self.hauling_loads.value() <= 0:
            QMessageBox.warning(self, "Validation", "Please enter the number of loads.")
            return
        
        # Build session data
        vehicle = self.vehicles[self.hauling_vehicle.currentIndex() - 1]
        volume = self.hauling_loads.value() * vehicle['capacity_yd3']
        fuel_used = self.hauling_duration.value() * vehicle['fuel_use_lph']
        fuel_cost = fuel_used * self.FUEL_PRICE_PER_LITER
        
        session = {
            'date': self.hauling_date.date().toString("yyyy-MM-dd"),
            'location': self.hauling_location.currentText(),
            'vehicle': vehicle['name'],
            'loads': self.hauling_loads.value(),
            'volume': volume,
            'stockpile': self.hauling_stockpile.currentText(),
            'duration': self.hauling_duration.value(),
            'fuel_used': fuel_used,
            'fuel_cost': fuel_cost,
            'notes': self.hauling_notes.text(),
        }
        
        self.hauling_sessions.append(session)
        self._refresh_hauling_history()
        self._update_totals()
        
        # Clear form
        self.hauling_loads.setValue(0)
        self.hauling_duration.setValue(0)
        self.hauling_notes.clear()
        
        QMessageBox.information(self, "Saved", "Hauling session saved!")
    
    def _save_processing_session(self):
        """Save the current processing session."""
        # Validate
        if self.processing_volume.value() <= 0:
            QMessageBox.warning(self, "Validation", "Please enter input volume.")
            return
        
        # Collect ores
        ores = []
        total_ores = 0
        gross_revenue = 0
        
        for row in range(self.ores_table.rowCount()):
            ore_combo = self.ores_table.cellWidget(row, 0)
            qty_spin = self.ores_table.cellWidget(row, 1)
            price_spin = self.ores_table.cellWidget(row, 2)
            
            if ore_combo.currentIndex() > 0 and qty_spin.value() > 0:
                ores.append({
                    'ore': ore_combo.currentText(),
                    'qty': qty_spin.value(),
                    'price': price_spin.value(),
                    'subtotal': qty_spin.value() * price_spin.value(),
                })
                total_ores += qty_spin.value()
                gross_revenue += qty_spin.value() * price_spin.value()
        
        net_revenue = gross_revenue - self.processing_cost.value()
        
        session = {
            'date': self.processing_date.date().toString("yyyy-MM-dd"),
            'processor': self.processor_type.currentText(),
            'material': self.processing_material.text(),
            'input_volume': self.processing_volume.value(),
            'ores': ores,
            'total_ores': total_ores,
            'gross_revenue': gross_revenue,
            'processing_cost': self.processing_cost.value(),
            'net_revenue': net_revenue,
            'per_yd3': net_revenue / self.processing_volume.value() if self.processing_volume.value() > 0 else 0,
        }
        
        self.processing_sessions.append(session)
        self._refresh_processing_history()
        self._update_totals()
        
        # Clear form
        self.processing_material.clear()
        self.processing_volume.setValue(0)
        self.processing_cost.setValue(0)
        for row in range(self.ores_table.rowCount()):
            self.ores_table.cellWidget(row, 0).setCurrentIndex(0)
            self.ores_table.cellWidget(row, 1).setValue(0)
            self.ores_table.cellWidget(row, 2).setValue(0)
        
        QMessageBox.information(self, "Saved", "Processing session saved!")
    
    def _refresh_hauling_history(self):
        """Refresh the hauling history table."""
        self.hauling_history_table.setRowCount(len(self.hauling_sessions))
        
        for row, session in enumerate(self.hauling_sessions):
            self.hauling_history_table.setItem(row, 0, QTableWidgetItem(session['date']))
            self.hauling_history_table.setItem(row, 1, QTableWidgetItem(session['location']))
            self.hauling_history_table.setItem(row, 2, QTableWidgetItem(session['vehicle']))
            self.hauling_history_table.setItem(row, 3, QTableWidgetItem(str(session['loads'])))
            self.hauling_history_table.setItem(row, 4, QTableWidgetItem(f"{session['volume']:,.1f}"))
            self.hauling_history_table.setItem(row, 5, QTableWidgetItem(session['stockpile']))
            self.hauling_history_table.setItem(row, 6, QTableWidgetItem(f"{session['duration']:.2f}"))
            self.hauling_history_table.setItem(row, 7, QTableWidgetItem(f"${session['fuel_cost']:,.2f}"))
            self.hauling_history_table.setItem(row, 8, QTableWidgetItem(session['notes']))
    
    def _refresh_processing_history(self):
        """Refresh the processing history table."""
        self.processing_history_table.setRowCount(len(self.processing_sessions))
        
        for row, session in enumerate(self.processing_sessions):
            self.processing_history_table.setItem(row, 0, QTableWidgetItem(session['date']))
            self.processing_history_table.setItem(row, 1, QTableWidgetItem(session['processor']))
            self.processing_history_table.setItem(row, 2, QTableWidgetItem(session['material']))
            self.processing_history_table.setItem(row, 3, QTableWidgetItem(f"{session['input_volume']:,.1f}"))
            self.processing_history_table.setItem(row, 4, QTableWidgetItem(str(session['total_ores'])))
            self.processing_history_table.setItem(row, 5, QTableWidgetItem(f"${session['gross_revenue']:,.0f}"))
            self.processing_history_table.setItem(row, 6, QTableWidgetItem(f"${session['net_revenue']:,.0f}"))
            self.processing_history_table.setItem(row, 7, QTableWidgetItem(f"${session['per_yd3']:,.2f}"))
    
    def _delete_hauling_session(self):
        """Delete selected hauling session."""
        row = self.hauling_history_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a session to delete.")
            return
        
        reply = QMessageBox.question(
            self, "Delete Session",
            "Delete this hauling session?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            del self.hauling_sessions[row]
            self._refresh_hauling_history()
            self._update_totals()
    
    def _delete_processing_session(self):
        """Delete selected processing session."""
        row = self.processing_history_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a session to delete.")
            return
        
        reply = QMessageBox.question(
            self, "Delete Session",
            "Delete this processing session?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            del self.processing_sessions[row]
            self._refresh_processing_history()
            self._update_totals()
    
    def _update_totals(self):
        """Update cumulative totals."""
        # Hauling totals
        total_volume = sum(s['volume'] for s in self.hauling_sessions)
        total_fuel = sum(s['fuel_used'] for s in self.hauling_sessions)
        total_fuel_cost = sum(s['fuel_cost'] for s in self.hauling_sessions)
        
        self.total_hauling_sessions_label.setText(str(len(self.hauling_sessions)))
        self.total_material_moved_label.setText(f"{total_volume:,.1f} yd³")
        self.total_fuel_used_label.setText(f"{total_fuel:,.0f} L")
        self.total_fuel_cost_label.setText(f"${total_fuel_cost:,.2f}")
        
        # Processing totals
        total_processed = sum(s['input_volume'] for s in self.processing_sessions)
        total_ores = sum(s['total_ores'] for s in self.processing_sessions)
        total_revenue = sum(s['net_revenue'] for s in self.processing_sessions)
        
        self.total_processing_sessions_label.setText(str(len(self.processing_sessions)))
        self.total_material_processed_label.setText(f"{total_processed:,.1f} yd³")
        self.total_ores_extracted_label.setText(str(total_ores))
        self.total_revenue_label.setText(f"${total_revenue:,.0f}")
        
        # Update session tracker material stats
        self.material_tons_label.setText(f"{total_volume + total_processed:,.1f}")
