"""
Initialize the scrapers package
"""

from .web_scraper import WebScraper

# Optional social media imports
try:
    from .social_scraper import TwitterScraper, RedditScraper
except ImportError:
    TwitterScraper = RedditScraper = None

__all__ = ["WebScraper", "TwitterScraper", "RedditScraper"]
