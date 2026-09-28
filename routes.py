from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ai_core.gemini_generator import (
    GeminiDocumentGenerator
)

from utils.text_utils import sanitize_text


router = APIRouter()


class DocumentRequest(BaseModel):

    document_type: str = Field(
        ...,
        min_length=2,
        max_length=100
    )

    parties: str = Field(
        ...,
        min_length=2,
        max_length=3000
    )

    terms: str = Field(
        ...,
        min_length=2,
        max_length=10000
    )

    effective_date: str = Field(
        ...,
        min_length=2,
        max_length=100
    )


class DocumentResponse(BaseModel):

    success: bool
    document_type: str
    generated_text: str


@router.post(
    "/generate",
    response_model=DocumentResponse
)
def generate_document(
    request: DocumentRequest
):

    try:

        generator = GeminiDocumentGenerator()

        generated_text = generator.generate_document(
            document_type=request.document_type,
            parties=request.parties,
            terms=request.terms,
            effective_date=request.effective_date,
        )

        generated_text = sanitize_text(
            generated_text
        )

        return DocumentResponse(
            success=True,
            document_type=request.document_type,
            generated_text=generated_text,
        )

    except ValueError as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to generate the document. "
                f"Error: {error}"
            )
        )