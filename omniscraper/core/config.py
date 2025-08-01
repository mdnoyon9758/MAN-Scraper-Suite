#!/usr/bin/env python3
"""
Configuration management for OmniScraper
Handles all settings, API keys, and user preferences
"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

class Config:
    """Central configuration manager for OmniScraper"""
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize configuration with optional config file"""
        self.config_dir = Path.home() / ".omniscraper"
        self.config_dir.mkdir(exist_ok=True)
        
        # Load environment variables
        load_dotenv()
        
        # Default configuration
        self.default_config = {
            "scraping": {
                "delay": 1.0,
                "timeout": 30,
                "retries": 3,
                "concurrent_requests": 8,
                "respect_robots": True,
                "user_agent_rotation": True,
                "headless": True,
                "javascript_enabled": True,
                "cookies_enabled": True,
                "images_enabled": False,
                "css_enabled": False
            },
            "stealth": {
                "proxy_rotation": False,
                "tor_proxy": False,
                "random_delays": True,
                "fake_headers": True,
                "browser_automation": "playwright",  # or "selenium"
                "captcha_solver": "2captcha"
            },
            "export": {
                "default_format": "json",
                "output_dir": "W:\\",
                "filename_template": "{site}_{timestamp}",
                "include_metadata": True,
                "compress_output": False
            },
            "database": {
                "type": None,  # mysql, postgresql, mongodb
                "host": "localhost",
                "port": None,
                "database": "omniscraper",
                "username": None,
                "password": None
            },
            "cloud": {
                "google_drive": {
                    "enabled": False,
                    "folder_id": None,
                    "credentials_file": None
                },
                "dropbox": {
                    "enabled": False,
                    "access_token": None
                }
            },
            "google_sheets": {
                "enabled": True,
                "service_account_file": "./credentials/scraper-467614-c06499213741.json",
                "credentials_file": "./credentials/client_secret.json",
                "spreadsheet_id": None,
                "folder_id": None,
                "auto_create": True,
                "auto_share": False,
                "share_emails": []
            },
            "notifications": {
                "email": {
                    "enabled": False,
                    "smtp_server": "smtp.gmail.com",
                    "smtp_port": 587,
                    "username": None,
                    "password": None,
                    "recipients": []
                },
                "telegram": {
                    "enabled": False,
                    "bot_token": None,
                    "chat_id": None
                }
            },
            "social_media": {
                "twitter": {
                    "api_key": None,
                    "api_secret": None,
                    "access_token": None,
                    "access_token_secret": None,
                    "bearer_token": None
                },
                "reddit": {
                    "client_id": None,
                    "client_secret": None,
                    "user_agent": "OmniScraper/1.0"
                }
            },
            "captcha": {
                "2captcha_api_key": None,
                "anticaptcha_api_key": None
            },
            "ai": {
                "gemini_api_key": None,
                "enabled": True,
                "model": "gemini-1.5-flash",
                "temperature": 0.7,
                "max_tokens": 1000
            },
            "analytics": {
                "enabled": True,
                "dashboard_port": 5000,
                "export_charts": True,
                "anomaly_detection": True
            },
            "compliance": {
                "gdpr_mode": True,
                "data_anonymization": True,
                "audit_logging": True,
                "ethical_scraping": True
            }
        }
        
        # Load configuration
        self.config = self.load_config(config_file)
        
        # Ensure output directory exists
        output_dir = Path(self.config["export"]["output_dir"])
        output_dir.mkdir(parents=True, exist_ok=True)
    
    def load_config(self, config_file: Optional[str] = None) -> Dict[str, Any]:
        """Load configuration from file or environment variables"""
        config = self.default_config.copy()
        
        # Load from config file if provided
        if config_file and Path(config_file).exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                if config_file.endswith(('.yaml', '.yml')):
                    file_config = yaml.safe_load(f)
                else:
                    file_config = json.load(f)
                config = self._merge_configs(config, file_config)
        
        # Load from default config file
        default_config_file = self.config_dir / "config.yaml"
        if default_config_file.exists():
            with open(default_config_file, 'r', encoding='utf-8') as f:
                file_config = yaml.safe_load(f)
                config = self._merge_configs(config, file_config)
        
        # Override with environment variables
        config = self._load_from_env(config)
        
        return config
    
    def _merge_configs(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge configuration dictionaries"""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                base[key] = self._merge_configs(base[key], value)
            else:
                base[key] = value
        return base
    
    def _load_from_env(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Load configuration from environment variables"""
        env_mappings = {
            # Social Media
            "TWITTER_API_KEY": ["social_media", "twitter", "api_key"],
            "TWITTER_API_SECRET": ["social_media", "twitter", "api_secret"],
            "TWITTER_ACCESS_TOKEN": ["social_media", "twitter", "access_token"],
            "TWITTER_ACCESS_TOKEN_SECRET": ["social_media", "twitter", "access_token_secret"],
            "TWITTER_BEARER_TOKEN": ["social_media", "twitter", "bearer_token"],
            "REDDIT_CLIENT_ID": ["social_media", "reddit", "client_id"],
            "REDDIT_CLIENT_SECRET": ["social_media", "reddit", "client_secret"],
            
            # Captcha
            "TWOCAPTCHA_API_KEY": ["captcha", "2captcha_api_key"],
            "ANTICAPTCHA_API_KEY": ["captcha", "anticaptcha_api_key"],
            
            # Database
            "DB_TYPE": ["database", "type"],
            "DB_HOST": ["database", "host"],
            "DB_PORT": ["database", "port"],
            "DB_NAME": ["database", "database"],
            "DB_USER": ["database", "username"],
            "DB_PASSWORD": ["database", "password"],
            
            # Cloud
            "GOOGLE_DRIVE_CREDENTIALS": ["cloud", "google_drive", "credentials_file"],
            "DROPBOX_ACCESS_TOKEN": ["cloud", "dropbox", "access_token"],
            
            # Notifications
            "EMAIL_USERNAME": ["notifications", "email", "username"],
            "EMAIL_PASSWORD": ["notifications", "email", "password"],
            "TELEGRAM_BOT_TOKEN": ["notifications", "telegram", "bot_token"],
            "TELEGRAM_CHAT_ID": ["notifications", "telegram", "chat_id"],
        }
        
        for env_var, config_path in env_mappings.items():
            value = os.getenv(env_var)
            if value:
                # Navigate to the nested config location
                current = config
                for key in config_path[:-1]:
                    current = current[key]
                current[config_path[-1]] = value
        
        return config
    
    def save_config(self, config_file: Optional[str] = None):
        """Save current configuration to file"""
        if not config_file:
            config_file = self.config_dir / "config.yaml"
        
        config_path = Path(config_file)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.config, f, default_flow_style=False, indent=2)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation (e.g., 'scraping.delay')"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Set configuration value using dot notation"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def get_user_agents(self) -> List[str]:
        """Get list of user agents for rotation"""
        user_agents_file = Path(__file__).parent.parent.parent / "config" / "user_agents.txt"
        
        if user_agents_file.exists():
            with open(user_agents_file, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f if line.strip()]
        
        # Default user agents if file doesn't exist
        return [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0"
        ]
    
    def validate_config(self) -> Dict[str, List[str]]:
        """Validate configuration and return any errors or warnings"""
        errors = []
        warnings = []
        
        # Check required directories
        output_dir = Path(self.config["export"]["output_dir"])
        if not output_dir.exists():
            try:
                output_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                errors.append(f"Cannot create output directory: {e}")
        
        # Check social media API keys
        twitter_config = self.config["social_media"]["twitter"]
        if any(twitter_config.values()) and not all([
            twitter_config["api_key"],
            twitter_config["api_secret"]
        ]):
            warnings.append("Twitter API credentials incomplete")
        
        reddit_config = self.config["social_media"]["reddit"]
        if any(reddit_config.values()) and not all([
            reddit_config["client_id"],
            reddit_config["client_secret"]
        ]):
            warnings.append("Reddit API credentials incomplete")
        
        # Check database configuration
        db_config = self.config["database"]
        if db_config["type"] and not all([
            db_config["host"],
            db_config["username"],
            db_config["password"]
        ]):
            warnings.append("Database configuration incomplete")
        
        return {"errors": errors, "warnings": warnings}
    
    def __repr__(self):
        return f"Config(config_dir='{self.config_dir}')"
