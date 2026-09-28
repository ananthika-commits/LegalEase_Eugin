"""
API Routes for LegalEase Document Generation.
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from ai_core.gemini_generator import GeminiDocumentGenerator

router = APIRouter(tags=["Legal Document Generation"])

# Instantiate core generator
generator = GeminiDocumentGenerator()


class DocumentRequest(BaseModel):
    """Payload schema for generating legal documents."""
    document_type: str = Field(
        ...,
        min_length=2,
        max_length=150,
        description="Type of legal document (e.g. 'Employment Contract', 'NDA', 'Lease Agreement')",
        json_schema_extra={"example": "Freelance Work Contract"}
    )
    parties: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="Names and roles of involved parties",
        json_schema_extra={"example": "Jane Doe (Service Provider), TechNova Inc. (Client)"}
    )
    terms: str = Field(
        ...,
        min_length=5,
        description="Semicolon-separated contractual clauses and terms",
        json_schema_extra={"example": "Payment within 30 days of invoice; Provider agrees to deliver work by agreed deadline; Confidentiality must be maintained at all times; Either party may terminate with 15 days notice"}
    )
    dates: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Effective date of the agreement",
        json_schema_extra={"example": "April 10, 2025"}
    )


class DocumentResponse(BaseModel):
    """Response schema returned after document generation."""
    success: bool
    document_type: str
    content: str
    terms_list: List[str]
    parties: str
    effective_date: str
    model_used: str
    source: str
    generated_at: str


@router.get("/health", summary="Service Health and AI Core Status")
async def health_check():
    """Health check endpoint to verify backend service and AI model readiness."""
    return {
        "status": "healthy",
        "service": "LegalEase Backend API",
        "version": "1.0.0",
        "gemini_configured": generator.is_configured(),
        "model_target": generator.model_name,
        "timestamp": datetime.now().isoformat()
    }


@router.post(
    "/generate",
    response_model=DocumentResponse,
    summary="Generate Legal Document via Gemini AI",
    status_code=status.HTTP_200_OK
)
async def generate_document(req: DocumentRequest):
    """
    Accepts document type, parties, terms, and dates;
    routes through GeminiDocumentGenerator to produce structured legal document content.
    """
    # Validation
    if not req.document_type.strip():
        raise HTTPException(status_code=400, detail="Document type cannot be empty.")
    if not req.parties.strip():
        raise HTTPException(status_code=400, detail="Parties involved cannot be empty.")
    if not req.terms.strip():
        raise HTTPException(status_code=400, detail="Terms and conditions cannot be empty.")
    if not req.dates.strip():
        raise HTTPException(status_code=400, detail="Effective date cannot be empty.")

    try:
        # Re-check API key in case it was updated in .env dynamically
        if not generator.is_configured():
            generator.__init__()

        result = generator.generate_document(
            document_type=req.document_type.strip(),
            parties=req.parties.strip(),
            terms=req.terms.strip(),
            dates=req.dates.strip()
        )

        return DocumentResponse(
            success=result["success"],
            document_type=result["document_type"],
            content=result["content"],
            terms_list=result["terms_list"],
            parties=result["parties"],
            effective_date=result["effective_date"],
            model_used=result["model_used"],
            source=result.get("source", "gemini_api"),
            generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while generating the legal document: {str(e)}"
        )
