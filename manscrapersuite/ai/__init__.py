#!/usr/bin/env python3
"""
AI Integration Module for MAN Scraper Suite
Provides AI-powered data filtering, analysis, and insights
"""

__version__ = "1.0.0"
__author__ = "MAN Scraper Suite Community"

from .ai_engine import AIEngine
from .data_analyzer import DataAnalyzer
from .smart_filter import SmartFilter

__all__ = ['AIEngine', 'DataAnalyzer', 'SmartFilter']
