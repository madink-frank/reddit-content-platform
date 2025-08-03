#!/bin/bash

# Railway.com deployment setup script
# This script helps configure environment variables for Railway deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Function to check if Railway CLI is installed
check_railway_cli() {
    if ! command -v railway &> /dev/null; then
        print_error "Railway CLI is not installed."
        print_info "Install it from: https://docs.railway.app/develop/cli"
        print_info "Or run: npm install -g @railway/cli"
        exit 1
    fi
}

# Function to login to Railway
railway_login() {
    print_status "Checking Railway authentication..."
    if ! railway whoami &> /dev/null; then
        print_warning "Not logged in to Railway. Please login first."
        railway login
    else
        print_status "Already logged in to Railway."
    fi
}

# Function to create or select project
setup_project() {
    print_status "Setting up Railway project..."
    
    # Check if already linked to a project
    if railway status &> /dev/null; then
        print_status "Already linked to a Railway project."
        railway status
    else
        print_warning "Not linked to a Railway project."
        echo "Would you like to:"
        echo "1. Create a new project"
        echo "2. Link to existing project"
        read -p "Enter choice (1 or 2): " choice
        
        case $choice in
            1)
                read -p "Enter project name: " project_name
                railway init "$project_name"
                ;;
            2)
                railway link
                ;;
            *)
                print_error "Invalid choice"
                exit 1
                ;;
        esac
    fi
}

# Function to set environment variables
set_environment_variables() {
    print_status "Setting up environment variables..."
    
    # Check if .env file exists for reference
    if [ -f ".env" ]; then
        print_info "Found .env file. Using it as reference for environment variables."
        source .env
    fi
    
    # Set basic application variables
    print_status "Setting application variables..."
    railway variables set ENVIRONMENT=production
    railway variables set API_V1_STR=/api/v1
    railway variables set PROJECT_NAME="Reddit Content Platform"
    railway variables set VERSION=1.0.0
    
    # JWT Configuration
    if [ -z "$JWT_SECRET_KEY" ]; then
        JWT_SECRET_KEY=$(openssl rand -base64 32)
        print_warning "Generated new JWT_SECRET_KEY. Store it securely!"
    fi
    railway variables set JWT_SECRET_KEY="$JWT_SECRET_KEY"
    railway variables set JWT_ALGORITHM=HS256
    railway variables set JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
    railway variables set JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
    
    # Reddit API Configuration
    if [ -z "$REDDIT_CLIENT_ID" ]; then
        read -p "Enter Reddit Client ID: " REDDIT_CLIENT_ID
    fi
    if [ -z "$REDDIT_CLIENT_SECRET" ]; then
        read -s -p "Enter Reddit Client Secret: " REDDIT_CLIENT_SECRET
        echo
    fi
    
    railway variables set REDDIT_CLIENT_ID="$REDDIT_CLIENT_ID"
    railway variables set REDDIT_CLIENT_SECRET="$REDDIT_CLIENT_SECRET"
    
    # Get Railway domain for redirect URI
    print_status "Getting Railway domain..."
    RAILWAY_DOMAIN=$(railway domain | grep -o 'https://[^[:space:]]*' | head -1)
    if [ -n "$RAILWAY_DOMAIN" ]; then
        railway variables set REDDIT_REDIRECT_URI="${RAILWAY_DOMAIN}/api/v1/auth/callback"
        print_status "Set Reddit redirect URI to: ${RAILWAY_DOMAIN}/api/v1/auth/callback"
    else
        print_warning "Could not determine Railway domain. Set REDDIT_REDIRECT_URI manually later."
    fi
    
    # CORS Configuration
    if [ -n "$RAILWAY_DOMAIN" ]; then
        railway variables set BACKEND_CORS_ORIGINS="[\"$RAILWAY_DOMAIN\"]"
    else
        railway variables set BACKEND_CORS_ORIGINS="[\"*\"]"
        print_warning "Using wildcard CORS. Update this in production!"
    fi
    
    # Monitoring
    railway variables set PROMETHEUS_ENABLED=true
    
    print_status "Environment variables set successfully!"
}

# Function to add database services
add_database_services() {
    print_status "Adding database services..."
    
    # Add PostgreSQL
    print_status "Adding PostgreSQL database..."
    railway add postgresql
    
    # Add Redis
    print_status "Adding Redis cache..."
    railway add redis
    
    print_status "Database services added. Railway will automatically set DATABASE_URL and REDIS_URL."
}

# Function to deploy the application
deploy_application() {
    print_status "Deploying application..."
    
    # Deploy the main application
    railway up
    
    print_status "Deployment initiated. Check Railway dashboard for progress."
}

# Function to run database migrations
run_migrations() {
    print_status "Running database migrations..."
    
    # Wait for deployment to complete
    print_info "Waiting for deployment to complete..."
    sleep 30
    
    # Run migrations
    railway run alembic upgrade head
    
    print_status "Database migrations completed."
}

# Function to show deployment status
show_status() {
    print_status "Deployment Status:"
    railway status
    
    print_status "Services:"
    railway ps
    
    print_status "Environment Variables:"
    railway variables
    
    # Get the application URL
    RAILWAY_DOMAIN=$(railway domain | grep -o 'https://[^[:space:]]*' | head -1)
    if [ -n "$RAILWAY_DOMAIN" ]; then
        print_status "Application URL: $RAILWAY_DOMAIN"
        print_status "API Documentation: $RAILWAY_DOMAIN/docs"
        print_status "Health Check: $RAILWAY_DOMAIN/health"
    fi
}

# Function to show help
show_help() {
    echo "Railway.com Deployment Setup Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  setup       Complete setup (login, project, variables, databases, deploy)"
    echo "  login       Login to Railway"
    echo "  project     Setup Railway project"
    echo "  variables   Set environment variables"
    echo "  databases   Add database services"
    echo "  deploy      Deploy application"
    echo "  migrate     Run database migrations"
    echo "  status      Show deployment status"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 setup      # Complete setup"
    echo "  $0 variables  # Only set environment variables"
    echo "  $0 status     # Check deployment status"
}

# Main script logic
case "$1" in
    setup)
        check_railway_cli
        railway_login
        setup_project
        set_environment_variables
        add_database_services
        deploy_application
        run_migrations
        show_status
        ;;
    login)
        check_railway_cli
        railway_login
        ;;
    project)
        check_railway_cli
        setup_project
        ;;
    variables)
        check_railway_cli
        set_environment_variables
        ;;
    databases)
        check_railway_cli
        add_database_services
        ;;
    deploy)
        check_railway_cli
        deploy_application
        ;;
    migrate)
        check_railway_cli
        run_migrations
        ;;
    status)
        check_railway_cli
        show_status
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        if [ -z "$1" ]; then
            show_help
        else
            print_error "Unknown command: $1"
            show_help
            exit 1
        fi
        ;;
esac