#!/bin/bash

# Development deployment script
# This script sets up and runs the development environment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

# Check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    log "Docker is running"
}

# Check if docker-compose is available
check_docker_compose() {
    if command -v docker-compose >/dev/null 2>&1; then
        DOCKER_COMPOSE="docker-compose"
    elif docker compose version >/dev/null 2>&1; then
        DOCKER_COMPOSE="docker compose"
    else
        error "Neither docker-compose nor 'docker compose' is available"
        exit 1
    fi
    log "Using: $DOCKER_COMPOSE"
}

# Load environment variables
load_env() {
    if [ -f .env.dev ]; then
        log "Loading development environment variables from .env.dev"
        export $(cat .env.dev | grep -v '^#' | xargs)
    else
        warn ".env.dev file not found, using default values"
    fi
}

# Clean up existing containers
cleanup() {
    log "Cleaning up existing containers..."
    $DOCKER_COMPOSE -f docker-compose.dev.yml down --remove-orphans
    
    # Remove dangling images
    if [ "$(docker images -f 'dangling=true' -q)" ]; then
        log "Removing dangling images..."
        docker rmi $(docker images -f 'dangling=true' -q) || true
    fi
}

# Build and start services
start_services() {
    log "Building and starting development services..."
    
    # Build images
    $DOCKER_COMPOSE -f docker-compose.dev.yml build --no-cache
    
    # Start services
    $DOCKER_COMPOSE -f docker-compose.dev.yml up -d
    
    log "Services started successfully"
}

# Wait for services to be healthy
wait_for_services() {
    log "Waiting for services to be healthy..."
    
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if $DOCKER_COMPOSE -f docker-compose.dev.yml ps | grep -q "healthy"; then
            log "Services are healthy"
            return 0
        fi
        
        info "Attempt $attempt/$max_attempts - waiting for services..."
        sleep 10
        attempt=$((attempt + 1))
    done
    
    error "Services did not become healthy within expected time"
    return 1
}

# Run database migrations
run_migrations() {
    log "Running database migrations..."
    
    $DOCKER_COMPOSE -f docker-compose.dev.yml exec -T api alembic upgrade head
    
    if [ $? -eq 0 ]; then
        log "Database migrations completed successfully"
    else
        error "Database migrations failed"
        return 1
    fi
}

# Show service status
show_status() {
    log "Service status:"
    $DOCKER_COMPOSE -f docker-compose.dev.yml ps
    
    echo ""
    log "Service URLs:"
    echo "  API: http://localhost:8000"
    echo "  API Docs: http://localhost:8000/docs"
    echo "  Database: localhost:5432"
    echo "  Redis: localhost:6379"
    echo "  Prometheus: http://localhost:9090 (if monitoring profile is enabled)"
    echo "  Grafana: http://localhost:3000 (if monitoring profile is enabled)"
    echo ""
    log "To view logs: $DOCKER_COMPOSE -f docker-compose.dev.yml logs -f [service_name]"
    log "To stop services: $DOCKER_COMPOSE -f docker-compose.dev.yml down"
}

# Main deployment function
main() {
    log "Starting development deployment..."
    
    check_docker
    check_docker_compose
    load_env
    
    if [ "$1" = "--clean" ]; then
        cleanup
    fi
    
    start_services
    
    if wait_for_services; then
        run_migrations
        show_status
        log "Development environment is ready!"
    else
        error "Deployment failed - services are not healthy"
        $DOCKER_COMPOSE -f docker-compose.dev.yml logs
        exit 1
    fi
}

# Handle script arguments
case "$1" in
    --help|-h)
        echo "Usage: $0 [--clean] [--help]"
        echo ""
        echo "Options:"
        echo "  --clean    Clean up existing containers before starting"
        echo "  --help     Show this help message"
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac