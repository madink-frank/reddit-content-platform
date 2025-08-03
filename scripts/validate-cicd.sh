#!/bin/bash

# CI/CD Setup Validation Script
# Usage: ./scripts/validate-cicd.sh

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

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

# Check if file exists
check_file() {
    local file="$1"
    local description="$2"
    
    if [[ -f "$PROJECT_ROOT/$file" ]]; then
        log_success "$description exists: $file"
        return 0
    else
        log_error "$description missing: $file"
        return 1
    fi
}

# Check if directory exists
check_directory() {
    local dir="$1"
    local description="$2"
    
    if [[ -d "$PROJECT_ROOT/$dir" ]]; then
        log_success "$description exists: $dir"
        return 0
    else
        log_error "$description missing: $dir"
        return 1
    fi
}

# Validate YAML syntax
validate_yaml() {
    local file="$1"
    local description="$2"
    
    if command -v python3 &> /dev/null; then
        if python3 -c "import yaml; yaml.safe_load(open('$PROJECT_ROOT/$file'))" 2>/dev/null; then
            log_success "$description has valid YAML syntax"
            return 0
        else
            log_error "$description has invalid YAML syntax"
            return 1
        fi
    else
        log_warning "Python3 not available, skipping YAML validation for $description"
        return 0
    fi
}

# Check GitHub Actions workflows
check_github_workflows() {
    log_info "Checking GitHub Actions workflows..."
    
    local workflows_dir=".github/workflows"
    local errors=0
    
    # Check workflows directory
    if ! check_directory "$workflows_dir" "GitHub workflows directory"; then
        ((errors++))
        return $errors
    fi
    
    # Check individual workflow files
    local workflows=(
        "ci.yml:CI Pipeline"
        "cd.yml:CD Pipeline"
        "security.yml:Security Pipeline"
    )
    
    for workflow in "${workflows[@]}"; do
        IFS=':' read -r file description <<< "$workflow"
        if check_file "$workflows_dir/$file" "$description workflow"; then
            validate_yaml "$workflows_dir/$file" "$description workflow" || ((errors++))
        else
            ((errors++))
        fi
    done
    
    return $errors
}

# Check Docker configuration
check_docker_config() {
    log_info "Checking Docker configuration..."
    
    local errors=0
    
    # Check Dockerfiles
    local dockerfiles=(
        "Dockerfile:Development Dockerfile"
        "Dockerfile.production:Production Dockerfile"
    )
    
    for dockerfile in "${dockerfiles[@]}"; do
        IFS=':' read -r file description <<< "$dockerfile"
        check_file "$file" "$description" || ((errors++))
    done
    
    # Check Docker Compose files
    local compose_files=(
        "docker-compose.yml:Default Docker Compose"
        "docker-compose.staging.yml:Staging Docker Compose"
        "docker-compose.prod.yml:Production Docker Compose"
    )
    
    for compose_file in "${compose_files[@]}"; do
        IFS=':' read -r file description <<< "$compose_file"
        if check_file "$file" "$description"; then
            validate_yaml "$file" "$description" || ((errors++))
        else
            ((errors++))
        fi
    done
    
    return $errors
}

# Check deployment scripts
check_deployment_scripts() {
    log_info "Checking deployment scripts..."
    
    local errors=0
    
    local scripts=(
        "scripts/deploy.sh:Main deployment script"
        "scripts/deploy-railway.sh:Railway deployment script"
        "scripts/validate-cicd.sh:CI/CD validation script"
    )
    
    for script in "${scripts[@]}"; do
        IFS=':' read -r file description <<< "$script"
        if check_file "$file" "$description"; then
            # Check if script is executable
            if [[ -x "$PROJECT_ROOT/$file" ]]; then
                log_success "$description is executable"
            else
                log_warning "$description is not executable"
                log_info "Run: chmod +x $file"
            fi
        else
            ((errors++))
        fi
    done
    
    return $errors
}

# Check environment configuration
check_environment_config() {
    log_info "Checking environment configuration..."
    
    local errors=0
    
    local env_files=(
        ".env.example:Environment template"
        ".env.staging:Staging environment"
        ".env.production:Production environment"
    )
    
    for env_file in "${env_files[@]}"; do
        IFS=':' read -r file description <<< "$env_file"
        check_file "$file" "$description" || ((errors++))
    done
    
    return $errors
}

# Check Python dependencies and configuration
check_python_config() {
    log_info "Checking Python configuration..."
    
    local errors=0
    
    local python_files=(
        "requirements.txt:Python dependencies"
        "pytest.ini:Pytest configuration"
        "alembic.ini:Alembic configuration"
    )
    
    for python_file in "${python_files[@]}"; do
        IFS=':' read -r file description <<< "$python_file"
        check_file "$file" "$description" || ((errors++))
    done
    
    # Check if Python virtual environment exists
    if [[ -d "$PROJECT_ROOT/.venv" ]]; then
        log_success "Python virtual environment exists"
    else
        log_warning "Python virtual environment not found"
        log_info "Create with: python3 -m venv .venv"
    fi
    
    return $errors
}

# Check Node.js configuration
check_nodejs_config() {
    log_info "Checking Node.js configuration..."
    
    local errors=0
    
    local nodejs_files=(
        "admin-dashboard/package.json:Frontend package.json"
        "admin-dashboard/package-lock.json:Frontend package-lock.json"
        "admin-dashboard/tsconfig.json:TypeScript configuration"
        "admin-dashboard/vite.config.ts:Vite configuration"
        "admin-dashboard/tailwind.config.js:Tailwind configuration"
    )
    
    for nodejs_file in "${nodejs_files[@]}"; do
        IFS=':' read -r file description <<< "$nodejs_file"
        check_file "$file" "$description" || ((errors++))
    done
    
    # Check if node_modules exists
    if [[ -d "$PROJECT_ROOT/admin-dashboard/node_modules" ]]; then
        log_success "Node.js dependencies installed"
    else
        log_warning "Node.js dependencies not installed"
        log_info "Install with: cd admin-dashboard && npm install"
    fi
    
    return $errors
}

# Check monitoring configuration
check_monitoring_config() {
    log_info "Checking monitoring configuration..."
    
    local errors=0
    
    local monitoring_files=(
        "monitoring/prometheus.yml:Prometheus configuration"
        "monitoring/alert_rules.yml:Prometheus alert rules"
        "monitoring/alertmanager.yml:Alertmanager configuration"
    )
    
    for monitoring_file in "${monitoring_files[@]}"; do
        IFS=':' read -r file description <<< "$monitoring_file"
        if check_file "$file" "$description"; then
            validate_yaml "$file" "$description" || ((errors++))
        else
            ((errors++))
        fi
    done
    
    return $errors
}

# Check documentation
check_documentation() {
    log_info "Checking documentation..."
    
    local errors=0
    
    local docs=(
        "README.md:Project README"
        "DEPLOYMENT_GUIDE.md:Deployment guide"
    )
    
    for doc in "${docs[@]}"; do
        IFS=':' read -r file description <<< "$doc"
        check_file "$file" "$description" || ((errors++))
    done
    
    return $errors
}

# Run syntax checks
run_syntax_checks() {
    log_info "Running syntax checks..."
    
    local errors=0
    
    # Check Python syntax
    if command -v python3 &> /dev/null; then
        log_info "Checking Python syntax..."
        if find "$PROJECT_ROOT/app" -name "*.py" -exec python3 -m py_compile {} \; 2>/dev/null; then
            log_success "Python syntax check passed"
        else
            log_error "Python syntax errors found"
            ((errors++))
        fi
    else
        log_warning "Python3 not available, skipping Python syntax check"
    fi
    
    # Check shell script syntax
    if command -v bash &> /dev/null; then
        log_info "Checking shell script syntax..."
        local script_errors=0
        for script in "$PROJECT_ROOT/scripts"/*.sh; do
            if [[ -f "$script" ]]; then
                if bash -n "$script" 2>/dev/null; then
                    log_success "Shell script syntax OK: $(basename "$script")"
                else
                    log_error "Shell script syntax error: $(basename "$script")"
                    ((script_errors++))
                fi
            fi
        done
        if [[ $script_errors -eq 0 ]]; then
            log_success "All shell scripts have valid syntax"
        else
            ((errors++))
        fi
    fi
    
    return $errors
}

# Main validation function
main() {
    log_info "Starting CI/CD setup validation..."
    
    local total_errors=0
    
    # Run all checks
    check_github_workflows || ((total_errors+=$?))
    check_docker_config || ((total_errors+=$?))
    check_deployment_scripts || ((total_errors+=$?))
    check_environment_config || ((total_errors+=$?))
    check_python_config || ((total_errors+=$?))
    check_nodejs_config || ((total_errors+=$?))
    check_monitoring_config || ((total_errors+=$?))
    check_documentation || ((total_errors+=$?))
    run_syntax_checks || ((total_errors+=$?))
    
    # Summary
    echo
    log_info "Validation Summary:"
    if [[ $total_errors -eq 0 ]]; then
        log_success "All checks passed! CI/CD setup is ready."
        echo
        log_info "Next steps:"
        log_info "1. Configure GitHub repository secrets"
        log_info "2. Test the CI pipeline with a pull request"
        log_info "3. Test staging deployment"
        log_info "4. Configure production environment"
    else
        log_error "Found $total_errors issues that need to be addressed."
        echo
        log_info "Please fix the issues above and run this script again."
        exit 1
    fi
}

# Script execution
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi