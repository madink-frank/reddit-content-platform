# Database Setup Guide

This guide explains how to set up and manage the database for the Reddit Content Platform.

## Overview

The Reddit Content Platform uses:
- **PostgreSQL** as the primary database
- **Alembic** for database migrations
- **SQLAlchemy** as the ORM
- **Redis** for caching and task queues

## Quick Start

### 1. Environment Setup

Copy the environment template:
```bash
cp .env.example .env
```

Edit `.env` with your database credentials:
```bash
# For local development
DATABASE_URL=postgresql://username:password@localhost:5432/reddit_platform
REDIS_URL=redis://localhost:6379
```

### 2. Database Initialization

Use the database setup script:
```bash
# Check database connection
python scripts/db_setup.py check

# Initialize database (creates tables and runs migrations)
python scripts/db_setup.py init

# Check database health
python scripts/db_setup.py health
```

## Database Setup Scripts

### Main Setup Script: `scripts/db_setup.py`

This is the primary database management tool with the following commands:

```bash
# Check database connection
python scripts/db_setup.py check

# Get comprehensive health information
python scripts/db_setup.py health

# Initialize database (create tables and run migrations)
python scripts/db_setup.py init

# Run migrations only
python scripts/db_setup.py migrate

# Reset database (WARNING: deletes all data)
python scripts/db_setup.py reset --confirm

# Validate migration integrity
python scripts/db_setup.py validate

# Backup database schema
python scripts/db_setup.py backup

# Show complete status
python scripts/db_setup.py status
```

### Additional Scripts

- `scripts/test_db_connection.py` - Test database connectivity
- `scripts/init_db.py` - Simple database initialization
- `test_db_setup.py` - Verify database setup without connection

## Database Schema

The platform includes the following tables:

### Core Tables
- **users** - User accounts and authentication
- **keywords** - User-defined keywords for tracking
- **posts** - Reddit posts collected by crawling
- **comments** - Comments on Reddit posts

### System Tables
- **process_logs** - Background task execution logs
- **generated_content** - AI-generated content
- **metrics_cache** - Cached analytics and metrics

## Migration Management

### Alembic Commands

```bash
# Check current migration status
alembic current

# Show migration history
alembic history --verbose

# Create new migration (auto-generate from model changes)
alembic revision --autogenerate -m "Description of changes"

# Run migrations to latest version
alembic upgrade head

# Rollback to previous migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade <revision_id>
```

### Using Database Manager

```python
from app.core.db_manager import db_manager

# Check migration status
current = db_manager.get_current_revision()
head = db_manager.get_head_revision()
up_to_date = db_manager.is_database_up_to_date()

# Run migrations
success = db_manager.run_migrations()

# Create new migration
success = db_manager.create_migration("Add new feature")
```

## Development Setup

### Local PostgreSQL Setup

1. **Install PostgreSQL**:
   ```bash
   # macOS with Homebrew
   brew install postgresql
   brew services start postgresql
   
   # Ubuntu/Debian
   sudo apt-get install postgresql postgresql-contrib
   sudo systemctl start postgresql
   ```

2. **Create Database**:
   ```bash
   # Connect to PostgreSQL
   psql postgres
   
   # Create user and database
   CREATE USER username WITH PASSWORD 'password';
   CREATE DATABASE reddit_platform OWNER username;
   GRANT ALL PRIVILEGES ON DATABASE reddit_platform TO username;
   ```

3. **Update Environment**:
   ```bash
   DATABASE_URL=postgresql://username:password@localhost:5432/reddit_platform
   ```

### Docker Setup (Alternative)

Use Docker Compose for local development:

```yaml
# docker-compose.yml
version: '3.8'
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: reddit_platform
      POSTGRES_USER: username
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

Start services:
```bash
docker-compose up -d
```

## Production Deployment

### Railway.com Setup

1. **Create Railway Project**:
   - Add PostgreSQL service
   - Add Redis service
   - Deploy your application

2. **Environment Variables**:
   Railway automatically provides:
   - `DATABASE_URL`
   - `REDIS_URL`

   You need to set manually:
   - `REDDIT_CLIENT_ID`
   - `REDDIT_CLIENT_SECRET`
   - `JWT_SECRET_KEY`
   - `BACKEND_CORS_ORIGINS`

3. **Database Initialization**:
   ```bash
   # Run in Railway console or deployment script
   python scripts/db_setup.py init
   ```

### Other Cloud Providers

For AWS, GCP, Azure, or other providers:

1. Set up managed PostgreSQL and Redis services
2. Update `DATABASE_URL` and `REDIS_URL` environment variables
3. Run database initialization script
4. Set up monitoring and backups

## Health Monitoring

### Health Check Endpoints

The application provides health check endpoints:

```bash
# Basic health check
curl http://localhost:8000/health

# Detailed health information
curl http://localhost:8000/health/detailed
```

### Database Health Monitoring

```python
from app.core.database import check_database_health
from app.core.db_manager import check_db_health

# Basic health check
is_healthy = await check_database_health()

# Comprehensive health check
health_info = await check_db_health()
```

## Troubleshooting

### Common Issues

1. **Connection Refused**:
   - Check if PostgreSQL is running
   - Verify connection credentials
   - Check firewall settings

2. **Migration Errors**:
   - Check current migration status: `alembic current`
   - Validate migration integrity: `python scripts/db_setup.py validate`
   - Reset if necessary: `python scripts/db_setup.py reset --confirm`

3. **Permission Errors**:
   - Ensure database user has proper permissions
   - Check table ownership and grants

4. **Performance Issues**:
   - Monitor connection pool usage
   - Check for long-running queries
   - Optimize database indexes

### Debug Commands

```bash
# Test database connection
python scripts/test_db_connection.py

# Validate setup without connection
python test_db_setup.py

# Check migration integrity
python scripts/db_setup.py validate

# Get detailed status
python scripts/db_setup.py status --verbose
```

### Logging

Enable detailed database logging:

```python
# In app/core/database.py
engine = create_engine(
    settings.DATABASE_URL,
    echo=True,  # Enable SQL query logging
    echo_pool=True,  # Enable connection pool logging
)
```

## Backup and Recovery

### Schema Backup

```bash
# Backup database schema
python scripts/db_setup.py backup
```

### Data Backup

```bash
# PostgreSQL dump
pg_dump -h localhost -U username -d reddit_platform > backup.sql

# Restore from dump
psql -h localhost -U username -d reddit_platform < backup.sql
```

### Migration Rollback

```bash
# Rollback to previous version
alembic downgrade -1

# Rollback to specific revision
alembic downgrade <revision_id>

# Using database manager
python -c "from app.core.db_manager import rollback_migration; rollback_migration('-1')"
```

## Best Practices

1. **Always backup before major changes**
2. **Test migrations on staging environment first**
3. **Monitor database performance and connection pool usage**
4. **Use transactions for data consistency**
5. **Implement proper error handling and logging**
6. **Regular health checks and monitoring**
7. **Keep migration files in version control**
8. **Document schema changes and migration reasons**

## API Reference

### Database Functions

```python
# Connection management
from app.core.database import get_db, close_db_connections

# Health checks
from app.core.database import check_database_health, test_database_connection

# Migration management
from app.core.db_manager import db_manager

# Quick setup
from app.core.database import quick_setup
```

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Yes | - |
| `REDIS_URL` | Redis connection string | Yes | - |
| `JWT_SECRET_KEY` | JWT signing key | Yes | - |
| `REDDIT_CLIENT_ID` | Reddit API client ID | Yes | - |
| `REDDIT_CLIENT_SECRET` | Reddit API client secret | Yes | - |

## Support

For issues or questions:
1. Check this documentation
2. Review error logs
3. Run diagnostic scripts
4. Check database connectivity
5. Validate migration status