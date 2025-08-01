"""
Stealth Engine for User-Agent Spoofing and Anti-Detection
"""

import random
import re
from typing import List, Dict

class StealthEngine:
    """
    Responsible for managing stealth operations like user-agent spoofing
    """

    def __init__(self, config: Dict[str, any]):
        self.config = config
        self.user_agents = config.get("user_agents", [])

    def select_random_user_agent(self) -> str:
        """Select a random User-Agent from the list"""
        if not self.user_agents:
            raise ValueError("User-Agent list is empty.")
        return random.choice(self.user_agents)

    def spoof_request_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Override headers to include a spoofed User-Agent"""
        headers['User-Agent'] = self.select_random_user_agent()
        return headers

    def scrub_data(self, data: str) -> str:
        """Scrub identifiable patterns like IP addresses"""
        return re.sub(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', '[scrubbed]', data)

    def delay_between_requests(self, base_delay: float) -> float:
        """Apply random delay to avoid bot detection"""
        random_wait = random.uniform(0.5, 1.5) * base_delay
        print(f"Delaying {random_wait:.2f} seconds between requests.")
        return random_wait
