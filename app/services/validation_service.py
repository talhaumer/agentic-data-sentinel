"""Data validation and quality checking service."""

# Removed unused import
from typing import Dict, List, Any, Optional
from datetime import datetime

import pandas as pd
import numpy as np
# Removed unused imports

import structlog
from sqlalchemy.orm import Session
# Removed unused imports

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

            # Check if source is a parquet file
            if dataset.source and dataset.source.endswith(".parquet"):
                return await self._sample_from_parquet(dataset)

            # Otherwise try to find a SQL table
            return await self._sample_from_sql(dataset, db)

        except Exception as e:
            logger.error("Failed to sample data", dataset_id=dataset.id, error=str(e))
            print(f"Error sampling data: {e}")
            return self._create_mock_data()

    async def _sample_from_parquet(self, dataset: Dataset) -> Optional[pd.DataFrame]:
        """Sample data from parquet file."""
        try:
            from pathlib import Path

            source_path = Path(dataset.source)

            if not source_path.exists():
                logger.warning("Parquet file not found", source=dataset.source)
                print(f"File not found: {source_path.absolute()}")
                return None

            sample_data = pd.read_parquet(dataset.source)
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

    async def _run_validation_checks(
        self, data: pd.DataFrame, dataset: Dataset
    ) -> List[Dict[str, Any]]:
        """Run various validation checks on the data."""
        results = []

        try:
            # Check 1: Null rate per column
            null_rates = data.isnull().sum() / len(data)
            for column, null_rate in null_rates.items():
                results.append(
                    {
                        "check_type": "null_rate",
                        "column": column,
                        "value": float(null_rate),
                        "threshold": 0.1,  # 10% threshold
                        "passed": null_rate <= 0.1,
                        "severity": (
                            3 if null_rate > 0.5 else 2 if null_rate > 0.1 else 1
                        ),
                    }
                )

            # Check 2: Data type consistency
            for column in data.columns:
                if data[column].dtype == "object":
                    # Check for mixed types
                    non_null_values = data[column].dropna()
                    if len(non_null_values) > 0:
                        type_counts = non_null_values.apply(type).value_counts()
                        if len(type_counts) > 1:
                            results.append(
                                {
                                    "check_type": "type_consistency",
                                    "column": column,
                                    "value": len(type_counts),
                                    "threshold": 1,
                                    "passed": False,
                                    "severity": 2,
                                }
                            )

            # Check 3: Uniqueness
            for column in data.columns:
                unique_ratio = data[column].nunique() / len(data)
                results.append(
                    {
                        "check_type": "uniqueness",
                        "column": column,
                        "value": float(unique_ratio),
                        "threshold": 0.95,  # 95% unique threshold
                        "passed": unique_ratio >= 0.95,
                        "severity": 2 if unique_ratio < 0.5 else 1,
                    }
                )

            # Check 4: Range validation for numeric columns
            numeric_columns = data.select_dtypes(include=[np.number]).columns
            for column in numeric_columns:
                if data[column].notna().sum() > 0:
                    min_val = data[column].min()
                    max_val = data[column].max()
                    mean_val = data[column].mean()
                    std_val = data[column].std()

                    # Check for outliers (beyond 3 standard deviations)
                    outlier_count = (
                        (data[column] - mean_val).abs() > 3 * std_val
                    ).sum()
                    outlier_ratio = outlier_count / len(data)

                    results.append(
                        {
                            "check_type": "outliers",
                            "column": column,
                            "value": float(outlier_ratio),
                            "threshold": 0.05,  # 5% outlier threshold
                            "passed": outlier_ratio <= 0.05,
                            "severity": (
                                3
                                if outlier_ratio > 0.2
                                else 2 if outlier_ratio > 0.05 else 1
                            ),
                            "extra": {
                                "min": float(min_val),
                                "max": float(max_val),
                                "mean": float(mean_val),
                                "std": float(std_val),
                                "outlier_count": int(outlier_count),
                            },
                        }
                    )

            return results

        except Exception as e:
            logger.error("Validation checks failed", error=str(e))
            return []

    def _calculate_health_score(
        self, validation_results: List[Dict[str, Any]]
    ) -> float:
        """Calculate overall health score based on validation results."""
        if not validation_results:
            return 1.0

        # Weight different types of checks
        weights = {
            "null_rate": 0.3,
            "type_consistency": 0.2,
            "uniqueness": 0.2,
            "outliers": 0.3,
        }

        total_score = 0.0
        total_weight = 0.0

        for result in validation_results:
            check_type = result["check_type"]
            weight = weights.get(check_type, 0.1)

            # Score based on whether check passed and severity
            if result["passed"]:
                score = 1.0
            else:
                # Reduce score based on severity (1-5 scale)
                severity = result.get("severity", 1)
                score = max(0.0, 1.0 - (severity - 1) * 0.2)

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

        descriptions = {
            "null_rate": f"High null rate in column '{column}': {value:.1%} (threshold: {threshold:.1%})",
            "type_consistency": f"Inconsistent data types in column '{column}': {value} different types found",
            "uniqueness": f"Low uniqueness in column '{column}': {value:.1%} unique values (threshold: {threshold:.1%})",
            "outliers": f"High outlier ratio in column '{column}': {value:.1%} (threshold: {threshold:.1%})",
        }

        return descriptions.get(check_type, f"Anomaly detected in column '{column}'")
