"""
API package for the real estate intake agent.

This package provides FastAPI routes for handling text mode interactions
and mode switching between text and voice modes.
"""
from .routes import router

__all__ = ["router"]
