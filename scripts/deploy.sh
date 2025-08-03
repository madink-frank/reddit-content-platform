#!/bin/bash

# Deployment automation script for Reddit Content Platform
# Usage: ./scripts/deploy.sh [environment] [version]
# Example: ./scripts/deploy.sh staging v1.0.0

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ENVIRONMENT="${1:-staging}"
VERSION="${2:-latest}"
REGISTRY="ghcr.io"
IMAGE_NAME="reddit-content-platform"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Validate environment
validate_environment() {
    case "$ENVIRONMENT" in
        development|staging|production)
            log_info "Deploying to $ENVIRONMENT environment"
            ;;
        *)
            log_error "Invalid environment: $ENVIRONMENT"
            log_error "Valid environments: development, staging, production"
            exit 1
            ;;
    esac
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if Docker is installed and running
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running"
        exit 1
    fi
    
    # Check if docker-compose is available
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi
    
    # Set compose command
    if docker compose version &> /dev/null; then
        COMPOSE_CMD="docker compose"
    else
        COMPOSE_CMD="docker-compose"
    fi
    
    log_success "Prerequisites check passed"
}

# Load environment configuration
load_environment_config() {
    local env_file="$PROJECT_ROOT/.env.$ENVIRONMENT"
    
    if [[ -f "$env_file" ]]; then
        log_info "Loading environment configuration from $env_file"
        set -a
        source "$env_file"
        set +a
    else
        log_warning "Environment file $env_file not found, using defaults"
    fi
    
    # Set default values if not provided
    export DATABASE_URL="${DATABASE_URL:-postgresql://reddit_user:reddit_pass@db:5432/reddit_platform}"
    export REDIS_URL="${REDIS_URL:-redis://redis:6379}"
    export CELERY_BROKER_URL="${CELERY_BROKER_URL:-redis://redis:6379/0}"
    export CELERY_RESULT_BACKEND="${CELERY_RESULT_BACKEND:-redis://redis:6379/0}"
    export JWT_SECRET_KEY="${JWT_SECRET_KEY:-change-this-in-production}"
    export ENVIRONMENT="${ENVIRONMENT}"
    export LOG_LEVEL="${LOG_LEVEL:-INFO}"
}

# Pull latest images
pull_images() {
    log_info "Pulling latest Docker images..."
    
    local image_tag="${REGISTRY}/${IMAGE_NAME}:${VERSION}"
    
    if [[ "$VERSION" != "latest" ]]; then
        log_info "Pulling specific version: $image_tag"
        docker pull "$image_tag" || {
            log_error "Failed to pull image $image_tag"
            exit 1
        }
    fi
    
    log_success "Images pulled successfully"
}

# Run database migrations
run_migrations() {
    log_info "Running database migrations..."
    
    local compose_file="docker-compose.$ENVIRONMENT.yml"
    if [[ ! -f "$PROJECT_ROOT/$compose_file" ]]; then
        compose_file="docker-compose.yml"
    fi
    
    cd "$PROJECT_ROOT"
    
    # Start database service
    $COMPOSE_CMD -f "$compose_file" up -d db redis
    
    # Wait for database to be ready
    log_info "Waiting for database to be ready..."
    sleep 10
    
    # Run migrations
    $COMPOSE_CMD -f "$compose_file" run --rm api alembic upgrade head || {
        log_error "Database migration failed"
        exit 1
    }
    
    log_success "Database migrations completed"
}

# Deploy services
deploy_services() {
    log_info "Deploying services..."
    
    local compose_file="docker-compose.$ENVIRONMENT.yml"
    if [[ ! -f "$PROJECT_ROOT/$compose_file" ]]; then
        compose_file="docker-compose.yml"
    fi
    
    cd "$PROJECT_ROOT"
    
    # Stop existing services
    log_info "Stopping existing services..."
    $COMPOSE_CMD -f "$compose_file" down || true
    
    # Start services
    log_info "Starting services..."
    $COMPOSE_CMD -f "$compose_file" up -d
    
    log_success "Services deployed successfully"
}

# Health check
health_check() {
    log_info "Performing health check..."
    
    local max_attempts=30
    local attempt=1
    local health_url="http://localhost:8000/health"
    
    while [[ $attempt -le $max_attempts ]]; do
        if curl -f -s "$health_url" > /dev/null 2>&1; then
            log_success "Health check passed"
            return 0
        fi
        
        log_info "Health check attempt $attempt/$max_attempts failed, retrying in 10 seconds..."
        sleep 10
        ((attempt++))
    done
    
    log_error "Health check failed after $max_attempts attempts"
    return 1
}

# Rollback function
rollback() {
    log_warning "Rolling back deployment..."
    
    local compose_file="docker-compose.$ENVIRONMENT.yml"
    if [[ ! -f "$PROJECT_ROOT/$compose_file" ]]; then
        compose_file="docker-compose.yml"
    fi
    
    cd "$PROJECT_ROOT"
    
    # Stop current services
    $COMPOSE_CMD -f "$compose_file" down
    
    # Start with previous version (assuming 'previous' tag exists)
    export IMAGE_TAG="previous"
    $COMPOSE_CMD -f "$compose_file" up -d
    
    log_warning "Rollback completed"
}

# Cleanup old images
cleanup() {
    log_info "Cleaning up old Docker images..."
    
    # Remove dangling images
    docker image prune -f
    
    # Remove old versions (keep last 3)
    docker images "${REGISTRY}/${IMAGE_NAME}" --format "table {{.Tag}}\t{{.ID}}" | \
        tail -n +2 | sort -V | head -n -3 | awk '{print $2}' | \
        xargs -r docker rmi || true
    
    log_success "Cleanup completed"
}

# Main deployment function
main() {
    log_info "Starting deployment of Reddit Content Platform"
    log_info "Environment: $ENVIRONMENT"
    log_info "Version: $VERSION"
    
    validate_environment
    check_prerequisites
    load_environment_config
    
    # Set trap for cleanup on failure
    trap 'log_error "Deployment failed"; rollback; exit 1' ERR
    
    pull_images
    run_migrations
    deploy_services
    
    # Perform health check
    if ! health_check; then
        log_error "Deployment failed health check"
        rollback
        exit 1
    fi
    
    cleanup
    
    log_success "Deployment completed successfully!"
    log_info "Application is running at: http://localhost:8000"
    log_info "API documentation: http://localhost:8000/docs"
    log_info "Admin dashboard: http://localhost:3000"
    
    # Show running services
    log_info "Running services:"
    cd "$PROJECT_ROOT"
    local compose_file="docker-compose.$ENVIRONMENT.yml"
    if [[ ! -f "$compose_file" ]]; then
        compose_file="docker-compose.yml"
    fi
    $COMPOSE_CMD -f "$compose_file" ps
}

# Script execution
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi