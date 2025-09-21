# Data Sentinel Anomaly Detection Logic

## Overview
The Data Sentinel system uses a comprehensive multi-layered approach to detect data quality anomalies. Here's the complete logic breakdown:

## 1. Data Validation Checks

### 1.1 Null Rate Check
```python
# Check for missing values per column
null_rates = data.isnull().sum() / len(data)
for column, null_rate in null_rates.items():
    severity = (
        3 if null_rate > 0.5 else  # Critical: >50% nulls
        2 if null_rate > 0.1 else  # Warning: >10% nulls
        1                           # Info: <10% nulls
    )
    threshold = 0.1  # 10% threshold
```

### 1.2 Data Type Consistency Check
```python
# Check for mixed data types in object columns
for column in data.columns:
    if data[column].dtype == "object":
        non_null_values = data[column].dropna()
        type_counts = non_null_values.apply(type).value_counts()
        if len(type_counts) > 1:  # Mixed types detected
            severity = 2
```

### 1.3 Uniqueness Check
```python
# Check uniqueness ratio per column
for column in data.columns:
    unique_ratio = data[column].nunique() / len(data)
    threshold = 0.95  # 95% unique threshold
    severity = 2 if unique_ratio < 0.5 else 1
```

### 1.4 Outlier Detection (Numeric Columns)
```python
# Statistical outlier detection using 3-sigma rule
for column in numeric_columns:
    mean_val = data[column].mean()
    std_val = data[column].std()
    
    # Count values beyond 3 standard deviations
    outlier_count = ((data[column] - mean_val).abs() > 3 * std_val).sum()
    outlier_ratio = outlier_count / len(data)
    
    severity = (
        3 if outlier_ratio > 0.2 else    # Critical: >20% outliers
        2 if outlier_ratio > 0.05 else   # Warning: >5% outliers
        1                                # Info: <5% outliers
    )
    threshold = 0.05  # 5% outlier threshold
```

## 2. Health Score Calculation

### 2.1 Weighted Scoring System
```python
weights = {
    "null_rate": 0.3,        # 30% weight - most critical
    "type_consistency": 0.2,  # 20% weight
    "uniqueness": 0.2,       # 20% weight
    "outliers": 0.3,         # 30% weight - most critical
}

# Calculate weighted score
for result in validation_results:
    if result["passed"]:
        score = 1.0
    else:
        severity = result.get("severity", 1)
        score = max(0.0, 1.0 - (severity - 1) * 0.2)
    
    total_score += score * weight
```

### 2.2 Health Score Ranges
- **0.9 - 1.0**: Excellent (Green)
- **0.7 - 0.9**: Good (Yellow)
- **0.5 - 0.7**: Poor (Orange)
- **0.0 - 0.5**: Critical (Red)

## 3. Anomaly Creation Logic

### 3.1 Anomaly Filtering
```python
# Only create anomalies for failed checks with severity >= 2
for result in validation_results:
    if not result["passed"] and result["severity"] >= 2:
        # Create anomaly record
        anomaly_data = AnomalyCreate(
            dataset_id=dataset.id,
            table_name=dataset.name,
            column_name=result.get("column"),
            issue_type=result["check_type"],
            severity=result["severity"],
            description=self._generate_anomaly_description(result),
            extra=result.get("extra", {}),
        )
```

### 3.2 Anomaly Description Generation
```python
def _generate_anomaly_description(self, result):
    check_type = result["check_type"]
    column = result.get("column", "Unknown")
    value = result["value"]
    threshold = result["threshold"]
    
    descriptions = {
        "null_rate": f"High null rate in column '{column}': {value:.1%} null values (threshold: {threshold:.1%})",
        "uniqueness": f"Low uniqueness in column '{column}': {value:.1%} unique values (threshold: {threshold:.1%})",
        "outliers": f"High outlier ratio in column '{column}': {value:.1%} outliers (threshold: {threshold:.1%})",
        "type_consistency": f"Mixed data types in column '{column}': {value} different types detected",
    }
    return descriptions.get(check_type, f"Data quality issue in column '{column}'")
```

## 4. SQL Query Generation

### 4.1 Suggested SQL for Investigation
```python
def _generate_suggested_sql(self, result):
    check_type = result["check_type"]
    column = result.get("column", "Unknown")
    table_name = result.get("table_name", "Unknown")
    
    sql_queries = {
        "null_rate": f"SELECT {column}, COUNT(*) as null_count FROM {table_name} WHERE {column} IS NULL GROUP BY {column};",
        "uniqueness": f"SELECT {column}, COUNT(*) as frequency FROM {table_name} GROUP BY {column} ORDER BY frequency DESC LIMIT 10;",
        "outliers": f"SELECT {column}, COUNT(*) as count FROM {table_name} GROUP BY {column} ORDER BY {column} DESC LIMIT 10;",
        "type_consistency": f"SELECT {column}, TYPEOF({column}) as data_type, COUNT(*) as count FROM {table_name} GROUP BY {column}, TYPEOF({column});",
    }
    return sql_queries.get(check_type, f"SELECT * FROM {table_name} WHERE {column} IS NOT NULL LIMIT 10;")
```

## 5. Severity Levels

### 5.1 Severity Scale (1-5)
- **Level 1**: Info - Minor issues, informational only
- **Level 2**: Warning - Moderate issues, should be reviewed
- **Level 3**: Critical - Major issues, requires attention
- **Level 4**: Severe - Serious issues, immediate action needed
- **Level 5**: Emergency - Critical issues, system impact

### 5.2 Severity Assignment Logic
```python
def assign_severity(check_type, value, threshold):
    if check_type == "null_rate":
        if value > 0.5: return 3      # >50% nulls
        elif value > 0.1: return 2    # >10% nulls
        else: return 1                # <10% nulls
    
    elif check_type == "uniqueness":
        if value < 0.1: return 3      # <10% unique
        elif value < 0.5: return 2    # <50% unique
        else: return 1                # >50% unique
    
    elif check_type == "outliers":
        if value > 0.2: return 3      # >20% outliers
        elif value > 0.05: return 2   # >5% outliers
        else: return 1                # <5% outliers
    
    elif check_type == "type_consistency":
        return 2  # Always warning level for mixed types
```

## 6. AI-Powered Explanations

### 6.1 LLM Integration
The system uses Groq/OpenAI to generate intelligent explanations:

```python
def generate_llm_explanation(anomaly_data):
    prompt = f"""
    You are a Data Steward assistant. Given the following anomaly metadata, 
    explain the most likely root cause and propose remediation steps.
    
    Anomaly: {anomaly_data}
    
    Return JSON with: cause, confidence, suggested_sql, action_type
    """
    
    # Send to LLM service
    response = llm_service.generate_explanation(prompt)
    return response
```

### 6.2 Action Recommendations
- **auto_fix**: Can be automatically resolved
- **notify_owner**: Requires owner notification
- **create_issue**: Create a ticket/issue
- **no_action**: No action needed

## 7. Real-time Monitoring

### 7.1 Continuous Validation
- Scheduled runs (hourly/daily/weekly)
- Real-time triggers on data changes
- Threshold-based alerting

### 7.2 Dashboard Integration
- Health score visualization
- Anomaly trend analysis
- Action tracking and approval workflow

## 8. Example Anomaly Detection Flow

```python
# 1. Load data
data = pd.read_parquet("/app/data/sample_events.parquet")

# 2. Run validation checks
results = await validation_service._run_validation_checks(data, dataset)

# 3. Calculate health score
health_score = validation_service._calculate_health_score(results)

# 4. Detect anomalies
anomalies = await validation_service._detect_anomalies(data, dataset, results, db)

# 5. Generate AI explanations
for anomaly in anomalies:
    explanation = await llm_service.explain_anomaly(anomaly)
    anomaly.llm_explanation = explanation

# 6. Create suggested actions
actions = await agent_service.suggest_actions(anomalies)
```

This comprehensive anomaly detection system provides:
- **Multi-dimensional analysis** (nulls, types, uniqueness, outliers)
- **Intelligent scoring** with weighted importance
- **AI-powered insights** for root cause analysis
- **Actionable recommendations** with SQL queries
- **Real-time monitoring** and alerting
- **Human-in-the-loop** approval workflow
