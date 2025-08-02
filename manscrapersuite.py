#!/usr/bin/env python3
"""
MAN Scraper Suite - Main Entry Point
Easy-to-use entry point for terminal users, Termux, and mobile environments
Usage: python manscrapersuite.py [options]
"""

import sys
import os
import argparse
import json
import time
import random
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Add the manscrapersuite package to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'manscrapersuite'))

# Google integration - real implementation
from manscrapersuite.core.config import Config
try:
    from manscrapersuite.exporters.google_sheets import upload_to_google_sheets as sheets_upload
    GOOGLE_SHEETS_AVAILABLE = True
except ImportError:
    GOOGLE_SHEETS_AVAILABLE = False

# Google Services Configuration
GOOGLE_CREDENTIALS_FILE = './credentials/client_secret.json'
GOOGLE_SERVICE_ACCOUNT_FILE = './credentials/scraper-467614-c06499213741.json'

def setup_google_services():
    """Setup Google Sheets and Drive services"""
    try:
        if not GOOGLE_SHEETS_AVAILABLE:
            print("⚠️  Google Sheets integration not available. Install dependencies: pip install gspread google-auth")
            return False
        
        # Check if credential files exist
        from pathlib import Path
        if Path(GOOGLE_SERVICE_ACCOUNT_FILE).exists() or Path(GOOGLE_CREDENTIALS_FILE).exists():
            print("✅ Google services credentials found")
            return True
        else:
            print("❌ Google credentials files not found")
            return False
            
    except Exception as e:
        print(f"❌ Google services setup failed: {e}")
        return False

def upload_to_google_sheets(data: List[Dict], sheet_name: str):
    """Upload data to Google Sheets"""
    try:
        if not GOOGLE_SHEETS_AVAILABLE:
            print("❌ Google Sheets integration not available")
            return False
        
        # Load configuration
        config = Config()
        config.set('google_sheets.enabled', True)
        config.set('google_sheets.service_account_file', GOOGLE_SERVICE_ACCOUNT_FILE)
        config.set('google_sheets.credentials_file', GOOGLE_CREDENTIALS_FILE)
        
        # Upload to sheets
        success = sheets_upload(data, config.config, sheet_name)
        
        if success:
            print(f"✅ Successfully uploaded {len(data)} rows to Google Sheets: {sheet_name}")
        else:
            print(f"❌ Failed to upload to Google Sheets: {sheet_name}")
            
        return success
        
    except Exception as e:
        print(f"❌ Google Sheets upload failed: {e}")
        return False

def contact_flow():
    """Collect and save contact information to Google Sheets"""
    print("📇 Contact Information Collection")
    print("Please provide your contact details:")
    
    name = input("Enter your name: ").strip()
    mobile = input("Enter your mobile: ").strip()
    email = input("Enter your email: ").strip()
    message = input("Enter your message: ").strip()
    
    if not name or not email:
        print("❌ Name and email are required!")
        return
    
    contact_info = {
        "Name": name,
        "Mobile": mobile,
        "Email": email,
        "Message": message,
        "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Save to local file first
    try:
        output_dir = Path("W:/MAN_Scraper_Suite_Data")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        contact_file = output_dir / "contacts.json"
        
        # Load existing contacts or create new list
        contacts = []
        if contact_file.exists():
            with open(contact_file, 'r', encoding='utf-8') as f:
                contacts = json.load(f)
        
        contacts.append(contact_info)
        
        # Save updated contacts
        with open(contact_file, 'w', encoding='utf-8') as f:
            json.dump(contacts, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Contact information saved locally: {contact_file}")
        
        # Try to upload to Google Sheets
        if upload_to_google_sheets([contact_info], "Contacts"):
            print("✅ Contact information also uploaded to Google Sheets")
        else:
            print("⚠️  Could not upload to Google Sheets, but saved locally")
            
    except Exception as e:
        print(f"❌ Error saving contact information: {e}")

def print_banner():
    """Print the MAN Scraper Suite banner"""
    banner = """
╔═══════════════════════════════════════════════════════════╗
║                 🔥 MAN SCRAPER SUITE v1.0.0 🔥                 ║
║           100% FREE - NO LIMITS - ALL FEATURES           ║
║                                                           ║
║  Universal Web Scraping & Automation Toolkit             ║
║  ✓ Any Website (Static + Dynamic JS)                     ║
║  ✓ Social Media (X/Twitter, Reddit, Instagram)           ║
║  ✓ PDF/Image Extraction                                   ║
║  ✓ Export to CSV/JSON/Excel/PDF                          ║
║  ✓ Cloud Push (Drive, Dropbox)                           ║
║  ✓ Database Direct (MySQL, PostgreSQL, MongoDB)          ║
║  ✓ Automation & Scheduling                               ║
║  ✓ Privacy & Stealth (Proxies, User-Agent Spoofing)      ║
║  ✓ CLI Interface (GUI under development)                  ║
║  ✓ Mobile Support (Termux/Android)                       ║
║                                                           ║
║  License: GPLv3 | Community-Driven | No Paywalls        ║
╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)
    print("\nWelcome to the MAN Scraper Suite! 🎉")
    print("This tool allows you to scrape websites and social media platforms, analyze data, and export results.")
    print("Use this interactive mode to guide yourself through available features and options.")

def run_cli(args):
    """Execute CLI commands"""
    try:
        from manscrapersuite.cli import cli_main
        # Filter out empty strings from args
        clean_args = [arg for arg in args if arg.strip()]
        sys.argv = ['cli'] + clean_args
        cli_main()
    except Exception as e:
        print(f"❌ Error executing command: {e}")

def webscrape_flow():
    """Interactive web scraping flow"""
    print("🔍 Web Scraping")
    url = input("🌐 Enter the URL to scrape: ").strip()
    if url:
        dynamic = input("Use dynamic scraping? (y/n): ").strip().lower() == 'y'
        format_ = input("Choose output format (json/csv/excel/pdf): ").strip().lower()
        if format_ not in ['json', 'csv', 'excel', 'pdf']:
            format_ = 'json'
        output = input("Enter output filename: ").strip()
        
        args = ['scrape', url]
        if dynamic:
            args.append('--dynamic')
        if format_:
            args.extend(['--format', format_])
        if output:
            args.extend(['--output', output])
        
        run_cli(args)

def social_media_flow():
    """Interactive social media scraping flow"""
    print("📱 Social Media Scraping")
    platform = input("Choose platform (reddit/twitter): ").strip().lower()
    if platform == 'reddit':
        subreddit = input("Enter subreddit: ").strip()
        limit = input("Enter post limit (default 50): ").strip() or '50'
        if subreddit:
            run_cli(['reddit', subreddit, '--limit', limit])
    elif platform == 'twitter':
        hashtag = input("Enter hashtag (include #): ").strip()
        count = input("Enter tweet count (default 100): ").strip() or '100'
        if hashtag:
            run_cli(['twitter', hashtag, '--count', count])
    else:
        print("❌ Invalid platform!")

def ai_analysis_flow():
    """Interactive AI analysis flow"""
    print("🤖 AI Data Analysis")
    data_file = input("Enter data file path: ").strip()
    if not os.path.exists(data_file):
        print("❌ File does not exist!")
        return
    topic = input("Enter analysis topic (optional): ").strip()
    
    args = ['analyze', data_file]
    if topic:
        args.extend(['--topic', topic])
    
    run_cli(args)

def interactive_mode():
    """Interactive mode with guided flow"""
    print("\n🎯 Welcome to Guided Interactive Mode!")
    print("Choose what you want to do:")
    
    options = [
      ("1", "🔍 Web Scraping"),
      ("2", "📱 Social Media Scraping"),
      ("3", "📊 Data Analysis"),
      ("4", "📇 Contact Us"),
      ("q", "❌ Quit")
    ]
    
    for idx, desc in options:
        print(f"  {idx}. {desc}")
    
    while True:
        choice = input("\n👉 Enter your choice (1-4 or q): ").strip().lower()
        
        if choice == 'q':
            print("👋 Thanks for using MAN Scraper Suite!")
            print("👋 Have a great day!")
            break
        
        try:
            if choice == '1':
                webscrape_flow()
            elif choice == '2':
                social_media_flow()
            elif choice == '3':
                ai_analysis_flow()
            elif choice == '4':
                contact_flow()
            # Hidden options (for internal use)
            elif choice == '5' and False:  # Dashboard - hidden
                print("⚠️  Web Dashboard temporarily disabled (under development)")
                print("💡 Use CLI commands for all functionality")
                # run_cli(['dashboard'])  # Disabled temporarily
            elif choice == '6' and False:  # Config - hidden
                run_cli(['config-show'])
            else:
                print("❌ Invalid choice! Please try again. Enter a number between 1-4 or 'q' to quit.")
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("\n" + "═" * 50)

def main():
    """Main entry point for MAN Scraper Suite"""
    print_banner()
    
    parser = argparse.ArgumentParser(
        description="🔥 MAN Scraper Suite - 100% Free Web Scraping & Automation Toolkit",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
📱 Perfect for Termux/Android users!

Basic Usage Examples:
  python manscrapersuite.py --scrape https://example.com
  python manscrapersuite.py --reddit technology --limit 50
  python manscrapersuite.py --twitter "#AI" --count 100
  python manscrapersuite.py --images https://example.com/gallery
  python manscrapersuite.py --pdf https://example.com/document.pdf
  
Advanced Examples:
  python manscrapersuite.py --scrape-multiple urls.txt
  python manscrapersuite.py --analyze data.json --topic "AI trends"
  python manscrapersuite.py --dashboard --port 8080
  python manscrapersuite.py --interactive

For full CLI features, use: python -m manscrapersuite.cli --help
        """
    )
    
    # Main scraping options
    scraping_group = parser.add_argument_group('🌐 Web Scraping')
    scraping_group.add_argument('--scrape', metavar='URL', help='Scrape a single webpage')
    scraping_group.add_argument('--scrape-multiple', metavar='FILE', help='Scrape multiple URLs from file')
    scraping_group.add_argument('--dynamic', action='store_true', help='Use dynamic scraping (JavaScript support)')
    
    # Social media scraping
    social_group = parser.add_argument_group('📱 Social Media')
    social_group.add_argument('--reddit', metavar='SUBREDDIT', help='Scrape Reddit subreddit')
    social_group.add_argument('--twitter', metavar='HASHTAG', help='Scrape Twitter by hashtag')
    social_group.add_argument('--limit', type=int, default=50, help='Limit number of posts (default: 50)')
    social_group.add_argument('--count', type=int, default=100, help='Count for Twitter scraping (default: 100)')
    
    # Media extraction
    media_group = parser.add_argument_group('🎨 Media Extraction')
    media_group.add_argument('--images', metavar='URL', help='Download images from webpage')
    media_group.add_argument('--pdf', metavar='URL', help='Extract text from PDF')
    
    # AI and Analytics
    ai_group = parser.add_argument_group('🤖 AI & Analytics')
    ai_group.add_argument('--analyze', metavar='FILE', help='Analyze data with AI')
    ai_group.add_argument('--topic', metavar='TOPIC', help='Topic for AI analysis')
    ai_group.add_argument('--smart-filter', metavar='CRITERIA', help='Smart filter data')
    
    # Export options
    export_group = parser.add_argument_group('💾 Export Options')
    export_group.add_argument('--output', '-o', metavar='FILE', help='Output filename')
    export_group.add_argument('--format', '-f', choices=['json', 'csv', 'excel', 'pdf'], 
                            default='json', help='Output format (default: json)')
    
    # Dashboard and tools
    tools_group = parser.add_argument_group('🛠️ Tools & Dashboard')
    tools_group.add_argument('--dashboard', action='store_true', help='Launch web dashboard')
    tools_group.add_argument('--port', type=int, default=5000, help='Dashboard port (default: 5000)')
    tools_group.add_argument('--interactive', action='store_true', help='Interactive mode')
    tools_group.add_argument('--config-show', action='store_true', help='Show configuration')
    tools_group.add_argument('--version', action='store_true', help='Show version info')
    
    # Parse arguments
    args = parser.parse_args()
    
    # If no arguments provided, show help
    if len(sys.argv) == 1:
        parser.print_help()
        return
    
    try:
        # Import the CLI module
        from manscrapersuite.cli import cli_main
        
        # Convert arguments to CLI format
        cli_args = []
        
        if args.version:
            cli_args = ['version']
        elif args.config_show:
            cli_args = ['config-show']
        elif args.dashboard:
            print("⚠️  Web Dashboard temporarily disabled (under development)")
            print("💡 Use CLI commands: python manscrapersuite.py --help")
            return
            # cli_args = ['dashboard']  # Disabled temporarily
            # if args.port != 5000:
            #     cli_args.extend(['--port', str(args.port)])
        elif args.scrape:
            cli_args = ['scrape', args.scrape]
            if args.dynamic:
                cli_args.append('--dynamic')
            if args.output:
                cli_args.extend(['--output', args.output])
            if args.format:
                cli_args.extend(['--format', args.format])
        elif args.scrape_multiple:
            cli_args = ['scrape-multiple', args.scrape_multiple]
            if args.output:
                cli_args.extend(['--output', args.output])
            if args.format:
                cli_args.extend(['--format', args.format])
        elif args.reddit:
            cli_args = ['reddit', args.reddit]
            if args.limit:
                cli_args.extend(['--limit', str(args.limit)])
            if args.output:
                cli_args.extend(['--output', args.output])
        elif args.twitter:
            cli_args = ['twitter', args.twitter]
            if args.count:
                cli_args.extend(['--count', str(args.count)])
            if args.output:
                cli_args.extend(['--output', args.output])
        elif args.images:
            cli_args = ['images', args.images]
            if args.output:
                cli_args.extend(['--output-dir', args.output])
        elif args.pdf:
            cli_args = ['pdf', args.pdf]
            if args.output:
                cli_args.extend(['--output', args.output])
        elif args.analyze:
            cli_args = ['analyze', args.analyze]
            if args.topic:
                cli_args.extend(['--topic', args.topic])
        elif args.smart_filter:
            if not args.analyze:
                print("❌ --smart-filter requires --analyze with a data file")
                return
            cli_args = ['smart-filter', args.analyze, '--criteria', args.smart_filter]
        elif args.interactive:
            interactive_mode()
            return
        else:
            parser.print_help()
            return
        
        # Run the CLI with converted arguments
        sys.argv = ['cli'] + cli_args
        cli_main()
        
    except ImportError as e:
        print(f"❌ Error importing CLI module: {e}")
        print("💡 Make sure all dependencies are installed:")
        print("   pip install -r requirements.txt")
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
