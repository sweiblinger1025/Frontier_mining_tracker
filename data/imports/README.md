# Reference Data Import Files

Place your Excel files here for importing reference data into the application.

## Required Files

### Frontier_Mining_Dashboard_5.xlsx
Contains:
- **Price Tables** - Item prices (buy/sell) for all 520+ items
- **Categories** - 64 item categories
- **Location List** - Game locations
- **Game Info** - Game settings and skill discounts

### Out_of_Ore__Frontier_Mining_Challenge_Tracker_5.xlsx
Contains:
- **Item Rules** - Purchase/sell rules for items (Can Buy?, Can Sell?)

## How to Import

1. Launch Frontier Mining Tracker
2. Go to **File → Import from Excel** (Ctrl+I)
3. Select `Frontier_Mining_Dashboard_5.xlsx`
4. The application will automatically look for the Challenge Tracker file in the same folder

Alternatively, go to **Reference Data → Items** tab and click **Import Excel**.

## Notes

- The database comes pre-populated with reference data
- Re-importing will update prices and rules if the game receives updates
- Your transaction data (Ledger) is preserved when re-importing reference data
