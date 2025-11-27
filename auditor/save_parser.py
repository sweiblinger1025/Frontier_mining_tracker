"""
Save File Parser - Parse Out of Ore GVAS save files

Handles Unreal Engine 4 GVAS save format used by Out of Ore.
All monetary values in the save file are scaled by 256.
"""

import struct
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional


# Scale factor for monetary values in save file
MONEY_SCALE = 256


@dataclass
class SaveTransaction:
    """A transaction record from the save file."""
    item_code: str
    category: str
    amount_raw: int  # Raw value from save (scaled)
    
    @property
    def amount(self) -> float:
        """Get the actual dollar amount."""
        return self.amount_raw / MONEY_SCALE
    
    @property
    def is_purchase(self) -> bool:
        """True if this was a purchase (negative amount)."""
        return self.amount_raw < 0
    
    @property
    def is_sale(self) -> bool:
        """True if this was a sale (positive amount)."""
        return self.amount_raw > 0


@dataclass 
class SaveInventoryItem:
    """An inventory item from the save file."""
    name: str
    amount: int
    condition: float = 100.0
    

@dataclass
class SaveFileData:
    """Parsed data from a save file."""
    file_path: Path
    file_size: int
    
    # Money
    current_money_raw: int = 0
    
    # Transactions
    transactions: list[SaveTransaction] = field(default_factory=list)
    
    # Inventory
    inventory_items: list[SaveInventoryItem] = field(default_factory=list)
    
    # Map/Location
    map_name: str = ""
    
    # Metadata
    engine_version: str = ""
    game_version: str = ""
    
    @property
    def current_money(self) -> float:
        """Get the actual current money amount."""
        return self.current_money_raw / MONEY_SCALE
    
    @property
    def total_purchases(self) -> float:
        """Total amount spent on purchases."""
        return sum(t.amount for t in self.transactions if t.is_purchase)
    
    @property
    def total_sales(self) -> float:
        """Total amount earned from sales."""
        return sum(t.amount for t in self.transactions if t.is_sale)


class SaveFileParser:
    """Parser for Out of Ore GVAS save files."""
    
    MAGIC = b'GVAS'
    
    def __init__(self):
        self.data: bytes = b''
        self.result: Optional[SaveFileData] = None
    
    def parse(self, file_path: Path) -> SaveFileData:
        """Parse a save file and return extracted data."""
        self.result = SaveFileData(
            file_path=file_path,
            file_size=file_path.stat().st_size
        )
        
        with open(file_path, 'rb') as f:
            self.data = f.read()
        
        # Verify magic
        if not self.data.startswith(self.MAGIC):
            raise ValueError(f"Not a valid GVAS save file: {file_path}")
        
        # Parse header
        self._parse_header()
        
        # Parse money
        self._parse_money()
        
        # Parse transactions
        self._parse_transactions()
        
        # Parse map name
        self._parse_map()
        
        # Parse inventory (basic)
        self._parse_inventory()
        
        return self.result
    
    def _parse_header(self):
        """Parse the GVAS header."""
        # Magic (4) + Version (4) + Package Version (4) + Unknown (4) + Engine Version String
        try:
            offset = 4 + 4 + 4 + 4
            
            # Read engine version string
            str_len = struct.unpack('<i', self.data[offset:offset+4])[0]
            offset += 4
            
            if str_len > 0 and str_len < 100:
                self.result.engine_version = self.data[offset:offset+str_len-1].decode('utf-8', errors='replace')
            
            # Look for game version pattern
            version_match = re.search(rb'(\d+\.\d+\.\d+)', self.data[:500])
            if version_match:
                self.result.game_version = version_match.group(1).decode('ascii')
                
        except Exception:
            pass  # Header parsing is optional
    
    def _parse_money(self):
        """Parse the current money value."""
        # Find NewMoney property
        pos = self.data.find(b'NewMoney\x00')
        if pos == -1:
            return
        
        try:
            # Structure: NewMoney\x00 + type_len(4) + "IntProperty\x00" + size(8) + value(4)
            offset = pos + 9  # After "NewMoney\x00"
            type_len = struct.unpack('<i', self.data[offset:offset+4])[0]
            offset += 4 + type_len + 8  # Skip type string and size
            
            self.result.current_money_raw = struct.unpack('<i', self.data[offset:offset+4])[0]
        except Exception:
            pass
    
    def _parse_transactions(self):
        """Parse transaction history."""
        # Find TransactionsHistory
        trans_start = self.data.find(b'TransactionsHistory')
        if trans_start == -1:
            return
        
        # Search area for transactions
        search_area = self.data[trans_start:trans_start+20000]
        
        # Find each Name property (start of a transaction)
        name_pattern = b'\x05\x00\x00\x00Name\x00'
        pos = 0
        
        while True:
            pos = search_area.find(name_pattern, pos)
            if pos == -1:
                break
            
            try:
                transaction = self._parse_single_transaction(search_area, pos)
                if transaction:
                    self.result.transactions.append(transaction)
            except Exception:
                pass
            
            pos += 1
    
    def _parse_single_transaction(self, data: bytes, name_pos: int) -> Optional[SaveTransaction]:
        """Parse a single transaction entry."""
        area = data[name_pos+6:name_pos+250]
        
        # Find item code (6-digit number)
        code_match = re.search(rb'([0-9]{6})\x00', area)
        if not code_match:
            return None
        
        item_code = code_match.group(1).decode()
        
        # Find Category
        cat_pos = area.find(b'Category\x00')
        if cat_pos == -1:
            return None
        
        cat_area = area[cat_pos:cat_pos+100]
        cat_match = re.search(rb'\x00([A-Za-z_]{3,30})\x00', cat_area[20:])
        category = cat_match.group(1).decode() if cat_match else "Unknown"
        
        # Find Amount
        amt_pos = area.find(b'Amount\x00')
        if amt_pos == -1:
            return None
        
        amount_area = area[amt_pos:amt_pos+50]
        int_pos = amount_area.find(b'IntProperty')
        if int_pos == -1:
            return None
        
        val_pos = int_pos + 12 + 8
        if val_pos + 4 > len(amount_area):
            return None
        
        amount_raw = struct.unpack('<i', amount_area[val_pos:val_pos+4])[0]
        
        return SaveTransaction(
            item_code=item_code,
            category=category,
            amount_raw=amount_raw
        )
    
    def _parse_map(self):
        """Parse the current map name."""
        # Look for known map patterns
        map_patterns = [
            b'FOREST_QUARRY',
            b'DESERT_MINE',
            b'ARCTIC_MINE',
            b'VOLCANO_MINE',
        ]
        
        for pattern in map_patterns:
            if pattern in self.data:
                self.result.map_name = pattern.decode()
                break
    
    def _parse_inventory(self):
        """Parse inventory items (basic parsing)."""
        # Find PLAYER INVENTORY section
        inv_start = self.data.find(b'PLAYER INVENTORY')
        if inv_start == -1:
            return
        
        # This is more complex - would need to parse the full inventory structure
        # For now, just count items
        inv_area = self.data[inv_start:inv_start+10000]
        
        # Count Amount properties as a rough item count
        amount_count = inv_area.count(b'Amount\x00')
        
        # We'll implement detailed inventory parsing later
        pass


def parse_save_file(file_path: Path) -> SaveFileData:
    """Convenience function to parse a save file."""
    parser = SaveFileParser()
    return parser.parse(file_path)


# For testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        path = Path(sys.argv[1])
        if path.exists():
            result = parse_save_file(path)
            print(f"File: {result.file_path.name}")
            print(f"Size: {result.file_size:,} bytes")
            print(f"Engine: {result.engine_version}")
            print(f"Game Version: {result.game_version}")
            print(f"Map: {result.map_name}")
            print(f"Current Money: ${result.current_money:,.0f}")
            print(f"Transactions: {len(result.transactions)}")
            print(f"Total Sales: ${result.total_sales:,.0f}")
            print(f"Total Purchases: ${result.total_purchases:,.0f}")
