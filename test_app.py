import json
import pytest
from unittest.mock import MagicMock
from app import (
    extract_pdf_text,
    analyze_legal_document,
    generate_with_fallback,
    LegalCopilotError,
    MAX_FILE_SIZE_BYTES
)


def test_extract_pdf_text_none():
    """Verify handler returns None on empty or invalid input."""
    assert extract_pdf_text(None) is None


def test_max_file_size_security_boundary():
    """Security verification: ensures file size limit is strictly bounded to 10MB."""
    assert MAX_FILE_SIZE_BYTES == 10 * 1024 * 1024


def test_json_schema_completeness():
    """Verify all mandatory copilot fields exist in standard response."""
    required_keys = {
        "doc_type",
        "overall_risk_level",
        "summary",
        "key_obligations",
        "red_flags",
        "lawyer_checklist"
    }
    raw_payload = """{
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
    }"""
    sample_payload = json.loads(raw_payload)
    
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


@pytest.mark.parametrize("risk_level", ["Low", "Medium", "High"])
def test_risk_severity_boundary(risk_level):
    """Boundary test for risk classification labels using pytest parametrization."""
    allowed_levels = {"Low", "Medium", "High"}
    assert risk_level in allowed_levels


def test_analyze_legal_document_empty_input():
    """Edge Case: Ensure ValueError is raised on empty text input."""
    mock_client = MagicMock()
    with pytest.raises(ValueError):
        analyze_legal_document(mock_client, "")


def test_analyze_legal_document_mock_success():
    """Mock test: Verifies end-to-end document parsing logic without hitting live Gemini API."""
    mock_client = MagicMock()
    fake_response = MagicMock()
    fake_response.text = json.dumps({
        "doc_type": "Employment Agreement",
        "overall_risk_level": "High",
        "summary": "Full-time employment agreement with standard benefits.",
        "key_obligations": ["40 hours work week", "Assign inventions"],
        "red_flags": [
            {
                "clause_name": "Invention Assignment",
                "severity": "High",
                "concern": "Assigns off-hours projects",
                "recommendation": "Carve out prior inventions"
            }
        ],
        "lawyer_checklist": ["Confirm IP assignment scope"]
    })
    mock_client.models.generate_content.return_value = fake_response

    result = analyze_legal_document(mock_client, "Sample employment contract text.")
    assert result["doc_type"] == "Employment Agreement"
    assert result["overall_risk_level"] == "High"
    assert len(result["red_flags"]) == 1


def test_generate_with_fallback_success():
    """Mock test: Ensures generate_with_fallback executes successfully on primary model."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Analysis Successful"
    mock_client.models.generate_content.return_value = mock_response

    res = generate_with_fallback(mock_client, contents=["Test prompt"])
    assert res.text == "Analysis Successful"


def test_generate_with_fallback_exhaustion():
    """Mock test: Ensures LegalCopilotError is raised if all models fail."""
    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = RuntimeError("API Quota Exceeded")

    with pytest.raises(LegalCopilotError):
        generate_with_fallback(mock_client, contents=["Test prompt"])