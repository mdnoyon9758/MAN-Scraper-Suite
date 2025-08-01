#!/usr/bin/env python3
"""
Smart Filter Module for MAN Scraper Suite
Provides intelligent data filtering capabilities
"""

import re
from typing import List, Dict, Any

class SmartFilter:
    """Intelligent data filtering engine"""

    def __init__(self):
        print("✅ SmartFilter initialized")

    def filter_based_on_keywords(self, data: List[Dict[str, Any]], include_keywords: List[str], exclude_keywords: List[str]) -> List[Dict[str, Any]]:
        """Filter data based on inclusion and exclusion keywords"""
        if not data:
            return []

        filtered_data = []
        include_keywords = [kw.lower() for kw in include_keywords]
        exclude_keywords = [kw.lower() for kw in exclude_keywords]

        for item in data:
            text = (item.get('title', '') + ' ' + item.get('content', '')).lower()

            # Include logic
            if include_keywords and not any(kw in text for kw in include_keywords):
                continue

            # Exclude logic
            if any(kw in text for kw in exclude_keywords):
                continue

            filtered_data.append(item)

        return filtered_data

    def filter_based_on_regex(self, data: List[Dict[str, Any]], include_patterns: List[str], exclude_patterns: List[str]) -> List[Dict[str, Any]]:
        """Filter data using regex patterns"""
        if not data:
            return []

        filtered_data = []

        for item in data:
            text = item.get('title', '') + ' ' + item.get('content', '')

            # Include logic
            if include_patterns and not any(re.search(pattern, text) for pattern in include_patterns):
                continue

            # Exclude logic
            if any(re.search(pattern, text) for pattern in exclude_patterns):
                continue

            filtered_data.append(item)

        return filtered_data

    def prioritize_sources(self, data: List[Dict[str, Any]], preferred_sources: List[str]) -> List[Dict[str, Any]]:
        """Prioritize certain data sources"""
        prioritized = []
        non_prioritized = []

        for item in data:
            source = item.get('source', '').lower()
            if source in preferred_sources:
                prioritized.append(item)
            else:
                non_prioritized.append(item)

        return prioritized + non_prioritized
