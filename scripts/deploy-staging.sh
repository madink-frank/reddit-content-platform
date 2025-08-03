#!/bin/bash

# Staging deployment script
# This script deploys the application to staging environment

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

# Configuration
COMPOSE_FILE="docker-compose.staging.yml"
ENV_FILE=".env.staging"

# Check prerequisites
check_prerequisites() {
    # Check Docker
    if ! docker info >/dev/null 2>&1; then
        error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    
    # Check docker-compose
    if command -v docker-compose >/dev/null 2>&1; then
        DOCKER_COMPOSE="docker-compose"
    elif docker compose version >/dev/null 2>&1; then
        DOCKER_COMPOSE="docker compose"
    else
        error "Neither docker-compose nor 'docker compose' is available"
        exit 1
    fi
    
    # Check environment file
    if [ ! -f "$ENV_FILE" ]; then
        error "Environment file $ENV_FILE not found"
        error "Please create $ENV_FILE with staging configuration"
        exit 1
    fi
    
    log "Prerequisites check passed"
}

# Validate environment variables
validate_env() {
    log "Validating environment variables..."
    
    # Load environment variables
    export $(cat $ENV_FILE | grep -v '^#' | xargs)
    
    # Required variables
    local required_vars=(
        "DATABASE_URL"
        "REDIS_URL"
        "REDDIT_CLIENT_ID"
        "REDDIT_CLIENT_SECRET"
        "JWT_SECRET_KEY"
    )
    
    local missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -ne 0 ]; then
        error "Missing required environment variables:"
        for var in "${missing_vars[@]}"; do
            error "  - $var"
        done
        exit 1
    fi
    
    # Validate JWT secret is not default
    if [[ "$JWT_SECRET_KEY" == *"staging-jwt-secret"* ]]; then
        error "JWT_SECRET_KEY appears to be a default value. Please set a secure secret."
        exit 1
    fi
    
    log "Environment validation passed"
}

# Pre-deployment checks
pre_deployment_checks() {
    log "Running pre-deployment checks..."
    
    # Check if staging services are already running
    if $DOCKER_COMPOSE -f $COMPOSE_FILE ps | grep -q "Up"; then
        warn "Staging services are already running"
        info "Use --force to force redeploy"
        if [ "$1" != "--force" ]; then
            exit 1
        fi
    fi
    
    # Test database connectivity (if possible)
    if command -v psql >/dev/null 2>&1 && [[ "$DATABASE_URL" == postgresql* ]]; then
        info "Testing database connectivity..."
        if ! psql "$DATABASE_URL" -c "SELECT 1;" >/dev/null 2>&1; then
            warn "Cannot connect to database. Deployment will continue but may fail."
        else
            log "Database connectivity test passed"
        fi
    fi
}

# Build and deploy
deploy() {
    log "Starting staging deployment..."
    
    # Pull latest images
    log "Pulling latest base images..."
    docker pull python:3.12-slim
    docker pull postgres:15-alpine
    docker pull redis:7-alpine
    docker pull nginx:alpine
    
    # Build application images
    log "Building application images..."
    $DOCKER_COMPOSE -f $COMPOSE_FILE build --no-cache --pull
    
    # Stop existing services
    log "Stopping existing services..."
    $DOCKER_COMPOSE -f $COMPOSE_FILE down --remove-orphans
    
    # Start services
    log "Starting staging services..."
    $DOCKER_COMPOSE -f $COMPOSE_FILE up -d
    
    log "Deployment initiated"
}

# Wait for services to be healthy
wait_for_health() {
    log "Waiting for services to be healthy..."
    
    local max_attempts=60
    local attempt=1
    local healthy_services=0
    local total_services
    
    while [ $attempt -le $max_attempts ]; do
        healthy_services=0
        total_services=0
        
        # Count healthy services
        while IFS= read -r line; do
            if [[ $line == *"healthy"* ]]; then
                healthy_services=$((healthy_services + 1))
            fi
            if [[ $line == *"Up"* ]]; then
                total_services=$((total_services + 1))
            fi
        done < <($DOCKER_COMPOSE -f $COMPOSE_FILE ps)
        
        if [ $healthy_services -eq $total_services ] && [ $total_services -gt 0 ]; then
            log "All services are healthy ($healthy_services/$total_services)"
            return 0
        fi
        
        info "Attempt $attempt/$max_attempts - $healthy_services/$total_services services healthy"
        sleep 10
        attempt=$((attempt + 1))
    done
    
    error "Services did not become healthy within expected time"
    return 1
}

# Run database migrations
run_migrations() {
    log "Running database migrations..."
    
    # Wait a bit more for database to be fully ready
    sleep 10
    
    if $DOCKER_COMPOSE -f $COMPOSE_FILE exec -T api alembic upgrade head; then
        log "Database migrations completed successfully"
    else
        error "Database migrations failed"
        return 1
    fi
}

# Post-deployment verification
verify_deployment() {
    log "Verifying deployment..."
    
    # Check API health endpoint
    local api_url="http://localhost:8000/health"
    local max_attempts=10
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s --max-time 10 "$api_url" >/dev/null 2>&1; then
            log "API health check passed"
            break
        fi
        
        if [ $attempt -eq $max_attempts ]; then
            error "API health check failed after $max_attempts attempts"
            return 1
        fi
        
        info "API health check attempt $attempt/$max_attempts failed, retrying..."
        sleep 5
        attempt=$((attempt + 1))
    done
    
    # Check service status
    log "Final service status:"
    $DOCKER_COMPOSE -f $COMPOSE_FILE ps
    
    return 0
}

# Show deployment info
show_deployment_info() {
    log "Staging deployment completed successfully!"
    echo ""
    log "Service URLs:"
    echo "  API: http://localhost:8000"
    echo "  API Docs: http://localhost:8000/docs"
    echo "  Health Check: http://localhost:8000/health"
    echo ""
    log "Management commands:"
    echo "  View logs: $DOCKER_COMPOSE -f $COMPOSE_FILE logs -f [service_name]"
    echo "  Stop services: $DOCKER_COMPOSE -f $COMPOSE_FILE down"
    echo "  Restart service: $DOCKER_COMPOSE -f $COMPOSE_FILE restart [service_name]"
    echo ""
    log "Monitoring:"
    echo "  Check service status: $DOCKER_COMPOSE -f $COMPOSE_FILE ps"
    echo "  View resource usage: docker stats"
}

# Rollback function
rollback() {
    error "Deployment failed. Initiating rollback..."
    
    $DOCKER_COMPOSE -f $COMPOSE_FILE down
    
    # Try to start previous version if available
    if docker images | grep -q "reddit-content-platform.*previous"; then
        warn "Starting previous version..."
        # Implementation would depend on your tagging strategy
    fi
    
    error "Rollback completed. Please check the logs and fix issues before redeploying."
}

# Main deployment function
main() {
    local force_deploy=false
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --force)
                force_deploy=true
                shift
                ;;
            --help|-h)
                echo "Usage: $0 [--force] [--help]"
                echo ""
                echo "Options:"
                echo "  --force    Force redeploy even if services are running"
                echo "  --help     Show this help message"
                exit 0
                ;;
            *)
                error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    log "Starting staging deployment process..."
    
    # Run deployment steps
    check_prerequisites
    validate_env
    
    if [ "$force_deploy" = true ]; then
        pre_deployment_checks --force
    else
        pre_deployment_checks
    fi
    
    deploy
    
    if wait_for_health; then
        if run_migrations && verify_deployment; then
            show_deployment_info
        else
            rollback
            exit 1
        fi
    else
        error "Deployment failed - services are not healthy"
        $DOCKER_COMPOSE -f $COMPOSE_FILE logs
        rollback
        exit 1
    fi
}

# Run main function
main "$@"