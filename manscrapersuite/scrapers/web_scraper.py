#!/usr/bin/env python3
"""
Web Scraper
Handles scraping for general web pages, PDFs, and images
"""

from typing import List, Dict, Any, Optional
import scrapy
from ..core.engine import UniversalScraper

import random
from urllib.parse import urlparse, urljoin
import requests

class WebScraper:
    """
    Enhanced web scraping class with support for URL validation,
    SPAs, and anti-detection measures
    """
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.2 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
    ]

    def validate_url(self, url: str) -> Optional[str]:
        """
        Validate and correct URL if needed
        """
        parsed = urlparse(url)
        if not parsed.scheme:
            url = 'https://' + url
        if urlparse(url).hostname:
            return url
        return None

    def fetch_html(self, url: str, dynamic: bool = False) -> Optional[str]:
        """
        Fetch HTML content, using dynamic methods if required
        """
        # Rotate user-agent
        headers = {'User-Agent': random.choice(self.user_agents)}

        if dynamic:
            # Placeholder for Selenium/Playwright
            return self.engine.fetch_using_selenium(url)
        else:
            response = requests.get(url, headers=headers, proxies=self.get_random_proxy())
            if response.status_code == 200:
                return response.content
        return None

    def get_random_proxy(self) -> Optional[Dict[str, str]]:
        """
        Fetch random proxy from the configured list
        """
        proxies = self.config.get('proxies', [])
        if proxies:
            return {'http': random.choice(proxies)}
        return None

    def __init__(self, config: Dict[str, Any]):
        self.config = config    
        self.engine = UniversalScraper(config)

    def scrape_page(self, url: str, dynamic: bool = False) -> Optional[Dict[str, Any]]:
        """
        Scrape a single webpage
        """
        valid_url = self.validate_url(url)
        if not valid_url:
            print(f"Invalid URL: {url}")
            return None

        content = self.fetch_html(valid_url, dynamic)
        if content:
            return {'url': valid_url, 'content': content}
        return None

    def scrape_multiple_pages(self, urls: List[str], dynamic: bool = False) -> List[Optional[Dict[str, Any]]]:
        """
        Scrape multiple web pages
        """
        return self.engine.fetch_urls_content(urls, dynamic)

    def scrape_images(self, url: str) -> List[Dict[str, str]]:
        """
        Scrape images from the webpage
        """
        class ImageSpider(scrapy.Spider):
            name = 'imagespider'
            start_urls = [url]

            def parse(self, response):
                for img in response.css('img::attr(src)').getall():
                    yield {'image_url': response.urljoin(img)}

        # Use basic requests to find image URLs
        import requests
        from bs4 import BeautifulSoup
        
        try:
            response = requests.get(url, timeout=self.config.get('scraping', {}).get('timeout', 30))
            soup = BeautifulSoup(response.content, 'html.parser')
            
            images = []
            for img in soup.find_all('img'):
                src = img.get('src')
                if src:
                    if not src.startswith('http'):
                        # Handle relative URLs
                        from urllib.parse import urljoin
                        src = urljoin(url, src)
                    images.append({'image_url': src})
            
            return images
        except Exception as e:
            print(f"Error scraping images from {url}: {e}")
            return []

    def scrape_pdfs(self, url: str) -> List[Dict[str, str]]:
        """
        Scrape PDFs from the webpage
        """
        class PdfSpider(scrapy.Spider):
            name = 'pdfspider'
            start_urls = [url]

            def parse(self, response):
                for pdf in response.css('a::attr(href)').re(r'.pdf$'):
                    yield {'pdf_url': response.urljoin(pdf)}

        # Use basic requests to find PDF URLs
        import requests
        from bs4 import BeautifulSoup
        
        try:
            response = requests.get(url, timeout=self.config.get('scraping', {}).get('timeout', 30))
            soup = BeautifulSoup(response.content, 'html.parser')
            
            pdfs = []
            # Find all links that end with .pdf
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.lower().endswith('.pdf'):
                    if not href.startswith('http'):
                        # Handle relative URLs
                        from urllib.parse import urljoin
                        href = urljoin(url, href)
                    pdfs.append({'pdf_url': href})
            
            return pdfs
        except Exception as e:
            print(f"Error scraping PDFs from {url}: {e}")
            return []

