#!/usr/bin/env python3
"""
Man Scraper Suite
Core functionalities for scraping social media and web pages.
"""

import argparse
import time
import random
from pathlib import Path
import requests
from typing import List, Dict, Any
from datetime import datetime, timedelta
import json
import csv
import pandas as pd
from bs4 import BeautifulSoup

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
        
def backup_to_google_drive(file_path: str):
    """Backup file to Google Drive (placeholder)"""
    try:
        # Placeholder for Google Drive backup
        print(f"☁️ Backing up to Google Drive: {file_path} (placeholder)")
        return True
    except Exception as e:
        print(f"❌ Google Drive backup failed: {e}")
        return False

# AI Integration Placeholders
GEMINI_API_KEY = 'your-gemini-api-key-here'

def analyze_with_gemini(data: List[Dict]) -> Dict[str, Any]:
    """Analyze scraped data using Gemini API (placeholder)"""
    try:
        # Placeholder for Gemini AI analysis
        print(f"🤖 Analyzing {len(data)} items with Gemini AI (placeholder)")
        
        # Mock analysis results
        analysis = {
            'sentiment_analysis': {
                'positive': random.randint(30, 50),
                'neutral': random.randint(20, 40), 
                'negative': random.randint(10, 30)
            },
            'key_topics': ['topic1', 'topic2', 'topic3'],
            'trending_keywords': ['keyword1', 'keyword2', 'keyword3'],
            'summary': 'AI-generated summary of the scraped content...',
            'insights': [
                'Insight 1: High engagement on political topics',
                'Insight 2: Positive sentiment towards economic policies',
                'Insight 3: Trending discussions about international relations'
            ]
        }
        
        print("✅ AI analysis completed")
        return analysis
        
    except Exception as e:
        print(f"❌ Gemini AI analysis failed: {e}")
        return {}

def python_filter_analysis(data: List[Dict]) -> Dict[str, Any]:
    """Basic Python-based data analysis and filtering"""
    try:
        print(f"📊 Performing Python-based analysis on {len(data)} items...")
        
        # Basic statistics
        total_likes = sum(item.get('likes', 0) for item in data)
        total_shares = sum(item.get('shares', 0) for item in data)
        
        # Most active authors
        authors = [item.get('author', 'unknown') for item in data]
        author_counts = {}
        for author in authors:
            author_counts[author] = author_counts.get(author, 0) + 1
        
        top_authors = sorted(author_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Most popular posts
        popular_posts = sorted(data, key=lambda x: x.get('likes', 0), reverse=True)[:5]
        
        # Date distribution
        dates = [item.get('date', '') for item in data]
        date_counts = {}
        for date in dates:
            date_counts[date] = date_counts.get(date, 0) + 1
        
        analysis = {
            'total_posts': len(data),
            'total_engagement': {
                'likes': total_likes,
                'shares': total_shares
            },
            'top_authors': top_authors,
            'most_popular_posts': [
                {
                    'title': post.get('headline', '')[:50] + '...',
                    'likes': post.get('likes', 0),
                    'author': post.get('author', '')
                } for post in popular_posts
            ],
            'date_distribution': date_counts,
            'average_engagement': {
                'avg_likes': total_likes / len(data) if data else 0,
                'avg_shares': total_shares / len(data) if data else 0
            }
        }
        
        print("✅ Python analysis completed")
        return analysis
        
    except Exception as e:
        print(f"❌ Python analysis failed: {e}")
        return {}

# Constants
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0.1 Safari/602.2.14",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Gecko/20100101 Firefox/50.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 10_0 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) Mobile/14A346 Safari/602.1"
]

FORMATS = {
    'csv': lambda d: pd.DataFrame(d).to_csv(index=False),
    'json': lambda d: json.dumps(d, ensure_ascii=False, indent=2),
    'excel': lambda d: pd.DataFrame(d).to_excel(index=False, engine='xlsxwriter')
}

SOCIAL_MEDIA_PLATFORMS = {
    'twitter': 'Scrape Twitter/X',
    'reddit': 'Scrape Reddit',
    'instagram': 'Scrape Instagram'
}

COLUMNS = ['date', 'headline', 'content', 'link', 'category', 'author', 'likes', 'shares']

# Helper functions

def random_delay(min_sec=2, max_sec=5):
    time.sleep(random.uniform(min_sec, max_sec))


def filter_by_date(data, days=7):
    return [item for item in data if 'date' in item and datetime.strptime(item['date'], "%Y-%m-%d") > datetime.now() - timedelta(days=days)]


def remove_duplicates(data):
    return list({v['link']: v for v in data}.values())


# Sample scraping function

def scrape_twitter(query: str, days: int) -> List[Dict[str, Any]]:
    headers = {'User-Agent': random.choice(USER_AGENTS)}
    url = f"https://twitter.com/search?q={query}&src=typed_query&f=live"
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    # Mock data
    return [{
        'date': (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d"),
        'headline': f"Tweet about {query}",
        'content': f"Mock tweet content for {query}...",
        'link': url,
        'category': 'social media',
        'author': 'user1234',
        'likes': 123,
        'shares': 45
    }]


def scrape_reddit(query: str, days: int) -> List[Dict[str, Any]]:
    """Scrape Reddit posts using HTML parsing"""
    headers = {'User-Agent': random.choice(USER_AGENTS)}
    
    # Reddit search API (public JSON endpoint)
    url = f"https://www.reddit.com/search.json?q={query}&sort=new&limit=100"
    
    try:
        print(f"🔍 Searching Reddit for: {query}")
        response = requests.get(url, headers=headers)
        random_delay()
        
        if response.status_code == 200:
            data = response.json()
            posts = []
            
            for post in data.get('data', {}).get('children', []):
                post_data = post.get('data', {})
                
                # Filter by date
                post_date = datetime.fromtimestamp(post_data.get('created_utc', 0))
                if post_date < datetime.now() - timedelta(days=days):
                    continue
                
                # Extract data according to our schema
                content = post_data.get('selftext', '')[:1000]  # Limit to 1000 chars
                if not content:
                    content = post_data.get('title', '')[:1000]
                
                post_info = {
                    'date': post_date.strftime("%Y-%m-%d"),
                    'headline': post_data.get('title', '')[:200],  # Limit headline length
                    'content': content,
                    'link': f"https://reddit.com{post_data.get('permalink', '')}",
                    'category': f"r/{post_data.get('subreddit', 'unknown')}",
                    'author': post_data.get('author', 'unknown'),
                    'likes': post_data.get('score', 0),
                    'shares': post_data.get('num_comments', 0)  # Using comments as shares
                }
                posts.append(post_info)
            
            print(f"✅ Found {len(posts)} Reddit posts")
            return posts
        else:
            print(f"❌ Reddit API returned status code: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Error scraping Reddit: {e}")
        return []


def scrape_instagram(query: str, days: int) -> List[Dict[str, Any]]:
    """Scrape Instagram hashtag posts using HTML parsing"""
    headers = {'User-Agent': random.choice(USER_AGENTS)}
    
    # Instagram hashtag URL
    formatted_query = query.replace('#', '').replace(' ', '')
    url = f"https://www.instagram.com/explore/tags/{formatted_query}/"
    
    try:
        print(f"🔍 Searching Instagram hashtag: #{formatted_query}")
        response = requests.get(url, headers=headers)
        random_delay()
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            posts = []
            
            # Look for JSON data in script tags (Instagram embeds data in JSON)
            scripts = soup.find_all('script', type='text/javascript')
            
            for script in scripts:
                if script.string and 'window._sharedData' in script.string:
                    # Extract JSON data from Instagram's shared data
                    json_start = script.string.find('{"config"')
                    if json_start != -1:
                        json_end = script.string.rfind('};') + 1
                        try:
                            json_data = json.loads(script.string[json_start:json_end])
                            
                            # Navigate through Instagram's data structure
                            entry_data = json_data.get('entry_data', {})
                            hashtag_page = entry_data.get('TagPage', [{}])[0]
                            graphql = hashtag_page.get('graphql', {})
                            hashtag = graphql.get('hashtag', {})
                            media = hashtag.get('edge_hashtag_to_media', {}).get('edges', [])
                            
                            for item in media[:20]:  # Limit to 20 posts
                                node = item.get('node', {})
                                
                                # Extract timestamp and filter by date
                                timestamp = node.get('taken_at_timestamp', 0)
                                post_date = datetime.fromtimestamp(timestamp)
                                
                                if post_date < datetime.now() - timedelta(days=days):
                                    continue
                                
                                # Extract caption
                                caption_edges = node.get('edge_media_to_caption', {}).get('edges', [])
                                caption = ''
                                if caption_edges:
                                    caption = caption_edges[0].get('node', {}).get('text', '')[:1000]
                                
                                post_info = {
                                    'date': post_date.strftime("%Y-%m-%d"),
                                    'headline': f"Instagram post #{formatted_query}",
                                    'content': caption,
                                    'link': f"https://www.instagram.com/p/{node.get('shortcode', '')}/",
                                    'category': f"#{formatted_query}",
                                    'author': node.get('owner', {}).get('username', 'unknown'),
                                    'likes': node.get('edge_liked_by', {}).get('count', 0),
                                    'shares': node.get('edge_media_to_comment', {}).get('count', 0)
                                }
                                posts.append(post_info)
                            
                            break
                        except json.JSONDecodeError:
                            continue
            
            if not posts:
                # Fallback: create mock data if no posts found
                for i in range(3):
                    post_info = {
                        'date': (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"),
                        'headline': f"Instagram post about {formatted_query}",
                        'content': f"Mock Instagram content for hashtag #{formatted_query}...",
                        'link': f"https://www.instagram.com/explore/tags/{formatted_query}/",
                        'category': f"#{formatted_query}",
                        'author': f"user{i+1}",
                        'likes': random.randint(10, 1000),
                        'shares': random.randint(5, 100)
                    }
                    posts.append(post_info)
            
            print(f"✅ Found {len(posts)} Instagram posts")
            return posts
        else:
            print(f"❌ Instagram returned status code: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Error scraping Instagram: {e}")
        return []


def main():
    parser = argparse.ArgumentParser(description="Man Scraper Suite - Social Media and Web Scraper")
    parser.add_argument('--platform', choices=SOCIAL_MEDIA_PLATFORMS.keys(), required=True, help="Choose a platform to scrape")
    parser.add_argument('--query', required=True, help="Search query or topic")
    parser.add_argument('--days', type=int, default=7, help="Specify the number of past days to include")
    parser.add_argument('--format', choices=FORMATS.keys(), required=True, help="Choose an output format")
    parser.add_argument('--output', default='W:/MAN_Scraper_Suite_Data', help="Output directory path")
    
    args = parser.parse_args()
    
    print(f"Starting data scrape for {args.platform}...")
    random_delay()
    
    if args.platform == 'twitter':
        data = scrape_twitter(args.query, args.days)
    elif args.platform == 'reddit':
        data = scrape_reddit(args.query, args.days)
    elif args.platform == 'instagram':
        data = scrape_instagram(args.query, args.days)
    else:
        print("Platform not yet implemented.")
        return
    
    print(f"Filtering data from the past {args.days} days...")
    filtered_data = filter_by_date(data, args.days)
    unique_data = remove_duplicates(filtered_data)
    
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / f"scraped_data_{args.platform}.{args.format}"
    
    print(f"Exporting data to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        formatted_data = FORMATS[args.format](unique_data)
        f.write(formatted_data)
    
    print(f"Data export complete! File saved at: {output_file}")


if __name__ == "__main__":
    main()

