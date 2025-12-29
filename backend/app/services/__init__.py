"""
Services module for AI and OCR functionality.

This module provides reusable services for AI engineering tasks including:
- OCR (Optical Character Recognition) services
- Document conversion utilities
- Image processing tools
- Future AI services can be added here

Organization:
- ocr_tools.py: OCR and document processing functions
- Add more services as needed (e.g., nlp_tools.py, vision_tools.py)
"""

from app.services.ocr_tools import (
    base64_encode_image,
    convert_excel_to_pdf,
    convert_pdf_to_images,
    encode_image,
    extract_ocr_texts,
)

__all__ = [
    "base64_encode_image",
    "convert_excel_to_pdf",
    "convert_pdf_to_images",
    "encode_image",
    "extract_ocr_texts",
]
