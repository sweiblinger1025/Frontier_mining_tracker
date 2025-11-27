"""
Application Settings and Configuration
"""

import os
from pathlib import Path


# Application Info
APP_NAME = "Frontier Mining Tracker"
APP_VERSION = "0.1.0"
APP_AUTHOR = "Your Name"

# Paths
APP_DIR = Path(__file__).parent.parent
DATA_DIR = APP_DIR / "data"
RESOURCES_DIR = APP_DIR / "resources"

# Database
DATABASE_NAME = "frontier_mining.db"
DATABASE_PATH = DATA_DIR / DATABASE_NAME

# Window Settings
WINDOW_MIN_WIDTH = 1200
WINDOW_MIN_HEIGHT = 800
WINDOW_DEFAULT_WIDTH = 1400
WINDOW_DEFAULT_HEIGHT = 900

# Game Settings (defaults, can be overridden)
STARTING_CAPITAL = 100000
GAME_START_DATE = "2021-04-22"

# Ensure data directory exists
def ensure_directories():
    """Create necessary directories if they don't exist."""
    DATA_DIR.mkdir(exist_ok=True)


# Tab Configuration - defines the order and names of tabs
TABS = [
    ("Dashboard", "dashboard"),
    ("Ledger", "ledger"),
    ("Reference Data", "reference"),         # Combined Price Tables + Item Rules
    ("Auditor", "auditor"),
    ("ROI Tracker", "roi_tracker"),
    ("Inventory", "inventory"),
    ("Material Movement", "material"),
    ("Budget Planner", "budget_planner"),
    ("Locations", "locations"),
    ("Settings", "settings"),
]

# Future tabs to add (from spreadsheets):
# - Story Templates (challenge mode narrative messages)
# - Vehicle Specs (detailed vehicle specifications)
