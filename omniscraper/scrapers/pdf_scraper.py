#!/usr/bin/env python3
"""
PDF Scraper
Handles PDF text extraction and metadata collection
"""

import PyPDF2
import requests
from pathlib import Path
from typing import Dict, Any, Optional, List
from io import BytesIO

class PDFScraper:
    """PDF text extraction and metadata scraper"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.output_dir = Path(config["export"]["output_dir"]) / "pdfs"
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def download_pdf(self, url: str, filename: Optional[str] = None) -> Optional[Path]:
        """Download PDF from URL"""
        try:
            response = requests.get(url, timeout=self.config["scraping"]["timeout"])
            response.raise_for_status()
            
            if not filename:
                filename = url.split("/")[-1]
                if not filename.endswith(".pdf"):
                    filename += ".pdf"
            
            filepath = self.output_dir / filename
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            return filepath
        except Exception as e:
            print(f"Error downloading PDF from {url}: {e}")
            return None
    
    def extract_text(self, pdf_path: Path) -> Dict[str, Any]:
        """Extract text from PDF file"""
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                
                text_pages = []
                for page_num, page in enumerate(reader.pages):
                    text = page.extract_text()
                    text_pages.append({
                        "page": page_num + 1,
                        "text": text.strip()
                    })
                
                # Extract metadata
                metadata = reader.metadata if reader.metadata else {}
                
                return {
                    "file_path": str(pdf_path),
                    "total_pages": len(reader.pages),
                    "metadata": {
                        "title": metadata.get("/Title", ""),
                        "author": metadata.get("/Author", ""),
                        "subject": metadata.get("/Subject", ""),
                        "creator": metadata.get("/Creator", ""),
                        "producer": metadata.get("/Producer", ""),
                        "creation_date": str(metadata.get("/CreationDate", "")),
                        "modification_date": str(metadata.get("/ModDate", ""))
                    },
                    "pages": text_pages,
                    "full_text": "\n".join([page["text"] for page in text_pages])
                }
                
        except Exception as e:
            return {
                "file_path": str(pdf_path),
                "error": f"Failed to extract text: {e}",
                "total_pages": 0,
                "metadata": {},
                "pages": [],
                "full_text": ""
            }
    
    def extract_from_url(self, url: str) -> Dict[str, Any]:
        """Download and extract text from PDF URL"""
        try:
            # Download PDF to memory
            response = requests.get(url, timeout=self.config["scraping"]["timeout"])
            response.raise_for_status()
            
            # Extract text directly from memory
            pdf_file = BytesIO(response.content)
            reader = PyPDF2.PdfReader(pdf_file)
            
            text_pages = []
            for page_num, page in enumerate(reader.pages):
                text = page.extract_text()
                text_pages.append({
                    "page": page_num + 1,
                    "text": text.strip()
                })
            
            # Extract metadata
            metadata = reader.metadata if reader.metadata else {}
            
            return {
                "source_url": url,
                "total_pages": len(reader.pages),
                "metadata": {
                    "title": metadata.get("/Title", ""),
                    "author": metadata.get("/Author", ""),
                    "subject": metadata.get("/Subject", ""),
                    "creator": metadata.get("/Creator", ""),
                    "producer": metadata.get("/Producer", ""),
                    "creation_date": str(metadata.get("/CreationDate", "")),
                    "modification_date": str(metadata.get("/ModDate", ""))
                },
                "pages": text_pages,
                "full_text": "\n".join([page["text"] for page in text_pages])
            }
            
        except Exception as e:
            return {
                "source_url": url,
                "error": f"Failed to extract text from URL: {e}",
                "total_pages": 0,
                "metadata": {},
                "pages": [],
                "full_text": ""
            }
    
    def batch_extract(self, pdf_paths: List[Path]) -> List[Dict[str, Any]]:
        """Extract text from multiple PDF files"""
        results = []
        for pdf_path in pdf_paths:
            result = self.extract_text(pdf_path)
            results.append(result)
        return results
    
    def batch_extract_from_urls(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Extract text from multiple PDF URLs"""
        results = []
        for url in urls:
            result = self.extract_from_url(url)
            results.append(result)
        return results
    
    def search_text(self, pdf_data: Dict[str, Any], search_term: str, case_sensitive: bool = False) -> List[Dict[str, Any]]:
        """Search for text within extracted PDF content"""
        matches = []
        search_term = search_term if case_sensitive else search_term.lower()
        
        for page in pdf_data.get("pages", []):
            page_text = page["text"] if case_sensitive else page["text"].lower()
            if search_term in page_text:
                # Find all occurrences in this page
                lines = page_text.split('\n')
                for line_num, line in enumerate(lines):
                    if search_term in line:
                        matches.append({
                            "page": page["page"],
                            "line": line_num + 1,
                            "text": page["text"].split('\n')[line_num].strip(),
                            "match_term": search_term
                        })
        
        return matches
