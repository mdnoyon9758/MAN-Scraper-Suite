#!/usr/bin/env python3
"""
Universal Scraping Engine
Handles crawling and data extraction across different platforms
Supports static, dynamic, and JS-heavy websites
"""

import asyncio
import requests
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from typing import Optional, List, Dict, Any
import time

class UniversalScraper:
    """A powerful web scraping engine."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    async def scrape_with_playwright(self, url: str) -> str:
        """Scrape a webpage using Playwright for JS-heavy content"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.config['scraping']['headless'])
            page = await browser.new_page()
            await page.goto(url, timeout=self.config['scraping']['timeout'] * 1000)
            content = await page.content()
            await browser.close()
            return content

    def scrape_with_requests(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Scrape static or simple websites using requests and BeautifulSoup"""
        results = []
        
        # Get user agent from config
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        if 'scraping' in self.config and 'user_agent' in self.config['scraping']:
            user_agent = self.config['scraping']['user_agent']
        
        headers = {'User-Agent': user_agent}
        delay = self.config.get('scraping', {}).get('delay', 1.0)
        timeout = self.config.get('scraping', {}).get('timeout', 30)
        
        for url in urls:
            try:
                # Add delay between requests
                if len(results) > 0:
                    time.sleep(delay)
                
                response = requests.get(url, headers=headers, timeout=timeout)
                response.raise_for_status()
                
                # Parse with BeautifulSoup
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract basic information
                title = soup.find('title')
                title_text = title.get_text().strip() if title else ''
                
                # Extract all text content
                body = soup.find('body')
                body_text = body.get_text().strip() if body else soup.get_text().strip()
                
                results.append({
                    'url': url,
                    'title': title_text,
                    'text': body_text,
                    'status_code': response.status_code
                })
                
            except Exception as e:
                results.append({
                    'url': url,
                    'error': str(e),
                    'title': '',
                    'text': ''
                })
        
        return results

    async def run(self, url: str, dynamic: bool = False) -> Dict[str, Any]:
        """Run the scraper for a given URL"""
        if dynamic:
            content = await self.scrape_with_playwright(url)
            # Parse with BeautifulSoup for consistency
            soup = BeautifulSoup(content, 'html.parser')
            title = soup.find('title')
            title_text = title.get_text().strip() if title else ''
            body = soup.find('body')
            body_text = body.get_text().strip() if body else soup.get_text().strip()
            
            return {
                'url': url,
                'title': title_text,
                'text': body_text,
                'content': content
            }
        else:
            results = self.scrape_with_requests([url])
            return results[0] if results else {'url': url, 'error': 'No data scraped'}

    def run_multiple(self, urls: List[str], dynamic: bool = False) -> List[Dict[str, Any]]:
        """Run the scraper for multiple URLs"""
        if dynamic:
            return [asyncio.run(self.run(url, dynamic)) for url in urls]
        else:
            return self.scrape_with_requests(urls)

    def fetch_content(self, url: str, dynamic: bool = False) -> Optional[Dict[str, Any]]:
        """Fetch content from URL"""
        return asyncio.run(self.run(url, dynamic))

    def fetch_urls_content(self, urls: List[str], dynamic: bool = False) -> List[Optional[Dict[str, Any]]]:
        """Fetch content from multiple URLs"""
        return self.run_multiple(urls, dynamic)

# The engine can be further extended with more features like CAPTCHA solving,
# detailed data extraction rules, error handling, and more.
