"""Pytest configuration and fixtures."""
import pytest
import pandas as pd
from pathlib import Path


@pytest.fixture
def sample_dataframe():
    """Create a sample DataFrame for testing."""
    return pd.DataFrame({
        'id': range(1, 11),
        'value': [10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
        'category': ['A', 'B', 'A', 'B', 'A', 'B', 'A', 'B', 'A', 'B'],
        'status': ['active'] * 10
    })


@pytest.fixture
def sample_dataframe_with_anomalies():
    """Create a DataFrame with known anomalies."""
    return pd.DataFrame({
        'id': range(1, 11),
        'value': [10, 20, 30, 1000, 50, 60, 70, -500, 90, 100],  # Anomalies at index 3 and 7
        'category': ['A', 'B', 'A', 'B', 'A', 'B', 'A', 'B', 'A', 'B'],
        'status': ['active'] * 10
    })


@pytest.fixture
def test_data_dir(tmp_path):
    """Create a temporary directory for test data."""
    data_dir = tmp_path / "test_data"
    data_dir.mkdir()
    return data_dir


@pytest.fixture
def sample_csv_file(test_data_dir, sample_dataframe):
    """Create a sample CSV file."""
    csv_path = test_data_dir / "sample.csv"
    sample_dataframe.to_csv(csv_path, index=False)
    return csv_path


@pytest.fixture
def sample_parquet_file(test_data_dir, sample_dataframe):
    """Create a sample Parquet file."""
    parquet_path = test_data_dir / "sample.parquet"
    sample_dataframe.to_parquet(parquet_path, index=False)
    return parquet_path


@pytest.fixture
def mock_llm_response():
    """Mock LLM response for testing."""
    return {
        "explanation": "This is a test explanation from the LLM.",
        "severity": "medium",
        "recommendations": ["Test recommendation 1", "Test recommendation 2"]
    }


@pytest.fixture(scope="session")
def test_config():
    """Test configuration."""
    return {
        "DATABASE_URL": "sqlite:///./test_sentinel.db",
        "LLM_PROVIDER": "openai",
        "DEBUG": True,
        "LOG_LEVEL": "debug"
    }

