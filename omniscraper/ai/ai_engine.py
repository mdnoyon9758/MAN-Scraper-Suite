#!/usr/bin/env python3
"""
AI Engine for MAN Scraper Suite
Integrates with Google Gemini and DeepSeek APIs for intelligent data processing
Features dual API fallback system and AI-powered search capabilities
"""

import os
import json
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, date
import requests
import logging

class AIEngine:
    """AI-powered data processing with dual API system (Gemini + DeepSeek)"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Secure API key handling
        self.gemini_api_key = self._get_secure_api_key('gemini')
        self.deepseek_api_key = self._get_secure_api_key('deepseek')
        
        # API endpoints
        self.gemini_base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.deepseek_base_url = "https://api.deepseek.com/v1"
        
        # API status tracking
        self.gemini_active = bool(self.gemini_api_key)
        self.deepseek_active = bool(self.deepseek_api_key)
        self.daily_limit_reached = False
        self.current_date = date.today()
        
        # Models
        self.gemini_model = "gemini-1.5-flash"
        self.deepseek_model = "deepseek-chat"
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        self._initialize_status()
    
    def _get_secure_api_key(self, api_type: str) -> Optional[str]:
        """Securely get API key from environment or config"""
        if api_type == 'gemini':
            # Try environment first for security
            key = os.getenv('GEMINI_API_KEY')
            if key:
                return key
            # Fallback to config if needed (not recommended for production)
            return self.config.get('ai', {}).get('gemini_api_key')
        
        elif api_type == 'deepseek':
            # Try environment first for security
            key = os.getenv('DEEPSEEK_API_KEY')
            if key:
                return key
            # Fallback to config if needed (not recommended for production)
            return self.config.get('ai', {}).get('deepseek_api_key')
        
        return None
    
    def _initialize_status(self):
        """Initialize AI engine status"""
        if self.gemini_active and self.deepseek_active:
            print("✅ AI Engine initialized with dual API system (Gemini + DeepSeek)")
        elif self.gemini_active:
            print("✅ AI Engine initialized with Gemini API only")
        elif self.deepseek_active:
            print("✅ AI Engine initialized with DeepSeek API only")
        else:
            print("⚠️ AI Engine disabled - No API keys found")
            print("💡 Set GEMINI_API_KEY or DEEPSEEK_API_KEY environment variables")
    
    def _check_daily_reset(self):
        """Check if we need to reset daily limits"""
        current_date = date.today()
        if current_date != self.current_date:
            self.current_date = current_date
            self.daily_limit_reached = False
            self.gemini_active = bool(self.gemini_api_key)
            self.deepseek_active = bool(self.deepseek_api_key)
            self.logger.info("Daily API limits reset")
    
    @property
    def enabled(self) -> bool:
        """Check if AI engine is enabled"""
        self._check_daily_reset()
        return (self.gemini_active or self.deepseek_active) and not self.daily_limit_reached
    
    def ai_powered_search(self, topic: str, context: str = "") -> Dict[str, Any]:
        """AI-powered search query generation for focused results"""
        if not self.enabled:
            return self._basic_search_query(topic)
        
        try:
            prompt = f"""
            Generate focused search queries for the topic: "{topic}"
            {f"Context: {context}" if context else ""}
            
            Create search queries that will find ONLY information directly related to "{topic}".
            Do not include associated or related topics unless specifically mentioned.
            
            For example, if topic is "Feni Bangladesh", search for Feni district/area in Bangladesh,
            not general Bangladesh information or other topics.
            
            Provide response as JSON with:
            - primary_query: main search term
            - specific_queries: list of 3-5 specific search phrases
            - exclude_terms: terms to avoid in results
            - location_focus: if applicable, location-specific terms
            - time_relevance: recent, historical, or any
            
            Return only valid JSON.
            """
            
            response = self._call_ai_api(prompt)
            if response:
                try:
                    search_data = json.loads(response)
                    search_data['ai_generated'] = True
                    search_data['timestamp'] = datetime.now().isoformat()
                    return search_data
                except json.JSONDecodeError:
                    pass
            
        except Exception as e:
            self.logger.error(f"AI search generation failed: {e}")
        
        return self._basic_search_query(topic)
    
    def _basic_search_query(self, topic: str) -> Dict[str, Any]:
        """Generate basic search query without AI"""
        return {
            'primary_query': topic,
            'specific_queries': [
                topic,
                f'"{topic}"',
                f'{topic} news',
                f'{topic} information',
                f'{topic} updates'
            ],
            'exclude_terms': ['advertisement', 'sponsored', 'ad'],
            'location_focus': '',
            'time_relevance': 'recent',
            'ai_generated': False,
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_api_key(self) -> Optional[str]:
        """Get Gemini API key from config or environment"""
        # Try config first
        api_key = self.config.get('ai', {}).get('gemini_api_key')
        if api_key:
            return api_key
        
        # Try environment variable
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            return api_key
        
        return None
    
    def analyze_scraped_data(self, data: List[Dict[str, Any]], topic: str) -> Dict[str, Any]:
        """Analyze scraped data using AI"""
        if not self.enabled:
            return self._fallback_analysis(data, topic)
        
        try:
            # Prepare data summary for AI
            data_summary = self._prepare_data_summary(data)
            
            prompt = f"""
            Analyze this scraped data about "{topic}":
            
            Data Summary:
            {data_summary}
            
            Please provide:
            1. Key insights and trends
            2. Data quality assessment (1-10)
            3. Most relevant sources
            4. Potential issues or biases
            5. Suggestions for improvement
            
            Format as JSON with keys: insights, quality_score, top_sources, issues, suggestions
            """
            
            response = self._call_ai_api(prompt)
            if response:
                try:
                    analysis = json.loads(response)
                    analysis['ai_processed'] = True
                    analysis['timestamp'] = datetime.now().isoformat()
                    return analysis
                except json.JSONDecodeError:
                    # If not valid JSON, create structured response
                    return {
                        'insights': response[:500] + "..." if len(response) > 500 else response,
                        'quality_score': 7,
                        'ai_processed': True,
                        'timestamp': datetime.now().isoformat()
                    }
            
        except Exception as e:
            print(f"❌ AI analysis failed: {e}")
        
        return self._fallback_analysis(data, topic)
    
    def smart_filter_data(self, data: List[Dict[str, Any]], criteria: str) -> List[Dict[str, Any]]:
        """Intelligently filter data based on criteria"""
        if not self.enabled or not data:
            return self._basic_filter(data, criteria)
        
        try:
            # Sample first few items for AI analysis
            sample_data = data[:5]
            sample_text = json.dumps(sample_data, indent=2)[:2000]
            
            prompt = f"""
            Given this sample data:
            {sample_text}
            
            Filter criteria: "{criteria}"
            
            Provide filtering rules as JSON with:
            1. keywords_include: list of keywords that should be present
            2. keywords_exclude: list of keywords to exclude
            3. quality_threshold: minimum quality score (1-10)
            4. source_preference: preferred source types
            
            Return only valid JSON.
            """
            
            response = self._call_ai_api(prompt)
            if response:
                try:
                    filter_rules = json.loads(response)
                    return self._apply_smart_filter(data, filter_rules)
                except json.JSONDecodeError:
                    pass
            
        except Exception as e:
            print(f"❌ Smart filtering failed: {e}")
        
        return self._basic_filter(data, criteria)
    
    def generate_summary(self, data: List[Dict[str, Any]], topic: str) -> str:
        """Generate AI-powered summary of scraped data"""
        if not self.enabled:
            return self._basic_summary(data, topic)
        
        try:
            # Prepare content for summarization
            content_items = []
            for item in data[:10]:  # Limit to first 10 items
                title = item.get('title', '')
                content = item.get('content', '')
                source = item.get('source', '')
                content_items.append(f"Title: {title}\nContent: {content[:200]}...\nSource: {source}")
            
            combined_content = "\n\n".join(content_items)
            
            prompt = f"""
            Create a comprehensive summary of this scraped data about "{topic}":
            
            {combined_content}
            
            Provide a clear, informative summary that includes:
            1. Main themes and topics
            2. Key findings
            3. Source diversity
            4. Overall sentiment
            
            Keep it concise but informative (200-300 words).
            """
            
            response = self._call_ai_api(prompt)
            if response:
                return response
            
        except Exception as e:
            print(f"❌ AI summary generation failed: {e}")
        
        return self._basic_summary(data, topic)
    
    def detect_sentiment(self, text: str) -> Dict[str, Any]:
        """Detect sentiment of text using AI"""
        if not self.enabled:
            return {'sentiment': 'neutral', 'confidence': 0.5, 'ai_processed': False}
        
        try:
            prompt = f"""
            Analyze the sentiment of this text:
            "{text[:500]}"
            
            Provide sentiment analysis as JSON with:
            - sentiment: positive/negative/neutral
            - confidence: 0.0 to 1.0
            - key_emotions: list of detected emotions
            
            Return only valid JSON.
            """
            
            response = self._call_gemini_api(prompt)
            if response:
                try:
                    sentiment_data = json.loads(response)
                    sentiment_data['ai_processed'] = True
                    return sentiment_data
                except json.JSONDecodeError:
                    pass
                    
        except Exception as e:
            print(f"❌ Sentiment analysis failed: {e}")
        
        return {'sentiment': 'neutral', 'confidence': 0.5, 'ai_processed': False}
    
    def _call_ai_api(self, prompt: str) -> Optional[str]:
        """Make API call with dual fallback system"""
        # Try Gemini first if available
        if self.gemini_active:
            result = self._call_gemini_api(prompt)
            if result:
                return result
            else:
                # If Gemini fails, mark as inactive for this session
                self.gemini_active = False
        
        # Try DeepSeek as fallback
        if self.deepseek_active:
            result = self._call_deepseek_api(prompt)
            if result:
                return result
            else:
                self.deepseek_active = False
        
        return None
    
    def _call_gemini_api(self, prompt: str) -> Optional[str]:
        """Make API call to Gemini"""
        if not self.gemini_api_key:
            return None
        
        try:
            url = f"{self.gemini_base_url}/models/{self.gemini_model}:generateContent"
            
            headers = {
                'Content-Type': 'application/json',
            }
            
            data = {
                'contents': [
                    {
                        'parts': [
                            {'text': prompt}
                        ]
                    }
                ],
                'generationConfig': {
                    'temperature': 0.7,
                    'maxOutputTokens': 1000,
                }
            }
            
            response = requests.post(
                f"{url}?key={self.gemini_api_key}",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and result['candidates']:
                    content = result['candidates'][0]['content']['parts'][0]['text']
                    return content.strip()
            elif response.status_code == 429:
                # Rate limit reached
                self.daily_limit_reached = True
                print("⚠️ Daily API limit reached for Gemini")
            else:
                print(f"❌ Gemini API error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Gemini API call failed: {e}")
        
        return None
    
    def _call_deepseek_api(self, prompt: str) -> Optional[str]:
        """Make API call to DeepSeek"""
        if not self.deepseek_api_key:
            return None
        
        try:
            url = f"{self.deepseek_base_url}/chat/completions"
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.deepseek_api_key}'
            }
            
            data = {
                'model': self.deepseek_model,
                'messages': [
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'temperature': 0.7,
                'max_tokens': 1000
            }
            
            response = requests.post(
                url,
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and result['choices']:
                    content = result['choices'][0]['message']['content']
                    return content.strip()
            elif response.status_code == 429:
                # Rate limit reached
                self.daily_limit_reached = True
                print("⚠️ Daily API limit reached for DeepSeek")
            else:
                print(f"❌ DeepSeek API error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ DeepSeek API call failed: {e}")
        
        return None
    
    def _prepare_data_summary(self, data: List[Dict[str, Any]]) -> str:
        """Prepare a summary of data for AI analysis"""
        if not data:
            return "No data available"
        
        platforms = set()
        sources = set()
        total_content = 0
        
        for item in data:
            platforms.add(item.get('platform', 'unknown'))
            sources.add(item.get('source', 'unknown'))
            content_length = len(item.get('content', ''))
            total_content += content_length
        
        avg_content_length = total_content // len(data) if data else 0
        
        return f"""
        Total items: {len(data)}
        Platforms: {', '.join(platforms)}
        Sources: {', '.join(sources)}
        Average content length: {avg_content_length} characters
        
        Sample titles:
        {chr(10).join([item.get('title', 'No title')[:100] for item in data[:3]])}
        """
    
    def _fallback_analysis(self, data: List[Dict[str, Any]], topic: str) -> Dict[str, Any]:
        """Fallback analysis without AI"""
        platforms = {}
        sources = {}
        total_engagement = 0
        
        for item in data:
            platform = item.get('platform', 'unknown')
            source = item.get('source', 'unknown')
            engagement = item.get('engagement_score', 0)
            
            platforms[platform] = platforms.get(platform, 0) + 1
            sources[source] = sources.get(source, 0) + 1
            total_engagement += engagement
        
        avg_engagement = total_engagement / len(data) if data else 0
        
        return {
            'insights': f"Found {len(data)} items about {topic} from {len(platforms)} platforms",
            'quality_score': min(10, max(1, int(avg_engagement / 10))),
            'top_sources': list(sources.keys())[:3],
            'platform_distribution': platforms,
            'ai_processed': False,
            'timestamp': datetime.now().isoformat()
        }
    
    def _basic_filter(self, data: List[Dict[str, Any]], criteria: str) -> List[Dict[str, Any]]:
        """Basic filtering without AI"""
        if not criteria:
            return data
        
        keywords = criteria.lower().split()
        filtered_data = []
        
        for item in data:
            title = item.get('title', '').lower()
            content = item.get('content', '').lower()
            
            # Check if any keyword is present
            if any(keyword in title or keyword in content for keyword in keywords):
                filtered_data.append(item)
        
        return filtered_data
    
    def _apply_smart_filter(self, data: List[Dict[str, Any]], rules: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply AI-generated filter rules"""
        filtered_data = []
        
        include_keywords = [kw.lower() for kw in rules.get('keywords_include', [])]
        exclude_keywords = [kw.lower() for kw in rules.get('keywords_exclude', [])]
        quality_threshold = rules.get('quality_threshold', 0)
        
        for item in data:
            title = item.get('title', '').lower()
            content = item.get('content', '').lower()
            text = f"{title} {content}"
            quality = item.get('engagement_score', 0)
            
            # Check include keywords
            if include_keywords and not any(kw in text for kw in include_keywords):
                continue
            
            # Check exclude keywords
            if exclude_keywords and any(kw in text for kw in exclude_keywords):
                continue
            
            # Check quality threshold
            if quality < quality_threshold:
                continue
            
            filtered_data.append(item)
        
        return filtered_data
    
    def _basic_summary(self, data: List[Dict[str, Any]], topic: str) -> str:
        """Basic summary without AI"""
        if not data:
            return f"No data found for topic: {topic}"
        
        platforms = set(item.get('platform', 'unknown') for item in data)
        sources = set(item.get('source', 'unknown') for item in data)
        
        return f"""
        Summary for "{topic}":
        
        • Found {len(data)} items from {len(platforms)} platforms
        • Sources include: {', '.join(list(sources)[:3])}
        • Data collected from: {', '.join(platforms)}
        • Average engagement score: {sum(item.get('engagement_score', 0) for item in data) / len(data):.1f}
        
        This summary was generated using basic analysis. Enable AI features for more detailed insights.
        """
