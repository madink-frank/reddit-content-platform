# Project Structure

## Backend Architecture (FastAPI)

```
app/
├── __init__.py
├── main.py                 # FastAPI application entry point
├── api/v1/                 # API routes organized by version
│   ├── api.py             # Main API router
│   └── endpoints/         # Individual endpoint modules
│       ├── auth.py        # Authentication endpoints
│       ├── keywords.py    # Keyword management
│       ├── posts.py       # Post retrieval and search
│       ├── trends.py      # Trend analysis endpoints
│       └── ...
├── core/                   # Core application components
│   ├── config.py          # Pydantic settings management
│   ├── database.py        # SQLAlchemy setup and session management
│   ├── security.py        # JWT and authentication utilities
│   ├── celery_app.py      # Celery configuration
│   ├── redis_client.py    # Redis connection and utilities
│   └── dependencies.py    # FastAPI dependency injection
├── models/                 # SQLAlchemy ORM models
│   ├── base.py            # Base model with common fields
│   ├── user.py            # User authentication model
│   ├── keyword.py         # Keyword tracking model
│   ├── post.py            # Reddit post model
│   └── ...
├── schemas/                # Pydantic schemas for API serialization
│   ├── auth.py            # Authentication request/response schemas
│   ├── keyword.py         # Keyword schemas
│   ├── post.py            # Post schemas
│   └── ...
├── services/               # Business logic layer
│   ├── auth_service.py    # Authentication business logic
│   ├── reddit_service.py  # Reddit API integration
│   ├── keyword_service.py # Keyword management logic
│   └── ...
├── workers/                # Celery background tasks
│   ├── crawling_tasks.py  # Reddit crawling tasks
│   ├── analysis_tasks.py  # Trend analysis tasks
│   └── ...
└── utils/                  # Utility functions and helpers
```

## Frontend Architecture (React + TypeScript)

```
admin-dashboard/
├── src/
│   ├── components/         # Reusable UI components
│   │   ├── ui/            # Base UI components
│   │   ├── forms/         # Form components
│   │   └── charts/        # Chart components
│   ├── pages/             # Route-based page components
│   │   ├── Dashboard.tsx  # Main dashboard
│   │   ├── Keywords.tsx   # Keyword management
│   │   └── Analytics.tsx  # Analytics and trends
│   ├── hooks/             # Custom React hooks
│   ├── services/          # API client and data fetching
│   ├── stores/            # Zustand state management
│   ├── types/             # TypeScript type definitions
│   ├── utils/             # Utility functions
│   └── App.tsx            # Main application component
├── public/                # Static assets
└── dist/                  # Build output
```

## Configuration and Infrastructure

```
.env                       # Environment variables (local)
.env.example              # Environment template
docker-compose.yml        # Development container setup
Dockerfile                # Production container
requirements.txt          # Python dependencies
alembic.ini              # Database migration config
pytest.ini               # Test configuration
```

## Architecture Patterns

### Backend Patterns
- **Layered Architecture**: API → Services → Models → Database
- **Dependency Injection**: FastAPI dependencies for database sessions, auth
- **Repository Pattern**: Services encapsulate data access logic
- **Background Tasks**: Celery workers for async operations
- **Configuration Management**: Pydantic Settings with environment variables

### API Design
- **RESTful Endpoints**: Standard HTTP methods and status codes
- **Versioned APIs**: `/api/v1/` prefix for version management
- **Consistent Response Format**: Standardized error and success responses
- **OpenAPI Documentation**: Auto-generated docs at `/docs`
- **Tag-based Organization**: Endpoints grouped by functionality

### Database Design
- **Base Model Pattern**: Common fields (id, created_at, updated_at) in BaseModel
- **Automatic Table Naming**: CamelCase class names → snake_case table names
- **Migration Management**: Alembic for schema versioning
- **Connection Pooling**: Configured for production PostgreSQL

### Frontend Patterns
- **Component-based Architecture**: Reusable UI components
- **Custom Hooks**: Encapsulate stateful logic and API calls
- **Global State Management**: Zustand for application state
- **Type Safety**: Full TypeScript coverage with strict mode
- **Atomic Design**: UI components organized by complexity level

## File Naming Conventions
- **Python**: snake_case for files, modules, functions, variables
- **Python Classes**: PascalCase for classes and models
- **TypeScript**: PascalCase for components, camelCase for functions/variables
- **API Endpoints**: kebab-case in URLs, snake_case in code
- **Database**: snake_case for tables and columns