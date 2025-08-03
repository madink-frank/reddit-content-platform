# API Documentation Guide

This guide explains how to use and maintain the comprehensive API documentation for the Reddit Content Platform.

## Overview

The Reddit Content Platform API provides complete documentation through multiple formats:

- **Interactive Documentation**: Swagger UI and ReDoc
- **OpenAPI Schema**: Machine-readable API specification
- **Postman Collection**: Ready-to-use API testing collection
- **Code Examples**: SDK examples in multiple programming languages
- **Comprehensive Guides**: Detailed usage documentation

## Documentation Structure

```
docs/
├── api/
│   ├── README.md                 # Main API documentation
│   ├── openapi.json             # OpenAPI 3.1 schema
│   └── examples/                # Code examples
│       ├── python_examples.py   # Python SDK
│       ├── javascript_examples.js # JavaScript/Node.js SDK
│       └── curl_examples.sh     # cURL examples
├── API_DOCUMENTATION_GUIDE.md   # This guide
postman/
├── Reddit_Content_Platform_API.postman_collection.json
└── Reddit_Content_Platform_Environment.postman_environment.json
```

## Accessing Documentation

### Interactive Documentation

1. **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
   - Interactive API explorer
   - Try endpoints directly in browser
   - Comprehensive parameter documentation
   - Response examples and schemas

2. **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
   - Clean, readable documentation
   - Better for reference and reading
   - Hierarchical navigation
   - Code samples in multiple languages

### API Schema

- **OpenAPI JSON**: [http://localhost:8000/api/v1/openapi.json](http://localhost:8000/api/v1/openapi.json)
- **Local File**: `docs/api/openapi.json`

### Version Information

- **API Version Endpoint**: [http://localhost:8000/api/version](http://localhost:8000/api/version)
- **API Examples**: [http://localhost:8000/api/docs/examples](http://localhost:8000/api/docs/examples)

## Using Postman Collection

### Setup

1. **Import Collection**:
   - Open Postman
   - Click "Import"
   - Select `postman/Reddit_Content_Platform_API.postman_collection.json`

2. **Import Environment**:
   - Click "Import"
   - Select `postman/Reddit_Content_Platform_Environment.postman_environment.json`
   - Set as active environment

3. **Configure Environment Variables**:
   ```
   base_url: http://localhost:8000 (or your deployment URL)
   access_token: (will be set automatically after login)
   refresh_token: (will be set automatically after login)
   ```

### Authentication Flow

1. **Start OAuth2**: Run "Initiate Login" request
2. **Complete in Browser**: Follow Reddit OAuth2 flow
3. **Exchange Code**: Use "Login with Code" with authorization code
4. **Automatic Token Management**: Tokens are set automatically

### Features

- **Automatic Token Management**: Tokens are stored and refreshed automatically
- **Pre-request Scripts**: Handle authentication headers
- **Test Scripts**: Validate responses and extract data
- **Environment Variables**: Consistent configuration across requests
- **Organized Folders**: Logical grouping of related endpoints

## Code Examples

### Python SDK

```python
from docs.api.examples.python_examples import RedditContentPlatformAPI

# Initialize client
api = RedditContentPlatformAPI("http://localhost:8000")

# Authenticate (after OAuth2 flow)
tokens = api.authenticate("auth_code", "state")

# Use API
keyword = api.create_keyword("artificial intelligence", "AI discussions")
crawl_result = api.start_crawling([keyword['id']], limit=50)
```

### JavaScript/Node.js SDK

```javascript
import RedditContentPlatformAPI from './docs/api/examples/javascript_examples.js';

const api = new RedditContentPlatformAPI('http://localhost:8000');

// Authenticate and use API
const tokens = await api.authenticate(authCode, state);
const keyword = await api.createKeyword('artificial intelligence', 'AI discussions');
const crawlResult = await api.startCrawling([keyword.id], 50);
```

### cURL Examples

```bash
# Make the script executable
chmod +x docs/api/examples/curl_examples.sh

# Set your tokens
export ACCESS_TOKEN="your_access_token"
export BASE_URL="http://localhost:8000"

# Run examples
./docs/api/examples/curl_examples.sh
```

## Generating Documentation

### Automatic Generation

Run the documentation generator to update all documentation:

```bash
python scripts/generate_api_docs.py
```

This will:
- Generate OpenAPI schema from FastAPI app
- Update Postman collection and environment
- Create comprehensive API documentation
- Generate code examples in multiple languages
- Update version information

### Manual Updates

1. **OpenAPI Configuration**: Edit `app/core/openapi_config.py`
2. **API Endpoints**: Update endpoint docstrings and schemas
3. **Examples**: Modify examples in the generator script
4. **Postman**: Update collection manually if needed

## API Features

### Authentication

- **OAuth2 Flow**: Reddit OAuth2 integration
- **JWT Tokens**: Access and refresh token management
- **Automatic Refresh**: Built-in token refresh mechanism
- **Security**: Secure token storage and transmission

### Versioning

- **URL Versioning**: `/api/v1/` prefix
- **Header Versioning**: `Accept: application/vnd.reddit-platform.v1+json`
- **Custom Header**: `X-API-Version: v1`
- **Deprecation Support**: Sunset headers for deprecated versions

### Rate Limiting

- **Per-User Limits**: 60 requests per minute for general API
- **Shared Limits**: 60 requests per minute for Reddit API
- **Content Generation**: 10 requests per hour per user
- **Public API**: 100 requests per minute per IP

### Error Handling

Consistent error format across all endpoints:

```json
{
  "error_code": "validation_error|unauthorized|forbidden|not_found|rate_limit|internal_error",
  "message": "Human readable error message",
  "details": {"field_name": ["Specific validation errors"]},
  "timestamp": "2024-01-01T00:00:00Z",
  "request_id": "uuid-v4-string"
}
```

### Pagination

Two pagination styles supported:

1. **Page-based**: `?page=1&page_size=20`
2. **Offset-based**: `?limit=20&offset=40`

Response includes pagination metadata:

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

## Best Practices

### For API Users

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

### For API Developers

1. **Documentation**:
   - Keep endpoint docstrings up to date
   - Include comprehensive examples
   - Document all parameters and responses
   - Update OpenAPI schema when making changes

2. **Versioning**:
   - Use semantic versioning
   - Provide migration guides for breaking changes
   - Support multiple versions during transition periods
   - Communicate deprecation timelines clearly

3. **Testing**:
   - Test all documented examples
   - Validate OpenAPI schema accuracy
   - Ensure Postman collection works
   - Test error scenarios

## Maintenance

### Regular Tasks

1. **Update Documentation**: Run generator after API changes
2. **Test Examples**: Verify all code examples work
3. **Review Postman Collection**: Ensure all endpoints are covered
4. **Check Links**: Verify all documentation links are valid

### Version Updates

1. **Update Version**: Change version in `app/core/config.py`
2. **Regenerate Docs**: Run `python scripts/generate_api_docs.py`
3. **Test Changes**: Verify all documentation is updated
4. **Update Deployment**: Deploy updated documentation

### Troubleshooting

#### Common Issues

1. **OpenAPI Generation Fails**:
   - Check for syntax errors in endpoint definitions
   - Verify all imports are working
   - Check for circular dependencies

2. **Postman Collection Issues**:
   - Verify JSON format is valid
   - Check environment variable names
   - Test authentication flow

3. **Code Examples Don't Work**:
   - Verify API endpoints are correct
   - Check authentication requirements
   - Test with actual API server

#### Getting Help

- **GitHub Issues**: Report bugs and request features
- **Documentation**: Check this guide and API docs
- **Code Review**: Review generated documentation files
- **Testing**: Use Postman collection to test endpoints

## Contributing

### Adding New Endpoints

1. **Create Endpoint**: Add to appropriate router
2. **Add Documentation**: Include comprehensive docstrings
3. **Update Examples**: Add to code examples
4. **Test**: Verify in Postman collection
5. **Generate**: Run documentation generator

### Improving Documentation

1. **Edit Generator**: Modify `scripts/generate_api_docs.py`
2. **Update Config**: Edit `app/core/openapi_config.py`
3. **Add Examples**: Include in appropriate example files
4. **Test Changes**: Verify generated output
5. **Submit PR**: Include documentation updates

---

*This guide is automatically updated when running the documentation generator.*