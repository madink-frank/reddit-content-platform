#!/bin/bash

# Frontend deployment script
# Usage: ./scripts/deploy-frontend.sh [app] [environment]
# Example: ./scripts/deploy-frontend.sh admin-dashboard production

set -e

# Configuration
APP=${1:-"both"}
ENVIRONMENT=${2:-"staging"}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
CONFIG_FILE="$PROJECT_ROOT/deployment-config.yml"

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

# Check dependencies
check_dependencies() {
    log_info "Checking dependencies..."
    
    local missing_deps=()
    
    if ! command -v node &> /dev/null; then
        missing_deps+=("node")
    fi
    
    if ! command -v npm &> /dev/null; then
        missing_deps+=("npm")
    fi
    
    if ! command -v yq &> /dev/null; then
        log_warning "yq not found. Installing..."
        if [[ "$OSTYPE" == "darwin"* ]]; then
            brew install yq
        elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
            sudo wget -qO /usr/local/bin/yq https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64
            sudo chmod +x /usr/local/bin/yq
        fi
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        log_error "Missing dependencies: ${missing_deps[*]}"
        exit 1
    fi
    
    log_success "All dependencies are available"
}

# Load configuration
load_config() {
    log_info "Loading configuration for $ENVIRONMENT environment..."
    
    if [ ! -f "$CONFIG_FILE" ]; then
        log_error "Configuration file not found: $CONFIG_FILE"
        exit 1
    fi
    
    # Export configuration variables
    export BUILD_COMMAND_ADMIN=$(yq eval ".environments.$ENVIRONMENT.admin_dashboard.build_command" "$CONFIG_FILE")
    export BUILD_COMMAND_BLOG=$(yq eval ".environments.$ENVIRONMENT.blog_site.build_command" "$CONFIG_FILE")
    export BASE_URL_ADMIN=$(yq eval ".environments.$ENVIRONMENT.admin_dashboard.base_url" "$CONFIG_FILE")
    export BASE_URL_BLOG=$(yq eval ".environments.$ENVIRONMENT.blog_site.base_url" "$CONFIG_FILE")
    export API_URL_ADMIN=$(yq eval ".environments.$ENVIRONMENT.admin_dashboard.api_url" "$CONFIG_FILE")
    export API_URL_BLOG=$(yq eval ".environments.$ENVIRONMENT.blog_site.api_url" "$CONFIG_FILE")
    export CDN_ENABLED_ADMIN=$(yq eval ".environments.$ENVIRONMENT.admin_dashboard.cdn_enabled" "$CONFIG_FILE")
    export CDN_ENABLED_BLOG=$(yq eval ".environments.$ENVIRONMENT.blog_site.cdn_enabled" "$CONFIG_FILE")
    export COMPRESSION_ADMIN=$(yq eval ".environments.$ENVIRONMENT.admin_dashboard.compression" "$CONFIG_FILE")
    export COMPRESSION_BLOG=$(yq eval ".environments.$ENVIRONMENT.blog_site.compression" "$CONFIG_FILE")
    
    log_success "Configuration loaded successfully"
}

# Build application
build_app() {
    local app_name=$1
    local app_dir="$PROJECT_ROOT/$app_name"
    
    log_info "Building $app_name..."
    
    if [ ! -d "$app_dir" ]; then
        log_error "Application directory not found: $app_dir"
        return 1
    fi
    
    cd "$app_dir"
    
    # Install dependencies if node_modules doesn't exist
    if [ ! -d "node_modules" ]; then
        log_info "Installing dependencies for $app_name..."
        npm ci --prefer-offline --no-audit
    fi
    
    # Set environment variables based on app and environment
    if [ "$app_name" = "admin-dashboard" ]; then
        export VITE_API_BASE_URL="$API_URL_ADMIN"
        export VITE_NODE_ENV="$ENVIRONMENT"
        build_command="$BUILD_COMMAND_ADMIN"
    else
        export NEXT_PUBLIC_API_BASE_URL="$API_URL_BLOG"
        export NODE_ENV="$ENVIRONMENT"
        build_command="$BUILD_COMMAND_BLOG"
    fi
    
    # Run build command
    log_info "Running build command: $build_command"
    eval "$build_command"
    
    # Optimize assets if compression is enabled
    if [ "$app_name" = "admin-dashboard" ] && [ "$COMPRESSION_ADMIN" = "true" ]; then
        log_info "Optimizing assets for $app_name..."
        "$SCRIPT_DIR/optimize-assets.sh" "$app_name"
    elif [ "$app_name" = "blog-site" ] && [ "$COMPRESSION_BLOG" = "true" ]; then
        log_info "Optimizing assets for $app_name..."
        "$SCRIPT_DIR/optimize-assets.sh" "$app_name"
    fi
    
    log_success "Build completed for $app_name"
    cd "$PROJECT_ROOT"
}

# Deploy to targets
deploy_to_targets() {
    local app_name=$1
    local targets_count
    
    log_info "Deploying $app_name to configured targets..."
    
    # Get number of targets
    targets_count=$(yq eval ".environments.$ENVIRONMENT.${app_name//-/_}.targets | length" "$CONFIG_FILE")
    
    if [ "$targets_count" = "0" ] || [ "$targets_count" = "null" ]; then
        log_warning "No deployment targets configured for $app_name in $ENVIRONMENT"
        return 0
    fi
    
    # Deploy to each target
    for ((i=0; i<targets_count; i++)); do
        local target_type=$(yq eval ".environments.$ENVIRONMENT.${app_name//-/_}.targets[$i].type" "$CONFIG_FILE")
        
        case $target_type in
            "netlify")
                deploy_to_netlify "$app_name" "$i"
                ;;
            "vercel")
                deploy_to_vercel "$app_name" "$i"
                ;;
            "s3")
                deploy_to_s3 "$app_name" "$i"
                ;;
            *)
                log_warning "Unknown deployment target type: $target_type"
                ;;
        esac
    done
    
    log_success "Deployment completed for $app_name"
}

# Deploy to Netlify
deploy_to_netlify() {
    local app_name=$1
    local target_index=$2
    
    log_info "Deploying $app_name to Netlify..."
    
    local site_id=$(yq eval ".environments.$ENVIRONMENT.${app_name//-/_}.targets[$target_index].site_id" "$CONFIG_FILE")
    local build_hook=$(yq eval ".environments.$ENVIRONMENT.${app_name//-/_}.targets[$target_index].build_hook" "$CONFIG_FILE")
    
    # Replace environment variables in site_id and build_hook
    site_id=$(eval echo "$site_id")
    build_hook=$(eval echo "$build_hook")
    
    if [ "$site_id" != "null" ] && [ -n "$NETLIFY_AUTH_TOKEN" ]; then
        # Use Netlify CLI if available
        if command -v netlify &> /dev/null; then
            cd "$PROJECT_ROOT/$app_name"
            netlify deploy --prod --dir=dist --site="$site_id"
            cd "$PROJECT_ROOT"
        else
            log_warning "Netlify CLI not found. Using build hook instead."
            if [ "$build_hook" != "null" ]; then
                curl -X POST -d {} "$build_hook"
            fi
        fi
    else
        log_warning "Netlify deployment skipped: missing site_id or NETLIFY_AUTH_TOKEN"
    fi
}

# Deploy to Vercel
deploy_to_vercel() {
    local app_name=$1
    local target_index=$2
    
    log_info "Deploying $app_name to Vercel..."
    
    local project_id=$(yq eval ".environments.$ENVIRONMENT.${app_name//-/_}.targets[$target_index].project_id" "$CONFIG_FILE")
    local team_id=$(yq eval ".environments.$ENVIRONMENT.${app_name//-/_}.targets[$target_index].team_id" "$CONFIG_FILE")
    
    # Replace environment variables
    project_id=$(eval echo "$project_id")
    team_id=$(eval echo "$team_id")
    
    if [ "$project_id" != "null" ] && [ -n "$VERCEL_TOKEN" ]; then
        # Use Vercel CLI if available
        if command -v vercel &> /dev/null; then
            cd "$PROJECT_ROOT/$app_name"
            if [ "$ENVIRONMENT" = "production" ]; then
                vercel --prod --token="$VERCEL_TOKEN"
            else
                vercel --token="$VERCEL_TOKEN"
            fi
            cd "$PROJECT_ROOT"
        else
            log_warning "Vercel CLI not found. Please install it: npm i -g vercel"
        fi
    else
        log_warning "Vercel deployment skipped: missing project_id or VERCEL_TOKEN"
    fi
}

# Deploy to S3
deploy_to_s3() {
    local app_name=$1
    local target_index=$2
    
    log_info "Deploying $app_name to S3..."
    
    local bucket=$(yq eval ".environments.$ENVIRONMENT.${app_name//-/_}.targets[$target_index].bucket" "$CONFIG_FILE")
    local cloudfront_distribution=$(yq eval ".environments.$ENVIRONMENT.${app_name//-/_}.targets[$target_index].cloudfront_distribution" "$CONFIG_FILE")
    
    # Replace environment variables
    bucket=$(eval echo "$bucket")
    cloudfront_distribution=$(eval echo "$cloudfront_distribution")
    
    if [ "$bucket" != "null" ] && command -v aws &> /dev/null; then
        local dist_dir
        if [ "$app_name" = "admin-dashboard" ]; then
            dist_dir="dist"
        else
            dist_dir=".next"
        fi
        
        cd "$PROJECT_ROOT/$app_name"
        
        # Sync files to S3
        aws s3 sync "$dist_dir/" "s3://$bucket/" --delete --cache-control "public, max-age=31536000" --exclude "*.html"
        aws s3 sync "$dist_dir/" "s3://$bucket/" --cache-control "public, max-age=3600" --include "*.html"
        
        # Invalidate CloudFront cache if distribution is configured
        if [ "$cloudfront_distribution" != "null" ]; then
            aws cloudfront create-invalidation --distribution-id "$cloudfront_distribution" --paths "/*"
        fi
        
        cd "$PROJECT_ROOT"
    else
        log_warning "S3 deployment skipped: missing bucket or AWS CLI"
    fi
}

# Run performance tests
run_performance_tests() {
    local app_name=$1
    
    log_info "Running performance tests for $app_name..."
    
    local base_url
    if [ "$app_name" = "admin-dashboard" ]; then
        base_url="$BASE_URL_ADMIN"
    else
        base_url="$BASE_URL_BLOG"
    fi
    
    # Run Lighthouse tests if enabled
    local lighthouse_enabled=$(yq eval ".monitoring.lighthouse.enabled" "$CONFIG_FILE")
    if [ "$lighthouse_enabled" = "true" ]; then
        log_info "Running Lighthouse tests..."
        
        # Get test URLs for the app
        local urls_count=$(yq eval ".monitoring.lighthouse.urls.${app_name//-/_} | length" "$CONFIG_FILE")
        
        for ((i=0; i<urls_count; i++)); do
            local path=$(yq eval ".monitoring.lighthouse.urls.${app_name//-/_}[$i]" "$CONFIG_FILE")
            local full_url="$base_url$path"
            
            log_info "Testing URL: $full_url"
            
            # Run Lighthouse (requires lighthouse CLI to be installed)
            if command -v lighthouse &> /dev/null; then
                lighthouse "$full_url" \
                    --output=json \
                    --output-path="./lighthouse-$app_name-$(echo "$path" | tr '/' '-').json" \
                    --chrome-flags="--headless --no-sandbox" \
                    --quiet
            else
                log_warning "Lighthouse CLI not found. Skipping Lighthouse tests."
                break
            fi
        done
    fi
    
    # Run custom performance monitoring
    if [ -f "$SCRIPT_DIR/performance-monitor.js" ]; then
        log_info "Running custom performance monitoring..."
        node "$SCRIPT_DIR/performance-monitor.js" "$base_url"
    fi
    
    log_success "Performance tests completed for $app_name"
}

# Main deployment function
deploy() {
    local app_name=$1
    
    log_info "Starting deployment for $app_name to $ENVIRONMENT environment"
    
    # Build the application
    build_app "$app_name"
    
    # Deploy to configured targets
    deploy_to_targets "$app_name"
    
    # Run performance tests
    if [ "$ENVIRONMENT" != "development" ]; then
        run_performance_tests "$app_name"
    fi
    
    log_success "Deployment completed successfully for $app_name"
}

# Main script execution
main() {
    log_info "Frontend Deployment Script"
    log_info "=========================="
    log_info "App: $APP"
    log_info "Environment: $ENVIRONMENT"
    log_info ""
    
    # Check dependencies
    check_dependencies
    
    # Load configuration
    load_config
    
    # Deploy applications
    if [ "$APP" = "both" ]; then
        deploy "admin-dashboard"
        deploy "blog-site"
    elif [ "$APP" = "admin-dashboard" ] || [ "$APP" = "blog-site" ]; then
        deploy "$APP"
    else
        log_error "Invalid app name: $APP. Use 'admin-dashboard', 'blog-site', or 'both'"
        exit 1
    fi
    
    log_success "All deployments completed successfully!"
}

# Show usage if no arguments provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 [app] [environment]"
    echo ""
    echo "Arguments:"
    echo "  app          Application to deploy (admin-dashboard, blog-site, both)"
    echo "  environment  Target environment (development, staging, production)"
    echo ""
    echo "Examples:"
    echo "  $0 admin-dashboard staging"
    echo "  $0 blog-site production"
    echo "  $0 both staging"
    echo ""
    echo "Environment variables:"
    echo "  NETLIFY_AUTH_TOKEN    - Netlify authentication token"
    echo "  VERCEL_TOKEN          - Vercel authentication token"
    echo "  AWS_ACCESS_KEY_ID     - AWS access key for S3 deployment"
    echo "  AWS_SECRET_ACCESS_KEY - AWS secret key for S3 deployment"
    echo ""
    exit 1
fi

# Run main function
main "$@"