"""
Database Module - SQLite database operations

Handles all database creation, connections, and queries.
"""

import sqlite3
from pathlib import Path
from datetime import date, datetime
from typing import Optional
from contextlib import contextmanager

from config.settings import DATABASE_PATH, ensure_directories
from core.models import (
    Transaction, 
    TransactionType, 
    AccountType,
    Category,
    Item,
    Location,
    GameSettings,
)


class Database:
    """SQLite database manager for the application."""
    
    def __init__(self, db_path: Optional[Path] = None):
        """Initialize database connection."""
        self.db_path = db_path or DATABASE_PATH
        ensure_directories()
        self._init_database()
    
    @contextmanager
    def _get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def _init_database(self):
        """Create database tables if they don't exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Transactions table (the ledger)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    type TEXT NOT NULL,
                    item TEXT NOT NULL,
                    category TEXT,
                    quantity REAL DEFAULT 1,
                    unit_price REAL DEFAULT 0,
                    subtotal REAL DEFAULT 0,
                    discount REAL DEFAULT 0,
                    total REAL DEFAULT 0,
                    personal_income REAL DEFAULT 0,
                    company_income REAL DEFAULT 0,
                    personal_expense REAL DEFAULT 0,
                    company_expense REAL DEFAULT 0,
                    account TEXT DEFAULT 'Personal',
                    location TEXT,
                    personal_balance REAL DEFAULT 0,
                    company_balance REAL DEFAULT 0,
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Categories table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    parent TEXT
                )
            """)
            
            # Items table (price list + item rules combined)
            # UNIQUE on (name, category) since items like "Concrete Block" 
            # exist in multiple categories
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    art_nr INTEGER,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    buy_price REAL DEFAULT 0,
                    current_buy_price REAL DEFAULT 0,
                    sell_price REAL DEFAULT 0,
                    can_purchase INTEGER DEFAULT 1,
                    can_sell INTEGER DEFAULT 1,
                    notes TEXT,
                    UNIQUE(name, category)
                )
            """)
            
            # Locations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS locations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    map_name TEXT,
                    location_type TEXT
                )
            """)
            
            # Game settings table (single row)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS game_settings (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    game_start_date TEXT,
                    current_game_date TEXT,
                    starting_capital REAL DEFAULT 100000,
                    difficulty TEXT DEFAULT 'Easy',
                    personal_balance REAL DEFAULT 0,
                    company_balance REAL DEFAULT 0,
                    personal_split REAL DEFAULT 0.1,
                    company_split REAL DEFAULT 0.9,
                    oil_quota INTEGER DEFAULT 10000,
                    oil_sold INTEGER DEFAULT 0,
                    vendor_negotiation_level INTEGER DEFAULT 0,
                    vendor_negotiation_discount REAL DEFAULT 0,
                    investment_forecasting_level INTEGER DEFAULT 0,
                    investment_forecasting_discount REAL DEFAULT 0
                )
            """)
            
            # Create indexes for common queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_transactions_date 
                ON transactions(date)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_transactions_category 
                ON transactions(category)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_items_art_nr 
                ON items(art_nr)
            """)
    
    # ==================== TRANSACTION OPERATIONS ====================
    
    def add_transaction(self, txn: Transaction) -> int:
        """Add a new transaction to the ledger. Returns the new ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO transactions 
                (date, type, item, category, quantity, unit_price, 
                 subtotal, discount, total, account, location,
                 personal_balance, company_balance, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                txn.date.isoformat(),
                txn.type.value,
                txn.item,
                txn.category,
                txn.quantity,
                txn.unit_price,
                txn.subtotal,
                txn.discount,
                txn.total,
                txn.account.value,
                txn.location,
                txn.personal_balance,
                txn.company_balance,
                txn.notes,
            ))
            return cursor.lastrowid
    
    def update_transaction(self, txn: Transaction) -> bool:
        """Update an existing transaction. Returns True if successful."""
        if txn.id is None:
            return False
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE transactions SET
                    date = ?,
                    type = ?,
                    item = ?,
                    category = ?,
                    quantity = ?,
                    unit_price = ?,
                    subtotal = ?,
                    discount = ?,
                    total = ?,
                    account = ?,
                    location = ?,
                    personal_balance = ?,
                    company_balance = ?,
                    notes = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                txn.date.isoformat(),
                txn.type.value,
                txn.item,
                txn.category,
                txn.quantity,
                txn.unit_price,
                txn.subtotal,
                txn.discount,
                txn.total,
                txn.account.value,
                txn.location,
                txn.personal_balance,
                txn.company_balance,
                txn.notes,
                txn.id,
            ))
            return cursor.rowcount > 0
    
    def delete_transaction(self, txn_id: int) -> bool:
        """Delete a transaction by ID. Returns True if successful."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM transactions WHERE id = ?", (txn_id,))
            return cursor.rowcount > 0
    
    def get_transaction(self, txn_id: int) -> Optional[Transaction]:
        """Get a single transaction by ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM transactions WHERE id = ?", (txn_id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_transaction(row)
            return None
    
    def get_all_transactions(self) -> list[Transaction]:
        """Get all transactions ordered by date."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM transactions 
                ORDER BY date ASC, id ASC
            """)
            return [self._row_to_transaction(row) for row in cursor.fetchall()]
    
    def get_transactions_by_date_range(
        self, 
        start_date: date, 
        end_date: date
    ) -> list[Transaction]:
        """Get transactions within a date range."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM transactions 
                WHERE date BETWEEN ? AND ?
                ORDER BY date ASC, id ASC
            """, (start_date.isoformat(), end_date.isoformat()))
            return [self._row_to_transaction(row) for row in cursor.fetchall()]
    
    def get_transaction_count(self) -> int:
        """Get total number of transactions."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM transactions")
            return cursor.fetchone()[0]
    
    def _row_to_transaction(self, row: sqlite3.Row) -> Transaction:
        """Convert a database row to a Transaction object."""
        return Transaction(
            id=row["id"],
            date=date.fromisoformat(row["date"]),
            type=TransactionType(row["type"]),
            item=row["item"],
            category=row["category"] or "",
            quantity=row["quantity"],
            unit_price=row["unit_price"],
            discount=row["discount"],
            account=AccountType(row["account"]),
            location=row["location"] or "",
            notes=row["notes"] or "",
            subtotal=row["subtotal"],
            total=row["total"],
            personal_balance=row["personal_balance"],
            company_balance=row["company_balance"],
        )
    
    # ==================== CATEGORY OPERATIONS ====================
    
    def add_category(self, category: Category) -> int:
        """Add a new category. Returns the new ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO categories (name, parent)
                VALUES (?, ?)
            """, (category.name, category.parent))
            return cursor.lastrowid
    
    def get_all_categories(self) -> list[Category]:
        """Get all categories."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM categories ORDER BY name")
            return [
                Category(id=row["id"], name=row["name"], parent=row["parent"] or "")
                for row in cursor.fetchall()
            ]
    
    def get_category_names(self) -> list[str]:
        """Get just the category names for dropdowns."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM categories ORDER BY name")
            return [row["name"] for row in cursor.fetchall()]
    
    # ==================== LOCATION OPERATIONS ====================
    
    def add_location(self, location: Location) -> int:
        """Add a new location. Returns the new ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO locations (name, map_name, location_type)
                VALUES (?, ?, ?)
            """, (location.name, location.map_name, location.location_type))
            return cursor.lastrowid
    
    def get_all_locations(self) -> list[Location]:
        """Get all locations."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM locations ORDER BY name")
            return [
                Location(
                    id=row["id"], 
                    name=row["name"], 
                    map_name=row["map_name"] or "",
                    location_type=row["location_type"] or ""
                )
                for row in cursor.fetchall()
            ]
    
    def get_location_names(self) -> list[str]:
        """Get just the location names for dropdowns."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM locations ORDER BY name")
            return [row["name"] for row in cursor.fetchall()]
    
    # ==================== GAME SETTINGS OPERATIONS ====================
    
    def get_game_settings(self) -> GameSettings:
        """Get game settings (creates default if none exist)."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM game_settings WHERE id = 1")
            row = cursor.fetchone()
            
            if row:
                return GameSettings(
                    id=1,
                    game_start_date=date.fromisoformat(row["game_start_date"]) if row["game_start_date"] else date.today(),
                    current_game_date=date.fromisoformat(row["current_game_date"]) if row["current_game_date"] else date.today(),
                    starting_capital=row["starting_capital"],
                    difficulty=row["difficulty"],
                    personal_balance=row["personal_balance"],
                    company_balance=row["company_balance"],
                    personal_split=row["personal_split"],
                    company_split=row["company_split"],
                    oil_quota=row["oil_quota"],
                    oil_sold=row["oil_sold"],
                    vendor_negotiation_level=row["vendor_negotiation_level"] if "vendor_negotiation_level" in row.keys() else 0,
                    vendor_negotiation_discount=row["vendor_negotiation_discount"] if "vendor_negotiation_discount" in row.keys() else 0.0,
                    investment_forecasting_level=row["investment_forecasting_level"] if "investment_forecasting_level" in row.keys() else 0,
                    investment_forecasting_discount=row["investment_forecasting_discount"] if "investment_forecasting_discount" in row.keys() else 0.0,
                )
            else:
                # Create default settings
                settings = GameSettings(id=1)
                self.save_game_settings(settings)
                return settings
    
    def save_game_settings(self, settings: GameSettings) -> bool:
        """Save game settings."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO game_settings
                (id, game_start_date, current_game_date, starting_capital,
                 difficulty, personal_balance, company_balance,
                 personal_split, company_split, oil_quota, oil_sold,
                 vendor_negotiation_level, vendor_negotiation_discount,
                 investment_forecasting_level, investment_forecasting_discount)
                VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                settings.game_start_date.isoformat(),
                settings.current_game_date.isoformat(),
                settings.starting_capital,
                settings.difficulty,
                settings.personal_balance,
                settings.company_balance,
                settings.personal_split,
                settings.company_split,
                settings.oil_quota,
                settings.oil_sold,
                settings.vendor_negotiation_level,
                settings.vendor_negotiation_discount,
                settings.investment_forecasting_level,
                settings.investment_forecasting_discount,
            ))
            return True


# Global database instance (created on first import)
_db_instance: Optional[Database] = None


def get_database() -> Database:
    """Get the global database instance."""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance
