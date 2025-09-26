#!/bin/bash
# Data Sentinel - Docker Run Script
# Easy deployment and management script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
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
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    print_success "Docker is running"
}

# Function to create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    mkdir -p data logs monitoring/grafana/dashboards monitoring/grafana/datasources nginx/ssl scripts
    print_success "Directories created"
}

# Function to build the application
build_app() {
    print_status "Building Data Sentinel application..."
    docker-compose build --no-cache
    print_success "Application built successfully"
}

# Function to start the application
start_app() {
    local profile=$1
    print_status "Starting Data Sentinel with profile: $profile"
    
    case $profile in
        "dev")
            docker-compose --profile dev up -d
            print_success "Development environment started"
            print_status "API: http://localhost:8001"
            print_status "Client: http://localhost:8502"
            ;;
        "prod")
            docker-compose up -d
            print_success "Production environment started"
            print_status "API: http://localhost:8000"
            print_status "Client: http://localhost:8501"
            ;;
        "full")
            docker-compose --profile db --profile cache --profile proxy --profile monitoring up -d
            print_success "Full environment started"
            print_status "API: http://localhost:8000"
            print_status "Client: http://localhost:8501"
            print_status "Grafana: http://localhost:3000 (admin/admin)"
            print_status "Prometheus: http://localhost:9090"
            ;;
        *)
            print_error "Invalid profile. Use: dev, prod, or full"
            exit 1
            ;;
    esac
}

# Function to stop the application
stop_app() {
    print_status "Stopping Data Sentinel..."
    docker-compose down
    print_success "Application stopped"
}

# Function to show logs
show_logs() {
    local service=$1
    if [ -z "$service" ]; then
        docker-compose logs -f
    else
        docker-compose logs -f "$service"
    fi
}

# Function to show status
show_status() {
    print_status "Data Sentinel Status:"
    docker-compose ps
}

# Function to clean up
cleanup() {
    print_status "Cleaning up Docker resources..."
    docker-compose down -v --remove-orphans
    docker system prune -f
    print_success "Cleanup completed"
}

# Function to show help
show_help() {
    echo "Data Sentinel Docker Management Script"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  build                    Build the application"
    echo "  start [profile]          Start the application (dev|prod|full)"
    echo "  stop                     Stop the application"
    echo "  restart [profile]        Restart the application"
    echo "  logs [service]           Show logs (optionally for specific service)"
    echo "  status                   Show application status"
    echo "  cleanup                  Clean up Docker resources"
    echo "  help                     Show this help message"
    echo ""
    echo "Profiles:"
    echo "  dev                      Development environment (ports 8001, 8502)"
    echo "  prod                     Production environment (ports 8000, 8501)"
    echo "  full                     Full environment with database, cache, proxy, monitoring"
    echo ""
    echo "Examples:"
    echo "  $0 build"
    echo "  $0 start dev"
    echo "  $0 start prod"
    echo "  $0 start full"
    echo "  $0 logs data-sentinel"
    echo "  $0 status"
    echo "  $0 cleanup"
}

# Main script logic
main() {
    check_docker
    create_directories
    
    case ${1:-help} in
        "build")
            build_app
            ;;
        "start")
            start_app ${2:-prod}
            ;;
        "stop")
            stop_app
            ;;
        "restart")
            stop_app
            start_app ${2:-prod}
            ;;
        "logs")
            show_logs $2
            ;;
        "status")
            show_status
            ;;
        "cleanup")
            cleanup
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# Run main function with all arguments
main "$@"

