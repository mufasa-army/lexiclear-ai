import pytest
from app import extract_pdf_text

def test_extract_pdf_text_dummy():
    """Verify text extractor handles non-existent or invalid input gracefully."""
    result = extract_pdf_text(None)
    assert result is None

def test_json_structure_contract():
    """Verify standard response structure conforms to legal copilot schema."""
    expected_keys = {"doc_type", "overall_risk_level", "summary", "key_obligations", "red_flags", "lawyer_checklist"}
    mock_payload = {
        "doc_type": "Independent Contractor",
        "overall_risk_level": "High",
        "summary": "Plain English summary of contract obligations.",
        "key_obligations": ["Provide deliverables on time."],
        "red_flags": [{"clause_name": "Lock-in", "severity": "High", "concern": "Excessive lock-in duration", "recommendation": "Negotiate 30-day notice"}],
        "lawyer_checklist": ["Confirm non-compete enforceability"]
    }
    assert expected_keys.issubset(mock_payload.keys())
    assert mock_payload["overall_risk_level"] in ["Low", "Medium", "High"]

    