"""
OpenAPI configuration for enhanced API documentation.
"""

from app.core.config import settings


def get_openapi_config():
    """Get OpenAPI configuration dictionary."""
    return {
        "title": "Reddit Content Platform API",
        "version": settings.VERSION,
        "description": """
# Reddit Content Platform API

A comprehensive platform for crawling Reddit content, analyzing trends, and generating blog posts.

## Features

- **Authentication**: OAuth2 with JWT tokens and refresh token support
- **Keyword Management**: Track specific topics and keywords with CRUD operations
- **Content Crawling**: Automated Reddit post collection with background processing
- **Trend Analysis**: TF-IDF based trend analysis with caching
- **Content Generation**: AI-powered blog post creation with templates
- **Public Blog API**: Public endpoints for blog site integration
- **Monitoring**: Prometheus metrics and comprehensive health checks

## Authentication

Most endpoints require authentication. Follow this flow:

1. **Initiate Login**: `GET /api/v1/auth/login` - Redirects to Reddit OAuth2
2. **Complete Login**: `POST /api/v1/auth/login` - Exchange code for JWT tokens
3. **Use Access Token**: Include `Authorization: Bearer <access_token>` header
4. **Refresh Token**: `POST /api/v1/auth/refresh` when access token expires

### Token Lifecycle
- **Access Token**: 15 minutes expiration
- **Refresh Token**: 7 days expiration
- **Auto-refresh**: Use refresh token to get new access tokens

## Rate Limiting

API requests are rate-limited to prevent abuse:
- **General API**: 60 requests per minute per user
- **Reddit API**: 60 requests per minute (shared across all users)
- **Content Generation**: 10 requests per hour per user
- **Public Blog API**: 100 requests per minute per IP (no auth required)

## Pagination

List endpoints support pagination with consistent parameters:
- `page`: Page number (starts from 1)
- `page_size` or `per_page`: Items per page (max 100)
- `limit` and `offset`: Alternative pagination style for some endpoints

## Error Handling

All errors follow a consistent format:
```json
{
    "error_code": "validation_error|unauthorized|forbidden|not_found|rate_limit|internal_error",
    "message": "Human readable error message",
    "details": {
        "field_name": ["Specific validation errors"]
    },
    "timestamp": "2024-01-01T00:00:00Z",
    "request_id": "uuid-v4-string"
}
```

## API Versioning

This API uses URL path versioning:
- **Current Version**: `/api/v1/`
- **Version Header**: `Accept: application/vnd.reddit-platform.v1+json` (optional)
- **Deprecation**: Deprecated endpoints include `Sunset` header with removal date

## Content Types

- **Request**: `application/json` for POST/PUT requests
- **Response**: `application/json` for all responses
- **Metrics**: `text/plain` for Prometheus metrics endpoint
- **Health**: `application/json` for health check endpoints
        """,
        "tags": [
            {
                "name": "authentication",
                "description": "Reddit OAuth2 authentication and JWT token management",
                "externalDocs": {
                    "description": "Reddit OAuth2 Documentation",
                    "url": "https://github.com/reddit-archive/reddit/wiki/OAuth2"
                }
            },
            {
                "name": "keywords",
                "description": "Keyword management for tracking specific topics on Reddit. Create, update, delete, and manage keywords that will be used for content crawling.",
                "externalDocs": {
                    "description": "Keyword Management Guide",
                    "url": "https://github.com/your-username/reddit-content-platform/blob/main/docs/keyword-management.md"
                }
            },
            {
                "name": "crawling",
                "description": "Reddit content crawling operations and status monitoring. Start background crawling jobs, monitor progress, and view crawling history.",
                "externalDocs": {
                    "description": "Crawling Guide",
                    "url": "https://github.com/your-username/reddit-content-platform/blob/main/docs/crawling-guide.md"
                }
            },
            {
                "name": "posts",
                "description": "Search and retrieve crawled Reddit posts with advanced filtering options. Access collected Reddit data with pagination and sorting.",
                "externalDocs": {
                    "description": "Posts API Guide",
                    "url": "https://github.com/your-username/reddit-content-platform/blob/main/docs/posts-api.md"
                }
            },
            {
                "name": "trends",
                "description": "Trend analysis and statistics from collected Reddit data using TF-IDF algorithms and engagement metrics.",
                "externalDocs": {
                    "description": "Trend Analysis Guide",
                    "url": "https://github.com/your-username/reddit-content-platform/blob/main/docs/trend-analysis.md"
                }
            },
            {
                "name": "content",
                "description": "AI-powered content generation based on analyzed Reddit data. Generate blog posts, articles, and other content using customizable templates.",
                "externalDocs": {
                    "description": "Content Generation Guide",
                    "url": "https://github.com/your-username/reddit-content-platform/blob/main/docs/content-generation.md"
                }
            },
            {
                "name": "public-blog",
                "description": "Public API endpoints for blog site integration. No authentication required. Used by frontend blog sites to display generated content.",
                "externalDocs": {
                    "description": "Public Blog API Guide",
                    "url": "https://github.com/your-username/reddit-content-platform/blob/main/docs/public-blog-api.md"
                }
            },
            {
                "name": "tasks",
                "description": "Background task management and monitoring. Track Celery task status, cancel running tasks, and view task history.",
                "externalDocs": {
                    "description": "Task Management Guide",
                    "url": "https://github.com/your-username/reddit-content-platform/blob/main/docs/task-management.md"
                }
            },
            {
                "name": "reddit",
                "description": "Direct Reddit API integration endpoints. Test Reddit connectivity and perform manual Reddit operations.",
                "externalDocs": {
                    "description": "Reddit Integration Guide",
                    "url": "https://github.com/your-username/reddit-content-platform/blob/main/docs/reddit-integration.md"
                }
            },
            {
                "name": "monitoring",
                "description": "System health monitoring, metrics collection, and observability endpoints. Includes Prometheus metrics and health checks.",
                "externalDocs": {
                    "description": "Monitoring Guide",
                    "url": "https://github.com/your-username/reddit-content-platform/blob/main/docs/monitoring.md"
                }
            }
        ],
        "security_schemes": {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "JWT token obtained from /auth/login endpoint"
            },
            "OAuth2": {
                "type": "oauth2",
                "flows": {
                    "authorizationCode": {
                        "authorizationUrl": "https://www.reddit.com/api/v1/authorize",
                        "tokenUrl": "/api/v1/auth/token",
                        "scopes": {
                            "read": "Read Reddit posts and comments",
                            "identity": "Access user identity information"
                        }
                    }
                },
                "description": "Reddit OAuth2 authentication"
            }
        },
        "servers": [
            {
                "url": "http://localhost:8000",
                "description": "Development server"
            },
            {
                "url": "https://your-app.railway.app",
                "description": "Production server"
            }
        ],
        "contact": {
            "name": "Reddit Content Platform",
            "url": "https://github.com/your-username/reddit-content-platform",
            "email": "support@yourcompany.com"
        },
        "license": {
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT"
        },
        "external_docs": {
            "description": "Find more info here",
            "url": "https://github.com/your-username/reddit-content-platform/blob/main/README.md"
        },
        "common_responses": {
            "ValidationError": {
                "description": "Validation Error - Request data failed validation",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "error_code": {"type": "string", "example": "validation_error"},
                                "message": {"type": "string", "example": "Invalid input data"},
                                "details": {
                                    "type": "object",
                                    "example": {
                                        "keyword": ["This field is required"],
                                        "email": ["Invalid email format"]
                                    }
                                },
                                "timestamp": {"type": "string", "format": "date-time", "example": "2024-01-01T12:00:00Z"},
                                "request_id": {"type": "string", "example": "req_123e4567-e89b-12d3-a456-426614174000"}
                            },
                            "required": ["error_code", "message", "timestamp", "request_id"]
                        }
                    }
                }
            },
            "Unauthorized": {
                "description": "Authentication required - Missing or invalid access token",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "error_code": {"type": "string", "example": "unauthorized"},
                                "message": {"type": "string", "example": "Authentication required"},
                                "details": {
                                    "type": "object",
                                    "example": {"hint": "Include 'Authorization: Bearer <token>' header"}
                                },
                                "timestamp": {"type": "string", "format": "date-time", "example": "2024-01-01T12:00:00Z"},
                                "request_id": {"type": "string", "example": "req_123e4567-e89b-12d3-a456-426614174000"}
                            },
                            "required": ["error_code", "message", "timestamp", "request_id"]
                        }
                    }
                }
            },
            "Forbidden": {
                "description": "Insufficient permissions - Valid token but lacks required permissions",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "error_code": {"type": "string", "example": "forbidden"},
                                "message": {"type": "string", "example": "Insufficient permissions"},
                                "details": {
                                    "type": "object",
                                    "example": {"required_permission": "admin", "user_permission": "user"}
                                },
                                "timestamp": {"type": "string", "format": "date-time", "example": "2024-01-01T12:00:00Z"},
                                "request_id": {"type": "string", "example": "req_123e4567-e89b-12d3-a456-426614174000"}
                            },
                            "required": ["error_code", "message", "timestamp", "request_id"]
                        }
                    }
                }
            },
            "NotFound": {
                "description": "Resource not found - The requested resource does not exist",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "error_code": {"type": "string", "example": "not_found"},
                                "message": {"type": "string", "example": "Resource not found"},
                                "details": {
                                    "type": "object",
                                    "example": {"resource_type": "keyword", "resource_id": "123"}
                                },
                                "timestamp": {"type": "string", "format": "date-time", "example": "2024-01-01T12:00:00Z"},
                                "request_id": {"type": "string", "example": "req_123e4567-e89b-12d3-a456-426614174000"}
                            },
                            "required": ["error_code", "message", "timestamp", "request_id"]
                        }
                    }
                }
            },
            "RateLimitExceeded": {
                "description": "Rate limit exceeded - Too many requests",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "error_code": {"type": "string", "example": "rate_limit_exceeded"},
                                "message": {"type": "string", "example": "Rate limit exceeded"},
                                "details": {
                                    "type": "object",
                                    "example": {
                                        "limit": 60,
                                        "window": "1 minute",
                                        "retry_after": 45
                                    }
                                },
                                "timestamp": {"type": "string", "format": "date-time", "example": "2024-01-01T12:00:00Z"},
                                "request_id": {"type": "string", "example": "req_123e4567-e89b-12d3-a456-426614174000"}
                            },
                            "required": ["error_code", "message", "timestamp", "request_id"]
                        }
                    }
                }
            },
            "InternalServerError": {
                "description": "Internal server error - Unexpected server error occurred",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "error_code": {"type": "string", "example": "internal_error"},
                                "message": {"type": "string", "example": "An unexpected error occurred"},
                                "details": {
                                    "type": "object",
                                    "example": {"error_id": "err_123e4567-e89b-12d3-a456-426614174000"}
                                },
                                "timestamp": {"type": "string", "format": "date-time", "example": "2024-01-01T12:00:00Z"},
                                "request_id": {"type": "string", "example": "req_123e4567-e89b-12d3-a456-426614174000"}
                            },
                            "required": ["error_code", "message", "timestamp", "request_id"]
                        }
                    }
                }
            },
            "ServiceUnavailable": {
                "description": "Service temporarily unavailable - Service is down for maintenance or overloaded",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "error_code": {"type": "string", "example": "service_unavailable"},
                                "message": {"type": "string", "example": "Service temporarily unavailable"},
                                "details": {
                                    "type": "object",
                                    "example": {"retry_after": 300, "maintenance": False}
                                },
                                "timestamp": {"type": "string", "format": "date-time", "example": "2024-01-01T12:00:00Z"},
                                "request_id": {"type": "string", "example": "req_123e4567-e89b-12d3-a456-426614174000"}
                            },
                            "required": ["error_code", "message", "timestamp", "request_id"]
                        }
                    }
                }
            }
        },
        "example_schemas": {
            "PaginationMeta": {
                "type": "object",
                "properties": {
                    "page": {"type": "integer", "example": 1, "description": "Current page number"},
                    "per_page": {"type": "integer", "example": 20, "description": "Items per page"},
                    "total": {"type": "integer", "example": 150, "description": "Total number of items"},
                    "pages": {"type": "integer", "example": 8, "description": "Total number of pages"},
                    "has_next": {"type": "boolean", "example": True, "description": "Whether there is a next page"},
                    "has_prev": {"type": "boolean", "example": False, "description": "Whether there is a previous page"}
                },
                "required": ["page", "per_page", "total", "pages", "has_next", "has_prev"]
            },
            "TaskStatus": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "example": "task_123e4567-e89b-12d3-a456-426614174000"},
                    "status": {"type": "string", "enum": ["pending", "running", "completed", "failed"], "example": "running"},
                    "progress": {"type": "integer", "minimum": 0, "maximum": 100, "example": 75},
                    "result": {"type": "object", "nullable": True, "example": None},
                    "error": {"type": "string", "nullable": True, "example": None},
                    "created_at": {"type": "string", "format": "date-time", "example": "2024-01-01T12:00:00Z"},
                    "updated_at": {"type": "string", "format": "date-time", "example": "2024-01-01T12:05:00Z"}
                },
                "required": ["task_id", "status", "created_at", "updated_at"]
            },
            "SuccessResponse": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean", "example": True, "description": "Operation success status"},
                    "message": {"type": "string", "example": "Operation completed successfully", "description": "Success message"},
                    "data": {"type": "object", "description": "Response data"},
                    "timestamp": {"type": "string", "format": "date-time", "example": "2024-01-01T12:00:00Z"},
                    "request_id": {"type": "string", "example": "req_123e4567-e89b-12d3-a456-426614174000"}
                },
                "required": ["success", "timestamp", "request_id"]
            },
            "KeywordExample": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer", "example": 1, "description": "Unique keyword identifier"},
                    "keyword": {"type": "string", "example": "artificial intelligence", "description": "The keyword text"},
                    "description": {"type": "string", "example": "Track AI-related discussions and trends", "description": "Optional keyword description"},
                    "is_active": {"type": "boolean", "example": True, "description": "Whether keyword is active for crawling"},
                    "user_id": {"type": "integer", "example": 123, "description": "ID of the user who owns this keyword"},
                    "created_at": {"type": "string", "format": "date-time", "example": "2024-01-01T12:00:00Z"},
                    "updated_at": {"type": "string", "format": "date-time", "example": "2024-01-01T12:05:00Z"},
                    "stats": {
                        "type": "object",
                        "properties": {
                            "total_posts": {"type": "integer", "example": 150, "description": "Total posts collected for this keyword"},
                            "last_crawl": {"type": "string", "format": "date-time", "example": "2024-01-01T11:00:00Z", "description": "Last crawling timestamp"},
                            "avg_score": {"type": "number", "example": 45.7, "description": "Average post score"}
                        }
                    }
                },
                "required": ["id", "keyword", "is_active", "user_id", "created_at", "updated_at"]
            },
            "PostExample": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer", "example": 1, "description": "Unique post identifier"},
                    "reddit_id": {"type": "string", "example": "abc123", "description": "Reddit post ID"},
                    "title": {"type": "string", "example": "Amazing breakthrough in AI research", "description": "Post title"},
                    "content": {"type": "string", "example": "Researchers have developed a new AI model...", "description": "Post content"},
                    "author": {"type": "string", "example": "reddit_user", "description": "Reddit username of the author"},
                    "subreddit": {"type": "string", "example": "MachineLearning", "description": "Subreddit name"},
                    "score": {"type": "integer", "example": 1250, "description": "Reddit post score (upvotes - downvotes)"},
                    "num_comments": {"type": "integer", "example": 89, "description": "Number of comments"},
                    "url": {"type": "string", "example": "https://reddit.com/r/MachineLearning/comments/abc123", "description": "Reddit post URL"},
                    "created_at": {"type": "string", "format": "date-time", "example": "2024-01-01T12:00:00Z"},
                    "keyword_id": {"type": "integer", "example": 1, "description": "Associated keyword ID"}
                },
                "required": ["id", "reddit_id", "title", "author", "subreddit", "score", "created_at", "keyword_id"]
            },
            "TrendMetricsExample": {
                "type": "object",
                "properties": {
                    "keyword_id": {"type": "integer", "example": 1, "description": "Keyword identifier"},
                    "keyword": {"type": "string", "example": "artificial intelligence", "description": "Keyword text"},
                    "time_period": {"type": "string", "example": "7d", "description": "Analysis time period"},
                    "metrics": {
                        "type": "object",
                        "properties": {
                            "total_posts": {"type": "integer", "example": 150, "description": "Total posts in period"},
                            "avg_score": {"type": "number", "example": 45.7, "description": "Average post score"},
                            "engagement_rate": {"type": "number", "example": 0.85, "description": "Engagement rate (0-1)"},
                            "trend_velocity": {"type": "number", "example": 1.25, "description": "Trend velocity indicator"},
                            "top_subreddits": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "subreddit": {"type": "string", "example": "MachineLearning"},
                                        "post_count": {"type": "integer", "example": 45}
                                    }
                                }
                            },
                            "tfidf_scores": {
                                "type": "object",
                                "example": {"ai": 0.85, "machine": 0.72, "learning": 0.68},
                                "description": "TF-IDF scores for related terms"
                            }
                        }
                    },
                    "generated_at": {"type": "string", "format": "date-time", "example": "2024-01-01T12:00:00Z"}
                },
                "required": ["keyword_id", "keyword", "time_period", "metrics", "generated_at"]
            },
            "ContentExample": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer", "example": 1, "description": "Unique content identifier"},
                    "title": {"type": "string", "example": "The Future of Artificial Intelligence: Trends and Insights", "description": "Generated content title"},
                    "content": {"type": "string", "example": "# The Future of AI\n\nBased on recent Reddit discussions...", "description": "Generated content in Markdown format"},
                    "content_type": {"type": "string", "example": "blog_post", "description": "Type of generated content"},
                    "template_used": {"type": "string", "example": "default", "description": "Template used for generation"},
                    "keyword_ids": {"type": "array", "items": {"type": "integer"}, "example": [1, 2], "description": "Keywords used for generation"},
                    "metadata": {
                        "type": "object",
                        "properties": {
                            "word_count": {"type": "integer", "example": 1250, "description": "Content word count"},
                            "reading_time": {"type": "integer", "example": 5, "description": "Estimated reading time in minutes"},
                            "sources_count": {"type": "integer", "example": 15, "description": "Number of Reddit posts used as sources"}
                        }
                    },
                    "user_id": {"type": "integer", "example": 123, "description": "ID of the user who generated this content"},
                    "created_at": {"type": "string", "format": "date-time", "example": "2024-01-01T12:00:00Z"},
                    "updated_at": {"type": "string", "format": "date-time", "example": "2024-01-01T12:05:00Z"}
                },
                "required": ["id", "title", "content", "content_type", "user_id", "created_at"]
            },
            "HealthCheckExample": {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "enum": ["healthy", "unhealthy"], "example": "healthy"},
                    "timestamp": {"type": "string", "format": "date-time", "example": "2024-01-01T12:00:00Z"},
                    "services": {
                        "type": "object",
                        "properties": {
                            "database": {
                                "type": "object",
                                "properties": {
                                    "status": {"type": "string", "example": "healthy"},
                                    "response_time_ms": {"type": "number", "example": 5.2},
                                    "connection_pool": {"type": "string", "example": "active"},
                                    "active_connections": {"type": "integer", "example": 3}
                                }
                            },
                            "redis": {
                                "type": "object",
                                "properties": {
                                    "status": {"type": "string", "example": "healthy"},
                                    "response_time_ms": {"type": "number", "example": 1.8},
                                    "memory_usage": {"type": "string", "example": "45MB"},
                                    "connected_clients": {"type": "integer", "example": 2}
                                }
                            },
                            "celery": {
                                "type": "object",
                                "properties": {
                                    "status": {"type": "string", "example": "healthy"},
                                    "active_workers": {"type": "integer", "example": 3},
                                    "pending_tasks": {"type": "integer", "example": 5},
                                    "processed_tasks": {"type": "integer", "example": 1250}
                                }
                            }
                        }
                    },
                    "version": {"type": "string", "example": "1.0.0", "description": "API version"},
                    "uptime": {"type": "string", "example": "2d 5h 30m", "description": "Service uptime"}
                },
                "required": ["status", "timestamp", "services"]
            },
            "AuthTokenResponse": {
                "type": "object",
                "properties": {
                    "access_token": {"type": "string", "example": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...", "description": "JWT access token"},
                    "refresh_token": {"type": "string", "example": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...", "description": "JWT refresh token"},
                    "token_type": {"type": "string", "example": "bearer", "description": "Token type"},
                    "expires_in": {"type": "integer", "example": 900, "description": "Access token expiration in seconds"},
                    "user": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer", "example": 123},
                            "username": {"type": "string", "example": "reddit_user"},
                            "email": {"type": "string", "example": "user@example.com"}
                        }
                    }
                },
                "required": ["access_token", "refresh_token", "token_type", "expires_in"]
            },
            "CrawlingJobResponse": {
                "type": "object",
                "properties": {
                    "job_id": {"type": "string", "example": "crawl_123e4567-e89b-12d3-a456-426614174000", "description": "Unique job identifier"},
                    "status": {"type": "string", "enum": ["pending", "running", "completed", "failed"], "example": "running"},
                    "keyword_ids": {"type": "array", "items": {"type": "integer"}, "example": [1, 2, 3]},
                    "subreddits": {"type": "array", "items": {"type": "string"}, "example": ["MachineLearning", "artificial"]},
                    "progress": {
                        "type": "object",
                        "properties": {
                            "total_keywords": {"type": "integer", "example": 3},
                            "completed_keywords": {"type": "integer", "example": 1},
                            "total_posts_found": {"type": "integer", "example": 150},
                            "posts_saved": {"type": "integer", "example": 145}
                        }
                    },
                    "created_at": {"type": "string", "format": "date-time", "example": "2024-01-01T12:00:00Z"},
                    "updated_at": {"type": "string", "format": "date-time", "example": "2024-01-01T12:05:00Z"}
                },
                "required": ["job_id", "status", "keyword_ids", "created_at"]
            },
            "APIVersionInfo": {
                "type": "object",
                "properties": {
                    "current_version": {"type": "string", "example": "v1", "description": "Current API version"},
                    "default_version": {"type": "string", "example": "v1", "description": "Default API version"},
                    "supported_versions": {
                        "type": "object",
                        "additionalProperties": {
                            "type": "object",
                            "properties": {
                                "version": {"type": "string"},
                                "is_default": {"type": "boolean"},
                                "is_deprecated": {"type": "boolean"},
                                "sunset_date": {"type": "string", "format": "date-time", "nullable": True},
                                "description": {"type": "string"}
                            }
                        },
                        "example": {
                            "v1": {
                                "version": "v1",
                                "is_default": True,
                                "is_deprecated": False,
                                "sunset_date": None,
                                "description": "Current stable version with full feature support"
                            }
                        }
                    },
                    "version_header": {"type": "string", "example": "Accept", "description": "Header name for version specification"},
                    "media_type_prefix": {"type": "string", "example": "application/vnd.reddit-platform", "description": "Media type prefix for version specification"},
                    "examples": {
                        "type": "object",
                        "properties": {
                            "url_versioning": {"type": "string", "example": "/api/v1/keywords"},
                            "header_versioning": {"type": "string", "example": "application/vnd.reddit-platform.v1+json"},
                            "custom_header": {"type": "string", "example": "X-API-Version: v1"}
                        }
                    }
                },
                "required": ["current_version", "default_version", "supported_versions"]
            },
            "BulkOperationResponse": {
                "type": "object",
                "properties": {
                    "total_requested": {"type": "integer", "example": 10, "description": "Total number of items requested"},
                    "successful": {"type": "integer", "example": 8, "description": "Number of successful operations"},
                    "failed": {"type": "integer", "example": 2, "description": "Number of failed operations"},
                    "results": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "index": {"type": "integer", "example": 0},
                                "success": {"type": "boolean", "example": True},
                                "data": {"type": "object", "description": "Result data if successful"},
                                "error": {"type": "string", "description": "Error message if failed", "nullable": True}
                            }
                        }
                    },
                    "processing_time_ms": {"type": "number", "example": 1250.5, "description": "Total processing time in milliseconds"}
                },
                "required": ["total_requested", "successful", "failed", "results"]
            },
            "RateLimitInfo": {
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "example": 60, "description": "Request limit per window"},
                    "remaining": {"type": "integer", "example": 45, "description": "Remaining requests in current window"},
                    "reset": {"type": "integer", "example": 1640995200, "description": "Unix timestamp when limit resets"},
                    "window": {"type": "string", "example": "1 minute", "description": "Rate limit window duration"},
                    "retry_after": {"type": "integer", "example": 30, "description": "Seconds to wait before retrying (when limit exceeded)", "nullable": True}
                },
                "required": ["limit", "remaining", "reset", "window"]
            }
        }
    }


def get_enhanced_openapi_examples():
    """Get enhanced examples for OpenAPI documentation."""
    return {
        "authentication_examples": {
            "oauth2_flow": {
                "summary": "Complete OAuth2 Authentication Flow",
                "description": "Step-by-step example of Reddit OAuth2 authentication",
                "value": {
                    "step_1": {
                        "description": "Initiate OAuth2 flow",
                        "request": "GET /api/v1/auth/login",
                        "response": "Redirects to Reddit authorization page"
                    },
                    "step_2": {
                        "description": "Exchange code for tokens",
                        "request": {
                            "method": "POST",
                            "url": "/api/v1/auth/login",
                            "body": {
                                "code": "authorization_code_from_reddit",
                                "state": "state_parameter"
                            }
                        },
                        "response": {
                            "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                            "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                            "token_type": "bearer",
                            "expires_in": 900
                        }
                    }
                }
            },
            "token_usage": {
                "summary": "Using JWT Tokens",
                "description": "How to use JWT tokens in API requests",
                "value": {
                    "header": "Authorization: Bearer <access_token>",
                    "example": "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                    "note": "Include this header in all authenticated requests"
                }
            }
        },
        "workflow_examples": {
            "basic_workflow": {
                "summary": "Basic Content Crawling Workflow",
                "description": "Complete workflow from keyword creation to content generation",
                "value": {
                    "steps": [
                        {
                            "step": 1,
                            "action": "Create keyword",
                            "endpoint": "POST /api/v1/keywords",
                            "payload": {
                                "keyword": "artificial intelligence",
                                "description": "AI discussions and trends"
                            }
                        },
                        {
                            "step": 2,
                            "action": "Start crawling",
                            "endpoint": "POST /api/v1/crawling/start",
                            "payload": {
                                "keyword_ids": [1],
                                "limit": 100
                            }
                        },
                        {
                            "step": 3,
                            "action": "Monitor progress",
                            "endpoint": "GET /api/v1/crawling/status"
                        },
                        {
                            "step": 4,
                            "action": "View results",
                            "endpoint": "GET /api/v1/posts?keyword_ids=1"
                        },
                        {
                            "step": 5,
                            "action": "Analyze trends",
                            "endpoint": "GET /api/v1/trends?keyword_ids=1"
                        },
                        {
                            "step": 6,
                            "action": "Generate content",
                            "endpoint": "POST /api/v1/content/generate",
                            "payload": {
                                "keyword_ids": [1],
                                "content_type": "blog_post"
                            }
                        }
                    ]
                }
            }
        },
        "error_examples": {
            "validation_error": {
                "summary": "Validation Error Response",
                "description": "Example of validation error when creating a keyword",
                "value": {
                    "error_code": "validation_error",
                    "message": "Invalid input data",
                    "details": {
                        "keyword": ["This field is required"],
                        "description": ["String too short"]
                    },
                    "timestamp": "2024-01-01T12:00:00Z",
                    "request_id": "req_123e4567-e89b-12d3-a456-426614174000"
                }
            },
            "rate_limit_error": {
                "summary": "Rate Limit Exceeded",
                "description": "Example response when rate limit is exceeded",
                "value": {
                    "error_code": "rate_limit_exceeded",
                    "message": "Rate limit exceeded",
                    "details": {
                        "limit": 60,
                        "window": "1 minute",
                        "retry_after": 45,
                        "current_usage": 61
                    },
                    "timestamp": "2024-01-01T12:00:00Z",
                    "request_id": "req_123e4567-e89b-12d3-a456-426614174000"
                }
            }
        }
    }


def get_api_documentation_config():
    """Get comprehensive API documentation configuration."""
    return {
        "info": {
            "title": "Reddit Content Platform API",
            "version": settings.VERSION,
            "description": get_openapi_config()["description"],
            "termsOfService": "https://github.com/your-username/reddit-content-platform/blob/main/TERMS.md",
            "contact": {
                "name": "Reddit Content Platform Support",
                "url": "https://github.com/your-username/reddit-content-platform",
                "email": "support@yourcompany.com"
            },
            "license": {
                "name": "MIT License",
                "url": "https://opensource.org/licenses/MIT"
            },
            "x-logo": {
                "url": "https://github.com/your-username/reddit-content-platform/raw/main/docs/logo.png",
                "altText": "Reddit Content Platform Logo"
            }
        },
        "servers": [
            {
                "url": "http://localhost:8000",
                "description": "Development server"
            },
            {
                "url": "https://your-app.railway.app",
                "description": "Production server"
            },
            {
                "url": "https://staging-your-app.railway.app",
                "description": "Staging server"
            }
        ],
        "externalDocs": {
            "description": "Complete API Documentation",
            "url": "https://github.com/your-username/reddit-content-platform/blob/main/docs/API.md"
        },
        "x-tagGroups": [
            {
                "name": "Core API",
                "tags": ["authentication", "keywords", "posts"],
                "description": "Essential API endpoints for basic functionality"
            },
            {
                "name": "Data Processing",
                "tags": ["crawling", "trends", "content"],
                "description": "Background processing and analysis endpoints"
            },
            {
                "name": "Public API",
                "tags": ["public-blog"],
                "description": "Public endpoints for blog site integration"
            },
            {
                "name": "System Management",
                "tags": ["tasks", "reddit", "monitoring"],
                "description": "System administration and monitoring endpoints"
            }
        ],
        "x-code-samples": {
            "curl": "true",
            "javascript": "true",
            "python": "true",
            "php": "false",
            "java": "false"
        }
    }


def get_enhanced_openapi_examples():
    """Get enhanced examples for OpenAPI documentation."""
    return {
        "authentication_flow": {
            "summary": "Complete Authentication Flow",
            "description": "Step-by-step authentication process",
            "value": {
                "step_1": {
                    "description": "Initiate OAuth2 flow",
                    "request": "GET /api/v1/auth/login",
                    "response": "Redirect to Reddit authorization"
                },
                "step_2": {
                    "description": "Exchange code for tokens",
                    "request": {
                        "method": "POST",
                        "url": "/api/v1/auth/login",
                        "body": {
                            "code": "authorization_code_from_reddit",
                            "state": "random_state_string"
                        }
                    },
                    "response": {
                        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                        "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                        "token_type": "bearer",
                        "expires_in": 900
                    }
                }
            }
        },
        "keyword_management": {
            "summary": "Keyword Management Workflow",
            "description": "Complete keyword lifecycle management",
            "value": {
                "create": {
                    "method": "POST",
                    "url": "/api/v1/keywords",
                    "body": {
                        "keyword": "artificial intelligence",
                        "description": "Track AI discussions and trends",
                        "is_active": True
                    }
                },
                "list": {
                    "method": "GET",
                    "url": "/api/v1/keywords?page=1&page_size=20&is_active=true"
                },
                "update": {
                    "method": "PUT",
                    "url": "/api/v1/keywords/1",
                    "body": {
                        "keyword": "machine learning",
                        "description": "Updated to focus on ML specifically"
                    }
                }
            }
        },
        "crawling_workflow": {
            "summary": "Content Crawling Workflow",
            "description": "Complete crawling process from start to results",
            "value": {
                "start_crawling": {
                    "method": "POST",
                    "url": "/api/v1/crawling/start",
                    "body": {
                        "keyword_ids": [1, 2, 3],
                        "subreddits": ["MachineLearning", "artificial", "technology"],
                        "limit": 100,
                        "time_filter": "week"
                    }
                },
                "check_status": {
                    "method": "GET",
                    "url": "/api/v1/crawling/status"
                },
                "view_results": {
                    "method": "GET",
                    "url": "/api/v1/posts?keyword_ids=1,2,3&page=1&page_size=20"
                }
            }
        },
        "content_generation": {
            "summary": "Content Generation Workflow",
            "description": "Generate blog content from collected data",
            "value": {
                "analyze_trends": {
                    "method": "GET",
                    "url": "/api/v1/trends?keyword_ids=1&time_period=7d"
                },
                "generate_content": {
                    "method": "POST",
                    "url": "/api/v1/content/generate",
                    "body": {
                        "content_type": "blog_post",
                        "keyword_ids": [1],
                        "template_id": 1,
                        "custom_prompt": "Write about recent AI trends"
                    }
                },
                "check_generation": {
                    "method": "GET",
                    "url": "/api/v1/content/tasks/{task_id}/status"
                }
            }
        }
    }


def get_api_documentation_config():
    """Get enhanced API documentation configuration."""
    return {
        "x-tagGroups": [
            {
                "name": "Core Features",
                "tags": ["authentication", "keywords", "crawling", "posts"]
            },
            {
                "name": "Analytics & Content",
                "tags": ["trends", "content"]
            },
            {
                "name": "Public & Monitoring",
                "tags": ["public-blog", "tasks", "reddit", "monitoring"]
            }
        ],
        "x-code-samples": [
            {
                "lang": "curl",
                "source": """# Authentication
curl -X GET "http://localhost:8000/api/v1/auth/login"

# Create keyword
curl -X POST "http://localhost:8000/api/v1/keywords" \\
  -H "Authorization: Bearer YOUR_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{"keyword": "artificial intelligence", "description": "AI discussions"}'

# Start crawling
curl -X POST "http://localhost:8000/api/v1/crawling/start" \\
  -H "Authorization: Bearer YOUR_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{"keyword_ids": [1], "limit": 100}'"""
            },
            {
                "lang": "python",
                "source": """import requests

# Authentication
auth_response = requests.get("http://localhost:8000/api/v1/auth/login")

# Create keyword
headers = {"Authorization": f"Bearer {access_token}"}
keyword_data = {
    "keyword": "artificial intelligence",
    "description": "AI discussions"
}
response = requests.post(
    "http://localhost:8000/api/v1/keywords",
    headers=headers,
    json=keyword_data
)

# Start crawling
crawl_data = {"keyword_ids": [1], "limit": 100}
crawl_response = requests.post(
    "http://localhost:8000/api/v1/crawling/start",
    headers=headers,
    json=crawl_data
)"""
            },
            {
                "lang": "javascript",
                "source": """// Authentication
const authResponse = await fetch('http://localhost:8000/api/v1/auth/login');

// Create keyword
const headers = {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
};

const keywordData = {
    keyword: 'artificial intelligence',
    description: 'AI discussions'
};

const response = await fetch('http://localhost:8000/api/v1/keywords', {
    method: 'POST',
    headers,
    body: JSON.stringify(keywordData)
});

# Start crawling
const crawlData = { keyword_ids: [1], limit: 100 };
const crawlResponse = await fetch('http://localhost:8000/api/v1/crawling/start', {
    method: 'POST',
    headers,
    body: JSON.stringify(crawlData)
});"""
            }
        ]
    }


def get_openapi_response_examples():
    """Get comprehensive response examples for OpenAPI documentation."""
    return {
        "success_responses": {
            "keyword_created": {
                "summary": "Keyword successfully created",
                "value": {
                    "id": 1,
                    "keyword": "artificial intelligence",
                    "description": "Track AI discussions and trends",
                    "is_active": True,
                    "user_id": 123,
                    "created_at": "2024-01-01T12:00:00Z",
                    "updated_at": "2024-01-01T12:00:00Z",
                    "stats": {
                        "total_posts": 0,
                        "last_crawl": None,
                        "avg_score": 0
                    }
                }
            },
            "posts_list": {
                "summary": "List of Reddit posts",
                "value": {
                    "data": [
                        {
                            "id": 1,
                            "reddit_id": "abc123",
                            "title": "Amazing breakthrough in AI research",
                            "content": "Researchers have developed...",
                            "author": "reddit_user",
                            "subreddit": "MachineLearning",
                            "score": 1250,
                            "num_comments": 89,
                            "url": "https://reddit.com/r/MachineLearning/comments/abc123",
                            "created_at": "2024-01-01T12:00:00Z",
                            "keyword_id": 1
                        }
                    ],
                    "pagination": {
                        "page": 1,
                        "per_page": 20,
                        "total": 150,
                        "pages": 8,
                        "has_next": True,
                        "has_prev": False
                    }
                }
            },
            "trend_analysis": {
                "summary": "Trend analysis results",
                "value": {
                    "keyword_id": 1,
                    "keyword": "artificial intelligence",
                    "time_period": "7d",
                    "metrics": {
                        "total_posts": 150,
                        "avg_score": 45.7,
                        "engagement_rate": 0.85,
                        "trend_velocity": 1.25,
                        "top_subreddits": [
                            {"subreddit": "MachineLearning", "post_count": 45},
                            {"subreddit": "artificial", "post_count": 32}
                        ],
                        "tfidf_scores": {
                            "ai": 0.85,
                            "machine": 0.72,
                            "learning": 0.68
                        }
                    },
                    "generated_at": "2024-01-01T12:00:00Z"
                }
            }
        },
        "error_responses": {
            "validation_error": {
                "summary": "Request validation failed",
                "value": {
                    "error_code": "validation_error",
                    "message": "Invalid input data",
                    "details": {
                        "keyword": ["This field is required"],
                        "email": ["Invalid email format"]
                    },
                    "timestamp": "2024-01-01T12:00:00Z",
                    "request_id": "req_123e4567-e89b-12d3-a456-426614174000"
                }
            },
            "unauthorized": {
                "summary": "Authentication required",
                "value": {
                    "error_code": "unauthorized",
                    "message": "Authentication required",
                    "details": {
                        "hint": "Include 'Authorization: Bearer <token>' header"
                    },
                    "timestamp": "2024-01-01T12:00:00Z",
                    "request_id": "req_123e4567-e89b-12d3-a456-426614174000"
                }
            },
            "rate_limit": {
                "summary": "Rate limit exceeded",
                "value": {
                    "error_code": "rate_limit_exceeded",
                    "message": "Rate limit exceeded",
                    "details": {
                        "limit": 60,
                        "window": "1 minute",
                        "retry_after": 45
                    },
                    "timestamp": "2024-01-01T12:00:00Z",
                    "request_id": "req_123e4567-e89b-12d3-a456-426614174000"
                }
            }
        }
    }


def get_api_documentation_config():
    """Get enhanced API documentation configuration."""
    return {
        "x-tagGroups": [
            {
                "name": "Authentication & Authorization",
                "tags": ["authentication"]
            },
            {
                "name": "Content Management",
                "tags": ["keywords", "posts", "content"]
            },
            {
                "name": "Data Collection & Analysis",
                "tags": ["crawling", "reddit", "trends"]
            },
            {
                "name": "Public APIs",
                "tags": ["public-blog"]
            },
            {
                "name": "System Management",
                "tags": ["tasks", "monitoring"]
            }
        ],
        "x-code-samples": {
            "authentication": {
                "curl": """# Start OAuth2 flow
curl -X GET "{{base_url}}/api/v1/auth/login"

# Exchange code for tokens
curl -X POST "{{base_url}}/api/v1/auth/login" \\
  -H "Content-Type: application/json" \\
  -d '{"code": "your_auth_code", "state": "your_state"}'

# Use access token
curl -X GET "{{base_url}}/api/v1/keywords" \\
  -H "Authorization: Bearer your_access_token"

# Refresh token
curl -X POST "{{base_url}}/api/v1/auth/refresh" \\
  -H "Authorization: Bearer your_refresh_token" """,
                "javascript": """// Authentication flow
const authUrl = '{{base_url}}/api/v1/auth/login';
window.location.href = authUrl;

// After OAuth callback, exchange code for tokens
const response = await fetch('{{base_url}}/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ code: authCode, state: stateParam })
});
const tokens = await response.json();

// Use access token in subsequent requests
const apiResponse = await fetch('{{base_url}}/api/v1/keywords', {
  headers: { 'Authorization': `Bearer ${tokens.access_token}` }
});""",
                "python": """import requests

# Start OAuth2 flow (redirect user to this URL)
auth_url = "{{base_url}}/api/v1/auth/login"

# Exchange code for tokens
response = requests.post("{{base_url}}/api/v1/auth/login", json={
    "code": "your_auth_code",
    "state": "your_state"
})
tokens = response.json()

# Use access token
headers = {"Authorization": f"Bearer {tokens['access_token']}"}
response = requests.get("{{base_url}}/api/v1/keywords", headers=headers)"""
            },
            "keywords": {
                "curl": """# Create keyword
curl -X POST "{{base_url}}/api/v1/keywords" \\
  -H "Authorization: Bearer your_token" \\
  -H "Content-Type: application/json" \\
  -d '{"keyword": "artificial intelligence", "description": "AI discussions"}'

# Get keywords with pagination
curl -X GET "{{base_url}}/api/v1/keywords?page=1&page_size=20" \\
  -H "Authorization: Bearer your_token" """,
                "javascript": """// Create keyword
const response = await fetch('{{base_url}}/api/v1/keywords', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    keyword: 'artificial intelligence',
    description: 'AI discussions'
  })
});

// Get keywords
const keywords = await fetch('{{base_url}}/api/v1/keywords?page=1&page_size=20', {
  headers: { 'Authorization': `Bearer ${accessToken}` }
}).then(r => r.json());""",
                "python": """import requests

headers = {"Authorization": f"Bearer {access_token}"}

# Create keyword
response = requests.post("{{base_url}}/api/v1/keywords", 
    headers=headers,
    json={"keyword": "artificial intelligence", "description": "AI discussions"}
)

# Get keywords
keywords = requests.get("{{base_url}}/api/v1/keywords?page=1&page_size=20", 
    headers=headers
).json()"""
            },
            "crawling": {
                "curl": """# Start crawling
curl -X POST "{{base_url}}/api/v1/crawling/start" \\
  -H "Authorization: Bearer your_token" \\
  -H "Content-Type: application/json" \\
  -d '{"keyword_ids": [1, 2], "limit": 100}'

# Check status
curl -X GET "{{base_url}}/api/v1/crawling/status" \\
  -H "Authorization: Bearer your_token" """,
                "javascript": """// Start crawling
const crawlResponse = await fetch('{{base_url}}/api/v1/crawling/start', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ keyword_ids: [1, 2], limit: 100 })
});

// Monitor status
const status = await fetch('{{base_url}}/api/v1/crawling/status', {
  headers: { 'Authorization': `Bearer ${accessToken}` }
}).then(r => r.json());""",
                "python": """import requests

headers = {"Authorization": f"Bearer {access_token}"}

# Start crawling
response = requests.post("{{base_url}}/api/v1/crawling/start",
    headers=headers,
    json={"keyword_ids": [1, 2], "limit": 100}
)

# Check status
status = requests.get("{{base_url}}/api/v1/crawling/status", 
    headers=headers
).json()"""
            }
        }
    }


def get_enhanced_openapi_examples():
    """Get enhanced examples for OpenAPI documentation."""
    return {
        "authentication_flow": {
            "summary": "Complete authentication workflow",
            "description": "Step-by-step authentication process from OAuth2 initiation to API usage",
            "steps": [
                {
                    "step": 1,
                    "title": "Initiate OAuth2 Flow",
                    "method": "GET",
                    "endpoint": "/api/v1/auth/login",
                    "description": "Redirects user to Reddit authorization page"
                },
                {
                    "step": 2,
                    "title": "Handle OAuth2 Callback",
                    "method": "POST",
                    "endpoint": "/api/v1/auth/login",
                    "body": {
                        "code": "authorization_code_from_reddit",
                        "state": "state_parameter_for_security"
                    },
                    "response": {
                        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                        "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                        "token_type": "bearer",
                        "expires_in": 900
                    }
                },
                {
                    "step": 3,
                    "title": "Use Access Token",
                    "method": "GET",
                    "endpoint": "/api/v1/keywords",
                    "headers": {
                        "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
                    }
                },
                {
                    "step": 4,
                    "title": "Refresh Token When Expired",
                    "method": "POST",
                    "endpoint": "/api/v1/auth/refresh",
                    "headers": {
                        "Authorization": "Bearer refresh_token_here"
                    }
                }
            ]
        },
        "content_generation_workflow": {
            "summary": "Complete content generation workflow",
            "description": "From keyword setup to content generation and retrieval",
            "steps": [
                {
                    "step": 1,
                    "title": "Create Keywords",
                    "method": "POST",
                    "endpoint": "/api/v1/keywords",
                    "body": {
                        "keyword": "artificial intelligence",
                        "description": "Track AI discussions and trends"
                    }
                },
                {
                    "step": 2,
                    "title": "Start Data Collection",
                    "method": "POST",
                    "endpoint": "/api/v1/crawling/start",
                    "body": {
                        "keyword_ids": [1],
                        "limit": 100,
                        "subreddits": ["MachineLearning", "artificial"]
                    }
                },
                {
                    "step": 3,
                    "title": "Monitor Collection Progress",
                    "method": "GET",
                    "endpoint": "/api/v1/crawling/status"
                },
                {
                    "step": 4,
                    "title": "Analyze Trends",
                    "method": "GET",
                    "endpoint": "/api/v1/trends?keyword_ids=1&time_period=7d"
                },
                {
                    "step": 5,
                    "title": "Generate Content",
                    "method": "POST",
                    "endpoint": "/api/v1/content/generate",
                    "body": {
                        "content_type": "blog_post",
                        "keyword_ids": [1],
                        "template_id": 1
                    }
                },
                {
                    "step": 6,
                    "title": "Retrieve Generated Content",
                    "method": "GET",
                    "endpoint": "/api/v1/content/{content_id}"
                }
            ]
        },
        "error_handling_examples": {
            "summary": "Common error scenarios and responses",
            "description": "Examples of error responses and how to handle them",
            "scenarios": [
                {
                    "scenario": "Invalid Authentication",
                    "status_code": 401,
                    "response": {
                        "error_code": "unauthorized",
                        "message": "Authentication required",
                        "details": {
                            "hint": "Include 'Authorization: Bearer <token>' header"
                        },
                        "timestamp": "2024-01-01T12:00:00Z",
                        "request_id": "req_123e4567-e89b-12d3-a456-426614174000"
                    }
                },
                {
                    "scenario": "Validation Error",
                    "status_code": 422,
                    "response": {
                        "error_code": "validation_error",
                        "message": "Invalid input data",
                        "details": {
                            "keyword": ["This field is required"],
                            "description": ["String too short"]
                        },
                        "timestamp": "2024-01-01T12:00:00Z",
                        "request_id": "req_123e4567-e89b-12d3-a456-426614174000"
                    }
                },
                {
                    "scenario": "Rate Limit Exceeded",
                    "status_code": 429,
                    "response": {
                        "error_code": "rate_limit_exceeded",
                        "message": "Rate limit exceeded",
                        "details": {
                            "limit": 60,
                            "window": "1 minute",
                            "retry_after": 45
                        },
                        "timestamp": "2024-01-01T12:00:00Z",
                        "request_id": "req_123e4567-e89b-12d3-a456-426614174000"
                    }
                }
            ]
        },
        "pagination_examples": {
            "summary": "Pagination patterns and examples",
            "description": "How to handle paginated responses across different endpoints",
            "examples": [
                {
                    "endpoint": "/api/v1/keywords",
                    "request": "GET /api/v1/keywords?page=2&page_size=20",
                    "response": {
                        "data": [
                            {
                                "id": 21,
                                "keyword": "machine learning",
                                "description": "ML discussions",
                                "is_active": True,
                                "created_at": "2024-01-01T12:00:00Z"
                            }
                        ],
                        "pagination": {
                            "page": 2,
                            "per_page": 20,
                            "total": 150,
                            "pages": 8,
                            "has_next": True,
                            "has_prev": True
                        }
                    }
                },
                {
                    "endpoint": "/api/v1/posts",
                    "request": "GET /api/v1/posts?limit=50&offset=100",
                    "response": {
                        "data": ["...posts..."],
                        "pagination": {
                            "limit": 50,
                            "offset": 100,
                            "total": 1500,
                            "has_more": True
                        }
                    }
                }
            ]
        }
    }


def get_api_schema_examples():
    """Get comprehensive API schema examples for documentation."""
    return {
        "request_examples": {
            "create_keyword": {
                "summary": "Create a new keyword",
                "value": {
                    "keyword": "artificial intelligence",
                    "description": "Track AI-related discussions and trends",
                    "is_active": True
                }
            },
            "bulk_create_keywords": {
                "summary": "Create multiple keywords",
                "value": {
                    "keywords": [
                        {
                            "keyword": "machine learning",
                            "description": "ML algorithms and applications"
                        },
                        {
                            "keyword": "deep learning",
                            "description": "Neural networks and deep learning"
                        },
                        {
                            "keyword": "natural language processing",
                            "description": "NLP and text processing"
                        }
                    ]
                }
            },
            "start_crawling": {
                "summary": "Start crawling with specific parameters",
                "value": {
                    "keyword_ids": [1, 2, 3],
                    "subreddits": ["MachineLearning", "artificial", "technology"],
                    "limit": 100,
                    "time_filter": "week",
                    "sort": "hot"
                }
            },
            "generate_content": {
                "summary": "Generate blog content",
                "value": {
                    "content_type": "blog_post",
                    "keyword_ids": [1, 2],
                    "template_id": 1,
                    "custom_prompt": "Write a comprehensive analysis of recent AI trends",
                    "date_from": "2024-01-01T00:00:00Z",
                    "date_to": "2024-01-31T23:59:59Z",
                    "max_posts": 50,
                    "min_score": 10
                }
            }
        },
        "response_examples": {
            "keyword_response": {
                "summary": "Keyword with statistics",
                "value": {
                    "id": 1,
                    "keyword": "artificial intelligence",
                    "description": "Track AI-related discussions and trends",
                    "is_active": True,
                    "user_id": 123,
                    "created_at": "2024-01-01T12:00:00Z",
                    "updated_at": "2024-01-01T12:05:00Z",
                    "stats": {
                        "total_posts": 150,
                        "last_crawl": "2024-01-01T11:00:00Z",
                        "avg_score": 45.7,
                        "top_subreddits": ["MachineLearning", "artificial", "technology"]
                    }
                }
            },
            "post_response": {
                "summary": "Reddit post with metadata",
                "value": {
                    "id": 1,
                    "reddit_id": "abc123",
                    "title": "Amazing breakthrough in AI research",
                    "content": "Researchers have developed a new AI model that...",
                    "author": "reddit_user",
                    "subreddit": "MachineLearning",
                    "score": 1250,
                    "num_comments": 89,
                    "url": "https://reddit.com/r/MachineLearning/comments/abc123",
                    "created_at": "2024-01-01T12:00:00Z",
                    "keyword_id": 1,
                    "sentiment_score": 0.8,
                    "engagement_rate": 0.15
                }
            },
            "trend_analysis_response": {
                "summary": "Comprehensive trend analysis",
                "value": {
                    "keyword_id": 1,
                    "keyword": "artificial intelligence",
                    "time_period": "7d",
                    "metrics": {
                        "total_posts": 150,
                        "avg_score": 45.7,
                        "engagement_rate": 0.85,
                        "trend_velocity": 1.25,
                        "sentiment_distribution": {
                            "positive": 0.6,
                            "neutral": 0.3,
                            "negative": 0.1
                        },
                        "top_subreddits": [
                            {"subreddit": "MachineLearning", "post_count": 45},
                            {"subreddit": "artificial", "post_count": 32},
                            {"subreddit": "technology", "post_count": 28}
                        ],
                        "tfidf_scores": {
                            "ai": 0.85,
                            "machine": 0.72,
                            "learning": 0.68,
                            "algorithm": 0.55,
                            "neural": 0.48
                        },
                        "trending_terms": [
                            {"term": "transformer", "score": 0.92, "growth": 0.35},
                            {"term": "gpt", "score": 0.88, "growth": 0.28},
                            {"term": "llm", "score": 0.75, "growth": 0.45}
                        ]
                    },
                    "generated_at": "2024-01-01T12:00:00Z",
                    "cache_expires_at": "2024-01-01T13:00:00Z"
                }
            },
            "content_generation_response": {
                "summary": "Generated content with metadata",
                "value": {
                    "id": 1,
                    "title": "The Future of Artificial Intelligence: Trends and Insights from Reddit",
                    "content": "# The Future of AI\n\nBased on recent Reddit discussions...",
                    "content_type": "blog_post",
                    "template_used": "default",
                    "keyword_ids": [1, 2],
                    "metadata": {
                        "word_count": 1250,
                        "reading_time": 5,
                        "sources_count": 15,
                        "generated_sections": ["introduction", "trends", "analysis", "conclusion"],
                        "quality_score": 0.87
                    },
                    "user_id": 123,
                    "created_at": "2024-01-01T12:00:00Z",
                    "updated_at": "2024-01-01T12:05:00Z",
                    "generation_stats": {
                        "processing_time_seconds": 45.2,
                        "posts_analyzed": 150,
                        "template_version": "1.2.0"
                    }
                }
            }
        }
    }