#!/usr/bin/env python3
"""
Proxy Manager
Handles proxy rotation, Tor integration, and residential proxies
"""

import random
import requests
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import socks
import socket

@dataclass
class Proxy:
    """Proxy configuration data class"""
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    proxy_type: str = "http"  # http, https, socks4, socks5
    
    def to_dict(self) -> Dict[str, str]:
        """Convert proxy to requests-compatible format"""
        if self.proxy_type.lower() in ["http", "https"]:
            if self.username and self.password:
                proxy_url = f"{self.proxy_type}://{self.username}:{self.password}@{self.host}:{self.port}"
            else:
                proxy_url = f"{self.proxy_type}://{self.host}:{self.port}"
            
            return {
                "http": proxy_url,
                "https": proxy_url
            }
        else:
            # SOCKS proxies
            return {
                "http": f"socks5://{self.host}:{self.port}",
                "https": f"socks5://{self.host}:{self.port}"
            }

class ProxyManager:
    """Manages proxy rotation and configuration"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.stealth_config = config["stealth"]
        self.proxies: List[Proxy] = []
        self.current_proxy_index = 0
        self.failed_proxies: List[str] = []
        
        # Initialize proxy lists
        self._load_proxies()
        
        # Tor configuration
        self.tor_proxy = Proxy("127.0.0.1", 9050, proxy_type="socks5")
    
    def _load_proxies(self):
        """Load proxies from configuration or external sources"""
        # This would typically load from a file or API
        # For demo purposes, using some common proxy endpoints
        sample_proxies = [
            Proxy("proxy1.example.com", 8080),
            Proxy("proxy2.example.com", 3128),
            Proxy("proxy3.example.com", 8888, "user", "pass"),
        ]
        
        # In a real implementation, you would:
        # 1. Load from config file
        # 2. Fetch from proxy provider APIs
        # 3. Validate proxy functionality
        self.proxies = sample_proxies
    
    def get_current_proxy(self) -> Optional[Proxy]:
        """Get the current proxy"""
        if not self.proxies:
            return None
        return self.proxies[self.current_proxy_index]
    
    def rotate_proxy(self) -> Optional[Proxy]:
        """Rotate to the next proxy in the list"""
        if not self.proxies:
            return None
        
        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxies)
        return self.proxies[self.current_proxy_index]
    
    def get_random_proxy(self) -> Optional[Proxy]:
        """Get a random proxy from the list"""
        if not self.proxies:
            return None
        return random.choice(self.proxies)
    
    def test_proxy(self, proxy: Proxy, timeout: int = 10) -> bool:
        """Test if a proxy is working"""
        try:
            proxies = proxy.to_dict()
            
            response = requests.get(
                "http://httpbin.org/ip",
                proxies=proxies,
                timeout=timeout
            )
            
            if response.status_code == 200:
                print(f"Proxy {proxy.host}:{proxy.port} is working")
                return True
            else:
                print(f"Proxy {proxy.host}:{proxy.port} returned status {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Proxy {proxy.host}:{proxy.port} failed: {e}")
            return False
    
    def test_all_proxies(self) -> List[Proxy]:
        """Test all proxies and return working ones"""
        working_proxies = []
        
        for proxy in self.proxies:
            if self.test_proxy(proxy):
                working_proxies.append(proxy)
            else:
                self.failed_proxies.append(f"{proxy.host}:{proxy.port}")
        
        print(f"Found {len(working_proxies)} working proxies out of {len(self.proxies)}")
        return working_proxies
    
    def get_tor_proxy(self) -> Proxy:
        """Get Tor proxy configuration"""
        return self.tor_proxy
    
    def is_tor_running(self) -> bool:
        """Check if Tor is running"""
        try:
            # Try to connect to Tor SOCKS port
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex(("127.0.0.1", 9050))
            sock.close()
            return result == 0
        except Exception:
            return False
    
    def get_current_ip(self, proxy: Optional[Proxy] = None) -> Optional[str]:
        """Get current IP address (with or without proxy)"""
        try:
            if proxy:
                proxies = proxy.to_dict()
                response = requests.get("http://httpbin.org/ip", proxies=proxies, timeout=10)
            else:
                response = requests.get("http://httpbin.org/ip", timeout=10)
            
            if response.status_code == 200:
                return response.json().get("origin")
            return None
            
        except Exception as e:
            print(f"Failed to get IP address: {e}")
            return None
    
    def setup_session_with_proxy(self, session: requests.Session, 
                                proxy: Optional[Proxy] = None) -> requests.Session:
        """Configure a requests session with proxy"""
        if not proxy:
            proxy = self.get_current_proxy()
        
        if proxy:
            session.proxies.update(proxy.to_dict())
            print(f"Session configured with proxy: {proxy.host}:{proxy.port}")
        
        return session
    
    def get_proxy_for_requests(self) -> Optional[Dict[str, str]]:
        """Get proxy configuration for requests library"""
        if self.stealth_config["tor_proxy"] and self.is_tor_running():
            return self.tor_proxy.to_dict()
        elif self.stealth_config["proxy_rotation"] and self.proxies:
            if random.random() < 0.3:  # 30% chance to rotate
                self.rotate_proxy()
            current_proxy = self.get_current_proxy()
            return current_proxy.to_dict() if current_proxy else None
        
        return None
    
    def add_proxy(self, host: str, port: int, username: Optional[str] = None, 
                  password: Optional[str] = None, proxy_type: str = "http"):
        """Add a new proxy to the list"""
        proxy = Proxy(host, port, username, password, proxy_type)
        self.proxies.append(proxy)
        print(f"Added proxy: {host}:{port}")
    
    def remove_failed_proxy(self, proxy: Proxy):
        """Remove a failed proxy from the list"""
        if proxy in self.proxies:
            self.proxies.remove(proxy)
            failed_key = f"{proxy.host}:{proxy.port}"
            if failed_key not in self.failed_proxies:
                self.failed_proxies.append(failed_key)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get proxy manager statistics"""
        return {
            "total_proxies": len(self.proxies),
            "current_proxy_index": self.current_proxy_index,
            "failed_proxies": len(self.failed_proxies),
            "tor_available": self.is_tor_running(),
            "current_ip": self.get_current_ip()
        }
