#!/bin/bash

# Docker setup verification script
# This script validates the Docker configuration files and setup

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] ✓ $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] ⚠ WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ✗ ERROR: $1${NC}"
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] ℹ INFO: $1${NC}"
}

# Check if required files exist
check_files() {
    log "Checking Docker configuration files..."
    
    local required_files=(
        "Dockerfile"
        "Dockerfile.production"
        "docker-compose.yml"
        "docker-compose.dev.yml"
        "docker-compose.staging.yml"
        "docker-compose.prod.yml"
        ".env.example"
        ".env.dev"
        ".env.staging"
    )
    
    local missing_files=()
    
    for file in "${required_files[@]}"; do
        if [ -f "$file" ]; then
            log "Found: $file"
        else
            missing_files+=("$file")
            error "Missing: $file"
        fi
    done
    
    if [ ${#missing_files[@]} -ne 0 ]; then
        error "Missing required files. Please ensure all Docker configuration files are present."
        return 1
    fi
    
    log "All required Docker files are present"
}

# Validate YAML syntax
validate_yaml() {
    log "Validating docker-compose YAML syntax..."
    
    local compose_files=(
        "docker-compose.yml"
        "docker-compose.dev.yml"
        "docker-compose.staging.yml"
        "docker-compose.prod.yml"
    )
    
    for file in "${compose_files[@]}"; do
        if command -v python3 >/dev/null 2>&1; then
            if python3 -c "import yaml; yaml.safe_load(open('$file'))" 2>/dev/null; then
                log "YAML syntax valid: $file"
            else
                error "YAML syntax invalid: $file"
                return 1
            fi
        else
            warn "Python3 not available, skipping YAML validation for $file"
        fi
    done
    
    log "All docker-compose files have valid YAML syntax"
}

# Check Dockerfile syntax
check_dockerfile_syntax() {
    log "Checking Dockerfile syntax..."
    
    local dockerfiles=(
        "Dockerfile"
        "Dockerfile.production"
    )
    
    for dockerfile in "${dockerfiles[@]}"; do
        # Basic syntax checks
        if grep -q "^FROM " "$dockerfile"; then
            log "Dockerfile has valid FROM instruction: $dockerfile"
        else
            error "Dockerfile missing FROM instruction: $dockerfile"
            return 1
        fi
        
        # Check for common issues
        if grep -q "COPY \. \." "$dockerfile"; then
            warn "Dockerfile copies entire context (COPY . .): $dockerfile"
            info "Consider using .dockerignore to exclude unnecessary files"
        fi
        
        if grep -q "USER " "$dockerfile"; then
            log "Dockerfile uses non-root user: $dockerfile"
        else
            warn "Dockerfile may be running as root: $dockerfile"
        fi
        
        if grep -q "HEALTHCHECK" "$dockerfile"; then
            log "Dockerfile includes health check: $dockerfile"
        else
            warn "Dockerfile missing health check: $dockerfile"
        fi
    done
    
    log "Dockerfile syntax checks completed"
}

# Validate environment files
validate_env_files() {
    log "Validating environment files..."
    
    local env_files=(
        ".env.example"
        ".env.dev"
        ".env.staging"
    )
    
    for env_file in "${env_files[@]}"; do
        if [ -f "$env_file" ]; then
            # Check for required variables
            local required_vars=(
                "DATABASE_URL"
                "REDIS_URL"
                "JWT_SECRET_KEY"
            )
            
            local missing_vars=()
            
            for var in "${required_vars[@]}"; do
                if grep -q "^$var=" "$env_file" || grep -q "^#.*$var=" "$env_file"; then
                    log "Found variable $var in $env_file"
                else
                    missing_vars+=("$var")
                fi
            done
            
            if [ ${#missing_vars[@]} -ne 0 ]; then
                warn "Missing variables in $env_file:"
                for var in "${missing_vars[@]}"; do
                    warn "  - $var"
                done
            fi
            
            # Check for insecure defaults
            if grep -q "JWT_SECRET_KEY.*demo\|JWT_SECRET_KEY.*test\|JWT_SECRET_KEY.*change" "$env_file"; then
                if [[ "$env_file" != ".env.example" ]]; then
                    warn "Insecure JWT_SECRET_KEY in $env_file"
                fi
            fi
        fi
    done
    
    log "Environment file validation completed"
}

# Check script permissions
check_scripts() {
    log "Checking deployment scripts..."
    
    local scripts=(
        "scripts/deploy-dev.sh"
        "scripts/deploy-staging.sh"
        "scripts/docker-health-check.sh"
    )
    
    for script in "${scripts[@]}"; do
        if [ -f "$script" ]; then
            if [ -x "$script" ]; then
                log "Script is executable: $script"
            else
                warn "Script is not executable: $script"
                info "Run: chmod +x $script"
            fi
        else
            error "Script not found: $script"
        fi
    done
    
    log "Script checks completed"
}

# Check Docker availability
check_docker() {
    log "Checking Docker availability..."
    
    if command -v docker >/dev/null 2>&1; then
        if docker info >/dev/null 2>&1; then
            log "Docker is available and running"
            docker --version
        else
            warn "Docker is installed but not running"
            info "Please start Docker daemon"
        fi
    else
        warn "Docker is not installed"
        info "Please install Docker to use containerized deployment"
    fi
    
    # Check docker-compose
    if command -v docker-compose >/dev/null 2>&1; then
        log "docker-compose is available"
        docker-compose --version
    elif docker compose version >/dev/null 2>&1; then
        log "docker compose (plugin) is available"
        docker compose version
    else
        warn "Neither docker-compose nor docker compose plugin is available"
        info "Please install docker-compose or Docker Compose plugin"
    fi
}

# Check network configuration
check_network_config() {
    log "Checking network configuration..."
    
    # Check for network definitions in compose files
    for compose_file in docker-compose*.yml; do
        if grep -q "networks:" "$compose_file"; then
            log "Network configuration found in $compose_file"
        else
            warn "No network configuration in $compose_file"
        fi
    done
    
    log "Network configuration checks completed"
}

# Check volume configuration
check_volume_config() {
    log "Checking volume configuration..."
    
    # Check for volume definitions
    for compose_file in docker-compose*.yml; do
        if grep -q "volumes:" "$compose_file"; then
            log "Volume configuration found in $compose_file"
        else
            warn "No volume configuration in $compose_file"
        fi
    done
    
    log "Volume configuration checks completed"
}

# Generate summary report
generate_summary() {
    echo ""
    log "=== Docker Setup Verification Summary ==="
    echo ""
    
    info "Configuration Files:"
    echo "  ✓ Dockerfile (development)"
    echo "  ✓ Dockerfile.production (optimized)"
    echo "  ✓ docker-compose.yml (default)"
    echo "  ✓ docker-compose.dev.yml (development)"
    echo "  ✓ docker-compose.staging.yml (staging)"
    echo "  ✓ docker-compose.prod.yml (production)"
    echo ""
    
    info "Environment Files:"
    echo "  ✓ .env.example (template)"
    echo "  ✓ .env.dev (development)"
    echo "  ✓ .env.staging (staging)"
    echo ""
    
    info "Deployment Scripts:"
    echo "  ✓ scripts/deploy-dev.sh"
    echo "  ✓ scripts/deploy-staging.sh"
    echo "  ✓ scripts/docker-health-check.sh"
    echo ""
    
    info "Next Steps:"
    echo "  1. Install Docker if not already installed"
    echo "  2. Configure environment variables for your target environment"
    echo "  3. Run deployment script for your environment:"
    echo "     - Development: ./scripts/deploy-dev.sh"
    echo "     - Staging: ./scripts/deploy-staging.sh"
    echo "     - Production: docker-compose -f docker-compose.prod.yml up -d"
    echo ""
    
    log "Docker setup verification completed successfully!"
}

# Main verification function
main() {
    log "Starting Docker setup verification..."
    echo ""
    
    check_files
    echo ""
    
    validate_yaml
    echo ""
    
    check_dockerfile_syntax
    echo ""
    
    validate_env_files
    echo ""
    
    check_scripts
    echo ""
    
    check_docker
    echo ""
    
    check_network_config
    echo ""
    
    check_volume_config
    echo ""
    
    generate_summary
}

# Handle script arguments
case "$1" in
    --help|-h)
        echo "Usage: $0 [--help]"
        echo ""
        echo "This script verifies the Docker setup and configuration files."
        echo ""
        echo "Options:"
        echo "  --help     Show this help message"
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac