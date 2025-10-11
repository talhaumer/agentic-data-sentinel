"""Sample unit tests to demonstrate testing structure."""
import pytest
import pandas as pd


class TestSampleTests:
    """Sample test class."""
    
    def test_sample_dataframe_fixture(self, sample_dataframe):
        """Test that the sample dataframe fixture works."""
        assert isinstance(sample_dataframe, pd.DataFrame)
        assert len(sample_dataframe) == 10
        assert 'id' in sample_dataframe.columns
        assert 'value' in sample_dataframe.columns
        
    def test_sample_dataframe_with_anomalies(self, sample_dataframe_with_anomalies):
        """Test that the anomalies dataframe has expected values."""
        assert isinstance(sample_dataframe_with_anomalies, pd.DataFrame)
        assert sample_dataframe_with_anomalies.loc[3, 'value'] == 1000
        assert sample_dataframe_with_anomalies.loc[7, 'value'] == -500
        
    def test_basic_pandas_operations(self, sample_dataframe):
        """Test basic pandas operations."""
        # Test filtering
        category_a = sample_dataframe[sample_dataframe['category'] == 'A']
        assert len(category_a) == 5
        
        # Test aggregation
        mean_value = sample_dataframe['value'].mean()
        assert mean_value == 55.0
        
        # Test groupby
        grouped = sample_dataframe.groupby('category')['value'].sum()
        assert 'A' in grouped.index
        assert 'B' in grouped.index

