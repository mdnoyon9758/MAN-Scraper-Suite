"""
Stealth package for OmniScraper
Handles proxy rotation, user-agent spoofing, and anti-detection
"""

from .proxy_manager import ProxyManager
from .stealth_engine import StealthEngine

__all__ = ["ProxyManager", "StealthEngine"]
