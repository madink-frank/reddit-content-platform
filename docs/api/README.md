# Reddit Content Platform API Documentation

**Version**: 1.0.0  
**Generated**: 2025-08-03T04:28:40.262359Z  
**Base URL**: `/api/v1`

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
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"code": "your_auth_code", "state": "your_state"}'
```

### 2. Create Keywords

```bash
curl -X POST "http://localhost:8000/api/v1/keywords" \
  -H "Authorization: Bearer your_access_token" \
  -H "Content-Type: application/json" \
  -d '{"keyword": "artificial intelligence", "description": "AI discussions"}'
```

### 3. Start Crawling

```bash
curl -X POST "http://localhost:8000/api/v1/crawling/start" \
  -H "Authorization: Bearer your_access_token" \
  -H "Content-Type: application/json" \
  -d '{"keyword_ids": [1], "limit": 100}'
```

### 4. Generate Content

```bash
curl -X POST "http://localhost:8000/api/v1/content/generate" \
  -H "Authorization: Bearer your_access_token" \
  -H "Content-Type: application/json" \
  -d '{"content_type": "blog_post", "keyword_ids": [1]}'
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

- **Access Token**: Expires in 15 minutes
- **Refresh Token**: Expires in 7 days
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
{
  "error_code": "validation_error|unauthorized|forbidden|not_found|rate_limit|internal_error",
  "message": "Human readable error message",
  "details": {"field_name": ["Specific validation errors"]},
  "timestamp": "2024-01-01T00:00:00Z",
  "request_id": "uuid-v4-string"
}
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
{
  "data": [...],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 150,
    "pages": 8,
    "has_next": true,
    "has_prev": false
  }
}
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
        self.headers = {"Authorization": f"Bearer {access_token}"}
    
    def create_keyword(self, keyword, description=None):
        response = requests.post(
            f"{self.base_url}/api/v1/keywords",
            headers=self.headers,
            json={"keyword": keyword, "description": description}
        )
        return response.json()
```

### JavaScript/Node.js

```javascript
class RedditContentPlatformAPI {
  constructor(baseUrl, accessToken) {
    this.baseUrl = baseUrl;
    this.headers = { 'Authorization': `Bearer ${accessToken}` };
  }
  
  async createKeyword(keyword, description) {
    const response = await fetch(`${this.baseUrl}/api/v1/keywords`, {
      method: 'POST',
      headers: { ...this.headers, 'Content-Type': 'application/json' },
      body: JSON.stringify({ keyword, description })
    });
    return response.json();
  }
}
```

## Support

- **Documentation**: [API Docs](http://localhost:8000/docs)
- **Issues**: [GitHub Issues](https://github.com/your-username/reddit-content-platform/issues)
- **Email**: support@yourcompany.com

---

*Generated automatically from OpenAPI specification*
