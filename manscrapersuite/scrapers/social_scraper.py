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
    Twitter scraping class without API keys, uses Selenium
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config

        # Setup Selenium WebDriver with headless options
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        self.driver = webdriver.Chrome(options=chrome_options)

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
        Scrape subreddit posts
        """
        subreddit_obj = self.reddit.subreddit(subreddit)
        return [
            {
                'title': post.title,
                'score': post.score,
                'url': post.url,
                'id': post.id,
                'comments': len(post.comments)
            } for post in subreddit_obj.hot(limit=limit)
        ]

