# Data Sentinel - Docker Run Script (PowerShell)
# Easy deployment and management script for Windows

param(
    [Parameter(Position=0)]
    [ValidateSet("build", "start", "stop", "restart", "logs", "status", "cleanup", "help")]
    [string]$Command = "help",
    
    [Parameter(Position=1)]
    [ValidateSet("dev", "prod", "full")]
    [string]$Profile = "prod",
    
    [Parameter(Position=2)]
    [string]$Service = ""
)

# Function to print colored output
function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Function to check if Docker is running
function Test-Docker {
    try {
        docker info | Out-Null
        Write-Success "Docker is running"
        return $true
    }
    catch {
        Write-Error "Docker is not running. Please start Docker Desktop and try again."
        return $false
    }
}

# Function to create necessary directories
function New-Directories {
    Write-Status "Creating necessary directories..."
    $directories = @(
        "data", "logs", "monitoring/grafana/dashboards", 
        "monitoring/grafana/datasources", "nginx/ssl", "scripts"
    )
    
    foreach ($dir in $directories) {
        if (!(Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
        }
    }
    Write-Success "Directories created"
}

# Function to build the application
function Build-App {
    Write-Status "Building Data Sentinel application..."
    docker-compose build --no-cache
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Application built successfully"
    } else {
        Write-Error "Build failed"
        exit 1
    }
}

# Function to start the application
function Start-App {
    param([string]$Profile)
    
    Write-Status "Starting Data Sentinel with profile: $Profile"
    
    switch ($Profile) {
        "dev" {
            docker-compose --profile dev up -d
            Write-Success "Development environment started"
            Write-Status "API: http://localhost:8001"
            Write-Status "Client: http://localhost:8502"
        }
        "prod" {
            docker-compose up -d
            Write-Success "Production environment started"
            Write-Status "API: http://localhost:8000"
            Write-Status "Client: http://localhost:8501"
        }
        "full" {
            docker-compose --profile db --profile cache --profile proxy --profile monitoring up -d
            Write-Success "Full environment started"
            Write-Status "API: http://localhost:8000"
            Write-Status "Client: http://localhost:8501"
            Write-Status "Grafana: http://localhost:3000 (admin/admin)"
            Write-Status "Prometheus: http://localhost:9090"
        }
        default {
            Write-Error "Invalid profile. Use: dev, prod, or full"
            exit 1
        }
    }
}

# Function to stop the application
function Stop-App {
    Write-Status "Stopping Data Sentinel..."
    docker-compose down
    Write-Success "Application stopped"
}

# Function to show logs
function Show-Logs {
    param([string]$Service)
    
    if ([string]::IsNullOrEmpty($Service)) {
        docker-compose logs -f
    } else {
        docker-compose logs -f $Service
    }
}

# Function to show status
function Show-Status {
    Write-Status "Data Sentinel Status:"
    docker-compose ps
}

# Function to clean up
function Remove-Resources {
    Write-Status "Cleaning up Docker resources..."
    docker-compose down -v --remove-orphans
    docker system prune -f
    Write-Success "Cleanup completed"
}

# Function to show help
function Show-Help {
    Write-Host "Data Sentinel Docker Management Script (PowerShell)" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage: .\docker-run.ps1 [COMMAND] [PROFILE] [SERVICE]" -ForegroundColor White
    Write-Host ""
    Write-Host "Commands:" -ForegroundColor Yellow
    Write-Host "  build                    Build the application"
    Write-Host "  start                    Start the application"
    Write-Host "  stop                     Stop the application"
    Write-Host "  restart                  Restart the application"
    Write-Host "  logs                     Show logs (optionally for specific service)"
    Write-Host "  status                   Show application status"
    Write-Host "  cleanup                  Clean up Docker resources"
    Write-Host "  help                     Show this help message"
    Write-Host ""
    Write-Host "Profiles:" -ForegroundColor Yellow
    Write-Host "  dev                      Development environment (ports 8001, 8502)"
    Write-Host "  prod                     Production environment (ports 8000, 8501)"
    Write-Host "  full                     Full environment with database, cache, proxy, monitoring"
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Green
    Write-Host "  .\docker-run.ps1 build"
    Write-Host "  .\docker-run.ps1 start dev"
    Write-Host "  .\docker-run.ps1 start prod"
    Write-Host "  .\docker-run.ps1 start full"
    Write-Host "  .\docker-run.ps1 logs data-sentinel"
    Write-Host "  .\docker-run.ps1 status"
    Write-Host "  .\docker-run.ps1 cleanup"
}

# Main script logic
function Main {
    if (!(Test-Docker)) {
        exit 1
    }
    
    New-Directories
    
    switch ($Command) {
        "build" {
            Build-App
        }
        "start" {
            Start-App $Profile
        }
        "stop" {
            Stop-App
        }
        "restart" {
            Stop-App
            Start-App $Profile
        }
        "logs" {
            Show-Logs $Service
        }
        "status" {
            Show-Status
        }
        "cleanup" {
            Remove-Resources
        }
        "help" {
            Show-Help
        }
        default {
            Write-Error "Invalid command. Use 'help' to see available commands."
            Show-Help
        }
    }
}

# Run main function
Main

