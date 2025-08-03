#!/bin/bash

# Docker development helper script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
}

# Function to build and start services
start_services() {
    print_status "Building and starting Reddit Content Platform services..."
    docker-compose up --build -d
    
    print_status "Waiting for services to be ready..."
    sleep 10
    
    # Check if services are healthy
    print_status "Checking service health..."
    docker-compose ps
}

# Function to stop services
stop_services() {
    print_status "Stopping Reddit Content Platform services..."
    docker-compose down
}

# Function to restart services
restart_services() {
    print_status "Restarting Reddit Content Platform services..."
    docker-compose restart
}

# Function to view logs
view_logs() {
    if [ -z "$1" ]; then
        print_status "Showing logs for all services..."
        docker-compose logs -f
    else
        print_status "Showing logs for service: $1"
        docker-compose logs -f "$1"
    fi
}

# Function to run database migrations
run_migrations() {
    print_status "Running database migrations..."
    docker-compose exec api alembic upgrade head
}

# Function to create a new migration
create_migration() {
    if [ -z "$1" ]; then
        print_error "Please provide a migration message"
        exit 1
    fi
    
    print_status "Creating new migration: $1"
    docker-compose exec api alembic revision --autogenerate -m "$1"
}

# Function to run tests
run_tests() {
    print_status "Running tests..."
    docker-compose exec api pytest -v
}

# Function to access shell
shell() {
    service=${1:-api}
    print_status "Opening shell for service: $service"
    docker-compose exec "$service" /bin/bash
}

# Function to clean up
cleanup() {
    print_status "Cleaning up Docker resources..."
    docker-compose down -v
    docker system prune -f
}

# Function to show help
show_help() {
    echo "Reddit Content Platform Docker Development Helper"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start           Build and start all services"
    echo "  stop            Stop all services"
    echo "  restart         Restart all services"
    echo "  logs [service]  View logs (all services or specific service)"
    echo "  migrate         Run database migrations"
    echo "  makemigration   Create new migration (requires message)"
    echo "  test            Run tests"
    echo "  shell [service] Open shell (default: api)"
    echo "  cleanup         Stop services and clean up volumes"
    echo "  help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start"
    echo "  $0 logs api"
    echo "  $0 makemigration 'Add new table'"
    echo "  $0 shell worker"
}

# Main script logic
case "$1" in
    start)
        check_docker
        start_services
        ;;
    stop)
        check_docker
        stop_services
        ;;
    restart)
        check_docker
        restart_services
        ;;
    logs)
        check_docker
        view_logs "$2"
        ;;
    migrate)
        check_docker
        run_migrations
        ;;
    makemigration)
        check_docker
        create_migration "$2"
        ;;
    test)
        check_docker
        run_tests
        ;;
    shell)
        check_docker
        shell "$2"
        ;;
    cleanup)
        check_docker
        cleanup
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac