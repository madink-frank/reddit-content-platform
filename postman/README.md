# Reddit Content Platform API - Postman Collection

This directory contains the complete Postman collection and environment for testing the Reddit Content Platform API.

## Files

- `Reddit_Content_Platform_API.postman_collection.json` - Complete API collection with all endpoints
- `Reddit_Content_Platform_Environment.postman_environment.json` - Environment template with variables
- `README.md` - This setup guide

## Quick Setup

### 1. Import Collection and Environment

1. Open Postman
2. Click "Import" button
3. Select both JSON files from this directory:
   - `Reddit_Content_Platform_API.postman_collection.json`
   - `Reddit_Content_Platform_Environment.postman_environment.json`

### 2. Configure Environment

1. Select the "Reddit Content Platform Environment" from the environment dropdown
2. Update the `base_url` variable:
   - **Local Development**: `http://localhost:8000`
   - **Production**: `https://your-production-domain.com`
   - **Staging**: `https://your-staging-domain.com`

### 3. Authentication Setup

The collection includes automatic token management. Follow these steps:

1. **Start Authentication Flow**:
   - Run the "Initiate Login" request
   - This will redirect you to Reddit's authorization page

2. **Complete Reddit Authorization**:
   - Authorize the application in your browser
   - Copy the authorization code from the callback URL

3. **Get JWT Tokens**:
   - Use the "Login with Code" request
   - Paste the authorization code and state parameter
   - Tokens will be automatically set in environment variables

4. **Test Authentication**:
   - Run the "Get Current User" request to verify authentication

## Collection Features

### Automatic Token Management

The collection includes pre-request and test scripts that:

- **Auto-set tokens**: Tokens are automatically saved to environment variables after login
- **Token expiration check**: Warns when tokens are about to expire
- **Error handling**: Provides helpful error messages for authentication issues
- **Auto-refresh**: Guides you to refresh tokens when needed

### Request Organization

Requests are organized into logical folders:

- **Authentication**: Login, logout, token management
- **Keywords**: Keyword CRUD operations and statistics
- **Crawling**: Start crawling jobs and monitor status
- **Posts**: Search and retrieve Reddit posts
- **Analytics**: Trend analysis and statistics
- **Content Generation**: AI-powered content creation
- **Monitoring**: Health checks and system metrics

### Example Data

All requests include realistic example data:

- **Request bodies**: Pre-filled with sample data
- **Query parameters**: Examples for filtering and pagination
- **Response examples**: Expected response formats

## Usage Examples

### Basic Workflow

1. **Authenticate**:
   ```
   Authentication → Initiate Login
   Authentication → Login with Code
   ```

2. **Create Keywords**:
   ```
   Keywords → Create Keyword
   Keywords → Get Keywords
   ```

3. **Start Crawling**:
   ```
   Crawling → Start Crawling
   Crawling → Get Crawling Status
   ```

4. **Analyze Data**:
   ```
   Posts → Search Posts
   Analytics → Get Trend Analysis
   ```

5. **Generate Content**:
   ```
   Content Generation → Generate Content
   Content Generation → Get Generated Content
   ```

### Bulk Operations

For testing with multiple items:

```
Keywords → Bulk Create Keywords
Content Generation → Generate Batch Content
```

### Monitoring

Check system health:

```
Monitoring → Basic Health Check
Monitoring → Detailed Health Check
Monitoring → Get Prometheus Metrics
```

## Environment Variables

The environment includes these variables:

| Variable | Description | Auto-Set |
|----------|-------------|----------|
| `base_url` | API base URL | Manual |
| `access_token` | JWT access token | Yes |
| `refresh_token` | JWT refresh token | Yes |
| `user_id` | Current user ID | Yes |
| `reddit_username` | Reddit username | Yes |

## Authentication Flow Details

### Reddit OAuth2 Setup

Before using the collection, ensure your Reddit application is configured:

1. Go to [Reddit App Preferences](https://www.reddit.com/prefs/apps)
2. Create a new application:
   - **Type**: Web app
   - **Redirect URI**: `http://localhost:8000/api/v1/auth/callback` (for local development)
3. Note your Client ID and Client Secret

### Token Lifecycle

- **Access Token**: Expires in 15 minutes
- **Refresh Token**: Expires in 7 days
- **Automatic Refresh**: Use the "Refresh Token" request when access token expires

## Troubleshooting

### Common Issues

1. **401 Unauthorized**:
   - Check if access token is set in environment
   - Verify token hasn't expired
   - Use "Refresh Token" request if needed

2. **Reddit OAuth2 Errors**:
   - Verify Reddit app configuration
   - Check redirect URI matches your setup
   - Ensure client credentials are correct

3. **Rate Limiting**:
   - Wait for rate limit reset
   - Check `X-RateLimit-*` headers in responses
   - Reduce request frequency

4. **Connection Errors**:
   - Verify `base_url` is correct
   - Check if API server is running
   - Confirm network connectivity

### Debug Mode

Enable Postman console to see:
- Pre-request script logs
- Test script results
- Token expiration warnings
- Error details

## Advanced Features

### Custom Scripts

The collection includes custom scripts for:

- **Token validation**: Checks token expiration before requests
- **Error handling**: Provides detailed error information
- **Response parsing**: Extracts useful data from responses

### Variables and Templating

Use environment variables in requests:

```
{{base_url}}/api/v1/keywords/{{keyword_id}}
```

### Test Automation

Each request includes tests that:
- Verify response status codes
- Validate response structure
- Extract data for subsequent requests

## API Documentation

For detailed API documentation, visit:

- **Swagger UI**: `{{base_url}}/docs`
- **ReDoc**: `{{base_url}}/redoc`
- **Documentation Guide**: `../docs/API_DOCUMENTATION_GUIDE.md`

## Support

If you encounter issues:

1. Check the [API Documentation Guide](../docs/API_DOCUMENTATION_GUIDE.md)
2. Review the Swagger UI at `{{base_url}}/docs`
3. Check server logs for error details
4. Contact support at support@your-domain.com

## Contributing

To update the collection:

1. Make changes in Postman
2. Export the updated collection
3. Replace the JSON file in this directory
4. Update this README if needed
5. Test the collection thoroughly

## Version History

- **v1.0**: Initial collection with core endpoints
- **v1.1**: Added content generation endpoints
- **v1.2**: Enhanced authentication flow and error handling
- **v1.3**: Added monitoring endpoints and improved documentation