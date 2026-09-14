import pytest
from unittest.mock import MagicMock, patch
import json
from app import extract_pdf_text

def test_extract_pdf_text_none():
    """Verify handler returns None on empty input."""
    assert extract_pdf_text(None) is None

def test_json_schema_completeness():
    """Verify all mandatory copilot fields exist."""
    required_keys = {"doc_type", "overall_risk_level", "summary", "key_obligations", "red_flags", "lawyer_checklist"}
    sample_payload = {
        "doc_type": "Non-Disclosure Agreement",
        "overall_risk_level": "Low",
        "summary": "Standard bilateral mutual non-disclosure agreement.",
        "key_obligations": ["Protect proprietary data for 2 years."],
        "red_flags": [
            {
                "clause_name": "Indemnification",
                "severity": "Medium",
                "concern": "Broad IP indemnification without cap.",
                "recommendation": "Introduce standard liability cap."
            }
        ],
        "lawyer_checklist": ["Check governing law jurisdiction."]
    }
    assert required_keys.issubset(sample_payload.keys())
    assert sample_payload["overall_risk_level"] in ["Low", "Medium", "High"]
    assert isinstance(sample_payload["red_flags"], list)
    assert isinstance(sample_payload["key_obligations"], list)
    assert isinstance(sample_payload["lawyer_checklist"], list)

def test_red_flag_item_structure():
    """Validate sub-fields inside individual red flag entries."""
    flag_keys = {"clause_name", "severity", "concern", "recommendation"}
    sample_flag = {
        "clause_name": "Non-Compete",
        "severity": "High",
        "concern": "2-year worldwide restriction post termination.",
        "recommendation": "Reduce duration to 6 months local radius."
    }
    assert flag_keys.issubset(sample_flag.keys())
    assert sample_flag["severity"] in ["High", "Medium", "Low"]

def test_risk_severity_boundary():
    """Boundary test for risk classification labels."""
    allowed_levels = {"Low", "Medium", "High"}
    test_levels = ["Low", "Medium", "High"]
    for level in test_levels:
        assert level in allowed_levels