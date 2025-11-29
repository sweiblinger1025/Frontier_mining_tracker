"""
Core module - Database, models, calculations, and session management.
"""

from core.database import get_database
from core.session_manager import SessionManager, SessionDialog

__all__ = [
    "get_database",
    "SessionManager",
    "SessionDialog",
]
