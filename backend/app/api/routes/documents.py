"""
API routes for document management and processing.

Endpoints for:
- Uploading documents
- Processing documents with OCR
- Comparing documents
- Retrieving document information
"""

import os
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.core.config import settings
from app.core.constants import Tags
from app.core.logging import get_logger
from app.crud.document import comparison_crud, document_crud
from app.models.document import Document, DocumentStatus, DocumentType
from app.schemas.document import (
    DocumentComparisonRequest,
    DocumentComparisonResponse,
    DocumentDetailResponse,
    DocumentListResponse,
    DocumentProcessRequest,
    DocumentProcessResponse,
    DocumentUploadResponse,
)
from app.services import comparison_service, ocr_service

logger = get_logger(__name__)

router = APIRouter(prefix="/documents", tags=[Tags.DOCUMENTS])


@router.post("/upload/", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    description: Optional[str] = None,
) -> DocumentUploadResponse:
    """
    Upload a document for processing.
    
    Accepts various document types including:
    - PDF files
    - Images (JPEG, PNG, TIFF)
    - Word documents
    
    The document will be stored and can then be processed with OCR.
    """
    # Validate file type
    if file.content_type not in settings.ALLOWED_DOCUMENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {settings.ALLOWED_DOCUMENT_TYPES}",
        )
    
    # Validate file size
    content = await file.read()
    file_size = len(content)
    max_size = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    
    if file_size > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE_MB}MB",
        )
    
    # Determine document type
    doc_type = DocumentType.OTHER
    if "pdf" in (file.content_type or ""):
        doc_type = DocumentType.PDF
    elif "image" in (file.content_type or ""):
        doc_type = DocumentType.IMAGE
    elif "word" in (file.content_type or "") or "document" in (file.content_type or ""):
        doc_type = DocumentType.WORD
    
    # Create storage directory if it doesn't exist
    storage_path = Path(settings.DOCUMENT_STORAGE_PATH)
    storage_path.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    timestamp = int(time.time())
    filename = f"{timestamp}_{file.filename}"
    file_path = storage_path / filename
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(content)
    
    logger.info(f"Saved document: {filename} ({file_size} bytes)")
    
    # Create document record
    document = Document(
        filename=file.filename or "unknown",
        file_path=str(file_path),
        file_type=doc_type,
        mime_type=file.content_type or "application/octet-stream",
        size_bytes=file_size,
        status=DocumentStatus.UPLOADED,
        uploaded_at=datetime.now(),
        description=description,
    )
    
    document = await document_crud.create(document)
    
    return DocumentUploadResponse(
        id=document.id or "",
        filename=document.filename,
        file_type=document.file_type,
        size_bytes=document.size_bytes,
        status=document.status,
        uploaded_at=document.uploaded_at,
    )


@router.post("/process/", response_model=DocumentProcessResponse)
async def process_document(
    request: DocumentProcessRequest,
) -> DocumentProcessResponse:
    """
    Process a document with OCR to extract text.
    
    This endpoint:
    1. Retrieves the uploaded document
    2. Performs OCR to extract text
    3. Updates the document with OCR results
    """
    # Get document
    document = await document_crud.get(request.document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    
    if document.status == DocumentStatus.PROCESSING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document is already being processed",
        )
    
    # Update status to processing
    await document_crud.update(
        request.document_id,
        status=DocumentStatus.PROCESSING,
    )
    
    try:
        # Perform OCR
        logger.info(f"Starting OCR for document: {request.document_id}")
        
        ocr_result = await ocr_service.extract_text(
            document.file_path,
            document.mime_type,
            request.language,
        )
        
        # Update document with OCR results
        await document_crud.update(
            request.document_id,
            ocr_text=ocr_result.text,
            ocr_confidence=ocr_result.confidence,
            status=DocumentStatus.COMPLETED,
            processed_at=datetime.now(),
        )
        
        logger.info(
            f"OCR completed for document: {request.document_id} "
            f"(confidence: {ocr_result.confidence})"
        )
        
        return DocumentProcessResponse(
            document_id=request.document_id,
            status=DocumentStatus.COMPLETED,
            ocr_text=ocr_result.text,
            ocr_confidence=ocr_result.confidence,
            processed_at=datetime.now(),
            message="Document processed successfully",
        )
        
    except Exception as e:
        logger.error(f"OCR failed for document {request.document_id}: {e}")
        
        await document_crud.update(
            request.document_id,
            status=DocumentStatus.FAILED,
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document processing failed: {str(e)}",
        )


@router.post("/compare/", response_model=DocumentComparisonResponse)
async def compare_documents(
    request: DocumentComparisonRequest,
) -> DocumentComparisonResponse:
    """
    Compare two documents for consistency and differences.
    
    This endpoint:
    1. Retrieves both documents
    2. Ensures both have been processed with OCR
    3. Performs text-based comparison
    4. Optionally uses AI (ChatGPT) for detailed analysis
    5. Returns comprehensive comparison results
    """
    # Get both documents
    document_1 = await document_crud.get(request.document_1_id)
    document_2 = await document_crud.get(request.document_2_id)
    
    if not document_1 or not document_2:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or both documents not found",
        )
    
    # Ensure both documents have been processed
    if document_1.status != DocumentStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Document 1 has not been processed. Status: {document_1.status}",
        )
    
    if document_2.status != DocumentStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Document 2 has not been processed. Status: {document_2.status}",
        )
    
    try:
        # Perform comparison
        logger.info(
            f"Comparing documents: {request.document_1_id} and {request.document_2_id}"
        )
        
        result = await comparison_service.compare_documents(
            document_1,
            document_2,
            use_ai_analysis=request.use_ai_analysis,
            comparison_prompt=request.comparison_prompt,
        )
        
        logger.info(
            f"Comparison completed: {result.comparison_id} "
            f"(similarity: {result.similarity_score})"
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Document comparison failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document comparison failed: {str(e)}",
        )


@router.get("/{document_id}/", response_model=DocumentDetailResponse)
async def get_document(document_id: str) -> DocumentDetailResponse:
    """
    Get detailed information about a document.
    
    Returns document metadata, processing status, and OCR results if available.
    """
    document = await document_crud.get(document_id)
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    
    return DocumentDetailResponse(
        id=document.id or "",
        filename=document.filename,
        file_type=document.file_type,
        mime_type=document.mime_type,
        size_bytes=document.size_bytes,
        status=document.status,
        uploaded_at=document.uploaded_at,
        processed_at=document.processed_at,
        ocr_text=document.ocr_text,
        ocr_confidence=document.ocr_confidence,
        description=document.description,
        tags=document.tags,
    )


@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    page: int = 1,
    page_size: int = 20,
    status: Optional[DocumentStatus] = None,
) -> DocumentListResponse:
    """
    List documents with pagination.
    
    Optionally filter by processing status.
    """
    if page < 1:
        page = 1
    if page_size < 1 or page_size > 100:
        page_size = 20
    
    skip = (page - 1) * page_size
    
    documents = await document_crud.list(skip=skip, limit=page_size, status=status)
    
    document_responses = [
        DocumentDetailResponse(
            id=doc.id or "",
            filename=doc.filename,
            file_type=doc.file_type,
            mime_type=doc.mime_type,
            size_bytes=doc.size_bytes,
            status=doc.status,
            uploaded_at=doc.uploaded_at,
            processed_at=doc.processed_at,
            ocr_text=doc.ocr_text,
            ocr_confidence=doc.ocr_confidence,
            description=doc.description,
            tags=doc.tags,
        )
        for doc in documents
    ]
    
    # Get total count (in production, this would be a separate query)
    all_documents = await document_crud.list(skip=0, limit=10000, status=status)
    total = len(all_documents)
    
    return DocumentListResponse(
        documents=document_responses,
        total=total,
        page=page,
        page_size=page_size,
    )
