# Frontier Mining Tracker

A comprehensive desktop application for tracking mining operations in the game **Out of Ore**. Built with Python and PyQt6.

![Version](https://img.shields.io/badge/version-0.1.0-blue)
![Python](https://img.shields.io/badge/python-3.10+-green)
![License](https://img.shields.io/badge/license-MIT-orange)
![Lines of Code](https://img.shields.io/badge/lines-22%2C000+-purple)

## Overview

Frontier Mining Tracker helps players manage their mining operations with proper bookkeeping practices. Originally designed for Hardcore mode playthroughs with $100,000 starting capital, it supports all game modes and provides comprehensive transaction tracking, inventory management, production logging, and financial analysis.

## What's New in v0.1.0

### 🆕 New Features

- **Ledger to Inventory Sync**: Sync button scans Ledger for ore/oil sales and decrements inventory quantities with confirmation dialog
- **Vehicle Fuel Tracking**: Track fuel consumption by vehicle in ROI Tracker with costs and transaction counts
- **Production → Ledger Integration**: Option to record sales directly to Ledger when logging production (sells immediately, skips inventory)
- **Daily Summary/Journal**: Dashboard section showing day's activities, income/expenses, and personal notes for each game day
- **Equipment Maintenance Tracking**: Log repairs, parts replacement, and scheduled service with costs in ROI Tracker
- **Export Reports**: Comprehensive export dialog with options for Ledger, Summary, Inventory, ROI, and Full Report exports
- **Undo/Redo Transactions**: Undo button in Ledger with Ctrl+Z/Ctrl+Y support for add and delete actions

## Features

### 📊 Dashboard
- **Financial Summary**: Net Worth, Company Balance, Personal Balance, Transaction Count
- **Oil Lifetime Progress**: Track progress toward the 10,000 oil cap with visual progress bar
- **ROI Performance Highlights**: Top performer, total profit, success rate
- **📓 Daily Journal** *(NEW)*: 
  - Date navigation with Prev/Next/Today buttons
  - Day's activities table (from Ledger and Production)
  - Daily income, expenses, and net totals
  - Personal notes with save functionality
- **Recent Activity**: Last 5 transactions with amounts, accounts, and running balances
- **Quick Actions**: Jump to Add Transaction, ROI Tracker, Budget Planner, or Inventory
- **Day Counter**: Track in-game days elapsed

### 📒 Ledger Tab
- **Opening Balance**: Configurable starting capital (Hardcore: $100,000)
- **Transaction Types**: Purchase, Sale, Transfer, Fuel
- **Vehicle Tracking**: Select vehicle for Fuel transactions *(NEW)*
- **↩️ Undo / ↪️ Redo** *(NEW)*: Revert or redo add/delete actions with history
- **Row Color Coding**:
  - Sale: Light green
  - Purchase: Light red
  - Transfer: Light blue
  - Fuel: Light orange
  - Opening: Light gray
- **In-Game Dates**: Uses game date from Settings (not real date)
- **Auto-Calculation**: 
  - Income/expense split based on account and item type
  - 10% Personal / 90% Company split for raw ore and refined oil sales
- **Skill Discounts**: Vendor Negotiation (0-7) and Investment Forecasting (0-6)
- **Bulk Pricing Logic**: Single unit rounds UP, bulk uses exact calculation
- **Running Balances**: Automatic Personal and Company balance tracking
- **Import/Export**: CSV and Excel support

### 📦 Reference Data Tab
Six sub-tabs for comprehensive game data:
- **Items**: 500+ items with buy/sell prices, categories, and trading rules
- **Factory Equipment**: Workbenches and production facilities
- **Vehicles**: All vehicles with specs and pricing (68 vehicles)
- **Buildings**: Construction elements and structures
- **Recipes**: 121 crafting recipes organized by workbench
- **Locations**: Game locations and trading posts

### 🏭 Production Tab
Three sub-tabs for production management:
- **Calculator**: Recipe cost/profit analysis
- **Log**: Track production runs with inventory integration
  - Concrete quality selector (Rough/Standard/Polished)
  - Deduct inputs from inventory option
  - Add outputs to inventory option
  - **📒 Record sale to Ledger** *(NEW)*: Sell production directly without adding to inventory
- **Cost Analysis**: Production profitability reports

### 📦 Inventory Tab
- **Summary Dashboard**: Total items, total value, low stock alerts
- **Filterable Inventory Table**: Search, filter by category, stock status
- **🔄 Sync from Ledger** *(NEW)*: Auto-decrement quantities based on sales
- **30 Categories**: Matching all in-game categories exactly
  - Resources: Ore, Fluids, Dirt, Rock, Wood
  - Materials: Ore (bars), Concrete, Sub Parts, Fuel, Metals, Wood
  - Equipment: Batteries, ECUs, Filters, Hoses, Injectors, Pumps, Rams, Sensors, Sub Parts, Turbos, Wearparts
  - Buildings: Steel, Steel Doors, Steel Mesh, Concrete (3 qualities), Wood, Quest buildings
- **Oil Lifetime Cap Tracker**: Configurable cap with progress monitoring
- **Stock Status**: Color-coded (Good/Low/Critical/Out)
- **Reference Data Integration**: Prices pulled from Items tab

### 🚚 Material Movement Tab
- **Session Types**: Hauling and Processing
- **Active Session Tracking**: Start/stop timer, automatic duration
- **Vehicle Integration**: Auto-fill specs from Reference Data
- **Ore Extraction Tracking**: For processing sessions
- **Revenue Calculations**: Based on current prices

### 📈 ROI Tracker
- **Investment Tracking**: Track return on investment for equipment and vehicles
- **⛽ Fuel Tab** *(NEW)*: View fuel costs by vehicle from Ledger
- **🔧 Maintenance Tab** *(NEW)*: 
  - Log repairs, parts replacement, scheduled service
  - Track costs per equipment
  - Maintenance types: Repair, Parts Replacement, Scheduled Service, Inspection, Upgrade, Other
- **Performance Metrics**: Profitability analysis and ROI calculations

### 💰 Budget Planner Tab
- **Equipment Planning**: Plan workbench and tool purchases
- **Facility Planning**: Plan building and infrastructure investments
- **Cost Projections**: Total costs with skill discounts applied

### ⚙️ Settings Tab
- **Game Dates**: Game Start Date and Current Game Date
- **Skill Levels**: Vendor Negotiation (0-7), Investment Forecasting (0-6)
- **Oil Lifetime Cap**: Configurable limit (default 10,000)
- **Game Mode**: Hardcore/Standard/Creative

### 🔍 Auditor Tab
- Save file parsing and verification
- Compare tracker data against game saves

### 📤 Export Reports *(NEW)*
Access via File → Export to Excel (Ctrl+E):
- **Ledger Export**: All transactions to CSV/Excel with date filtering
- **Summary Report**: Income/expenses grouped by day, week, or month
- **Inventory Export**: Current stock levels with values
- **ROI Export**: Investment data with maintenance and fuel costs
- **Full Report**: Multi-sheet Excel workbook with all data

## Game Mechanics Supported

### Account System
- **Personal Account**: Day-to-day operations, starting capital
- **Company Account**: Long-term savings, carries over between playthroughs

### Income Split (Personal Account Sales)
| Item Type | Personal | Company |
|-----------|----------|---------|
| Raw Ores (Resources - Ore) | 10% | 90% |
| Refined Oil (Resources - Fluids) | 10% | 90% |
| Everything Else | 100% | 0% |

### Skill Discounts
- **Vendor Negotiation (VN)**: 0-7 levels, 0.5% per level on ALL items
- **Investment Forecasting (IF)**: 0-6 levels, 0.5% per level on VEHICLES only
- Maximum combined discount on vehicles: 6.5%

### Concrete Quality Tiers
- **Rough Concrete**: Lower sell prices
- **Standard Concrete**: Base prices
- **Polished Concrete**: Higher sell prices

### Pricing
- **Buy Price**: Whole numbers
- **Sell Price**: Decimals for bulk pricing (e.g., $66.50 for Oil)
- **Transactions**: Whole number totals (game rounds appropriately)

## Installation

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)

### Setup

1. Clone or download the repository

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python main.py
```

## Requirements

```
PyQt6>=6.4.0
pandas>=1.5.0
openpyxl>=3.0.0
```

## Project Structure

```
frontier_mining_tracker/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── FUTURE_UPDATES.md      # Planned features
├── config/
│   ├── settings.py        # App configuration
│   └── item_codes.py      # Game item codes
├── core/
│   ├── database.py        # SQLite database operations
│   ├── models.py          # Data models
│   ├── calculations.py    # Financial calculations
│   └── session_manager.py # Session state management
├── importers/
│   └── excel_importer.py  # Excel/CSV import functionality
├── ui/
│   ├── main_window.py     # Main application window
│   ├── dialogs/
│   │   ├── tools_dialogs.py
│   │   └── export_dialog.py  # Export reports dialog
│   └── tabs/
│       ├── dashboard_tab.py
│       ├── ledger_tab.py
│       ├── reference_tab.py
│       ├── production_tab.py
│       ├── inventory_tab.py
│       ├── material_movement_tab.py
│       ├── roi_tracker_tab.py
│       ├── budget_planner_tab.py
│       ├── auditor_tab.py
│       ├── settings_tab.py
│       ├── recipes_subtab.py
│       ├── vehicles_subtab.py
│       ├── factory_subtab.py
│       ├── buildings_subtab.py
│       └── locations_subtab.py
├── auditor/
│   └── save_parser.py     # Game save file parsing
├── resources/
│   └── icons/             # Application icons
├── utils/                 # Utility functions
├── sessions/              # Session save files
└── data/
    └── frontier_mining.db # SQLite database (created on first run)
```

## Usage

### Getting Started

1. **Import Reference Data**: 
   - Go to Reference Data → Items tab
   - Click "Import Excel" and select your Price Tables file
   - This populates item prices for auto-complete and calculations

2. **Set Game Date**:
   - Go to Settings tab
   - Set Game Start Date (default: April 22, 2021)
   - Update Current Game Date as you play

3. **Configure Opening Balance**:
   - In Ledger tab, set Personal Balance (default $100,000 for Hardcore)
   - Set Company Balance if carrying over from previous game

### Recording Transactions

1. Click "Add Transaction" in Ledger tab
2. Select transaction type (Purchase/Sale/Transfer/Fuel)
3. For Fuel, select vehicle from dropdown
4. Type item name (autocomplete from Reference Data)
5. Category and price auto-fill
6. Adjust quantity as needed
7. Select Account (Personal/Company)
8. Click OK

### Tracking Production

1. Go to Production → Log tab
2. Select building (workbench)
3. For Concrete Mixer, select quality tier
4. Choose recipe and quantity
5. Options:
   - "Deduct inputs from inventory" - reduces input materials
   - "Add outputs to inventory" - adds produced items to stock
   - "Record sale to Ledger" - sells directly (skips inventory)
6. Click "Log Production"

### Managing Inventory

1. Go to Inventory tab
2. Use "Add Item" or let Production tab auto-add
3. Use "Sync from Ledger" to auto-decrement sold items
4. Filter by category or stock status
5. Monitor Oil Lifetime Cap progress

### Exporting Reports

1. Go to File → Export to Excel (Ctrl+E)
2. Select report type:
   - **Ledger**: All transactions with optional date filter
   - **Summary**: Financial summary by period
   - **Inventory**: Current stock snapshot
   - **ROI**: Investment and maintenance data
   - **Full Report**: Everything in one Excel workbook
3. Choose file location and export

### Using Undo/Redo

- **Undo**: Click ↩️ Undo button or press Ctrl+Z
- **Redo**: Click ↪️ Redo button or press Ctrl+Y
- Supports undoing: Add transaction, Delete transaction
- Up to 50 actions in history

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+N | New Transaction |
| Ctrl+S | Save Session |
| Ctrl+O | Load Session |
| Ctrl+E | Export Reports |
| Ctrl+Z | Undo |
| Ctrl+Y | Redo |
| Ctrl+1-9 | Navigate to tabs |
| Delete | Delete selected item |

## Data Files

The application can import Excel files with these sheets:

### Price Tables (Dashboard file)
| Column | Description |
|--------|-------------|
| Item Name | Name of the item |
| Category | Item category |
| Buy Price | Purchase price |
| Sell Price | Sale price (bulk rate) |

### Ledger Import
| Column | Description |
|--------|-------------|
| Date | Transaction date (in-game) |
| Type | Purchase/Sale/Transfer/Fuel |
| Item | Item name |
| Category | Item category |
| Qty | Quantity |
| Unit Price | Price per unit |

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- **Out of Ore** game developers for creating an engaging mining simulation
- The Out of Ore community for documenting game mechanics

## Disclaimer

This is a fan-made tool and is not affiliated with or endorsed by the developers of Out of Ore.

---

## Version History

### v0.1.0 (2024-11-30)
- ✅ Ledger to Inventory Sync
- ✅ Vehicle Fuel Tracking
- ✅ Production Log → Ledger Integration
- ✅ Daily Summary/Journal
- ✅ Equipment Maintenance Tracking
- ✅ Export Reports
- ✅ Undo/Revert Last Transaction
- 🔧 Fixed Built Filter Kit recipe name
- 🔧 Fixed Materials - Sub Parts sell prices
- 🔧 Standardized all date fields to use in-game dates
- 🔧 ROI Tracker layout optimization
