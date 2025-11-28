"""
UI Tabs Module

Contains all tab widgets for the main application.
"""

from ui.tabs.reference_tab import ReferenceDataTab, ItemsSubTab
from ui.tabs.ledger_tab import LedgerTab
from ui.tabs.auditor_tab import AuditorTab
from ui.tabs.locations_tab import LocationsTab  # Legacy - kept for backwards compatibility
from ui.tabs.factory_subtab import FactoryEquipmentSubTab
from ui.tabs.vehicles_subtab import VehiclesSubTab
from ui.tabs.buildings_subtab import BuildingsSubTab
from ui.tabs.recipes_subtab import RecipesSubTab
from ui.tabs.locations_subtab import LocationsSubTab

__all__ = [
    "ReferenceDataTab",
    "ItemsSubTab",
    "LedgerTab",
    "AuditorTab",
    "LocationsTab",  # Legacy
    "LocationsSubTab",
    "FactoryEquipmentSubTab",
    "VehiclesSubTab",
    "BuildingsSubTab",
    "RecipesSubTab",
]
