# Structured Logging System

## Overview

The Reddit Content Platform implements a comprehensive structured logging system that provides JSON-formatted logs, request correlation tracking, error categorization, and automated alerting. This system is designed to facilitate debugging, monitoring, and operational insights across all application components.

## Key Features

### 1. JSON Structured Logging
- **Format**: All logs are output in JSON format for easy parsing and analysis
- **Consistency**: Standardized log structure across all application components
- **Metadata**: Automatic inclusion of timestamp, log level, module, function, and environment information
- **Context**: Request ID and user ID correlation for tracing requests across services

### 2. Request Correlation Tracking
- **Request IDs**: Automatic generation or extraction of correlation IDs from headers
- **Context Propagation**: Request context maintained across async operations and background tasks
- **Header Support**: Multiple correlation header formats supported (`X-Request-ID`, `X-Correlation-ID`)
- **Middleware Integration**: Seamless integration with FastAPI middleware stack

### 3. Error Categorization and Alerting
- **Categories**: Predefined error categories (authentication, database, external_api, etc.)
- **Alert Levels**: Configurable alert levels (low, medium, high, critical)
- **Automated Alerts**: Integration with Slack, email, and webhook notification systems
- **Smart Filtering**: Environment-aware alerting to prevent noise in development

### 4. Performance and Security Monitoring
- **Performance Metrics**: Built-in logging for API response times, database queries, and external API calls
- **Security Events**: Dedicated logging for authentication failures and security-related events
- **Business Events**: Tracking of important business operations and user actions
- **Data Sanitization**: Automatic removal of sensitive information from logs

## Architecture

### Core Components

```
app/core/logging.py          # Main logging system
app/core/middleware.py       # Request tracking middleware
app/core/alert_notifier.py   # Alert notification system
app/core/api_logging.py      # External API call logging
app/core/db_logging.py       # Database operation logging
app/core/celery_logging.py   # Celery task logging
app/core/redis_logging.py    # Redis operation logging
```

### Log Flow

```
Request → Middleware → Application Code → Structured Logger → JSON Formatter → Output
                                      ↓
                                 Alert Handler → Notification System
```

## Configuration

### Environment Variables

```bash
# Logging Configuration
LOG_LEVEL=INFO                           # Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_FORMAT=json                          # Output format (json or text)
LOG_REQUEST_DETAILS=false                # Log detailed request/response info
LOG_SQL_QUERIES=false                    # Log SQL queries (debug only)
SLOW_QUERY_THRESHOLD_MS=100.0           # Threshold for slow query logging
LOG_CORRELATION_ID_HEADER=X-Correlation-ID  # Header for correlation ID
LOG_MAX_STRING_LENGTH=1000              # Maximum length for logged strings
LOG_EXCLUDE_PATHS=["/health", "/metrics"]  # Paths to exclude from request logging

# Alert Configuration
ALERT_WEBHOOK_URL=https://hooks.slack.com/...  # Slack webhook URL
ALERT_EMAIL_ENABLED=true                 # Enable email alerts
ALERT_SLACK_WEBHOOK=https://hooks.slack.com/...  # Slack webhook
ADMIN_EMAIL=admin@example.com           # Admin email for alerts
```

### Programmatic Configuration

```python
from app.core.logging import setup_logging, configure_advanced_logging

# Initialize logging system
setup_logging()
configure_advanced_logging()
```

## Usage Examples

### Basic Logging

```python
from app.core.logging import get_logger

logger = get_logger(__name__)

# Basic logging
logger.info("User logged in", user_id=123, operation="user_login")
logger.error("Database connection failed", 
             error_category="database", 
             alert_level="high")
```

### Request Context Logging

```python
from app.core.logging import set_request_context, get_logger

# Set request context (usually done by middleware)
set_request_context(request_id="req-123", user_id=456)

logger = get_logger(__name__)
logger.info("Processing request")  # Will include request_id and user_id
```

### Function Call Logging

```python
from app.core.logging import log_function_call

@log_function_call()
async def process_data(data: dict):
    # Function calls are automatically logged with timing
    return processed_data

@log_function_call("custom_function_name")
def sync_function(param: str):
    return result
```

### Business Event Logging

```python
from app.core.logging import log_business_event

# Track important business events
log_business_event(
    "user_registered",
    user_id=123,
    email="user@example.com",
    registration_method="oauth"
)
```

### Security Event Logging

```python
from app.core.logging import log_security_event

# Log security-related events
log_security_event(
    "failed_login",
    severity="medium",
    user_id=456,
    ip_address="192.168.1.100",
    user_agent="Mozilla/5.0..."
)
```

### Performance Metric Logging

```python
from app.core.logging import log_performance_metric

# Log performance metrics
log_performance_metric(
    "api_response_time",
    value=150.5,
    unit="ms",
    endpoint="/api/users",
    method="GET"
)
```

### External API Call Logging

```python
from app.core.api_logging import log_api_call

@log_api_call("reddit", "/api/posts")
async def fetch_reddit_posts():
    # API calls are automatically logged with timing and status
    response = await httpx.get("https://reddit.com/api/posts")
    return response
```

### Database Operation Logging

```python
from app.core.db_logging import log_db_operation

@log_db_operation("create")
def create_user(user_data: dict):
    # Database operations are logged with timing
    return db.create(User(**user_data))
```

## Log Format

### Standard Log Entry

```json
{
  "timestamp": "2024-01-01T12:00:00.000Z",
  "level": "INFO",
  "logger": "app.services.user_service",
  "message": "User created successfully",
  "module": "user_service",
  "function": "create_user",
  "line": 42,
  "thread": 123456789,
  "thread_name": "MainThread",
  "process": 1234,
  "request_id": "req-abc-123",
  "user_id": 456,
  "operation": "user_creation",
  "environment": "production",
  "service": "Reddit Content Platform",
  "version": "1.0.0"
}
```

### Error Log Entry

```json
{
  "timestamp": "2024-01-01T12:00:00.000Z",
  "level": "ERROR",
  "logger": "app.services.database",
  "message": "Database connection failed",
  "module": "database",
  "function": "connect",
  "line": 15,
  "request_id": "req-def-456",
  "operation": "db_connection",
  "error_category": "database",
  "alert_level": "high",
  "exception": {
    "type": "ConnectionError",
    "message": "Unable to connect to database",
    "traceback": "Traceback (most recent call last):\n..."
  },
  "environment": "production",
  "service": "Reddit Content Platform",
  "version": "1.0.0"
}
```

### HTTP Request Log Entry

```json
{
  "timestamp": "2024-01-01T12:00:00.000Z",
  "level": "INFO",
  "logger": "app.core.middleware",
  "message": "GET /api/users - 200",
  "operation": "http_request",
  "method": "GET",
  "path": "/api/users",
  "status_code": 200,
  "duration": 150.5,
  "query_params": {"page": "1", "limit": "10"},
  "user_agent": "Mozilla/5.0...",
  "client_ip": "192.168.1.100",
  "content_length": "1024",
  "request_id": "req-ghi-789",
  "user_id": 123,
  "environment": "production",
  "service": "Reddit Content Platform",
  "version": "1.0.0"
}
```

## Error Categories

The system uses predefined error categories for better organization and alerting:

- `authentication`: Authentication and authorization errors
- `validation`: Input validation and data format errors
- `database`: Database connection and query errors
- `redis`: Redis cache operation errors
- `external_api`: External API call failures
- `celery`: Background task processing errors
- `system`: System-level errors and resource issues
- `business_logic`: Application business logic errors
- `unknown`: Uncategorized errors

## Alert Levels

Alert levels determine the urgency and notification behavior:

- `low`: Minor issues, logged but no alerts in production
- `medium`: Moderate issues, alerts in production only
- `high`: Serious issues, always generate alerts
- `critical`: System-critical issues, immediate alerts with high priority

## Middleware Integration

### Request Tracking Middleware

Automatically handles:
- Request ID generation and extraction
- User context propagation
- Request timing and logging
- Error handling and response formatting

### Error Handling Middleware

Provides:
- Centralized error handling
- Consistent error response format
- Automatic error categorization
- Alert generation for critical errors

## Monitoring and Analysis

### Log Viewer Utility

Use the provided log viewer for filtering and analysis:

```bash
# View logs with filtering
python scripts/log_viewer.py logs/app.log --level ERROR
python scripts/log_viewer.py logs/app.log --category database --format pretty
python scripts/log_viewer.py logs/app.log --request-id abc-123

# Follow logs in real-time
python scripts/log_viewer.py logs/app.log --follow --level WARNING
```

### Integration with Monitoring Tools

The structured JSON format integrates well with:
- **ELK Stack**: Elasticsearch, Logstash, and Kibana
- **Grafana**: Log aggregation and visualization
- **Prometheus**: Metrics extraction from logs
- **Datadog**: Log monitoring and alerting
- **Splunk**: Log analysis and search

## Best Practices

### 1. Use Appropriate Log Levels
- `DEBUG`: Detailed diagnostic information
- `INFO`: General operational information
- `WARNING`: Potentially harmful situations
- `ERROR`: Error events that don't stop the application
- `CRITICAL`: Serious errors that may cause the application to abort

### 2. Include Context Information
```python
# Good: Include relevant context
logger.info("User profile updated", 
           user_id=123, 
           fields_updated=["email", "name"],
           operation="profile_update")

# Avoid: Vague messages without context
logger.info("Profile updated")
```

### 3. Use Error Categories
```python
# Good: Categorize errors for better alerting
logger.error("Payment processing failed",
            error_category="external_api",
            alert_level="high",
            payment_id="pay_123")
```

### 4. Sanitize Sensitive Data
```python
# The system automatically sanitizes sensitive fields
# But be explicit when logging user data
safe_user_data = sanitize_log_data(user_data)
logger.info("User data processed", user_data=safe_user_data)
```

### 5. Use Decorators for Function Logging
```python
# Automatically log function calls with timing
@log_function_call()
async def process_payment(payment_data: dict):
    # Function execution is automatically logged
    return process_result
```

## Testing

### Unit Tests
```bash
# Run logging system tests
python -m pytest tests/test_logging.py -v
```

### Integration Tests
```bash
# Run comprehensive integration tests
python test_structured_logging_integration.py
```

### Demo Script
```bash
# See the logging system in action
python test_logging_demo.py
```

## Troubleshooting

### Common Issues

1. **Logs not appearing**: Check `LOG_LEVEL` configuration
2. **Missing request IDs**: Ensure middleware is properly configured
3. **Alerts not working**: Verify alert configuration and network connectivity
4. **Performance impact**: Adjust log levels and exclude paths as needed

### Debug Mode

Enable debug logging for troubleshooting:

```bash
export LOG_LEVEL=DEBUG
export LOG_SQL_QUERIES=true
export LOG_REQUEST_DETAILS=true
```

### Log File Locations

- **Development**: Console output (stdout)
- **Production**: Configured log files or container logs
- **Docker**: Container logs accessible via `docker logs`

## Performance Considerations

### Log Volume Management
- Use appropriate log levels to control volume
- Exclude health check endpoints from request logging
- Implement log rotation for file-based logging
- Consider async logging for high-throughput applications

### Resource Usage
- JSON formatting has minimal overhead
- Request context uses thread-local storage efficiently
- Alert system uses background tasks to avoid blocking

### Optimization Tips
- Set `LOG_EXCLUDE_PATHS` for high-frequency endpoints
- Use `LOG_MAX_STRING_LENGTH` to prevent excessive log sizes
- Configure appropriate `SLOW_QUERY_THRESHOLD_MS` for database logging

## Security Considerations

### Data Protection
- Automatic sanitization of sensitive fields (passwords, tokens, keys)
- Configurable field exclusion patterns
- String truncation to prevent log injection attacks

### Access Control
- Logs may contain sensitive operational information
- Implement appropriate access controls for log files
- Consider log encryption for highly sensitive environments

### Compliance
- Structured logs facilitate compliance reporting
- Request correlation supports audit trails
- Configurable retention policies for log data

## Future Enhancements

### Planned Features
- Log sampling for high-volume applications
- Custom log formatters for different output targets
- Enhanced metrics extraction and reporting
- Integration with distributed tracing systems

### Extension Points
- Custom error categories
- Additional alert channels
- Custom log filters and processors
- Integration with external monitoring services