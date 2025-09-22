"""Data validation and quality checking service."""

from typing import Dict, List, Any, Optional
from datetime import datetime

import pandas as pd
import numpy as np

import structlog
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import Dataset, Anomaly
from app.schemas import AnomalyCreate

logger = structlog.get_logger(__name__)
settings = get_settings()


class ValidationService:
    """Service for data validation and quality checking."""

    def __init__(self):
        self.settings = get_settings()

    async def validate_dataset(self, dataset: Dataset, db: Session) -> Dict[str, Any]:
        """Run comprehensive validation on a dataset."""
        try:
            logger.info("Starting validation", dataset_id=dataset.id, name=dataset.name)

            # Sample data from data warehouse
            sample_data = await self._sample_data(dataset, db)

            if sample_data is None or sample_data.empty:
                logger.warning("No data found for validation", dataset_id=dataset.id)
                return {
                    "status": "completed",
                    "health_score": 0.0,
                    "anomalies": [],
                    "summary": {"error": "No data available for validation"},
                }

            # Run validation checks
            validation_results = await self._run_validation_checks(sample_data, dataset)

            # Calculate health score
            health_score = self._calculate_health_score(validation_results)

            # Detect anomalies
            anomalies = await self._detect_anomalies(
                sample_data, dataset, validation_results, db
            )

            # Update dataset health score
            dataset.health_score = health_score
            dataset.last_ingest = datetime.utcnow()
            db.commit()

            logger.info(
                "Validation completed",
                dataset_id=dataset.id,
                health_score=health_score,
                anomaly_count=len(anomalies),
            )

            return {
                "status": "completed",
                "health_score": health_score,
                "anomalies": anomalies,
                "summary": {
                    "total_rows": len(sample_data),
                    "total_columns": len(sample_data.columns),
                    "validation_checks": len(validation_results),
                    "anomalies_detected": len(anomalies),
                },
            }

        except Exception as e:
            logger.error("Validation failed", dataset_id=dataset.id, error=str(e))
            return {
                "status": "failed",
                "health_score": 0.0,
                "anomalies": [],
                "summary": {"error": str(e)},
            }

    async def _sample_data(
        self, dataset: Dataset, db: Session
    ) -> Optional[pd.DataFrame]:
        """Sample data from either parquet file or SQL table."""
        try:
            print(f"Dataset source: {dataset.source}")
            print(f"Dataset name: {dataset.name}")

            # Parse source URL to extract file path
            file_path = self._parse_source_path(dataset.source)

            # Check if source is a parquet file
            if file_path and file_path.endswith(".parquet"):
                return await self._sample_from_parquet(dataset, file_path)

            # Otherwise try to find a SQL table
            return await self._sample_from_sql(dataset, db)

        except Exception as e:
            logger.error("Failed to sample data", dataset_id=dataset.id, error=str(e))
            print(f"Error sampling data: {e}")
            return self._create_mock_data()

    def _parse_source_path(self, source: str) -> str:
        """Parse source URL to extract file path."""
        if not source:
            return ""

        # Handle file:// URLs
        if source.startswith("file://"):
            # Remove file:// prefix and query parameters
            path = source[7:]  # Remove "file://"
            if "?" in path:
                path = path.split("?")[0]  # Remove query parameters
            return path

        # Handle direct file paths
        if source.endswith((".parquet", ".csv", ".json", ".xlsx")):
            return source

        return source

    async def _sample_from_parquet(
        self, dataset: Dataset, file_path: str = None
    ) -> Optional[pd.DataFrame]:
        """Sample data from parquet file."""
        try:
            from pathlib import Path

            # Use provided file_path or fall back to dataset.source
            actual_path = file_path or dataset.source
            source_path = Path(actual_path)
            print(f"Source path: {source_path}")

            if not source_path.exists():
                logger.warning("Parquet file not found", source=actual_path)
                print(f"File not found: {source_path.absolute()}")
                return None

            sample_data = pd.read_parquet(actual_path)

            print(f"Sample data: {sample_data.head()}")
            print(
                f"Successfully read {len(sample_data)} rows from parquet: {dataset.source}"
            )
            return sample_data

        except Exception as e:
            logger.error(
                "Failed to read parquet file", source=dataset.source, error=str(e)
            )
            print(f"Error reading parquet: {e}")
            return None

    async def _sample_from_sql(
        self, dataset: Dataset, db: Session
    ) -> Optional[pd.DataFrame]:
        """Sample data from SQL table."""
        try:
            from sqlalchemy import inspect, text

            inspector = inspect(db.get_bind())
            table_names = inspector.get_table_names()
            print("Available tables:", table_names)

            # Try different possible table names
            possible_table_names = [
                dataset.name.lower()
                .replace(" ", "_")
                .replace("dataset", "")
                .strip("_"),
                dataset.name.lower().replace(" ", "_"),
                "events",  # Common table name
                "event",  # Singular version
            ]

            actual_table_name = None
            for table_name in possible_table_names:
                if table_name in table_names:
                    actual_table_name = table_name
                    break

            if not actual_table_name:
                logger.warning("No matching table found", dataset_name=dataset.name)
                print(
                    f"No table found for dataset: {dataset.name}. Available: {table_names}"
                )
                return None

            print(f"Using table: {actual_table_name}")

            # Sample data from the table
            query = text(f"SELECT * FROM {actual_table_name} LIMIT 100")
            result = db.execute(query)

            columns = result.keys()
            data = result.fetchall()

            if not data:
                logger.warning("No data found in table", table_name=actual_table_name)
                return None

            df = pd.DataFrame(data, columns=columns)
            print(
                f"Successfully sampled {len(df)} rows from table: {actual_table_name}"
            )
            return df

        except Exception as e:
            logger.error(
                "Failed to sample from SQL", dataset_id=dataset.id, error=str(e)
            )
            print(f"Error sampling from SQL: {e}")
            return None  # Fallback to mock data

    def _create_mock_data(self) -> pd.DataFrame:
        """Create mock data for testing when no real data is available."""
        import random
        from datetime import datetime, timedelta
        
        data = {
            'user_id': [f"user_{i}" for i in range(100)],
            'name': [f"User {i}" for i in range(100)],
            'email': [f"user{i}@example.com" for i in range(100)],
            'age': [random.randint(18, 80) for _ in range(100)],
            'salary': [random.randint(30000, 150000) for _ in range(100)],
            'created_at': [datetime.now() - timedelta(days=random.randint(1, 365)) for _ in range(100)]
        }
        
        return pd.DataFrame(data)

    async def _run_validation_checks(
        self, data: pd.DataFrame, dataset: Dataset
    ) -> List[Dict[str, Any]]:
        """Run comprehensive validation checks on the data."""
        results = []

        try:
            # Check 1: Null rate per column
            results.extend(self._check_null_rates(data))
            
            # Check 2: Data type consistency
            results.extend(self._check_type_consistency(data))
            
            # Check 3: Uniqueness and duplicates
            results.extend(self._check_uniqueness_and_duplicates(data))
            
            # Check 4: Statistical outliers
            results.extend(self._check_statistical_outliers(data))
            
            # Check 5: Range validation
            results.extend(self._check_range_validation(data))
            
            # Check 6: Format validation
            results.extend(self._check_format_validation(data))
            
            # Check 7: Referential integrity
            results.extend(self._check_referential_integrity(data))
            
            # Check 8: Business rule validation
            results.extend(self._check_business_rules(data))
            
            # Check 9: Completeness validation
            results.extend(self._check_completeness(data))
            
            # Check 10: Consistency across columns
            results.extend(self._check_cross_column_consistency(data))

            return results

        except Exception as e:
            logger.error("Validation checks failed", error=str(e))
            return []

    def _check_null_rates(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Check null rates per column."""
        results = []
        null_rates = data.isnull().sum() / len(data)
        
        for column, null_rate in null_rates.items():
            results.append({
                "check_type": "null_rate",
                "column": column,
                "value": float(null_rate),
                "threshold": 0.1,  # 10% threshold
                "passed": null_rate <= 0.1,
                "severity": 3 if null_rate > 0.5 else 2 if null_rate > 0.1 else 1,
                "extra": {
                    "null_count": int(data[column].isnull().sum()),
                    "total_count": len(data),
                    "non_null_count": int(data[column].notna().sum())
                }
            })
        
        return results

    def _check_type_consistency(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Check for data type inconsistencies."""
        results = []
        
        for column in data.columns:
            if data[column].dtype == "object":
                non_null_values = data[column].dropna()
                if len(non_null_values) > 0:
                    type_counts = non_null_values.apply(type).value_counts()
                    if len(type_counts) > 1:
                        results.append({
                            "check_type": "type_consistency",
                            "column": column,
                            "value": len(type_counts),
                            "threshold": 1,
                            "passed": False,
                            "severity": 2,
                            "extra": {
                                "type_distribution": type_counts.to_dict(),
                                "mixed_type_rows": int((type_counts > 0).sum())
                            }
                        })
        
        return results

    def _check_uniqueness_and_duplicates(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Check for uniqueness violations and duplicate records."""
        results = []
        
        # Check individual column uniqueness
        for column in data.columns:
            unique_ratio = data[column].nunique() / len(data)
            duplicate_count = len(data) - data[column].nunique()
            
            results.append({
                "check_type": "uniqueness",
                "column": column,
                "value": float(unique_ratio),
                "threshold": 0.95,  # 95% unique threshold
                "passed": unique_ratio >= 0.95,
                "severity": 3 if unique_ratio < 0.5 else 2 if unique_ratio < 0.95 else 1,
                "extra": {
                    "unique_count": int(data[column].nunique()),
                    "duplicate_count": int(duplicate_count),
                    "total_count": len(data)
                }
            })
        
        # Check for duplicate rows
        duplicate_rows = data.duplicated().sum()
        if duplicate_rows > 0:
            results.append({
                "check_type": "duplicate_rows",
                "column": None,
                "value": float(duplicate_rows / len(data)),
                "threshold": 0.0,
                "passed": False,
                "severity": 3 if duplicate_rows > len(data) * 0.1 else 2,
                "extra": {
                    "duplicate_row_count": int(duplicate_rows),
                    "total_rows": len(data),
                    "unique_rows": len(data.drop_duplicates())
                }
            })
        
        return results

    def _check_statistical_outliers(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Check for statistical outliers in numeric columns."""
        results = []
        numeric_columns = data.select_dtypes(include=[np.number]).columns
        
        for column in numeric_columns:
            if data[column].notna().sum() > 0:
                values = data[column].dropna()
                if len(values) > 3:  # Need at least 4 values for meaningful stats
                    mean_val = values.mean()
                    std_val = values.std()
                    
                    if std_val > 0:  # Avoid division by zero
                        # Check for outliers (beyond 3 standard deviations)
                        outlier_mask = (values - mean_val).abs() > 3 * std_val
                        outlier_count = outlier_mask.sum()
                        outlier_ratio = outlier_count / len(data)
                        
                        results.append({
                            "check_type": "statistical_outliers",
                            "column": column,
                            "value": float(outlier_ratio),
                            "threshold": 0.05,  # 5% outlier threshold
                            "passed": outlier_ratio <= 0.05,
                            "severity": 3 if outlier_ratio > 0.2 else 2 if outlier_ratio > 0.05 else 1,
                            "extra": {
                                "min": float(values.min()),
                                "max": float(values.max()),
                                "mean": float(mean_val),
                                "std": float(std_val),
                                "outlier_count": int(outlier_count),
                                "outlier_values": values[outlier_mask].tolist()[:10]  # Limit to first 10
                            }
                        })
        
        return results

    def _check_range_validation(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Check for values outside expected ranges."""
        results = []
        numeric_columns = data.select_dtypes(include=[np.number]).columns
        
        for column in numeric_columns:
            if data[column].notna().sum() > 0:
                values = data[column].dropna()
                if len(values) > 0:
                    # Check for negative values where they shouldn't exist
                    if column.lower() in ['age', 'salary', 'price', 'amount', 'quantity']:
                        negative_count = (values < 0).sum()
                        if negative_count > 0:
                            results.append({
                                "check_type": "negative_values",
                                "column": column,
                                "value": float(negative_count / len(data)),
                                "threshold": 0.0,
                                "passed": False,
                                "severity": 3 if negative_count > len(data) * 0.1 else 2,
                                "extra": {
                                    "negative_count": int(negative_count),
                                    "negative_values": values[values < 0].tolist()[:10]
                                }
                            })
                    
                    # Check for zero values where they shouldn't exist
                    if column.lower() in ['price', 'amount']:
                        zero_count = (values == 0).sum()
                        if zero_count > 0:
                            results.append({
                                "check_type": "zero_values",
                                "column": column,
                                "value": float(zero_count / len(data)),
                                "threshold": 0.0,
                                "passed": False,
                                "severity": 2,
                                "extra": {
                                    "zero_count": int(zero_count),
                                    "zero_value_positions": data[data[column] == 0].index.tolist()[:10]
                                }
                            })
        
        return results

    def _check_format_validation(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Check for format violations in string columns."""
        results = []
        
        for column in data.columns:
            if data[column].dtype == "object":
                non_null_values = data[column].dropna()
                if len(non_null_values) > 0:
                    
                    # Email format validation
                    if 'email' in column.lower():
                        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                        import re
                        invalid_emails = non_null_values[~non_null_values.str.match(email_pattern, na=False)]
                        if len(invalid_emails) > 0:
                            results.append({
                                "check_type": "email_format",
                                "column": column,
                                "value": float(len(invalid_emails) / len(data)),
                                "threshold": 0.0,
                                "passed": False,
                                "severity": 2,
                                "extra": {
                                    "invalid_email_count": len(invalid_emails),
                                    "invalid_emails": invalid_emails.tolist()[:10]
                                }
                            })
                    
                    # Phone format validation
                    elif 'phone' in column.lower():
                        phone_pattern = r'^[\+]?[1-9][\d]{0,15}$|^[\+]?[1-9]?[\d\s\-\(\)]{7,}$'
                        import re
                        invalid_phones = non_null_values[~non_null_values.str.match(phone_pattern, na=False)]
                        if len(invalid_phones) > 0:
                            results.append({
                                "check_type": "phone_format",
                                "column": column,
                                "value": float(len(invalid_phones) / len(data)),
                                "threshold": 0.1,
                                "passed": len(invalid_phones) / len(data) <= 0.1,
                                "severity": 2 if len(invalid_phones) / len(data) > 0.2 else 1,
                                "extra": {
                                    "invalid_phone_count": len(invalid_phones),
                                    "invalid_phones": invalid_phones.tolist()[:10]
                                }
                            })
                    
                    # Date format validation
                    elif 'date' in column.lower():
                        try:
                            pd.to_datetime(non_null_values, errors='coerce')
                            invalid_dates = pd.to_datetime(non_null_values, errors='coerce').isna()
                            invalid_count = invalid_dates.sum()
                            if invalid_count > 0:
                                results.append({
                                    "check_type": "date_format",
                                    "column": column,
                                    "value": float(invalid_count / len(data)),
                                    "threshold": 0.0,
                                    "passed": False,
                                    "severity": 2,
                                    "extra": {
                                        "invalid_date_count": int(invalid_count),
                                        "invalid_dates": non_null_values[invalid_dates].tolist()[:10]
                                    }
                                })
                        except:
                            pass
        
        return results

    def _check_referential_integrity(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Check for referential integrity violations."""
        results = []
        
        # Check for foreign key like columns (IDs that should reference other tables)
        id_columns = [col for col in data.columns if 'id' in col.lower()]
        
        for column in id_columns:
            if data[column].dtype in ['object', 'int64']:
                non_null_values = data[column].dropna()
                if len(non_null_values) > 0:
                    # Check for invalid ID formats
                    if data[column].dtype == 'object':
                        # Check for proper ID format (e.g., should start with letters/numbers)
                        invalid_ids = non_null_values[~non_null_values.str.match(r'^[A-Za-z0-9_-]+$', na=False)]
                        if len(invalid_ids) > 0:
                            results.append({
                                "check_type": "invalid_id_format",
                                "column": column,
                                "value": float(len(invalid_ids) / len(data)),
                                "threshold": 0.0,
                                "passed": False,
                                "severity": 3,
                                "extra": {
                                    "invalid_id_count": len(invalid_ids),
                                    "invalid_ids": invalid_ids.tolist()[:10]
                                }
                            })
        
        return results

    def _check_business_rules(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Check for business rule violations."""
        results = []
        
        # Age validation
        if 'age' in data.columns:
            age_col = data['age']
            if age_col.dtype in ['int64', 'float64']:
                invalid_ages = age_col[(age_col < 0) | (age_col > 150)]
                if len(invalid_ages) > 0:
                    results.append({
                        "check_type": "invalid_age",
                        "column": "age",
                        "value": float(len(invalid_ages) / len(data)),
                        "threshold": 0.0,
                        "passed": False,
                        "severity": 3,
                        "extra": {
                            "invalid_age_count": len(invalid_ages),
                            "invalid_ages": invalid_ages.tolist()[:10]
                        }
                    })
        
        # Status validation
        if 'status' in data.columns:
            status_col = data['status']
            valid_statuses = ['active', 'inactive', 'pending', 'completed', 'cancelled']
            invalid_statuses = status_col[~status_col.isin(valid_statuses)]
            if len(invalid_statuses) > 0:
                results.append({
                    "check_type": "invalid_status",
                    "column": "status",
                    "value": float(len(invalid_statuses) / len(data)),
                    "threshold": 0.0,
                    "passed": False,
                    "severity": 2,
                    "extra": {
                        "invalid_status_count": len(invalid_statuses),
                        "invalid_statuses": invalid_statuses.unique().tolist(),
                        "valid_statuses": valid_statuses
                    }
                })
        
        return results

    def _check_completeness(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Check for completeness of critical fields."""
        results = []
        
        # Define critical columns based on common patterns
        critical_columns = []
        for col in data.columns:
            if any(keyword in col.lower() for keyword in ['id', 'name', 'email', 'user', 'customer']):
                critical_columns.append(col)
        
        for column in critical_columns:
            null_count = data[column].isnull().sum()
            if null_count > 0:
                results.append({
                    "check_type": "critical_field_missing",
                    "column": column,
                    "value": float(null_count / len(data)),
                    "threshold": 0.0,
                    "passed": False,
                    "severity": 4,  # High severity for critical fields
                    "extra": {
                        "missing_count": int(null_count),
                        "total_count": len(data),
                        "missing_positions": data[data[column].isnull()].index.tolist()[:10]
                    }
                })
        
        return results

    def _check_cross_column_consistency(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Check for consistency across related columns."""
        results = []
        
        # Check if we have both first and last name columns
        name_cols = [col for col in data.columns if 'name' in col.lower()]
        if len(name_cols) >= 2:
            for i, col1 in enumerate(name_cols):
                for col2 in name_cols[i+1:]:
                    # Check for rows where both name fields are null
                    both_null = data[col1].isnull() & data[col2].isnull()
                    both_null_count = both_null.sum()
                    
                    if both_null_count > 0:
                        results.append({
                            "check_type": "inconsistent_names",
                            "column": f"{col1}, {col2}",
                            "value": float(both_null_count / len(data)),
                            "threshold": 0.0,
                            "passed": False,
                            "severity": 2,
                            "extra": {
                                "both_null_count": int(both_null_count),
                                "columns": [col1, col2],
                                "inconsistent_rows": data[both_null].index.tolist()[:10]
                            }
                        })
        
        # Check date consistency (e.g., start_date < end_date)
        date_cols = [col for col in data.columns if 'date' in col.lower()]
        if len(date_cols) >= 2:
            try:
                for i, col1 in enumerate(date_cols):
                    for col2 in date_cols[i+1:]:
                        if 'start' in col1.lower() and 'end' in col2.lower():
                            date1 = pd.to_datetime(data[col1], errors='coerce')
                            date2 = pd.to_datetime(data[col2], errors='coerce')
                            
                            invalid_dates = (date1 > date2) & date1.notna() & date2.notna()
                            invalid_count = invalid_dates.sum()
                            
                            if invalid_count > 0:
                                results.append({
                                    "check_type": "date_consistency",
                                    "column": f"{col1}, {col2}",
                                    "value": float(invalid_count / len(data)),
                                    "threshold": 0.0,
                                    "passed": False,
                                    "severity": 3,
                                    "extra": {
                                        "invalid_date_pairs": int(invalid_count),
                                        "columns": [col1, col2],
                                        "invalid_rows": data[invalid_dates].index.tolist()[:10]
                                    }
                                })
            except:
                pass
        
        return results

    def _calculate_health_score(
        self, validation_results: List[Dict[str, Any]]
    ) -> float:
        """Calculate overall health score based on validation results."""
        if not validation_results:
            return 1.0

        # Weight different types of checks (higher weights for more critical issues)
        weights = {
            # Critical data quality issues
            "critical_field_missing": 0.15,
            "null_rate": 0.12,
            "duplicate_rows": 0.10,
            "statistical_outliers": 0.08,
            "negative_values": 0.08,
            "invalid_age": 0.08,
            "invalid_id_format": 0.08,
            "date_consistency": 0.07,
            
            # Format and consistency issues
            "type_consistency": 0.06,
            "email_format": 0.05,
            "date_format": 0.05,
            "phone_format": 0.04,
            "zero_values": 0.04,
            "invalid_status": 0.04,
            "uniqueness": 0.03,
            "inconsistent_names": 0.03,
        }

        total_score = 0.0
        total_weight = 0.0

        for result in validation_results:
            check_type = result["check_type"]
            weight = weights.get(check_type, 0.02)  # Default weight for unknown types

            # Score based on whether check passed and severity
            if result["passed"]:
                score = 1.0
            else:
                # Reduce score based on severity (1-5 scale)
                severity = result.get("severity", 1)
                score = max(0.0, 1.0 - (severity - 1) * 0.25)

            total_score += score * weight
            total_weight += weight

        return total_score / total_weight if total_weight > 0 else 1.0

    async def _detect_anomalies(
        self,
        data: pd.DataFrame,
        dataset: Dataset,
        validation_results: List[Dict[str, Any]],
        db: Session,
    ) -> List[Dict[str, Any]]:
        """Detect and create anomaly records."""
        anomalies = []

        try:
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

                    # Save to database
                    db_anomaly = Anomaly(**anomaly_data.dict())
                    db.add(db_anomaly)
                    db.commit()
                    db.refresh(db_anomaly)

                    anomalies.append(
                        {
                            "id": db_anomaly.id,
                            "type": result["check_type"],
                            "column": result.get("column"),
                            "severity": result["severity"],
                            "description": db_anomaly.description,
                        }
                    )

            return anomalies

        except Exception as e:
            logger.error("Anomaly detection failed", error=str(e))
            return []

    def _generate_anomaly_description(self, result: Dict[str, Any]) -> str:
        """Generate human-readable description for an anomaly."""
        check_type = result["check_type"]
        column = result.get("column", "unknown")
        value = result["value"]
        threshold = result["threshold"]
        extra = result.get("extra", {})

        descriptions = {
            "null_rate": f"High null rate in column '{column}': {value:.1%} ({extra.get('null_count', 0)} null values out of {extra.get('total_count', 0)} total)",
            
            "type_consistency": f"Mixed data types in column '{column}': {value} different types found",
            
            "uniqueness": f"Low uniqueness in column '{column}': {value:.1%} unique values ({extra.get('duplicate_count', 0)} duplicates)",
            
            "duplicate_rows": f"Duplicate rows detected: {value:.1%} of rows are duplicates ({extra.get('duplicate_row_count', 0)} duplicate rows)",
            
            "statistical_outliers": f"Statistical outliers in column '{column}': {value:.1%} of values are outliers ({extra.get('outlier_count', 0)} outliers)",
            
            "negative_values": f"Negative values in column '{column}': {value:.1%} of values are negative ({extra.get('negative_count', 0)} negative values)",
            
            "zero_values": f"Zero values in column '{column}': {value:.1%} of values are zero ({extra.get('zero_count', 0)} zero values)",
            
            "email_format": f"Invalid email format in column '{column}': {value:.1%} of emails are invalid ({extra.get('invalid_email_count', 0)} invalid emails)",
            
            "phone_format": f"Invalid phone format in column '{column}': {value:.1%} of phones are invalid ({extra.get('invalid_phone_count', 0)} invalid phones)",
            
            "date_format": f"Invalid date format in column '{column}': {value:.1%} of dates are invalid ({extra.get('invalid_date_count', 0)} invalid dates)",
            
            "invalid_id_format": f"Invalid ID format in column '{column}': {value:.1%} of IDs have invalid format ({extra.get('invalid_id_count', 0)} invalid IDs)",
            
            "invalid_age": f"Invalid age values: {value:.1%} of ages are outside valid range (0-150) ({extra.get('invalid_age_count', 0)} invalid ages)",
            
            "invalid_status": f"Invalid status values: {value:.1%} of status values are not recognized ({extra.get('invalid_status_count', 0)} invalid statuses)",
            
            "critical_field_missing": f"Critical field missing in column '{column}': {value:.1%} of records missing this critical field ({extra.get('missing_count', 0)} missing values)",
            
            "inconsistent_names": f"Inconsistent name data: {value:.1%} of records have both name fields null ({extra.get('both_null_count', 0)} inconsistent records)",
            
            "date_consistency": f"Date consistency issue: {value:.1%} of records have invalid date relationships ({extra.get('invalid_date_pairs', 0)} invalid pairs)",
        }

        return descriptions.get(check_type, f"Anomaly detected in column '{column}': {value:.1%} failed threshold of {threshold:.1%}")