"""Service layer tests."""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch

from app.services.validation_service import ValidationService
from app.services.llm_service import LLMService
from app.models import Dataset, Anomaly


class TestValidationService:
    """Test validation service functionality."""

    def test_calculate_health_score(self):
        """Test health score calculation."""
        service = ValidationService()

        # Test with all passed checks
        results = [
            {"check_type": "null_rate", "passed": True, "severity": 1},
            {"check_type": "uniqueness", "passed": True, "severity": 1},
        ]
        score = service._calculate_health_score(results)
        assert score == 1.0

        # Test with failed checks
        results = [
            {"check_type": "null_rate", "passed": False, "severity": 3},
            {"check_type": "uniqueness", "passed": True, "severity": 1},
        ]
        score = service._calculate_health_score(results)
        assert 0.0 < score < 1.0

        # Test with empty results
        score = service._calculate_health_score([])
        assert score == 1.0

    def test_generate_anomaly_description(self):
        """Test anomaly description generation."""
        service = ValidationService()

        result = {
            "check_type": "null_rate",
            "column": "price",
            "value": 0.15,
            "threshold": 0.1,
            "severity": 3,
        }

        description = service._generate_anomaly_description(result)
        assert "null rate" in description.lower()
        assert "price" in description
        assert "15%" in description

    @pytest.mark.asyncio
    async def test_run_validation_checks(self):
        """Test validation checks execution."""
        service = ValidationService()

        # Create sample data with known issues
        data = pd.DataFrame(
            {
                "price": [1.0, 2.0, None, 4.0, 5.0],  # 20% null rate
                "category": ["A", "B", "A", "B", "A"],  # Low uniqueness
                "amount": [100, 200, 300, 400, 500],  # Normal data
            }
        )

        dataset = Mock(spec=Dataset)
        dataset.name = "test_table"

        results = await service._run_validation_checks(data, dataset)

        assert len(results) > 0
        assert any(result["check_type"] == "null_rate" for result in results)
        assert any(result["check_type"] == "uniqueness" for result in results)


class TestLLMService:
    """Test LLM service functionality."""

    @pytest.mark.asyncio
    async def test_explain_anomaly(self):
        """Test anomaly explanation generation."""
        # Mock the LLM service to avoid API calls in tests
        with patch("app.services.llm_service.ChatOpenAI") as mock_llm:
            mock_llm.return_value.agenerate.return_value.generations = [
                [
                    Mock(
                        text='{"explanation": "Test explanation", "confidence": 0.8, "action_type": "notify_owner"}'
                    )
                ]
            ]

            service = LLMService()

            anomaly = Mock(spec=Anomaly)
            anomaly.id = 1
            anomaly.table_name = "test_table"
            anomaly.column_name = "price"
            anomaly.issue_type = "null_rate"
            anomaly.severity = 3
            anomaly.description = "High null rate"
            anomaly.detected_at = "2024-01-01T00:00:00Z"
            anomaly.extra = {}

            explanation = await service.explain_anomaly(anomaly)

            assert explanation.explanation == "Test explanation"
            assert explanation.confidence == 0.8
            assert explanation.action_type == "notify_owner"

    def test_parse_llm_response(self):
        """Test LLM response parsing."""
        service = LLMService()

        # Test valid JSON response
        response_text = (
            '{"explanation": "Test", "confidence": 0.9, "action_type": "auto_fix"}'
        )
        result = service._parse_llm_response(response_text)

        assert result.explanation == "Test"
        assert result.confidence == 0.9
        assert result.action_type == "auto_fix"

        # Test invalid JSON response
        response_text = "This is not JSON"
        result = service._parse_llm_response(response_text)

        assert result.explanation == "This is not JSON"
        assert result.confidence == 0.3  # Default low confidence
        assert result.action_type == "no_action"

    def test_build_explanation_prompt(self):
        """Test prompt building."""
        service = LLMService()

        context = {
            "anomaly_id": 1,
            "dataset_name": "test_table",
            "column_name": "price",
            "issue_type": "null_rate",
            "severity": 3,
            "description": "High null rate",
            "detected_at": "2024-01-01T00:00:00Z",
            "extra_data": {},
        }

        prompt = service._build_explanation_prompt(context)

        assert "test_table" in prompt
        assert "price" in prompt
        assert "null_rate" in prompt
        assert "JSON" in prompt
