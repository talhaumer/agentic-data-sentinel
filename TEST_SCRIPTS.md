# 🧪 Data Sentinel - Test Scripts

This directory contains comprehensive test scripts to validate the Data Sentinel platform functionality in new environments.

## 📋 Available Test Scripts

### 1. **Complete System Test (Bash)**
```bash
./test_complete_system.sh
```
**Features:**
- ✅ Comprehensive end-to-end testing
- ✅ Multi-format file support validation
- ✅ Agent workflow testing
- ✅ Anomaly detection verification
- ✅ Human-in-the-loop approval queue testing
- ✅ Error handling validation
- ✅ Colored output with detailed progress

### 2. **Quick Test (Bash)**
```bash
./test_quick.sh
```
**Features:**
- ✅ Fast core functionality test
- ✅ Basic dataset operations
- ✅ Simple workflow execution
- ✅ Results verification

### 3. **Complete System Test (PowerShell)**
```powershell
.\test_complete_system.ps1
```
**Features:**
- ✅ Windows-compatible comprehensive testing
- ✅ Same functionality as Bash version
- ✅ PowerShell-native error handling

### 4. **Complete System Test (Python)**
```bash
python test_system.py
```
**Features:**
- ✅ Cross-platform Python implementation
- ✅ Detailed error reporting
- ✅ JSON response handling
- ✅ Colored terminal output

## 🚀 Quick Start

### Prerequisites
1. **Start Data Sentinel:**
   ```bash
   python run.py
   ```

2. **Verify services are running:**
   - API: http://localhost:8000
   - Dashboard: http://localhost:8501

### Run Tests

**Option 1: Complete Test (Recommended)**
```bash
# Bash/Linux/macOS
./test_complete_system.sh

# Windows PowerShell
.\test_complete_system.ps1

# Python (Cross-platform)
python test_system.py
```

**Option 2: Quick Test**
```bash
./test_quick.sh
```

## 📊 What Gets Tested

### **Core Functionality**
- [x] Health check endpoint
- [x] Dataset CRUD operations
- [x] Multi-format file support (Parquet, CSV, JSON, Excel)
- [x] Agent workflow execution
- [x] Anomaly detection and reporting
- [x] Human-in-the-loop approval queue
- [x] Error handling and edge cases

### **Data Quality Checks**
- [x] Completeness validation
- [x] Uniqueness checks
- [x] Consistency validation
- [x] Accuracy assessment
- [x] Timeliness verification

### **AI Features**
- [x] LLM-powered anomaly explanations
- [x] Automated action planning
- [x] Severity-based routing
- [x] GitHub issue creation
- [x] Email notification system

### **Integration Testing**
- [x] API endpoint validation
- [x] Database operations
- [x] External service integration
- [x] Workflow orchestration
- [x] Error recovery

## 🔧 Test Configuration

### **Environment Variables**
The test scripts use these default configurations:
```bash
API_BASE="http://localhost:8000"
DASHBOARD_URL="http://localhost:8501"
```

### **Custom Configuration**
You can modify the scripts to use different endpoints:
```bash
# Bash
API_BASE="http://your-server:8000" ./test_complete_system.sh

# PowerShell
.\test_complete_system.ps1 -ApiBase "http://your-server:8000"

# Python
python test_system.py  # Edit the API_BASE variable in the script
```

## 📈 Expected Results

### **Successful Test Output**
```
🛡️ Data Sentinel - Complete System Test
==========================================

✅ Health check passed
✅ Dataset list retrieved
✅ Parquet dataset added
✅ CSV dataset added
✅ JSON dataset added
✅ Excel dataset added
✅ Workflow 1 completed
✅ CSV workflow completed
✅ JSON workflow completed
✅ Workflow runs retrieved
✅ Anomalies retrieved
✅ Approval queue retrieved
✅ High-severity anomaly created
✅ Anomaly updated to pending approval
✅ Approval process completed
✅ Final dataset list retrieved
✅ Final anomalies retrieved
✅ Final approval queue retrieved

🎉 ALL TESTS COMPLETED SUCCESSFULLY! 🎉
```

### **Sample Data Created**
- **test_events** (Parquet): Sample event data
- **test_employees** (CSV): Employee records
- **test_products** (JSON): Product catalog
- **test_employees_excel** (Excel): Excel employee data

### **Expected Anomalies**
- Low uniqueness in categorical columns
- Missing value patterns
- Data type inconsistencies
- Statistical outliers

## 🚨 Troubleshooting

### **Common Issues**

**1. "Connection refused" errors**
```bash
# Ensure Data Sentinel is running
python run.py

# Check if ports are available
netstat -an | grep :8000
netstat -an | grep :8501
```

**2. "jq command not found" (Bash scripts)**
```bash
# Install jq
# macOS
brew install jq

# Ubuntu/Debian
sudo apt-get install jq

# CentOS/RHEL
sudo yum install jq
```

**3. "PowerShell execution policy" (Windows)**
```powershell
# Allow script execution
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**4. "Module not found" (Python)**
```bash
# Install required packages
pip install requests
```

### **Debug Mode**
For detailed debugging, modify the scripts to show full responses:
```bash
# In test_complete_system.sh, change:
curl -s "$API_BASE/health" | jq '.'

# To:
curl -v "$API_BASE/health" | jq '.'
```

## 📝 Test Script Details

### **test_complete_system.sh**
- **Lines of Code:** ~200
- **Test Cases:** 11 comprehensive tests
- **Dependencies:** curl, jq
- **Platform:** Linux, macOS, WSL

### **test_quick.sh**
- **Lines of Code:** ~50
- **Test Cases:** 4 core tests
- **Dependencies:** curl, jq
- **Platform:** Linux, macOS, WSL

### **test_complete_system.ps1**
- **Lines of Code:** ~150
- **Test Cases:** 11 comprehensive tests
- **Dependencies:** PowerShell 5.0+
- **Platform:** Windows

### **test_system.py**
- **Lines of Code:** ~300
- **Test Cases:** 11 comprehensive tests
- **Dependencies:** requests
- **Platform:** Cross-platform

## 🎯 Best Practices

1. **Run tests in clean environment** - Start with fresh Data Sentinel instance
2. **Check prerequisites** - Ensure all services are running before testing
3. **Review test output** - Look for any failed assertions or errors
4. **Clean up after testing** - Remove test datasets if needed
5. **Use appropriate script** - Choose based on your platform and needs

## 🔄 Continuous Integration

These test scripts can be integrated into CI/CD pipelines:

```yaml
# GitHub Actions example
- name: Test Data Sentinel
  run: |
    python run.py &
    sleep 30
    ./test_complete_system.sh
```

```yaml
# Azure DevOps example
- script: |
    python run.py &
    Start-Sleep 30
    .\test_complete_system.ps1
  displayName: 'Test Data Sentinel'
```

---

**Happy Testing! 🧪✨**
