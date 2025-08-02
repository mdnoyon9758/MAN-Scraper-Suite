#!/usr/bin/env python3
"""
Web Scraper
Handles scraping for general web pages, PDFs, and images
"""

from typing import List, Dict, Any, Optional
import scrapy
from ..core.engine import UniversalScraper

class WebScraper:
    """
    General web scraping class, supports static and dynamic pages
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config    
        self.engine = UniversalScraper(config)

    def scrape_page(self, url: str, dynamic: bool = False) -> Optional[Dict[str, Any]]:
        """
        Scrape a single webpage
        """
        return self.engine.fetch_content(url, dynamic)

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

