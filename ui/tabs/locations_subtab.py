"""
Locations Sub-Tab - Manage maps, location types, and locations

Features:
- Maps table with abbreviations  
- Location types table
- Full locations list with map and type
- All tables are editable (add/edit/delete)
- Import from Excel
- Filter by map and type
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
    QFileDialog,
    QApplication,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor

from pathlib import Path
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


class LocationsSubTab(QWidget):
    """Locations sub-tab for managing maps and locations."""
    
    # Signals
    data_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = get_database()
        
        self._setup_ui()
        self._load_data()
    
    def _setup_ui(self):
        """Setup the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Top: Import button and stats
        top_layout = QHBoxLayout()
        
        self.import_btn = QPushButton("📥 Import from Excel")
        self.import_btn.setToolTip("Import locations from Dashboard Excel file")
        self.import_btn.clicked.connect(self._on_import_excel)
        top_layout.addWidget(self.import_btn)
        
        self.generate_btn = QPushButton("🔄 Generate Defaults")
        self.generate_btn.setToolTip("Generate default locations for all maps")
        self.generate_btn.clicked.connect(self._on_generate_defaults)
        top_layout.addWidget(self.generate_btn)
        
        top_layout.addStretch()
        
        self.stats_label = QLabel("Maps: 0 | Types: 0 | Locations: 0")
        top_layout.addWidget(self.stats_label)
        
        layout.addLayout(top_layout)
        
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
        layout.addWidget(main_splitter, stretch=1)
    
    def _create_maps_panel(self) -> QGroupBox:
        """Create the maps management panel."""
        group = QGroupBox("🗺️ Maps")
        layout = QVBoxLayout(group)
        
        # Table
        self.maps_table = QTableWidget()
        self.maps_table.setColumnCount(2)
        self.maps_table.setHorizontalHeaderLabels(["Abbrev", "Map Name"])
        self.maps_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.maps_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.maps_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.maps_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.maps_table.cellChanged.connect(self._on_map_cell_changed)
        layout.addWidget(self.maps_table)
        
        # Buttons
        btn_row = QHBoxLayout()
        
        self.add_map_btn = QPushButton("➕")
        self.add_map_btn.setToolTip("Add Map")
        self.add_map_btn.setMaximumWidth(40)
        self.add_map_btn.clicked.connect(self._on_add_map)
        btn_row.addWidget(self.add_map_btn)
        
        self.delete_map_btn = QPushButton("🗑️")
        self.delete_map_btn.setToolTip("Delete Map")
        self.delete_map_btn.setMaximumWidth(40)
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
        
        self.add_type_btn = QPushButton("➕")
        self.add_type_btn.setToolTip("Add Type")
        self.add_type_btn.setMaximumWidth(40)
        self.add_type_btn.clicked.connect(self._on_add_type)
        btn_row.addWidget(self.add_type_btn)
        
        self.delete_type_btn = QPushButton("🗑️")
        self.delete_type_btn.setToolTip("Delete Type")
        self.delete_type_btn.setMaximumWidth(40)
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
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Filter by Map:"))
        self.map_filter = QComboBox()
        self.map_filter.setMinimumWidth(150)
        self.map_filter.currentTextChanged.connect(self._apply_filters)
        filter_layout.addWidget(self.map_filter)
        
        filter_layout.addWidget(QLabel("Type:"))
        self.type_filter = QComboBox()
        self.type_filter.setMinimumWidth(120)
        self.type_filter.currentTextChanged.connect(self._apply_filters)
        filter_layout.addWidget(self.type_filter)
        
        filter_layout.addStretch()
        
        self.location_count_label = QLabel("Showing: 0")
        filter_layout.addWidget(self.location_count_label)
        
        layout.addLayout(filter_layout)
        
        # Table
        self.locations_table = QTableWidget()
        self.locations_table.setColumnCount(3)
        self.locations_table.setHorizontalHeaderLabels(["Location Name", "Map", "Type"])
        self.locations_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.locations_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.locations_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.locations_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.locations_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.locations_table.setAlternatingRowColors(True)
        self.locations_table.setSortingEnabled(True)
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
        layout.addLayout(btn_row)
        
        return group
    
    def _load_data(self):
        """Load all data from database."""
        self._load_maps()
        self._load_types()
        self._load_locations()
        self._update_filter_combos()
        self._update_stats()
    
    def _load_maps(self):
        """Load maps into the table."""
        self.maps_table.blockSignals(True)
        self.maps_table.setRowCount(0)
        
        maps = self.db.get_maps()
        self.maps_table.setRowCount(len(maps))
        
        for row, map_data in enumerate(maps):
            # Abbreviation
            abbrev_item = QTableWidgetItem(map_data['abbreviation'])
            abbrev_item.setData(Qt.ItemDataRole.UserRole, map_data['id'])
            self.maps_table.setItem(row, 0, abbrev_item)
            
            # Name
            name_item = QTableWidgetItem(map_data['name'])
            self.maps_table.setItem(row, 1, name_item)
        
        self.maps_table.blockSignals(False)
    
    def _load_types(self):
        """Load location types into the table."""
        self.types_table.blockSignals(True)
        self.types_table.setRowCount(0)
        
        types = self.db.get_location_types()
        self.types_table.setRowCount(len(types))
        
        for row, type_data in enumerate(types):
            item = QTableWidgetItem(type_data['name'])
            item.setData(Qt.ItemDataRole.UserRole, type_data['id'])
            self.types_table.setItem(row, 0, item)
        
        self.types_table.blockSignals(False)
    
    def _load_locations(self, map_filter: str = None, type_filter: str = None):
        """Load locations into the table with optional filters."""
        self.locations_table.blockSignals(True)
        self.locations_table.setSortingEnabled(False)
        self.locations_table.setRowCount(0)
        
        # Get locations with filters
        locations = self.db.get_locations(
            map_name=map_filter if map_filter and map_filter != "All Maps" else None,
            location_type=type_filter if type_filter and type_filter != "All Types" else None
        )
        
        self.locations_table.setRowCount(len(locations))
        
        # Color coding by type
        type_colors = {
            'Base': QColor(200, 230, 255),          # Light blue
            'Infrastructure': QColor(255, 230, 200),  # Light orange
            'Mine Site': QColor(220, 220, 220),      # Light gray
            'Drill Site': QColor(255, 220, 220),     # Light red
            'Stockpile': QColor(220, 255, 220),      # Light green
            'Pad': QColor(255, 255, 200),            # Light yellow
            'Processing': QColor(230, 200, 255),     # Light purple
            'Feature': QColor(200, 255, 255),        # Light cyan
        }
        
        for row, loc in enumerate(locations):
            # Name
            name_item = QTableWidgetItem(loc['name'])
            name_item.setData(Qt.ItemDataRole.UserRole, loc['id'])
            self.locations_table.setItem(row, 0, name_item)
            
            # Map
            map_item = QTableWidgetItem(loc['map'])
            self.locations_table.setItem(row, 1, map_item)
            
            # Type
            type_item = QTableWidgetItem(loc['type'])
            self.locations_table.setItem(row, 2, type_item)
            
            # Apply color based on type
            loc_type = loc['type']
            if loc_type in type_colors:
                for col in range(3):
                    self.locations_table.item(row, col).setBackground(type_colors[loc_type])
        
        self.locations_table.setSortingEnabled(True)
        self.locations_table.blockSignals(False)
        
        self.location_count_label.setText(f"Showing: {len(locations)}")
    
    def _update_filter_combos(self):
        """Update the filter combo boxes."""
        # Save current selections
        current_map = self.map_filter.currentText()
        current_type = self.type_filter.currentText()
        
        # Update map filter
        self.map_filter.blockSignals(True)
        self.map_filter.clear()
        self.map_filter.addItem("All Maps")
        maps = self.db.get_maps()
        for m in maps:
            self.map_filter.addItem(m['name'])
        
        # Restore selection if possible
        idx = self.map_filter.findText(current_map)
        if idx >= 0:
            self.map_filter.setCurrentIndex(idx)
        self.map_filter.blockSignals(False)
        
        # Update type filter
        self.type_filter.blockSignals(True)
        self.type_filter.clear()
        self.type_filter.addItem("All Types")
        types = self.db.get_location_types()
        for t in types:
            self.type_filter.addItem(t['name'])
        
        # Restore selection if possible
        idx = self.type_filter.findText(current_type)
        if idx >= 0:
            self.type_filter.setCurrentIndex(idx)
        self.type_filter.blockSignals(False)
    
    def _update_stats(self):
        """Update the statistics label."""
        maps = self.db.get_maps()
        types = self.db.get_location_types()
        locations = self.db.get_locations()
        self.stats_label.setText(f"Maps: {len(maps)} | Types: {len(types)} | Locations: {len(locations)}")
    
    def _apply_filters(self):
        """Apply the current filters to the locations table."""
        map_filter = self.map_filter.currentText()
        type_filter = self.type_filter.currentText()
        self._load_locations(map_filter, type_filter)
    
    def _on_map_cell_changed(self, row, col):
        """Handle map cell edit."""
        item = self.maps_table.item(row, 0)
        if not item:
            return
        
        map_id = item.data(Qt.ItemDataRole.UserRole)
        
        abbrev = self.maps_table.item(row, 0).text().strip().upper()
        name = self.maps_table.item(row, 1).text().strip()
        
        if abbrev and name:
            self.db.update_map(map_id, abbrev, name)
            self._update_filter_combos()
            self._load_locations()
            self._update_stats()
    
    def _on_type_cell_changed(self, row, col):
        """Handle type cell edit."""
        item = self.types_table.item(row, 0)
        if not item:
            return
        
        type_id = item.data(Qt.ItemDataRole.UserRole)
        name = item.text().strip()
        
        if name:
            self.db.update_location_type(type_id, name)
            self._update_filter_combos()
            self._load_locations()
            self._update_stats()
    
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
        self._update_stats()
        self.data_changed.emit()
    
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
        self._update_stats()
        self.data_changed.emit()
    
    def _on_add_type(self):
        """Add a new location type."""
        name, ok = QInputDialog.getText(self, "Add Location Type", "Type Name:")
        if ok and name.strip():
            self.db.add_location_type(name.strip())
            self._load_types()
            self._update_filter_combos()
            self._update_stats()
            self.data_changed.emit()
    
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
        self._update_stats()
        self.data_changed.emit()
    
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
                self._apply_filters()
                self._update_stats()
                self.data_changed.emit()
    
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
                self._apply_filters()
                self._update_stats()
                self.data_changed.emit()
    
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
            self._apply_filters()
            self._update_stats()
            self.data_changed.emit()
    
    def _on_import_excel(self):
        """Import locations from Excel file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Dashboard Excel File",
            "",
            "Excel Files (*.xlsx *.xls);;All Files (*)"
        )
        
        if not file_path:
            return
        
        self.import_btn.setEnabled(False)
        self.import_btn.setText("Importing...")
        QApplication.processEvents()
        
        try:
            import pandas as pd
            
            xl = pd.ExcelFile(file_path)
            
            # Check for Location List sheet
            if 'Location List' not in xl.sheet_names:
                QMessageBox.warning(
                    self, "Sheet Not Found",
                    "Could not find 'Location List' sheet in the Excel file."
                )
                return
            
            df = pd.read_excel(xl, sheet_name='Location List')
            
            # Expected columns: Location, Map, Type
            if 'Location' not in df.columns or 'Map' not in df.columns:
                QMessageBox.warning(
                    self, "Invalid Format",
                    "Expected columns: Location, Map, Type"
                )
                return
            
            # Get unique maps and types
            unique_maps = df['Map'].dropna().unique()
            unique_types = df['Type'].dropna().unique() if 'Type' in df.columns else []
            
            # Add maps (need to extract abbreviation from location names)
            map_abbrevs = {}
            for _, row in df.iterrows():
                loc_name = str(row['Location'])
                map_name = str(row['Map'])
                
                # Extract abbreviation from location name (e.g., "FQR - Main Base" -> "FQR")
                if ' - ' in loc_name:
                    abbrev = loc_name.split(' - ')[0].strip()
                    if map_name not in map_abbrevs:
                        map_abbrevs[map_name] = abbrev
            
            # Add maps to database
            existing_maps = {m['name']: m for m in self.db.get_maps()}
            for map_name in unique_maps:
                if map_name not in existing_maps:
                    abbrev = map_abbrevs.get(map_name, map_name[:3].upper())
                    self.db.add_map(abbrev, map_name)
            
            # Add types to database
            existing_types = {t['name']: t for t in self.db.get_location_types()}
            for type_name in unique_types:
                if type_name not in existing_types:
                    self.db.add_location_type(type_name)
            
            # Add locations
            existing_locations = {loc['name']: loc for loc in self.db.get_locations()}
            added = 0
            updated = 0
            
            for _, row in df.iterrows():
                loc_name = str(row['Location'])
                map_name = str(row['Map'])
                loc_type = str(row['Type']) if 'Type' in df.columns and pd.notna(row['Type']) else ''
                
                if loc_name in existing_locations:
                    # Update existing
                    loc_id = existing_locations[loc_name]['id']
                    self.db.update_location(loc_id, loc_name, map_name, loc_type)
                    updated += 1
                else:
                    # Add new
                    self.db.add_location(loc_name, map_name, loc_type)
                    added += 1
            
            # Reload data
            self._load_data()
            
            QMessageBox.information(
                self, "Import Complete",
                f"Import complete!\n\n"
                f"Maps: {len(unique_maps)}\n"
                f"Types: {len(unique_types)}\n"
                f"Locations added: {added}\n"
                f"Locations updated: {updated}"
            )
            
            self.data_changed.emit()
            
        except Exception as e:
            import traceback
            QMessageBox.critical(
                self, "Import Error",
                f"Failed to import:\n{str(e)}\n\n{traceback.format_exc()}"
            )
        finally:
            self.import_btn.setEnabled(True)
            self.import_btn.setText("📥 Import from Excel")
    
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
        
        self._load_data()
        
        QMessageBox.information(
            self, "Complete",
            f"Generated {count} new locations."
        )
        
        self.data_changed.emit()
    
    # --- Public API for other tabs ---
    
    def get_all_locations(self) -> list[dict]:
        """Get all locations for other tabs."""
        return self.db.get_locations()
    
    def get_location_names(self) -> list[str]:
        """Get all location names for autocomplete."""
        locations = self.db.get_locations()
        return [loc['name'] for loc in locations]
    
    def get_maps(self) -> list[dict]:
        """Get all maps."""
        return self.db.get_maps()
    
    def get_location_types(self) -> list[dict]:
        """Get all location types."""
        return self.db.get_location_types()
