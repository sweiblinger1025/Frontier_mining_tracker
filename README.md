# Frontier Mining Tracker

A desktop application for tracking mining operations in the game **Out of Ore**. Built with Python and PyQt6.

![Version](https://img.shields.io/badge/version-0.1.0-blue)
![Python](https://img.shields.io/badge/python-3.10+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

## Overview

Frontier Mining Tracker helps players manage their mining operations with proper bookkeeping practices. Originally designed for Hardcore mode playthroughs, it supports all game modes and provides comprehensive transaction tracking, reference data management, and financial analysis.

## Features

### Reference Data Tab
- **Item Database**: 500+ items with buy/sell prices, categories, and trading rules
- **Skill Discounts**: Vendor Negotiation (VN) and Investment Forecasting (IF) discount calculations
- **Bulk Pricing**: Supports decimal unit prices for bulk sales (qty ≥ 2)
- **Editable Rules**: Can Buy/Can Sell permissions editable per item
- **Search & Filter**: Find items quickly by name, category, or properties
- **Import Support**: Import from Excel (.xlsx) or CSV files

### Ledger Tab
- **Opening Balance**: Configurable starting capital for any game mode
  - Hardcore: $100,000
  - Standard: Any amount
  - Creative: N/A (not tracked)
- **Transaction Types**: Purchase, Sale, Transfer, Opening
- **Auto-Calculation**: 
  - Income/expense split based on account and item type
  - 10% Personal / 90% Company split for raw ore and refined oil sales
- **Bulk Pricing Logic**: 
  - Single unit (qty=1): Rounds UP
  - Bulk (qty≥2): Exact calculation
- **Running Balances**: Automatic Personal and Company balance tracking
- **Import/Export**: CSV and Excel support

### Coming Soon
- Dashboard (financial overview)
- Auditor (save file verification)
- ROI Tracker
- Inventory Management
- Material Movement
- Budget Planner
- Locations
- Settings

## Game Mechanics Supported

### Account System
- **Personal Account**: Day-to-day operations, starting capital
- **Company Account**: Long-term savings for map expansions, carries over between playthroughs

### Income Split (Personal Account Sales)
When selling through the Personal account:
| Item Type | Personal | Company |
|-----------|----------|---------|
| Raw Ores (Resources - Ore) | 10% | 90% |
| Refined Oil (Resources - Fluids) | 10% | 90% |
| Everything Else | 100% | 0% |

### Skill Discounts
- **Vendor Negotiation (VN)**: 0-7 levels, 0.5% per level on ALL items
- **Investment Forecasting (IF)**: 0-6 levels, 0.5% per level on VEHICLES only
- Maximum combined discount on vehicles: 6.5%

### Pricing
- **Buy Price**: Whole numbers
- **Sell Price**: Decimals for bulk pricing (e.g., $66.50 for Oil)
- **Transactions**: Whole number totals (game rounds appropriately)

## Installation

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/frontier-mining-tracker.git
cd frontier-mining-tracker
```

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
├── config/
│   ├── settings.py        # App configuration
│   └── item_codes.py      # Game item codes
├── core/
│   ├── database.py        # SQLite database operations
│   ├── models.py          # Data models
│   └── calculations.py    # Financial calculations
├── importers/
│   └── excel_importer.py  # Excel/CSV import functionality
├── ui/
│   ├── main_window.py     # Main application window
│   └── tabs/
│       ├── reference_tab.py  # Reference Data tab
│       └── ledger_tab.py     # Ledger tab
├── auditor/               # Save file auditing (coming soon)
├── resources/
│   └── icons/             # Application icons
├── utils/                 # Utility functions
└── data/
    └── frontier_mining.db # SQLite database (created on first run)
```

## Usage

### Importing Data

1. **Reference Data**: 
   - Go to Reference Data tab
   - Click "Import Excel" or "Import CSV"
   - Select your Price Tables file

2. **Existing Ledger**:
   - Go to Ledger tab
   - Click "Import"
   - Select your Excel file with a "Ledger" sheet

### Recording Transactions

1. Click "Add Transaction"
2. Select transaction type (Purchase/Sale/Transfer)
3. Type item name (autocomplete available)
4. Category and price auto-fill from Reference Data
5. Adjust quantity as needed
6. Select Account (Personal/Company)
7. Click OK

### Opening Balance

- Set your starting capital in the Opening Balance section
- Personal Balance: Your chosen starting amount
- Company Balance: Carryover from previous playthroughs (or $0)

## Data Files

The application expects Excel files with the following sheets:

### Price Tables (Dashboard file)
| Column | Description |
|--------|-------------|
| Item Name | Name of the item |
| Category | Item category |
| Buy Price | Purchase price |
| Sell Price | Sale price (bulk rate) |

### Item Rules (Tracker file)
| Column | Description |
|--------|-------------|
| Item Name | Name of the item |
| Category | Item category |
| Can Purchase? | Yes/No |
| Can Sell? | Yes/No |

### Ledger
| Column | Description |
|--------|-------------|
| Date | Transaction date |
| Type | Purchase/Sale/Transfer/Opening |
| Item | Item name |
| Category | Item category |
| Qty | Quantity |
| Unit Price | Price per unit |
| ... | (additional columns) |

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- **Out of Ore** game developers for creating an engaging mining simulation
- The Out of Ore community for documenting game mechanics

## Disclaimer

This is a fan-made tool and is not affiliated with or endorsed by the developers of Out of Ore.
