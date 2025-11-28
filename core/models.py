"""
Data Models - Define the structure of all data objects
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional
from enum import Enum


class TransactionType(Enum):
    """Types of transactions."""
    PURCHASE = "Purchase"
    SALE = "Sale"
    TRANSFER = "Transfer"


class AccountType(Enum):
    """Account types for transactions."""
    PERSONAL = "Personal"
    COMPANY = "Company"


@dataclass
class Transaction:
    """
    Represents a single ledger transaction.
    
    This is the core data structure for the ledger.
    """
    id: Optional[int] = None  # Database ID (None for new transactions)
    date: date = field(default_factory=date.today)
    type: TransactionType = TransactionType.PURCHASE
    item: str = ""
    category: str = ""
    quantity: float = 1.0
    unit_price: float = 0.0
    discount: float = 0.0
    account: AccountType = AccountType.PERSONAL
    location: str = ""
    notes: str = ""
    
    # Calculated fields (set by the application, not user input)
    subtotal: float = field(default=0.0, repr=False)
    total: float = field(default=0.0, repr=False)
    personal_balance: float = field(default=0.0, repr=False)
    company_balance: float = field(default=0.0, repr=False)
    
    def __post_init__(self):
        """Calculate derived fields after initialization."""
        self.calculate_totals()
    
    def calculate_totals(self):
        """Calculate subtotal and total from quantity, price, and discount."""
        self.subtotal = self.quantity * self.unit_price
        self.total = self.subtotal - self.discount
    
    @property
    def is_income(self) -> bool:
        """Check if this transaction is income (sale)."""
        return self.type == TransactionType.SALE
    
    @property
    def is_expense(self) -> bool:
        """Check if this transaction is an expense (purchase)."""
        return self.type == TransactionType.PURCHASE
    
    @property
    def signed_amount(self) -> float:
        """Return the amount with correct sign (positive for income, negative for expense)."""
        if self.is_income:
            return self.total
        elif self.is_expense:
            return -self.total
        return 0.0  # Transfers don't affect balance directly


@dataclass
class Category:
    """Represents an item category."""
    id: Optional[int] = None
    name: str = ""
    parent: str = ""  # Parent category (e.g., "Vehicles" for "Vehicles - Rock Trucks")
    
    @property
    def full_name(self) -> str:
        """Return full category name."""
        if self.parent:
            return f"{self.parent} - {self.name}"
        return self.name


@dataclass
class Item:
    """
    Represents an item from the combined price tables + item rules.
    
    IMPORTANT: (name, category) together form the unique identifier,
    since items like "Concrete Block" exist in multiple categories
    (Concrete, Polished Concrete, Rough Concrete).
    
    PRICES:
    - buy_price: Base price (no discounts)
    - current_buy_price: Actual price after skill tree discounts (Vendor Negotiation, Investment)
    - sell_price: What you get when selling
    
    The art_nr (Article Number) matches the game's internal ID (for save file auditing).
    """
    id: Optional[int] = None
    art_nr: int = 0  # Game's internal item code (e.g., 400187 for Oil Pump)
    name: str = ""
    category: str = ""
    buy_price: float = 0.0           # Base price (no discounts)
    current_buy_price: float = 0.0   # Price after skill tree discounts
    sell_price: float = 0.0
    can_purchase: bool = True  # From Item Rules
    can_sell: bool = True      # From Item Rules
    notes: str = ""
    
    def __post_init__(self):
        """Set current_buy_price to buy_price if not specified."""
        if self.current_buy_price == 0 and self.buy_price > 0:
            self.current_buy_price = self.buy_price
    
    @property
    def display_name(self) -> str:
        """Full display name including category for duplicates."""
        return f"{self.name} ({self.category})" if self.category else self.name
    
    @property
    def discount_amount(self) -> float:
        """How much discount is applied."""
        return self.buy_price - self.current_buy_price
    
    @property
    def discount_percent(self) -> float:
        """Discount as a percentage."""
        if self.buy_price == 0:
            return 0.0
        return (self.discount_amount / self.buy_price) * 100
    
    @property
    def has_discount(self) -> bool:
        """Whether a discount is currently applied."""
        return self.current_buy_price < self.buy_price
    
    @property
    def profit_margin(self) -> float:
        """Calculate profit margin (sell - current buy price)."""
        if not self.can_purchase or not self.can_sell:
            return 0.0
        return self.sell_price - self.current_buy_price
    
    @property
    def roi_percent(self) -> float:
        """Calculate ROI percentage based on current buy price."""
        if self.current_buy_price == 0 or not self.can_purchase:
            return 0.0
        return (self.profit_margin / self.current_buy_price) * 100
    
    @property
    def is_craftable(self) -> bool:
        """Item can only be obtained through crafting (can't purchase)."""
        return not self.can_purchase and self.can_sell
    
    @property
    def is_manufacturing_only(self) -> bool:
        """Item can only be used for manufacturing (can't sell)."""
        return not self.can_sell


@dataclass
class Location:
    """Represents a game location."""
    id: Optional[int] = None
    name: str = ""
    map_name: str = ""
    location_type: str = ""  # Base, Mine Site, Stockpile, etc.


@dataclass
class GameSettings:
    """
    Game configuration and state.
    
    Tracks current game date, difficulty, balances, and skill tree discounts.
    """
    id: Optional[int] = None
    game_start_date: date = field(default_factory=date.today)
    current_game_date: date = field(default_factory=date.today)
    starting_capital: float = 100000.0
    difficulty: str = "Easy"
    personal_balance: float = 0.0
    company_balance: float = 0.0
    
    # Challenge mode settings
    personal_split: float = 0.1  # 10% to personal
    company_split: float = 0.9  # 90% to company
    oil_quota: int = 10000
    oil_sold: int = 0
    
    # Skill tree discounts
    vendor_negotiation_level: int = 0      # Skill level (affects all items)
    vendor_negotiation_discount: float = 0.0  # Current % discount
    investment_forecasting_level: int = 0  # Skill level (affects vehicles)
    investment_forecasting_discount: float = 0.0  # Current % discount
    
    @property
    def days_played(self) -> int:
        """Calculate days played."""
        delta = self.current_game_date - self.game_start_date
        return delta.days + 1
    
    @property
    def total_balance(self) -> float:
        """Total balance across both accounts."""
        return self.personal_balance + self.company_balance
    
    @property
    def oil_remaining(self) -> int:
        """Oil quota remaining."""
        return max(0, self.oil_quota - self.oil_sold)
    
    @property
    def oil_percent_used(self) -> float:
        """Percentage of oil quota used."""
        if self.oil_quota == 0:
            return 0.0
        return (self.oil_sold / self.oil_quota) * 100
    
    @property
    def max_vehicle_discount(self) -> float:
        """Combined discount for vehicles (VN + IF)."""
        return self.vendor_negotiation_discount + self.investment_forecasting_discount
    
    def get_item_discount(self, is_vehicle: bool = False) -> float:
        """Get the applicable discount for an item type."""
        if is_vehicle:
            return self.max_vehicle_discount
        return self.vendor_negotiation_discount


@dataclass 
class Vehicle:
    """
    Represents a vehicle from the game.
    
    Used for equipment planning and tracking.
    """
    id: Optional[int] = None
    name: str = ""
    category: str = ""
    description: str = ""
    weight_lbs: float = 0.0
    capacity_yd3: float = 0.0
    power_kw: float = 0.0
    fuel_use_lph: float = 0.0  # Liters per hour
    fuel_capacity_l: float = 0.0
    purchase_price: float = 0.0
    
    @property
    def weight_kg(self) -> float:
        """Convert weight to kg."""
        return self.weight_lbs * 0.453592
    
    @property
    def capacity_m3(self) -> float:
        """Convert capacity to cubic meters."""
        return self.capacity_yd3 * 0.764555


@dataclass
class FactoryEquipment:
    """
    Represents factory equipment (conveyors, power, pipelines).
    
    Used for factory planning and power calculations.
    """
    id: Optional[int] = None
    art_nr: int = 0
    name: str = ""
    category: str = ""  # Conveyor, Power, Pipeline
    subcategory: str = ""  # Straight, Up, Down, Turn, etc.
    length_m: float = 0.0
    height_m: float = 0.0
    conveyor_speed: float = 0.0  # M/s
    power_consumption_kw: float = 0.0
    power_generated_kw: float = 0.0
    max_capacity_kw: float = 0.0  # For pylons
    max_connections: int = 1
    power_efficiency: str = "1x"
    fuel_type: str = ""  # Coal, Generator Fuel, None
    price: float = 0.0
    notes: str = ""
    
    @property
    def is_power_consumer(self) -> bool:
        """Check if this equipment consumes power."""
        return self.power_consumption_kw > 0
    
    @property
    def is_power_generator(self) -> bool:
        """Check if this equipment generates power."""
        return self.power_generated_kw > 0
    
    @property
    def is_power_distributor(self) -> bool:
        """Check if this equipment distributes power (pylons)."""
        return self.max_capacity_kw > 0
    
    @property
    def price_per_kw(self) -> float:
        """Calculate cost per kW for generators."""
        if self.power_generated_kw > 0:
            return self.price / self.power_generated_kw
        return 0.0
    
    @property
    def price_per_kw_capacity(self) -> float:
        """Calculate cost per kW capacity for pylons."""
        if self.max_capacity_kw > 0:
            return self.price / self.max_capacity_kw
        return 0.0
    
    @property
    def dimensions(self) -> str:
        """Format dimensions as string."""
        if self.length_m > 0 and self.height_m > 0:
            return f"{self.length_m:.0f}m × {self.height_m:.0f}m"
        elif self.length_m > 0:
            return f"{self.length_m:.0f}m"
        return "-"
