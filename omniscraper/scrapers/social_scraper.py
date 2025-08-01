#!/usr/bin/env python3
"""
Social Media Scraper
Handles scraping for Twitter and Reddit
"""

from typing import List, Dict, Any
from twython import Twython
from praw import Reddit
from ..core.engine import UniversalScraper

class TwitterScraper:
    """
    Twitter scraping class, supports tweets, users, and hashtags
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.twitter = Twython(
            self.config['social_media']['twitter']['api_key'],
            self.config['social_media']['twitter']['api_secret'],
            oauth_version=2
        )
        self.twitter.authenticate()

    def scrape_tweets(self, hashtag: str, count: int = 100) -> List[Dict[str, Any]]:
        """
        Scrape tweets by hashtag
        """
        results = self.twitter.search(q=f"#{hashtag}", count=count)
        return [
            {
                'tweet': t['text'],
                'user': t['user']['screen_name'],
                'date': t['created_at'],
                'retweets': t['retweet_count'],
                'favorites': t['favorite_count']
            } for t in results['statuses']
        ]

class RedditScraper:
    """
    Reddit scraping class, supports posts and comments
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.reddit = Reddit(
            client_id=self.config['social_media']['reddit']['client_id'],
            client_secret=self.config['social_media']['reddit']['client_secret'],
            user_agent=self.config['social_media']['reddit']['user_agent'],
        )

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

