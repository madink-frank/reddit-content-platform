#!/usr/bin/env python3
"""
API Documentation Generator

This script generates comprehensive API documentation including:
- OpenAPI/Swagger JSON schema
- Postman collection updates
- API documentation markdown files
- Code examples in multiple languages
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any
import asyncio
from datetime import datetime

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app
from app.core.config import settings
from app.core.openapi_config import (
    get_openapi_config, 
    get_enhanced_openapi_examples, 
    get_api_documentation_config,
    get_api_schema_examples
)


def generate_openapi_schema() -> Dict[str, Any]:
    """Generate the complete OpenAPI schema."""
    print("🔧 Generating OpenAPI schema...")
    
    # Get the OpenAPI schema from the FastAPI app
    openapi_schema = app.openapi()
    
    # Enhance with additional documentation
    config = get_openapi_config()
    doc_config = get_api_documentation_config()
    enhanced_examples = get_enhanced_openapi_examples()
    schema_examples = get_api_schema_examples()
    
    # Add enhanced features
    openapi_schema.update({
        "x-tagGroups": doc_config["x-tagGroups"],
        "x-code-samples": doc_config["x-code-samples"],
        "x-examples": enhanced_examples,
        "x-schema-examples": schema_examples,
        "x-rate-limits": {
            "general": "60 requests per minute per user",
            "reddit_api": "60 requests per minute (shared)",
            "content_generation": "10 requests per hour per user",
            "public_api": "100 requests per minute per IP"
        },
        "x-api-guidelines": {
            "authentication": {
                "description": "All endpoints except public blog API require authentication",
                "token_lifetime": "Access tokens expire in 15 minutes, refresh tokens in 7 days",
                "best_practices": [
                    "Store tokens securely",
                    "Implement automatic token refresh",
                    "Handle 401 responses gracefully"
                ]
            },
            "pagination": {
                "description": "List endpoints support pagination",
                "parameters": ["page", "page_size", "limit", "offset"],
                "max_page_size": 100,
                "default_page_size": 20
            },
            "error_handling": {
                "description": "All errors follow consistent format",
                "include_request_id": True,
                "retry_strategy": "Exponential backoff for 5xx errors"
            }
        }
    })
    
    return openapi_schema


def save_openapi_schema(schema: Dict[str, Any]) -> None:
    """Save OpenAPI schema to file."""
    output_dir = Path("docs/api")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    schema_file = output_dir / "openapi.json"
    with open(schema_file, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2, ensure_ascii=False)
    
    print(f"✅ OpenAPI schema saved to {schema_file}")


def update_postman_collection() -> None:
    """Update the Postman collection with latest API changes."""
    print("🔧 Updating Postman collection...")
    
    collection_file = Path("postman/Reddit_Content_Platform_API.postman_collection.json")
    
    if not collection_file.exists():
        print(f"❌ Postman collection not found at {collection_file}")
        return
    
    # Load existing collection
    with open(collection_file, "r", encoding="utf-8") as f:
        collection = json.load(f)
    
    # Update collection metadata
    collection["info"]["description"] = f"""Complete API collection for Reddit Content Crawling and Trend Analysis Platform

## Version Information
- **API Version**: {settings.VERSION}
- **Generated**: {datetime.utcnow().isoformat()}Z
- **Base URL**: {{{{base_url}}}}

## Authentication

This API uses Reddit OAuth2 for authentication and JWT tokens for authorization.

### Setup Instructions

1. **Environment Variables**: Set up the following variables in your Postman environment:
   - `base_url`: Your API base URL (e.g., `http://localhost:8000` or `https://your-domain.com`)
   - `access_token`: JWT access token (will be set automatically after login)
   - `refresh_token`: JWT refresh token (will be set automatically after login)

2. **Authentication Flow**:
   - Use the "Initiate Login" request to start OAuth2 flow
   - Complete Reddit authorization in browser
   - Use "Login with Code" or callback to get tokens
   - Tokens will be automatically set in environment variables

3. **Token Management**:
   - Access tokens expire in {settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES} minutes
   - Use "Refresh Token" request to get new access tokens
   - Refresh tokens are valid for {settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS} days

### Rate Limits

- General API: 60 requests per minute per user
- Reddit API: 60 requests per minute (shared across all users)
- Content Generation: 10 requests per hour per user
- Public Blog API: 100 requests per minute per IP (no auth required)

### Error Handling

All endpoints return consistent error responses with the following structure:

```json
{{
  "error_code": "error_type",
  "message": "Human readable error message",
  "details": {{"field_name": ["Specific validation errors"]}},
  "timestamp": "2024-01-01T00:00:00Z",
  "request_id": "uuid-v4-string"
}}
```

### API Versioning

This API uses URL path versioning:
- **Current Version**: `/api/v1/`
- **Version Header**: `Accept: application/vnd.reddit-platform.v1+json` (optional)
- **Custom Header**: `X-API-Version: v1` (alternative)

### Best Practices

1. **Authentication**:
   - Store tokens securely
   - Implement automatic token refresh
   - Handle token expiration gracefully
   - Use HTTPS in production

2. **API Usage**:
   - Use pagination for large datasets
   - Implement exponential backoff for retries
   - Cache responses when appropriate
   - Monitor rate limits
   - Use specific error handling for different status codes

3. **Performance**:
   - Use bulk operations when available
   - Filter results at the API level
   - Use async/await for concurrent requests
   - Implement request timeouts
"""
    
    # Add version information to collection
    collection["info"]["version"] = settings.VERSION
    collection["info"]["schema"] = "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
    
    # Update variables in collection
    if "variable" not in collection:
        collection["variable"] = []
    
    # Add or update base URL variable
    base_url_var = next((var for var in collection["variable"] if var["key"] == "base_url"), None)
    if base_url_var:
        base_url_var["value"] = "{{base_url}}"
        base_url_var["description"] = "Base URL for the API (set in environment)"
    else:
        collection["variable"].append({
            "key": "base_url",
            "value": "{{base_url}}",
            "description": "Base URL for the API (set in environment)",
            "type": "string"
        })
    
    # Save updated collection
    with open(collection_file, "w", encoding="utf-8") as f:
        json.dump(collection, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Postman collection updated at {collection_file}")


def update_postman_environment() -> None:
    """Update the Postman environment with latest configuration."""
    print("🔧 Updating Postman environment...")
    
    env_file = Path("postman/Reddit_Content_Platform_Environment.postman_environment.json")
    
    if not env_file.exists():
        print(f"❌ Postman environment not found at {env_file}")
        return
    
    # Load existing environment
    with open(env_file, "r", encoding="utf-8") as f:
        environment = json.load(f)
    
    # Update environment metadata
    environment["name"] = "Reddit Content Platform Environment"
    environment["_postman_exported_at"] = datetime.utcnow().isoformat() + ".000Z"
    
    # Ensure all required variables exist
    required_vars = [
        {
            "key": "base_url",
            "value": "http://localhost:8000",
            "description": "Base URL for the API (change to your deployment URL)",
            "enabled": True,
            "type": "default"
        },
        {
            "key": "access_token",
            "value": "",
            "description": "JWT access token (automatically set after login)",
            "enabled": True,
            "type": "secret"
        },
        {
            "key": "refresh_token",
            "value": "",
            "description": "JWT refresh token (automatically set after login)",
            "enabled": True,
            "type": "secret"
        },
        {
            "key": "user_id",
            "value": "",
            "description": "Current user ID (automatically set after login)",
            "enabled": True,
            "type": "default"
        },
        {
            "key": "reddit_username",
            "value": "",
            "description": "Reddit username (automatically set after login)",
            "enabled": True,
            "type": "default"
        },
        {
            "key": "api_version",
            "value": "v1",
            "description": "API version to use",
            "enabled": True,
            "type": "default"
        }
    ]
    
    # Update or add variables
    existing_keys = {var["key"] for var in environment["values"]}
    
    for required_var in required_vars:
        if required_var["key"] not in existing_keys:
            environment["values"].append(required_var)
        else:
            # Update existing variable (preserve value if it exists)
            for var in environment["values"]:
                if var["key"] == required_var["key"]:
                    var["description"] = required_var["description"]
                    var["enabled"] = required_var["enabled"]
                    var["type"] = required_var["type"]
                    # Only update value if it's empty or default
                    if not var.get("value") or var["key"] == "api_version":
                        var["value"] = required_var["value"]
                    break
    
    # Save updated environment
    with open(env_file, "w", encoding="utf-8") as f:
        json.dump(environment, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Postman environment updated at {env_file}")


def generate_api_documentation() -> None:
    """Generate comprehensive API documentation."""
    print("🔧 Generating API documentation...")
    
    docs_dir = Path("docs/api")
    docs_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate main API documentation
    api_docs = f"""# Reddit Content Platform API Documentation

**Version**: {settings.VERSION}  
**Generated**: {datetime.utcnow().isoformat()}Z  
**Base URL**: `{settings.API_V1_STR}`

## Overview

The Reddit Content Platform API provides comprehensive functionality for:

- **Authentication**: Reddit OAuth2 integration with JWT tokens
- **Keyword Management**: Track specific topics and keywords
- **Content Crawling**: Automated Reddit post collection
- **Trend Analysis**: AI-powered analysis of collected data
- **Content Generation**: Automated blog post creation
- **Public Blog API**: Public endpoints for blog site integration
- **System Monitoring**: Health checks and metrics

## Quick Start

### 1. Authentication

```bash
# Start OAuth2 flow
curl -X GET "http://localhost:8000/api/v1/auth/login"

# Exchange code for tokens (after OAuth callback)
curl -X POST "http://localhost:8000/api/v1/auth/login" \\
  -H "Content-Type: application/json" \\
  -d '{{"code": "your_auth_code", "state": "your_state"}}'
```

### 2. Create Keywords

```bash
curl -X POST "http://localhost:8000/api/v1/keywords" \\
  -H "Authorization: Bearer your_access_token" \\
  -H "Content-Type: application/json" \\
  -d '{{"keyword": "artificial intelligence", "description": "AI discussions"}}'
```

### 3. Start Crawling

```bash
curl -X POST "http://localhost:8000/api/v1/crawling/start" \\
  -H "Authorization: Bearer your_access_token" \\
  -H "Content-Type: application/json" \\
  -d '{{"keyword_ids": [1], "limit": 100}}'
```

### 4. Generate Content

```bash
curl -X POST "http://localhost:8000/api/v1/content/generate" \\
  -H "Authorization: Bearer your_access_token" \\
  -H "Content-Type: application/json" \\
  -d '{{"content_type": "blog_post", "keyword_ids": [1]}}'
```

## API Reference

### Interactive Documentation

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **OpenAPI Schema**: [http://localhost:8000/api/v1/openapi.json](http://localhost:8000/api/v1/openapi.json)

### Postman Collection

Import the Postman collection for easy API testing:

1. Download: [`Reddit_Content_Platform_API.postman_collection.json`](../postman/Reddit_Content_Platform_API.postman_collection.json)
2. Import into Postman
3. Set up environment variables using [`Reddit_Content_Platform_Environment.postman_environment.json`](../postman/Reddit_Content_Platform_Environment.postman_environment.json)

## Authentication

### OAuth2 Flow

1. **Initiate**: `GET /api/v1/auth/login` - Redirects to Reddit
2. **Callback**: `POST /api/v1/auth/login` - Exchange code for tokens
3. **Use Token**: Include `Authorization: Bearer <token>` header
4. **Refresh**: `POST /api/v1/auth/refresh` when token expires

### Token Management

- **Access Token**: Expires in {settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES} minutes
- **Refresh Token**: Expires in {settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS} days
- **Storage**: Store securely, never expose in client-side code

## Rate Limits

| Endpoint Category | Limit | Window |
|------------------|-------|--------|
| General API | 60 requests | per minute per user |
| Reddit API | 60 requests | per minute (shared) |
| Content Generation | 10 requests | per hour per user |
| Public Blog API | 100 requests | per minute per IP |

Rate limit headers are included in responses:
- `X-RateLimit-Limit`: Request limit per window
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Unix timestamp when limit resets

## Error Handling

All errors follow a consistent format:

```json
{{
  "error_code": "validation_error|unauthorized|forbidden|not_found|rate_limit|internal_error",
  "message": "Human readable error message",
  "details": {{"field_name": ["Specific validation errors"]}},
  "timestamp": "2024-01-01T00:00:00Z",
  "request_id": "uuid-v4-string"
}}
```

### Common Error Codes

- `400` - Bad Request: Invalid request parameters
- `401` - Unauthorized: Missing or invalid authentication
- `403` - Forbidden: Valid auth but insufficient permissions
- `404` - Not Found: Resource doesn't exist
- `422` - Unprocessable Entity: Data validation failed
- `429` - Too Many Requests: Rate limit exceeded
- `500` - Internal Server Error: Unexpected server error

## Pagination

List endpoints support pagination with consistent parameters:

```bash
# Page-based pagination
GET /api/v1/keywords?page=1&page_size=20

# Offset-based pagination
GET /api/v1/posts?limit=50&offset=100
```

Response format:
```json
{{
  "data": [...],
  "pagination": {{
    "page": 1,
    "per_page": 20,
    "total": 150,
    "pages": 8,
    "has_next": true,
    "has_prev": false
  }}
}}
```

## API Versioning

The API uses URL path versioning:

- **Current**: `/api/v1/`
- **Header**: `Accept: application/vnd.reddit-platform.v1+json`
- **Custom**: `X-API-Version: v1`

Version information is included in response headers:
- `X-API-Version`: Version used for this request
- `X-API-Version-Default`: Default API version
- `X-API-Versions-Supported`: Comma-separated list of supported versions

## SDKs and Libraries

### Python

```python
import requests

class RedditContentPlatformAPI:
    def __init__(self, base_url, access_token):
        self.base_url = base_url
        self.headers = {{"Authorization": f"Bearer {{access_token}}"}}
    
    def create_keyword(self, keyword, description=None):
        response = requests.post(
            f"{{self.base_url}}/api/v1/keywords",
            headers=self.headers,
            json={{"keyword": keyword, "description": description}}
        )
        return response.json()
```

### JavaScript/Node.js

```javascript
class RedditContentPlatformAPI {{
  constructor(baseUrl, accessToken) {{
    this.baseUrl = baseUrl;
    this.headers = {{ 'Authorization': `Bearer ${{accessToken}}` }};
  }}
  
  async createKeyword(keyword, description) {{
    const response = await fetch(`${{this.baseUrl}}/api/v1/keywords`, {{
      method: 'POST',
      headers: {{ ...this.headers, 'Content-Type': 'application/json' }},
      body: JSON.stringify({{ keyword, description }})
    }});
    return response.json();
  }}
}}
```

## Support

- **Documentation**: [API Docs](http://localhost:8000/docs)
- **Issues**: [GitHub Issues](https://github.com/your-username/reddit-content-platform/issues)
- **Email**: support@yourcompany.com

---

*Generated automatically from OpenAPI specification*
"""
    
    # Save API documentation
    with open(docs_dir / "README.md", "w", encoding="utf-8") as f:
        f.write(api_docs)
    
    print(f"✅ API documentation generated at {docs_dir / 'README.md'}")


def generate_code_examples() -> None:
    """Generate code examples for different programming languages."""
    print("🔧 Generating code examples...")
    
    examples_dir = Path("docs/api/examples")
    examples_dir.mkdir(parents=True, exist_ok=True)
    
    # Python examples
    python_examples = '''"""
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
'''
    
    with open(examples_dir / "python_examples.py", "w", encoding="utf-8") as f:
        f.write(python_examples)
    
    # JavaScript examples
    js_examples = r'''/**
 * JavaScript/Node.js SDK Examples for Reddit Content Platform API
 */

class RedditContentPlatformAPI {
    constructor(baseUrl, accessToken = null) {
        this.baseUrl = baseUrl.replace(/\/$/, '');
        this.accessToken = accessToken;
        this.headers = {
            'Content-Type': 'application/json'
        };
        
        if (accessToken) {
            this.headers['Authorization'] = `Bearer ${accessToken}`;
        }
    }
    
    async authenticate(authCode, state) {
        const response = await fetch(`${this.baseUrl}/api/v1/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code: authCode, state: state })
        });
        
        if (!response.ok) {
            throw new Error(`Authentication failed: ${response.statusText}`);
        }
        
        const tokens = await response.json();
        this.accessToken = tokens.access_token;
        this.headers['Authorization'] = `Bearer ${this.accessToken}`;
        
        return tokens;
    }
    
    async refreshToken(refreshToken) {
        const response = await fetch(`${this.baseUrl}/api/v1/auth/refresh`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${refreshToken}` }
        });
        
        if (!response.ok) {
            throw new Error(`Token refresh failed: ${response.statusText}`);
        }
        
        const tokens = await response.json();
        this.accessToken = tokens.access_token;
        this.headers['Authorization'] = `Bearer ${this.accessToken}`;
        
        return tokens;
    }
    
    async createKeyword(keyword, description = null) {
        const data = { keyword };
        if (description) {
            data.description = description;
        }
        
        const response = await fetch(`${this.baseUrl}/api/v1/keywords`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            throw new Error(`Failed to create keyword: ${response.statusText}`);
        }
        
        return response.json();
    }
    
    async getKeywords(page = 1, pageSize = 20) {
        const params = new URLSearchParams({ page, page_size: pageSize });
        const response = await fetch(`${this.baseUrl}/api/v1/keywords?${params}`, {
            headers: this.headers
        });
        
        if (!response.ok) {
            throw new Error(`Failed to get keywords: ${response.statusText}`);
        }
        
        return response.json();
    }
    
    async startCrawling(keywordIds, limit = 100) {
        const data = { keyword_ids: keywordIds, limit };
        
        const response = await fetch(`${this.baseUrl}/api/v1/crawling/start`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            throw new Error(`Failed to start crawling: ${response.statusText}`);
        }
        
        return response.json();
    }
    
    async getCrawlingStatus() {
        const response = await fetch(`${this.baseUrl}/api/v1/crawling/status`, {
            headers: this.headers
        });
        
        if (!response.ok) {
            throw new Error(`Failed to get crawling status: ${response.statusText}`);
        }
        
        return response.json();
    }
    
    async generateContent(contentType, keywordIds, templateId = null) {
        const data = {
            content_type: contentType,
            keyword_ids: keywordIds
        };
        
        if (templateId) {
            data.template_id = templateId;
        }
        
        const response = await fetch(`${this.baseUrl}/api/v1/content/generate`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            throw new Error(`Failed to generate content: ${response.statusText}`);
        }
        
        return response.json();
    }
    
    async getContent(contentId) {
        const response = await fetch(`${this.baseUrl}/api/v1/content/${contentId}`, {
            headers: this.headers
        });
        
        if (!response.ok) {
            throw new Error(`Failed to get content: ${response.statusText}`);
        }
        
        return response.json();
    }
}

// Example usage
async function example() {
    const api = new RedditContentPlatformAPI('http://localhost:8000');
    
    try {
        // After OAuth2 flow, authenticate
        // const tokens = await api.authenticate('auth_code', 'state');
        
        // Create keywords
        const keyword = await api.createKeyword('artificial intelligence', 'AI discussions');
        console.log('Created keyword:', keyword);
        
        // Start crawling
        const crawlResult = await api.startCrawling([keyword.id], 50);
        console.log('Started crawling:', crawlResult);
        
        // Monitor crawling status
        const status = await api.getCrawlingStatus();
        console.log('Crawling status:', status);
        
        // Generate content
        const contentResult = await api.generateContent('blog_post', [keyword.id]);
        console.log('Generated content:', contentResult);
        
    } catch (error) {
        console.error('API Error:', error.message);
    }
}

// For Node.js environments
if (typeof module !== 'undefined' && module.exports) {
    module.exports = RedditContentPlatformAPI;
}

// For browser environments
if (typeof window !== 'undefined') {
    window.RedditContentPlatformAPI = RedditContentPlatformAPI;
}
'''
    
    with open(examples_dir / "javascript_examples.js", "w", encoding="utf-8") as f:
        f.write(js_examples)
    
    # cURL examples
    curl_examples = r'''#!/bin/bash

# Reddit Content Platform API - cURL Examples
# Make sure to set your base URL and tokens

BASE_URL="http://localhost:8000"
ACCESS_TOKEN="your_access_token_here"
REFRESH_TOKEN="your_refresh_token_here"

# Colors for output
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
NC='\\033[0m' # No Color

echo -e "${GREEN}Reddit Content Platform API - cURL Examples${NC}"
echo "=============================================="

# Function to make authenticated requests
auth_request() {
    curl -s -H "Authorization: Bearer $ACCESS_TOKEN" -H "Content-Type: application/json" "$@"
}

echo -e "\\n${YELLOW}1. Authentication${NC}"
echo "=================="

echo "Starting OAuth2 flow..."
curl -X GET "$BASE_URL/api/v1/auth/login"

echo -e "\\nExchange code for tokens (replace with actual code and state):"
echo "curl -X POST \"$BASE_URL/api/v1/auth/login\" \\\\"
echo "  -H \"Content-Type: application/json\" \\\\"
echo "  -d '{\"code\": \"your_auth_code\", \"state\": \"your_state\"}'"

echo -e "\\nRefresh token:"
echo "curl -X POST \"$BASE_URL/api/v1/auth/refresh\" \\\\"
echo "  -H \"Authorization: Bearer $REFRESH_TOKEN\""

echo -e "\\n${YELLOW}2. Keywords Management${NC}"
echo "======================"

echo "Create keyword:"
KEYWORD_RESULT=$(auth_request -X POST "$BASE_URL/api/v1/keywords" \\
  -d '{"keyword": "artificial intelligence", "description": "AI discussions"}')
echo "$KEYWORD_RESULT" | jq '.'

echo -e "\\nGet keywords:"
auth_request -X GET "$BASE_URL/api/v1/keywords?page=1&page_size=20" | jq '.'

echo -e "\\nGet keyword by ID:"
auth_request -X GET "$BASE_URL/api/v1/keywords/1" | jq '.'

echo -e "\\nUpdate keyword:"
auth_request -X PUT "$BASE_URL/api/v1/keywords/1" \\
  -d '{"keyword": "machine learning", "description": "Updated ML description"}' | jq '.'

echo -e "\\n${YELLOW}3. Crawling Operations${NC}"
echo "======================"

echo "Start crawling:"
CRAWL_RESULT=$(auth_request -X POST "$BASE_URL/api/v1/crawling/start" \\
  -d '{"keyword_ids": [1, 2], "limit": 100, "subreddits": ["MachineLearning", "artificial"]}')
echo "$CRAWL_RESULT" | jq '.'

echo -e "\\nGet crawling status:"
auth_request -X GET "$BASE_URL/api/v1/crawling/status" | jq '.'

echo -e "\\nGet crawling history:"
auth_request -X GET "$BASE_URL/api/v1/crawling/history?page=1&page_size=10" | jq '.'

echo -e "\\n${YELLOW}4. Posts and Data${NC}"
echo "=================="

echo "Search posts:"
auth_request -X GET "$BASE_URL/api/v1/posts?keyword_ids=1&page=1&page_size=20" | jq '.'

echo -e "\\nGet post by ID:"
auth_request -X GET "$BASE_URL/api/v1/posts/1" | jq '.'

echo -e "\\nGet trending posts:"
auth_request -X GET "$BASE_URL/api/v1/posts/trending?limit=10&time_period=24h" | jq '.'

echo -e "\\n${YELLOW}5. Trend Analysis${NC}"
echo "=================="

echo "Get trend analysis:"
auth_request -X GET "$BASE_URL/api/v1/trends?keyword_ids=1,2&time_period=7d" | jq '.'

echo -e "\\n${YELLOW}6. Content Generation${NC}"
echo "======================"

echo "Generate content:"
CONTENT_RESULT=$(auth_request -X POST "$BASE_URL/api/v1/content/generate" \\
  -d '{"content_type": "blog_post", "keyword_ids": [1], "template_id": 1}')
echo "$CONTENT_RESULT" | jq '.'

echo -e "\\nGet generated content:"
auth_request -X GET "$BASE_URL/api/v1/content?limit=10" | jq '.'

echo -e "\\nGet content by ID:"
auth_request -X GET "$BASE_URL/api/v1/content/1" | jq '.'

echo -e "\\n${YELLOW}7. System Monitoring${NC}"
echo "===================="

echo "Health check:"
curl -s -X GET "$BASE_URL/health" | jq '.'

echo -e "\\nDetailed health check:"
curl -s -X GET "$BASE_URL/health/detailed" | jq '.'

echo -e "\\nAPI version info:"
curl -s -X GET "$BASE_URL/api/version" | jq '.'

echo -e "\\nPrometheus metrics:"
curl -s -X GET "$BASE_URL/metrics"

echo -e "\\n${GREEN}Examples completed!${NC}"
echo "====================="
echo "Make sure to:"
echo "1. Replace BASE_URL with your actual API URL"
echo "2. Set ACCESS_TOKEN and REFRESH_TOKEN with real values"
echo "3. Install jq for JSON formatting: brew install jq (macOS) or apt-get install jq (Ubuntu)"
'''
    
    with open(examples_dir / "curl_examples.sh", "w", encoding="utf-8") as f:
        f.write(curl_examples)
    
    # Make the shell script executable
    os.chmod(examples_dir / "curl_examples.sh", 0o755)
    
    print(f"✅ Code examples generated at {examples_dir}")


def main():
    """Main function to generate all API documentation."""
    print("🚀 Starting API documentation generation...")
    print(f"📋 API Version: {settings.VERSION}")
    print(f"🔗 Base URL: {settings.API_V1_STR}")
    
    try:
        # Generate OpenAPI schema
        schema = generate_openapi_schema()
        save_openapi_schema(schema)
        
        # Update Postman collection and environment
        update_postman_collection()
        update_postman_environment()
        
        # Generate documentation files
        generate_api_documentation()
        generate_code_examples()
        
        print("\n🎉 API documentation generation completed successfully!")
        print("\n📚 Generated files:")
        print("   - docs/api/openapi.json - OpenAPI schema")
        print("   - docs/api/README.md - API documentation")
        print("   - docs/api/examples/ - Code examples")
        print("   - postman/ - Updated Postman collection and environment")
        
        print("\n🔗 Access documentation at:")
        print("   - Swagger UI: http://localhost:8000/docs")
        print("   - ReDoc: http://localhost:8000/redoc")
        print("   - OpenAPI JSON: http://localhost:8000/api/v1/openapi.json")
        
    except Exception as e:
        print(f"\n❌ Error generating API documentation: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()