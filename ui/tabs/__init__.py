"""
UI Tabs Module

Contains all tab widgets for the main application.
"""

from ui.tabs.dashboard_tab import DashboardTab
from ui.tabs.reference_tab import ReferenceDataTab, ItemsSubTab
from ui.tabs.ledger_tab import LedgerTab
from ui.tabs.auditor_tab import AuditorTab
from ui.tabs.locations_tab import LocationsTab  # Legacy - kept for backwards compatibility
from ui.tabs.factory_subtab import FactoryEquipmentSubTab
from ui.tabs.vehicles_subtab import VehiclesSubTab
from ui.tabs.buildings_subtab import BuildingsSubTab
from ui.tabs.recipes_subtab import RecipesSubTab
from ui.tabs.locations_subtab import LocationsSubTab
from ui.tabs.material_movement_tab import MaterialMovementTab
from ui.tabs.inventory_tab import InventoryTab
from ui.tabs.settings_tab import SettingsTab
from ui.tabs.budget_planner_tab import BudgetPlannerTab
from ui.tabs.roi_tracker_tab import ROITrackerTab
from ui.tabs.production_tab import ProductionTab

__all__ = [
    "DashboardTab",
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
    "MaterialMovementTab",
    "InventoryTab",
    "SettingsTab",
    "BudgetPlannerTab",
    "ROITrackerTab",
    "ProductionTab",
]
