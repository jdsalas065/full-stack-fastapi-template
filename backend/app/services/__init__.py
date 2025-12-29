"""
Services module for AI and OCR functionality.

This module provides reusable services for AI engineering tasks including:
- OCR (Optical Character Recognition) services
- Document conversion utilities
- Image processing tools
- LLM-based OCR and field extraction
- Document processing and comparison
- Storage services

Organization:
- ocr_tools.py: OCR and document processing functions (legacy)
- storage_service.py: MinIO storage with streaming
- llm_ocr_service.py: LLM-based OCR using GPT-4 Vision
- document_processor.py: Excel and PDF processing
- field_comparison_service.py: Field extraction and comparison
"""

from app.services.field_comparison_service import (
    field_comparison_service,
    FieldComparisonService,
)
from app.services.document_processor import (
    document_processor,
    DocumentProcessor,
)
from app.services.llm_ocr_service import (
    llm_ocr_service,
    LLMOCRService,
)
from app.services.storage_service import (
    storage_service,
    StorageService,
)
from app.services.ocr_tools import (
    base64_encode_image,
    convert_excel_to_pdf,
    convert_pdf_to_images,
    encode_image,
    extract_ocr_texts,
)

__all__ = [
    # Legacy OCR tools
    "base64_encode_image",
    "convert_excel_to_pdf",
    "convert_pdf_to_images",
    "encode_image",
    "extract_ocr_texts",
    # New services
    "storage_service",
    "StorageService",
    "llm_ocr_service",
    "LLMOCRService",
    "document_processor",
    "DocumentProcessor",
    "field_comparison_service",
    "FieldComparisonService",
]
