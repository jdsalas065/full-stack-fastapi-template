"""
Document processing service.

Processes Excel and PDF files to extract structured data.
Uses pandas/openpyxl for Excel and LLM OCR for PDF.
"""

import asyncio
from io import BytesIO
from pathlib import Path
from typing import Any

import fitz  # PyMuPDF
import pandas as pd
from PIL import Image

from app.core.logging import get_logger
from app.services.llm_ocr_service import llm_ocr_service

logger = get_logger(__name__)


class DocumentProcessor:
    """Process documents (Excel/PDF) and extract structured data."""

    async def process_file(
        self,
        file_stream: BytesIO,
        file_name: str,
        file_type: str | None = None,
    ) -> dict[str, Any]:
        """
        Process a single file and extract structured data.
        
        DEPRECATED: Use process_file_from_path instead.

        Args:
            file_stream: File content as BytesIO
            file_name: Original file name
            file_type: 'excel' or 'pdf' (auto-detect if None)

        Returns:
            Dictionary with:
            - file_name
            - file_type
            - extracted_data: Structured data
            - text: Full text content
            - fields: Extracted fields
        """
        # Auto-detect file type
        if file_type is None:
            file_type = self.detect_file_type(file_name)

        if file_type == "excel":
            return await self._process_excel(file_stream, file_name)
        elif file_type == "pdf":
            return await self._process_pdf(file_stream, file_name)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

    async def process_file_from_path(
        self,
        file_path: str,
        file_name: str | None = None,
        file_type: str | None = None,
    ) -> dict[str, Any]:
        """
        Process a single file from local path and extract structured data.

        Args:
            file_path: Path to local file
            file_name: Original file name (use Path basename if None)
            file_type: 'excel', 'pdf', 'doc', 'docx', or 'image' (auto-detect if None)

        Returns:
            Dictionary with:
            - file_name
            - file_type
            - extracted_data: Structured data
            - text: Full text content
            - fields: Extracted fields
        """
        if file_name is None:
            file_name = Path(file_path).name
            
        # Auto-detect file type
        if file_type is None:
            file_type = self.detect_file_type(file_name)

        if file_type == "excel":
            return await self._process_excel_from_path(file_path, file_name)
        elif file_type == "pdf":
            return await self._process_pdf_from_path(file_path, file_name)
        elif file_type in ["doc", "docx"]:
            return await self._process_doc_from_path(file_path, file_name)
        elif file_type == "image":
            return await self._process_image_from_path(file_path, file_name)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

    def detect_file_type(self, file_name: str) -> str:
        """
        Detect file type from extension.

        Args:
            file_name: File name with extension

        Returns:
            'excel', 'pdf', 'doc', 'docx', or 'image'

        Raises:
            ValueError: If file type cannot be detected
        """
        ext = Path(file_name).suffix.lower()
        if ext in [".xlsx", ".xls"]:
            return "excel"
        elif ext == ".pdf":
            return "pdf"
        elif ext in [".doc", ".docx"]:
            return "docx"
        elif ext in [".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".gif"]:
            return "image"
        else:
            raise ValueError(f"Cannot detect file type for: {file_name}")

    async def _process_excel(
        self,
        file_stream: BytesIO,
        file_name: str,
    ) -> dict[str, Any]:
        """
        Process Excel file and extract structured data.
        
        DEPRECATED: Use _process_excel_from_path instead.

        Args:
            file_stream: Excel file content as BytesIO
            file_name: Original file name

        Returns:
            Dictionary with extracted data and fields
        """

        # Read Excel (blocking operation, run in thread)
        def read_excel():
            file_stream.seek(0)
            # Try to read all sheets
            try:
                excel_file = pd.ExcelFile(file_stream, engine="openpyxl")
                sheets_data = {}
                for sheet_name in excel_file.sheet_names:
                    df = pd.read_excel(excel_file, sheet_name=sheet_name)
                    sheets_data[sheet_name] = df.to_dict("records")
                return sheets_data
            except Exception as e:
                logger.error(f"Error reading Excel: {e}")
                raise

        sheets_data = await asyncio.to_thread(read_excel)

        # Extract fields from structured data
        fields = self._extract_fields_from_excel(sheets_data)

        return {
            "file_name": file_name,
            "file_type": "excel",
            "extracted_data": sheets_data,
            "text": self._excel_to_text(sheets_data),
            "fields": fields,
        }

    async def _process_excel_from_path(
        self,
        file_path: str,
        file_name: str,
    ) -> dict[str, Any]:
        """
        Process Excel file from path and extract structured data.

        Args:
            file_path: Path to Excel file
            file_name: Original file name

        Returns:
            Dictionary with extracted data and fields
        """
        # Read Excel (blocking operation, run in thread)
        def read_excel():
            try:
                excel_file = pd.ExcelFile(file_path, engine="openpyxl")
                sheets_data = {}
                for sheet_name in excel_file.sheet_names:
                    df = pd.read_excel(excel_file, sheet_name=sheet_name)
                    sheets_data[sheet_name] = df.to_dict("records")
                return sheets_data
            except Exception as e:
                logger.error(f"Error reading Excel from {file_path}: {e}")
                raise

        sheets_data = await asyncio.to_thread(read_excel)

        # Extract fields from structured data
        fields = self._extract_fields_from_excel(sheets_data)

        return {
            "file_name": file_name,
            "file_type": "excel",
            "extracted_data": sheets_data,
            "text": self._excel_to_text(sheets_data),
            "fields": fields,
        }

    async def _process_pdf(
        self,
        file_stream: BytesIO,
        file_name: str,
    ) -> dict[str, Any]:
        """
        Process PDF file using LLM OCR.
        
        DEPRECATED: Use _process_pdf_from_path instead.

        Args:
            file_stream: PDF file content as BytesIO
            file_name: Original file name

        Returns:
            Dictionary with extracted data and fields
        """

        # Convert PDF to images (blocking, run in thread)
        def pdf_to_images():
            file_stream.seek(0)
            pdf_bytes = file_stream.read()
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            images = []
            for page_num in range(len(doc)):
                page = doc[page_num]
                pix = page.get_pixmap(dpi=200)  # 200 DPI for good quality
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                images.append(img)
            doc.close()
            return images

        images = await asyncio.to_thread(pdf_to_images)
        logger.info(f"Converted PDF to {len(images)} images")

        # Extract text and fields using LLM OCR
        ocr_results = await llm_ocr_service.extract_from_images(
            images,
            extract_fields=True,
        )

        # Combine results from all pages
        full_text = "\n\n".join([r["text"] for r in ocr_results])
        combined_fields = self._combine_fields([r["fields"] for r in ocr_results])

        return {
            "file_name": file_name,
            "file_type": "pdf",
            "extracted_data": ocr_results,
            "text": full_text,
            "fields": combined_fields,
            "page_count": len(images),
        }

    async def _process_pdf_from_path(
        self,
        file_path: str,
        file_name: str,
    ) -> dict[str, Any]:
        """
        Process PDF file from path using LLM OCR.

        Args:
            file_path: Path to PDF file
            file_name: Original file name

        Returns:
            Dictionary with extracted data and fields
        """
        # Convert PDF to images (blocking, run in thread)
        def pdf_to_images():
            doc = fitz.open(file_path)
            images = []
            for page_num in range(len(doc)):
                page = doc[page_num]
                pix = page.get_pixmap(dpi=200)  # 200 DPI for good quality
                img = Image.frombytes(
                    "RGB", [pix.width, pix.height], pix.samples
                )
                images.append(img)
            doc.close()
            return images

        images = await asyncio.to_thread(pdf_to_images)
        logger.info(f"Converted PDF to {len(images)} images")

        # Extract text and fields using LLM OCR
        ocr_results = await llm_ocr_service.extract_from_images(
            images,
            extract_fields=True,
        )

        # Combine results from all pages
        full_text = "\n\n".join([r["text"] for r in ocr_results])
        combined_fields = self._combine_fields(
            [r["fields"] for r in ocr_results]
        )

        return {
            "file_name": file_name,
            "file_type": "pdf",
            "extracted_data": ocr_results,
            "text": full_text,
            "fields": combined_fields,
            "page_count": len(images),
        }

    async def _process_doc_from_path(
        self,
        file_path: str,
        file_name: str,
    ) -> dict[str, Any]:
        """
        Process DOC/DOCX file from path.
        
        Note: Basic implementation. For production, consider python-docx library.

        Args:
            file_path: Path to DOC/DOCX file
            file_name: Original file name

        Returns:
            Dictionary with extracted data and fields
        """
        # For now, treat as unsupported - would need python-docx
        logger.warning(f"DOC/DOCX processing not fully implemented for {file_name}")
        return {
            "file_name": file_name,
            "file_type": "docx",
            "extracted_data": {},
            "text": "",
            "fields": {},
            "note": "DOC/DOCX processing requires additional library (python-docx)",
        }

    async def _process_image_from_path(
        self,
        file_path: str,
        file_name: str,
    ) -> dict[str, Any]:
        """
        Process image file from path using LLM OCR.

        Args:
            file_path: Path to image file
            file_name: Original file name

        Returns:
            Dictionary with extracted data and fields
        """
        # Load image (blocking, run in thread)
        def load_image():
            return Image.open(file_path).convert("RGB")

        image = await asyncio.to_thread(load_image)
        logger.info(f"Loaded image {file_name}")

        # Extract text and fields using LLM OCR
        ocr_results = await llm_ocr_service.extract_from_images(
            [image],
            extract_fields=True,
        )

        # Get first result (single image)
        result = ocr_results[0] if ocr_results else {"text": "", "fields": {}}

        return {
            "file_name": file_name,
            "file_type": "image",
            "extracted_data": result,
            "text": result.get("text", ""),
            "fields": result.get("fields", {}),
        }

    def _extract_fields_from_excel(
        self, sheets_data: dict[str, list[dict[str, Any]]]
    ) -> dict[str, Any]:
        """
        Extract common fields from Excel data.

        Args:
            sheets_data: Dictionary of sheet names to records

        Returns:
            Dictionary of extracted fields
        """
        # This is a simplified version
        # In production, you might use LLM to identify field mappings
        fields = {
            "amounts": [],
            "dates": [],
            "line_items": [],
            "references": [],
        }

        # Extract from all sheets
        for _sheet_name, records in sheets_data.items():
            for record in records:
                # Simple field extraction (can be enhanced with LLM)
                for key, value in record.items():
                    if isinstance(value, (int, float)):
                        if "amount" in key.lower() or "total" in key.lower():
                            fields["amounts"].append(value)
                    # Add more field extraction logic

        return fields

    def _combine_fields(self, fields_list: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Combine fields from multiple pages.

        Args:
            fields_list: List of field dictionaries

        Returns:
            Combined fields dictionary
        """
        combined = {
            "amounts": [],
            "dates": [],
            "line_items": [],
            "references": [],
        }

        for fields in fields_list:
            for key, values in fields.items():
                if key in combined and isinstance(values, list):
                    combined[key].extend(values)

        return combined

    def _excel_to_text(self, sheets_data: dict[str, list[dict[str, Any]]]) -> str:
        """
        Convert Excel data to text representation.

        Args:
            sheets_data: Dictionary of sheet names to records

        Returns:
            Text representation of Excel data
        """
        text_parts = []
        for sheet_name, records in sheets_data.items():
            text_parts.append(f"Sheet: {sheet_name}")
            for record in records:
                text_parts.append(str(record))
        return "\n".join(text_parts)


# Singleton instance
document_processor = DocumentProcessor()
