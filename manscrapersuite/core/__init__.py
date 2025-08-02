"""
Core module for OmniScraper
Contains the main engine and configuration management
"""

from .engine import UniversalScraper
from .config import Config

__all__ = ["UniversalScraper", "Config"]
