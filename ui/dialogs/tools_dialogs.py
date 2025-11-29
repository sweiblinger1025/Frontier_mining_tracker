"""
Tools Dialogs - Utility dialogs for the Tools menu

Includes:
- Fuel Calculator
- Discount Calculator
- Split Calculator
- Challenge Status
"""

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QGroupBox,
    QLabel,
    QPushButton,
    QDoubleSpinBox,
    QSpinBox,
    QLineEdit,
    QComboBox,
    QProgressBar,
    QFrame,
    QMessageBox,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class FuelCalculatorDialog(QDialog):
    """
    Fuel Calculator & Verification Tool
    
    Two methods to calculate fuel consumption:
    1. Money Method - Based on balance change and fuel price
    2. Time Method - Based on session duration and vehicle fuel use rate
    
    Compares both methods to verify accuracy.
    """
    
    def __init__(self, fuel_price: float = 0.32, parent=None):
        super().__init__(parent)
        self.fuel_price = fuel_price
        self.setWindowTitle("⛽ Fuel Calculator & Verification")
        self.setMinimumWidth(450)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Money Method
        money_group = QGroupBox("💰 Money Method")
        money_layout = QFormLayout(money_group)
        
        self.balance_before_spin = QDoubleSpinBox()
        self.balance_before_spin.setRange(0, 999999999)
        self.balance_before_spin.setDecimals(2)
        self.balance_before_spin.setPrefix("$")
        self.balance_before_spin.valueChanged.connect(self._calculate)
        money_layout.addRow("Balance Before:", self.balance_before_spin)
        
        self.balance_after_spin = QDoubleSpinBox()
        self.balance_after_spin.setRange(0, 999999999)
        self.balance_after_spin.setDecimals(2)
        self.balance_after_spin.setPrefix("$")
        self.balance_after_spin.valueChanged.connect(self._calculate)
        money_layout.addRow("Balance After:", self.balance_after_spin)
        
        self.money_spent_label = QLabel("$0.00")
        self.money_spent_label.setStyleSheet("font-weight: bold;")
        money_layout.addRow("Money Spent:", self.money_spent_label)
        
        self.fuel_price_spin = QDoubleSpinBox()
        self.fuel_price_spin.setRange(0.01, 100)
        self.fuel_price_spin.setDecimals(2)
        self.fuel_price_spin.setValue(self.fuel_price)
        self.fuel_price_spin.setPrefix("$")
        self.fuel_price_spin.setSuffix(" /L")
        self.fuel_price_spin.valueChanged.connect(self._calculate)
        money_layout.addRow("Fuel Price:", self.fuel_price_spin)
        
        self.fuel_from_money_label = QLabel("0 L")
        self.fuel_from_money_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #1976d2;")
        money_layout.addRow("Fuel from Money:", self.fuel_from_money_label)
        
        layout.addWidget(money_group)
        
        # Time Method
        time_group = QGroupBox("⏱️ Time Method")
        time_layout = QFormLayout(time_group)
        
        self.session_duration_spin = QDoubleSpinBox()
        self.session_duration_spin.setRange(0, 9999)
        self.session_duration_spin.setDecimals(1)
        self.session_duration_spin.setSuffix(" min")
        self.session_duration_spin.valueChanged.connect(self._calculate)
        time_layout.addRow("Session Duration:", self.session_duration_spin)
        
        self.vehicle_fuel_use_spin = QDoubleSpinBox()
        self.vehicle_fuel_use_spin.setRange(0, 1000)
        self.vehicle_fuel_use_spin.setDecimals(2)
        self.vehicle_fuel_use_spin.setSuffix(" L/min")
        self.vehicle_fuel_use_spin.valueChanged.connect(self._calculate)
        time_layout.addRow("Vehicle Fuel Use:", self.vehicle_fuel_use_spin)
        
        self.fuel_from_time_label = QLabel("0 L")
        self.fuel_from_time_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #1976d2;")
        time_layout.addRow("Fuel from Time:", self.fuel_from_time_label)
        
        layout.addWidget(time_group)
        
        # Verification
        verify_group = QGroupBox("📊 Verification")
        verify_layout = QFormLayout(verify_group)
        
        self.verify_money_label = QLabel("0 L")
        verify_layout.addRow("Fuel (Money Method):", self.verify_money_label)
        
        self.verify_time_label = QLabel("0 L")
        verify_layout.addRow("Fuel (Time Method):", self.verify_time_label)
        
        self.difference_label = QLabel("0 L")
        verify_layout.addRow("Difference:", self.difference_label)
        
        self.match_status_label = QLabel("✅ PERFECT MATCH")
        self.match_status_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #2e7d32;")
        verify_layout.addRow("Match Status:", self.match_status_label)
        
        layout.addWidget(verify_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        clear_btn = QPushButton("Clear All")
        clear_btn.clicked.connect(self._clear_all)
        btn_layout.addWidget(clear_btn)
        
        btn_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
    
    def _calculate(self):
        """Calculate fuel from both methods and compare."""
        # Money method
        balance_before = self.balance_before_spin.value()
        balance_after = self.balance_after_spin.value()
        fuel_price = self.fuel_price_spin.value()
        
        money_spent = balance_before - balance_after
        self.money_spent_label.setText(f"${money_spent:,.2f}")
        
        if fuel_price > 0:
            fuel_from_money = money_spent / fuel_price
        else:
            fuel_from_money = 0
        
        self.fuel_from_money_label.setText(f"{fuel_from_money:,.1f} L")
        
        # Time method
        session_duration = self.session_duration_spin.value()
        vehicle_fuel_use = self.vehicle_fuel_use_spin.value()
        
        fuel_from_time = session_duration * vehicle_fuel_use
        self.fuel_from_time_label.setText(f"{fuel_from_time:,.1f} L")
        
        # Verification
        self.verify_money_label.setText(f"{fuel_from_money:,.1f} L")
        self.verify_time_label.setText(f"{fuel_from_time:,.1f} L")
        
        difference = abs(fuel_from_money - fuel_from_time)
        self.difference_label.setText(f"{difference:,.1f} L")
        
        # Match status (allow 1% tolerance)
        if fuel_from_money == 0 and fuel_from_time == 0:
            self.match_status_label.setText("✅ PERFECT MATCH")
            self.match_status_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #2e7d32;")
        elif fuel_from_money > 0 and difference / fuel_from_money < 0.01:
            self.match_status_label.setText("✅ PERFECT MATCH")
            self.match_status_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #2e7d32;")
        elif fuel_from_money > 0 and difference / fuel_from_money < 0.05:
            self.match_status_label.setText("⚠️ CLOSE MATCH")
            self.match_status_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #f57c00;")
        else:
            self.match_status_label.setText("❌ MISMATCH")
            self.match_status_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #c62828;")
    
    def _clear_all(self):
        """Clear all inputs."""
        self.balance_before_spin.setValue(0)
        self.balance_after_spin.setValue(0)
        self.session_duration_spin.setValue(0)
        self.vehicle_fuel_use_spin.setValue(0)


class DiscountCalculatorDialog(QDialog):
    """
    Discount Calculator
    
    Calculate item prices with VN (Vendor Negotiation) and IF (Investment Forecasting) discounts.
    """
    
    def __init__(self, vn_level: int = 0, if_level: int = 0, parent=None):
        super().__init__(parent)
        self.setWindowTitle("💰 Discount Calculator")
        self.setMinimumWidth(400)
        self.vn_level = vn_level
        self.if_level = if_level
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Skill Levels
        skills_group = QGroupBox("📊 Skill Levels")
        skills_layout = QFormLayout(skills_group)
        
        self.vn_spin = QSpinBox()
        self.vn_spin.setRange(0, 10)
        self.vn_spin.setValue(self.vn_level)
        self.vn_spin.valueChanged.connect(self._calculate)
        skills_layout.addRow("Vendor Negotiation:", self.vn_spin)
        
        self.vn_discount_label = QLabel(f"{self.vn_level * 0.5}%")
        skills_layout.addRow("VN Discount:", self.vn_discount_label)
        
        self.if_spin = QSpinBox()
        self.if_spin.setRange(0, 10)
        self.if_spin.setValue(self.if_level)
        self.if_spin.valueChanged.connect(self._calculate)
        skills_layout.addRow("Investment Forecasting:", self.if_spin)
        
        self.if_discount_label = QLabel(f"{self.if_level * 0.5}%")
        skills_layout.addRow("IF Discount (Vehicles):", self.if_discount_label)
        
        layout.addWidget(skills_group)
        
        # Price Input
        price_group = QGroupBox("💵 Price Calculation")
        price_layout = QFormLayout(price_group)
        
        self.base_price_spin = QDoubleSpinBox()
        self.base_price_spin.setRange(0, 999999999)
        self.base_price_spin.setDecimals(2)
        self.base_price_spin.setPrefix("$")
        self.base_price_spin.valueChanged.connect(self._calculate)
        price_layout.addRow("Base Price:", self.base_price_spin)
        
        self.is_vehicle_combo = QComboBox()
        self.is_vehicle_combo.addItems(["No (VN only)", "Yes (VN + IF)"])
        self.is_vehicle_combo.currentIndexChanged.connect(self._calculate)
        price_layout.addRow("Is Vehicle?", self.is_vehicle_combo)
        
        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        price_layout.addRow(sep)
        
        self.discount_rate_label = QLabel("0%")
        self.discount_rate_label.setStyleSheet("font-weight: bold;")
        price_layout.addRow("Total Discount:", self.discount_rate_label)
        
        self.discount_amount_label = QLabel("$0.00")
        self.discount_amount_label.setStyleSheet("font-weight: bold;")
        price_layout.addRow("You Save:", self.discount_amount_label)
        
        self.final_price_label = QLabel("$0.00")
        self.final_price_label.setStyleSheet("font-weight: bold; font-size: 18px; color: #2e7d32;")
        price_layout.addRow("Final Price:", self.final_price_label)
        
        layout.addWidget(price_group)
        
        # Quick Examples
        examples_group = QGroupBox("🔢 Quick Examples")
        examples_layout = QVBoxLayout(examples_group)
        
        self.examples_label = QLabel()
        self.examples_label.setWordWrap(True)
        examples_layout.addWidget(self.examples_label)
        
        layout.addWidget(examples_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
        
        # Initial calculation
        self._calculate()
    
    def _calculate(self):
        """Calculate discounted price."""
        vn_level = self.vn_spin.value()
        if_level = self.if_spin.value()
        base_price = self.base_price_spin.value()
        is_vehicle = self.is_vehicle_combo.currentIndex() == 1
        
        vn_discount = vn_level * 0.5
        if_discount = if_level * 0.5
        
        self.vn_discount_label.setText(f"{vn_discount}%")
        self.if_discount_label.setText(f"{if_discount}%")
        
        if is_vehicle:
            total_discount = vn_discount + if_discount
        else:
            total_discount = vn_discount
        
        self.discount_rate_label.setText(f"{total_discount}%")
        
        discount_amount = base_price * (total_discount / 100)
        final_price = base_price - discount_amount
        
        self.discount_amount_label.setText(f"${discount_amount:,.2f}")
        self.final_price_label.setText(f"${final_price:,.2f}")
        
        # Update examples
        examples = []
        example_prices = [1000, 10000, 50000, 100000]
        for price in example_prices:
            discounted = price * (1 - total_discount / 100)
            examples.append(f"${price:,} → ${discounted:,.0f}")
        
        self.examples_label.setText(" | ".join(examples))
    
    def set_skill_levels(self, vn_level: int, if_level: int):
        """Set skill levels from settings."""
        self.vn_spin.setValue(vn_level)
        self.if_spin.setValue(if_level)


class SplitCalculatorDialog(QDialog):
    """
    Split Calculator
    
    Calculate how revenue splits between Personal and Company accounts.
    """
    
    def __init__(self, personal_pct: float = 0.10, company_pct: float = 0.90, parent=None):
        super().__init__(parent)
        self.setWindowTitle("💵 Split Calculator")
        self.setMinimumWidth(400)
        self.personal_pct = personal_pct
        self.company_pct = company_pct
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Split Configuration
        config_group = QGroupBox("⚙️ Split Configuration")
        config_layout = QFormLayout(config_group)
        
        split_widget = QHBoxLayout()
        
        self.personal_spin = QSpinBox()
        self.personal_spin.setRange(0, 100)
        self.personal_spin.setValue(int(self.personal_pct * 100))
        self.personal_spin.setSuffix("%")
        self.personal_spin.valueChanged.connect(self._on_personal_changed)
        split_widget.addWidget(QLabel("Personal:"))
        split_widget.addWidget(self.personal_spin)
        
        self.company_spin = QSpinBox()
        self.company_spin.setRange(0, 100)
        self.company_spin.setValue(int(self.company_pct * 100))
        self.company_spin.setSuffix("%")
        self.company_spin.setEnabled(False)
        split_widget.addWidget(QLabel("Company:"))
        split_widget.addWidget(self.company_spin)
        
        config_layout.addRow("Revenue Split:", split_widget)
        
        layout.addWidget(config_group)
        
        # Amount Input
        calc_group = QGroupBox("💰 Calculate Split")
        calc_layout = QFormLayout(calc_group)
        
        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setRange(0, 999999999)
        self.amount_spin.setDecimals(2)
        self.amount_spin.setPrefix("$")
        self.amount_spin.valueChanged.connect(self._calculate)
        calc_layout.addRow("Gross Revenue:", self.amount_spin)
        
        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        calc_layout.addRow(sep)
        
        self.personal_amount_label = QLabel("$0.00")
        self.personal_amount_label.setStyleSheet("font-weight: bold; font-size: 16px; color: #1976d2;")
        calc_layout.addRow("→ Personal Account:", self.personal_amount_label)
        
        self.company_amount_label = QLabel("$0.00")
        self.company_amount_label.setStyleSheet("font-weight: bold; font-size: 16px; color: #2e7d32;")
        calc_layout.addRow("→ Company Account:", self.company_amount_label)
        
        layout.addWidget(calc_group)
        
        # Quick Reference Table
        ref_group = QGroupBox("📋 Quick Reference")
        ref_layout = QVBoxLayout(ref_group)
        
        self.ref_label = QLabel()
        self.ref_label.setStyleSheet("font-family: monospace;")
        ref_layout.addWidget(self.ref_label)
        
        layout.addWidget(ref_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
        
        # Initial calculation
        self._calculate()
    
    def _on_personal_changed(self):
        """Update company when personal changes."""
        personal = self.personal_spin.value()
        self.company_spin.setValue(100 - personal)
        self._calculate()
    
    def _calculate(self):
        """Calculate split amounts."""
        amount = self.amount_spin.value()
        personal_pct = self.personal_spin.value() / 100
        company_pct = self.company_spin.value() / 100
        
        personal_amount = amount * personal_pct
        company_amount = amount * company_pct
        
        self.personal_amount_label.setText(f"${personal_amount:,.2f}")
        self.company_amount_label.setText(f"${company_amount:,.2f}")
        
        # Update quick reference
        ref_lines = []
        ref_amounts = [1000, 5000, 10000, 50000, 100000, 500000]
        ref_lines.append(f"{'Gross':>12} {'Personal':>12} {'Company':>12}")
        ref_lines.append("-" * 40)
        for amt in ref_amounts:
            p = amt * personal_pct
            c = amt * company_pct
            ref_lines.append(f"${amt:>10,} ${p:>10,.0f} ${c:>10,.0f}")
        
        self.ref_label.setText("\n".join(ref_lines))
    
    def set_split(self, personal_pct: float, company_pct: float):
        """Set split percentages from settings."""
        self.personal_spin.setValue(int(personal_pct * 100))
        self.company_spin.setValue(int(company_pct * 100))


class ChallengeStatusDialog(QDialog):
    """
    Challenge Status
    
    Quick view of challenge progress including oil cap, daily limit, and thresholds.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🎯 Challenge Status")
        self.setMinimumWidth(450)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Difficulty Info
        diff_group = QGroupBox("🎮 Current Challenge")
        diff_layout = QFormLayout(diff_group)
        
        self.difficulty_label = QLabel("Easy")
        self.difficulty_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        diff_layout.addRow("Difficulty:", self.difficulty_label)
        
        self.description_label = QLabel("Generous seed funding. 10% personal salary, oil cap 10,000 barrels.")
        self.description_label.setWordWrap(True)
        self.description_label.setStyleSheet("color: #666; font-style: italic;")
        diff_layout.addRow("", self.description_label)
        
        layout.addWidget(diff_group)
        
        # Oil Cap Status
        oil_group = QGroupBox("🛢️ Oil Lifetime Cap")
        oil_layout = QVBoxLayout(oil_group)
        
        oil_stats = QHBoxLayout()
        
        self.oil_sold_label = QLabel("0")
        self.oil_sold_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        stats_widget1 = QVBoxLayout()
        stats_widget1.addWidget(QLabel("Sold"))
        stats_widget1.addWidget(self.oil_sold_label)
        oil_stats.addLayout(stats_widget1)
        
        oil_stats.addWidget(QLabel("/"))
        
        self.oil_cap_label = QLabel("10,000")
        self.oil_cap_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        stats_widget2 = QVBoxLayout()
        stats_widget2.addWidget(QLabel("Cap"))
        stats_widget2.addWidget(self.oil_cap_label)
        oil_stats.addLayout(stats_widget2)
        
        oil_stats.addWidget(QLabel("="))
        
        self.oil_remaining_label = QLabel("10,000")
        self.oil_remaining_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #2e7d32;")
        stats_widget3 = QVBoxLayout()
        stats_widget3.addWidget(QLabel("Remaining"))
        stats_widget3.addWidget(self.oil_remaining_label)
        oil_stats.addLayout(stats_widget3)
        
        oil_stats.addStretch()
        oil_layout.addLayout(oil_stats)
        
        self.oil_progress = QProgressBar()
        self.oil_progress.setRange(0, 100)
        self.oil_progress.setValue(0)
        self.oil_progress.setFormat("%p% used")
        oil_layout.addWidget(self.oil_progress)
        
        self.oil_status_label = QLabel("✅ Oil cap in good standing")
        self.oil_status_label.setStyleSheet("font-weight: bold; color: #2e7d32;")
        oil_layout.addWidget(self.oil_status_label)
        
        layout.addWidget(oil_group)
        
        # Daily Limit Status
        daily_group = QGroupBox("📅 Daily Spending Limit")
        daily_layout = QFormLayout(daily_group)
        
        self.daily_enabled_label = QLabel("Disabled")
        daily_layout.addRow("Status:", self.daily_enabled_label)
        
        self.daily_limit_label = QLabel("N/A")
        daily_layout.addRow("Limit:", self.daily_limit_label)
        
        self.daily_spent_label = QLabel("$0")
        daily_layout.addRow("Spent Today:", self.daily_spent_label)
        
        self.daily_remaining_label = QLabel("N/A")
        self.daily_remaining_label.setStyleSheet("font-weight: bold;")
        daily_layout.addRow("Remaining:", self.daily_remaining_label)
        
        layout.addWidget(daily_group)
        
        # Bar Threshold
        bar_group = QGroupBox("📊 Bar Threshold")
        bar_layout = QFormLayout(bar_group)
        
        self.bar_threshold_label = QLabel("5,000")
        bar_layout.addRow("Minimum Reserve:", self.bar_threshold_label)
        
        self.current_balance_label = QLabel("$0")
        bar_layout.addRow("Current Balance:", self.current_balance_label)
        
        self.bar_status_label = QLabel("⚠️ Below threshold")
        bar_layout.addRow("Status:", self.bar_status_label)
        
        layout.addWidget(bar_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self._refresh)
        btn_layout.addWidget(refresh_btn)
        
        btn_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
    
    def _refresh(self):
        """Refresh status from current data."""
        # This will be connected to actual data
        pass
    
    def update_status(self, 
                      difficulty: str = "Easy",
                      description: str = "",
                      oil_sold: int = 0,
                      oil_cap: int = 10000,
                      oil_enabled: bool = True,
                      daily_enabled: bool = False,
                      daily_limit: int = 0,
                      daily_spent: float = 0,
                      bar_threshold: int = 5000,
                      current_balance: float = 0):
        """Update all status displays."""
        
        # Difficulty
        self.difficulty_label.setText(difficulty)
        self.description_label.setText(description)
        
        # Oil Cap
        if oil_enabled:
            oil_remaining = oil_cap - oil_sold
            oil_pct = (oil_sold / oil_cap * 100) if oil_cap > 0 else 0
            
            self.oil_sold_label.setText(f"{oil_sold:,}")
            self.oil_cap_label.setText(f"{oil_cap:,}")
            self.oil_remaining_label.setText(f"{oil_remaining:,}")
            self.oil_progress.setValue(int(oil_pct))
            
            if oil_pct < 75:
                self.oil_status_label.setText("✅ Oil cap in good standing")
                self.oil_status_label.setStyleSheet("font-weight: bold; color: #2e7d32;")
                self.oil_remaining_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #2e7d32;")
            elif oil_pct < 90:
                self.oil_status_label.setText("⚠️ Approaching oil cap limit")
                self.oil_status_label.setStyleSheet("font-weight: bold; color: #f57c00;")
                self.oil_remaining_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #f57c00;")
            else:
                self.oil_status_label.setText("🛑 Near oil cap limit!")
                self.oil_status_label.setStyleSheet("font-weight: bold; color: #c62828;")
                self.oil_remaining_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #c62828;")
        else:
            self.oil_status_label.setText("Oil cap disabled")
            self.oil_status_label.setStyleSheet("font-weight: bold; color: #666;")
        
        # Daily Limit
        if daily_enabled:
            self.daily_enabled_label.setText("✅ Enabled")
            self.daily_enabled_label.setStyleSheet("color: #2e7d32;")
            self.daily_limit_label.setText(f"${daily_limit:,}")
            self.daily_spent_label.setText(f"${daily_spent:,.2f}")
            daily_remaining = daily_limit - daily_spent
            self.daily_remaining_label.setText(f"${daily_remaining:,.2f}")
            
            if daily_remaining < 0:
                self.daily_remaining_label.setStyleSheet("font-weight: bold; color: #c62828;")
            elif daily_remaining < daily_limit * 0.2:
                self.daily_remaining_label.setStyleSheet("font-weight: bold; color: #f57c00;")
            else:
                self.daily_remaining_label.setStyleSheet("font-weight: bold; color: #2e7d32;")
        else:
            self.daily_enabled_label.setText("Disabled")
            self.daily_enabled_label.setStyleSheet("color: #666;")
            self.daily_limit_label.setText("N/A")
            self.daily_spent_label.setText("N/A")
            self.daily_remaining_label.setText("N/A")
            self.daily_remaining_label.setStyleSheet("font-weight: bold; color: #666;")
        
        # Bar Threshold
        self.bar_threshold_label.setText(f"{bar_threshold:,}")
        self.current_balance_label.setText(f"${current_balance:,.2f}")
        
        if current_balance >= bar_threshold:
            self.bar_status_label.setText("✅ Above threshold")
            self.bar_status_label.setStyleSheet("font-weight: bold; color: #2e7d32;")
        else:
            self.bar_status_label.setText("⚠️ Below threshold")
            self.bar_status_label.setStyleSheet("font-weight: bold; color: #c62828;")


class AdvanceGameDayDialog(QDialog):
    """
    Advance Game Day
    
    Increment the game day and optionally log a daily summary.
    """
    
    def __init__(self, current_date: str = "04/23/2021", days_played: int = 1, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📅 Advance Game Day")
        self.setMinimumWidth(350)
        self.current_date = current_date
        self.days_played = days_played
        self.advanced = False
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Current Status
        status_group = QGroupBox("📊 Current Status")
        status_layout = QFormLayout(status_group)
        
        self.current_date_label = QLabel(self.current_date)
        self.current_date_label.setStyleSheet("font-weight: bold;")
        status_layout.addRow("Current Game Date:", self.current_date_label)
        
        self.days_played_label = QLabel(str(self.days_played))
        self.days_played_label.setStyleSheet("font-weight: bold;")
        status_layout.addRow("Days Played:", self.days_played_label)
        
        layout.addWidget(status_group)
        
        # Advance Options
        advance_group = QGroupBox("➡️ Advance Day")
        advance_layout = QFormLayout(advance_group)
        
        self.days_spin = QSpinBox()
        self.days_spin.setRange(1, 30)
        self.days_spin.setValue(1)
        self.days_spin.setSuffix(" day(s)")
        advance_layout.addRow("Advance by:", self.days_spin)
        
        self.new_date_label = QLabel("04/24/2021")
        self.new_date_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #1976d2;")
        advance_layout.addRow("New Date:", self.new_date_label)
        
        layout.addWidget(advance_group)
        
        # Summary note
        note_label = QLabel("ℹ️ This will update the game date in Settings → Game Info")
        note_label.setStyleSheet("color: #666; font-style: italic;")
        note_label.setWordWrap(True)
        layout.addWidget(note_label)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        btn_layout.addStretch()
        
        advance_btn = QPushButton("📅 Advance Day")
        advance_btn.setStyleSheet("font-weight: bold;")
        advance_btn.clicked.connect(self._advance)
        btn_layout.addWidget(advance_btn)
        
        layout.addLayout(btn_layout)
    
    def _advance(self):
        """Advance the game day."""
        self.advanced = True
        self.accept()
    
    def get_days_to_advance(self) -> int:
        """Get the number of days to advance."""
        return self.days_spin.value() if self.advanced else 0
    
    def set_current_date(self, date_str: str, days_played: int):
        """Set the current date display."""
        self.current_date_label.setText(date_str)
        self.days_played_label.setText(str(days_played))
