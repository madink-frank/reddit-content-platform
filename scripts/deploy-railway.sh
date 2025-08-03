#!/bin/bash

# Railway deployment script for Reddit Content Platform
# Usage: ./scripts/deploy-railway.sh [environment] [service]
# Example: ./scripts/deploy-railway.sh production api

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ENVIRONMENT="${1:-staging}"
SERVICE="${2:-api}"

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

# Check if Railway CLI is installed
check_railway_cli() {
    if ! command -v railway &> /dev/null; then
        log_error "Railway CLI is not installed"
        log_info "Install it with: npm install -g @railway/cli"
        log_info "Or visit: https://docs.railway.app/develop/cli"
        exit 1
    fi
    
    # Check if logged in
    if ! railway whoami &> /dev/null; then
        log_error "Not logged in to Railway"
        log_info "Login with: railway login"
        exit 1
    fi
    
    log_success "Railway CLI is ready"
}

# Set Railway project and environment
set_railway_context() {
    log_info "Setting Railway context..."
    
    # Link to project if not already linked
    if [[ ! -f "$PROJECT_ROOT/.railway/project.json" ]]; then
        log_warning "Project not linked to Railway"
        log_info "Please run 'railway link' first"
        exit 1
    fi
    
    # Set environment
    case "$ENVIRONMENT" in
        staging)
            railway environment staging || {
                log_error "Failed to switch to staging environment"
                exit 1
            }
            ;;
        production)
            railway environment production || {
                log_error "Failed to switch to production environment"
                exit 1
            }
            ;;
        *)
            log_error "Invalid environment: $ENVIRONMENT"
            log_error "Valid environments: staging, production"
            exit 1
            ;;
    esac
    
    log_success "Railway context set to $ENVIRONMENT"
}

# Deploy backend API
deploy_api() {
    log_info "Deploying API service to Railway..."
    
    cd "$PROJECT_ROOT"
    
    # Set environment variables for Railway
    log_info "Setting environment variables..."
    
    # Database URL (Railway provides this automatically)
    # railway variables set DATABASE_URL="$DATABASE_URL"
    
    # Redis URL (Railway provides this automatically)
    # railway variables set REDIS_URL="$REDIS_URL"
    
    # Application-specific variables
    railway variables set ENVIRONMENT="$ENVIRONMENT"
    railway variables set LOG_LEVEL="${LOG_LEVEL:-INFO}"
    railway variables set PYTHONPATH="/app"
    
    # Reddit API credentials (should be set manually in Railway dashboard)
    if [[ -n "${REDDIT_CLIENT_ID:-}" ]]; then
        railway variables set REDDIT_CLIENT_ID="$REDDIT_CLIENT_ID"
    fi
    
    if [[ -n "${REDDIT_CLIENT_SECRET:-}" ]]; then
        railway variables set REDDIT_CLIENT_SECRET="$REDDIT_CLIENT_SECRET"
    fi
    
    # JWT secret (should be set manually in Railway dashboard)
    if [[ -n "${JWT_SECRET_KEY:-}" ]]; then
        railway variables set JWT_SECRET_KEY="$JWT_SECRET_KEY"
    fi
    
    # Deploy using Railway
    log_info "Starting Railway deployment..."
    railway up --detach || {
        log_error "Railway deployment failed"
        exit 1
    }
    
    log_success "API deployment initiated"
}

# Deploy frontend to Railway (if using Railway for frontend)
deploy_frontend() {
    log_info "Building and deploying frontend..."
    
    cd "$PROJECT_ROOT/admin-dashboard"
    
    # Install dependencies
    log_info "Installing frontend dependencies..."
    npm ci
    
    # Build frontend
    log_info "Building frontend..."
    npm run build
    
    # Deploy to Railway (if configured for frontend)
    # This would require a separate Railway service for the frontend
    log_info "Frontend build completed"
    log_warning "Frontend deployment to Railway requires separate service configuration"
    
    log_success "Frontend ready for deployment"
}

# Run database migrations
run_migrations() {
    log_info "Running database migrations..."
    
    cd "$PROJECT_ROOT"
    
    # Run migrations using Railway CLI
    railway run alembic upgrade head || {
        log_error "Database migration failed"
        exit 1
    }
    
    log_success "Database migrations completed"
}

# Health check
health_check() {
    log_info "Performing health check..."
    
    # Get the Railway service URL
    local service_url
    service_url=$(railway status --json | jq -r '.deployments[0].url' 2>/dev/null || echo "")
    
    if [[ -z "$service_url" || "$service_url" == "null" ]]; then
        log_warning "Could not determine service URL, skipping health check"
        return 0
    fi
    
    local health_url="${service_url}/health"
    local max_attempts=30
    local attempt=1
    
    log_info "Checking health at: $health_url"
    
    while [[ $attempt -le $max_attempts ]]; do
        if curl -f -s "$health_url" > /dev/null 2>&1; then
            log_success "Health check passed"
            log_info "Service is available at: $service_url"
            log_info "API documentation: ${service_url}/docs"
            return 0
        fi
        
        log_info "Health check attempt $attempt/$max_attempts failed, retrying in 10 seconds..."
        sleep 10
        ((attempt++))
    done
    
    log_error "Health check failed after $max_attempts attempts"
    return 1
}

# Show deployment status
show_status() {
    log_info "Deployment status:"
    railway status
    
    log_info "Recent logs:"
    railway logs --tail 20
}

# Main deployment function
main() {
    log_info "Starting Railway deployment of Reddit Content Platform"
    log_info "Environment: $ENVIRONMENT"
    log_info "Service: $SERVICE"
    
    check_railway_cli
    set_railway_context
    
    case "$SERVICE" in
        api|backend)
            deploy_api
            run_migrations
            ;;
        frontend)
            deploy_frontend
            ;;
        all)
            deploy_api
            run_migrations
            deploy_frontend
            ;;
        *)
            log_error "Invalid service: $SERVICE"
            log_error "Valid services: api, frontend, all"
            exit 1
            ;;
    esac
    
    # Perform health check for API deployments
    if [[ "$SERVICE" == "api" || "$SERVICE" == "backend" || "$SERVICE" == "all" ]]; then
        if ! health_check; then
            log_error "Deployment failed health check"
            show_status
            exit 1
        fi
    fi
    
    show_status
    
    log_success "Railway deployment completed successfully!"
}

# Script execution
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi