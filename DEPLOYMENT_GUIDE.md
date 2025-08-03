# Deployment Guide and Operations Manual

## Overview

This comprehensive guide covers deployment strategies, configuration management, and operational procedures for the Reddit Content Platform. The platform supports multiple deployment environments and provides detailed instructions for each.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [Environment Configuration](#environment-configuration)
4. [Local Development](#local-development)
5. [Docker Deployment](#docker-deployment)
6. [Production Deployment](#production-deployment)
7. [Railway Deployment](#railway-deployment)
8. [Frontend Deployment](#frontend-deployment)
9. [Database Management](#database-management)
10. [Monitoring and Logging](#monitoring-and-logging)
11. [Security Configuration](#security-configuration)
12. [Backup and Recovery](#backup-and-recovery)
13. [Scaling and Performance](#scaling-and-performance)
14. [Troubleshooting](#troubleshooting)
15. [Maintenance Procedures](#maintenance-procedures)

## Architecture Overview

### System Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Admin         │    │   Blog Site     │
│   (React)       │    │   Dashboard     │    │   (Next.js)     │
│   Port: 3000    │    │   Port: 3001    │    │   Port: 3002    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Load Balancer │
                    │   (Nginx)       │
                    │   Port: 80/443  │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │   API Server    │
                    │   (FastAPI)     │
                    │   Port: 8000    │
                    └─────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PostgreSQL    │    │   Redis         │    │   Celery        │
│   Port: 5432    │    │   Port: 6379    │    │   Workers       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Deployment Environments

1. **Development**: Local development with SQLite and Redis
2. **Staging**: Docker-based staging environment
3. **Production**: Full production deployment with monitoring
4. **Railway**: Cloud deployment on Railway platform

## Prerequisites

### System Requirements

#### Minimum Requirements
- **CPU**: 2 cores
- **RAM**: 4GB
- **Storage**: 20GB SSD
- **OS**: Ubuntu 20.04+, CentOS 8+, or macOS 10.15+

#### Recommended Requirements
- **CPU**: 4+ cores
- **RAM**: 8GB+
- **Storage**: 50GB+ SSD
- **OS**: Ubuntu 22.04 LTS

### Software Dependencies

#### Required Software
```bash
# Python 3.12+
python3 --version

# Node.js 18+
node --version
npm --version

# Docker and Docker Compose
docker --version
docker-compose --version

# Git
git --version
```

#### Database Requirements
- **PostgreSQL**: 13+ (production)
- **Redis**: 6+ (caching and queues)
- **SQLite**: 3.35+ (development only)

### External Services

#### Required Services
- **Reddit API**: OAuth2 application registration
- **Email Service**: SMTP server for notifications (optional)
- **CDN**: Content delivery network (optional)

#### Optional Services
- **Monitoring**: Prometheus + Grafana
- **Logging**: ELK Stack or similar
- **Backup**: S3-compatible storage

## Environment Configuration

### Environment Variables

#### Core Configuration
```bash
# Application
APP_NAME="Reddit Content Platform"
APP_VERSION="1.0.0"
ENVIRONMENT="production"  # development, staging, production
DEBUG=false
SECRET_KEY="your-secret-key-here"

# Database
DATABASE_URL="postgresql://user:password@localhost:5432/reddit_platform"
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30

# Redis
REDIS_URL="redis://localhost:6379/0"
REDIS_CACHE_DB=1
REDIS_SESSION_DB=2

# Reddit API
REDDIT_CLIENT_ID="your-reddit-client-id"
REDDIT_CLIENT_SECRET="your-reddit-client-secret"
REDDIT_USER_AGENT="Reddit Content Platform v1.0"
REDDIT_REDIRECT_URI="http://localhost:8000/api/v1/auth/callback"

# JWT Configuration
JWT_SECRET_KEY="your-jwt-secret-key"
JWT_ALGORITHM="HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Celery
CELERY_BROKER_URL="redis://localhost:6379/3"
CELERY_RESULT_BACKEND="redis://localhost:6379/4"
CELERY_TASK_SERIALIZER="json"
CELERY_RESULT_SERIALIZER="json"

# API Configuration
API_V1_STR="/api/v1"
CORS_ORIGINS=["http://localhost:3000", "http://localhost:3001"]
RATE_LIMIT_PER_MINUTE=60

# Monitoring
PROMETHEUS_ENABLED=true
PROMETHEUS_PORT=9090
GRAFANA_ENABLED=true
GRAFANA_PORT=3000

# Logging
LOG_LEVEL="INFO"
LOG_FORMAT="json"
LOG_FILE="/var/log/reddit-platform/app.log"
```

#### Frontend Configuration
```bash
# Admin Dashboard (.env)
VITE_API_BASE_URL="http://localhost:8000"
VITE_APP_NAME="Reddit Content Platform Admin"
VITE_APP_VERSION="1.0.0"
VITE_ENVIRONMENT="production"

# Blog Site (.env.local)
NEXT_PUBLIC_API_BASE_URL="http://localhost:8000"
NEXT_PUBLIC_SITE_NAME="Reddit Content Platform Blog"
NEXT_PUBLIC_SITE_URL="https://blog.yourplatform.com"
NEXT_PUBLIC_ANALYTICS_ID="your-analytics-id"
```

### Configuration Files

#### Environment-Specific Files
```
.env                    # Default environment variables
.env.development       # Development overrides
.env.staging          # Staging overrides
.env.production       # Production overrides
```

#### Docker Configuration
```
docker-compose.yml          # Development
docker-compose.staging.yml  # Staging
docker-compose.prod.yml     # Production
```

## Local Development

### Quick Start

#### 1. Clone Repository
```bash
git clone https://github.com/your-username/reddit-content-platform.git
cd reddit-content-platform
```

#### 2. Backend Setup
```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # or .venv/bin/activate.fish

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your configuration

# Initialize database
alembic upgrade head

# Start Redis (if not using Docker)
redis-server

# Start Celery worker
celery -A app.core.celery_app worker --loglevel=info &

# Start API server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 3. Frontend Setup
```bash
# Admin Dashboard
cd admin-dashboard
npm install
cp .env.example .env
npm run dev

# Blog Site (in another terminal)
cd ../blog-site
npm install
cp .env.example .env.local
npm run dev
```

### Development Tools

#### Database Management
```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# Reset database
python scripts/init_db.py
```

#### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test types
pytest -m unit
pytest -m integration
```

#### Code Quality
```bash
# Format code
black app/
isort app/

# Lint code
flake8 app/

# Type checking
mypy app/
```

## Docker Deployment

### Development with Docker

#### Start All Services
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

#### Individual Services
```bash
# Start specific services
docker-compose up -d postgres redis

# Rebuild and start
docker-compose up -d --build api

# Execute commands in containers
docker-compose exec api alembic upgrade head
docker-compose exec api python scripts/init_db.py
```

### Staging Deployment

#### Configuration
```bash
# Use staging configuration
docker-compose -f docker-compose.staging.yml up -d

# Environment variables
cp .env.staging .env

# Initialize staging database
docker-compose -f docker-compose.staging.yml exec api alembic upgrade head
```

#### Staging Services
```yaml
# docker-compose.staging.yml
version: '3.8'
services:
  api:
    build: .
    environment:
      - ENVIRONMENT=staging
      - DATABASE_URL=postgresql://user:pass@postgres:5432/reddit_platform_staging
    depends_on:
      - postgres
      - redis
    
  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=reddit_platform_staging
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_staging_data:/var/lib/postgresql/data
    
  redis:
    image: redis:7-alpine
    volumes:
      - redis_staging_data:/data

volumes:
  postgres_staging_data:
  redis_staging_data:
```

## Production Deployment

### Server Setup

#### 1. Server Preparation
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Nginx
sudo apt install nginx -y

# Install Certbot for SSL
sudo apt install certbot python3-certbot-nginx -y
```

#### 2. Application Deployment
```bash
# Clone repository
git clone https://github.com/your-username/reddit-content-platform.git
cd reddit-content-platform

# Setup production environment
cp .env.production .env
# Edit .env with production values

# Start production services
docker-compose -f docker-compose.prod.yml up -d

# Initialize database
docker-compose -f docker-compose.prod.yml exec api alembic upgrade head

# Create admin user (if needed)
docker-compose -f docker-compose.prod.yml exec api python scripts/create_admin.py
```

#### 3. Nginx Configuration
```nginx
# /etc/nginx/sites-available/reddit-platform
server {
    listen 80;
    server_name api.yourplatform.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 80;
    server_name admin.yourplatform.com;
    
    location / {
        proxy_pass http://localhost:3001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 80;
    server_name blog.yourplatform.com;
    
    location / {
        proxy_pass http://localhost:3002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### 4. SSL Configuration
```bash
# Enable sites
sudo ln -s /etc/nginx/sites-available/reddit-platform /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Get SSL certificates
sudo certbot --nginx -d api.yourplatform.com
sudo certbot --nginx -d admin.yourplatform.com
sudo certbot --nginx -d blog.yourplatform.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### Production Configuration

#### Docker Compose Production
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  api:
    build:
      context: .
      dockerfile: Dockerfile.production
    environment:
      - ENVIRONMENT=production
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    depends_on:
      - postgres
      - redis
    
  celery-worker:
    build:
      context: .
      dockerfile: Dockerfile.production
    command: celery -A app.core.celery_app worker --loglevel=info
    environment:
      - ENVIRONMENT=production
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    depends_on:
      - postgres
      - redis
    
  celery-beat:
    build:
      context: .
      dockerfile: Dockerfile.production
    command: celery -A app.core.celery_app beat --loglevel=info
    environment:
      - ENVIRONMENT=production
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    depends_on:
      - postgres
      - redis
    
  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=reddit_platform
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    restart: unless-stopped
    
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    restart: unless-stopped
    
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/prod.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl/certs
    restart: unless-stopped
    depends_on:
      - api

volumes:
  postgres_data:
  redis_data:
```

## Railway Deployment

### Railway Setup

#### 1. Railway CLI Installation
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Initialize project
railway init
```

#### 2. Service Configuration
```bash
# Create services
railway add --service postgres
railway add --service redis
railway add --service api

# Set environment variables
railway variables set DATABASE_URL=${{Postgres.DATABASE_URL}}
railway variables set REDIS_URL=${{Redis.REDIS_URL}}
railway variables set ENVIRONMENT=production
```

#### 3. Deployment Configuration
```yaml
# railway.toml
[build]
builder = "DOCKERFILE"
dockerfilePath = "Dockerfile.production"

[deploy]
healthcheckPath = "/health"
healthcheckTimeout = 300
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10

[[services]]
name = "api"
source = "."

[services.variables]
ENVIRONMENT = "production"
PORT = "8000"

[[services]]
name = "worker"
source = "."
command = "celery -A app.core.celery_app worker --loglevel=info"

[[services]]
name = "scheduler"
source = "."
command = "celery -A app.core.celery_app beat --loglevel=info"
```

#### 4. Deploy to Railway
```bash
# Deploy application
railway up

# Check deployment status
railway status

# View logs
railway logs

# Connect to database
railway connect postgres
```

## Frontend Deployment

### Admin Dashboard Deployment

#### Build for Production
```bash
cd admin-dashboard

# Install dependencies
npm install

# Build for production
npm run build

# Preview build
npm run preview
```

#### Deploy to Vercel
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel --prod

# Set environment variables
vercel env add VITE_API_BASE_URL production
```

#### Deploy to Netlify
```bash
# Build and deploy
npm run build
npx netlify deploy --prod --dir=dist

# Set environment variables in Netlify dashboard
```

### Blog Site Deployment

#### Build for Production
```bash
cd blog-site

# Install dependencies
npm install

# Build for production
npm run build

# Start production server
npm start
```

#### Deploy to Vercel
```bash
# Deploy with Vercel
vercel --prod

# Environment variables
vercel env add NEXT_PUBLIC_API_BASE_URL production
vercel env add NEXT_PUBLIC_SITE_URL production
```

#### Deploy to Netlify
```bash
# Build and deploy
npm run build
npx netlify deploy --prod --dir=.next
```

## Database Management

### PostgreSQL Setup

#### Installation
```bash
# Ubuntu/Debian
sudo apt install postgresql postgresql-contrib

# Start service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql
CREATE DATABASE reddit_platform;
CREATE USER reddit_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE reddit_platform TO reddit_user;
```

#### Configuration
```bash
# Edit postgresql.conf
sudo nano /etc/postgresql/15/main/postgresql.conf

# Key settings
listen_addresses = '*'
max_connections = 100
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB

# Edit pg_hba.conf for authentication
sudo nano /etc/postgresql/15/main/pg_hba.conf

# Add line for application access
host reddit_platform reddit_user 0.0.0.0/0 md5
```

### Database Migrations

#### Alembic Setup
```bash
# Initialize Alembic (if not done)
alembic init alembic

# Generate migration
alembic revision --autogenerate -m "Initial migration"

# Apply migration
alembic upgrade head

# Check current version
alembic current

# Migration history
alembic history
```

#### Migration Best Practices
```bash
# Always backup before migrations
pg_dump reddit_platform > backup_$(date +%Y%m%d_%H%M%S).sql

# Test migrations on staging first
alembic upgrade head --sql > migration.sql
# Review SQL before applying

# Rollback if needed
alembic downgrade -1
```

### Database Maintenance

#### Regular Maintenance
```sql
-- Analyze tables for query optimization
ANALYZE;

-- Vacuum to reclaim space
VACUUM;

-- Reindex for performance
REINDEX DATABASE reddit_platform;

-- Check database size
SELECT pg_size_pretty(pg_database_size('reddit_platform'));

-- Check table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

#### Performance Monitoring
```sql
-- Check slow queries
SELECT query, mean_time, calls, total_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

-- Check connection stats
SELECT * FROM pg_stat_activity;

-- Check index usage
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;
```

## Monitoring and Logging

### Prometheus Setup

#### Installation
```bash
# Create prometheus user
sudo useradd --no-create-home --shell /bin/false prometheus

# Download and install
wget https://github.com/prometheus/prometheus/releases/download/v2.40.0/prometheus-2.40.0.linux-amd64.tar.gz
tar xvf prometheus-2.40.0.linux-amd64.tar.gz
sudo cp prometheus-2.40.0.linux-amd64/prometheus /usr/local/bin/
sudo cp prometheus-2.40.0.linux-amd64/promtool /usr/local/bin/

# Create directories
sudo mkdir /etc/prometheus
sudo mkdir /var/lib/prometheus
sudo chown prometheus:prometheus /var/lib/prometheus
```

#### Configuration
```yaml
# /etc/prometheus/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  - job_name: 'reddit-platform-api'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    scrape_interval: 5s
    
  - job_name: 'postgres'
    static_configs:
      - targets: ['localhost:9187']
      
  - job_name: 'redis'
    static_configs:
      - targets: ['localhost:9121']
      
  - job_name: 'node'
    static_configs:
      - targets: ['localhost:9100']
```

#### Service Configuration
```ini
# /etc/systemd/system/prometheus.service
[Unit]
Description=Prometheus
Wants=network-online.target
After=network-online.target

[Service]
User=prometheus
Group=prometheus
Type=simple
ExecStart=/usr/local/bin/prometheus \
    --config.file /etc/prometheus/prometheus.yml \
    --storage.tsdb.path /var/lib/prometheus/ \
    --web.console.templates=/etc/prometheus/consoles \
    --web.console.libraries=/etc/prometheus/console_libraries \
    --web.listen-address=0.0.0.0:9090 \
    --web.enable-lifecycle

[Install]
WantedBy=multi-user.target
```

### Grafana Setup

#### Installation
```bash
# Add Grafana repository
sudo apt-get install -y software-properties-common
sudo add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -

# Install Grafana
sudo apt-get update
sudo apt-get install grafana

# Start service
sudo systemctl start grafana-server
sudo systemctl enable grafana-server
```

#### Dashboard Configuration
```json
{
  "dashboard": {
    "title": "Reddit Content Platform",
    "panels": [
      {
        "title": "API Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      },
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ]
      }
    ]
  }
}
```

### Logging Configuration

#### Structured Logging
```python
# app/core/logging.py
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
            
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
            
        return json.dumps(log_entry)
```

#### Log Rotation
```bash
# /etc/logrotate.d/reddit-platform
/var/log/reddit-platform/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        systemctl reload reddit-platform
    endscript
}
```

## Security Configuration

### SSL/TLS Setup

#### Let's Encrypt with Certbot
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get certificates
sudo certbot --nginx -d api.yourplatform.com
sudo certbot --nginx -d admin.yourplatform.com
sudo certbot --nginx -d blog.yourplatform.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

#### Manual SSL Configuration
```nginx
server {
    listen 443 ssl http2;
    server_name api.yourplatform.com;
    
    ssl_certificate /etc/ssl/certs/api.yourplatform.com.crt;
    ssl_certificate_key /etc/ssl/private/api.yourplatform.com.key;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    add_header Strict-Transport-Security "max-age=63072000" always;
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
}
```

### Firewall Configuration

#### UFW Setup
```bash
# Enable UFW
sudo ufw enable

# Allow SSH
sudo ufw allow ssh

# Allow HTTP/HTTPS
sudo ufw allow 80
sudo ufw allow 443

# Allow specific services
sudo ufw allow 8000  # API
sudo ufw allow 5432  # PostgreSQL (if external access needed)
sudo ufw allow 6379  # Redis (if external access needed)

# Check status
sudo ufw status
```

#### iptables Rules
```bash
# Basic iptables rules
sudo iptables -A INPUT -i lo -j ACCEPT
sudo iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
sudo iptables -A INPUT -j DROP

# Save rules
sudo iptables-save > /etc/iptables/rules.v4
```

### Application Security

#### Environment Variables Security
```bash
# Secure environment files
chmod 600 .env*
chown root:root .env*

# Use secrets management in production
# Example with Docker secrets
echo "your-secret-key" | docker secret create jwt_secret -
```

#### Database Security
```sql
-- Create read-only user for monitoring
CREATE USER monitoring WITH PASSWORD 'monitoring_password';
GRANT CONNECT ON DATABASE reddit_platform TO monitoring;
GRANT USAGE ON SCHEMA public TO monitoring;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO monitoring;

-- Revoke unnecessary permissions
REVOKE ALL ON SCHEMA public FROM PUBLIC;
GRANT USAGE ON SCHEMA public TO reddit_user;
```

## Backup and Recovery

### Database Backups

#### Automated Backup Script
```bash
#!/bin/bash
# /usr/local/bin/backup-db.sh

DB_NAME="reddit_platform"
DB_USER="reddit_user"
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/reddit_platform_$DATE.sql"

# Create backup
pg_dump -h localhost -U $DB_USER -d $DB_NAME > $BACKUP_FILE

# Compress backup
gzip $BACKUP_FILE

# Remove backups older than 30 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete

# Upload to S3 (optional)
# aws s3 cp $BACKUP_FILE.gz s3://your-backup-bucket/database/
```

#### Cron Job for Backups
```bash
# Add to crontab
sudo crontab -e

# Daily backup at 2 AM
0 2 * * * /usr/local/bin/backup-db.sh

# Weekly full backup at 3 AM on Sundays
0 3 * * 0 /usr/local/bin/full-backup.sh
```

### Application Backups

#### File System Backup
```bash
#!/bin/bash
# /usr/local/bin/backup-app.sh

APP_DIR="/opt/reddit-platform"
BACKUP_DIR="/backups/app"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup
tar -czf $BACKUP_DIR/app_backup_$DATE.tar.gz \
    --exclude='*.log' \
    --exclude='__pycache__' \
    --exclude='node_modules' \
    --exclude='.git' \
    $APP_DIR

# Remove old backups
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

### Recovery Procedures

#### Database Recovery
```bash
# Stop application
docker-compose down

# Restore database
gunzip reddit_platform_20240101_120000.sql.gz
psql -h localhost -U reddit_user -d reddit_platform < reddit_platform_20240101_120000.sql

# Start application
docker-compose up -d

# Verify recovery
docker-compose exec api python scripts/verify_db.py
```

#### Application Recovery
```bash
# Extract backup
tar -xzf app_backup_20240101_120000.tar.gz -C /opt/

# Restore configuration
cp /backups/config/.env /opt/reddit-platform/

# Restart services
docker-compose up -d --build

# Verify application
curl http://localhost:8000/health
```

## Scaling and Performance

### Horizontal Scaling

#### Load Balancer Configuration
```nginx
# /etc/nginx/conf.d/load-balancer.conf
upstream api_servers {
    server api1.internal:8000;
    server api2.internal:8000;
    server api3.internal:8000;
}

server {
    listen 80;
    server_name api.yourplatform.com;
    
    location / {
        proxy_pass http://api_servers;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

#### Docker Swarm Deployment
```yaml
# docker-stack.yml
version: '3.8'
services:
  api:
    image: reddit-platform:latest
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
      restart_policy:
        condition: on-failure
    networks:
      - reddit-platform
    
  worker:
    image: reddit-platform:latest
    command: celery -A app.core.celery_app worker --loglevel=info
    deploy:
      replicas: 2
    networks:
      - reddit-platform

networks:
  reddit-platform:
    driver: overlay
```

### Database Scaling

#### Read Replicas
```python
# app/core/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Master database (write)
master_engine = create_engine(DATABASE_URL)
MasterSession = sessionmaker(bind=master_engine)

# Read replica (read-only)
replica_engine = create_engine(READ_REPLICA_URL)
ReplicaSession = sessionmaker(bind=replica_engine)

def get_db_session(read_only=False):
    if read_only:
        return ReplicaSession()
    return MasterSession()
```

#### Connection Pooling
```python
# app/core/database.py
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

### Caching Strategy

#### Redis Clustering
```yaml
# docker-compose.redis-cluster.yml
version: '3.8'
services:
  redis-master:
    image: redis:7-alpine
    command: redis-server --appendonly yes --replica-announce-ip redis-master
    
  redis-replica-1:
    image: redis:7-alpine
    command: redis-server --replicaof redis-master 6379
    depends_on:
      - redis-master
      
  redis-replica-2:
    image: redis:7-alpine
    command: redis-server --replicaof redis-master 6379
    depends_on:
      - redis-master
```

#### Application-Level Caching
```python
# app/core/cache.py
from functools import wraps
import redis
import json

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_result(expiration=3600):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            redis_client.setex(cache_key, expiration, json.dumps(result))
            return result
        return wrapper
    return decorator
```

## Troubleshooting

### Common Issues

#### Application Won't Start
```bash
# Check logs
docker-compose logs api

# Common issues:
# 1. Database connection
docker-compose exec api python -c "from app.core.database import engine; print(engine.execute('SELECT 1'))"

# 2. Redis connection
docker-compose exec api python -c "from app.core.redis_client import redis_client; print(redis_client.ping())"

# 3. Environment variables
docker-compose exec api env | grep -E "(DATABASE|REDIS|SECRET)"

# 4. Port conflicts
sudo netstat -tulpn | grep :8000
```

#### Database Connection Issues
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check connections
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity;"

# Check configuration
sudo -u postgres psql -c "SHOW config_file;"

# Test connection
psql -h localhost -U reddit_user -d reddit_platform -c "SELECT version();"
```

#### Performance Issues
```bash
# Check system resources
htop
df -h
free -h

# Check database performance
sudo -u postgres psql reddit_platform -c "
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;"

# Check Redis performance
redis-cli info stats
redis-cli slowlog get 10
```

#### SSL Certificate Issues
```bash
# Check certificate validity
openssl x509 -in /etc/ssl/certs/api.yourplatform.com.crt -text -noout

# Test SSL connection
openssl s_client -connect api.yourplatform.com:443

# Renew Let's Encrypt certificates
sudo certbot renew --dry-run
sudo certbot renew
```

### Debugging Tools

#### Application Debugging
```python
# Enable debug mode
import logging
logging.basicConfig(level=logging.DEBUG)

# Add debug endpoints
@app.get("/debug/health")
async def debug_health():
    return {
        "database": await check_database(),
        "redis": await check_redis(),
        "celery": await check_celery(),
        "environment": os.environ.get("ENVIRONMENT")
    }
```

#### Database Debugging
```sql
-- Check slow queries
SELECT query, mean_time, calls, total_time
FROM pg_stat_statements
WHERE mean_time > 1000
ORDER BY mean_time DESC;

-- Check locks
SELECT * FROM pg_locks WHERE NOT granted;

-- Check table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

## Maintenance Procedures

### Regular Maintenance Tasks

#### Daily Tasks
```bash
#!/bin/bash
# daily-maintenance.sh

# Check system health
curl -f http://localhost:8000/health || echo "API health check failed"

# Check disk space
df -h | awk '$5 > 80 {print "Warning: " $0}'

# Check logs for errors
grep -i error /var/log/reddit-platform/*.log | tail -10

# Backup database
/usr/local/bin/backup-db.sh

# Clean up old logs
find /var/log/reddit-platform -name "*.log" -mtime +7 -delete
```

#### Weekly Tasks
```bash
#!/bin/bash
# weekly-maintenance.sh

# Update system packages
sudo apt update && sudo apt list --upgradable

# Analyze database
docker-compose exec postgres psql -U reddit_user -d reddit_platform -c "ANALYZE;"

# Check SSL certificate expiration
for domain in api.yourplatform.com admin.yourplatform.com blog.yourplatform.com; do
    echo "Checking $domain"
    echo | openssl s_client -servername $domain -connect $domain:443 2>/dev/null | openssl x509 -noout -dates
done

# Generate performance report
python scripts/generate_performance_report.py
```

#### Monthly Tasks
```bash
#!/bin/bash
# monthly-maintenance.sh

# Full database backup
pg_dump -h localhost -U reddit_user reddit_platform | gzip > /backups/monthly/reddit_platform_$(date +%Y%m).sql.gz

# Vacuum database
docker-compose exec postgres psql -U reddit_user -d reddit_platform -c "VACUUM FULL;"

# Update Docker images
docker-compose pull
docker-compose up -d

# Security updates
sudo apt update && sudo apt upgrade -y

# Review and rotate logs
logrotate -f /etc/logrotate.d/reddit-platform
```

### Update Procedures

#### Application Updates
```bash
# 1. Backup current version
cp -r /opt/reddit-platform /opt/reddit-platform.backup.$(date +%Y%m%d)

# 2. Pull latest code
cd /opt/reddit-platform
git fetch origin
git checkout main
git pull origin main

# 3. Update dependencies
pip install -r requirements.txt

# 4. Run migrations
alembic upgrade head

# 5. Restart services
docker-compose down
docker-compose up -d --build

# 6. Verify deployment
curl http://localhost:8000/health
```

#### Database Updates
```bash
# 1. Backup database
pg_dump reddit_platform > backup_before_update.sql

# 2. Test migration on copy
createdb reddit_platform_test
psql reddit_platform_test < backup_before_update.sql
alembic upgrade head

# 3. Apply to production
alembic upgrade head

# 4. Verify migration
python scripts/verify_migration.py
```

### Monitoring and Alerting

#### Health Check Script
```python
#!/usr/bin/env python3
# scripts/health_check.py

import requests
import sys
import json
from datetime import datetime

def check_api_health():
    try:
        response = requests.get('http://localhost:8000/health', timeout=10)
        return response.status_code == 200
    except:
        return False

def check_database():
    # Add database connectivity check
    pass

def check_redis():
    # Add Redis connectivity check
    pass

def main():
    checks = {
        'api': check_api_health(),
        'database': check_database(),
        'redis': check_redis(),
        'timestamp': datetime.utcnow().isoformat()
    }
    
    if all(checks.values()):
        print(json.dumps(checks))
        sys.exit(0)
    else:
        print(json.dumps(checks))
        sys.exit(1)

if __name__ == '__main__':
    main()
```

#### Alert Configuration
```yaml
# monitoring/alert_rules.yml
groups:
  - name: reddit-platform
    rules:
      - alert: APIDown
        expr: up{job="reddit-platform-api"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Reddit Platform API is down"
          
      - alert: HighResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High API response time"
          
      - alert: DatabaseConnections
        expr: pg_stat_activity_count > 80
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High database connection count"
```

---

**Document Version**: 1.0.0  
**Last Updated**: 2025-08-03  
**Maintained By**: Platform Engineering Team  
**Review Schedule**: Monthly

For additional support or questions about deployment, please refer to the troubleshooting section or contact the development team.