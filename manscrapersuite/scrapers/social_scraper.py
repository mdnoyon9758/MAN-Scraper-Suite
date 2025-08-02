#!/usr/bin/env python3
"""
Enhanced Social Media Scraper
Handles scraping for Twitter (no API), Reddit (topic-based), and automatic URL generation
"""

import re
import time
import random
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote, urljoin
from typing import List, Dict, Any, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
try:
    from twython import Twython
    from praw import Reddit
except ImportError:
    Twython = None
    Reddit = None
from ..core.engine import UniversalScraper

class TwitterScraper:
    """
    Twitter scraping class - now requires authentication due to Twitter/X policy changes
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.has_credentials = self._check_twitter_credentials()
        
        if not self.has_credentials:
            print("⚠️  Twitter/X now requires authentication for scraping.")
            print("💡 Options:")
            print("   1. Use Twitter API (recommended)")
            print("   2. Manual login (not recommended for automation)")
            print("   3. Try alternative platforms like Reddit, LinkedIn, etc.")
            
    def _check_twitter_credentials(self) -> bool:
        """Check if Twitter API credentials are available"""
        twitter_config = self.config.get('social_media', {}).get('twitter', {})
        return bool(
            twitter_config.get('api_key') and 
            twitter_config.get('api_secret') and
            twitter_config.get('bearer_token')
        )

    def scrape_tweets_no_api(self, keyword: str, quantity: int = 20) -> List[Dict[str, Any]]:
        """
        Scrape tweets using Selenium without API
        """
        url = f'https://twitter.com/search?q={quote(keyword)}&src=typed_query'
        
        try:
            self.driver.get(url)
            time.sleep(3)  # Wait for page load
            
            tweets = []
            tweet_elements = self.driver.find_elements(By.CSS_SELECTOR, '[data-testid="tweet"]')
            
            for i, element in enumerate(tweet_elements[:quantity]):
                try:
                    # Extract tweet text
                    tweet_text_elem = element.find_element(By.CSS_SELECTOR, '[data-testid="tweetText"]')
                    tweet_text = tweet_text_elem.text if tweet_text_elem else "No text"
                    
                    # Extract user
                    user_elem = element.find_element(By.CSS_SELECTOR, '[data-testid="User-Names"] a')
                    username = user_elem.text if user_elem else "Unknown"
                    
                    tweets.append({
                        'tweet': tweet_text,
                        'user': username,
                        'platform': 'twitter',
                        'engagement_score': random.randint(1, 100)  # Mock engagement
                    })
                    
                except Exception as e:
                    print(f"Error extracting tweet {i}: {e}")
                    continue
            
            return tweets
            
        except Exception as e:
            print(f"Error scraping Twitter: {e}")
            return []
        
        finally:
            if hasattr(self, 'driver'):
                self.driver.quit()

class RedditScraper:
    """
    Reddit scraping class, supports topic-based search
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        # Ensure Reddit API is optional
        if Reddit:
            self.reddit = Reddit(
                client_id=self.config['social_media']['reddit'].get('client_id', ''),
                client_secret=self.config['social_media']['reddit'].get('client_secret', ''),
                user_agent=self.config['social_media']['reddit'].get('user_agent', 'MAN-SCRAPER'),
            )

    def scrape_posts_by_topic(self, topic: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Scrape posts related to a specific topic without API
        """
        try:
            # Direct Reddit search without API
            search_url = f'https://www.reddit.com/search/?q={quote(topic)}'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(search_url, headers=headers)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                posts = []
                
                # Look for post elements in HTML
                post_elements = soup.find_all('div', {'data-testid': 'post-content'})
                if not post_elements:
                    # Fallback to different selectors
                    post_elements = soup.find_all('div', class_=re.compile(r'Post'))
                
                for i, element in enumerate(post_elements[:limit]):
                    try:
                        title_elem = element.find('h3') or element.find('a')
                        title = title_elem.get_text(strip=True) if title_elem else f"Reddit post {i+1}"
                        
                        posts.append({
                            'title': title,
                            'platform': 'reddit',
                            'topic': topic,
                            'engagement_score': random.randint(1, 100)
                        })
                    except Exception as e:
                        continue
                
                return posts
            else:
                print(f"Failed to fetch Reddit data: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Error scraping Reddit: {e}")
            return []

    def scrape_subreddit_posts(self, subreddit: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Scrape subreddit posts without API using web scraping
        """
        try:
            # Use old Reddit format which is more scraping-friendly
            url = f'https://old.reddit.com/r/{subreddit}/.json?limit={limit}'
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            # Add random delay to avoid rate limiting
            time.sleep(random.uniform(1, 3))
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    posts = []
                    
                    if 'data' in data and 'children' in data['data']:
                        for post_data in data['data']['children'][:limit]:
                            if 'data' in post_data:
                                post = post_data['data']
                                posts.append({
                                    'title': post.get('title', 'No title'),
                                    'score': post.get('score', 0),
                                    'url': post.get('url', ''),
                                    'subreddit': subreddit,
                                    'author': post.get('author', 'Unknown'),
                                    'created_utc': post.get('created_utc', 0),
                                    'num_comments': post.get('num_comments', 0),
                                    'selftext': post.get('selftext', '')[:500],  # Limit text length
                                    'platform': 'reddit'
                                })
                    
                    return posts
                    
                except ValueError as e:
                    print(f"Error parsing Reddit JSON: {e}")
                    return self._fallback_html_scrape(subreddit, limit)
                    
            elif response.status_code == 429:
                print("Rate limited by Reddit. Trying with longer delay...")
                time.sleep(10)
                return self._fallback_html_scrape(subreddit, limit)
                
            else:
                print(f"Reddit API returned {response.status_code}. Trying HTML scraping...")
                return self._fallback_html_scrape(subreddit, limit)
                
        except requests.exceptions.RequestException as e:
            print(f"Network error accessing Reddit: {e}")
            return self._fallback_html_scrape(subreddit, limit)
        except Exception as e:
            print(f"Unexpected error scraping Reddit: {e}")
            return self._fallback_html_scrape(subreddit, limit)
    
    def _fallback_html_scrape(self, subreddit: str, limit: int) -> List[Dict[str, Any]]:
        """
        Fallback HTML scraping method for Reddit
        """
        try:
            url = f'https://old.reddit.com/r/{subreddit}/'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                posts = []
                
                # Find post elements
                post_elements = soup.find_all('div', class_='thing')
                
                for i, element in enumerate(post_elements[:limit]):
                    try:
                        title_elem = element.find('a', class_='title')
                        title = title_elem.get_text(strip=True) if title_elem else f"Reddit post {i+1}"
                        
                        score_elem = element.find('div', class_='score')
                        score = score_elem.get_text(strip=True) if score_elem else "0"
                        
                        author_elem = element.find('a', class_='author')
                        author = author_elem.get_text(strip=True) if author_elem else "Unknown"
                        
                        posts.append({
                            'title': title,
                            'score': score,
                            'author': author,
                            'subreddit': subreddit,
                            'platform': 'reddit',
                            'scraped_via': 'html_fallback'
                        })
                        
                    except Exception as e:
                        continue
                
                return posts
            else:
                print(f"HTML fallback also failed with status {response.status_code}")
                return []
                
        except Exception as e:
            print(f"HTML fallback error: {e}")
            return []

