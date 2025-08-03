#!/usr/bin/env python3
"""
Command Line Interface for MAN Scraper Suite
Provides all functionality through terminal commands
"""

import sys
import os
import json
import time
from pathlib import Path
from typing import Optional, List

# Add basic error handling for missing dependencies
try:
    import click
except ImportError:
    print("❌ Missing dependency: click")
    print("💡 Install with: pip install click")
    sys.exit(1)

# Core imports with error handling
try:
    from .core.config import Config
except ImportError:
    # Fallback basic config class
    class Config:
        def __init__(self, config_file=None):
            self.config = {}

try:
    from .scrapers.web_scraper import WebScraper
except ImportError:
    WebScraper = None
    
try:
    from .exporters.data_exporter import DataExporter
except ImportError:
    DataExporter = None
    
try:
    from .stealth.proxy_manager import ProxyManager
except ImportError:
    ProxyManager = None

# Optional imports
try:
    from .scrapers.social_scraper import TwitterScraper, RedditScraper
except ImportError:
    TwitterScraper = RedditScraper = None

try:
    from .scrapers.url_generator import URLGenerator
except ImportError:
    URLGenerator = None
    
try:
    from .scrapers.pdf_scraper import PDFScraper
except ImportError:
    PDFScraper = None
    
try:
    from .scrapers.image_scraper import ImageScraper
except ImportError:
    ImageScraper = None
    
try:
    from .exporters.cloud_uploader import CloudUploader
except ImportError:
    CloudUploader = None
    
try:
    from .exporters.database_exporter import DatabaseExporter
except ImportError:
    DatabaseExporter = None

# Google Authentication Imports
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
except ImportError:
    print("❌ Missing dependencies for Google Authentication")
    sys.exit(1)

# User Management Import
try:
    from .core.user_manager import UserManager
except ImportError:
    UserManager = None

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# User OAuth scopes (for authentication)
USER_SCOPES = [
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'openid'
]

# Global authentication state
USER_AUTHENTICATED = False
CURRENT_USER_INFO = {}

def require_authentication(func):
    """Decorator to require authentication before command execution"""
    def wrapper(*args, **kwargs):
        if not check_authentication():
            show_authentication_required()
            return
        return func(*args, **kwargs)
    return wrapper

def check_authentication():
    """Check if user is authenticated"""
    # Check for token file
    token_file = Path('token.json')
    if token_file.exists():
        try:
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            if creds and creds.valid:
                return True
        except:
            pass
    return False

def show_authentication_required():
    """Show authentication required message"""
    click.echo("\n" + "="*60)
    click.echo("🔐 AUTHENTICATION REQUIRED")
    click.echo("="*60)
    click.echo("⚠️  You must authenticate before using MAN Scraper Suite")
    click.echo("")
    click.echo("🚀 To get started:")
    click.echo("   1. Run: py -m manscrapersuite.cli google-auth")
    click.echo("   2. Complete Google OAuth in your browser")
    click.echo("   3. Start scraping!")
    click.echo("")
    click.echo("💡 This helps us:")
    click.echo("   • Track usage and prevent abuse")
    click.echo("   • Provide better support")
    click.echo("   • Export data to your Google Sheets")
    click.echo("   • Monitor system performance")
    click.echo("")
    click.echo("🔒 Your data remains private and secure.")
    click.echo("="*60)

def authenticate_and_log_user():
    """Authenticate user and log to Google Sheets"""
    global USER_AUTHENTICATED, CURRENT_USER_INFO
    
    if not UserManager:
        click.echo("❌ User management not available")
        return False
    
    try:
        # Initialize user manager
        config = Config()
        user_manager = UserManager(config.config)
        
        # Get basic user info
        import socket
        import uuid
        
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        device_id = str(uuid.uuid4())[:8]
        
        # For now, use a generic email. In real implementation, 
        # you'd extract from Google OAuth token
        user_email = "authenticated_user@example.com"
        
        # Register/authenticate user
        success, message = user_manager.authenticate_user(user_email, ip_address, device_id)
        
        if success:
            USER_AUTHENTICATED = True
            CURRENT_USER_INFO = {
                'email': user_email,
                'ip_address': ip_address,
                'device_id': device_id,
                'authenticated_at': time.time()
            }
            return True
    except Exception as e:
        click.echo(f"Warning: User logging failed: {e}")
        # Don't block authentication if logging fails
        return True
    
    return False

# NEW PHASE 5-7 IMPORTS
try:
    from .ai.ai_engine import AIEngine
    from .ai.data_analyzer import DataAnalyzer
    from .ai.smart_filter import SmartFilter
    AI_AVAILABLE = True
except ImportError:
    AIEngine = DataAnalyzer = SmartFilter = None
    AI_AVAILABLE = False

try:
    from .stealth.enhanced_stealth import EnhancedStealth
except ImportError:
    EnhancedStealth = None

@click.group()
@click.option('--config', '-c', type=str, help='Path to configuration file')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.pass_context
def cli(ctx, config: Optional[str], verbose: bool):
    """🔥 MAN Scraper Suite - 100% Free Web Scraping & Automation Toolkit"""
    ctx.ensure_object(dict)
    
    # Load configuration
    ctx.obj['config'] = Config(config)
    ctx.obj['verbose'] = verbose
    
    if verbose:
        click.echo("🔥 MAN Scraper Suite initialized with verbose mode")

@cli.command()
@click.argument('url')
@click.option('--dynamic', '-d', is_flag=True, help='Use dynamic scraping (Playwright)')
@click.option('--output', '-o', type=str, help='Output filename')
@click.option('--format', '-f', type=click.Choice(['json', 'csv', 'excel', 'pdf']), default='json', help='Output format')
@click.pass_context
def scrape(ctx, url: str, dynamic: bool, output: Optional[str], format: str):
    """Scrape a single webpage"""
    # Check authentication first
    if not check_authentication():
        show_authentication_required()
        return
    
    config = ctx.obj['config']
    
    click.echo(f"🔍 Scraping: {url}")
    click.echo(f"📊 Mode: {'Dynamic (JS)' if dynamic else 'Static'}")
    
    # Initialize scraper
    scraper = WebScraper(config.config)
    
    # Scrape data
    try:
        data = scraper.scrape_page(url, dynamic=dynamic)
        
        if data:
            # Export data
            exporter = DataExporter(config.config)
            
            if not output:
                output = f"scraped_data_{int(time.time())}"
            
            if format == 'json':
                filepath = exporter.export_to_json([data], output)
            elif format == 'csv':
                filepath = exporter.export_to_csv([data], output)
            elif format == 'excel':
                filepath = exporter.export_to_excel([data], output)
            elif format == 'pdf':
                filepath = exporter.export_to_pdf([data], output)
            
            click.echo(f"✅ Data saved to: {filepath}")
        else:
            click.echo("❌ No data scraped")
            
    except Exception as e:
        click.echo(f"❌ Error scraping {url}: {e}")

@cli.command()
@click.argument('urls', nargs=-1, required=True)
@click.option('--dynamic', '-d', is_flag=True, help='Use dynamic scraping')
@click.option('--output', '-o', type=str, help='Output filename')
@click.option('--format', '-f', type=click.Choice(['json', 'csv', 'excel']), default='json')
@click.pass_context
def scrape_multiple(ctx, urls: List[str], dynamic: bool, output: Optional[str], format: str):
    """Scrape multiple webpages"""
    config = ctx.obj['config']
    
    click.echo(f"🔍 Scraping {len(urls)} URLs")
    
    scraper = WebScraper(config.config)
    
    try:
        data = scraper.scrape_multiple_pages(list(urls), dynamic=dynamic)
        
        if data:
            exporter = DataExporter(config.config)
            
            if not output:
                output = f"scraped_multiple_{int(time.time())}"
            
            if format == 'json':
                filepath = exporter.export_to_json(data, output)
            elif format == 'csv':
                filepath = exporter.export_to_csv(data, output)
            elif format == 'excel':
                filepath = exporter.export_to_excel(data, output)
            
            click.echo(f"✅ Data from {len(data)} pages saved to: {filepath}")
        else:
            click.echo("❌ No data scraped")
            
    except Exception as e:
        click.echo(f"❌ Error scraping multiple URLs: {e}")

@cli.command()
@click.argument('keyword')
@click.option('--count', '-n', type=int, default=20, help='Number of tweets to scrape')
@click.option('--output', '-o', type=str, help='Output filename')
@click.pass_context
def twitter(ctx, keyword: str, count: int, output: Optional[str]):
    """Scrape Twitter tweets by keyword (No API required)"""
    if TwitterScraper is None:
        click.echo("❌ Twitter scraping not available. Missing dependencies.")
        return
        
    config = ctx.obj['config']
    
    click.echo(f"🐦 Scraping Twitter for keyword: '{keyword}' (No API)")
    
    try:
        scraper = TwitterScraper(config.config)
        tweets = scraper.scrape_tweets_no_api(keyword, count)
        
        if tweets:
            exporter = DataExporter(config.config)
            
            if not output:
                output = f"twitter_{keyword.replace(' ', '_')}_{int(time.time())}"
            
            filepath = exporter.export_to_json(tweets, output)
            click.echo(f"✅ {len(tweets)} tweets saved to: {filepath}")
        else:
            click.echo("❌ No tweets found")
            
    except Exception as e:
        click.echo(f"❌ Error scraping Twitter: {e}")

@cli.command()
@click.argument('subreddit')
@click.option('--limit', '-l', type=int, default=10, help='Number of posts to scrape')
@click.option('--output', '-o', type=str, help='Output filename')
@click.pass_context
def reddit(ctx, subreddit: str, limit: int, output: Optional[str]):
    """Scrape Reddit posts from a subreddit"""
    # Check authentication first
    if not check_authentication():
        show_authentication_required()
        return
    
    config = ctx.obj['config']
    
    click.echo(f"📱 Scraping Reddit: r/{subreddit}")
    
    try:
        scraper = RedditScraper(config.config)
        posts = scraper.scrape_subreddit_posts(subreddit, limit)
        
        if posts:
            exporter = DataExporter(config.config)
            
            if not output:
                output = f"reddit_{subreddit}_{int(time.time())}"
            
            filepath = exporter.export_to_json(posts, output)
            click.echo(f"✅ {len(posts)} posts saved to: {filepath}")
        else:
            click.echo("❌ No posts found")
            
    except Exception as e:
        click.echo(f"❌ Error scraping Reddit: {e}")

@cli.command()
@click.argument('topic')
@click.option('--limit', '-l', type=int, default=10, help='Number of posts to scrape')
@click.option('--output', '-o', type=str, help='Output filename')
@click.pass_context
def reddit_topic(ctx, topic: str, limit: int, output: Optional[str]):
    """Scrape Reddit posts by topic (No API required)"""
    if RedditScraper is None:
        click.echo("❌ Reddit scraping not available. Missing dependencies.")
        return
        
    config = ctx.obj['config']
    
    click.echo(f"📱 Scraping Reddit for topic: '{topic}' (No API)")
    
    try:
        scraper = RedditScraper(config.config)
        posts = scraper.scrape_posts_by_topic(topic, limit)
        
        if posts:
            exporter = DataExporter(config.config)
            
            if not output:
                output = f"reddit_{topic.replace(' ', '_')}_{int(time.time())}"
            
            filepath = exporter.export_to_json(posts, output)
            click.echo(f"✅ {len(posts)} posts saved to: {filepath}")
        else:
            click.echo("❌ No posts found")
            
    except Exception as e:
        click.echo(f"❌ Error scraping Reddit by topic: {e}")

@cli.command()
@click.argument('topic')
@click.option('--content-type', '-t', type=click.Choice(['general', 'news', 'social', 'academic', 'shopping', 'images', 'videos']), default='general', help='Content type for URL generation')
@click.option('--limit', '-l', type=int, default=5, help='Number of URLs to generate')
@click.option('--ai', is_flag=True, help='Use AI for smart URL generation')
@click.pass_context
def generate_urls(ctx, topic: str, content_type: str, limit: int, ai: bool):
    """🔗 Generate URLs automatically based on topic"""
    if URLGenerator is None:
        click.echo("❌ URL generator not available. Missing dependencies.")
        return
        
    config = ctx.obj['config']
    
    click.echo(f"🔗 Generating URLs for topic: '{topic}'")
    click.echo(f"📊 Content type: {content_type}")
    click.echo(f"🤖 AI mode: {'Enabled' if ai else 'Disabled'}")
    
    try:
        generator = URLGenerator(config.config)
        
        if ai and AI_AVAILABLE:
            urls = generator.ai_generate_urls(topic)
            click.echo(f"🤖 AI-generated URLs:")
        else:
            urls = generator.generate_urls_by_topic(topic, content_type, limit)
            click.echo(f"🔗 Pattern-based URLs:")
        
        for i, url in enumerate(urls, 1):
            click.echo(f"  {i}. {url}")
        
        # Save URLs to file
        output_file = f"generated_urls_{topic.replace(' ', '_')}_{int(time.time())}.txt"
        with open(output_file, 'w') as f:
            for url in urls:
                f.write(url + '\n')
        
        click.echo(f"\n✅ URLs saved to: {output_file}")
        
    except Exception as e:
        click.echo(f"❌ Error generating URLs: {e}")

@cli.command()
@click.argument('pdf_url')
@click.option('--output', '-o', type=str, help='Output filename')
@click.pass_context
def pdf(ctx, pdf_url: str, output: Optional[str]):
    """Extract text from PDF URL"""
    config = ctx.obj['config']
    
    click.echo(f"📄 Extracting text from PDF: {pdf_url}")
    
    try:
        scraper = PDFScraper(config.config)
        pdf_data = scraper.extract_from_url(pdf_url)
        
        if pdf_data and not pdf_data.get('error'):
            exporter = DataExporter(config.config)
            
            if not output:
                output = f"pdf_extract_{int(time.time())}"
            
            filepath = exporter.export_to_json([pdf_data], output)
            click.echo(f"✅ PDF text extracted ({pdf_data['total_pages']} pages) saved to: {filepath}")
        else:
            click.echo(f"❌ Error extracting PDF: {pdf_data.get('error', 'Unknown error')}")
            
    except Exception as e:
        click.echo(f"❌ Error processing PDF: {e}")

@cli.command()
@click.argument('page_url')
@click.option('--output-dir', '-o', type=str, help='Output directory for images')
@click.pass_context
def images(ctx, page_url: str, output_dir: Optional[str]):
    """Download images from a webpage"""
    config = ctx.obj['config']
    
    click.echo(f"🖼️  Downloading images from: {page_url}")
    
    try:
        scraper = ImageScraper(config.config)
        
        if output_dir:
            scraper.output_dir = Path(output_dir)
            scraper.output_dir.mkdir(parents=True, exist_ok=True)
        
        results = scraper.scrape_and_download(page_url)
        
        if results:
            click.echo(f"✅ Downloaded {len(results)} images to: {scraper.output_dir}")
            for result in results:
                click.echo(f"  📸 {result['file_path']}")
        else:
            click.echo("❌ No images found or downloaded")
            
    except Exception as e:
        click.echo(f"❌ Error downloading images: {e}")

@cli.command()
@click.pass_context
def proxy_test(ctx):
    """Test proxy connections"""
    config = ctx.obj['config']
    
    click.echo("🔒 Testing proxy connections...")
    
    try:
        proxy_manager = ProxyManager(config.config)
        working_proxies = proxy_manager.test_all_proxies()
        
        stats = proxy_manager.get_stats()
        click.echo(f"📊 Proxy Statistics:")
        click.echo(f"  Total proxies: {stats['total_proxies']}")
        click.echo(f"  Working proxies: {len(working_proxies)}")
        click.echo(f"  Failed proxies: {stats['failed_proxies']}")
        click.echo(f"  Tor available: {stats['tor_available']}")
        click.echo(f"  Current IP: {stats['current_ip']}")
        
    except Exception as e:
        click.echo(f"❌ Error testing proxies: {e}")

@cli.command()
@click.pass_context
def config_show(ctx):
    """Show current configuration"""
    config = ctx.obj['config']
    
    # Don't show sensitive information
    safe_config = config.config.copy()
    
    # Remove sensitive keys
    sensitive_keys = ['password', 'api_key', 'api_secret', 'access_token', 'bot_token']
    
    def remove_sensitive(obj, keys):
        if isinstance(obj, dict):
            for key in list(obj.keys()):
                if any(sensitive in key.lower() for sensitive in keys):
                    obj[key] = "***HIDDEN***"
                else:
                    remove_sensitive(obj[key], keys)
        elif isinstance(obj, list):
            for item in obj:
                remove_sensitive(item, keys)
    
    remove_sensitive(safe_config, sensitive_keys)
    
    click.echo("⚙️  Current Configuration:")
    click.echo(json.dumps(safe_config, indent=2))

@cli.command()
@click.pass_context
def google_auth(ctx):
    """Authenticate using Google OAuth and redirect to success page"""
    creds = None

    # Check for valid credentials
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', USER_SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials/client_secret.json', USER_SCOPES)
            success_html = 'http://example.com/success.html'
            creds = flow.run_local_server(
                port=0,
                success_message=f'<html><head><meta http-equiv="Refresh" content="0; url={success_html}" /></head><body>Success! You may close this window.</body></html>'
            )

        # Save the credentials
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    click.echo(f"✅ Google Authentication Successful! Redirect to: {success_html}")

# NEW AI AND ANALYTICS COMMANDS
@cli.command()
@click.argument('data_file')
@click.option('--topic', '-t', type=str, help='Topic for analysis')
@click.pass_context
def analyze(ctx, data_file: str, topic: Optional[str]):
    """🤖 AI-powered data analysis"""
    if not AI_AVAILABLE:
        click.echo("❌ AI features not available. Set GEMINI_API_KEY environment variable.")
        return
    
    config = ctx.obj['config']
    
    try:
        # Load data from file
        with open(data_file, 'r', encoding='utf-8') as f:
            if data_file.endswith('.json'):
                file_data = json.load(f)
                data = file_data.get('data', file_data)
            else:
                click.echo("❌ Only JSON files supported for analysis")
                return
        
        # Initialize AI engine
        ai_engine = AIEngine(config.config)
        
        # Perform analysis
        click.echo(f"🔍 Analyzing data with AI...")
        analysis = ai_engine.analyze_scraped_data(data, topic or "data analysis")
        
        # Display results
        click.echo("\n📊 AI Analysis Results:")
        click.echo(f"Quality Score: {analysis.get('quality_score', 'N/A')}/10")
        click.echo(f"Insights: {analysis.get('insights', 'No insights available')}")
        
        if analysis.get('ai_processed'):
            click.echo("✅ Analysis powered by AI")
        else:
            click.echo("⚠️  Basic analysis (AI not available)")
            
    except Exception as e:
        click.echo(f"❌ Error analyzing data: {e}")

@cli.command()
@click.argument('data_file')
@click.option('--criteria', '-c', type=str, help='Filter criteria')
@click.option('--output', '-o', type=str, help='Output filename')
@click.pass_context
def smart_filter(ctx, data_file: str, criteria: str, output: Optional[str]):
    """🎯 Smart data filtering"""
    if not AI_AVAILABLE:
        click.echo("❌ AI features not available. Using basic filtering.")
    
    config = ctx.obj['config']
    
    try:
        # Load data
        with open(data_file, 'r', encoding='utf-8') as f:
            if data_file.endswith('.json'):
                file_data = json.load(f)
                data = file_data.get('data', file_data)
            else:
                click.echo("❌ Only JSON files supported")
                return
        
        # Apply smart filtering
        if AI_AVAILABLE:
            ai_engine = AIEngine(config.config)
            filtered_data = ai_engine.smart_filter_data(data, criteria)
            click.echo(f"🤖 AI-powered filtering applied")
        else:
            smart_filter = SmartFilter()
            keywords = criteria.split() if criteria else []
            filtered_data = smart_filter.filter_based_on_keywords(data, keywords, [])
            click.echo(f"🔍 Basic filtering applied")
        
        # Export filtered data
        exporter = DataExporter(config.config)
        if not output:
            output = f"filtered_data_{int(time.time())}"
        
        filepath = exporter.export_to_json(filtered_data, output, f"Filtered: {criteria}")
        click.echo(f"✅ Filtered data saved: {filepath}")
        click.echo(f"📊 Results: {len(filtered_data)}/{len(data)} items match criteria")
        
    except Exception as e:
        click.echo(f"❌ Error filtering data: {e}")

@cli.command()
@click.pass_context
def dashboard(ctx):
    """🌐 Launch web dashboard (TEMPORARILY DISABLED)"""
    click.echo("⚠️  Web Dashboard temporarily disabled (under development)")
    click.echo("💡 All functionality available through CLI commands")
    click.echo("📖 Use --help to see available commands")
    return
    
    # DISABLED TEMPORARILY - UNDER DEVELOPMENT
    # click.echo("🚀 Starting MAN Scraper Suite Web Dashboard...")
    # click.echo("📍 Dashboard will be available at: http://localhost:5000")
    # click.echo("⚠️  Note: This is a development server. Use Gunicorn for production.")
    # 
    # try:
    #     from .dash.web_dashboard import app
    #     app.run(host='0.0.0.0', port=5000, debug=False)
    # except ImportError:
    #     click.echo("❌ Web dashboard not available. Install Flask: pip install flask")
    # except Exception as e:
    #     click.echo(f"❌ Error starting dashboard: {e}")

@cli.command()
@click.pass_context
def version(ctx):
    """Show version information"""
    try:
        from . import __version__, get_info
        info = get_info()
        version_str = __version__
    except:
        version_str = "1.0.0"
        info = {
            'description': '100% Free Web Scraping & Automation Toolkit',
            'license': 'GPLv3',
            'repository': 'https://github.com/manscrapersuite/manscrapersuite'
        }
    
    click.echo(f"🔥 MAN Scraper Suite v{version_str}")
    click.echo(f"📝 {info['description']}")
    click.echo(f"📄 License: {info['license']}")
    click.echo(f"🌐 Repository: {info['repository']}")
    
    # Show available features
    click.echo("\n✨ Available Features:")
    click.echo(f"  🤖 AI Analysis: {'✅' if AI_AVAILABLE else '❌ (Set GEMINI_API_KEY)'}")
    click.echo(f"  🔒 Enhanced Stealth: {'✅' if EnhancedStealth else '❌'}")
    click.echo(f"  📊 Analytics: ✅")
    click.echo(f"  🌐 Web Dashboard: ✅")

def main():
    """Entry point for the CLI"""
    import time
    cli()

def cli_main():
    """Main CLI entry point for external use"""
    cli()

if __name__ == '__main__':
    cli_main()
