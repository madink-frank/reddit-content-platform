#!/bin/bash

# Docker health check script for the FastAPI application
# This script performs comprehensive health checks for all services

set -e

# Configuration
API_HOST=${API_HOST:-localhost}
API_PORT=${API_PORT:-8000}
REDIS_HOST=${REDIS_HOST:-localhost}
REDIS_PORT=${REDIS_PORT:-6379}
DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-5432}
TIMEOUT=${TIMEOUT:-10}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

# Check if a service is reachable
check_service() {
    local host=$1
    local port=$2
    local service_name=$3
    
    if timeout $TIMEOUT bash -c "cat < /dev/null > /dev/tcp/$host/$port" 2>/dev/null; then
        log "$service_name is reachable at $host:$port"
        return 0
    else
        error "$service_name is not reachable at $host:$port"
        return 1
    fi
}

# Check API health endpoint
check_api_health() {
    local url="http://$API_HOST:$API_PORT/health"
    
    if command -v curl >/dev/null 2>&1; then
        if curl -f -s --max-time $TIMEOUT "$url" >/dev/null; then
            log "API health check passed"
            return 0
        else
            error "API health check failed"
            return 1
        fi
    elif command -v wget >/dev/null 2>&1; then
        if wget -q --timeout=$TIMEOUT --tries=1 --spider "$url" 2>/dev/null; then
            log "API health check passed"
            return 0
        else
            error "API health check failed"
            return 1
        fi
    else
        warn "Neither curl nor wget available, skipping API health check"
        return 0
    fi
}

# Check Redis connectivity
check_redis() {
    if command -v redis-cli >/dev/null 2>&1; then
        if redis-cli -h $REDIS_HOST -p $REDIS_PORT --connect-timeout $TIMEOUT ping >/dev/null 2>&1; then
            log "Redis connectivity check passed"
            return 0
        else
            error "Redis connectivity check failed"
            return 1
        fi
    else
        warn "redis-cli not available, using basic connectivity check"
        check_service $REDIS_HOST $REDIS_PORT "Redis"
    fi
}

# Check PostgreSQL connectivity
check_postgres() {
    if command -v pg_isready >/dev/null 2>&1; then
        if pg_isready -h $DB_HOST -p $DB_PORT -t $TIMEOUT >/dev/null 2>&1; then
            log "PostgreSQL connectivity check passed"
            return 0
        else
            error "PostgreSQL connectivity check failed"
            return 1
        fi
    else
        warn "pg_isready not available, using basic connectivity check"
        check_service $DB_HOST $DB_PORT "PostgreSQL"
    fi
}

# Check Celery worker
check_celery() {
    if command -v celery >/dev/null 2>&1; then
        if celery -A app.core.celery_app inspect ping --timeout=$TIMEOUT >/dev/null 2>&1; then
            log "Celery worker check passed"
            return 0
        else
            error "Celery worker check failed"
            return 1
        fi
    else
        warn "Celery not available, skipping worker check"
        return 0
    fi
}

# Main health check function
main() {
    log "Starting comprehensive health check..."
    
    local exit_code=0
    
    # Check API health
    if ! check_api_health; then
        exit_code=1
    fi
    
    # Check Redis (if not using SQLite)
    if [[ "$DATABASE_URL" != *"sqlite"* ]]; then
        if ! check_redis; then
            exit_code=1
        fi
    fi
    
    # Check PostgreSQL (if using PostgreSQL)
    if [[ "$DATABASE_URL" == *"postgresql"* ]]; then
        if ! check_postgres; then
            exit_code=1
        fi
    fi
    
    # Check Celery (if in worker mode)
    if [[ "$CHECK_CELERY" == "true" ]]; then
        if ! check_celery; then
            exit_code=1
        fi
    fi
    
    if [ $exit_code -eq 0 ]; then
        log "All health checks passed"
    else
        error "Some health checks failed"
    fi
    
    exit $exit_code
}

# Run main function
main "$@"