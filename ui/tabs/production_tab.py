"""
Production Tab - Manufacturing and processing workflow management.

Sub-tabs:
- Production Calculator: Calculate materials needed for recipes
- Production Log: Track production runs
- Cost Analysis: Analyze recipe profitability
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QComboBox, QSpinBox, QDoubleSpinBox, QCheckBox, QTabWidget,
    QFormLayout, QFrame, QSplitter, QTreeWidget, QTreeWidgetItem,
    QDateTimeEdit, QMessageBox, QAbstractItemView, QTextEdit
)
from PyQt6.QtCore import Qt, pyqtSignal, QDateTime
from PyQt6.QtGui import QFont, QColor
from datetime import datetime

# Import recipe data
from ui.tabs.recipes_subtab import RECIPE_DATA
from ui.tabs.buildings_subtab import BUILDING_DATA


class ProductionTab(QWidget):
    """Production tab for manufacturing workflow."""
    
    data_changed = pyqtSignal()
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        
        # Production log storage
        self.production_log = []
        
        # Build recipe lookup dictionaries
        self._build_lookups()
        
        self._setup_ui()
    
    def _build_lookups(self):
        """Build lookup dictionaries for recipes and items."""
        # Recipe lookup by output
        self.recipes_by_output = {}
        for recipe in RECIPE_DATA:
            output = recipe["output"]
            if output not in self.recipes_by_output:
                self.recipes_by_output[output] = []
            self.recipes_by_output[output].append(recipe)
        
        # Recipe lookup by workbench
        self.recipes_by_workbench = {}
        for recipe in RECIPE_DATA:
            wb = recipe["workbench"]
            if wb not in self.recipes_by_workbench:
                self.recipes_by_workbench[wb] = []
            self.recipes_by_workbench[wb].append(recipe)
        
        # All unique outputs
        self.all_outputs = sorted(set(r["output"] for r in RECIPE_DATA))
        
        # All workbenches
        self.all_workbenches = sorted(set(r["workbench"] for r in RECIPE_DATA))
        
        # Fallback prices (SELL prices for accurate value tracking)
        self._fallback_prices = {
            # Resources - Ore (sell prices)
            "Aluminium Ore": 26, "Coal": 9, "Copper Ore": 20,
            "Diamond Ore": 32, "Gold Ore": 30, "Iron Ore": 17,
            "Lithium Ore": 37, "Platinum Ore": 39, "Ruby Ore": 32, 
            "Silicon Ore": 35, "Silver Ore": 29,
            # Resources - Wood
            "Tree Logs": 4, "Log": 4,
            # Materials - Ore (Bars, Diamond, Ruby) - sell prices
            "Aluminium Bar": 105, "Copper Bar": 67, "Diamond": 186,
            "Gold Bar": 147, "Iron Bar": 46, "Lithium Bar": 175,
            "Platinum Bar": 186, "Ruby": 193, "Silicon Bar": 56,
            "Silver Bar": 123, "Steel Bar": 60,
            # Materials - Concrete
            "Cement": 11,
            # Materials - Sub Parts
            "Electronic Parts": 140, "Empty Barrel": 35, "Plastics": 56,
            "Rubber": 63, "Wearplate": 105,
            # Materials - Fuel
            "Fuel": 70,
            # Materials - Metals
            "Steel Rod": 84, "Steel Sheet": 84,
            # Materials - Wood
            "Wood Beam": 6, "Wood Plank": 6, "Wood Sheet": 6,
            # Resources - Fluids (sell prices)
            "Oil": 47, "Crude Oil": 47, "Refined Oil": 93, 
            "Water": 4, "Unfiltered Water": 2,
            # Resources - Dirt (sell prices)
            "PayDirt": 1.50, "Dirt": 1, "Tailings": 0.50,
            # Resources - Rock (sell prices)
            "Crushed Rock": 4, "Blasted Rock": 3, "Solid Rock": 3, "Gravel": 4,
        }
    
    def _setup_ui(self):
        """Set up the production tab interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Create sub-tab widget
        self.sub_tabs = QTabWidget()
        
        # Add sub-tabs
        self.calculator_tab = ProductionCalculatorSubTab(self)
        self.sub_tabs.addTab(self.calculator_tab, "⚙️ Production Calculator")
        
        self.log_tab = ProductionLogSubTab(self)
        self.sub_tabs.addTab(self.log_tab, "📋 Production Log")
        
        self.analysis_tab = CostAnalysisSubTab(self)
        self.sub_tabs.addTab(self.analysis_tab, "📊 Cost Analysis")
        
        layout.addWidget(self.sub_tabs)
    
    def get_item_price(self, item_name, price_type="sell"):
        """
        Get price for an item from Reference Data.
        
        Args:
            item_name: Name of the item
            price_type: "sell" for sell price, "buy" for buy price
            
        Returns:
            Price as float, or 0 if not found
        """
        # Try to get from Reference Data
        try:
            if hasattr(self.main_window, 'reference_tab'):
                ref = self.main_window.reference_tab
                item = ref.get_item_by_name(item_name)
                if item:
                    if price_type == "sell":
                        return item.sell_price
                    else:
                        return item.buy_price
        except Exception as e:
            pass
        
        # Fallback to hardcoded prices
        return self._fallback_prices.get(item_name, 0)
    
    def get_inventory_quantity(self, item_name):
        """Get current inventory quantity for an item."""
        try:
            if hasattr(self.main_window, 'inventory_tab'):
                inv = self.main_window.inventory_tab
                for item in inv.inventory_items:
                    if item.get("name") == item_name:
                        return item.get("quantity", 0)
        except:
            pass
        return 0
    
    def calculate_chain(self, output_name, quantity, trace_full_chain=True):
        """
        Calculate all materials needed for a recipe.
        Returns list of (material, quantity_needed, depth) tuples.
        """
        results = []
        self._calculate_chain_recursive(output_name, quantity, 0, results, trace_full_chain, set())
        return results
    
    def _calculate_chain_recursive(self, output_name, quantity, depth, results, trace_full_chain, visited):
        """Recursive helper for chain calculation."""
        # Prevent infinite loops
        if output_name in visited:
            return
        
        # Find recipe for this output
        recipes = self.recipes_by_output.get(output_name, [])
        if not recipes:
            # No recipe - this is a raw material
            results.append({
                "material": output_name,
                "quantity": quantity,
                "depth": depth,
                "is_raw": True
            })
            return
        
        # Use first recipe (could be enhanced to let user choose)
        recipe = recipes[0]
        output_qty = recipe.get("output_qty", 1)
        
        # Calculate how many times we need to run the recipe
        runs_needed = (quantity + output_qty - 1) // output_qty  # Ceiling division
        
        # Add this recipe's output
        results.append({
            "material": output_name,
            "quantity": quantity,
            "depth": depth,
            "is_raw": False,
            "recipe": recipe,
            "runs": runs_needed
        })
        
        if trace_full_chain:
            visited.add(output_name)
            
            # Process each input
            for input_name, input_qty in recipe["inputs"]:
                total_input_needed = input_qty * runs_needed
                self._calculate_chain_recursive(
                    input_name, total_input_needed, depth + 1, 
                    results, trace_full_chain, visited
                )
            
            visited.remove(output_name)
        else:
            # Just show direct inputs
            for input_name, input_qty in recipe["inputs"]:
                total_input_needed = input_qty * runs_needed
                results.append({
                    "material": input_name,
                    "quantity": total_input_needed,
                    "depth": depth + 1,
                    "is_raw": True
                })


class ProductionCalculatorSubTab(QWidget):
    """Production Calculator - calculate materials needed for recipes."""
    
    def __init__(self, parent_tab):
        super().__init__()
        self.parent_tab = parent_tab
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the calculator interface."""
        layout = QVBoxLayout(self)
        
        # === Input Section ===
        input_group = QGroupBox("🎯 What do you want to make?")
        input_layout = QHBoxLayout(input_group)
        
        input_layout.addWidget(QLabel("Product:"))
        self.product_combo = QComboBox()
        self.product_combo.setEditable(True)
        self.product_combo.addItems(["-- Select Product --"] + self.parent_tab.all_outputs)
        self.product_combo.setMinimumWidth(200)
        input_layout.addWidget(self.product_combo)
        
        input_layout.addWidget(QLabel("Quantity:"))
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setRange(1, 10000)
        self.quantity_spin.setValue(10)
        self.quantity_spin.setMinimumWidth(80)
        input_layout.addWidget(self.quantity_spin)
        
        self.full_chain_check = QCheckBox("Show full production chain")
        self.full_chain_check.setChecked(True)
        self.full_chain_check.setToolTip("Trace back to raw ores/materials")
        input_layout.addWidget(self.full_chain_check)
        
        self.calculate_btn = QPushButton("🔢 Calculate")
        self.calculate_btn.clicked.connect(self._calculate)
        input_layout.addWidget(self.calculate_btn)
        
        input_layout.addStretch()
        layout.addWidget(input_group)
        
        # === Results Section ===
        results_group = QGroupBox("📋 Materials Required")
        results_layout = QVBoxLayout(results_group)
        
        # Summary cards
        cards_layout = QHBoxLayout()
        
        self.total_materials_card = self._create_card("📦 TOTAL MATERIALS", "0", "Unique items needed")
        cards_layout.addWidget(self.total_materials_card, 1)
        
        self.input_cost_card = self._create_card("💰 INPUT COST", "$0", "Raw material value")
        cards_layout.addWidget(self.input_cost_card, 1)
        
        self.output_value_card = self._create_card("💵 OUTPUT VALUE", "$0", "Finished product value")
        cards_layout.addWidget(self.output_value_card, 1)
        
        self.profit_card = self._create_card("📈 PROFIT", "$0", "Value added")
        cards_layout.addWidget(self.profit_card, 1)
        
        results_layout.addLayout(cards_layout)
        
        # Materials tree
        self.materials_tree = QTreeWidget()
        self.materials_tree.setHeaderLabels(["Material", "Needed", "In Stock", "Shortfall", "Cost"])
        self.materials_tree.setAlternatingRowColors(True)
        self.materials_tree.header().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.materials_tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        self.materials_tree.setColumnWidth(0, 250)
        results_layout.addWidget(self.materials_tree)
        
        layout.addWidget(results_group)
    
    def _create_card(self, title, value, subtitle):
        """Create a summary card."""
        card = QFrame()
        card.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        card.setStyleSheet("background-color: #E8F4FD; border-radius: 5px;")
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 8, 10, 8)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("", 9, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setObjectName("value_label")
        value_label.setFont(QFont("", 14, QFont.Weight.Bold))
        value_label.setStyleSheet("color: #1F4E79;")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(value_label)
        
        subtitle_label = QLabel(subtitle)
        subtitle_label.setObjectName("subtitle_label")
        subtitle_label.setStyleSheet("color: #666666; font-size: 10px;")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle_label)
        
        return card
    
    def _calculate(self):
        """Calculate materials needed."""
        product = self.product_combo.currentText()
        if product == "-- Select Product --" or not product:
            QMessageBox.warning(self, "Error", "Please select a product.")
            return
        
        quantity = self.quantity_spin.value()
        trace_full = self.full_chain_check.isChecked()
        
        # Calculate chain
        results = self.parent_tab.calculate_chain(product, quantity, trace_full)
        
        # Clear tree
        self.materials_tree.clear()
        
        # Build tree and calculate totals
        total_input_cost = 0
        raw_materials = {}  # Aggregate raw materials
        
        # First pass: aggregate raw materials
        for item in results:
            if item.get("is_raw") or item["depth"] > 0:
                mat = item["material"]
                qty = item["quantity"]
                if mat in raw_materials:
                    raw_materials[mat] = max(raw_materials[mat], qty)
                else:
                    raw_materials[mat] = qty
        
        # Create tree items
        root_items = {}
        for item in results:
            mat = item["material"]
            qty = item["quantity"]
            depth = item["depth"]
            is_raw = item.get("is_raw", False)
            
            # Get inventory and price
            in_stock = self.parent_tab.get_inventory_quantity(mat)
            price = self.parent_tab.get_item_price(mat)
            cost = price * qty
            shortfall = qty - in_stock
            
            # Create tree item
            tree_item = QTreeWidgetItem()
            
            # Indent based on depth
            prefix = "  " * depth + ("└ " if depth > 0 else "")
            tree_item.setText(0, f"{prefix}{mat}")
            tree_item.setText(1, f"{qty:,}")
            tree_item.setText(2, f"{in_stock:,}")
            
            # Shortfall
            if shortfall > 0:
                tree_item.setText(3, f"-{shortfall:,}")
                tree_item.setForeground(3, QColor("#CC0000"))
                tree_item.setBackground(3, QColor("#F8D6D6"))
            else:
                tree_item.setText(3, "✓")
                tree_item.setForeground(3, QColor("#008800"))
                tree_item.setBackground(3, QColor("#D5F5D5"))
            
            # Cost
            if price > 0:
                tree_item.setText(4, f"${cost:,.0f}")
                if is_raw:
                    total_input_cost += cost
            
            # Alignment
            for col in range(1, 5):
                tree_item.setTextAlignment(col, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            
            # Color raw materials differently
            if is_raw:
                tree_item.setBackground(0, QColor("#FFF2CC"))
            
            self.materials_tree.addTopLevelItem(tree_item)
        
        # Update summary cards
        output_price = self.parent_tab.get_item_price(product)
        output_value = output_price * quantity
        profit = output_value - total_input_cost
        
        self.total_materials_card.findChild(QLabel, "value_label").setText(str(len(raw_materials)))
        self.input_cost_card.findChild(QLabel, "value_label").setText(f"${total_input_cost:,.0f}")
        self.output_value_card.findChild(QLabel, "value_label").setText(f"${output_value:,.0f}")
        
        profit_label = self.profit_card.findChild(QLabel, "value_label")
        profit_label.setText(f"${profit:+,.0f}")
        if profit >= 0:
            profit_label.setStyleSheet("color: #008800;")
            self.profit_card.setStyleSheet("background-color: #D5F5D5; border-radius: 5px;")
        else:
            profit_label.setStyleSheet("color: #CC0000;")
            self.profit_card.setStyleSheet("background-color: #F8D6D6; border-radius: 5px;")
        
        # Expand all
        self.materials_tree.expandAll()


class ProductionLogSubTab(QWidget):
    """Production Log - track production runs."""
    
    def __init__(self, parent_tab):
        super().__init__()
        self.parent_tab = parent_tab
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the log interface."""
        layout = QVBoxLayout(self)
        
        # === Log Entry Form ===
        entry_group = QGroupBox("➕ Log Production Run")
        entry_layout = QVBoxLayout(entry_group)
        
        # Row 1: Building and Recipe
        row1 = QHBoxLayout()
        
        row1.addWidget(QLabel("Building:"))
        self.building_combo = QComboBox()
        self.building_combo.addItems(["-- Select Building --"] + self.parent_tab.all_workbenches)
        self.building_combo.currentIndexChanged.connect(self._on_building_changed)
        self.building_combo.setMinimumWidth(150)
        row1.addWidget(self.building_combo)
        
        # Concrete quality dropdown (only visible for Concrete Mixer)
        self.quality_label = QLabel("Quality:")
        self.quality_label.setVisible(False)
        row1.addWidget(self.quality_label)
        
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["Rough Concrete", "Standard Concrete", "Polished Concrete"])
        self.quality_combo.setMinimumWidth(130)
        self.quality_combo.setVisible(False)
        self.quality_combo.currentIndexChanged.connect(self._on_quality_changed)
        row1.addWidget(self.quality_combo)
        
        row1.addWidget(QLabel("Recipe:"))
        self.recipe_combo = QComboBox()
        self.recipe_combo.setMinimumWidth(200)
        self.recipe_combo.currentIndexChanged.connect(self._on_recipe_changed)
        row1.addWidget(self.recipe_combo)
        
        row1.addWidget(QLabel("Output Qty:"))
        self.output_qty_spin = QSpinBox()
        self.output_qty_spin.setRange(1, 10000)
        self.output_qty_spin.setValue(1)
        row1.addWidget(self.output_qty_spin)
        
        row1.addStretch()
        entry_layout.addLayout(row1)
        
        # Row 2: Date and options
        row2 = QHBoxLayout()
        
        row2.addWidget(QLabel("Date/Time:"))
        self.datetime_edit = QDateTimeEdit()
        self.datetime_edit.setDateTime(QDateTime.currentDateTime())
        self.datetime_edit.setCalendarPopup(True)
        row2.addWidget(self.datetime_edit)
        
        self.deduct_inputs_check = QCheckBox("Deduct inputs from Inventory")
        self.deduct_inputs_check.setToolTip("Reduce inventory quantities for materials used")
        row2.addWidget(self.deduct_inputs_check)
        
        self.add_outputs_check = QCheckBox("Add outputs to Inventory")
        self.add_outputs_check.setToolTip("Increase inventory quantities for products made")
        row2.addWidget(self.add_outputs_check)
        
        self.log_btn = QPushButton("📝 Log Production")
        self.log_btn.clicked.connect(self._log_production)
        row2.addWidget(self.log_btn)
        
        row2.addStretch()
        entry_layout.addLayout(row2)
        
        # Recipe info panel
        self.recipe_info = QLabel("Select a building and recipe to see details")
        self.recipe_info.setStyleSheet("color: #666; font-style: italic; padding: 5px;")
        entry_layout.addWidget(self.recipe_info)
        
        layout.addWidget(entry_group)
        
        # === Production History ===
        history_group = QGroupBox("📜 Production History")
        history_layout = QVBoxLayout(history_group)
        
        # Summary
        summary_layout = QHBoxLayout()
        self.total_runs_label = QLabel("Total Runs: 0")
        self.total_runs_label.setFont(QFont("", 10, QFont.Weight.Bold))
        summary_layout.addWidget(self.total_runs_label)
        
        summary_layout.addStretch()
        
        self.total_value_label = QLabel("Total Value Created: $0")
        self.total_value_label.setFont(QFont("", 10, QFont.Weight.Bold))
        self.total_value_label.setStyleSheet("color: #008800;")
        summary_layout.addWidget(self.total_value_label)
        
        history_layout.addLayout(summary_layout)
        
        # History table
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(6)
        self.history_table.setHorizontalHeaderLabels([
            "Date/Time", "Building", "Output", "Qty", "Inputs Used", "Value Created"
        ])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.history_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Interactive)
        self.history_table.setColumnWidth(4, 200)
        self.history_table.setAlternatingRowColors(True)
        self.history_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        history_layout.addWidget(self.history_table)
        
        # Buttons
        btn_layout = QHBoxLayout()
        self.delete_btn = QPushButton("🗑️ Delete Selected")
        self.delete_btn.clicked.connect(self._delete_selected)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addStretch()
        history_layout.addLayout(btn_layout)
        
        layout.addWidget(history_group)
    
    def _on_building_changed(self, index):
        """Handle building selection change."""
        self.recipe_combo.clear()
        
        building = self.building_combo.currentText()
        
        # Show/hide concrete quality dropdown
        is_concrete_mixer = (building == "Concrete Mixer")
        self.quality_label.setVisible(is_concrete_mixer)
        self.quality_combo.setVisible(is_concrete_mixer)
        
        if building == "-- Select Building --":
            return
        
        # Get recipes, filtering by quality if Concrete Mixer
        recipes = self.parent_tab.recipes_by_workbench.get(building, [])
        
        if is_concrete_mixer:
            # Filter recipes by selected quality
            quality = self.quality_combo.currentText()
            recipes = [r for r in recipes if r.get("notes", "") == quality]
        
        self.recipe_combo.addItem("-- Select Recipe --")
        
        # Get unique recipe outputs (avoid duplicates)
        seen = set()
        for recipe in recipes:
            output = recipe["output"]
            if output not in seen:
                seen.add(output)
                self.recipe_combo.addItem(output)
    
    def _on_quality_changed(self, index):
        """Handle concrete quality selection change."""
        # Refresh recipe list when quality changes
        building = self.building_combo.currentText()
        if building == "Concrete Mixer":
            # Save current recipe selection if possible
            current_recipe = self.recipe_combo.currentText()
            
            self.recipe_combo.clear()
            recipes = self.parent_tab.recipes_by_workbench.get(building, [])
            quality = self.quality_combo.currentText()
            recipes = [r for r in recipes if r.get("notes", "") == quality]
            
            self.recipe_combo.addItem("-- Select Recipe --")
            seen = set()
            for recipe in recipes:
                output = recipe["output"]
                if output not in seen:
                    seen.add(output)
                    self.recipe_combo.addItem(output)
            
            # Try to restore previous selection
            idx = self.recipe_combo.findText(current_recipe)
            if idx >= 0:
                self.recipe_combo.setCurrentIndex(idx)
    
    def _on_recipe_changed(self, index):
        """Handle recipe selection change."""
        building = self.building_combo.currentText()
        recipe_name = self.recipe_combo.currentText()
        
        if building == "-- Select Building --" or recipe_name == "-- Select Recipe --":
            self.recipe_info.setText("Select a building and recipe to see details")
            return
        
        # Find the recipe (consider quality for Concrete Mixer)
        recipes = self.parent_tab.recipes_by_workbench.get(building, [])
        recipe = None
        
        if building == "Concrete Mixer":
            quality = self.quality_combo.currentText()
            for r in recipes:
                if r["output"] == recipe_name and r.get("notes", "") == quality:
                    recipe = r
                    break
        else:
            for r in recipes:
                if r["output"] == recipe_name:
                    recipe = r
                    break
        
        if recipe:
            inputs_str = ", ".join([f"{qty}× {name}" for name, qty in recipe["inputs"]])
            output_qty = recipe.get("output_qty", 1)
            
            # Calculate value - for concrete, need to get price based on quality
            input_cost = sum(self.parent_tab.get_item_price(name) * qty for name, qty in recipe["inputs"])
            
            # Get output value (consider concrete quality for category-based pricing)
            if building == "Concrete Mixer":
                quality = self.quality_combo.currentText()
                output_value = self._get_concrete_price(recipe["output"], quality) * output_qty
            else:
                output_value = self.parent_tab.get_item_price(recipe["output"]) * output_qty
            
            profit = output_value - input_cost
            
            info = f"<b>Inputs:</b> {inputs_str}<br>"
            info += f"<b>Output:</b> {output_qty}× {recipe['output']}"
            if building == "Concrete Mixer":
                info += f" ({self.quality_combo.currentText()})"
            info += "<br>"
            info += f"<b>Value:</b> ${input_cost:.0f} → ${output_value:.0f} "
            if profit >= 0:
                info += f"(<span style='color: green;'>+${profit:.0f}</span>)"
            else:
                info += f"(<span style='color: red;'>${profit:.0f}</span>)"
            
            self.recipe_info.setText(info)
            self.recipe_info.setStyleSheet("padding: 5px;")
    
    def _get_concrete_price(self, item_name, quality):
        """Get concrete item price based on quality tier."""
        # Map quality to category
        category_map = {
            "Rough Concrete": "Buildings - Rough Concrete",
            "Standard Concrete": "Buildings - Concrete",
            "Polished Concrete": "Buildings - Polished Concrete",
        }
        target_category = category_map.get(quality, "Buildings - Concrete")
        
        # Try to get from Reference Data with quality-specific category
        try:
            if self.parent_tab.main_window and hasattr(self.parent_tab.main_window, 'reference_tab'):
                ref = self.parent_tab.main_window.reference_tab
                
                # Method 1: Use the database lookup method
                item = ref.get_item_by_name_and_category(item_name, target_category)
                if item:
                    return item.sell_price
                
                # Method 2: Search through all_items in the items_tab (in-memory)
                if hasattr(ref, 'items_tab') and hasattr(ref.items_tab, 'all_items'):
                    for item in ref.items_tab.all_items:
                        if item.name == item_name and item.category == target_category:
                            return item.sell_price
        except Exception as e:
            pass
        
        # Fallback - try to get standard price and estimate based on actual game ratios
        # From user's data: Rough=$1610, Standard=$1680, Polished=$1750 for Concrete Block
        # Rough is ~96% of Standard, Polished is ~104% of Standard
        base_price = self.parent_tab.get_item_price(item_name)
        if base_price > 0:
            if quality == "Rough Concrete":
                return base_price * 0.96  # Rough is ~4% cheaper than standard
            elif quality == "Polished Concrete":
                return base_price * 1.04  # Polished is ~4% more expensive
        return base_price  # Standard or unknown
    
    def _log_production(self):
        """Log a production run."""
        building = self.building_combo.currentText()
        recipe_name = self.recipe_combo.currentText()
        
        if building == "-- Select Building --":
            QMessageBox.warning(self, "Error", "Please select a building.")
            return
        
        if recipe_name == "-- Select Recipe --" or not recipe_name:
            QMessageBox.warning(self, "Error", "Please select a recipe.")
            return
        
        # Find the recipe (consider quality for Concrete Mixer)
        recipes = self.parent_tab.recipes_by_workbench.get(building, [])
        recipe = None
        concrete_quality = None
        
        if building == "Concrete Mixer":
            concrete_quality = self.quality_combo.currentText()
            for r in recipes:
                if r["output"] == recipe_name and r.get("notes", "") == concrete_quality:
                    recipe = r
                    break
        else:
            for r in recipes:
                if r["output"] == recipe_name:
                    recipe = r
                    break
        
        if not recipe:
            return
        
        output_qty = self.output_qty_spin.value()
        recipe_output_qty = recipe.get("output_qty", 1)
        runs = output_qty  # User specifies how many times to run recipe
        total_output = runs * recipe_output_qty
        
        # Calculate inputs needed
        inputs_used = [(name, qty * runs) for name, qty in recipe["inputs"]]
        inputs_str = ", ".join([f"{qty}× {name}" for name, qty in inputs_used])
        
        # Calculate value (consider concrete quality)
        input_cost = sum(self.parent_tab.get_item_price(name) * qty for name, qty in inputs_used)
        if concrete_quality:
            output_value = self._get_concrete_price(recipe["output"], concrete_quality) * total_output
        else:
            output_value = self.parent_tab.get_item_price(recipe["output"]) * total_output
        value_created = output_value - input_cost
        
        # Check if we should deduct from inventory
        inventory_tab = None
        if hasattr(self.parent_tab.main_window, 'inventory_tab'):
            inventory_tab = self.parent_tab.main_window.inventory_tab
        
        # Validate inventory has enough inputs
        if self.deduct_inputs_check.isChecked() and inventory_tab:
            insufficient = []
            for input_name, input_qty in inputs_used:
                available = inventory_tab.get_item_quantity(input_name)
                if available < input_qty:
                    insufficient.append(f"{input_name}: need {input_qty}, have {available}")
            
            if insufficient:
                reply = QMessageBox.question(
                    self, "Insufficient Inventory",
                    "Not enough materials in inventory:\n\n" + "\n".join(insufficient) +
                    "\n\nLog production anyway without deducting?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return
                # Don't deduct if they say yes but don't have enough
                self.deduct_inputs_check.setChecked(False)
        
        # Create log entry
        entry = {
            "datetime": self.datetime_edit.dateTime().toPyDateTime(),
            "building": building,
            "recipe": recipe,
            "output": recipe["output"],
            "output_qty": total_output,
            "inputs_used": inputs_used,
            "input_cost": input_cost,
            "output_value": output_value,
            "value_created": value_created,
            "deducted_inputs": self.deduct_inputs_check.isChecked(),
            "added_outputs": self.add_outputs_check.isChecked(),
            "concrete_quality": concrete_quality,  # Track quality for concrete
        }
        
        self.parent_tab.production_log.append(entry)
        self._refresh_history()
        
        # Handle inventory updates
        if inventory_tab:
            if self.deduct_inputs_check.isChecked():
                for input_name, input_qty in inputs_used:
                    inventory_tab.adjust_item_quantity(input_name, -input_qty)
            
            if self.add_outputs_check.isChecked():
                # Get category and price for the output item
                output_name = recipe["output"]
                if concrete_quality:
                    category = self._get_concrete_category(concrete_quality)
                    unit_price = self._get_concrete_price(output_name, concrete_quality)
                else:
                    category = self._guess_category(output_name)
                    unit_price = self.parent_tab.get_item_price(output_name, "sell")
                inventory_tab.add_or_update_item(
                    output_name, 
                    total_output,
                    category=category,
                    unit_price=unit_price
                )
        
        self.parent_tab.data_changed.emit()
        
        # Show confirmation
        msg_parts = [f"Logged: {total_output}× {recipe['output']}"]
        if concrete_quality:
            msg_parts[0] += f" ({concrete_quality})"
        if self.deduct_inputs_check.isChecked():
            msg_parts.append("Inputs deducted from inventory")
        if self.add_outputs_check.isChecked():
            msg_parts.append("Outputs added to inventory")
        
        # Reset form
        self.output_qty_spin.setValue(1)
        self.datetime_edit.setDateTime(QDateTime.currentDateTime())
    
    def _get_concrete_category(self, quality):
        """Get the inventory category for concrete based on quality."""
        category_map = {
            "Rough Concrete": "Buildings - Rough Concrete",
            "Standard Concrete": "Buildings - Concrete",
            "Polished Concrete": "Buildings - Polished Concrete",
        }
        return category_map.get(quality, "Buildings - Concrete")
    
    def _guess_category(self, item_name):
        """Guess category based on item name - matches game categories exactly."""
        name_lower = item_name.lower()
        
        # === MATERIALS ===
        
        # Materials - Sub Parts (Electronic Parts, Empty Barrel, Plastics, Rubber, Wearplate)
        # Check this FIRST to catch "Empty Barrel" before "bar" match
        if any(x in name_lower for x in ["electronic part", "empty barrel", "plastic", "rubber"]):
            return "Materials - Sub Parts"
        
        # Materials - Ore (Bars, Diamond, Ruby - but not Diamond Ore/Ruby Ore)
        if "bar" in name_lower:
            return "Materials - Ore"
        elif name_lower in ["diamond", "ruby"]:
            return "Materials - Ore"
        
        # Materials - Concrete (Cement)
        elif name_lower == "cement":
            return "Materials - Concrete"
        
        # Materials - Fuel (Fuel - not vehicle fuel)
        elif name_lower == "fuel":
            return "Materials - Fuel"
        
        # Materials - Metals (Steel Rod, Steel Sheet)
        elif name_lower in ["steel rod", "steel sheet"]:
            return "Materials - Metals"
        
        # Materials - Wood (Wood Beam, Wood Plank, Wood Sheet)
        elif name_lower in ["wood beam", "wood plank", "wood sheet"]:
            return "Materials - Wood"
        
        # Resources - Wood (Tree Logs - raw wood)
        elif name_lower == "tree logs" or name_lower == "log":
            return "Resources - Wood"
        
        # === EQUIPMENT ===
        
        # Equipment - Batteries
        elif "battery" in name_lower:
            return "Equipment - Batteries"
        
        # Equipment - ECUs
        elif "ecu" in name_lower:
            return "Equipment - ECUs"
        
        # Equipment - Filters (Filter Kit)
        elif "filter" in name_lower:
            return "Equipment - Filters"
        
        # Equipment - Hoses (Hydraulic Hose)
        elif "hose" in name_lower:
            return "Equipment - Hoses"
        
        # Equipment - Injectors
        elif "injector" in name_lower:
            return "Equipment - Injectors"
        
        # Equipment - Pumps (Hydraulic Pump)
        elif "pump" in name_lower and "hydraulic" in name_lower:
            return "Equipment - Pumps"
        
        # Equipment - Rams (Hydraulic Ram)
        elif "ram" in name_lower:
            return "Equipment - Rams"
        
        # Equipment - Sensors
        elif "sensor" in name_lower:
            return "Equipment - Sensors"
        
        # Equipment - Turbos
        elif "turbo" in name_lower:
            return "Equipment - Turbos"
        
        # Equipment - Wearparts (Built/Quality Wearplate variants)
        elif "wearplate" in name_lower and any(x in name_lower for x in ["built", "quality", "brand", "oem", "used"]):
            return "Equipment - Wearparts"
        
        # Equipment - Sub Parts (Bearing, Bolts, Cable, Gear, Gearbox, Motor, etc.)
        elif any(x in name_lower for x in ["bearing", "bolt", "cable", "cam axle", "chain", 
                                            "drive axle", "motor", "engine head", "gear", 
                                            "gearbox", "piston rod"]):
            return "Equipment - Sub Parts"
        
        # === BUILDINGS ===
        
        # Buildings - Steel Doors
        elif any(x in name_lower for x in ["massive door", "small door"]):
            return "Buildings - Steel Doors"
        
        # Buildings - Steel Mesh
        elif "steel mesh" in name_lower:
            return "Buildings - Steel Mesh"
        
        # Buildings - Steel (Steel Block, Ceiling, Floor, Wall, etc.)
        elif name_lower.startswith("steel ") and any(x in name_lower for x in 
                ["block", "ceiling", "floor", "railing", "roof", "staircase", "wall", "window"]):
            return "Buildings - Steel"
        
        # Buildings - Concrete (Concrete Block, Floor, Ramp, Roof, Wall)
        elif name_lower.startswith("concrete ") and any(x in name_lower for x in 
                ["block", "chamfer", "cut", "floor", "ramp", "roof", "wall"]):
            return "Buildings - Concrete"
        
        # Buildings - Wood (Wood Block, Floor, Roof, Wall)
        elif name_lower.startswith("wood ") and any(x in name_lower for x in 
                ["block", "floor", "roof", "wall"]):
            return "Buildings - Wood"
        
        # Buildings - Quest buildings
        elif name_lower in ["cell tower", "radio array", "watch tower"]:
            return "Buildings - Quest buildings"
        
        # === RESOURCES ===
        
        # Resources - Ore
        elif "ore" in name_lower:
            return "Resources - Ore"
        
        # Resources - Fluids
        elif any(x in name_lower for x in ["oil", "water"]):
            return "Resources - Fluids"
        
        # Resources - Dirt
        elif any(x in name_lower for x in ["dirt", "paydirt", "tailing"]):
            return "Resources - Dirt"
        
        # Resources - Rock
        elif any(x in name_lower for x in ["rock", "gravel"]):
            return "Resources - Rock"
        
        # Default
        else:
            return "Equipment - Sub Parts"
    
    def _refresh_history(self):
        """Refresh the history table."""
        log = self.parent_tab.production_log
        self.history_table.setRowCount(len(log))
        
        total_value = 0
        
        for row, entry in enumerate(reversed(log)):  # Show newest first
            # Date
            dt = entry["datetime"]
            if isinstance(dt, datetime):
                dt_str = dt.strftime("%Y-%m-%d %H:%M")
            else:
                dt_str = str(dt)
            self.history_table.setItem(row, 0, QTableWidgetItem(dt_str))
            
            # Building
            self.history_table.setItem(row, 1, QTableWidgetItem(entry["building"]))
            
            # Output
            self.history_table.setItem(row, 2, QTableWidgetItem(entry["output"]))
            
            # Qty
            qty_item = QTableWidgetItem(str(entry["output_qty"]))
            qty_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.history_table.setItem(row, 3, qty_item)
            
            # Inputs Used
            inputs_str = ", ".join([f"{qty}× {name}" for name, qty in entry["inputs_used"]])
            self.history_table.setItem(row, 4, QTableWidgetItem(inputs_str))
            
            # Value Created
            value = entry["value_created"]
            total_value += value
            value_item = QTableWidgetItem(f"${value:+,.0f}")
            value_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            if value >= 0:
                value_item.setForeground(QColor("#008800"))
            else:
                value_item.setForeground(QColor("#CC0000"))
            self.history_table.setItem(row, 5, value_item)
        
        # Update summary
        self.total_runs_label.setText(f"Total Runs: {len(log)}")
        self.total_value_label.setText(f"Total Value Created: ${total_value:+,.0f}")
    
    def _delete_selected(self):
        """Delete selected log entries."""
        selected_rows = set()
        for item in self.history_table.selectedItems():
            selected_rows.add(item.row())
        
        if not selected_rows:
            QMessageBox.information(self, "Info", "Please select entries to delete.")
            return
        
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Delete {len(selected_rows)} selected log entries?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Convert to indices in original list (reversed display)
            log_len = len(self.parent_tab.production_log)
            indices_to_remove = [log_len - 1 - row for row in selected_rows]
            
            for idx in sorted(indices_to_remove, reverse=True):
                if 0 <= idx < len(self.parent_tab.production_log):
                    del self.parent_tab.production_log[idx]
            
            self._refresh_history()
            self.parent_tab.data_changed.emit()


class CostAnalysisSubTab(QWidget):
    """Cost Analysis - analyze recipe profitability."""
    
    def __init__(self, parent_tab):
        super().__init__()
        self.parent_tab = parent_tab
        self._setup_ui()
        self._calculate_all()
    
    def _setup_ui(self):
        """Set up the analysis interface."""
        layout = QVBoxLayout(self)
        
        # === Top Performers ===
        top_group = QGroupBox("🏆 Top Performers")
        top_layout = QHBoxLayout(top_group)
        
        self.top_cards = []
        for i, (title, color) in enumerate([
            ("🥇 MOST PROFITABLE", "#D5F5D5"),
            ("🥈 RUNNER UP", "#FFF2CC"),
            ("🥉 THIRD PLACE", "#E8F4FD"),
        ]):
            card = self._create_top_card(title, "-", "$0", color)
            self.top_cards.append(card)
            top_layout.addWidget(card, 1)
        
        layout.addWidget(top_group)
        
        # === Filter ===
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Filter by Building:"))
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All Buildings"] + self.parent_tab.all_workbenches)
        self.filter_combo.currentIndexChanged.connect(self._apply_filter)
        filter_layout.addWidget(self.filter_combo)
        
        filter_layout.addStretch()
        
        self.refresh_btn = QPushButton("🔄 Refresh Analysis")
        self.refresh_btn.clicked.connect(self._calculate_all)
        filter_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(filter_layout)
        
        # === Full Analysis Table ===
        table_group = QGroupBox("📊 Recipe Profitability Analysis")
        table_layout = QVBoxLayout(table_group)
        
        self.analysis_table = QTableWidget()
        self.analysis_table.setColumnCount(7)
        self.analysis_table.setHorizontalHeaderLabels([
            "Recipe", "Building", "Input Cost", "Output Value", "Profit", "Margin %", "Notes"
        ])
        self.analysis_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.analysis_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        self.analysis_table.setColumnWidth(0, 200)
        self.analysis_table.setAlternatingRowColors(True)
        self.analysis_table.setSortingEnabled(True)
        table_layout.addWidget(self.analysis_table)
        
        layout.addWidget(table_group)
    
    def _create_top_card(self, title, recipe, profit, color):
        """Create a top performer card."""
        card = QFrame()
        card.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        card.setStyleSheet(f"background-color: {color}; border-radius: 5px;")
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 8, 10, 8)
        
        title_label = QLabel(title)
        title_label.setObjectName("title_label")
        title_label.setFont(QFont("", 9, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        recipe_label = QLabel(recipe)
        recipe_label.setObjectName("recipe_label")
        recipe_label.setFont(QFont("", 12, QFont.Weight.Bold))
        recipe_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(recipe_label)
        
        profit_label = QLabel(profit)
        profit_label.setObjectName("profit_label")
        profit_label.setStyleSheet("color: #008800;")
        profit_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(profit_label)
        
        return card
    
    def _calculate_all(self):
        """Calculate profitability for all recipes."""
        self.recipe_analysis = []
        
        for recipe in RECIPE_DATA:
            # Calculate input cost
            input_cost = 0
            for input_name, input_qty in recipe["inputs"]:
                price = self.parent_tab.get_item_price(input_name)
                input_cost += price * input_qty
            
            # Calculate output value
            output_price = self.parent_tab.get_item_price(recipe["output"])
            output_qty = recipe.get("output_qty", 1)
            output_value = output_price * output_qty
            
            # Calculate profit and margin
            profit = output_value - input_cost
            margin = (profit / input_cost * 100) if input_cost > 0 else 0
            
            self.recipe_analysis.append({
                "recipe": recipe,
                "output": recipe["output"],
                "building": recipe["workbench"],
                "input_cost": input_cost,
                "output_value": output_value,
                "profit": profit,
                "margin": margin,
                "notes": recipe.get("notes", ""),
            })
        
        # Sort by profit descending
        self.recipe_analysis.sort(key=lambda x: x["profit"], reverse=True)
        
        self._update_top_cards()
        self._apply_filter()
    
    def _update_top_cards(self):
        """Update top performer cards."""
        # Filter to only profitable recipes
        profitable = [r for r in self.recipe_analysis if r["profit"] > 0]
        
        for i, card in enumerate(self.top_cards):
            if i < len(profitable):
                data = profitable[i]
                card.findChild(QLabel, "recipe_label").setText(data["output"])
                card.findChild(QLabel, "profit_label").setText(
                    f"+${data['profit']:.0f}/unit ({data['margin']:+.0f}%)"
                )
            else:
                card.findChild(QLabel, "recipe_label").setText("-")
                card.findChild(QLabel, "profit_label").setText("$0")
    
    def _apply_filter(self):
        """Apply building filter to table."""
        building_filter = self.filter_combo.currentText()
        
        if building_filter == "All Buildings":
            filtered = self.recipe_analysis
        else:
            filtered = [r for r in self.recipe_analysis if r["building"] == building_filter]
        
        self.analysis_table.setSortingEnabled(False)
        self.analysis_table.setRowCount(len(filtered))
        
        for row, data in enumerate(filtered):
            # Recipe name
            self.analysis_table.setItem(row, 0, QTableWidgetItem(data["output"]))
            
            # Building
            self.analysis_table.setItem(row, 1, QTableWidgetItem(data["building"]))
            
            # Input Cost
            cost_item = QTableWidgetItem(f"${data['input_cost']:.0f}")
            cost_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.analysis_table.setItem(row, 2, cost_item)
            
            # Output Value
            value_item = QTableWidgetItem(f"${data['output_value']:.0f}")
            value_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.analysis_table.setItem(row, 3, value_item)
            
            # Profit
            profit_item = QTableWidgetItem(f"${data['profit']:+.0f}")
            profit_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            if data["profit"] >= 0:
                profit_item.setForeground(QColor("#008800"))
                profit_item.setBackground(QColor("#D5F5D5"))
            else:
                profit_item.setForeground(QColor("#CC0000"))
                profit_item.setBackground(QColor("#F8D6D6"))
            self.analysis_table.setItem(row, 4, profit_item)
            
            # Margin
            margin_item = QTableWidgetItem(f"{data['margin']:+.0f}%")
            margin_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            if data["margin"] >= 50:
                margin_item.setForeground(QColor("#008800"))
            elif data["margin"] >= 0:
                margin_item.setForeground(QColor("#CC8800"))
            else:
                margin_item.setForeground(QColor("#CC0000"))
            self.analysis_table.setItem(row, 5, margin_item)
            
            # Notes
            self.analysis_table.setItem(row, 6, QTableWidgetItem(data["notes"]))
        
        self.analysis_table.setSortingEnabled(True)
