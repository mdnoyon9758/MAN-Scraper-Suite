#!/usr/bin/env python3
"""
Web Dashboard Module for MAN Scraper Suite
Provides web-based user management interface
"""

__version__ = "1.0.0"
__author__ = "MAN Scraper Suite Community"

from .web_dashboard import WebDashboard
from .dashboard_server import DashboardServer

__all__ = ['WebDashboard', 'DashboardServer']
