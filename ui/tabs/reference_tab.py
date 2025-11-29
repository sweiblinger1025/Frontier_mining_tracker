"""
Reference Data Tab - Item database with prices, rules, and skill discounts

Features:
- Full item table (520 items) with prices and rules
- Search and filter functionality
- Skill discount controls (VN Level, IF Level)
- Import/Export Excel buttons
- Editable Can Buy/Can Sell dropdowns
- Sub-tabs for different reference data types
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
    QSpinBox,
    QGroupBox,
    QFileDialog,
    QMessageBox,
    QAbstractItemView,
    QApplication,
    QInputDialog,
    QTabWidget,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor

from pathlib import Path
from typing import Optional

from core.database import Database, get_database
from core.models import Item
from importers.excel_importer import ExcelImporter
from ui.tabs.factory_subtab import FactoryEquipmentSubTab
from ui.tabs.vehicles_subtab import VehiclesSubTab
from ui.tabs.buildings_subtab import BuildingsSubTab
from ui.tabs.recipes_subtab import RecipesSubTab
from ui.tabs.locations_subtab import LocationsSubTab


class ReferenceDataTab(QWidget):
    """Reference Data tab with sub-tabs for items, factory equipment, etc."""
    
    # Signal emitted when data is imported/changed
    data_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = get_database()
        self.importer = ExcelImporter(self.db)
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the user interface with sub-tabs."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Create tab widget for sub-tabs
        self.sub_tabs = QTabWidget()
        self.sub_tabs.setTabPosition(QTabWidget.TabPosition.North)
        
        # Items Sub-Tab (the original content)
        self.items_tab = ItemsSubTab(self)
        self.items_tab.data_changed.connect(self._on_data_changed)
        self.sub_tabs.addTab(self.items_tab, "📦 Items")
        
        # Factory Equipment Sub-Tab
        self.factory_tab = FactoryEquipmentSubTab(self)
        self.factory_tab.data_changed.connect(self._on_data_changed)
        self.sub_tabs.addTab(self.factory_tab, "🏭 Factory Equipment")
        
        # Vehicles Sub-Tab
        self.vehicles_tab = VehiclesSubTab(self)
        self.vehicles_tab.data_changed.connect(self._on_data_changed)
        self.sub_tabs.addTab(self.vehicles_tab, "🚛 Vehicles")
        
        # Buildings Sub-Tab
        self.buildings_tab = BuildingsSubTab(self)
        self.buildings_tab.data_changed.connect(self._on_data_changed)
        self.sub_tabs.addTab(self.buildings_tab, "🏗️ Buildings")
        
        # Recipes Sub-Tab
        self.recipes_tab = RecipesSubTab(self)
        self.recipes_tab.data_changed.connect(self._on_data_changed)
        self.sub_tabs.addTab(self.recipes_tab, "📋 Recipes")
        
        # Locations Sub-Tab
        self.locations_tab = LocationsSubTab(self)
        self.locations_tab.data_changed.connect(self._on_data_changed)
        self.sub_tabs.addTab(self.locations_tab, "📍 Locations")
        
        layout.addWidget(self.sub_tabs)
    
    def _on_data_changed(self):
        """Handle data changes from sub-tabs."""
        self.data_changed.emit()
    
    # Delegate methods to items tab for backwards compatibility
    def get_item_by_name(self, name: str) -> Optional[Item]:
        """Get item by name (for other tabs to use)."""
        return self.items_tab.get_item_by_name(name)
    
    def get_item_by_name_and_category(self, name: str, category: str) -> Optional[Item]:
        """Get item by name and category (for duplicates)."""
        return self.items_tab.get_item_by_name_and_category(name, category)
    
    def get_all_item_names(self) -> list[str]:
        """Get all item names (for autocomplete)."""
        return self.items_tab.get_all_item_names()
    
    def get_purchasable_items(self) -> list[Item]:
        """Get items that can be purchased."""
        return self.items_tab.get_purchasable_items()
    
    def get_sellable_items(self) -> list[Item]:
        """Get items that can be sold."""
        return self.items_tab.get_sellable_items()
    
    # Delegate methods to locations tab for backwards compatibility
    def get_all_locations(self) -> list[dict]:
        """Get all locations (for other tabs to use)."""
        return self.locations_tab.get_all_locations()
    
    def get_location_names(self) -> list[str]:
        """Get all location names (for autocomplete)."""
        return self.locations_tab.get_location_names()
    
    def get_maps(self) -> list[dict]:
        """Get all maps."""
        return self.locations_tab.get_maps()
    
    def get_location_types(self) -> list[dict]:
        """Get all location types."""
        return self.locations_tab.get_location_types()


class ItemsSubTab(QWidget):
    """Items sub-tab showing all items with prices and rules."""
    
    data_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = get_database()
        self.importer = ExcelImporter(self.db)
        self.all_items: list[Item] = []
        self.filtered_items: list[Item] = []
        
        self._setup_ui()
        self._load_data()
    
    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Top section: Filters and Skill Discounts
        top_layout = QHBoxLayout()
        
        # Left side: Search and Filters
        filter_group = self._create_filter_group()
        top_layout.addWidget(filter_group, stretch=2)
        
        # Right side: Skill Discounts
        discount_group = self._create_discount_group()
        top_layout.addWidget(discount_group, stretch=1)
        
        layout.addLayout(top_layout)
        
        # Middle section: Import/Export buttons and item count
        button_layout = QHBoxLayout()
        
        self.import_excel_btn = QPushButton("📥 Import Excel")
        self.import_excel_btn.setToolTip("Import from Dashboard Excel file (all sheets)")
        self.import_excel_btn.clicked.connect(self._on_import_excel_clicked)
        button_layout.addWidget(self.import_excel_btn)
        
        self.import_csv_btn = QPushButton("📄 Import CSV")
        self.import_csv_btn.setToolTip("Import individual CSV files (Price Tables, Item Rules, etc.)")
        self.import_csv_btn.clicked.connect(self._on_import_csv_clicked)
        button_layout.addWidget(self.import_csv_btn)
        
        self.export_btn = QPushButton("📤 Export to Excel")
        self.export_btn.clicked.connect(self._on_export_clicked)
        button_layout.addWidget(self.export_btn)
        
        button_layout.addStretch()
        
        self.item_count_label = QLabel("Total Items: 0 | Showing: 0")
        button_layout.addWidget(self.item_count_label)
        
        layout.addLayout(button_layout)
        
        # Main section: Item Table
        self.table = self._create_table()
        layout.addWidget(self.table)
    
    def _create_filter_group(self) -> QGroupBox:
        """Create the search and filter controls."""
        group = QGroupBox("🔍 Search & Filter")
        layout = QHBoxLayout(group)
        
        # Search box
        layout.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Type to search items...")
        self.search_input.textChanged.connect(self._apply_filters)
        layout.addWidget(self.search_input, stretch=2)
        
        # Category filter
        layout.addWidget(QLabel("Category:"))
        self.category_combo = QComboBox()
        self.category_combo.setMinimumWidth(200)
        self.category_combo.currentTextChanged.connect(self._apply_filters)
        layout.addWidget(self.category_combo, stretch=1)
        
        # Show filter (All, Purchasable, Sellable, etc.)
        layout.addWidget(QLabel("Show:"))
        self.show_combo = QComboBox()
        self.show_combo.addItems([
            "All Items",
            "Can Purchase",
            "Can Sell",
            "Can't Purchase (Crafted)",
            "Can't Sell (Mfg Only)",
            "Has Discount",
        ])
        self.show_combo.currentTextChanged.connect(self._apply_filters)
        layout.addWidget(self.show_combo)
        
        return group
    
    def _create_discount_group(self) -> QGroupBox:
        """Create the skill discount controls."""
        group = QGroupBox("🎯 Skill Discounts")
        layout = QHBoxLayout(group)
        
        # VN Level (0-7, 0.5% per level = max 3.5%)
        layout.addWidget(QLabel("VN Level:"))
        self.vn_level_spin = QSpinBox()
        self.vn_level_spin.setRange(0, 7)
        self.vn_level_spin.setValue(0)
        self.vn_level_spin.valueChanged.connect(self._on_discount_changed)
        layout.addWidget(self.vn_level_spin)
        
        self.vn_percent_label = QLabel("(0.0%)")
        layout.addWidget(self.vn_percent_label)
        
        layout.addSpacing(20)
        
        # IF Level (0-6, 0.5% per level = max 3.0%)
        layout.addWidget(QLabel("IF Level:"))
        self.if_level_spin = QSpinBox()
        self.if_level_spin.setRange(0, 6)
        self.if_level_spin.setValue(0)
        self.if_level_spin.valueChanged.connect(self._on_discount_changed)
        layout.addWidget(self.if_level_spin)
        
        self.if_percent_label = QLabel("(0.0%)")
        layout.addWidget(self.if_percent_label)
        
        layout.addSpacing(20)
        
        # Combined display
        self.combined_label = QLabel("All: 0% | Vehicles: 0%")
        self.combined_label.setStyleSheet("font-weight: bold; color: #2e7d32;")
        layout.addWidget(self.combined_label)
        
        return group
    
    def _create_table(self) -> QTableWidget:
        """Create the item table."""
        table = QTableWidget()
        
        # Define columns
        self.columns = [
            "Item Name",
            "Category", 
            "Base Price",
            "Sell Price",
            "Current Buy",
            "Margin",
            "ROI %",
            "Can Buy?",
            "Can Sell?",
        ]
        
        table.setColumnCount(len(self.columns))
        table.setHorizontalHeaderLabels(self.columns)
        
        # Configure table
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        table.setSortingEnabled(True)
        
        # Configure header
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Item Name
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Category
        for i in range(2, len(self.columns)):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        
        return table
    
    def _load_data(self):
        """Load items from database."""
        self.all_items = self.importer.get_all_items()
        
        # Populate category dropdown
        categories = sorted(set(item.category for item in self.all_items if item.category))
        self.category_combo.clear()
        self.category_combo.addItem("All Categories")
        self.category_combo.addItems(categories)
        
        # Load game settings for discount levels
        settings = self.db.get_game_settings()
        self.vn_level_spin.setValue(settings.vendor_negotiation_level)
        self.if_level_spin.setValue(settings.investment_forecasting_level)
        self._update_discount_labels()
        
        # Apply filters and populate table
        self._apply_filters()
    
    def _apply_filters(self):
        """Filter items based on search, category, and show filter."""
        search_text = self.search_input.text().lower().strip()
        category_filter = self.category_combo.currentText()
        show_filter = self.show_combo.currentText()
        
        self.filtered_items = []
        
        for item in self.all_items:
            # Search filter
            if search_text:
                if search_text not in item.name.lower() and search_text not in item.category.lower():
                    continue
            
            # Category filter
            if category_filter != "All Categories":
                if item.category != category_filter:
                    continue
            
            # Show filter
            if show_filter == "Can Purchase" and not item.can_purchase:
                continue
            elif show_filter == "Can Sell" and not item.can_sell:
                continue
            elif show_filter == "Can't Purchase (Crafted)" and item.can_purchase:
                continue
            elif show_filter == "Can't Sell (Mfg Only)" and item.can_sell:
                continue
            elif show_filter == "Has Discount":
                # Check if item has a calculated discount
                current_price = self._get_current_buy_price(item)
                if current_price >= item.buy_price:
                    continue
            
            self.filtered_items.append(item)
        
        self._populate_table()
        self._update_item_count()
    
    def _populate_table(self):
        """Populate the table with filtered items."""
        self.table.setSortingEnabled(False)  # Disable during population
        self.table.setRowCount(len(self.filtered_items))
        
        for row, item in enumerate(self.filtered_items):
            # Item Name
            name_item = QTableWidgetItem(item.name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 0, name_item)
            
            # Category
            cat_item = QTableWidgetItem(item.category)
            cat_item.setFlags(cat_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 1, cat_item)
            
            # Base Price (whole number)
            base_price_item = QTableWidgetItem(f"${item.buy_price:,.0f}")
            base_price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            base_price_item.setFlags(base_price_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 2, base_price_item)
            
            # Sell Price (can have decimals for bulk pricing)
            if item.sell_price == int(item.sell_price):
                sell_price_text = f"${item.sell_price:,.0f}"
            else:
                sell_price_text = f"${item.sell_price:,.2f}"
            sell_price_item = QTableWidgetItem(sell_price_text)
            sell_price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            sell_price_item.setFlags(sell_price_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 3, sell_price_item)
            
            # Current Buy - calculated from base price with skill discounts
            current_buy_price = self._get_current_buy_price(item)
            has_discount = current_buy_price < item.buy_price
            
            # Current buy can have decimals from discount calculation
            if current_buy_price == int(current_buy_price):
                current_buy_text = f"${current_buy_price:,.0f}"
            else:
                current_buy_text = f"${current_buy_price:,.2f}"
            current_buy_item = QTableWidgetItem(current_buy_text)
            current_buy_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            current_buy_item.setFlags(current_buy_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            if has_discount:
                current_buy_item.setForeground(QColor("#2e7d32"))  # Green
            self.table.setItem(row, 4, current_buy_item)
            
            # Margin (red if negative, green if positive) - can have decimals
            margin = item.sell_price - current_buy_price
            if margin == int(margin):
                margin_text = f"${margin:,.0f}"
            else:
                margin_text = f"${margin:,.2f}"
            margin_item = QTableWidgetItem(margin_text)
            margin_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            margin_item.setFlags(margin_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            if margin < 0:
                margin_item.setForeground(QColor("#c62828"))  # Red
            elif margin > 0:
                margin_item.setForeground(QColor("#2e7d32"))  # Green
            self.table.setItem(row, 5, margin_item)
            
            # ROI % (red if negative, green if positive)
            if current_buy_price > 0:
                roi = (margin / current_buy_price) * 100
            else:
                roi = 0
            roi_item = QTableWidgetItem(f"{roi:.2f}%")
            roi_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            roi_item.setFlags(roi_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            if roi < 0:
                roi_item.setForeground(QColor("#c62828"))  # Red
            elif roi > 0:
                roi_item.setForeground(QColor("#2e7d32"))  # Green
            self.table.setItem(row, 6, roi_item)
            
            # Can Buy? - Editable ComboBox
            can_buy_combo = QComboBox()
            can_buy_combo.addItems(["Yes", "No"])
            can_buy_combo.setCurrentText("Yes" if item.can_purchase else "No")
            can_buy_combo.currentTextChanged.connect(
                lambda text, r=row, i=item: self._on_can_buy_changed(r, i, text)
            )
            self.table.setCellWidget(row, 7, can_buy_combo)
            
            # Can Sell? - Editable ComboBox
            can_sell_combo = QComboBox()
            can_sell_combo.addItems(["Yes", "No"])
            can_sell_combo.setCurrentText("Yes" if item.can_sell else "No")
            can_sell_combo.currentTextChanged.connect(
                lambda text, r=row, i=item: self._on_can_sell_changed(r, i, text)
            )
            self.table.setCellWidget(row, 8, can_sell_combo)
        
        self.table.setSortingEnabled(True)
    
    def _on_can_buy_changed(self, row: int, item: Item, text: str):
        """Handle Can Buy dropdown change."""
        can_purchase = (text == "Yes")
        
        # Update database
        with self.db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE items SET can_purchase = ? 
                WHERE name = ? AND category = ?
            """, (1 if can_purchase else 0, item.name, item.category))
        
        # Update the item in our cache
        item.can_purchase = can_purchase
        
        # Show brief status
        self._show_status(f"Updated '{item.name}': Can Buy = {text}")
    
    def _on_can_sell_changed(self, row: int, item: Item, text: str):
        """Handle Can Sell dropdown change."""
        can_sell = (text == "Yes")
        
        # Update database
        with self.db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE items SET can_sell = ? 
                WHERE name = ? AND category = ?
            """, (1 if can_sell else 0, item.name, item.category))
        
        # Update the item in our cache
        item.can_sell = can_sell
        
        # Show brief status
        self._show_status(f"Updated '{item.name}': Can Sell = {text}")
    
    def _show_status(self, message: str):
        """Show a status message (could be expanded to use a status bar)."""
        # For now, just update the item count label briefly
        # In the future, this could emit a signal to the main window's status bar
        print(message)  # Debug output
    
    def _update_item_count(self):
        """Update the item count label."""
        total = len(self.all_items)
        showing = len(self.filtered_items)
        self.item_count_label.setText(f"Total Items: {total} | Showing: {showing}")
    
    def _update_discount_labels(self):
        """Update the discount percentage labels."""
        vn_level = self.vn_level_spin.value()
        if_level = self.if_level_spin.value()
        
        # 0.5% per level
        vn_percent = vn_level * 0.5
        if_percent = if_level * 0.5
        combined_vehicle = vn_percent + if_percent
        
        self.vn_percent_label.setText(f"({vn_percent:.1f}%)")
        self.if_percent_label.setText(f"({if_percent:.1f}%)")
        self.combined_label.setText(f"All: {vn_percent:.1f}% | Vehicles: {combined_vehicle:.1f}%")
    
    def _on_discount_changed(self):
        """Handle discount level changes - recalculate prices and refresh table."""
        self._update_discount_labels()
        
        # Save to game settings
        settings = self.db.get_game_settings()
        settings.vendor_negotiation_level = self.vn_level_spin.value()
        settings.vendor_negotiation_discount = self.vn_level_spin.value() * 0.005  # 0.5% per level
        settings.investment_forecasting_level = self.if_level_spin.value()
        settings.investment_forecasting_discount = self.if_level_spin.value() * 0.005
        self.db.save_game_settings(settings)
        
        # Refresh the table to show updated current buy prices
        self._populate_table()
    
    def _get_current_buy_price(self, item: Item) -> float:
        """
        Calculate current buy price based on base price and skill discounts.
        
        VN (Vendor Negotiation) applies to ALL items.
        IF (Investment Forecasting) applies only to VEHICLES.
        """
        vn_discount = self.vn_level_spin.value() * 0.005  # 0.5% per level
        if_discount = self.if_level_spin.value() * 0.005  # 0.5% per level
        
        # Check if item is a vehicle (category starts with "Vehicles")
        is_vehicle = item.category.startswith("Vehicles")
        
        if is_vehicle:
            total_discount = vn_discount + if_discount
        else:
            total_discount = vn_discount
        
        # Calculate discounted price
        current_price = item.buy_price * (1 - total_discount)
        return current_price
    
    def _on_import_excel_clicked(self):
        """Handle Import from Excel button click."""
        # Get file paths
        dashboard_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Dashboard Excel File (Frontier_Mining_Dashboard.xlsx)",
            "",
            "Excel Files (*.xlsx *.xls);;All Files (*)"
        )
        
        if not dashboard_path:
            return
        
        # Verify file exists
        if not Path(dashboard_path).exists():
            QMessageBox.critical(self, "Error", f"File not found:\n{dashboard_path}")
            return
        
        # Ask for tracker file (optional)
        reply = QMessageBox.question(
            self,
            "Import Item Rules",
            "Do you also want to import Item Rules from the Challenge Tracker file?\n\n"
            "(This adds Can Buy/Can Sell rules for challenge mode)",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        tracker_path = None
        if reply == QMessageBox.StandardButton.Yes:
            tracker_path, _ = QFileDialog.getOpenFileName(
                self,
                "Select Challenge Tracker Excel File",
                "",
                "Excel Files (*.xlsx *.xls);;All Files (*)"
            )
        
        # Show progress
        self.import_excel_btn.setEnabled(False)
        self.import_excel_btn.setText("Importing...")
        QApplication.processEvents()
        
        # Perform import
        try:
            results = self.importer.import_all_reference_data(
                Path(dashboard_path),
                Path(tracker_path) if tracker_path else None
            )
            
            # Show results
            msg = f"Import Complete!\n\n"
            msg += f"✓ Items: {results['items']}\n"
            msg += f"✓ Categories: {results['categories']}\n"
            msg += f"✓ Locations: {results['locations']}\n"
            msg += f"✓ Game Settings: {'Yes' if results['game_settings'] else 'No'}"
            
            if results['errors']:
                msg += f"\n\n⚠ Errors:\n" + "\n".join(results['errors'])
            
            QMessageBox.information(self, "Import Results", msg)
            
            # Reload data
            self._load_data()
            self.data_changed.emit()
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            QMessageBox.critical(
                self, 
                "Import Error", 
                f"Failed to import:\n{str(e)}\n\nDetails:\n{error_details}"
            )
        finally:
            self.import_excel_btn.setEnabled(True)
            self.import_excel_btn.setText("📥 Import Excel")
    
    def _on_import_csv_clicked(self):
        """Handle Import CSV button click - shows dialog to select which CSV to import."""
        # Create a dialog to choose what to import
        items = [
            "Price Tables (items with prices)",
            "Item Rules (Can Buy/Can Sell rules)",
            "Both Price Tables + Item Rules",
        ]
        
        choice, ok = QInputDialog.getItem(
            self,
            "Import CSV",
            "What would you like to import?",
            items,
            0,
            False
        )
        
        if not ok:
            return
        
        results = {"items": 0, "rules": 0, "errors": []}
        
        try:
            if choice == items[0] or choice == items[2]:
                # Import Price Tables
                price_path, _ = QFileDialog.getOpenFileName(
                    self,
                    "Select Price Tables CSV",
                    "",
                    "CSV Files (*.csv);;All Files (*)"
                )
                
                if price_path:
                    self.import_csv_btn.setEnabled(False)
                    self.import_csv_btn.setText("Importing...")
                    QApplication.processEvents()
                    
                    results["items"] = self.importer.import_price_tables_csv(Path(price_path))
            
            if choice == items[1] or choice == items[2]:
                # Import Item Rules
                rules_path, _ = QFileDialog.getOpenFileName(
                    self,
                    "Select Item Rules CSV",
                    "",
                    "CSV Files (*.csv);;All Files (*)"
                )
                
                if rules_path:
                    self.import_csv_btn.setEnabled(False)
                    self.import_csv_btn.setText("Importing...")
                    QApplication.processEvents()
                    
                    results["rules"] = self.importer.import_item_rules_csv(Path(rules_path))
            
            # Show results
            msg = "Import Complete!\n\n"
            if results["items"] > 0:
                msg += f"✓ Items (Price Tables): {results['items']}\n"
            if results["rules"] > 0:
                msg += f"✓ Item Rules updated: {results['rules']}\n"
            
            if results["items"] == 0 and results["rules"] == 0:
                msg = "No files were imported."
            
            QMessageBox.information(self, "CSV Import Results", msg)
            
            # Reload data
            self._load_data()
            self.data_changed.emit()
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            QMessageBox.critical(
                self,
                "Import Error",
                f"Failed to import CSV:\n{str(e)}\n\nDetails:\n{error_details}"
            )
        finally:
            self.import_csv_btn.setEnabled(True)
            self.import_csv_btn.setText("📄 Import CSV")
    
    def _on_export_clicked(self):
        """Handle Export to Excel button click."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export to Excel",
            "item_database.xlsx",
            "Excel Files (*.xlsx);;All Files (*)"
        )
        
        if not file_path:
            return
        
        try:
            import pandas as pd
            
            # Build data for export
            data = []
            for item in self.all_items:
                data.append({
                    "Item Name": item.name,
                    "Category": item.category,
                    "Base Price": item.buy_price,
                    "Current Buy Price": item.current_buy_price,
                    "Sell Price": item.sell_price,
                    "Margin": item.sell_price - item.current_buy_price,
                    "ROI %": ((item.sell_price - item.current_buy_price) / item.current_buy_price * 100) if item.current_buy_price > 0 else 0,
                    "Can Purchase?": "Yes" if item.can_purchase else "No",
                    "Can Sell?": "Yes" if item.can_sell else "No",
                })
            
            df = pd.DataFrame(data)
            df.to_excel(file_path, index=False)
            
            QMessageBox.information(self, "Export Complete", f"Exported {len(data)} items to:\n{file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export:\n{str(e)}")
    
    def get_item_by_name(self, name: str) -> Optional[Item]:
        """Get item by name (for other tabs to use)."""
        return self.importer.get_item_by_name(name)
    
    def get_item_by_name_and_category(self, name: str, category: str) -> Optional[Item]:
        """Get item by name and category (for duplicates)."""
        return self.importer.get_item_by_name_and_category(name, category)
    
    def get_all_item_names(self) -> list[str]:
        """Get all item names (for autocomplete)."""
        return [item.name for item in self.all_items]
    
    def get_all_items(self) -> list[dict]:
        """Get all items as dictionaries for syncing with Settings."""
        return [
            {
                "name": item.name,
                "category": item.category,
                "can_purchase": item.can_purchase,
                "can_sell": item.can_sell,
            }
            for item in self.all_items
        ]
    
    def get_purchasable_items(self) -> list[Item]:
        """Get items that can be purchased."""
        return [item for item in self.all_items if item.can_purchase]
    
    def get_sellable_items(self) -> list[Item]:
        """Get items that can be sold."""
        return [item for item in self.all_items if item.can_sell]
