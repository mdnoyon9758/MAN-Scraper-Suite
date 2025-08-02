#!/usr/bin/env python3
"""
URL Auto-Generator
Automatically generates URLs based on topics using AI and smart patterns
"""

import re
from typing import List, Dict, Any, Optional
from urllib.parse import quote
from ..ai.ai_engine import AIEngine

class URLGenerator:
    """Generate URLs automatically based on topics and search patterns"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.ai_engine = AIEngine(config)
        
        # Common website patterns for different types of content
        self.site_patterns = {
            'news': [
                'https://www.google.com/search?q={topic}+news&tbm=nws',
                'https://news.google.com/search?q={topic}',
                'https://www.bing.com/news/search?q={topic}',
            ],
            'social': [
                'https://twitter.com/search?q={topic}',
                'https://www.reddit.com/search/?q={topic}',
                'https://www.instagram.com/explore/tags/{hashtag}/',
            ],
            'academic': [
                'https://scholar.google.com/scholar?q={topic}',
                'https://www.researchgate.net/search?q={topic}',
                'https://arxiv.org/search/?query={topic}',
            ],
            'shopping': [
                'https://www.google.com/search?q={topic}&tbm=shop',
                'https://www.amazon.com/s?k={topic}',
                'https://www.ebay.com/sch/i.html?_nkw={topic}',
            ],
            'images': [
                'https://www.google.com/search?q={topic}&tbm=isch',
                'https://www.bing.com/images/search?q={topic}',
                'https://unsplash.com/s/photos/{topic}',
            ],
            'videos': [
                'https://www.youtube.com/results?search_query={topic}',
                'https://vimeo.com/search?q={topic}',
                'https://www.dailymotion.com/search/{topic}',
            ]
        }
    
    def generate_urls_by_topic(self, topic: str, content_type: str = 'general', limit: int = 5) -> List[str]:
        """
        Generate URLs based on topic and content type
        """
        generated_urls = []
        
        # Clean and format topic
        clean_topic = self._clean_topic(topic)
        hashtag_topic = self._to_hashtag(topic)
        
        if content_type in self.site_patterns:
            patterns = self.site_patterns[content_type]
            for pattern in patterns[:limit]:
                url = pattern.format(topic=quote(clean_topic), hashtag=hashtag_topic)
                generated_urls.append(url)
        else:
            # General search patterns
            general_patterns = [
                f'https://www.google.com/search?q={quote(clean_topic)}',
                f'https://www.bing.com/search?q={quote(clean_topic)}',
                f'https://duckduckgo.com/?q={quote(clean_topic)}',
                f'https://en.wikipedia.org/wiki/Special:Search?search={quote(clean_topic)}',
                f'https://www.reddit.com/search/?q={quote(clean_topic)}',
            ]
            generated_urls.extend(general_patterns[:limit])
        
        return generated_urls
    
    def ai_generate_urls(self, topic: str, context: str = "") -> List[str]:
        """
        Use AI to generate smart, targeted URLs
        """
        if not self.ai_engine.enabled:
            return self.generate_urls_by_topic(topic)
        
        try:
            prompt = f"""
            Generate 5-7 specific URLs for scraping information about: "{topic}"
            {f"Context: {context}" if context else ""}
            
            Requirements:
            1. Focus on reliable, scrapable websites
            2. Include diverse source types (news, official sites, forums)
            3. Avoid sites that require login or have heavy anti-scraping
            4. Prioritize sites likely to have recent, relevant content
            
            Return only the URLs, one per line, no explanations.
            Format: https://example.com/search?q=topic
            """
            
            response = self.ai_engine._call_ai_api(prompt)
            if response:
                # Extract URLs from AI response
                urls = []
                for line in response.split('\n'):
                    line = line.strip()
                    if line.startswith('http'):
                        urls.append(line)
                
                if urls:
                    return urls[:7]  # Limit to 7 URLs
                    
        except Exception as e:
            print(f"AI URL generation failed: {e}")
        
        # Fallback to pattern-based generation
        return self.generate_urls_by_topic(topic)
    
    def generate_social_urls(self, topic: str) -> Dict[str, List[str]]:
        """
        Generate social media specific URLs
        """
        clean_topic = self._clean_topic(topic)
        hashtag_topic = self._to_hashtag(topic)
        
        return {
            'twitter': [
                f'https://twitter.com/search?q={quote(clean_topic)}',
                f'https://twitter.com/search?q=%23{hashtag_topic}',
                f'https://twitter.com/search?q={quote(clean_topic)}%20filter%3Alinks',
            ],
            'reddit': [
                f'https://www.reddit.com/search/?q={quote(clean_topic)}',
                f'https://www.reddit.com/r/all/search/?q={quote(clean_topic)}',
            ],
            'instagram': [
                f'https://www.instagram.com/explore/tags/{hashtag_topic}/',
            ],
            'linkedin': [
                f'https://www.linkedin.com/search/results/content/?keywords={quote(clean_topic)}',
            ]
        }
    
    def generate_news_urls(self, topic: str, time_range: str = 'recent') -> List[str]:
        """
        Generate news-specific URLs with time filtering
        """
        clean_topic = self._clean_topic(topic)
        
        urls = [
            f'https://news.google.com/search?q={quote(clean_topic)}',
            f'https://www.bing.com/news/search?q={quote(clean_topic)}',
        ]
        
        # Add time-based Google search
        if time_range == 'recent':
            urls.append(f'https://www.google.com/search?q={quote(clean_topic)}&tbm=nws&tbs=qdr:d')
        elif time_range == 'week':
            urls.append(f'https://www.google.com/search?q={quote(clean_topic)}&tbm=nws&tbs=qdr:w')
        elif time_range == 'month':
            urls.append(f'https://www.google.com/search?q={quote(clean_topic)}&tbm=nws&tbs=qdr:m')
        
        return urls
    
    def generate_location_specific_urls(self, topic: str, location: str) -> List[str]:
        """
        Generate location-specific URLs
        """
        clean_topic = self._clean_topic(topic)
        clean_location = self._clean_topic(location)
        
        combined_query = f"{clean_topic} {clean_location}"
        
        return [
            f'https://www.google.com/search?q={quote(combined_query)}',
            f'https://www.google.com/search?q={quote(combined_query)}&tbm=nws',
            f'https://maps.google.com/search/{quote(combined_query)}',
            f'https://www.bing.com/search?q={quote(combined_query)}',
            f'https://www.reddit.com/search/?q={quote(combined_query)}',
        ]
    
    def _clean_topic(self, topic: str) -> str:
        """Clean and normalize topic for URL generation"""
        # Remove special characters except spaces and hyphens
        cleaned = re.sub(r'[^\w\s\-]', '', topic)
        # Replace multiple spaces with single space
        cleaned = re.sub(r'\s+', ' ', cleaned)
        return cleaned.strip()
    
    def _to_hashtag(self, topic: str) -> str:
        """Convert topic to hashtag format"""
        # Remove spaces and special characters, keep only alphanumeric
        hashtag = re.sub(r'[^\w]', '', topic)
        return hashtag.lower()
    
    def validate_generated_urls(self, urls: List[str]) -> List[str]:
        """
        Validate generated URLs and remove invalid ones
        """
        valid_urls = []
        
        for url in urls:
            if self._is_valid_url(url):
                valid_urls.append(url)
        
        return valid_urls
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid"""
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        return url_pattern.match(url) is not None
