"""
Unit and integration tests for FastAPI backend routes:
- GET /
- GET /health
- POST /generate
"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_root_endpoint():
    """Verify root GET / returns 200 and welcoming metadata."""
    res = client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert "LegalEase" in data["message"]
    assert data["status"] == "online"
    assert "documentation" in data


def test_health_endpoint():
    """Verify health GET /health reports service and AI readiness."""
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "gemini_configured" in data
    assert "model_target" in data


def test_generate_document_success():
    """Verify document generation endpoint with valid parameters."""
    payload = {
        "document_type": "Non-Disclosure Agreement (NDA)",
        "parties": "Alpha Corp (Disclosing Party), Beta LLC (Receiving Party)",
        "terms": "Maintain confidentiality for 2 years; No unauthorized reproduction; Remedies include injunctive relief",
        "dates": "May 1, 2025"
    }
    res = client.post("/generate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["document_type"] == payload["document_type"]
    assert len(data["content"]) > 100
    assert "NON-DISCLOSURE" in data["content"].upper()
    assert len(data["terms_list"]) == 3
    assert data["parties"] == payload["parties"]
    assert data["effective_date"] == payload["dates"]


def test_generate_document_missing_fields():
    """Verify validation error when required fields are missing."""
    # Missing 'terms' and 'dates'
    payload = {
        "document_type": "Employment Contract",
        "parties": "Tech Corp, John Doe"
    }
    res = client.post("/generate", json=payload)
    assert res.status_code == 422  # Unprocessable Entity / validation error


def test_generate_document_empty_fields():
    """Verify validation error when fields are empty strings."""
    payload = {
        "document_type": " ",
        "parties": "Party A, Party B",
        "terms": "Term 1; Term 2",
        "dates": "2025-01-01"
    }
    res = client.post("/generate", json=payload)
    assert res.status_code in [400, 422]
