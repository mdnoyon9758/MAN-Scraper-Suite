#!/usr/bin/env python3
"""
GUI Main Launcher for OmniScraper
Provides a graphical user interface using tkinter
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import webbrowser
from pathlib import Path
from typing import Dict, Any

from ..core.config import Config
from ..scrapers.web_scraper import WebScraper
from ..scrapers.social_scraper import TwitterScraper, RedditScraper
from ..scrapers.pdf_scraper import PDFScraper
from ..scrapers.image_scraper import ImageScraper
from ..exporters.data_exporter import DataExporter
from ..automation.notifications import NotificationManager
from ..stealth.proxy_manager import ProxyManager

class OmniScraperGUI:
    """Main GUI class for OmniScraper"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🔥 MAN Scraper Suite - 100% Free Web Scraping Toolkit")
        self.root.geometry("1000x700")
        self.root.configure(bg='#2b2b2b')
        
        # Initialize configuration
        self.config = Config()
        
        # Create GUI elements
        self.create_widgets()
        self.create_menu()
        
        # Status variables
        self.is_scraping = False
        
    def create_menu(self):
        """Create the menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Config", command=self.open_config)
        file_menu.add_command(label="Save Config", command=self.save_config)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Test Proxies", command=self.test_proxies)
        tools_menu.add_command(label="Test Notifications", command=self.test_notifications)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Documentation", command=self.open_docs)
        help_menu.add_command(label="About", command=self.show_about)
    
    def create_widgets(self):
        """Create the main GUI widgets"""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(
            main_frame, 
            text="🔥 MAN Scraper Suite", 
            font=("Arial", 20, "bold"),
            bg='#2b2b2b', 
            fg='#ff6b35'
        )
        title_label.pack(pady=(0, 10))
        
        # Subtitle
        subtitle_label = tk.Label(
            main_frame,
            text="100% Free Web Scraping & Automation Toolkit - No Limits, All Features",
            font=("Arial", 10),
            bg='#2b2b2b',
            fg='#cccccc'
        )
        subtitle_label.pack(pady=(0, 20))
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.create_web_scraping_tab()
        self.create_social_media_tab()
        self.create_pdf_tab()
        self.create_images_tab()
        self.create_settings_tab()
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = tk.Label(
            main_frame,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            bg='#3b3b3b',
            fg='#cccccc'
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))
    
    def create_web_scraping_tab(self):
        """Create web scraping tab"""
        web_frame = ttk.Frame(self.notebook)
        self.notebook.add(web_frame, text="🌐 Web Scraping")
        
        # URL input
        ttk.Label(web_frame, text="URL to Scrape:", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(10, 5))
        self.url_entry = tk.Entry(web_frame, font=("Arial", 10), width=80)
        self.url_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Options frame
        options_frame = ttk.Frame(web_frame)
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Dynamic scraping checkbox
        self.dynamic_var = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Dynamic Scraping (JavaScript)", variable=self.dynamic_var).pack(side=tk.LEFT)
        
        # Export format
        ttk.Label(options_frame, text="Format:").pack(side=tk.LEFT, padx=(20, 5))
        self.format_var = tk.StringVar(value="json")
        format_combo = ttk.Combobox(options_frame, textvariable=self.format_var, values=["json", "csv", "excel"], width=10)
        format_combo.pack(side=tk.LEFT)
        
        # Buttons frame
        buttons_frame = ttk.Frame(web_frame)
        buttons_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(buttons_frame, text="🔍 Scrape Single Page", command=self.scrape_single_page).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="📄 Load URLs from File", command=self.load_urls_from_file).pack(side=tk.LEFT)
        
        # Multiple URLs text area
        ttk.Label(web_frame, text="Multiple URLs (one per line):", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(20, 5))
        self.urls_text = scrolledtext.ScrolledText(web_frame, height=8, font=("Arial", 9))
        self.urls_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        ttk.Button(web_frame, text="🔍 Scrape Multiple Pages", command=self.scrape_multiple_pages).pack(pady=5)
        
        # Results area
        ttk.Label(web_frame, text="Results:", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(20, 5))
        self.results_text = scrolledtext.ScrolledText(web_frame, height=6, font=("Arial", 9))
        self.results_text.pack(fill=tk.BOTH, expand=True)
    
    def create_social_media_tab(self):
        """Create social media scraping tab"""
        social_frame = ttk.Frame(self.notebook)
        self.notebook.add(social_frame, text="📱 Social Media")
        
        # Twitter section
        twitter_frame = ttk.LabelFrame(social_frame, text="🐦 Twitter", padding=10)
        twitter_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(twitter_frame, text="Hashtag (without #):").pack(anchor=tk.W)
        self.twitter_hashtag_entry = tk.Entry(twitter_frame, font=("Arial", 10))
        self.twitter_hashtag_entry.pack(fill=tk.X, pady=(0, 5))
        
        twitter_options = ttk.Frame(twitter_frame)
        twitter_options.pack(fill=tk.X)
        
        ttk.Label(twitter_options, text="Count:").pack(side=tk.LEFT)
        self.twitter_count = tk.IntVar(value=100)
        ttk.Spinbox(twitter_options, from_=1, to=1000, textvariable=self.twitter_count, width=10).pack(side=tk.LEFT, padx=(5, 20))
        
        ttk.Button(twitter_options, text="🐦 Scrape Tweets", command=self.scrape_twitter).pack(side=tk.LEFT)
        
        # Reddit section
        reddit_frame = ttk.LabelFrame(social_frame, text="📱 Reddit", padding=10)
        reddit_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(reddit_frame, text="Subreddit (without r/):").pack(anchor=tk.W)
        self.reddit_subreddit_entry = tk.Entry(reddit_frame, font=("Arial", 10))
        self.reddit_subreddit_entry.pack(fill=tk.X, pady=(0, 5))
        
        reddit_options = ttk.Frame(reddit_frame)
        reddit_options.pack(fill=tk.X)
        
        ttk.Label(reddit_options, text="Limit:").pack(side=tk.LEFT)
        self.reddit_limit = tk.IntVar(value=25)
        ttk.Spinbox(reddit_options, from_=1, to=100, textvariable=self.reddit_limit, width=10).pack(side=tk.LEFT, padx=(5, 20))
        
        ttk.Button(reddit_options, text="📱 Scrape Posts", command=self.scrape_reddit).pack(side=tk.LEFT)
        
        # Social media results
        ttk.Label(social_frame, text="Social Media Results:", font=("Arial", 12, "bold")).pack(anchor=tk.W, padx=10, pady=(20, 5))
        self.social_results_text = scrolledtext.ScrolledText(social_frame, height=12, font=("Arial", 9))
        self.social_results_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
    
    def create_pdf_tab(self):
        """Create PDF extraction tab"""
        pdf_frame = ttk.Frame(self.notebook)
        self.notebook.add(pdf_frame, text="📄 PDF Extraction")
        
        ttk.Label(pdf_frame, text="PDF URL:", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(10, 5))
        self.pdf_url_entry = tk.Entry(pdf_frame, font=("Arial", 10))
        self.pdf_url_entry.pack(fill=tk.X, pady=(0, 10))
        
        pdf_buttons = ttk.Frame(pdf_frame)
        pdf_buttons.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(pdf_buttons, text="📄 Extract Text from URL", command=self.extract_pdf_from_url).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(pdf_buttons, text="📁 Extract from Local File", command=self.extract_pdf_from_file).pack(side=tk.LEFT)
        
        # PDF results
        ttk.Label(pdf_frame, text="PDF Extraction Results:", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(20, 5))
        self.pdf_results_text = scrolledtext.ScrolledText(pdf_frame, height=20, font=("Arial", 9))
        self.pdf_results_text.pack(fill=tk.BOTH, expand=True)
    
    def create_images_tab(self):
        """Create image downloading tab"""
        images_frame = ttk.Frame(self.notebook)
        self.notebook.add(images_frame, text="🖼️ Images")
        
        ttk.Label(images_frame, text="Page URL:", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(10, 5))
        self.images_url_entry = tk.Entry(images_frame, font=("Arial", 10))
        self.images_url_entry.pack(fill=tk.X, pady=(0, 10))
        
        images_options = ttk.Frame(images_frame)
        images_options.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(images_options, text="Output Directory:").pack(side=tk.LEFT)
        self.images_dir_var = tk.StringVar()
        ttk.Entry(images_options, textvariable=self.images_dir_var, width=50).pack(side=tk.LEFT, padx=(5, 5))
        ttk.Button(images_options, text="Browse", command=self.browse_images_dir).pack(side=tk.LEFT)
        
        ttk.Button(images_frame, text="🖼️ Download Images", command=self.download_images).pack(pady=10)
        
        # Images results
        ttk.Label(images_frame, text="Image Download Results:", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(20, 5))
        self.images_results_text = scrolledtext.ScrolledText(images_frame, height=15, font=("Arial", 9))
        self.images_results_text.pack(fill=tk.BOTH, expand=True)
    
    def create_settings_tab(self):
        """Create settings/configuration tab"""
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="⚙️ Settings")
        
        # Scraping settings
        scraping_frame = ttk.LabelFrame(settings_frame, text="Scraping Settings", padding=10)
        scraping_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Delay setting
        delay_frame = ttk.Frame(scraping_frame)
        delay_frame.pack(fill=tk.X, pady=5)
        ttk.Label(delay_frame, text="Delay between requests (seconds):").pack(side=tk.LEFT)
        self.delay_var = tk.DoubleVar(value=self.config.get("scraping.delay", 1.0))
        ttk.Spinbox(delay_frame, from_=0.1, to=10.0, increment=0.1, textvariable=self.delay_var, width=10).pack(side=tk.RIGHT)
        
        # Timeout setting
        timeout_frame = ttk.Frame(scraping_frame)
        timeout_frame.pack(fill=tk.X, pady=5)
        ttk.Label(timeout_frame, text="Request timeout (seconds):").pack(side=tk.LEFT)
        self.timeout_var = tk.IntVar(value=self.config.get("scraping.timeout", 30))
        ttk.Spinbox(timeout_frame, from_=5, to=120, textvariable=self.timeout_var, width=10).pack(side=tk.RIGHT)
        
        # Stealth settings
        stealth_frame = ttk.LabelFrame(settings_frame, text="Stealth Settings", padding=10)
        stealth_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.proxy_rotation_var = tk.BooleanVar(value=self.config.get("stealth.proxy_rotation", False))
        ttk.Checkbutton(stealth_frame, text="Enable Proxy Rotation", variable=self.proxy_rotation_var).pack(anchor=tk.W)
        
        self.user_agent_rotation_var = tk.BooleanVar(value=self.config.get("scraping.user_agent_rotation", True))
        ttk.Checkbutton(stealth_frame, text="Enable User-Agent Rotation", variable=self.user_agent_rotation_var).pack(anchor=tk.W)
        
        # Output settings
        output_frame = ttk.LabelFrame(settings_frame, text="Output Settings", padding=10)
        output_frame.pack(fill=tk.X, padx=10, pady=10)
        
        output_dir_frame = ttk.Frame(output_frame)
        output_dir_frame.pack(fill=tk.X, pady=5)
        ttk.Label(output_dir_frame, text="Output Directory:").pack(side=tk.LEFT)
        self.output_dir_var = tk.StringVar(value=self.config.get("export.output_dir", ""))
        ttk.Entry(output_dir_frame, textvariable=self.output_dir_var, width=40).pack(side=tk.LEFT, padx=(5, 5))
        ttk.Button(output_dir_frame, text="Browse", command=self.browse_output_dir).pack(side=tk.RIGHT)
        
        # Save settings button
        ttk.Button(settings_frame, text="💾 Save Settings", command=self.save_settings).pack(pady=20)
    
    # Event handlers
    def scrape_single_page(self):
        """Handle single page scraping"""
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a URL to scrape")
            return
        
        self.run_in_thread(self._scrape_single_page, url)
    
    def _scrape_single_page(self, url):
        """Internal method to scrape single page"""
        try:
            self.status_var.set("Scraping...")
            self.is_scraping = True
            
            scraper = WebScraper(self.config.config)
            data = scraper.scrape_page(url, dynamic=self.dynamic_var.get())
            
            if data:
                # Export data
                exporter = DataExporter(self.config.config)
                filename = f"scraped_data_{int(time.time())}"
                
                if self.format_var.get() == "json":
                    filepath = exporter.export_to_json([data], filename)
                elif self.format_var.get() == "csv":
                    filepath = exporter.export_to_csv([data], filename)
                elif self.format_var.get() == "excel":
                    filepath = exporter.export_to_excel([data], filename)
                
                result_msg = f"✅ Successfully scraped {url}\n📁 Saved to: {filepath}\n\n"
                self.results_text.insert(tk.END, result_msg)
                self.results_text.see(tk.END)
                
                self.status_var.set("Scraping completed successfully")
            else:
                error_msg = f"❌ No data scraped from {url}\n\n"
                self.results_text.insert(tk.END, error_msg)
                self.status_var.set("No data found")
                
        except Exception as e:
            error_msg = f"❌ Error scraping {url}: {str(e)}\n\n"
            self.results_text.insert(tk.END, error_msg)
            self.status_var.set("Error occurred")
        finally:
            self.is_scraping = False
    
    def scrape_multiple_pages(self):
        """Handle multiple pages scraping"""
        urls_text = self.urls_text.get("1.0", tk.END).strip()
        if not urls_text:
            messagebox.showerror("Error", "Please enter URLs to scrape")
            return
        
        urls = [url.strip() for url in urls_text.split('\n') if url.strip()]
        if not urls:
            messagebox.showerror("Error", "No valid URLs found")
            return
        
        self.run_in_thread(self._scrape_multiple_pages, urls)
    
    def _scrape_multiple_pages(self, urls):
        """Internal method to scrape multiple pages"""
        try:
            self.status_var.set(f"Scraping {len(urls)} URLs...")
            self.is_scraping = True
            
            scraper = WebScraper(self.config.config)
            data = scraper.scrape_multiple_pages(urls, dynamic=self.dynamic_var.get())
            
            if data:
                # Export data
                exporter = DataExporter(self.config.config)
                filename = f"scraped_multiple_{int(time.time())}"
                
                if self.format_var.get() == "json":
                    filepath = exporter.export_to_json(data, filename)
                elif self.format_var.get() == "csv":
                    filepath = exporter.export_to_csv(data, filename)
                elif self.format_var.get() == "excel":
                    filepath = exporter.export_to_excel(data, filename)
                
                result_msg = f"✅ Successfully scraped {len(data)} pages\n📁 Saved to: {filepath}\n\n"
                self.results_text.insert(tk.END, result_msg)
                self.results_text.see(tk.END)
                
                self.status_var.set(f"Scraped {len(data)} pages successfully")
            else:
                error_msg = f"❌ No data scraped from {len(urls)} URLs\n\n"
                self.results_text.insert(tk.END, error_msg)
                self.status_var.set("No data found")
                
        except Exception as e:
            error_msg = f"❌ Error scraping multiple pages: {str(e)}\n\n"
            self.results_text.insert(tk.END, error_msg)
            self.status_var.set("Error occurred")
        finally:
            self.is_scraping = False
    
    def scrape_twitter(self):
        """Handle Twitter scraping"""
        hashtag = self.twitter_hashtag_entry.get().strip()
        if not hashtag:
            messagebox.showerror("Error", "Please enter a hashtag")
            return
        
        count = self.twitter_count.get()
        self.run_in_thread(self._scrape_twitter, hashtag, count)
    
    def _scrape_twitter(self, hashtag, count):
        """Internal method to scrape Twitter"""
        try:
            self.status_var.set(f"Scraping Twitter #{hashtag}...")
            
            scraper = TwitterScraper(self.config.config)
            tweets = scraper.scrape_tweets(hashtag, count)
            
            if tweets:
                # Export data
                exporter = DataExporter(self.config.config)
                filename = f"twitter_{hashtag}_{int(time.time())}"
                filepath = exporter.export_to_json(tweets, filename)
                
                result_msg = f"✅ Twitter: Scraped {len(tweets)} tweets for #{hashtag}\n📁 Saved to: {filepath}\n\n"
                self.social_results_text.insert(tk.END, result_msg)
                self.social_results_text.see(tk.END)
                
                self.status_var.set(f"Twitter scraping completed - {len(tweets)} tweets")
            else:
                error_msg = f"❌ No tweets found for #{hashtag}\n\n"
                self.social_results_text.insert(tk.END, error_msg)
                self.status_var.set("No tweets found")
                
        except Exception as e:
            error_msg = f"❌ Error scraping Twitter #{hashtag}: {str(e)}\n\n"
            self.social_results_text.insert(tk.END, error_msg)
            self.status_var.set("Twitter error occurred")
    
    def scrape_reddit(self):
        """Handle Reddit scraping"""
        subreddit = self.reddit_subreddit_entry.get().strip()
        if not subreddit:
            messagebox.showerror("Error", "Please enter a subreddit")
            return
        
        limit = self.reddit_limit.get()
        self.run_in_thread(self._scrape_reddit, subreddit, limit)
    
    def _scrape_reddit(self, subreddit, limit):
        """Internal method to scrape Reddit"""
        try:
            self.status_var.set(f"Scraping Reddit r/{subreddit}...")
            
            scraper = RedditScraper(self.config.config)
            posts = scraper.scrape_subreddit_posts(subreddit, limit)
            
            if posts:
                # Export data
                exporter = DataExporter(self.config.config)
                filename = f"reddit_{subreddit}_{int(time.time())}"
                filepath = exporter.export_to_json(posts, filename)
                
                result_msg = f"✅ Reddit: Scraped {len(posts)} posts from r/{subreddit}\n📁 Saved to: {filepath}\n\n"
                self.social_results_text.insert(tk.END, result_msg)
                self.social_results_text.see(tk.END)
                
                self.status_var.set(f"Reddit scraping completed - {len(posts)} posts")
            else:
                error_msg = f"❌ No posts found in r/{subreddit}\n\n"
                self.social_results_text.insert(tk.END, error_msg)
                self.status_var.set("No posts found")
                
        except Exception as e:
            error_msg = f"❌ Error scraping Reddit r/{subreddit}: {str(e)}\n\n"
            self.social_results_text.insert(tk.END, error_msg)
            self.status_var.set("Reddit error occurred")
    
    def extract_pdf_from_url(self):
        """Handle PDF extraction from URL"""
        url = self.pdf_url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a PDF URL")
            return
        
        self.run_in_thread(self._extract_pdf_from_url, url)
    
    def _extract_pdf_from_url(self, url):
        """Internal method to extract PDF from URL"""
        try:
            self.status_var.set("Extracting PDF text...")
            
            scraper = PDFScraper(self.config.config)
            pdf_data = scraper.extract_from_url(url)
            
            if pdf_data and not pdf_data.get('error'):
                # Export data
                exporter = DataExporter(self.config.config)
                filename = f"pdf_extract_{int(time.time())}"
                filepath = exporter.export_to_json([pdf_data], filename)
                
                result_msg = f"✅ PDF: Extracted text from {pdf_data['total_pages']} pages\n📁 Saved to: {filepath}\n\n"
                result_msg += f"📄 Title: {pdf_data['metadata'].get('title', 'N/A')}\n"
                result_msg += f"👤 Author: {pdf_data['metadata'].get('author', 'N/A')}\n\n"
                
                self.pdf_results_text.insert(tk.END, result_msg)
                self.pdf_results_text.see(tk.END)
                
                self.status_var.set(f"PDF extraction completed - {pdf_data['total_pages']} pages")
            else:
                error_msg = f"❌ Error extracting PDF: {pdf_data.get('error', 'Unknown error')}\n\n"
                self.pdf_results_text.insert(tk.END, error_msg)
                self.status_var.set("PDF extraction failed")
                
        except Exception as e:
            error_msg = f"❌ Error processing PDF: {str(e)}\n\n"
            self.pdf_results_text.insert(tk.END, error_msg)
            self.status_var.set("PDF error occurred")
    
    def extract_pdf_from_file(self):
        """Handle PDF extraction from local file"""
        file_path = filedialog.askopenfilename(
            title="Select PDF File",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if file_path:
            self.run_in_thread(self._extract_pdf_from_file, Path(file_path))
    
    def _extract_pdf_from_file(self, file_path):
        """Internal method to extract PDF from file"""
        try:
            self.status_var.set("Extracting PDF text from file...")
            
            scraper = PDFScraper(self.config.config)
            pdf_data = scraper.extract_text(file_path)
            
            if pdf_data and not pdf_data.get('error'):
                # Export data
                exporter = DataExporter(self.config.config)
                filename = f"pdf_extract_{file_path.stem}_{int(time.time())}"
                filepath = exporter.export_to_json([pdf_data], filename)
                
                result_msg = f"✅ PDF: Extracted text from {pdf_data['total_pages']} pages ({file_path.name})\n📁 Saved to: {filepath}\n\n"
                result_msg += f"📄 Title: {pdf_data['metadata'].get('title', 'N/A')}\n"
                result_msg += f"👤 Author: {pdf_data['metadata'].get('author', 'N/A')}\n\n"
                
                self.pdf_results_text.insert(tk.END, result_msg)
                self.pdf_results_text.see(tk.END)
                
                self.status_var.set(f"PDF extraction completed - {pdf_data['total_pages']} pages")
            else:
                error_msg = f"❌ Error extracting PDF: {pdf_data.get('error', 'Unknown error')}\n\n"
                self.pdf_results_text.insert(tk.END, error_msg)
                self.status_var.set("PDF extraction failed")
                
        except Exception as e:
            error_msg = f"❌ Error processing PDF file: {str(e)}\n\n"
            self.pdf_results_text.insert(tk.END, error_msg)
            self.status_var.set("PDF error occurred")
    
    def download_images(self):
        """Handle image downloading"""
        url = self.images_url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a page URL")
            return
        
        self.run_in_thread(self._download_images, url)
    
    def _download_images(self, url):
        """Internal method to download images"""
        try:
            self.status_var.set("Downloading images...")
            
            scraper = ImageScraper(self.config.config)
            
            # Set custom output directory if specified
            if self.images_dir_var.get():
                scraper.output_dir = Path(self.images_dir_var.get())
                scraper.output_dir.mkdir(parents=True, exist_ok=True)
            
            results = scraper.scrape_and_download(url)
            
            if results:
                result_msg = f"✅ Images: Downloaded {len(results)} images from {url}\n📁 Saved to: {scraper.output_dir}\n\n"
                
                for result in results[:5]:  # Show first 5 files
                    result_msg += f"  📸 {Path(result['file_path']).name}\n"
                
                if len(results) > 5:
                    result_msg += f"  ... and {len(results) - 5} more files\n"
                
                result_msg += "\n"
                
                self.images_results_text.insert(tk.END, result_msg)
                self.images_results_text.see(tk.END)
                
                self.status_var.set(f"Downloaded {len(results)} images")
            else:
                error_msg = f"❌ No images found or downloaded from {url}\n\n"
                self.images_results_text.insert(tk.END, error_msg)
                self.status_var.set("No images found")
                
        except Exception as e:
            error_msg = f"❌ Error downloading images: {str(e)}\n\n"
            self.images_results_text.insert(tk.END, error_msg)
            self.status_var.set("Image download error")
    
    # Utility methods
    def run_in_thread(self, func, *args):
        """Run function in separate thread to prevent GUI freezing"""
        if self.is_scraping:
            messagebox.showwarning("Warning", "Another scraping operation is already running")
            return
        
        thread = threading.Thread(target=func, args=args, daemon=True)
        thread.start()
    
    def load_urls_from_file(self):
        """Load URLs from text file"""
        file_path = filedialog.askopenfilename(
            title="Select URLs file",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    urls = f.read()
                    self.urls_text.delete("1.0", tk.END)
                    self.urls_text.insert("1.0", urls)
                    self.status_var.set(f"Loaded URLs from {Path(file_path).name}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {str(e)}")
    
    def browse_output_dir(self):
        """Browse for output directory"""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_dir_var.set(directory)
    
    def browse_images_dir(self):
        """Browse for images output directory"""
        directory = filedialog.askdirectory(title="Select Images Output Directory")
        if directory:
            self.images_dir_var.set(directory)
    
    def test_proxies(self):
        """Test proxy connections"""
        def _test_proxies():
            try:
                self.status_var.set("Testing proxies...")
                proxy_manager = ProxyManager(self.config.config)
                stats = proxy_manager.get_stats()
                
                messagebox.showinfo("Proxy Test Results", 
                    f"Total proxies: {stats['total_proxies']}\n"
                    f"Failed proxies: {stats['failed_proxies']}\n"
                    f"Tor available: {stats['tor_available']}\n"
                    f"Current IP: {stats['current_ip']}")
                
                self.status_var.set("Proxy test completed")
            except Exception as e:
                messagebox.showerror("Error", f"Proxy test failed: {str(e)}")
                self.status_var.set("Proxy test failed")
        
        threading.Thread(target=_test_proxies, daemon=True).start()
    
    def test_notifications(self):
        """Test notification systems"""
        def _test_notifications():
            try:
                self.status_var.set("Testing notifications...")
                notification_manager = NotificationManager(self.config.config)
                results = notification_manager.test_notifications()
                
                message = "Notification Test Results:\n\n"
                message += f"Email: {'✅ Success' if results['email'] else '❌ Failed'}\n"
                message += f"Telegram: {'✅ Success' if results['telegram'] else '❌ Failed'}"
                
                messagebox.showinfo("Notification Test Results", message)
                self.status_var.set("Notification test completed")
            except Exception as e:
                messagebox.showerror("Error", f"Notification test failed: {str(e)}")
                self.status_var.set("Notification test failed")
        
        threading.Thread(target=_test_notifications, daemon=True).start()
    
    def save_settings(self):
        """Save current settings to configuration"""
        try:
            # Update config with current values
            self.config.set("scraping.delay", self.delay_var.get())
            self.config.set("scraping.timeout", self.timeout_var.get())
            self.config.set("stealth.proxy_rotation", self.proxy_rotation_var.get())
            self.config.set("scraping.user_agent_rotation", self.user_agent_rotation_var.get())
            self.config.set("export.output_dir", self.output_dir_var.get())
            
            # Save to file
            self.config.save_config()
            
            messagebox.showinfo("Success", "Settings saved successfully!")
            self.status_var.set("Settings saved")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")
    
    def open_config(self):
        """Open configuration file"""
        file_path = filedialog.askopenfilename(
            title="Open Configuration File",
            filetypes=[("YAML files", "*.yaml"), ("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.config = Config(file_path)
                messagebox.showinfo("Success", "Configuration loaded successfully!")
                self.status_var.set(f"Loaded config from {Path(file_path).name}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load configuration: {str(e)}")
    
    def save_config(self):
        """Save configuration to file"""
        file_path = filedialog.asksaveasfilename(
            title="Save Configuration File",
            defaultextension=".yaml",
            filetypes=[("YAML files", "*.yaml"), ("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.config.save_config(file_path)
                messagebox.showinfo("Success", "Configuration saved successfully!")
                self.status_var.set(f"Saved config to {Path(file_path).name}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save configuration: {str(e)}")
    
    def open_docs(self):
        """Open documentation in web browser"""
        webbrowser.open("https://omniscraper.readthedocs.io/")
    
    def show_about(self):
        """Show about dialog"""
        from .. import __version__, get_info
        
        info = get_info()
        about_text = f"""🔥 OmniScraper v{__version__}

{info['description']}

🌟 Features:
• Universal Web Scraping (Static + Dynamic JS)
• Social Media Scraping (X/Twitter, Reddit, Instagram)
• PDF/Image Extraction
• Multiple Export Formats (CSV, JSON, Excel, PDF)
• Cloud Integration (Google Drive, Dropbox)
• Database Support (MySQL, PostgreSQL, MongoDB)
• Automation & Scheduling
• Privacy & Stealth (Proxy Rotation, User-Agent Spoofing)
• CLI & GUI Interfaces
• Mobile Support (Termux/Android)

📄 License: {info['license']}
🌐 Repository: {info['repository']}

💝 100% Free - No Limits - All Features Unlocked!
Community-Driven - No Paywalls - Open Source"""
        
        messagebox.showinfo("About OmniScraper", about_text)
    
    def run(self):
        """Start the GUI application"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\nGUI application interrupted by user")
        except Exception as e:
            print(f"GUI application error: {e}")

def launch_gui():
    """Launch the OmniScraper GUI"""
    try:
        app = OmniScraperGUI()
        app.run()
    except ImportError as e:
        print(f"GUI dependencies not available: {e}")
        print("Please install GUI dependencies: pip install customtkinter")
    except Exception as e:
        print(f"Failed to launch GUI: {e}")

# Import time for timestamp functions
import time

if __name__ == "__main__":
    launch_gui()
