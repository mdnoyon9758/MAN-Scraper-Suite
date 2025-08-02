#!/usr/bin/env python3
"""
MAN Scraper Suite - 100% Free Web Scraping & Automation Toolkit
No limits, no paywalls, all premium features unlocked from Day 1

A comprehensive toolkit for ethical data extraction across websites, 
social media, and public APIs with all premium features included.
"""

__version__ = "1.0.0"
__author__ = "MAN Scraper Suite Community"
__license__ = "GPLv3"
__email__ = "community@manscrapersuite.org"

# Core imports for easy access
from .core.engine import UniversalScraper
from .core.config import Config
from .scrapers.web_scraper import WebScraper
from .exporters.data_exporter import DataExporter
from .stealth.proxy_manager import ProxyManager
from .stealth.stealth_engine import StealthEngine

# Optional social media imports
try:
    from .scrapers.social_scraper import TwitterScraper, RedditScraper
except ImportError:
    TwitterScraper = RedditScraper = None

# Make key classes available at package level
__all__ = [
    "UniversalScraper",
    "Config", 
    "WebScraper",
    "TwitterScraper",
    "RedditScraper", 
    "DataExporter",
    "ProxyManager",
    "StealthEngine",
]

# Package metadata
PACKAGE_INFO = {
    "name": "MAN Scraper Suite",
    "version": __version__,
    "description": "100% Free Web Scraping & Automation Toolkit",
    "features": [
        "Universal Scraping Engine (Static + Dynamic JS)",
        "Social Media Scraping (X/Twitter, Reddit, Instagram)",
        "PDF/Image Extraction",
        "Multiple Export Formats (CSV, JSON, Excel, PDF)",
        "Cloud Integration (Drive, Dropbox)",
        "Database Support (MySQL, PostgreSQL, MongoDB)",
        "Automation & Scheduling",
        "Privacy & Stealth (Proxy Rotation, User-Agent Spoofing)",
        "CLI & GUI Interfaces",
        "Mobile Support (Termux/Android)",
    ],
    "license": __license__,
    "repository": "https://github.com/manscrapersuite/manscrapersuite",
    "documentation": "https://manscrapersuite.readthedocs.io/",
}

def get_version():
    """Return the current version of MAN Scraper Suite."""
    return __version__

def get_info():
    """Return package information."""
    return PACKAGE_INFO

def print_banner():
    """Print the MAN Scraper Suite banner."""
    banner = f"""
╔═══════════════════════════════════════════════════════════╗
║                 🔥 MAN SCRAPER SUITE v{__version__} 🔥                 ║
║           100% FREE - NO LIMITS - ALL FEATURES           ║
║                                                           ║
║  Universal Web Scraping & Automation Toolkit             ║
║  ✓ Any Website (Static + Dynamic JS)                     ║
║  ✓ Social Media (X/Twitter, Reddit, Instagram)           ║
║  ✓ PDF/Image Extraction                                   ║
║  ✓ Export to CSV/JSON/Excel/PDF                          ║
║  ✓ Cloud Push (Drive, Dropbox)                           ║
║  ✓ Database Direct (MySQL, PostgreSQL, MongoDB)          ║
║  ✓ Automation & Scheduling                               ║
║  ✓ Privacy & Stealth (Proxies, User-Agent Spoofing)      ║
║  ✓ CLI & GUI Interfaces                                   ║
║  ✓ Mobile Support (Termux/Android)                       ║
║                                                           ║
║  License: {__license__} | Community-Driven | No Paywalls        ║
╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)

# Print banner on import (can be disabled with env var)
import os
if os.getenv("MANSCRAPERSUITE_HIDE_BANNER", "").lower() not in ("1", "true", "yes"):
    print_banner()
