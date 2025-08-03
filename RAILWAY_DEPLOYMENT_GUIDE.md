# Railway.com Deployment Guide

This guide explains how to deploy the Reddit Content Platform to Railway.com.

## Prerequisites

1. Railway.com account
2. GitHub repository with the project code
3. Reddit API credentials (Client ID and Secret)

## Deployment Steps

### 1. Create Railway Project

1. Go to [Railway.com](https://railway.app)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your Reddit Content Platform repository

### 2. Configure Services

Railway will automatically detect the `railway.toml` file and create the following services:

- **API Service**: Main FastAPI application
- **Worker Service**: Celery background workers
- **Scheduler Service**: Celery Beat scheduler

### 3. Add Database Services

#### PostgreSQL Database
1. In your Railway project, click "New Service"
2. Select "Database" → "PostgreSQL"
3. Railway will automatically provision a PostgreSQL instance
4. Note the connection details for environment variables

#### Redis Cache
1. Click "New Service" again
2. Select "Database" → "Redis"
3. Railway will provision a Redis instance
4. Note the connection details for environment variables

### 4. Configure Environment Variables

Set the following environment variables for each service:

#### API Service Variables
```bash
# Database
DATABASE_URL=postgresql://username:password@host:port/database  # From Railway PostgreSQL service

# Redis
REDIS_URL=redis://username:password@host:port  # From Railway Redis service

# Celery
CELERY_BROKER_URL=$REDIS_URL
CELERY_RESULT_BACKEND=$REDIS_URL

# Reddit API
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_REDIRECT_URI=https://your-app-domain.railway.app/api/v1/auth/callback

# JWT
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Application
ENVIRONMENT=production
API_V1_STR=/api/v1
PROJECT_NAME=Reddit Content Platform
VERSION=1.0.0

# CORS
BACKEND_CORS_ORIGINS=["https://your-frontend-domain.com"]

# Monitoring
PROMETHEUS_ENABLED=true
```

#### Worker Service Variables
Copy the same environment variables as the API service.

#### Scheduler Service Variables
Copy the same environment variables as the API service.

### 5. Deploy

1. Railway will automatically deploy when you push to your main branch
2. Monitor the deployment logs in the Railway dashboard
3. Once deployed, your API will be available at: `https://your-project-name.railway.app`

### 6. Run Database Migrations

After the first deployment:

1. Go to your API service in Railway dashboard
2. Open the "Deploy" tab
3. Click on "View Logs"
4. In the service settings, add a one-time deployment command:
   ```bash
   alembic upgrade head
   ```

Or use Railway CLI:
```bash
railway run alembic upgrade head
```

### 7. Verify Deployment

1. Check the health endpoint: `https://your-project-name.railway.app/health`
2. Access the API documentation: `https://your-project-name.railway.app/docs`
3. Test authentication endpoints
4. Verify Celery workers are running by checking logs

## Environment-Specific Configuration

### Production Environment
- Use strong JWT secret keys
- Enable HTTPS only
- Configure proper CORS origins
- Set up monitoring and alerting
- Use connection pooling for database

### Staging Environment
- Use separate database instances
- Relaxed CORS settings for testing
- Debug logging enabled
- Smaller worker concurrency

## Monitoring and Maintenance

### Health Checks
Railway automatically monitors the `/health` endpoint. The application includes:
- Basic health check at `/health`
- Detailed health check at `/health/detailed`
- Service-specific checks at `/health/{service_name}`

### Logs
Access logs through:
- Railway dashboard
- Railway CLI: `railway logs`
- Prometheus metrics at `/metrics`

### Scaling
- **API Service**: Can be scaled horizontally
- **Worker Service**: Scale based on queue length
- **Scheduler Service**: Should run only one instance

### Database Backups
Railway automatically backs up PostgreSQL databases. For additional safety:
- Set up regular database dumps
- Store backups in external storage
- Test restore procedures

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Verify DATABASE_URL is correct
   - Check if PostgreSQL service is running
   - Ensure network connectivity between services

2. **Celery Workers Not Starting**
   - Check CELERY_BROKER_URL and CELERY_RESULT_BACKEND
   - Verify Redis service is running
   - Check worker service logs

3. **Reddit API Authentication Fails**
   - Verify REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET
   - Check REDDIT_REDIRECT_URI matches Railway domain
   - Ensure Reddit app is configured correctly

4. **High Memory Usage**
   - Reduce Celery worker concurrency
   - Optimize database queries
   - Implement proper caching

### Getting Help

- Railway Documentation: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Project Issues: Create GitHub issues for application-specific problems

## Cost Optimization

- Use Railway's usage-based pricing efficiently
- Monitor resource usage in dashboard
- Scale services based on actual demand
- Use Redis for caching to reduce database load
- Optimize Docker images for faster deployments

## Security Best Practices

- Use Railway's environment variables for secrets
- Enable HTTPS only in production
- Implement rate limiting
- Regular security updates
- Monitor for suspicious activity
- Use strong authentication tokens