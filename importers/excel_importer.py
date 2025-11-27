"""
Excel/CSV Importer - Import reference data from Excel or CSV files

Imports:
- Price Tables + Item Rules (merged: 520 items with prices and purchase/sell rules)
- Categories (71 categories)
- Locations (212 locations)
- Game Info (settings, skill discounts)
- Ledger transactions (for migration)

Supports both .xlsx and .csv file formats.
"""

import pandas as pd
from pathlib import Path
from typing import Optional
from datetime import datetime, date

from core.models import Item, Category, Location, Transaction, TransactionType, AccountType
from core.database import Database


class ExcelImporter:
    """Import data from Excel/CSV files into the database."""
    
    def __init__(self, db: Database):
        self.db = db
        self._items_cache: list[Item] = []
        self._categories_cache: list[str] = []
        self._locations_cache: list[str] = []
    
    # ==================== FILE READING HELPERS ====================
    
    def _read_file(self, file_path: Path) -> pd.DataFrame:
        """Read a file as DataFrame, supporting both Excel and CSV."""
        suffix = file_path.suffix.lower()
        if suffix == '.csv':
            return pd.read_csv(file_path)
        elif suffix in ['.xlsx', '.xls']:
            return pd.read_excel(file_path)
        else:
            raise ValueError(f"Unsupported file format: {suffix}")
    
    def _parse_currency(self, value) -> float:
        """
        Parse a currency value that may have formatting like $1,234.56
        Returns 0.0 if parsing fails.
        """
        if pd.isna(value):
            return 0.0
        
        if isinstance(value, (int, float)):
            return float(value)
        
        # Convert to string and clean up
        s = str(value).strip()
        
        # Remove currency symbols and thousands separators
        s = s.replace('$', '').replace(',', '').replace(' ', '')
        
        # Handle parentheses for negative numbers: ($100) -> -100
        if s.startswith('(') and s.endswith(')'):
            s = '-' + s[1:-1]
        
        # Handle percentage signs
        s = s.replace('%', '')
        
        try:
            return float(s)
        except ValueError:
            return 0.0
    
    # ==================== CSV IMPORT METHODS ====================
    
    def import_price_tables_csv(self, file_path: Path) -> int:
        """Import Price Tables from a CSV file."""
        df = self._read_file(file_path)
        return self._import_items_from_dataframe(df, None)
    
    def import_item_rules_csv(self, file_path: Path) -> int:
        """
        Import Item Rules from a CSV file and update existing items.
        Should be called AFTER importing Price Tables.
        """
        df = self._read_file(file_path)
        
        count = 0
        with self.db._get_connection() as conn:
            cursor = conn.cursor()
            
            for _, row in df.iterrows():
                try:
                    name = str(row["Item Name"]) if pd.notna(row.get("Item Name")) else ""
                    category = str(row["Category"]) if pd.notna(row.get("Category")) else ""
                    
                    if not name:
                        continue
                    
                    can_purchase = str(row.get("Can Purchase?", "Yes")).strip().lower() == "yes"
                    can_sell = str(row.get("Can Sell?", "Yes")).strip().lower() == "yes"
                    notes = str(row.get("Notes", "")) if pd.notna(row.get("Notes")) else ""
                    
                    # Update existing item
                    cursor.execute("""
                        UPDATE items 
                        SET can_purchase = ?, can_sell = ?, notes = ?
                        WHERE name = ? AND category = ?
                    """, (
                        1 if can_purchase else 0,
                        1 if can_sell else 0,
                        notes,
                        name,
                        category,
                    ))
                    
                    if cursor.rowcount > 0:
                        count += 1
                    else:
                        # Item doesn't exist, insert it with zero prices
                        cursor.execute("""
                            INSERT OR IGNORE INTO items 
                            (name, category, buy_price, current_buy_price, sell_price, 
                             can_purchase, can_sell, notes)
                            VALUES (?, ?, 0, 0, 0, ?, ?, ?)
                        """, (
                            name,
                            category,
                            1 if can_purchase else 0,
                            1 if can_sell else 0,
                            notes,
                        ))
                        if cursor.rowcount > 0:
                            count += 1
                            
                except Exception as e:
                    print(f"Error importing item rule {row.get('Item Name', 'unknown')}: {e}")
        
        return count
    
    def import_categories_csv(self, file_path: Path) -> int:
        """Import Categories from a CSV file."""
        df = self._read_file(file_path)
        
        count = 0
        with self.db._get_connection() as conn:
            cursor = conn.cursor()
            
            current_parent = ""
            for _, row in df.iterrows():
                cat_name = str(row["Category"]) if pd.notna(row.get("Category")) else ""
                if not cat_name:
                    continue
                
                # Check if this is a parent category (ALL CAPS, no hyphen)
                if cat_name.isupper() and " - " not in cat_name:
                    current_parent = cat_name
                    continue
                
                try:
                    if " - " in cat_name:
                        parts = cat_name.split(" - ", 1)
                        parent = parts[0].strip()
                        name = cat_name
                    else:
                        parent = current_parent
                        name = cat_name
                    
                    cursor.execute("""
                        INSERT OR IGNORE INTO categories (name, parent)
                        VALUES (?, ?)
                    """, (name, parent))
                    if cursor.rowcount > 0:
                        count += 1
                except Exception as e:
                    print(f"Error importing category {cat_name}: {e}")
        
        return count
    
    def import_locations_csv(self, file_path: Path) -> int:
        """Import Locations from a CSV file."""
        df = self._read_file(file_path)
        
        count = 0
        with self.db._get_connection() as conn:
            cursor = conn.cursor()
            
            for _, row in df.iterrows():
                try:
                    name = str(row["Location"]) if pd.notna(row.get("Location")) else ""
                    if not name:
                        continue
                    
                    cursor.execute("""
                        INSERT OR IGNORE INTO locations (name, map_name, location_type)
                        VALUES (?, ?, ?)
                    """, (
                        name,
                        str(row["Map"]) if pd.notna(row.get("Map")) else "",
                        str(row["Type"]) if pd.notna(row.get("Type")) else "",
                    ))
                    if cursor.rowcount > 0:
                        count += 1
                except Exception as e:
                    print(f"Error importing location {row.get('Location', 'unknown')}: {e}")
        
        return count
    
    def import_game_info_csv(self, file_path: Path) -> bool:
        """Import Game Info from a CSV file."""
        df = self._read_file(file_path)
        
        # Build a lookup dict from Setting -> Value
        settings_lookup = {}
        for _, row in df.iterrows():
            setting = str(row["Setting"]) if pd.notna(row.get("Setting")) else ""
            value = row.get("Value")
            if setting:
                settings_lookup[setting] = value
        
        return self._save_game_settings_from_lookup(settings_lookup)
    
    # ==================== SHARED IMPORT LOGIC ====================
    
    def _save_game_settings_from_lookup(self, settings_lookup: dict) -> bool:
        """Save game settings from a lookup dictionary."""
        try:
            from core.models import GameSettings
            
            def parse_date(val):
                if pd.isna(val):
                    return date.today()
                if isinstance(val, datetime):
                    return val.date()
                try:
                    return datetime.fromisoformat(str(val)[:10]).date()
                except:
                    return date.today()
            
            def parse_float(val, default=0.0):
                if pd.isna(val):
                    return default
                try:
                    return float(val)
                except:
                    return default
            
            def parse_int(val, default=0):
                if pd.isna(val):
                    return default
                try:
                    return int(float(val))
                except:
                    return default
            
            settings = GameSettings(
                id=1,
                game_start_date=parse_date(settings_lookup.get("Game Start Date")),
                current_game_date=parse_date(settings_lookup.get("Current Game Date")),
                starting_capital=parse_float(settings_lookup.get("Starting Capital"), 100000),
                personal_balance=parse_float(settings_lookup.get("Current Personal Balance")),
                company_balance=parse_float(settings_lookup.get("Current Company Balance")),
                vendor_negotiation_level=parse_int(settings_lookup.get("Vendor Negotiation (VN)")),
                vendor_negotiation_discount=parse_float(settings_lookup.get("VN Discount %")) / 100 if parse_float(settings_lookup.get("VN Discount %")) > 1 else parse_float(settings_lookup.get("VN Discount %")),
                investment_forecasting_level=parse_int(settings_lookup.get("Investment Forecasting (IF)")),
                investment_forecasting_discount=parse_float(settings_lookup.get("IF Discount %")) / 100 if parse_float(settings_lookup.get("IF Discount %")) > 1 else parse_float(settings_lookup.get("IF Discount %")),
            )
            
            self.db.save_game_settings(settings)
            return True
            
        except Exception as e:
            print(f"Error saving game settings: {e}")
            return False
    
    def _import_items_from_dataframe(
        self, 
        df_prices: pd.DataFrame, 
        item_rules_df: Optional[pd.DataFrame]
    ) -> int:
        """Import items from a DataFrame, optionally merging with item rules."""
        
        # Build a lookup from Item Rules: (name, category) -> (can_purchase, can_sell, notes)
        rules_lookup = {}
        if item_rules_df is not None:
            for _, row in item_rules_df.iterrows():
                name = str(row["Item Name"]) if pd.notna(row.get("Item Name")) else ""
                category = str(row["Category"]) if pd.notna(row.get("Category")) else ""
                can_purchase = str(row.get("Can Purchase?", "Yes")).strip().lower() == "yes"
                can_sell = str(row.get("Can Sell?", "Yes")).strip().lower() == "yes"
                notes = str(row.get("Notes", "")) if pd.notna(row.get("Notes")) else ""
                rules_lookup[(name, category)] = (can_purchase, can_sell, notes)
        
        count = 0
        with self.db._get_connection() as conn:
            cursor = conn.cursor()
            
            for _, row in df_prices.iterrows():
                try:
                    name = str(row["Item Name"]) if pd.notna(row.get("Item Name")) else ""
                    category = str(row["Category"]) if pd.notna(row.get("Category")) else ""
                    
                    if not name:
                        continue
                    
                    # Look up rules (default to Yes/Yes if not found)
                    can_purchase, can_sell, notes = rules_lookup.get(
                        (name, category), 
                        (True, True, "")
                    )
                    
                    # Get both base price and current (discounted) price
                    # Use _parse_currency to handle formatted values like "$1,234"
                    buy_price = self._parse_currency(row.get("Buy Price"))
                    sell_price = self._parse_currency(row.get("Sell Price"))
                    current_buy_price = self._parse_currency(row.get("Current Buy Price"))
                    
                    # If no current price, use base price
                    if current_buy_price == 0 and buy_price > 0:
                        current_buy_price = buy_price
                    
                    cursor.execute("""
                        INSERT OR REPLACE INTO items 
                        (name, category, buy_price, current_buy_price, sell_price, 
                         can_purchase, can_sell, notes)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        name,
                        category,
                        buy_price,
                        current_buy_price,
                        sell_price,
                        1 if can_purchase else 0,
                        1 if can_sell else 0,
                        notes,
                    ))
                    count += 1
                except Exception as e:
                    print(f"Error importing item {row.get('Item Name', 'unknown')}: {e}")
        
        return count

    # ==================== EXCEL IMPORT METHODS ====================
    
    def import_all_reference_data(
        self, 
        dashboard_path: Path, 
        tracker_path: Optional[Path] = None
    ) -> dict:
        """
        Import all reference data from Excel file(s).
        
        Args:
            dashboard_path: Path to Frontier_Mining_Dashboard.xlsx
            tracker_path: Path to Challenge_Tracker.xlsx (for Item Rules)
        
        Returns dict with counts of imported items.
        """
        results = {
            "items": 0,
            "categories": 0,
            "locations": 0,
            "game_settings": False,
            "errors": [],
        }
        
        try:
            xl_dashboard = pd.ExcelFile(dashboard_path)
            xl_tracker = pd.ExcelFile(tracker_path) if tracker_path else None
            
            # Import Game Info (settings, skill discounts)
            if "Game Info" in xl_dashboard.sheet_names:
                results["game_settings"] = self._import_game_info(xl_dashboard)
            
            # Import Price Tables + Item Rules (merged)
            if "Price Tables" in xl_dashboard.sheet_names:
                item_rules_df = None
                if xl_tracker and "Item Rules" in xl_tracker.sheet_names:
                    item_rules_df = pd.read_excel(xl_tracker, sheet_name="Item Rules")
                results["items"] = self._import_items_merged(xl_dashboard, item_rules_df)
            
            # Import Categories
            if "Categories" in xl_dashboard.sheet_names:
                results["categories"] = self._import_categories(xl_dashboard)
            
            # Import Locations
            if "Location List" in xl_dashboard.sheet_names:
                results["locations"] = self._import_locations(xl_dashboard)
                
        except Exception as e:
            import traceback
            results["errors"].append(f"{str(e)}\n{traceback.format_exc()}")
        
        return results
    
    def _import_game_info(self, xl: pd.ExcelFile) -> bool:
        """Import game settings from Game Info sheet."""
        df = pd.read_excel(xl, sheet_name="Game Info")
        
        # Build a lookup dict from Setting -> Value
        settings_lookup = {}
        for _, row in df.iterrows():
            setting = str(row["Setting"]) if pd.notna(row.get("Setting")) else ""
            value = row.get("Value")
            if setting:
                settings_lookup[setting] = value
        
        return self._save_game_settings_from_lookup(settings_lookup)
    
    def _import_items_merged(
        self, 
        xl_dashboard: pd.ExcelFile, 
        item_rules_df: Optional[pd.DataFrame]
    ) -> int:
        """Import items from Price Tables, merging with Item Rules if available."""
        df_prices = pd.read_excel(xl_dashboard, sheet_name="Price Tables")
        return self._import_items_from_dataframe(df_prices, item_rules_df)
    
    def _import_categories(self, xl: pd.ExcelFile) -> int:
        """Import categories from Categories sheet."""
        df = pd.read_excel(xl, sheet_name="Categories")
        
        count = 0
        with self.db._get_connection() as conn:
            cursor = conn.cursor()
            
            current_parent = ""
            for _, row in df.iterrows():
                cat_name = str(row["Category"]) if pd.notna(row.get("Category")) else ""
                if not cat_name:
                    continue
                
                # Check if this is a parent category (ALL CAPS, no hyphen)
                if cat_name.isupper() and " - " not in cat_name:
                    current_parent = cat_name
                    continue
                
                try:
                    if " - " in cat_name:
                        parts = cat_name.split(" - ", 1)
                        parent = parts[0].strip()
                        name = cat_name
                    else:
                        parent = current_parent
                        name = cat_name
                    
                    cursor.execute("""
                        INSERT OR IGNORE INTO categories (name, parent)
                        VALUES (?, ?)
                    """, (name, parent))
                    if cursor.rowcount > 0:
                        count += 1
                except Exception as e:
                    print(f"Error importing category {cat_name}: {e}")
        
        return count
    
    def _import_locations(self, xl: pd.ExcelFile) -> int:
        """Import locations from Location List sheet."""
        df = pd.read_excel(xl, sheet_name="Location List")
        
        count = 0
        with self.db._get_connection() as conn:
            cursor = conn.cursor()
            
            for _, row in df.iterrows():
                try:
                    name = str(row["Location"]) if pd.notna(row.get("Location")) else ""
                    if not name:
                        continue
                    
                    cursor.execute("""
                        INSERT OR IGNORE INTO locations (name, map_name, location_type)
                        VALUES (?, ?, ?)
                    """, (
                        name,
                        str(row["Map"]) if pd.notna(row.get("Map")) else "",
                        str(row["Type"]) if pd.notna(row.get("Type")) else "",
                    ))
                    if cursor.rowcount > 0:
                        count += 1
                except Exception as e:
                    print(f"Error importing location {row.get('Location', 'unknown')}: {e}")
        
        return count
    
    def import_ledger(self, file_path: Path) -> dict:
        """
        Import existing ledger transactions from Excel or CSV.
        
        Returns dict with count and any errors.
        """
        results = {
            "transactions": 0,
            "errors": [],
        }
        
        try:
            # Read file - for Excel, try to read "Ledger" sheet specifically
            suffix = file_path.suffix.lower()
            if suffix in ['.xlsx', '.xls']:
                xl = pd.ExcelFile(file_path)
                if "Ledger" in xl.sheet_names:
                    df = pd.read_excel(xl, sheet_name="Ledger")
                else:
                    df = pd.read_excel(file_path)  # First sheet
            else:
                df = pd.read_csv(file_path)
            
            with self.db._get_connection() as conn:
                cursor = conn.cursor()
                
                for _, row in df.iterrows():
                    # Skip empty rows
                    if pd.isna(row.get("Type")) or pd.isna(row.get("Item")):
                        continue
                    
                    try:
                        # Parse transaction type
                        type_str = str(row["Type"]).strip()
                        
                        # Handle Opening Balance specially
                        if type_str == "Transfer" and str(row.get("Item", "")).strip() == "Opening Balance":
                            type_str = "Opening"
                        
                        # Parse account type
                        account_str = str(row.get("Account", "")) if pd.notna(row.get("Account")) else ""
                        
                        # Parse date
                        date_val = row.get("Date")
                        if pd.notna(date_val):
                            if isinstance(date_val, datetime):
                                date_str = date_val.date().isoformat()
                            else:
                                date_str = str(date_val)[:10]
                        else:
                            date_str = datetime.now().date().isoformat()
                        
                        cursor.execute("""
                            INSERT INTO transactions 
                            (date, type, item, category, quantity, unit_price,
                             subtotal, discount, total, 
                             personal_income, company_income, personal_expense, company_expense,
                             account, location, personal_balance, company_balance, notes)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            date_str,
                            type_str,
                            str(row["Item"]).strip(),
                            str(row.get("Category", "")).strip() if pd.notna(row.get("Category")) else "",
                            float(row.get("Qty", 1)) if pd.notna(row.get("Qty")) else None,
                            self._parse_currency(row.get("Unit Price")),
                            self._parse_currency(row.get("Subtotal")),
                            self._parse_currency(row.get("Discount")),
                            self._parse_currency(row.get("Total")),
                            self._parse_currency(row.get("Personal Income")),
                            self._parse_currency(row.get("Company Income")),
                            self._parse_currency(row.get("Personal Expense")),
                            self._parse_currency(row.get("Company Expense")),
                            account_str,
                            str(row.get("Location", "")).strip() if pd.notna(row.get("Location")) else "",
                            self._parse_currency(row.get("Personal Balance")),
                            self._parse_currency(row.get("Company Balance")),
                            str(row.get("Notes", "")).strip() if pd.notna(row.get("Notes")) else "",
                        ))
                        results["transactions"] += 1
                        
                    except Exception as e:
                        results["errors"].append(f"Row error ({row.get('Item', 'unknown')}): {e}")
                        
        except Exception as e:
            import traceback
            results["errors"].append(f"{str(e)}\n{traceback.format_exc()}")
        
        return results
        
        return results
    
    # ==================== QUERY METHODS (for UI dropdowns) ====================
    
    def get_all_items(self) -> list[Item]:
        """Get all items from database."""
        with self.db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, art_nr, name, category, buy_price, current_buy_price,
                       sell_price, can_purchase, can_sell, notes
                FROM items ORDER BY category, name
            """)
            return [
                Item(
                    id=row["id"],
                    art_nr=row["art_nr"] or 0,
                    name=row["name"],
                    category=row["category"] or "",
                    buy_price=row["buy_price"],
                    current_buy_price=row["current_buy_price"],
                    sell_price=row["sell_price"],
                    can_purchase=bool(row["can_purchase"]),
                    can_sell=bool(row["can_sell"]),
                    notes=row["notes"] or "",
                )
                for row in cursor.fetchall()
            ]
    
    def get_item_names(self) -> list[str]:
        """Get just item names for autocomplete (unique names only)."""
        with self.db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT name FROM items ORDER BY name")
            return [row["name"] for row in cursor.fetchall()]
    
    def get_item_names_with_category(self) -> list[tuple[str, str]]:
        """Get item names with categories for full selection (handles duplicates)."""
        with self.db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name, category FROM items ORDER BY category, name")
            return [(row["name"], row["category"]) for row in cursor.fetchall()]
    
    def get_item_by_name(self, name: str) -> Optional[Item]:
        """
        Get item details by name.
        NOTE: Returns first match. For items with duplicate names across categories,
        use get_item_by_name_and_category() instead.
        """
        with self.db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, art_nr, name, category, buy_price, current_buy_price,
                       sell_price, can_purchase, can_sell, notes
                FROM items WHERE name = ? LIMIT 1
            """, (name,))
            row = cursor.fetchone()
            if row:
                return Item(
                    id=row["id"],
                    art_nr=row["art_nr"] or 0,
                    name=row["name"],
                    category=row["category"] or "",
                    buy_price=row["buy_price"],
                    current_buy_price=row["current_buy_price"],
                    sell_price=row["sell_price"],
                    can_purchase=bool(row["can_purchase"]),
                    can_sell=bool(row["can_sell"]),
                    notes=row["notes"] or "",
                )
            return None
    
    def get_item_by_name_and_category(self, name: str, category: str) -> Optional[Item]:
        """Get item by both name and category (for items with duplicate names)."""
        with self.db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, art_nr, name, category, buy_price, current_buy_price,
                       sell_price, can_purchase, can_sell, notes
                FROM items WHERE name = ? AND category = ?
            """, (name, category))
            row = cursor.fetchone()
            if row:
                return Item(
                    id=row["id"],
                    art_nr=row["art_nr"] or 0,
                    name=row["name"],
                    category=row["category"] or "",
                    buy_price=row["buy_price"],
                    current_buy_price=row["current_buy_price"],
                    sell_price=row["sell_price"],
                    can_purchase=bool(row["can_purchase"]),
                    can_sell=bool(row["can_sell"]),
                    notes=row["notes"] or "",
                )
            return None
    
    def get_items_by_category(self, category: str) -> list[Item]:
        """Get all items in a category."""
        with self.db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, art_nr, name, category, buy_price, current_buy_price,
                       sell_price, can_purchase, can_sell, notes
                FROM items WHERE category = ? ORDER BY name
            """, (category,))
            return [
                Item(
                    id=row["id"],
                    art_nr=row["art_nr"] or 0,
                    name=row["name"],
                    category=row["category"] or "",
                    buy_price=row["buy_price"],
                    current_buy_price=row["current_buy_price"],
                    sell_price=row["sell_price"],
                    can_purchase=bool(row["can_purchase"]),
                    can_sell=bool(row["can_sell"]),
                    notes=row["notes"] or "",
                )
                for row in cursor.fetchall()
            ]
    
    def get_purchasable_items(self) -> list[Item]:
        """Get only items that can be purchased (for Purchase transactions)."""
        with self.db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, art_nr, name, category, buy_price, current_buy_price,
                       sell_price, can_purchase, can_sell, notes
                FROM items WHERE can_purchase = 1 ORDER BY category, name
            """)
            return [
                Item(
                    id=row["id"],
                    art_nr=row["art_nr"] or 0,
                    name=row["name"],
                    category=row["category"] or "",
                    buy_price=row["buy_price"],
                    current_buy_price=row["current_buy_price"],
                    sell_price=row["sell_price"],
                    can_purchase=True,
                    can_sell=bool(row["can_sell"]),
                    notes=row["notes"] or "",
                )
                for row in cursor.fetchall()
            ]
    
    def get_sellable_items(self) -> list[Item]:
        """Get only items that can be sold (for Sale transactions)."""
        with self.db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, art_nr, name, category, buy_price, current_buy_price,
                       sell_price, can_purchase, can_sell, notes
                FROM items WHERE can_sell = 1 ORDER BY category, name
            """)
            return [
                Item(
                    id=row["id"],
                    art_nr=row["art_nr"] or 0,
                    name=row["name"],
                    category=row["category"] or "",
                    buy_price=row["buy_price"],
                    current_buy_price=row["current_buy_price"],
                    sell_price=row["sell_price"],
                    can_purchase=bool(row["can_purchase"]),
                    can_sell=True,
                    notes=row["notes"] or "",
                )
                for row in cursor.fetchall()
            ]
    
    def get_discounted_items(self) -> list[Item]:
        """Get items that currently have a discount applied."""
        with self.db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, art_nr, name, category, buy_price, current_buy_price,
                       sell_price, can_purchase, can_sell, notes
                FROM items 
                WHERE current_buy_price < buy_price 
                ORDER BY category, name
            """)
            return [
                Item(
                    id=row["id"],
                    art_nr=row["art_nr"] or 0,
                    name=row["name"],
                    category=row["category"] or "",
                    buy_price=row["buy_price"],
                    current_buy_price=row["current_buy_price"],
                    sell_price=row["sell_price"],
                    can_purchase=bool(row["can_purchase"]),
                    can_sell=bool(row["can_sell"]),
                    notes=row["notes"] or "",
                )
                for row in cursor.fetchall()
            ]
    
    def check_duplicate_name(self, name: str) -> list[str]:
        """
        Check if an item name exists in multiple categories.
        Returns list of categories if duplicates exist, empty list otherwise.
        """
        with self.db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT category FROM items WHERE name = ? ORDER BY category
            """, (name,))
            categories = [row["category"] for row in cursor.fetchall()]
            return categories if len(categories) > 1 else []
