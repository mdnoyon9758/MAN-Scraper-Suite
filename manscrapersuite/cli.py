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
@click.argument('hashtag')
@click.option('--count', '-n', type=int, default=100, help='Number of tweets to scrape')
@click.option('--output', '-o', type=str, help='Output filename')
@click.pass_context
def twitter(ctx, hashtag: str, count: int, output: Optional[str]):
    """Scrape Twitter tweets by hashtag"""
    if TwitterScraper is None:
        click.echo("❌ Twitter scraping not available. Install twython: pip install twython")
        return
        
    config = ctx.obj['config']
    
    click.echo(f"🐦 Scraping Twitter hashtag: #{hashtag}")
    
    try:
        scraper = TwitterScraper(config.config)
        tweets = scraper.scrape_tweets(hashtag, count)
        
        if tweets:
            exporter = DataExporter(config.config)
            
            if not output:
                output = f"twitter_{hashtag}_{int(time.time())}"
            
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
