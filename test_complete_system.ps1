# 🛡️ Data Sentinel - Complete System Test Script (PowerShell)
# This script tests all functionality of the Data Sentinel platform
# Run this after starting the system with: python run.py

param(
    [string]$ApiBase = "http://localhost:8000",
    [string]$DashboardUrl = "http://localhost:8501"
)

# Colors for output
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"
$Blue = "Blue"
$Cyan = "Cyan"

Write-Host "🛡️ Data Sentinel - Complete System Test" -ForegroundColor $Blue
Write-Host "==========================================" -ForegroundColor $Blue
Write-Host ""

# Function to test API endpoint
function Test-ApiEndpoint {
    param(
        [string]$Url,
        [string]$Method = "GET",
        [hashtable]$Body = $null,
        [string]$Description
    )
    
    try {
        if ($Body) {
            $jsonBody = $Body | ConvertTo-Json -Depth 10
            $response = Invoke-RestMethod -Uri $Url -Method $Method -Body $jsonBody -ContentType "application/json"
        } else {
            $response = Invoke-RestMethod -Uri $Url -Method $Method
        }
        Write-Host "✅ $Description" -ForegroundColor $Green
        return $response
    }
    catch {
        Write-Host "❌ $Description - Error: $($_.Exception.Message)" -ForegroundColor $Red
        throw
    }
}

# Function to wait for service
function Wait-ForService {
    param(
        [string]$Url,
        [string]$ServiceName,
        [int]$MaxAttempts = 30
    )
    
    Write-Host "⏳ Waiting for $ServiceName to be ready..." -ForegroundColor $Yellow
    
    for ($i = 1; $i -le $MaxAttempts; $i++) {
        try {
            Invoke-RestMethod -Uri $Url -Method GET -TimeoutSec 5 | Out-Null
            Write-Host "✅ $ServiceName is ready!" -ForegroundColor $Green
            return $true
        }
        catch {
            Write-Host "." -NoNewline
            Start-Sleep -Seconds 2
        }
    }
    
    Write-Host ""
    Write-Host "❌ $ServiceName failed to start after $MaxAttempts attempts" -ForegroundColor $Red
    return $false
}

# Wait for services to be ready
if (-not (Wait-ForService "$ApiBase/health" "API Server")) { exit 1 }
if (-not (Wait-ForService "$DashboardUrl" "Dashboard")) { exit 1 }

Write-Host ""
Write-Host "🚀 Starting Complete System Test" -ForegroundColor Magenta
Write-Host ""

# Test 1: Health Check
Write-Host "1. Testing Health Check" -ForegroundColor $Cyan
Test-ApiEndpoint -Url "$ApiBase/health" -Description "Health check passed"

# Test 2: List Initial Datasets
Write-Host "2. Testing Initial Dataset List" -ForegroundColor $Cyan
$datasets = Test-ApiEndpoint -Url "$ApiBase/api/v1/datasets/" -Description "Dataset list retrieved"

# Test 3: Add Sample Datasets
Write-Host "3. Adding Sample Datasets" -ForegroundColor $Cyan

# Add Parquet dataset
$parquetDataset = Test-ApiEndpoint -Url "$ApiBase/api/v1/datasets/" -Method "POST" -Body @{
    name = "test_events"
    owner = "test_team"
    source = "file:///Users/talha.umer/agentic-data-sentinel/data/sample_events.parquet"
} -Description "Parquet dataset added"

# Add CSV dataset
$csvDataset = Test-ApiEndpoint -Url "$ApiBase/api/v1/datasets/" -Method "POST" -Body @{
    name = "test_employees"
    owner = "hr_team"
    source = "file:///Users/talha.umer/agentic-data-sentinel/data/sample_employees.csv?format=csv"
} -Description "CSV dataset added"

# Add JSON dataset
$jsonDataset = Test-ApiEndpoint -Url "$ApiBase/api/v1/datasets/" -Method "POST" -Body @{
    name = "test_products"
    owner = "product_team"
    source = "file:///Users/talha.umer/agentic-data-sentinel/data/sample_products.json?format=json"
} -Description "JSON dataset added"

# Add Excel dataset
$excelDataset = Test-ApiEndpoint -Url "$ApiBase/api/v1/datasets/" -Method "POST" -Body @{
    name = "test_employees_excel"
    owner = "hr_team"
    source = "file:///Users/talha.umer/agentic-data-sentinel/data/sample_employees.xlsx?format=xlsx"
} -Description "Excel dataset added"

# Test 4: Run Agent Workflows
Write-Host "4. Running Agent Workflows" -ForegroundColor $Cyan

# Get updated dataset list
$datasets = Test-ApiEndpoint -Url "$ApiBase/api/v1/datasets/" -Description "Updated dataset list retrieved"
Write-Host "Available datasets:"
$datasets | ForEach-Object { Write-Host "ID $($_.id): $($_.name) ($($_.owner))" }

# Run workflow on first dataset
Write-Host "Running workflow on dataset 1..." -ForegroundColor $Yellow
$workflow1 = Test-ApiEndpoint -Url "$ApiBase/api/v1/agent/workflow" -Method "POST" -Body @{
    dataset_id = 1
    include_llm_explanation = $true
} -Description "Workflow 1 completed"

# Run workflow on CSV dataset
Write-Host "Running workflow on CSV dataset..." -ForegroundColor $Yellow
$workflow2 = Test-ApiEndpoint -Url "$ApiBase/api/v1/agent/workflow" -Method "POST" -Body @{
    dataset_id = 2
    include_llm_explanation = $true
} -Description "CSV workflow completed"

# Run workflow on JSON dataset
Write-Host "Running workflow on JSON dataset..." -ForegroundColor $Yellow
$workflow3 = Test-ApiEndpoint -Url "$ApiBase/api/v1/agent/workflow" -Method "POST" -Body @{
    dataset_id = 3
    include_llm_explanation = $true
} -Description "JSON workflow completed"

# Test 5: Check Workflow Runs
Write-Host "5. Checking Workflow Runs" -ForegroundColor $Cyan
$runs = Test-ApiEndpoint -Url "$ApiBase/api/v1/runs/" -Description "Workflow runs retrieved"

Write-Host "Recent runs:"
$runs | ForEach-Object { 
    $healthScore = if ($_.summary.health_score) { $_.summary.health_score } else { "N/A" }
    Write-Host "Run $($_.id): Dataset $($_.dataset_id) | Status: $($_.status) | Health: $healthScore"
}

# Test 6: Check Anomalies
Write-Host "6. Checking Detected Anomalies" -ForegroundColor $Cyan
$anomalies = Test-ApiEndpoint -Url "$ApiBase/api/v1/anomalies/" -Description "Anomalies retrieved"

$anomalyCount = $anomalies.Count
Write-Host "Total anomalies detected: $anomalyCount"

if ($anomalyCount -gt 0) {
    Write-Host "Sample anomalies:"
    $anomalies | Select-Object -First 3 | ForEach-Object {
        Write-Host "ID $($_.id): $($_.table_name).$($_.column_name) - $($_.issue_type) (Severity: $($_.severity))"
    }
}

# Test 7: Test Approval Queue
Write-Host "7. Testing Approval Queue" -ForegroundColor $Cyan
$approvals = Test-ApiEndpoint -Url "$ApiBase/api/v1/agent/pending-approvals" -Description "Approval queue retrieved"

$pendingCount = $approvals.count
Write-Host "Pending approvals: $pendingCount"

# Test 8: Create High-Severity Anomaly for Testing
Write-Host "8. Creating Test High-Severity Anomaly" -ForegroundColor $Cyan
$highSeverityAnomaly = Test-ApiEndpoint -Url "$ApiBase/api/v1/anomalies/" -Method "POST" -Body @{
    dataset_id = 1
    table_name = "events"
    column_name = "critical_field"
    issue_type = "data_loss"
    severity = 5
    description = "Critical data loss detected - test anomaly for approval queue"
    status = "open"
} -Description "High-severity anomaly created"

# Update anomaly to pending approval
$anomalyId = $highSeverityAnomaly.id
Test-ApiEndpoint -Url "$ApiBase/api/v1/anomalies/$anomalyId" -Method "PUT" -Body @{
    status = "pending_approval"
    action_taken = "pending_approval"
} -Description "Anomaly updated to pending approval"

# Test 9: Test Approval Process
Write-Host "9. Testing Approval Process" -ForegroundColor $Cyan
$approveResponse = Test-ApiEndpoint -Url "$ApiBase/api/v1/agent/approve/$anomalyId?approved=true&approved_by=test_user" -Method "POST" -Description "Approval process completed"

# Test 10: Check Final Status
Write-Host "10. Checking Final System Status" -ForegroundColor $Cyan

# Check datasets
Write-Host "Dataset health scores:"
$finalDatasets = Test-ApiEndpoint -Url "$ApiBase/api/v1/datasets/" -Description "Final dataset list retrieved"
$finalDatasets | ForEach-Object { Write-Host "$($_.name): $($_.health_score)" }

# Check final anomaly count
$finalAnomalies = Test-ApiEndpoint -Url "$ApiBase/api/v1/anomalies/" -Description "Final anomalies retrieved"
$finalAnomalyCount = $finalAnomalies.Count
Write-Host "Total anomalies: $finalAnomalyCount"

# Check final approval queue
$finalApprovals = Test-ApiEndpoint -Url "$ApiBase/api/v1/agent/pending-approvals" -Description "Final approval queue retrieved"
$finalPendingCount = $finalApprovals.count
Write-Host "Pending approvals: $finalPendingCount"

Write-Host ""
Write-Host "🎉 ALL TESTS COMPLETED SUCCESSFULLY! 🎉" -ForegroundColor $Green
Write-Host ""
Write-Host "📊 Test Summary:" -ForegroundColor $Blue
Write-Host "  • Health check: ✅"
Write-Host "  • Dataset management: ✅"
Write-Host "  • Multi-format support: ✅"
Write-Host "  • Agent workflows: ✅"
Write-Host "  • Anomaly detection: ✅"
Write-Host "  • Approval queue: ✅"
Write-Host ""
Write-Host "🌐 Access Points:" -ForegroundColor Magenta
Write-Host "  • Dashboard: $DashboardUrl"
Write-Host "  • API: $ApiBase"
Write-Host "  • API Docs: $ApiBase/docs"
Write-Host "  • Health: $ApiBase/health"
Write-Host ""
Write-Host "Data Sentinel is fully operational! 🚀" -ForegroundColor $Green
