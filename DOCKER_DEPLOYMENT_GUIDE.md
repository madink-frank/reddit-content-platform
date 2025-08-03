# Docker Deployment Guide

This guide covers Docker containerization and deployment setup for the Reddit Content Platform across different environments.

## Overview

The platform supports three deployment environments:
- **Development**: Local development with hot reloading and debugging
- **Staging**: Pre-production testing environment
- **Production**: Optimized production deployment

## Quick Start

### Development Environment

```bash
# Using the development deployment script
./scripts/deploy-dev.sh

# Or manually with docker-compose
docker-compose -f docker-compose.dev.yml up -d

# With monitoring (Prometheus + Grafana)
docker-compose -f docker-compose.dev.yml --profile monitoring up -d
```

### Staging Environment

```bash
# Configure environment variables in .env.staging
cp .env.staging.example .env.staging
# Edit .env.staging with your staging configuration

# Deploy to staging
./scripts/deploy-staging.sh

# Force redeploy
./scripts/deploy-staging.sh --force
```

### Production Environment

```bash
# Configure environment variables
export DATABASE_URL="postgresql://user:pass@host:port/db"
export REDIS_URL="redis://host:port"
# ... other production variables

# Deploy to production
docker-compose -f docker-compose.prod.yml up -d
```

## Environment Configurations

### Development (.env.dev)

- SQLite database for simplicity
- Debug logging enabled
- Hot reloading with volume mounts
- Lower resource limits
- Development-friendly settings

### Staging (.env.staging)

- PostgreSQL database
- JSON structured logging
- Resource limits applied
- Production-like configuration
- SSL/TLS ready

### Production (.env.prod)

- Optimized multi-stage builds
- Minimal attack surface
- Resource constraints
- Health checks and monitoring
- Load balancing with Nginx

## Docker Images

### Base Images

- **API/Worker**: `python:3.12-slim` (multi-stage build for production)
- **Database**: `postgres:15-alpine`
- **Cache**: `redis:7-alpine`
- **Proxy**: `nginx:alpine`
- **Monitoring**: `prom/prometheus:latest`, `grafana/grafana:latest`

### Custom Images

The application uses custom Dockerfiles:

- `Dockerfile`: Development build with debugging tools
- `Dockerfile.production`: Optimized production build

## Services Architecture

```
┌─────────────────┐    ┌─────────────────┐
│   Nginx Proxy   │    │   Grafana UI    │
│   (Production)  │    │  (Monitoring)   │
└─────────┬───────┘    └─────────────────┘
          │
┌─────────▼───────┐    ┌─────────────────┐
│   FastAPI API   │    │   Prometheus    │
│   (Multiple)    │    │   (Metrics)     │
└─────────┬───────┘    └─────────────────┘
          │
┌─────────▼───────┐    ┌─────────────────┐
│ Celery Workers  │    │   PostgreSQL    │
│   (Multiple)    │◄───┤   (Database)    │
└─────────┬───────┘    └─────────────────┘
          │
┌─────────▼───────┐
│     Redis       │
│ (Cache/Queue)   │
└─────────────────┘
```

## Health Checks

All services include comprehensive health checks:

### API Service
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:$PORT/health || exit 1
```

### Database Service
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD pg_isready -U $POSTGRES_USER -d $POSTGRES_DB
```

### Redis Service
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD redis-cli ping
```

### Celery Worker
```dockerfile
HEALTHCHECK --interval=30s --timeout=15s --retries=3 \
    CMD celery -A app.core.celery_app inspect ping
```

## Resource Management

### Development
- Minimal resource constraints
- Focus on development experience
- Volume mounts for hot reloading

### Staging
```yaml
deploy:
  resources:
    limits:
      memory: 512M
      cpus: '0.5'
    reservations:
      memory: 256M
      cpus: '0.25'
```

### Production
```yaml
deploy:
  replicas: 2
  resources:
    limits:
      memory: 1G
      cpus: '1.0'
    reservations:
      memory: 512M
      cpus: '0.5'
```

## Security Features

### Container Security
- Non-root user execution
- Minimal base images
- Security headers in Nginx
- Network isolation
- Read-only file systems where possible

### Network Security
- Custom Docker networks
- Service-to-service communication
- Rate limiting in Nginx
- Connection limits

### Data Security
- Encrypted environment variables
- Secure secret management
- Database connection encryption
- Redis AUTH (when configured)

## Monitoring and Logging

### Prometheus Metrics
- Application metrics
- System metrics
- Custom business metrics
- Alert rules

### Grafana Dashboards
- System overview
- Application performance
- Business metrics
- Alert visualization

### Structured Logging
- JSON format in production
- Correlation IDs
- Error tracking
- Performance monitoring

## Deployment Scripts

### Development Deployment
```bash
./scripts/deploy-dev.sh [--clean]
```
- Builds and starts development environment
- Runs database migrations
- Shows service status and URLs

### Staging Deployment
```bash
./scripts/deploy-staging.sh [--force]
```
- Validates environment configuration
- Builds optimized images
- Performs health checks
- Runs migrations
- Verifies deployment

### Health Check Script
```bash
./scripts/docker-health-check.sh
```
- Comprehensive service health verification
- Database connectivity testing
- API endpoint validation
- Celery worker status

## Troubleshooting

### Common Issues

1. **Services not starting**
   ```bash
   # Check service logs
   docker-compose -f docker-compose.dev.yml logs [service_name]
   
   # Check service status
   docker-compose -f docker-compose.dev.yml ps
   ```

2. **Database connection issues**
   ```bash
   # Test database connectivity
   docker-compose -f docker-compose.dev.yml exec db psql -U reddit_user -d reddit_platform
   
   # Check database logs
   docker-compose -f docker-compose.dev.yml logs db
   ```

3. **Redis connection issues**
   ```bash
   # Test Redis connectivity
   docker-compose -f docker-compose.dev.yml exec redis redis-cli ping
   
   # Check Redis logs
   docker-compose -f docker-compose.dev.yml logs redis
   ```

4. **Celery worker issues**
   ```bash
   # Check worker status
   docker-compose -f docker-compose.dev.yml exec worker celery -A app.core.celery_app inspect ping
   
   # Check worker logs
   docker-compose -f docker-compose.dev.yml logs worker
   ```

### Performance Optimization

1. **Image Size Optimization**
   - Multi-stage builds
   - Minimal base images
   - Layer caching
   - .dockerignore usage

2. **Runtime Optimization**
   - Resource limits
   - Connection pooling
   - Caching strategies
   - Load balancing

3. **Storage Optimization**
   - Volume management
   - Data persistence
   - Backup strategies
   - Log rotation

## Maintenance

### Regular Tasks

1. **Image Updates**
   ```bash
   # Pull latest base images
   docker-compose pull
   
   # Rebuild with latest images
   docker-compose build --pull --no-cache
   ```

2. **Volume Cleanup**
   ```bash
   # Remove unused volumes
   docker volume prune
   
   # Remove unused images
   docker image prune -a
   ```

3. **Log Management**
   ```bash
   # View logs with timestamps
   docker-compose logs -t -f [service_name]
   
   # Limit log output
   docker-compose logs --tail=100 [service_name]
   ```

### Backup and Recovery

1. **Database Backup**
   ```bash
   # Create database backup
   docker-compose exec db pg_dump -U reddit_user reddit_platform > backup.sql
   
   # Restore database backup
   docker-compose exec -T db psql -U reddit_user reddit_platform < backup.sql
   ```

2. **Redis Backup**
   ```bash
   # Create Redis backup
   docker-compose exec redis redis-cli BGSAVE
   
   # Copy backup file
   docker cp $(docker-compose ps -q redis):/data/dump.rdb ./redis_backup.rdb
   ```

## Environment Variables Reference

### Required Variables
- `DATABASE_URL`: Database connection string
- `REDIS_URL`: Redis connection string
- `REDDIT_CLIENT_ID`: Reddit API client ID
- `REDDIT_CLIENT_SECRET`: Reddit API client secret
- `JWT_SECRET_KEY`: JWT signing secret

### Optional Variables
- `BACKEND_CORS_ORIGINS`: Allowed CORS origins
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `WORKERS`: Number of API workers (production)
- `SMTP_*`: Email configuration
- `WEBHOOK_URL`: Webhook notifications
- `ALERT_*`: Alert configuration

## Best Practices

1. **Security**
   - Use strong, unique secrets
   - Regularly update base images
   - Implement proper access controls
   - Monitor for vulnerabilities

2. **Performance**
   - Set appropriate resource limits
   - Use health checks
   - Implement proper caching
   - Monitor resource usage

3. **Reliability**
   - Use restart policies
   - Implement graceful shutdowns
   - Plan for failure scenarios
   - Regular backups

4. **Monitoring**
   - Collect comprehensive metrics
   - Set up alerting
   - Monitor logs
   - Track business metrics

## Support

For deployment issues:
1. Check service logs
2. Verify environment configuration
3. Test connectivity between services
4. Review resource usage
5. Check health check endpoints

For more detailed troubleshooting, refer to the application logs and monitoring dashboards.