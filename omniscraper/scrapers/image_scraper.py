#!/usr/bin/env python3
"""
Image Scraper
Handles bulk image downloading and renaming
"""

import os
import requests
from pathlib import Path
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse

class ImageScraper:
    """
    Image downloading and renaming class
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.output_dir = Path(config['export']['output_dir']) / "images"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def download_image(self, url: str, rename: Optional[str] = None) -> Optional[Path]:
        """
        Download an image and optionally rename it
        """
        try:
            response = requests.get(url, stream=True, timeout=self.config['scraping']['timeout'])
            response.raise_for_status()

            # Determine filename
            if rename:
                filename = f"{rename}.jpg"
            else:
                filename = os.path.basename(urlparse(url).path)

            filepath = self.output_dir / filename
            with open(filepath, 'wb') as file:
                for chunk in response.iter_content(1024):
                    if not chunk:
                        break
                    file.write(chunk)

            return filepath
        except Exception as e:
            print(f"Error downloading image from {url}: {e}")
            return None

    def bulk_download(self, urls: List[str]) -> List[Dict[str, Any]]:
        """
        Bulk download images from a list of URLs
        """
        results = []
        for index, url in enumerate(urls):
            rename = f"image_{index:03d}"  # Optional renaming format
            filepath = self.download_image(url, rename=rename)
            if filepath:
                results.append({
                    "url": url,
                    "file_path": str(filepath)
                })
        return results

    def scrape_and_download(self, page_url: str) -> List[Dict[str, Any]]:
        """
        Scrape a webpage for images, then download them
        """
        response = requests.get(page_url)
        image_urls = self.extract_image_urls(response.text)
        return self.bulk_download(image_urls)

    @staticmethod
    def extract_image_urls(html: str) -> List[str]:
        """
        Extract image URLs from HTML content
        """
        # This is a simple example and may need more complex parsing
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, 'html.parser')
        return [img['src'] for img in soup.find_all('img') if 'src' in img.attrs]


