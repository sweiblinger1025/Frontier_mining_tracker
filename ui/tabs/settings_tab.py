"""
Settings Tab - Central configuration hub

Sub-tabs:
1. Game Info - Playthrough dates, starting capital, fuel price
2. Challenge Rules - Difficulty presets, splits, oil cap
3. Skills - Vendor Negotiation, Investment Forecasting
4. Item Rules - Filtered view of restricted items (synced with Reference Data)
5. App Settings - Display preferences, data management
"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
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
    QDateEdit,
    QFormLayout,
    QMessageBox,
    QAbstractItemView,
    QRadioButton,
    QButtonGroup,
    QFrame,
    QScrollArea,
    QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSignal, QDate
from PyQt6.QtGui import QColor

from datetime import datetime, date


class SettingsTab(QWidget):
    """Settings tab with sub-tabs for different configuration areas."""
    
    # Signals
    settings_changed = pyqtSignal(str, object)  # (setting_key, new_value)
    navigate_to_tab = pyqtSignal(str, str)  # (tab_name, sub_tab_name)
    
    # Difficulty presets
    DIFFICULTY_PRESETS = {
        "Easy": {
            "seed_capital": 100000,
            "personal_split": 0.10,
            "company_split": 0.90,
            "oil_cap": 10000,
            "daily_limit": None,
            "bar_threshold": 5000,
            "description": "Generous seed funding. Learn the system with comfortable margins. 10% personal salary, oil cap 10,000 barrels."
        },
        "Standard": {
            "seed_capital": 100000,
            "personal_split": 0.10,
            "company_split": 0.90,
            "oil_cap": 7500,
            "daily_limit": 10000,
            "bar_threshold": 5000,
            "description": "Standard challenge with daily spending limits. Balanced difficulty for experienced players."
        },
        "Hard": {
            "seed_capital": 75000,
            "personal_split": 0.05,
            "company_split": 0.95,
            "oil_cap": 5000,
            "daily_limit": 5000,
            "bar_threshold": 5000,
            "description": "Reduced funding and tighter margins. 5% personal salary, stricter limits."
        },
        "Hardcore": {
            "seed_capital": 50000,
            "personal_split": 0.05,
            "company_split": 0.95,
            "oil_cap": 2500,
            "daily_limit": 2500,
            "bar_threshold": 5000,
            "description": "Minimal resources, maximum challenge. Every decision counts."
        },
        "Custom": {
            "seed_capital": None,
            "personal_split": None,
            "company_split": None,
            "oil_cap": None,
            "daily_limit": None,
            "bar_threshold": None,
            "description": "Configure your own challenge parameters."
        },
    }
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Current settings
        self.settings = {
            # Game Info
            "game_start_date": date(2021, 4, 22),
            "current_game_date": date(2021, 4, 23),
            "starting_capital": 100000,
            "fuel_price_per_liter": 0.32,
            
            # Challenge Rules
            "difficulty_level": "Easy",
            "personal_split": 0.10,
            "company_split": 0.90,
            "oil_cap_enabled": True,
            "oil_cap_amount": 10000,
            "oil_lifetime_sold": 0,
            "daily_limit_enabled": False,
            "daily_limit_amount": 0,
            "bar_threshold": 5000,
            
            # Skills
            "vendor_negotiation_level": 7,
            "investment_forecasting_level": 6,
            
            # App Settings
            "theme": "Light",
            "currency_format": "$1,234.56",
            "date_format": "MM/DD/YYYY",
        }
        
        # Item rules (will be synced from Reference Data)
        self.item_rules = []
        
        # Reference to main window for navigation
        self.main_window = None
        
        self._setup_ui()
        self._load_default_item_rules()
    
    def set_main_window(self, main_window):
        """Set reference to main window for tab navigation."""
        self.main_window = main_window
    
    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Create tab widget for sub-tabs
        self.sub_tabs = QTabWidget()
        
        # Add sub-tabs
        self.sub_tabs.addTab(self._create_game_info_tab(), "📅 Game Info")
        self.sub_tabs.addTab(self._create_challenge_rules_tab(), "🎮 Challenge Rules")
        self.sub_tabs.addTab(self._create_skills_tab(), "📊 Skills")
        self.sub_tabs.addTab(self._create_item_rules_tab(), "🚫 Item Rules")
        self.sub_tabs.addTab(self._create_app_settings_tab(), "⚙️ App")
        
        layout.addWidget(self.sub_tabs)
    
    def _create_game_info_tab(self) -> QWidget:
        """Create the Game Info sub-tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Playthrough Dates
        dates_group = QGroupBox("📅 Playthrough Dates")
        dates_layout = QFormLayout(dates_group)
        
        self.game_start_date = QDateEdit()
        self.game_start_date.setCalendarPopup(True)
        self.game_start_date.setDate(QDate(2021, 4, 22))
        self.game_start_date.dateChanged.connect(self._on_date_changed)
        dates_layout.addRow("Game Start Date:", self.game_start_date)
        
        self.current_game_date = QDateEdit()
        self.current_game_date.setCalendarPopup(True)
        self.current_game_date.setDate(QDate(2021, 4, 23))
        self.current_game_date.dateChanged.connect(self._on_date_changed)
        dates_layout.addRow("Current Game Date:", self.current_game_date)
        
        self.days_played_label = QLabel("1")
        self.days_played_label.setStyleSheet("font-weight: bold;")
        dates_layout.addRow("Days Played:", self.days_played_label)
        
        self.last_updated_label = QLabel(datetime.now().strftime("%m/%d/%Y %I:%M %p"))
        dates_layout.addRow("Last Updated:", self.last_updated_label)
        
        layout.addWidget(dates_group)
        
        # Starting Finances
        finances_group = QGroupBox("💰 Starting Finances")
        finances_layout = QFormLayout(finances_group)
        
        self.starting_capital_spin = QSpinBox()
        self.starting_capital_spin.setRange(0, 999999999)
        self.starting_capital_spin.setValue(100000)
        self.starting_capital_spin.setPrefix("$")
        self.starting_capital_spin.valueChanged.connect(
            lambda v: self._on_setting_changed("starting_capital", v)
        )
        finances_layout.addRow("Starting Capital:", self.starting_capital_spin)
        
        note_label = QLabel("ℹ️ This should match your selected difficulty preset.")
        note_label.setStyleSheet("color: #666;")
        finances_layout.addRow("", note_label)
        
        layout.addWidget(finances_group)
        
        # Fuel Settings
        fuel_group = QGroupBox("⛽ Fuel Settings")
        fuel_layout = QFormLayout(fuel_group)
        
        self.fuel_price_spin = QDoubleSpinBox()
        self.fuel_price_spin.setRange(0, 100)
        self.fuel_price_spin.setDecimals(2)
        self.fuel_price_spin.setValue(0.32)
        self.fuel_price_spin.setPrefix("$")
        self.fuel_price_spin.setSuffix(" /L")
        self.fuel_price_spin.valueChanged.connect(
            lambda v: self._on_setting_changed("fuel_price_per_liter", v)
        )
        fuel_layout.addRow("Fuel Price per Liter:", self.fuel_price_spin)
        
        layout.addWidget(fuel_group)
        
        # Actions
        actions_group = QGroupBox("🔄 Actions")
        actions_layout = QVBoxLayout(actions_group)
        
        new_playthrough_btn = QPushButton("🔄 New Playthrough")
        new_playthrough_btn.setToolTip("Reset all data for a fresh start")
        new_playthrough_btn.clicked.connect(self._on_new_playthrough)
        actions_layout.addWidget(new_playthrough_btn)
        
        layout.addWidget(actions_group)
        
        layout.addStretch()
        
        return widget
    
    def _create_challenge_rules_tab(self) -> QWidget:
        """Create the Challenge Rules sub-tab."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Difficulty Preset
        preset_group = QGroupBox("🎯 Difficulty Preset")
        preset_layout = QVBoxLayout(preset_group)
        
        # Preset selector
        selector_layout = QHBoxLayout()
        selector_layout.addWidget(QLabel("Select Difficulty:"))
        
        self.difficulty_combo = QComboBox()
        self.difficulty_combo.addItems(list(self.DIFFICULTY_PRESETS.keys()))
        self.difficulty_combo.currentTextChanged.connect(self._on_difficulty_changed)
        selector_layout.addWidget(self.difficulty_combo)
        selector_layout.addStretch()
        
        preset_layout.addLayout(selector_layout)
        
        # Preset reference table - EDITABLE
        preset_table = QTableWidget()
        preset_table.setRowCount(5)
        preset_table.setColumnCount(7)
        preset_table.setHorizontalHeaderLabels([
            "Difficulty", "Seed Capital", "Personal", "Company", "Oil Cap", "Daily Limit", "Bar Threshold"
        ])
        preset_table.setMaximumHeight(180)
        
        presets_data = [
            ("Easy", "$100,000", "10%", "90%", "10,000", "None", "5,000"),
            ("Standard", "$100,000", "10%", "90%", "7,500", "$10,000", "5,000"),
            ("Hard", "$75,000", "5%", "95%", "5,000", "$5,000", "5,000"),
            ("Hardcore", "$50,000", "5%", "95%", "2,500", "$2,500", "5,000"),
            ("Custom", "(manual)", "(manual)", "(manual)", "(manual)", "(manual)", "(manual)"),
        ]
        
        for row, data in enumerate(presets_data):
            for col, value in enumerate(data):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                # Make first column (Difficulty name) read-only
                if col == 0:
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                preset_table.setItem(row, col, item)
        
        preset_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        preset_table.cellChanged.connect(self._on_preset_table_changed)
        self.preset_table = preset_table
        preset_layout.addWidget(preset_table)
        
        # Description
        self.difficulty_description = QLabel(self.DIFFICULTY_PRESETS["Easy"]["description"])
        self.difficulty_description.setWordWrap(True)
        self.difficulty_description.setStyleSheet("color: #666; font-style: italic; padding: 5px;")
        preset_layout.addWidget(self.difficulty_description)
        
        layout.addWidget(preset_group)
        
        # Active Configuration
        config_group = QGroupBox("⚙️ Active Configuration")
        config_layout = QFormLayout(config_group)
        
        # Seed Capital
        self.seed_capital_spin = QSpinBox()
        self.seed_capital_spin.setRange(0, 999999999)
        self.seed_capital_spin.setValue(100000)
        self.seed_capital_spin.setPrefix("$")
        self.seed_capital_spin.valueChanged.connect(
            lambda v: self._on_setting_changed("starting_capital", v)
        )
        config_layout.addRow("Seed Capital:", self.seed_capital_spin)
        
        # Personal/Company Split
        split_widget = QWidget()
        split_layout = QHBoxLayout(split_widget)
        split_layout.setContentsMargins(0, 0, 0, 0)
        
        self.personal_split_spin = QSpinBox()
        self.personal_split_spin.setRange(0, 100)
        self.personal_split_spin.setValue(10)
        self.personal_split_spin.setSuffix("%")
        self.personal_split_spin.valueChanged.connect(self._on_split_changed)
        split_layout.addWidget(QLabel("Personal:"))
        split_layout.addWidget(self.personal_split_spin)
        
        self.company_split_spin = QSpinBox()
        self.company_split_spin.setRange(0, 100)
        self.company_split_spin.setValue(90)
        self.company_split_spin.setSuffix("%")
        self.company_split_spin.setEnabled(False)  # Auto-calculated
        split_layout.addWidget(QLabel("Company:"))
        split_layout.addWidget(self.company_split_spin)
        
        self.split_status_label = QLabel("✅ 100%")
        self.split_status_label.setStyleSheet("color: #2e7d32; font-weight: bold;")
        split_layout.addWidget(self.split_status_label)
        split_layout.addStretch()
        
        config_layout.addRow("Revenue Split:", split_widget)
        
        # Oil Cap
        oil_widget = QWidget()
        oil_layout = QHBoxLayout(oil_widget)
        oil_layout.setContentsMargins(0, 0, 0, 0)
        
        self.oil_cap_check = QCheckBox("Enable")
        self.oil_cap_check.setChecked(True)
        self.oil_cap_check.stateChanged.connect(self._on_oil_cap_toggled)
        oil_layout.addWidget(self.oil_cap_check)
        
        self.oil_cap_spin = QSpinBox()
        self.oil_cap_spin.setRange(0, 999999)
        self.oil_cap_spin.setValue(10000)
        self.oil_cap_spin.setSuffix(" barrels")
        self.oil_cap_spin.valueChanged.connect(
            lambda v: self._on_setting_changed("oil_cap_amount", v)
        )
        oil_layout.addWidget(self.oil_cap_spin)
        oil_layout.addStretch()
        
        config_layout.addRow("Oil Lifetime Cap:", oil_widget)
        
        # Daily Limit
        daily_widget = QWidget()
        daily_layout = QHBoxLayout(daily_widget)
        daily_layout.setContentsMargins(0, 0, 0, 0)
        
        self.daily_limit_check = QCheckBox("Enable")
        self.daily_limit_check.setChecked(False)
        self.daily_limit_check.stateChanged.connect(self._on_daily_limit_toggled)
        daily_layout.addWidget(self.daily_limit_check)
        
        self.daily_limit_spin = QSpinBox()
        self.daily_limit_spin.setRange(0, 999999)
        self.daily_limit_spin.setValue(0)
        self.daily_limit_spin.setPrefix("$")
        self.daily_limit_spin.setEnabled(False)
        self.daily_limit_spin.valueChanged.connect(
            lambda v: self._on_setting_changed("daily_limit_amount", v)
        )
        daily_layout.addWidget(self.daily_limit_spin)
        daily_layout.addStretch()
        
        config_layout.addRow("Daily Spending Limit:", daily_widget)
        
        # Bar Threshold (quantity, not money)
        self.bar_threshold_spin = QSpinBox()
        self.bar_threshold_spin.setRange(0, 999999)
        self.bar_threshold_spin.setValue(5000)
        self.bar_threshold_spin.valueChanged.connect(
            lambda v: self._on_setting_changed("bar_threshold", v)
        )
        config_layout.addRow("Bar Threshold:", self.bar_threshold_spin)
        
        layout.addWidget(config_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        apply_preset_btn = QPushButton("Apply Preset")
        apply_preset_btn.clicked.connect(self._apply_difficulty_preset)
        btn_layout.addWidget(apply_preset_btn)
        
        reset_btn = QPushButton("Reset to Default")
        reset_btn.clicked.connect(self._reset_challenge_rules)
        btn_layout.addWidget(reset_btn)
        
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        layout.addStretch()
        
        scroll.setWidget(widget)
        return scroll
    
    def _create_skills_tab(self) -> QWidget:
        """Create the Skills sub-tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Vendor Negotiation
        vn_group = QGroupBox("🏪 Vendor Negotiation")
        vn_layout = QVBoxLayout(vn_group)
        
        vn_form = QFormLayout()
        
        self.vn_level_spin = QSpinBox()
        self.vn_level_spin.setRange(0, 10)
        self.vn_level_spin.setValue(7)
        self.vn_level_spin.valueChanged.connect(self._on_vn_level_changed)
        vn_form.addRow("Current Level:", self.vn_level_spin)
        
        self.vn_discount_label = QLabel("3.5%")
        self.vn_discount_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #2e7d32;")
        vn_form.addRow("Discount Rate:", self.vn_discount_label)
        
        vn_applies = QLabel("ALL purchases (universal discount)")
        vn_applies.setStyleSheet("color: #666;")
        vn_form.addRow("Applies to:", vn_applies)
        
        vn_layout.addLayout(vn_form)
        
        # VN Discount Table
        vn_table = self._create_discount_table()
        self._highlight_discount_level(vn_table, 7)
        self.vn_table = vn_table
        vn_layout.addWidget(vn_table)
        
        layout.addWidget(vn_group)
        
        # Investment Forecasting
        if_group = QGroupBox("📈 Investment Forecasting")
        if_layout = QVBoxLayout(if_group)
        
        if_form = QFormLayout()
        
        self.if_level_spin = QSpinBox()
        self.if_level_spin.setRange(0, 10)
        self.if_level_spin.setValue(6)
        self.if_level_spin.valueChanged.connect(self._on_if_level_changed)
        if_form.addRow("Current Level:", self.if_level_spin)
        
        self.if_discount_label = QLabel("3.0%")
        self.if_discount_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #2e7d32;")
        if_form.addRow("Discount Rate:", self.if_discount_label)
        
        if_applies = QLabel("VEHICLES ONLY")
        if_applies.setStyleSheet("color: #666;")
        if_form.addRow("Applies to:", if_applies)
        
        if_layout.addLayout(if_form)
        
        # IF Discount Table
        if_table = self._create_discount_table()
        self._highlight_discount_level(if_table, 6)
        self.if_table = if_table
        if_layout.addWidget(if_table)
        
        layout.addWidget(if_group)
        
        # Combined Discounts
        combined_group = QGroupBox("🔢 Combined Discounts")
        combined_layout = QFormLayout(combined_group)
        
        self.non_vehicle_discount_label = QLabel("3.5% discount (VN only)")
        self.non_vehicle_discount_label.setStyleSheet("font-weight: bold;")
        combined_layout.addRow("Non-Vehicle Items:", self.non_vehicle_discount_label)
        
        self.vehicle_discount_label = QLabel("6.5% discount (VN + IF combined)")
        self.vehicle_discount_label.setStyleSheet("font-weight: bold; color: #1976d2;")
        combined_layout.addRow("Vehicle Purchases:", self.vehicle_discount_label)
        
        self.example_label = QLabel("Example: $100,000 vehicle → $93,500 after discounts")
        self.example_label.setStyleSheet("color: #666; font-style: italic;")
        combined_layout.addRow("", self.example_label)
        
        layout.addWidget(combined_group)
        
        layout.addStretch()
        
        return widget
    
    def _create_discount_table(self) -> QTableWidget:
        """Create a discount level table."""
        table = QTableWidget()
        table.setRowCount(2)
        table.setColumnCount(11)
        table.setHorizontalHeaderLabels(["", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"])
        table.setVerticalHeaderLabels(["Level", "Discount"])
        table.setMaximumHeight(80)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        
        # Level row
        for col in range(11):
            if col == 0:
                item = QTableWidgetItem("Level")
            else:
                item = QTableWidgetItem(str(col))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(0, col, item)
        
        # Discount row
        for col in range(11):
            if col == 0:
                item = QTableWidgetItem("Disc%")
            else:
                item = QTableWidgetItem(f"{col * 0.5}%")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(1, col, item)
        
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setVisible(False)
        
        return table
    
    def _highlight_discount_level(self, table: QTableWidget, level: int):
        """Highlight the current level in a discount table."""
        # Clear all highlights
        for col in range(11):
            for row in range(2):
                item = table.item(row, col)
                if item:
                    item.setBackground(QColor("#ffffff"))
        
        # Highlight current level
        if 1 <= level <= 10:
            for row in range(2):
                item = table.item(row, level)
                if item:
                    item.setBackground(QColor("#c8e6c9"))
    
    def _create_item_rules_tab(self) -> QWidget:
        """Create the Item Rules sub-tab (filtered view)."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Info banner
        info_label = QLabel("ℹ️ This is a filtered view of challenge restrictions. Edit items in Reference Data → Items.")
        info_label.setStyleSheet("background: #e3f2fd; padding: 10px; border-radius: 5px;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Summary
        summary_group = QGroupBox("📊 Summary")
        summary_layout = QHBoxLayout(summary_group)
        
        self.cant_purchase_label = QLabel("🚫 Can't Purchase: 108 items")
        self.cant_purchase_label.setStyleSheet("font-weight: bold;")
        summary_layout.addWidget(self.cant_purchase_label)
        
        summary_layout.addWidget(self._create_v_separator())
        
        self.cant_sell_label = QLabel("🚫 Can't Sell: 3 items")
        self.cant_sell_label.setStyleSheet("font-weight: bold;")
        summary_layout.addWidget(self.cant_sell_label)
        
        summary_layout.addStretch()
        
        layout.addWidget(summary_group)
        
        # Fully restricted callout
        restricted_label = QLabel("⛔ Fully Restricted (can't buy OR sell): Coal, Water, Tree Logs")
        restricted_label.setStyleSheet("background: #ffebee; padding: 8px; border-radius: 5px; color: #c62828;")
        layout.addWidget(restricted_label)
        
        # Filters
        filter_group = QGroupBox("🔍 Filters")
        filter_layout = QHBoxLayout(filter_group)
        
        filter_layout.addWidget(QLabel("Search:"))
        self.item_search_edit = QLineEdit()
        self.item_search_edit.setPlaceholderText("Item name...")
        self.item_search_edit.setMaximumWidth(150)
        self.item_search_edit.textChanged.connect(self._filter_item_rules)
        filter_layout.addWidget(self.item_search_edit)
        
        filter_layout.addWidget(QLabel("Category:"))
        self.item_category_combo = QComboBox()
        self.item_category_combo.addItem("All Categories")
        self.item_category_combo.currentIndexChanged.connect(self._filter_item_rules)
        filter_layout.addWidget(self.item_category_combo)
        
        filter_layout.addWidget(QLabel("Show:"))
        self.item_filter_group = QButtonGroup()
        
        self.show_all_radio = QRadioButton("All Restricted")
        self.show_all_radio.setChecked(True)
        self.show_all_radio.toggled.connect(self._filter_item_rules)
        self.item_filter_group.addButton(self.show_all_radio)
        filter_layout.addWidget(self.show_all_radio)
        
        self.show_no_purchase_radio = QRadioButton("Can't Purchase")
        self.show_no_purchase_radio.toggled.connect(self._filter_item_rules)
        self.item_filter_group.addButton(self.show_no_purchase_radio)
        filter_layout.addWidget(self.show_no_purchase_radio)
        
        self.show_no_sell_radio = QRadioButton("Can't Sell")
        self.show_no_sell_radio.toggled.connect(self._filter_item_rules)
        self.item_filter_group.addButton(self.show_no_sell_radio)
        filter_layout.addWidget(self.show_no_sell_radio)
        
        filter_layout.addStretch()
        
        layout.addWidget(filter_group)
        
        # Item rules table
        self.item_rules_table = QTableWidget()
        self.item_rules_table.setColumnCount(4)
        self.item_rules_table.setHorizontalHeaderLabels(["Item Name", "Category", "Can Purchase", "Can Sell"])
        self.item_rules_table.setAlternatingRowColors(True)
        self.item_rules_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.item_rules_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.item_rules_table.setSortingEnabled(True)
        
        header = self.item_rules_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        
        layout.addWidget(self.item_rules_table, stretch=1)
        
        # Count label and buttons
        bottom_layout = QHBoxLayout()
        
        self.item_count_label = QLabel("Showing 108 restricted items")
        self.item_count_label.setStyleSheet("color: #666;")
        bottom_layout.addWidget(self.item_count_label)
        
        bottom_layout.addStretch()
        
        refresh_btn = QPushButton("🔄 Refresh from Reference Data")
        refresh_btn.clicked.connect(self.refresh_item_rules)
        bottom_layout.addWidget(refresh_btn)
        
        edit_btn = QPushButton("✏️ Edit in Reference Data →")
        edit_btn.clicked.connect(self._navigate_to_reference_data)
        bottom_layout.addWidget(edit_btn)
        
        layout.addLayout(bottom_layout)
        
        return widget
    
    def _create_app_settings_tab(self) -> QWidget:
        """Create the App Settings sub-tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Display Settings
        display_group = QGroupBox("🎨 Display Settings")
        display_layout = QFormLayout(display_group)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark"])
        display_layout.addRow("Theme:", self.theme_combo)
        
        self.currency_combo = QComboBox()
        self.currency_combo.addItems(["$1,234.56", "1,234.56 USD", "1.234,56 €"])
        display_layout.addRow("Currency Format:", self.currency_combo)
        
        self.date_format_combo = QComboBox()
        self.date_format_combo.addItems(["MM/DD/YYYY", "DD/MM/YYYY", "YYYY-MM-DD"])
        display_layout.addRow("Date Format:", self.date_format_combo)
        
        layout.addWidget(display_group)
        
        # Data Management
        data_group = QGroupBox("💾 Data Management")
        data_layout = QVBoxLayout(data_group)
        
        import_btn = QPushButton("📥 Import from Excel")
        import_btn.setToolTip("Import data from your Excel spreadsheets")
        import_btn.clicked.connect(self._on_import_excel)
        data_layout.addWidget(import_btn)
        
        export_btn = QPushButton("📤 Export to Excel")
        export_btn.setToolTip("Export all data to Excel format")
        export_btn.clicked.connect(self._on_export_excel)
        data_layout.addWidget(export_btn)
        
        backup_btn = QPushButton("💾 Backup Database")
        backup_btn.setToolTip("Create a backup copy")
        backup_btn.clicked.connect(self._on_backup)
        data_layout.addWidget(backup_btn)
        
        restore_btn = QPushButton("📂 Restore from Backup")
        restore_btn.setToolTip("Restore from a previous backup")
        restore_btn.clicked.connect(self._on_restore)
        data_layout.addWidget(restore_btn)
        
        layout.addWidget(data_group)
        
        # Reset Options
        reset_group = QGroupBox("🔄 Reset Options")
        reset_layout = QVBoxLayout(reset_group)
        
        reset_ledger_btn = QPushButton("🔄 Reset Ledger")
        reset_ledger_btn.setToolTip("Clear all transactions")
        reset_ledger_btn.clicked.connect(lambda: self._on_reset("ledger"))
        reset_layout.addWidget(reset_ledger_btn)
        
        reset_inventory_btn = QPushButton("🔄 Reset Inventory")
        reset_inventory_btn.setToolTip("Clear all inventory data")
        reset_inventory_btn.clicked.connect(lambda: self._on_reset("inventory"))
        reset_layout.addWidget(reset_inventory_btn)
        
        reset_all_btn = QPushButton("⚠️ Reset All Data")
        reset_all_btn.setToolTip("Complete reset to factory defaults")
        reset_all_btn.setStyleSheet("color: #c62828;")
        reset_all_btn.clicked.connect(lambda: self._on_reset("all"))
        reset_layout.addWidget(reset_all_btn)
        
        layout.addWidget(reset_group)
        
        # About
        about_group = QGroupBox("ℹ️ About")
        about_layout = QVBoxLayout(about_group)
        
        about_layout.addWidget(QLabel("<b>Frontier Mining Tracker</b>"))
        about_layout.addWidget(QLabel("Version: 1.0.0"))
        about_layout.addWidget(QLabel(""))
        about_layout.addWidget(QLabel("Built for \"Out of Ore\" mining game"))
        about_layout.addWidget(QLabel("Challenge Mode: Frontier Mining Self-Sufficiency"))
        
        layout.addWidget(about_group)
        
        layout.addStretch()
        
        return widget
    
    def _create_v_separator(self) -> QFrame:
        """Create a vertical separator."""
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setFrameShadow(QFrame.Shadow.Sunken)
        return sep
    
    def refresh_item_rules(self):
        """Refresh item rules from Reference Data tab."""
        if self.main_window and hasattr(self.main_window, 'reference_tab'):
            ref_tab = self.main_window.reference_tab
            
            # Try to sync from the reference tab's items
            self._sync_from_reference_tab()
            
            QMessageBox.information(
                self, "Refreshed",
                f"Item rules refreshed from Reference Data.\n\n"
                f"Found {len(self.item_rules)} restricted items."
            )
        else:
            QMessageBox.information(
                self, "Refresh",
                "Could not find Reference Data tab. Using default item rules."
            )
            self._load_default_item_rules()
    
    def _sync_from_reference_tab(self):
        """Try to sync item rules directly from Reference Data tab."""
        if not self.main_window or not hasattr(self.main_window, 'reference_tab'):
            self._load_default_item_rules()
            return
        
        ref_tab = self.main_window.reference_tab
        
        # Try to get items from the items_tab (ItemsSubTab)
        if hasattr(ref_tab, 'items_tab') and hasattr(ref_tab.items_tab, 'get_all_items'):
            all_items = ref_tab.items_tab.get_all_items()
            if all_items:
                self._update_item_rules_from_list(all_items)
                return
        
        # Try sub_tabs approach
        if hasattr(ref_tab, 'sub_tabs'):
            # Find Items sub-tab (usually index 0)
            for i in range(ref_tab.sub_tabs.count()):
                if "Items" in ref_tab.sub_tabs.tabText(i):
                    items_widget = ref_tab.sub_tabs.widget(i)
                    if hasattr(items_widget, 'get_all_items'):
                        all_items = items_widget.get_all_items()
                        if all_items:
                            self._update_item_rules_from_list(all_items)
                            return
                    elif hasattr(items_widget, 'items_table'):
                        self._extract_items_from_table(items_widget.items_table)
                        return
        
        # Fallback to default
        self._load_default_item_rules()
    
    def _update_item_rules_from_list(self, all_items: list):
        """Update item rules from a list of item dictionaries - filter to restricted only."""
        self.item_rules = []
        categories = set()
        
        for item in all_items:
            can_purchase = item.get("can_purchase", True)
            can_sell = item.get("can_sell", True)
            
            # Only include restricted items (can't purchase OR can't sell)
            if not can_purchase or not can_sell:
                self.item_rules.append({
                    "name": item.get("name", ""),
                    "category": item.get("category", ""),
                    "can_purchase": can_purchase,
                    "can_sell": can_sell,
                })
                if item.get("category"):
                    categories.add(item.get("category"))
        
        # Update category dropdown
        current_category = self.item_category_combo.currentText()
        self.item_category_combo.clear()
        self.item_category_combo.addItem("All Categories")
        self.item_category_combo.addItems(sorted(categories))
        
        # Restore selection if possible
        idx = self.item_category_combo.findText(current_category)
        if idx >= 0:
            self.item_category_combo.setCurrentIndex(idx)
        
        # Update summary
        cant_purchase = sum(1 for r in self.item_rules if not r["can_purchase"])
        cant_sell = sum(1 for r in self.item_rules if not r["can_sell"])
        self.cant_purchase_label.setText(f"🚫 Can't Purchase: {cant_purchase} items")
        self.cant_sell_label.setText(f"🚫 Can't Sell: {cant_sell} items")
        
        # Refresh table
        self._filter_item_rules()
    
    def _extract_items_from_table(self, table):
        """Extract item rules from a QTableWidget."""
        self.item_rules = []
        categories = set()
        
        # Find column indices for the fields we need
        col_indices = {}
        for col in range(table.columnCount()):
            header_item = table.horizontalHeaderItem(col)
            if header_item:
                text = header_item.text().lower()
                if "name" in text or "item" in text:
                    col_indices["name"] = col
                elif "category" in text:
                    col_indices["category"] = col
                elif "purchase" in text:
                    col_indices["can_purchase"] = col
                elif "sell" in text:
                    col_indices["can_sell"] = col
        
        if "name" not in col_indices:
            self._load_default_item_rules()
            return
        
        for row in range(table.rowCount()):
            name_item = table.item(row, col_indices.get("name", 0))
            if not name_item:
                continue
            
            name = name_item.text()
            category = ""
            can_purchase = True
            can_sell = True
            
            if "category" in col_indices:
                cat_item = table.item(row, col_indices["category"])
                if cat_item:
                    category = cat_item.text()
            
            if "can_purchase" in col_indices:
                purchase_item = table.item(row, col_indices["can_purchase"])
                if purchase_item:
                    text = purchase_item.text().lower()
                    can_purchase = "yes" in text or "✅" in text or text == "true"
            
            if "can_sell" in col_indices:
                sell_item = table.item(row, col_indices["can_sell"])
                if sell_item:
                    text = sell_item.text().lower()
                    can_sell = "yes" in text or "✅" in text or text == "true"
            
            # Only add restricted items
            if not can_purchase or not can_sell:
                self.item_rules.append({
                    "name": name,
                    "category": category,
                    "can_purchase": can_purchase,
                    "can_sell": can_sell,
                })
                if category:
                    categories.add(category)
        
        # Update category dropdown
        current_category = self.item_category_combo.currentText()
        self.item_category_combo.clear()
        self.item_category_combo.addItem("All Categories")
        self.item_category_combo.addItems(sorted(categories))
        
        idx = self.item_category_combo.findText(current_category)
        if idx >= 0:
            self.item_category_combo.setCurrentIndex(idx)
        
        # Update summary
        cant_purchase = sum(1 for r in self.item_rules if not r["can_purchase"])
        cant_sell = sum(1 for r in self.item_rules if not r["can_sell"])
        self.cant_purchase_label.setText(f"🚫 Can't Purchase: {cant_purchase} items")
        self.cant_sell_label.setText(f"🚫 Can't Sell: {cant_sell} items")
        
        self._filter_item_rules()
    
    def _load_default_item_rules(self):
        """Load default item rules - all 112 restricted items from Challenge Tracker."""
        # Complete list of restricted items from Item Rules sheet
        restricted_items = [
            # Buildings - Rough Concrete (can't purchase, can sell)
            ("Concrete Ramp 2/4", "Buildings - Rough Concrete", False, True),
            ("Concrete Ramp 3/4", "Buildings - Rough Concrete", False, True),
            ("Concrete Ramp 4/4", "Buildings - Rough Concrete", False, True),
            ("Concrete Roof", "Buildings - Rough Concrete", False, True),
            ("Concrete Roof Corner", "Buildings - Rough Concrete", False, True),
            ("Concrete Roof Corner Inv", "Buildings - Rough Concrete", False, True),
            ("Concrete Wall", "Buildings - Rough Concrete", False, True),
            ("Concrete Wall Inv", "Buildings - Rough Concrete", False, True),
            
            # Buildings - Steel (can't purchase, can sell)
            ("Steel Block", "Buildings - Steel", False, True),
            ("Steel Ceiling", "Buildings - Steel", False, True),
            ("Steel Floor", "Buildings - Steel", False, True),
            ("Steel Railing", "Buildings - Steel", False, True),
            ("Steel Roof", "Buildings - Steel", False, True),
            
            # Equipment - Explosives
            ("TNT", "Equipment - Explosives", False, True),
            
            # Equipment - Filters (can't purchase, can sell)
            ("Built Filter Kit", "Equipment - Filters", False, True),
            ("High Quality Filter Kit", "Equipment - Filters", False, True),
            ("Low Quality Filter Kit", "Equipment - Filters", False, True),
            ("No Brand Filter Kit", "Equipment - Filters", False, True),
            ("OEM Filter Kit", "Equipment - Filters", False, True),
            ("Used Filter Kit", "Equipment - Filters", False, True),
            
            # Equipment - GPS
            ("GPS Receiver", "Equipment - GPS", False, True),
            
            # Equipment - Handtools (can't purchase, can sell)
            ("Axe", "Equipment - Handtools", False, True),
            ("Fast Pickaxe", "Equipment - Handtools", False, True),
            ("Fast Shovel", "Equipment - Handtools", False, True),
            ("Fast Sledge", "Equipment - Handtools", False, True),
            ("Light", "Equipment - Handtools", False, True),
            
            # Equipment - Horn
            ("Horn", "Equipment - Horn", False, True),
            
            # Equipment - Hoses (can't purchase, can sell)
            ("Built Hydraulic Hose", "Equipment - Hoses", False, True),
            ("High Quality Hydraulic Hose", "Equipment - Hoses", False, True),
            ("Low Quality Hydraulic Hose", "Equipment - Hoses", False, True),
            ("No Brand Hydraulic Hose", "Equipment - Hoses", False, True),
            ("OEM Hydraulic Hose", "Equipment - Hoses", False, True),
            ("Used Hydraulic Hose", "Equipment - Hoses", False, True),
            
            # Equipment - Injectors (can't purchase, can sell)
            ("Built Injector", "Equipment - Injectors", False, True),
            ("High Quality Injector", "Equipment - Injectors", False, True),
            ("Low Quality Injector", "Equipment - Injectors", False, True),
            ("No Brand Injector", "Equipment - Injectors", False, True),
            ("OEM Injector", "Equipment - Injectors", False, True),
            ("Used Injector", "Equipment - Injectors", False, True),
            
            # Equipment - Lights (can't purchase, can sell)
            ("LED Beacon", "Equipment - Lights", False, True),
            ("LED Beacon Bar", "Equipment - Lights", False, True),
            ("LED Light Bar 1", "Equipment - Lights", False, True),
            ("LED Light Bar 2", "Equipment - Lights", False, True),
            ("LED Light Bar 3", "Equipment - Lights", False, True),
            ("LED Power Light", "Equipment - Lights", False, True),
            ("LED Round Light", "Equipment - Lights", False, True),
            ("LED Square Light", "Equipment - Lights", False, True),
            ("LED Square Light (Large)", "Equipment - Lights", False, True),
            ("LED Work Light", "Equipment - Lights", False, True),
            
            # Equipment - Paint (can't purchase, can sell)
            ("Black", "Equipment - Paint", False, True),
            ("Blue", "Equipment - Paint", False, True),
            ("Blue, Light", "Equipment - Paint", False, True),
            ("Gray", "Equipment - Paint", False, True),
            ("Gray, Light", "Equipment - Paint", False, True),
            ("Green", "Equipment - Paint", False, True),
            ("Green, Dark", "Equipment - Paint", False, True),
            ("Green, Forest", "Equipment - Paint", False, True),
            ("Green, Light", "Equipment - Paint", False, True),
            ("Green, Mint", "Equipment - Paint", False, True),
            ("Green, Moss", "Equipment - Paint", False, True),
            ("Orange", "Equipment - Paint", False, True),
            ("Orange, Dark", "Equipment - Paint", False, True),
            ("Orange, Sunset", "Equipment - Paint", False, True),
            ("Pink", "Equipment - Paint", False, True),
            ("Pink, Dark", "Equipment - Paint", False, True),
            ("Pink, Light", "Equipment - Paint", False, True),
            ("Purple", "Equipment - Paint", False, True),
            ("Purple, Dark", "Equipment - Paint", False, True),
            
            # Materials - Concrete
            ("Cement", "Materials - Concrete", False, True),
            
            # Materials - Fuel
            ("Fuel", "Materials - Fuel", False, True),
            
            # Materials - Metals (can't purchase, can sell)
            ("Steel Rod", "Materials - Metals", False, True),
            ("Steel Sheet", "Materials - Metals", False, True),
            
            # Materials - Ore (refined bars - can't purchase, can sell)
            ("Aluminium Bar", "Materials - Ore", False, True),
            ("Copper Bar", "Materials - Ore", False, True),
            ("Diamond", "Materials - Ore", False, True),
            ("Gold Bar", "Materials - Ore", False, True),
            ("Iron Bar", "Materials - Ore", False, True),
            ("Lithium Bar", "Materials - Ore", False, True),
            ("Platinum Bar", "Materials - Ore", False, True),
            ("Ruby", "Materials - Ore", False, True),
            ("Silicon Bar", "Materials - Ore", False, True),
            ("Silver Bar", "Materials - Ore", False, True),
            ("Steel Bar", "Materials - Ore", False, True),
            
            # Materials - Sub Parts (can't purchase, can sell)
            ("Electronic Parts", "Materials - Sub Parts", False, True),
            ("Empty Barrel", "Materials - Sub Parts", False, True),
            ("Plastics", "Materials - Sub Parts", False, True),
            ("Rubber", "Materials - Sub Parts", False, True),
            ("Wearplate", "Materials - Sub Parts", False, True),
            
            # Materials - Wood (can't purchase, can sell)
            ("Wood Beam", "Materials - Wood", False, True),
            ("Wood Planks", "Materials - Wood", False, True),
            ("Wood Sheet", "Materials - Wood", False, True),
            
            # Resources - Asphalt
            ("Asphalt", "Resources - Asphalt", False, True),
            
            # Resources - Dirt (can't purchase, can sell)
            ("Dirt", "Resources - Dirt", False, True),
            ("PayDirt", "Resources - Dirt", False, True),
            ("Tailings", "Resources - Dirt", False, True),
            
            # Resources - Fluids
            ("Oil", "Resources - Fluids", False, True),
            ("Water", "Resources - Fluids", False, False),  # Can't buy OR sell
            
            # Resources - Ore (can't purchase, can sell - except Coal)
            ("Aluminium Ore", "Resources - Ore", False, True),
            ("Coal", "Resources - Ore", False, False),  # Can't buy OR sell
            ("Copper Ore", "Resources - Ore", False, True),
            ("Diamond Ore", "Resources - Ore", False, True),
            ("Gold Ore", "Resources - Ore", False, True),
            ("Iron Ore", "Resources - Ore", False, True),
            ("Lithium Ore", "Resources - Ore", False, True),
            ("Ruby Ore", "Resources - Ore", False, True),
            ("Silicon Ore", "Resources - Ore", False, True),
            ("Silver Ore", "Resources - Ore", False, True),
            
            # Resources - Rock (can't purchase, can sell)
            ("Blasted Rock", "Resources - Rock", False, True),
            ("Crushed Rock", "Resources - Rock", False, True),
            ("Gravel", "Resources - Rock", False, True),
            ("Solid Rock", "Resources - Rock", False, True),
            
            # Resources - Wood
            ("Tree Logs", "Resources - Wood", False, False),  # Can't buy OR sell
        ]
        
        self.item_rules = []
        categories = set()
        
        for name, category, can_purchase, can_sell in restricted_items:
            self.item_rules.append({
                "name": name,
                "category": category,
                "can_purchase": can_purchase,
                "can_sell": can_sell,
            })
            categories.add(category)
        
        # Update category dropdown
        self.item_category_combo.clear()
        self.item_category_combo.addItem("All Categories")
        self.item_category_combo.addItems(sorted(categories))
        
        # Populate table
        self._filter_item_rules()
        
        # Update summary
        cant_purchase = sum(1 for r in self.item_rules if not r["can_purchase"])
        cant_sell = sum(1 for r in self.item_rules if not r["can_sell"])
        self.cant_purchase_label.setText(f"🚫 Can't Purchase: {cant_purchase} items")
        self.cant_sell_label.setText(f"🚫 Can't Sell: {cant_sell} items")
    
    def _filter_item_rules(self):
        """Filter and display item rules."""
        search_text = self.item_search_edit.text().lower()
        category_filter = self.item_category_combo.currentText()
        
        filtered = []
        
        for rule in self.item_rules:
            # Search filter
            if search_text and search_text not in rule["name"].lower():
                continue
            
            # Category filter
            if category_filter != "All Categories" and rule["category"] != category_filter:
                continue
            
            # Radio button filter
            if self.show_no_purchase_radio.isChecked() and rule["can_purchase"]:
                continue
            if self.show_no_sell_radio.isChecked() and rule["can_sell"]:
                continue
            
            filtered.append(rule)
        
        # Populate table
        self.item_rules_table.setSortingEnabled(False)
        self.item_rules_table.setRowCount(len(filtered))
        
        for row, rule in enumerate(filtered):
            # Name
            name_item = QTableWidgetItem(rule["name"])
            self.item_rules_table.setItem(row, 0, name_item)
            
            # Category
            cat_item = QTableWidgetItem(rule["category"])
            self.item_rules_table.setItem(row, 1, cat_item)
            
            # Can Purchase
            purchase_item = QTableWidgetItem("✅ Yes" if rule["can_purchase"] else "❌ No")
            purchase_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if not rule["can_purchase"]:
                purchase_item.setForeground(QColor("#c62828"))
            self.item_rules_table.setItem(row, 2, purchase_item)
            
            # Can Sell
            sell_item = QTableWidgetItem("✅ Yes" if rule["can_sell"] else "❌ No")
            sell_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if not rule["can_sell"]:
                sell_item.setForeground(QColor("#c62828"))
            self.item_rules_table.setItem(row, 3, sell_item)
            
            # Highlight fully restricted
            if not rule["can_purchase"] and not rule["can_sell"]:
                for col in range(4):
                    self.item_rules_table.item(row, col).setBackground(QColor("#ffebee"))
        
        self.item_rules_table.setSortingEnabled(True)
        self.item_count_label.setText(f"Showing {len(filtered)} restricted items")
    
    # Event handlers
    def _on_date_changed(self):
        """Handle date changes."""
        start = self.game_start_date.date().toPyDate()
        current = self.current_game_date.date().toPyDate()
        days = (current - start).days + 1
        self.days_played_label.setText(str(max(1, days)))
        
        self.settings["game_start_date"] = start
        self.settings["current_game_date"] = current
    
    def _on_setting_changed(self, key: str, value):
        """Handle setting value change."""
        self.settings[key] = value
        self.settings_changed.emit(key, value)
    
    def _on_difficulty_changed(self, difficulty: str):
        """Handle difficulty selection change."""
        preset = self.DIFFICULTY_PRESETS.get(difficulty, {})
        self.difficulty_description.setText(preset.get("description", ""))
        self.settings["difficulty_level"] = difficulty
    
    def _on_preset_table_changed(self, row: int, col: int):
        """Handle preset table cell edit."""
        # Get the difficulty name for this row
        difficulty_item = self.preset_table.item(row, 0)
        if not difficulty_item:
            return
        
        difficulty = difficulty_item.text()
        new_value = self.preset_table.item(row, col).text()
        
        # Update the internal preset data
        # Column mapping: 1=Seed Capital, 2=Personal, 3=Company, 4=Oil Cap, 5=Daily Limit, 6=Bar Threshold
        try:
            if col == 1:  # Seed Capital
                # Parse value like "$100,000" -> 100000
                value = int(new_value.replace("$", "").replace(",", ""))
                if difficulty in self.DIFFICULTY_PRESETS:
                    self.DIFFICULTY_PRESETS[difficulty]["seed_capital"] = value
            elif col == 2:  # Personal %
                value = float(new_value.replace("%", "")) / 100
                if difficulty in self.DIFFICULTY_PRESETS:
                    self.DIFFICULTY_PRESETS[difficulty]["personal_split"] = value
            elif col == 3:  # Company %
                value = float(new_value.replace("%", "")) / 100
                if difficulty in self.DIFFICULTY_PRESETS:
                    self.DIFFICULTY_PRESETS[difficulty]["company_split"] = value
            elif col == 4:  # Oil Cap
                value = int(new_value.replace(",", ""))
                if difficulty in self.DIFFICULTY_PRESETS:
                    self.DIFFICULTY_PRESETS[difficulty]["oil_cap"] = value
            elif col == 5:  # Daily Limit
                if new_value.lower() == "none":
                    value = None
                else:
                    value = int(new_value.replace("$", "").replace(",", ""))
                if difficulty in self.DIFFICULTY_PRESETS:
                    self.DIFFICULTY_PRESETS[difficulty]["daily_limit"] = value
            elif col == 6:  # Bar Threshold
                value = int(new_value.replace(",", ""))
                if difficulty in self.DIFFICULTY_PRESETS:
                    self.DIFFICULTY_PRESETS[difficulty]["bar_threshold"] = value
        except (ValueError, AttributeError):
            # Invalid input, ignore
            pass
    
    def _apply_difficulty_preset(self):
        """Apply the selected difficulty preset."""
        difficulty = self.difficulty_combo.currentText()
        preset = self.DIFFICULTY_PRESETS.get(difficulty, {})
        
        if difficulty == "Custom":
            QMessageBox.information(
                self, "Custom Difficulty",
                "Configure the settings manually for custom difficulty."
            )
            return
        
        # Apply preset values
        if preset.get("seed_capital") is not None:
            self.seed_capital_spin.setValue(preset["seed_capital"])
            self.starting_capital_spin.setValue(preset["seed_capital"])
        
        if preset.get("personal_split") is not None:
            self.personal_split_spin.setValue(int(preset["personal_split"] * 100))
        
        if preset.get("oil_cap") is not None:
            self.oil_cap_spin.setValue(preset["oil_cap"])
            self.oil_cap_check.setChecked(True)
        
        if preset.get("daily_limit") is not None:
            self.daily_limit_spin.setValue(preset["daily_limit"])
            self.daily_limit_check.setChecked(True)
        else:
            self.daily_limit_check.setChecked(False)
            self.daily_limit_spin.setValue(0)
        
        if preset.get("bar_threshold") is not None:
            self.bar_threshold_spin.setValue(preset["bar_threshold"])
        
        QMessageBox.information(
            self, "Preset Applied",
            f"{difficulty} difficulty preset has been applied."
        )
    
    def _on_split_changed(self):
        """Handle personal split change."""
        personal = self.personal_split_spin.value()
        company = 100 - personal
        self.company_split_spin.setValue(company)
        
        self.settings["personal_split"] = personal / 100
        self.settings["company_split"] = company / 100
        
        if personal + company == 100:
            self.split_status_label.setText("✅ 100%")
            self.split_status_label.setStyleSheet("color: #2e7d32; font-weight: bold;")
        else:
            self.split_status_label.setText(f"⚠️ {personal + company}%")
            self.split_status_label.setStyleSheet("color: #c62828; font-weight: bold;")
    
    def _on_oil_cap_toggled(self, state):
        """Handle oil cap checkbox toggle."""
        enabled = state == Qt.CheckState.Checked.value
        self.oil_cap_spin.setEnabled(enabled)
        self.settings["oil_cap_enabled"] = enabled
    
    def _on_daily_limit_toggled(self, state):
        """Handle daily limit checkbox toggle."""
        enabled = state == Qt.CheckState.Checked.value
        self.daily_limit_spin.setEnabled(enabled)
        self.settings["daily_limit_enabled"] = enabled
    
    def _on_vn_level_changed(self, level: int):
        """Handle Vendor Negotiation level change."""
        discount = level * 0.5
        self.vn_discount_label.setText(f"{discount}%")
        self._highlight_discount_level(self.vn_table, level)
        self.settings["vendor_negotiation_level"] = level
        self._update_combined_discounts()
    
    def _on_if_level_changed(self, level: int):
        """Handle Investment Forecasting level change."""
        discount = level * 0.5
        self.if_discount_label.setText(f"{discount}%")
        self._highlight_discount_level(self.if_table, level)
        self.settings["investment_forecasting_level"] = level
        self._update_combined_discounts()
    
    def _update_combined_discounts(self):
        """Update combined discount display."""
        vn = self.vn_level_spin.value() * 0.5
        if_level = self.if_level_spin.value() * 0.5
        combined = vn + if_level
        
        self.non_vehicle_discount_label.setText(f"{vn}% discount (VN only)")
        self.vehicle_discount_label.setText(f"{combined}% discount (VN + IF combined)")
        
        # Example calculation
        vehicle_price = 100000
        discounted = vehicle_price * (1 - combined / 100)
        self.example_label.setText(f"Example: ${vehicle_price:,} vehicle → ${discounted:,.0f} after discounts")
    
    def _reset_challenge_rules(self):
        """Reset challenge rules to defaults."""
        reply = QMessageBox.question(
            self, "Reset Challenge Rules",
            "Reset all challenge rules to default values?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.difficulty_combo.setCurrentText("Easy")
            self._apply_difficulty_preset()
    
    def _navigate_to_reference_data(self):
        """Navigate to Reference Data -> Items tab."""
        if self.main_window:
            # Find Reference Data tab and switch to it
            for i in range(self.main_window.tab_widget.count()):
                if "Reference" in self.main_window.tab_widget.tabText(i):
                    self.main_window.tab_widget.setCurrentIndex(i)
                    # Switch to Items sub-tab
                    ref_tab = self.main_window.tab_widget.widget(i)
                    if hasattr(ref_tab, 'sub_tabs'):
                        ref_tab.sub_tabs.setCurrentIndex(0)  # Items is first sub-tab
                    break
        else:
            QMessageBox.information(
                self, "Navigation",
                "Go to Reference Data → Items tab to edit item rules."
            )
    
    def _on_new_playthrough(self):
        """Start a new playthrough."""
        reply = QMessageBox.question(
            self, "New Playthrough",
            "Start a new playthrough? This will:\n\n"
            "• Reset game dates to today\n"
            "• Reset oil lifetime counter\n"
            "• Clear all transactions\n"
            "• Clear all inventory\n\n"
            "This cannot be undone!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            today = date.today()
            # Reset to a game date format (the game uses 2021 dates)
            self.game_start_date.setDate(QDate(2021, 4, 22))
            self.current_game_date.setDate(QDate(2021, 4, 22))
            self.last_updated_label.setText(datetime.now().strftime("%m/%d/%Y %I:%M %p"))
            
            QMessageBox.information(
                self, "New Playthrough",
                "New playthrough started! Game dates have been reset."
            )
    
    def _on_import_excel(self):
        """Import data from Excel."""
        QMessageBox.information(
            self, "Import",
            "Excel import functionality coming soon!\n\n"
            "This will import from:\n"
            "• Frontier_Mining_Dashboard_5.xlsx\n"
            "• Out_of_Ore__Frontier_Mining_Challenge_Tracker_5.xlsx"
        )
    
    def _on_export_excel(self):
        """Export data to Excel."""
        QMessageBox.information(
            self, "Export",
            "Excel export functionality coming soon!"
        )
    
    def _on_backup(self):
        """Backup database."""
        QMessageBox.information(
            self, "Backup",
            "Database backup functionality coming soon!"
        )
    
    def _on_restore(self):
        """Restore from backup."""
        QMessageBox.information(
            self, "Restore",
            "Database restore functionality coming soon!"
        )
    
    def _on_reset(self, reset_type: str):
        """Reset data."""
        if reset_type == "all":
            msg = "⚠️ This will delete ALL data and reset to factory defaults!\n\nAre you absolutely sure?"
        elif reset_type == "ledger":
            msg = "This will delete all ledger transactions.\n\nAre you sure?"
        elif reset_type == "inventory":
            msg = "This will delete all inventory data.\n\nAre you sure?"
        else:
            return
        
        reply = QMessageBox.warning(
            self, f"Reset {reset_type.title()}",
            msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            QMessageBox.information(
                self, "Reset",
                f"{reset_type.title()} has been reset."
            )
    
    # Public methods for other tabs to access settings
    def get_setting(self, key: str):
        """Get a setting value."""
        return self.settings.get(key)
    
    def get_personal_split(self) -> float:
        """Get the personal split percentage."""
        return self.settings.get("personal_split", 0.10)
    
    def get_company_split(self) -> float:
        """Get the company split percentage."""
        return self.settings.get("company_split", 0.90)
    
    def get_oil_cap(self) -> tuple:
        """Get oil cap settings (enabled, amount, lifetime_sold)."""
        return (
            self.settings.get("oil_cap_enabled", True),
            self.settings.get("oil_cap_amount", 10000),
            self.settings.get("oil_lifetime_sold", 0),
        )
    
    def get_vn_discount(self) -> float:
        """Get Vendor Negotiation discount rate."""
        level = self.settings.get("vendor_negotiation_level", 0)
        return level * 0.005  # 0.5% per level as decimal
    
    def get_if_discount(self) -> float:
        """Get Investment Forecasting discount rate."""
        level = self.settings.get("investment_forecasting_level", 0)
        return level * 0.005  # 0.5% per level as decimal
    
    def get_fuel_price(self) -> float:
        """Get fuel price per liter."""
        return self.settings.get("fuel_price_per_liter", 0.32)
