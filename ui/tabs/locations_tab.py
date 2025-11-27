"""
Locations Tab - Manage maps, location types, and locations

Features:
- Maps table with abbreviations
- Location types table
- Full locations list with map and type
- All tables are editable (add/edit/delete)
- Import from Excel/CSV
"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
    QInputDialog,
    QComboBox,
    QSplitter,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QAbstractItemView,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor

from core.database import Database, get_database


class AddLocationDialog(QDialog):
    """Dialog for adding a new location."""
    
    def __init__(self, maps: list, location_types: list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Location")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # Form
        form = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("e.g., FQR - Main Base")
        form.addRow("Location Name:", self.name_edit)
        
        self.map_combo = QComboBox()
        self.map_combo.addItems(maps)
        form.addRow("Map:", self.map_combo)
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(location_types)
        form.addRow("Type:", self.type_combo)
        
        layout.addLayout(form)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def get_data(self) -> dict:
        """Get the entered data."""
        return {
            'name': self.name_edit.text().strip(),
            'map': self.map_combo.currentText(),
            'type': self.type_combo.currentText(),
        }


class EditLocationDialog(QDialog):
    """Dialog for editing a location."""
    
    def __init__(self, location: dict, maps: list, location_types: list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Location")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # Form
        form = QFormLayout()
        
        self.name_edit = QLineEdit(location.get('name', ''))
        form.addRow("Location Name:", self.name_edit)
        
        self.map_combo = QComboBox()
        self.map_combo.addItems(maps)
        if location.get('map') in maps:
            self.map_combo.setCurrentText(location['map'])
        form.addRow("Map:", self.map_combo)
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(location_types)
        if location.get('type') in location_types:
            self.type_combo.setCurrentText(location['type'])
        form.addRow("Type:", self.type_combo)
        
        layout.addLayout(form)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def get_data(self) -> dict:
        """Get the entered data."""
        return {
            'name': self.name_edit.text().strip(),
            'map': self.map_combo.currentText(),
            'type': self.type_combo.currentText(),
        }


class LocationsTab(QWidget):
    """Locations tab for managing maps and locations."""
    
    # Signals
    locations_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = get_database()
        
        self._setup_ui()
        self._load_data()
    
    def _setup_ui(self):
        """Setup the UI components."""
        layout = QVBoxLayout(self)
        
        # Main splitter - horizontal
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side: Maps and Types (stacked vertically)
        left_splitter = QSplitter(Qt.Orientation.Vertical)
        left_splitter.addWidget(self._create_maps_panel())
        left_splitter.addWidget(self._create_types_panel())
        left_splitter.setSizes([200, 200])
        
        main_splitter.addWidget(left_splitter)
        
        # Right side: Locations list
        main_splitter.addWidget(self._create_locations_panel())
        
        main_splitter.setSizes([300, 700])
        layout.addWidget(main_splitter)
    
    def _create_maps_panel(self) -> QGroupBox:
        """Create the maps management panel."""
        group = QGroupBox("🗺️ Maps")
        layout = QVBoxLayout(group)
        
        # Table
        self.maps_table = QTableWidget()
        self.maps_table.setColumnCount(2)
        self.maps_table.setHorizontalHeaderLabels(["Abbreviation", "Map Name"])
        self.maps_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.maps_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.maps_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.maps_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.maps_table.cellChanged.connect(self._on_map_cell_changed)
        layout.addWidget(self.maps_table)
        
        # Buttons
        btn_row = QHBoxLayout()
        
        self.add_map_btn = QPushButton("➕ Add")
        self.add_map_btn.clicked.connect(self._on_add_map)
        btn_row.addWidget(self.add_map_btn)
        
        self.delete_map_btn = QPushButton("🗑️ Delete")
        self.delete_map_btn.clicked.connect(self._on_delete_map)
        btn_row.addWidget(self.delete_map_btn)
        
        btn_row.addStretch()
        layout.addLayout(btn_row)
        
        return group
    
    def _create_types_panel(self) -> QGroupBox:
        """Create the location types management panel."""
        group = QGroupBox("📍 Location Types")
        layout = QVBoxLayout(group)
        
        # Table
        self.types_table = QTableWidget()
        self.types_table.setColumnCount(1)
        self.types_table.setHorizontalHeaderLabels(["Type Name"])
        self.types_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.types_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.types_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.types_table.cellChanged.connect(self._on_type_cell_changed)
        layout.addWidget(self.types_table)
        
        # Buttons
        btn_row = QHBoxLayout()
        
        self.add_type_btn = QPushButton("➕ Add")
        self.add_type_btn.clicked.connect(self._on_add_type)
        btn_row.addWidget(self.add_type_btn)
        
        self.delete_type_btn = QPushButton("🗑️ Delete")
        self.delete_type_btn.clicked.connect(self._on_delete_type)
        btn_row.addWidget(self.delete_type_btn)
        
        btn_row.addStretch()
        layout.addLayout(btn_row)
        
        return group
    
    def _create_locations_panel(self) -> QGroupBox:
        """Create the locations management panel."""
        group = QGroupBox("📋 Locations")
        layout = QVBoxLayout(group)
        
        # Filter row
        filter_row = QHBoxLayout()
        
        filter_row.addWidget(QLabel("Filter by Map:"))
        self.map_filter_combo = QComboBox()
        self.map_filter_combo.addItem("All Maps")
        self.map_filter_combo.currentTextChanged.connect(self._on_filter_changed)
        filter_row.addWidget(self.map_filter_combo)
        
        filter_row.addWidget(QLabel("Type:"))
        self.type_filter_combo = QComboBox()
        self.type_filter_combo.addItem("All Types")
        self.type_filter_combo.currentTextChanged.connect(self._on_filter_changed)
        filter_row.addWidget(self.type_filter_combo)
        
        filter_row.addStretch()
        
        self.location_count_label = QLabel("0 locations")
        filter_row.addWidget(self.location_count_label)
        
        layout.addLayout(filter_row)
        
        # Table
        self.locations_table = QTableWidget()
        self.locations_table.setColumnCount(3)
        self.locations_table.setHorizontalHeaderLabels(["Location", "Map", "Type"])
        self.locations_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.locations_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.locations_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.locations_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.locations_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.locations_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.locations_table.doubleClicked.connect(self._on_edit_location)
        layout.addWidget(self.locations_table)
        
        # Buttons
        btn_row = QHBoxLayout()
        
        self.add_location_btn = QPushButton("➕ Add Location")
        self.add_location_btn.clicked.connect(self._on_add_location)
        btn_row.addWidget(self.add_location_btn)
        
        self.edit_location_btn = QPushButton("✏️ Edit")
        self.edit_location_btn.clicked.connect(self._on_edit_location)
        btn_row.addWidget(self.edit_location_btn)
        
        self.delete_location_btn = QPushButton("🗑️ Delete")
        self.delete_location_btn.clicked.connect(self._on_delete_location)
        btn_row.addWidget(self.delete_location_btn)
        
        btn_row.addStretch()
        
        self.generate_btn = QPushButton("🔧 Generate Default Locations")
        self.generate_btn.clicked.connect(self._on_generate_defaults)
        btn_row.addWidget(self.generate_btn)
        
        layout.addLayout(btn_row)
        
        return group
    
    def _load_data(self):
        """Load all data from database."""
        self._load_maps()
        self._load_types()
        self._load_locations()
        self._update_filter_combos()
    
    def _load_maps(self):
        """Load maps from database."""
        self.maps_table.blockSignals(True)
        self.maps_table.setRowCount(0)
        
        maps = self.db.get_maps()
        self.maps_table.setRowCount(len(maps))
        
        for row, map_data in enumerate(maps):
            abbrev_item = QTableWidgetItem(map_data.get('abbreviation', ''))
            name_item = QTableWidgetItem(map_data.get('name', ''))
            
            # Store ID in first column
            abbrev_item.setData(Qt.ItemDataRole.UserRole, map_data.get('id'))
            
            self.maps_table.setItem(row, 0, abbrev_item)
            self.maps_table.setItem(row, 1, name_item)
        
        self.maps_table.blockSignals(False)
    
    def _load_types(self):
        """Load location types from database."""
        self.types_table.blockSignals(True)
        self.types_table.setRowCount(0)
        
        types = self.db.get_location_types()
        self.types_table.setRowCount(len(types))
        
        for row, type_data in enumerate(types):
            name_item = QTableWidgetItem(type_data.get('name', ''))
            name_item.setData(Qt.ItemDataRole.UserRole, type_data.get('id'))
            self.types_table.setItem(row, 0, name_item)
        
        self.types_table.blockSignals(False)
    
    def _load_locations(self):
        """Load locations from database with current filters."""
        map_filter = self.map_filter_combo.currentText()
        type_filter = self.type_filter_combo.currentText()
        
        if map_filter == "All Maps":
            map_filter = None
        if type_filter == "All Types":
            type_filter = None
        
        locations = self.db.get_locations(map_name=map_filter, location_type=type_filter)
        
        self.locations_table.setRowCount(len(locations))
        
        for row, loc in enumerate(locations):
            name_item = QTableWidgetItem(loc.get('name', ''))
            name_item.setData(Qt.ItemDataRole.UserRole, loc.get('id'))
            
            map_item = QTableWidgetItem(loc.get('map', ''))
            type_item = QTableWidgetItem(loc.get('type', ''))
            
            self.locations_table.setItem(row, 0, name_item)
            self.locations_table.setItem(row, 1, map_item)
            self.locations_table.setItem(row, 2, type_item)
        
        self.location_count_label.setText(f"{len(locations)} locations")
    
    def _update_filter_combos(self):
        """Update the filter combo boxes."""
        # Save current selections
        current_map = self.map_filter_combo.currentText()
        current_type = self.type_filter_combo.currentText()
        
        # Update map filter
        self.map_filter_combo.blockSignals(True)
        self.map_filter_combo.clear()
        self.map_filter_combo.addItem("All Maps")
        for map_data in self.db.get_maps():
            self.map_filter_combo.addItem(map_data.get('name', ''))
        
        # Restore selection if still valid
        idx = self.map_filter_combo.findText(current_map)
        if idx >= 0:
            self.map_filter_combo.setCurrentIndex(idx)
        self.map_filter_combo.blockSignals(False)
        
        # Update type filter
        self.type_filter_combo.blockSignals(True)
        self.type_filter_combo.clear()
        self.type_filter_combo.addItem("All Types")
        for type_data in self.db.get_location_types():
            self.type_filter_combo.addItem(type_data.get('name', ''))
        
        idx = self.type_filter_combo.findText(current_type)
        if idx >= 0:
            self.type_filter_combo.setCurrentIndex(idx)
        self.type_filter_combo.blockSignals(False)
    
    def _on_filter_changed(self):
        """Handle filter combo change."""
        self._load_locations()
    
    def _on_map_cell_changed(self, row: int, col: int):
        """Handle map table cell edit."""
        item = self.maps_table.item(row, 0)
        if not item:
            return
        
        map_id = item.data(Qt.ItemDataRole.UserRole)
        if not map_id:
            return
        
        abbrev = self.maps_table.item(row, 0).text().strip()
        name = self.maps_table.item(row, 1).text().strip()
        
        if abbrev and name:
            self.db.update_map(map_id, abbrev, name)
            self._update_filter_combos()
            self._load_locations()
    
    def _on_type_cell_changed(self, row: int, col: int):
        """Handle type table cell edit."""
        item = self.types_table.item(row, 0)
        if not item:
            return
        
        type_id = item.data(Qt.ItemDataRole.UserRole)
        if not type_id:
            return
        
        name = item.text().strip()
        if name:
            self.db.update_location_type(type_id, name)
            self._update_filter_combos()
            self._load_locations()
    
    def _on_add_map(self):
        """Add a new map."""
        abbrev, ok1 = QInputDialog.getText(self, "Add Map", "Abbreviation (e.g., FQR):")
        if not ok1 or not abbrev.strip():
            return
        
        name, ok2 = QInputDialog.getText(self, "Add Map", "Map Name (e.g., Forest Quarry):")
        if not ok2 or not name.strip():
            return
        
        self.db.add_map(abbrev.strip().upper(), name.strip())
        self._load_maps()
        self._update_filter_combos()
    
    def _on_delete_map(self):
        """Delete selected map."""
        row = self.maps_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a map to delete.")
            return
        
        item = self.maps_table.item(row, 0)
        map_id = item.data(Qt.ItemDataRole.UserRole)
        map_name = self.maps_table.item(row, 1).text()
        
        # Check for locations using this map
        locations = self.db.get_locations(map_name=map_name)
        if locations:
            reply = QMessageBox.question(
                self, "Delete Map",
                f"Map '{map_name}' has {len(locations)} locations.\n"
                "Deleting will also delete all locations on this map.\n\n"
                "Continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        
        self.db.delete_map(map_id)
        self._load_maps()
        self._load_locations()
        self._update_filter_combos()
    
    def _on_add_type(self):
        """Add a new location type."""
        name, ok = QInputDialog.getText(self, "Add Location Type", "Type Name:")
        if ok and name.strip():
            self.db.add_location_type(name.strip())
            self._load_types()
            self._update_filter_combos()
    
    def _on_delete_type(self):
        """Delete selected location type."""
        row = self.types_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a type to delete.")
            return
        
        item = self.types_table.item(row, 0)
        type_id = item.data(Qt.ItemDataRole.UserRole)
        type_name = item.text()
        
        # Check for locations using this type
        locations = self.db.get_locations(location_type=type_name)
        if locations:
            reply = QMessageBox.question(
                self, "Delete Type",
                f"Type '{type_name}' is used by {len(locations)} locations.\n"
                "These locations will have their type cleared.\n\n"
                "Continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        
        self.db.delete_location_type(type_id)
        self._load_types()
        self._load_locations()
        self._update_filter_combos()
    
    def _on_add_location(self):
        """Add a new location."""
        maps = [m['name'] for m in self.db.get_maps()]
        types = [t['name'] for t in self.db.get_location_types()]
        
        if not maps:
            QMessageBox.warning(self, "No Maps", "Please add at least one map first.")
            return
        
        if not types:
            QMessageBox.warning(self, "No Types", "Please add at least one location type first.")
            return
        
        dialog = AddLocationDialog(maps, types, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if data['name']:
                self.db.add_location(data['name'], data['map'], data['type'])
                self._load_locations()
                self.locations_changed.emit()
    
    def _on_edit_location(self):
        """Edit selected location."""
        row = self.locations_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a location to edit.")
            return
        
        item = self.locations_table.item(row, 0)
        loc_id = item.data(Qt.ItemDataRole.UserRole)
        
        current = {
            'name': self.locations_table.item(row, 0).text(),
            'map': self.locations_table.item(row, 1).text(),
            'type': self.locations_table.item(row, 2).text(),
        }
        
        maps = [m['name'] for m in self.db.get_maps()]
        types = [t['name'] for t in self.db.get_location_types()]
        
        dialog = EditLocationDialog(current, maps, types, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if data['name']:
                self.db.update_location(loc_id, data['name'], data['map'], data['type'])
                self._load_locations()
                self.locations_changed.emit()
    
    def _on_delete_location(self):
        """Delete selected location."""
        row = self.locations_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a location to delete.")
            return
        
        item = self.locations_table.item(row, 0)
        loc_id = item.data(Qt.ItemDataRole.UserRole)
        loc_name = item.text()
        
        reply = QMessageBox.question(
            self, "Delete Location",
            f"Delete location '{loc_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.db.delete_location(loc_id)
            self._load_locations()
            self.locations_changed.emit()
    
    def _on_generate_defaults(self):
        """Generate default locations for all maps."""
        reply = QMessageBox.question(
            self, "Generate Default Locations",
            "This will generate a standard set of locations for each map:\n"
            "- Main Base\n"
            "- Fuel Station\n"
            "- Mine Sites 1-2\n"
            "- Drill Site 1\n"
            "- Stockpiles (Main, Ore)\n"
            "- Pads (A, B)\n"
            "- Processing Area\n"
            "- Washplant Site\n\n"
            "Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        maps = self.db.get_maps()
        types = {t['name']: t['id'] for t in self.db.get_location_types()}
        
        # Ensure we have the required types
        required_types = ['Base', 'Infrastructure', 'Mine Site', 'Drill Site', 
                         'Stockpile', 'Pad', 'Processing']
        for t in required_types:
            if t not in types:
                self.db.add_location_type(t)
        
        # Reload types
        types = {t['name']: t['id'] for t in self.db.get_location_types()}
        
        # Generate locations for each map
        default_locations = [
            ("Main Base", "Base"),
            ("Fuel Station", "Infrastructure"),
            ("Mine Site 1", "Mine Site"),
            ("Mine Site 2", "Mine Site"),
            ("Drill Site 1", "Drill Site"),
            ("Main Stockpile", "Stockpile"),
            ("Ore Stockpile", "Stockpile"),
            ("Pad A", "Pad"),
            ("Pad B", "Pad"),
            ("Processing Area", "Processing"),
            ("Washplant Site", "Processing"),
        ]
        
        count = 0
        for map_data in maps:
            abbrev = map_data['abbreviation']
            map_name = map_data['name']
            
            for loc_suffix, loc_type in default_locations:
                loc_name = f"{abbrev} - {loc_suffix}"
                
                # Check if location already exists
                existing = self.db.get_locations(map_name=map_name)
                if not any(l['name'] == loc_name for l in existing):
                    self.db.add_location(loc_name, map_name, loc_type)
                    count += 1
        
        self._load_types()
        self._load_locations()
        self._update_filter_combos()
        
        QMessageBox.information(
            self, "Complete",
            f"Generated {count} new locations."
        )
