"""
Python SDK Examples for Reddit Content Platform API
"""

import requests
import asyncio
import aiohttp
from typing import Optional, List, Dict, Any
from datetime import datetime


class RedditContentPlatformAPI:
    """Synchronous Python client for Reddit Content Platform API."""
    
    def __init__(self, base_url: str, access_token: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.access_token = access_token
        self.session = requests.Session()
        
        if access_token:
            self.session.headers.update({
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            })
    
    def authenticate(self, auth_code: str, state: str) -> Dict[str, Any]:
        """Exchange OAuth2 code for tokens."""
        response = self.session.post(
            f'{self.base_url}/api/v1/auth/login',
            json={'code': auth_code, 'state': state}
        )
        response.raise_for_status()
        
        tokens = response.json()
        self.access_token = tokens['access_token']
        self.session.headers.update({
            'Authorization': f'Bearer {self.access_token}'
        })
        
        return tokens
    
    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token."""
        response = self.session.post(
            f'{self.base_url}/api/v1/auth/refresh',
            headers={'Authorization': f'Bearer {refresh_token}'}
        )
        response.raise_for_status()
        
        tokens = response.json()
        self.access_token = tokens['access_token']
        self.session.headers.update({
            'Authorization': f'Bearer {self.access_token}'
        })
        
        return tokens
    
    def create_keyword(self, keyword: str, description: Optional[str] = None) -> Dict[str, Any]:
        """Create a new keyword."""
        data = {'keyword': keyword}
        if description:
            data['description'] = description
            
        response = self.session.post(f'{self.base_url}/api/v1/keywords', json=data)
        response.raise_for_status()
        return response.json()
    
    def get_keywords(self, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """Get user's keywords with pagination."""
        params = {'page': page, 'page_size': page_size}
        response = self.session.get(f'{self.base_url}/api/v1/keywords', params=params)
        response.raise_for_status()
        return response.json()
    
    def start_crawling(self, keyword_ids: List[int], limit: int = 100) -> Dict[str, Any]:
        """Start crawling for specified keywords."""
        data = {'keyword_ids': keyword_ids, 'limit': limit}
        response = self.session.post(f'{self.base_url}/api/v1/crawling/start', json=data)
        response.raise_for_status()
        return response.json()
    
    def get_crawling_status(self) -> Dict[str, Any]:
        """Get current crawling status."""
        response = self.session.get(f'{self.base_url}/api/v1/crawling/status')
        response.raise_for_status()
        return response.json()
    
    def generate_content(self, content_type: str, keyword_ids: List[int], 
                        template_id: Optional[int] = None) -> Dict[str, Any]:
        """Generate content based on keywords."""
        data = {
            'content_type': content_type,
            'keyword_ids': keyword_ids
        }
        if template_id:
            data['template_id'] = template_id
            
        response = self.session.post(f'{self.base_url}/api/v1/content/generate', json=data)
        response.raise_for_status()
        return response.json()


class AsyncRedditContentPlatformAPI:
    """Asynchronous Python client for Reddit Content Platform API."""
    
    def __init__(self, base_url: str, access_token: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.access_token = access_token
        self.headers = {'Content-Type': 'application/json'}
        
        if access_token:
            self.headers['Authorization'] = f'Bearer {access_token}'
    
    async def authenticate(self, auth_code: str, state: str) -> Dict[str, Any]:
        """Exchange OAuth2 code for tokens."""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f'{self.base_url}/api/v1/auth/login',
                json={'code': auth_code, 'state': state}
            ) as response:
                response.raise_for_status()
                tokens = await response.json()
                
                self.access_token = tokens['access_token']
                self.headers['Authorization'] = f'Bearer {self.access_token}'
                
                return tokens
    
    async def create_keyword(self, keyword: str, description: Optional[str] = None) -> Dict[str, Any]:
        """Create a new keyword."""
        data = {'keyword': keyword}
        if description:
            data['description'] = description
            
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f'{self.base_url}/api/v1/keywords',
                json=data,
                headers=self.headers
            ) as response:
                response.raise_for_status()
                return await response.json()
    
    async def start_crawling(self, keyword_ids: List[int], limit: int = 100) -> Dict[str, Any]:
        """Start crawling for specified keywords."""
        data = {'keyword_ids': keyword_ids, 'limit': limit}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f'{self.base_url}/api/v1/crawling/start',
                json=data,
                headers=self.headers
            ) as response:
                response.raise_for_status()
                return await response.json()


# Example usage
if __name__ == "__main__":
    # Synchronous example
    api = RedditContentPlatformAPI("http://localhost:8000")
    
    # After OAuth2 flow, authenticate
    # tokens = api.authenticate("auth_code", "state")
    
    # Create keywords
    keyword = api.create_keyword("artificial intelligence", "AI discussions")
    print(f"Created keyword: {keyword}")
    
    # Start crawling
    crawl_result = api.start_crawling([keyword['id']], limit=50)
    print(f"Started crawling: {crawl_result}")
    
    # Asynchronous example
    async def async_example():
        async_api = AsyncRedditContentPlatformAPI("http://localhost:8000", "your_token")
        
        keyword = await async_api.create_keyword("machine learning", "ML topics")
        print(f"Created keyword: {keyword}")
        
        crawl_result = await async_api.start_crawling([keyword['id']], limit=50)
        print(f"Started crawling: {crawl_result}")
    
    # asyncio.run(async_example())
