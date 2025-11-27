"""
Item Code Mapping - Maps game's internal Art.Nr codes to item names

PURPOSE: This file is ONLY used for save file auditing/parsing.
         For the main item list, we import from Price Tables (Excel).

The Art.Nr (Article Number) is the game's internal ID for each item.
These codes appear in save files and can be used to cross-reference
transactions with actual game data.

NOTE: This is a partial list covering items commonly found in save files.
      The complete item database (520 items) is loaded from Price Tables.

Format: ART_NR -> (Item Name, Category)
"""

# Item code ranges (observed pattern):
# 1xxxxx - Resources/Materials
# 2xxxxx - Buildings
# 3xxxxx - Equipment/Handtools
# 4xxxxx - Factory/Production
# 5xxxxx - (unknown)
# 6xxxxx - Vehicles

ITEM_CODES: dict[int, tuple[str, str]] = {
    # ==================== EQUIPMENT - HANDTOOLS (3xxxxx) ====================
    300001: ("Pickaxe", "Equipment - Handtools"),
    300002: ("Shovel", "Equipment - Handtools"),
    300004: ("Sledge", "Equipment - Handtools"),
    300065: ("Fast Sledge", "Equipment - Handtools"),
    300066: ("Fast Pickaxe", "Equipment - Handtools"),
    300067: ("Fast Shovel", "Equipment - Handtools"),
    
    # ==================== FACTORY - PRODUCTION (4xxxxx) ====================
    # Extraction
    400181: ("Water Pump", "Factory - Production"),
    400187: ("Oil Pump", "Factory - Production"),
    
    # Crushing
    400129: ("Jaw Crusher", "Factory - Production"),
    400130: ("Cone Crusher", "Factory - Production"),
    
    # Sorting
    400131: ("Trommel", "Factory - Production"),
    400132: ("Shaker Screen", "Factory - Production"),
    400155: ("Coal Screen", "Factory - Production"),
    400203: ("High Temp Sorter", "Factory - Production"),
    400209: ("Metal Ore Sorter", "Factory - Production"),
    
    # Washing
    400133: ("Froth Floater", "Factory - Production"),
    400134: ("Washplant", "Factory - Production"),
    400163: ("Sluice Box", "Factory - Production"),
    
    # Refining
    400204: ("Oil Refinery", "Factory - Production"),
    400205: ("Water Refinery", "Factory - Production"),
    400111: ("Asphalt Plant", "Factory - Production"),
    
    # Smelting
    400188: ("Smelter", "Factory - Production"),
    400199: ("High Temp Smelter", "Factory - Production"),
    
    # Rolling
    400189: ("Bar Roller", "Factory - Production"),
    400192: ("Coil Roller", "Factory - Production"),
    400193: ("Bloom Roller", "Factory - Production"),
    400194: ("Rod Roller", "Factory - Production"),
    400195: ("Plate Shear", "Factory - Production"),
    400196: ("Beam Roller", "Factory - Production"),
    
    # ==================== FACTORY - POWER (4xxxxx) ====================
    400140: ("Power Cable", "Factory - Power"),
    400146: ("Power Input 1x Speed", "Factory - Power"),
    400148: ("Solar Panel 300kW", "Factory - Power"),
    
    # ==================== FACTORY - PIPELINE (4xxxxx) ====================
    400202: ("Liquid Tank", "Factory - Pipeline"),
    
    # ==================== BUILDINGS - WORKBENCHES (4xxxxx) ====================
    400069: ("Wood Workbench", "Buildings - Workbenches"),
    
    # ==================== VEHICLES - FLYING (6xxxxx) ====================
    600041: ("Drone", "Vehicles - Flying"),
}


def get_item_name(art_nr: int) -> str:
    """Get item name from article number."""
    if art_nr in ITEM_CODES:
        return ITEM_CODES[art_nr][0]
    return f"Unknown Item ({art_nr})"


def get_item_category(art_nr: int) -> str:
    """Get item category from article number."""
    if art_nr in ITEM_CODES:
        return ITEM_CODES[art_nr][1]
    return "Unknown"


def get_item_info(art_nr: int) -> tuple[str, str]:
    """Get both name and category from article number."""
    return ITEM_CODES.get(art_nr, (f"Unknown Item ({art_nr})", "Unknown"))


def find_art_nr_by_name(name: str) -> int | None:
    """Find article number by item name (case-insensitive)."""
    name_lower = name.lower()
    for art_nr, (item_name, _) in ITEM_CODES.items():
        if item_name.lower() == name_lower:
            return art_nr
    return None


def get_items_by_category(category: str) -> list[tuple[int, str]]:
    """Get all items in a category. Returns list of (art_nr, name) tuples."""
    result = []
    for art_nr, (name, cat) in ITEM_CODES.items():
        if cat == category:
            result.append((art_nr, name))
    return sorted(result, key=lambda x: x[1])  # Sort by name


def get_all_categories() -> list[str]:
    """Get list of all unique categories."""
    categories = set(cat for _, cat in ITEM_CODES.values())
    return sorted(categories)


# Quick lookup for validation
VALID_ART_NRS = set(ITEM_CODES.keys())


def is_valid_art_nr(art_nr: int) -> bool:
    """Check if an article number is known."""
    return art_nr in VALID_ART_NRS
