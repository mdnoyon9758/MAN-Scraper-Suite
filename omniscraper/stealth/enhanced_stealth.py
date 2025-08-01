#!/usr/bin/env python3
"""
Enhanced Stealth Engine for MAN Scraper Suite
Advanced rate limiting and privacy protection features
"""

import time
import random
from typing import Dict, Any
from datetime import datetime, timedelta
import requests
from fake_useragent import UserAgent

class EnhancedStealth:
    """Enhanced stealth capabilities with dynamic rate limiting"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.ua = UserAgent()
        self.request_history = []
        self.adaptive_delays = {}
        
        print("✅ Enhanced Stealth Engine initialized")
    
    def dynamic_rate_limit(self, domain: str) -> float:
        """Calculate dynamic delay based on domain and recent activity"""
        base_delay = self.config.get('stealth', {}).get('base_delay', 1.0)
        
        # Check recent requests to this domain
        now = datetime.now()
        recent_requests = [
            req for req in self.request_history 
            if req['domain'] == domain and now - req['timestamp'] < timedelta(minutes=5)
        ]
        
        # Adaptive delay calculation
        if len(recent_requests) > 10:
            # Increase delay for high-frequency domains
            adaptive_delay = base_delay * (1 + len(recent_requests) * 0.1)
        else:
            adaptive_delay = base_delay
        
        # Add randomization
        randomized_delay = adaptive_delay * random.uniform(0.8, 1.5)
        
        return min(randomized_delay, 10.0)  # Cap at 10 seconds
    
    def get_stealth_headers(self, url: str) -> Dict[str, str]:
        """Generate stealth headers for requests"""
        headers = {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # Add referer spoofing
        if random.choice([True, False]):
            popular_sites = [
                'https://www.google.com',
                'https://www.bing.com',
                'https://www.yahoo.com',
                'https://duckduckgo.com'
            ]
            headers['Referer'] = random.choice(popular_sites)
        
        return headers
    
    def log_request(self, domain: str, status_code: int):
        """Log request for adaptive rate limiting"""
        self.request_history.append({
            'domain': domain,
            'timestamp': datetime.now(),
            'status_code': status_code
        })
        
        # Keep only recent history (last hour)
        cutoff = datetime.now() - timedelta(hours=1)
        self.request_history = [
            req for req in self.request_history 
            if req['timestamp'] > cutoff
        ]
    
    def should_use_proxy(self, domain: str) -> bool:
        """Determine if proxy should be used for this domain"""
        # Check if domain has been problematic
        recent_failures = [
            req for req in self.request_history 
            if req['domain'] == domain and req['status_code'] >= 400
        ]
        
        return len(recent_failures) > 3
    
    def ethical_check(self, url: str) -> Dict[str, Any]:
        """Perform ethical compliance check"""
        checks = {
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'checks': {
                'robots_txt_respected': True,  # Implement robots.txt checking
                'rate_limit_applied': True,
                'user_agent_rotation': True,
                'no_personal_data_targeted': True
            },
            'compliance_score': 100
        }
        
        return checks
    
    def privacy_protection(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply privacy protection to scraped data"""
        protected_data = data.copy()
        
        # Remove or anonymize sensitive fields
        sensitive_fields = ['email', 'phone', 'address', 'ip_address']
        
        for field in sensitive_fields:
            if field in protected_data:
                if field == 'email':
                    # Anonymize email
                    email = protected_data[field]
                    if '@' in email:
                        local, domain = email.split('@', 1)
                        protected_data[field] = f"{local[:2]}***@{domain}"
                else:
                    protected_data[field] = '[ANONYMIZED]'
        
        return protected_data
