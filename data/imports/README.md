# Reference Data Import Files

Place your Excel files here for importing reference data into the application.

## Required Files

### Frontier_Mining_Dashboard_5.xlsx
Contains:
- **Price Tables** - Item prices (buy/sell) for all 520+ items
- **Categories** - 64 item categories
- **Location List** - 212 game locations across 10 maps
- **Game Info** - Game settings and skill discounts

### Out_of_Ore__Frontier_Mining_Challenge_Tracker_5.xlsx
Contains:
- **Item Rules** - Purchase/sell rules for items (Can Buy?, Can Sell?)

## How to Import

### Full Import (Recommended)
1. Launch Frontier Mining Tracker
2. Go to **File → Import from Excel** (Ctrl+I)
3. Select `Frontier_Mining_Dashboard_5.xlsx`
4. The application will automatically look for the Challenge Tracker file in the same folder

### Individual Tab Imports
- **Reference Data → Items** - Click "Import Excel" for price tables
- **Reference Data → Locations** - Click "Import from Excel" for locations

## What Gets Imported

| Data | Count | Source |
|------|-------|--------|
| Items (prices) | 520+ | Price Tables sheet |
| Categories | 64 | Categories sheet |
| Locations | 212 | Location List sheet |
| Maps | 10 | Extracted from locations |
| Location Types | 8 | Location List sheet |
| Item Rules | 520+ | Item Rules sheet |

## Notes

- The database comes pre-populated with reference data
- Re-importing will update prices and rules if the game receives updates
- Your transaction data (Ledger) is preserved when re-importing reference data
- Custom locations you add are preserved during re-import
