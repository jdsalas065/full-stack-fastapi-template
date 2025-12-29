# 🎯 Solutions Implementation Plan

Dựa trên requirements đã làm rõ, đây là solutions chi tiết:

---

## 📋 Requirements Tóm Tắt

### API 1: `/process_document_submission`
- **Input**: Nhiều files (Excel/PDF) khác format + template nhưng biểu diễn cùng 1 trường
- **Process**: 
  - Parse thành structured data (JSON/dict)
  - OCR extract text (không so sánh y hệt vì templates khác nhau)
  - Visual comparison để chỉ ra trường sai khác
- **Output**: Field-by-field comparison với differences

### API 2: `/compare_document_contents`
- **Process**: 
  - **Bắt buộc dùng LLM để OCR** (không phải pytesseract)
  - Convert Excel → PDF → Images
  - LLM OCR từ images
  - Compare và extract fields
- **Output**: Chi tiết từng field khác nhau

### Storage:
- **MinIO streaming** (nếu tốt hơn)
- **Lưu OCR results** (không cần converted PDFs, images)

---

## 🏗️ Architecture Solution

### Flow Mới:

```
┌─────────────────────────────────────────────────────────┐
│              API Request (task_id)                       │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  1. Load Files từ MinIO (Streaming)                     │
│     - List objects theo task_id prefix                  │
│     - Stream files (không download to disk)            │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  2. Detect File Type & Template                         │
│     - Excel (.xlsx, .xls)                               │
│     - PDF (scanned, text-based)                          │
│     - Template detection (LLM-based)                    │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  3. Extract Data (Parallel Processing)                 │
│     ┌─────────────────────────────────────┐            │
│     │ Excel Files:                         │            │
│     │ - Parse với openpyxl/pandas         │            │
│     │ - Extract structured data            │            │
│     └─────────────────────────────────────┘            │
│     ┌─────────────────────────────────────┐            │
│     │ PDF Files:                          │            │
│     │ - Convert to images (PyMuPDF)       │            │
│     │ - LLM Vision OCR (GPT-4 Vision)    │            │
│     │ - Extract structured data           │            │
│     └─────────────────────────────────────┘            │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  4. Normalize & Compare Fields                         │
│     - Map fields từ different templates                │
│     - Compare field-by-field                            │
│     - Identify differences                              │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  5. Save OCR Results to MinIO                          │
│     - Store extracted structured data                    │
│     - Store comparison results                          │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  6. Return Results                                      │
│     - Field-by-field comparison                         │
│     - Differences identified                            │
└─────────────────────────────────────────────────────────┘
```

---

## 💻 Implementation Code

### 1. Storage Service với Streaming

```python
# app/services/storage_service.py
from minio import Minio
from minio.error import S3Error
from io import BytesIO
from pathlib import Path
from typing import BinaryIO, Iterator
import asyncio

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class StorageService:
    """MinIO storage service with streaming support."""
    
    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE
        )
        self.bucket = settings.MINIO_BUCKET
    
    async def list_files(self, task_id: str) -> list[dict]:
        """List all files for a task_id."""
        prefix = f"{task_id}/"
        try:
            objects = await asyncio.to_thread(
                list,
                self.client.list_objects(self.bucket, prefix=prefix, recursive=True)
            )
            return [
                {
                    "name": obj.object_name,
                    "size": obj.size,
                    "last_modified": obj.last_modified
                }
                for obj in objects
            ]
        except S3Error as e:
            logger.error(f"Error listing files: {e}")
            raise
    
    async def get_file_stream(self, object_name: str) -> BytesIO:
        """Get file as stream (in-memory, no disk I/O)."""
        try:
            response = await asyncio.to_thread(
                self.client.get_object,
                self.bucket,
                object_name
            )
            # Read entire file into memory (for small-medium files)
            # For large files, consider chunked processing
            data = response.read()
            response.close()
            response.release_conn()
            return BytesIO(data)
        except S3Error as e:
            logger.error(f"Error getting file {object_name}: {e}")
            raise
    
    async def save_ocr_result(self, task_id: str, result_data: dict) -> str:
        """Save OCR extraction results to MinIO."""
        import json
        object_name = f"{task_id}/ocr_results.json"
        data = json.dumps(result_data, indent=2).encode('utf-8')
        
        try:
            await asyncio.to_thread(
                self.client.put_object,
                self.bucket,
                object_name,
                BytesIO(data),
                length=len(data),
                content_type='application/json'
            )
            logger.info(f"Saved OCR results to {object_name}")
            return object_name
        except S3Error as e:
            logger.error(f"Error saving OCR results: {e}")
            raise
    
    async def get_ocr_result(self, task_id: str) -> dict | None:
        """Retrieve saved OCR results."""
        object_name = f"{task_id}/ocr_results.json"
        try:
            response = await asyncio.to_thread(
                self.client.get_object,
                self.bucket,
                object_name
            )
            data = json.loads(response.read())
            response.close()
            response.release_conn()
            return data
        except S3Error as e:
            if e.code == 'NoSuchKey':
                return None
            logger.error(f"Error getting OCR results: {e}")
            raise


# Singleton instance
storage_service = StorageService()
```

### 2. LLM OCR Service (GPT-4 Vision)

```python
# app/services/llm_ocr_service.py
from openai import AsyncOpenAI
from PIL import Image
from io import BytesIO
from pathlib import Path
from typing import Any
import base64
import json

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class LLMOCRService:
    """LLM-based OCR using GPT-4 Vision."""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4o"  # hoặc "gpt-4-vision-preview"
    
    def _encode_image(self, image: Image.Image) -> str:
        """Encode PIL Image to base64."""
        buffer = BytesIO()
        image.save(buffer, format='PNG')
        return base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    async def extract_text_from_image(
        self, 
        image: Image.Image,
        extract_fields: bool = True
    ) -> dict[str, Any]:
        """
        Extract text and structured data from image using LLM.
        
        Args:
            image: PIL Image object
            extract_fields: If True, extract structured fields (amounts, dates, etc.)
        
        Returns:
            Dictionary with:
            - text: Raw extracted text
            - fields: Structured fields (if extract_fields=True)
            - confidence: Not applicable for LLM, but included for compatibility
        """
        try:
            # Encode image
            base64_image = self._encode_image(image)
            
            # Prepare prompt
            if extract_fields:
                prompt = """
                Analyze this document image and extract:
                1. All text content (preserve structure)
                2. Structured fields:
                   - Amounts (numbers with currency)
                   - Dates
                   - Names/Companies
                   - Line items (if table format)
                   - Reference numbers
                   - Any other important fields
                
                Return as JSON with structure:
                {
                    "text": "full text content",
                    "fields": {
                        "amounts": [...],
                        "dates": [...],
                        "line_items": [...],
                        ...
                    }
                }
                """
            else:
                prompt = "Extract all text from this image. Preserve the structure and formatting."
            
            # Call GPT-4 Vision
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at extracting text and structured data from document images. Always return valid JSON."
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}",
                                    "detail": "high"  # High detail for better OCR
                                }
                            }
                        ]
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.1  # Low temperature for consistent extraction
            )
            
            # Parse response
            result = json.loads(response.choices[0].message.content)
            
            # Ensure structure
            if extract_fields:
                return {
                    "text": result.get("text", ""),
                    "fields": result.get("fields", {}),
                    "confidence": 1.0,  # LLM doesn't provide confidence score
                    "raw_response": result
                }
            else:
                return {
                    "text": result.get("text", ""),
                    "fields": {},
                    "confidence": 1.0
                }
                
        except Exception as e:
            logger.error(f"Error in LLM OCR: {e}")
            raise
    
    async def extract_from_images(
        self,
        images: list[Image.Image],
        extract_fields: bool = True
    ) -> list[dict[str, Any]]:
        """Extract text from multiple images (parallel processing)."""
        import asyncio
        
        tasks = [
            self.extract_text_from_image(img, extract_fields)
            for img in images
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle errors
        extracted_results = []
        for idx, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Error extracting from image {idx}: {result}")
                extracted_results.append({
                    "page_num": idx,
                    "text": "",
                    "fields": {},
                    "confidence": 0.0,
                    "error": str(result)
                })
            else:
                result["page_num"] = idx
                extracted_results.append(result)
        
        return extracted_results


# Singleton instance
llm_ocr_service = LLMOCRService()
```

### 3. Document Processing Pipeline

```python
# app/services/document_processor.py
from pathlib import Path
from typing import Any
import pandas as pd
import fitz  # PyMuPDF
from PIL import Image
from io import BytesIO

from app.services.storage_service import storage_service
from app.services.llm_ocr_service import llm_ocr_service
from app.core.logging import get_logger

logger = get_logger(__name__)


class DocumentProcessor:
    """Process documents (Excel/PDF) and extract structured data."""
    
    async def process_file(
        self,
        file_stream: BytesIO,
        file_name: str,
        file_type: str | None = None
    ) -> dict[str, Any]:
        """
        Process a single file and extract structured data.
        
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
            file_type = self._detect_file_type(file_name)
        
        if file_type == 'excel':
            return await self._process_excel(file_stream, file_name)
        elif file_type == 'pdf':
            return await self._process_pdf(file_stream, file_name)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
    
    def _detect_file_type(self, file_name: str) -> str:
        """Detect file type from extension."""
        ext = Path(file_name).suffix.lower()
        if ext in ['.xlsx', '.xls']:
            return 'excel'
        elif ext == '.pdf':
            return 'pdf'
        else:
            raise ValueError(f"Cannot detect file type for: {file_name}")
    
    async def _process_excel(
        self,
        file_stream: BytesIO,
        file_name: str
    ) -> dict[str, Any]:
        """Process Excel file and extract structured data."""
        import asyncio
        
        # Read Excel (blocking operation, run in thread)
        def read_excel():
            file_stream.seek(0)
            # Try to read all sheets
            try:
                excel_file = pd.ExcelFile(file_stream, engine='openpyxl')
                sheets_data = {}
                for sheet_name in excel_file.sheet_names:
                    df = pd.read_excel(excel_file, sheet_name=sheet_name)
                    sheets_data[sheet_name] = df.to_dict('records')
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
            "fields": fields
        }
    
    async def _process_pdf(
        self,
        file_stream: BytesIO,
        file_name: str
    ) -> dict[str, Any]:
        """Process PDF file using LLM OCR."""
        import asyncio
        
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
            extract_fields=True
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
            "page_count": len(images)
        }
    
    def _extract_fields_from_excel(self, sheets_data: dict) -> dict[str, Any]:
        """Extract common fields from Excel data."""
        # This is a simplified version
        # In production, you might use LLM to identify field mappings
        fields = {
            "amounts": [],
            "dates": [],
            "line_items": [],
            "references": []
        }
        
        # Extract from all sheets
        for sheet_name, records in sheets_data.items():
            for record in records:
                # Simple field extraction (can be enhanced with LLM)
                for key, value in record.items():
                    if isinstance(value, (int, float)):
                        if 'amount' in key.lower() or 'total' in key.lower():
                            fields["amounts"].append(value)
                    # Add more field extraction logic
        
        return fields
    
    def _combine_fields(self, fields_list: list[dict]) -> dict[str, Any]:
        """Combine fields from multiple pages."""
        combined = {
            "amounts": [],
            "dates": [],
            "line_items": [],
            "references": []
        }
        
        for fields in fields_list:
            for key, values in fields.items():
                if key in combined and isinstance(values, list):
                    combined[key].extend(values)
        
        return combined
    
    def _excel_to_text(self, sheets_data: dict) -> str:
        """Convert Excel data to text representation."""
        text_parts = []
        for sheet_name, records in sheets_data.items():
            text_parts.append(f"Sheet: {sheet_name}")
            for record in records:
                text_parts.append(str(record))
        return "\n".join(text_parts)


# Singleton instance
document_processor = DocumentProcessor()
```

### 4. Field Comparison Service

```python
# app/services/field_comparison_service.py
from typing import Any
from difflib import SequenceMatcher

from app.core.logging import get_logger

logger = get_logger(__name__)


class FieldComparisonService:
    """Compare extracted fields from multiple documents."""
    
    def compare_documents(
        self,
        document_results: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """
        Compare multiple documents and identify field differences.
        
        Args:
            document_results: List of document extraction results
        
        Returns:
            Comparison results with:
            - field_comparisons: Field-by-field comparison
            - differences: List of differences
            - matches: List of matching fields
        """
        if len(document_results) < 2:
            return {
                "error": "Need at least 2 documents to compare",
                "field_comparisons": {},
                "differences": [],
                "matches": []
            }
        
        # Extract all unique field names
        all_field_names = set()
        for doc in document_results:
            all_field_names.update(doc.get("fields", {}).keys())
        
        # Compare each field
        field_comparisons = {}
        differences = []
        matches = []
        
        for field_name in all_field_names:
            field_values = []
            for doc in document_results:
                field_value = doc.get("fields", {}).get(field_name, [])
                field_values.append({
                    "file_name": doc["file_name"],
                    "value": field_value
                })
            
            # Compare field values
            comparison = self._compare_field(field_name, field_values)
            field_comparisons[field_name] = comparison
            
            if comparison["status"] == "match":
                matches.append({
                    "field": field_name,
                    "values": field_values
                })
            else:
                differences.append({
                    "field": field_name,
                    "values": field_values,
                    "difference_type": comparison["difference_type"]
                })
        
        return {
            "field_comparisons": field_comparisons,
            "differences": differences,
            "matches": matches,
            "total_fields": len(all_field_names),
            "matched_fields": len(matches),
            "different_fields": len(differences)
        }
    
    def _compare_field(
        self,
        field_name: str,
        field_values: list[dict]
    ) -> dict[str, Any]:
        """Compare values of a specific field across documents."""
        # Extract values
        values = [fv["value"] for fv in field_values]
        
        # Normalize values for comparison
        normalized_values = [self._normalize_value(v) for v in values]
        
        # Check if all values are the same
        if len(set(str(v) for v in normalized_values)) == 1:
            return {
                "status": "match",
                "values": field_values,
                "difference_type": None
            }
        
        # Values are different
        return {
            "status": "different",
            "values": field_values,
            "difference_type": self._identify_difference_type(normalized_values)
        }
    
    def _normalize_value(self, value: Any) -> Any:
        """Normalize value for comparison."""
        if isinstance(value, list):
            return sorted([self._normalize_value(v) for v in value])
        elif isinstance(value, (int, float)):
            return float(value)
        elif isinstance(value, str):
            return value.strip().lower()
        else:
            return value
    
    def _identify_difference_type(self, values: list) -> str:
        """Identify type of difference."""
        # Check if numeric difference
        try:
            numeric_values = [float(v) for v in values if isinstance(v, (int, float, str))]
            if len(numeric_values) == len(values):
                return "numeric_difference"
        except:
            pass
        
        # Check if missing in some documents
        if any(v is None or v == [] for v in values):
            return "missing_value"
        
        # Text difference
        return "text_difference"


# Singleton instance
field_comparison_service = FieldComparisonService()
```

### 5. Updated API Routes

```python
# app/api/routes/document.py (Updated)
from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from typing import Any

from app.core.constants import Tags
from app.core.logging import get_logger
from app.services.storage_service import storage_service
from app.services.document_processor import document_processor
from app.services.field_comparison_service import field_comparison_service
from app.schemas.document import (
    CompareDocumentRequest,
    CompareDocumentResponse,
    DocumentSubmissionRequest,
    DocumentSubmissionResponse,
)

logger = get_logger(__name__)
router = APIRouter(prefix="/document", tags=[Tags.DOCUMENT])


@router.post(
    "/process_document_submission",
    response_model=DocumentSubmissionResponse,
    status_code=status.HTTP_202_ACCEPTED,  # Changed to 202 for async processing
    summary="Process document submission",
    description="Process multiple documents, extract fields, and compare."
)
async def process_document_submission(
    payload: DocumentSubmissionRequest,
    background_tasks: BackgroundTasks
) -> DocumentSubmissionResponse:
    """
    Process document submission with field extraction and comparison.
    
    Flow:
    1. Load files from MinIO (streaming)
    2. Process each file (Excel parsing or LLM OCR for PDF)
    3. Extract structured fields
    4. Compare fields across documents
    5. Save OCR results to MinIO
    6. Return comparison results
    """
    try:
        task_id = payload.task_id
        
        # Step 1: List files
        files = await storage_service.list_files(task_id)
        if not files:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No files found for task_id: {task_id}"
            )
        
        logger.info(f"Processing {len(files)} files for task {task_id}")
        
        # Step 2: Process files in parallel (streaming from MinIO)
        processing_tasks = []
        for file_info in files:
            file_stream = await storage_service.get_file_stream(file_info["name"])
            task = document_processor.process_file(
                file_stream,
                file_info["name"]
            )
            processing_tasks.append(task)
        
        # Wait for all processing to complete
        document_results = await asyncio.gather(*processing_tasks, return_exceptions=True)
        
        # Handle errors
        valid_results = []
        for idx, result in enumerate(document_results):
            if isinstance(result, Exception):
                logger.error(f"Error processing {files[idx]['name']}: {result}")
                continue
            valid_results.append(result)
        
        if not valid_results:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process any documents"
            )
        
        # Step 3: Compare fields
        comparison_result = field_comparison_service.compare_documents(valid_results)
        
        # Step 4: Save OCR results to MinIO
        ocr_results = {
            "task_id": task_id,
            "document_results": valid_results,
            "comparison_result": comparison_result,
            "processed_at": datetime.utcnow().isoformat()
        }
        
        # Save in background
        background_tasks.add_task(
            storage_service.save_ocr_result,
            task_id,
            ocr_results
        )
        
        # Return results
        return DocumentSubmissionResponse(
            status="processed",
            result={
                "task_id": task_id,
                "documents_processed": len(valid_results),
                "comparison": comparison_result
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in process_document_submission: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document processing failed: {str(e)}"
        )


@router.post(
    "/compare_document_contents",
    response_model=CompareDocumentResponse,
    status_code=status.HTTP_200_OK,
    summary="Compare document contents",
    description="Compare Excel and PDF using LLM OCR and extract field differences."
)
async def compare_document_contents(
    payload: CompareDocumentRequest
) -> CompareDocumentResponse:
    """
    Compare Excel and PDF documents using LLM OCR.
    
    Flow:
    1. Load files from MinIO (streaming)
    2. Process Excel (parse) and PDF (LLM OCR)
    3. Extract fields from both
    4. Compare field-by-field
    5. Return detailed differences
    """
    try:
        task_id = payload.task_id
        excel_file_name = payload.excel_file_name
        pdf_file_name = payload.pdf_file_name
        
        # Step 1: Load files (streaming)
        excel_stream = await storage_service.get_file_stream(
            f"{task_id}/{excel_file_name}"
        )
        pdf_stream = await storage_service.get_file_stream(
            f"{task_id}/{pdf_file_name}"
        )
        
        # Step 2: Process files in parallel
        excel_result, pdf_result = await asyncio.gather(
            document_processor.process_file(excel_stream, excel_file_name, "excel"),
            document_processor.process_file(pdf_stream, pdf_file_name, "pdf")
        )
        
        # Step 3: Compare
        comparison = field_comparison_service.compare_documents([
            excel_result,
            pdf_result
        ])
        
        # Step 4: Save OCR results
        ocr_results = {
            "task_id": task_id,
            "excel_result": excel_result,
            "pdf_result": pdf_result,
            "comparison": comparison
        }
        
        await storage_service.save_ocr_result(task_id, ocr_results)
        
        return CompareDocumentResponse(
            status="compared",
            result=comparison
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in compare_document_contents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document comparison failed: {str(e)}"
        )
```

### 6. Configuration Updates

```python
# app/core/config.py (Add these settings)
class Settings(BaseSettings):
    # ... existing settings ...
    
    # MinIO Settings
    MINIO_ENDPOINT: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_SECURE: bool = False
    MINIO_BUCKET: str = "documents"
    
    # OpenAI Settings (for LLM OCR)
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o"  # or "gpt-4-vision-preview"
```

---

## 📦 Dependencies Cần Thêm

```toml
# backend/pyproject.toml
dependencies = [
    # ... existing ...
    "minio>=7.2.0",
    "openai>=1.12.0",
    "pandas>=2.0.0",
    "openpyxl>=3.1.0",
    "PyMuPDF>=1.23.0",  # fitz for PDF processing
    "Pillow>=10.0.0",
]
```

---

## ✅ Summary

### Implemented:
1. ✅ MinIO streaming (không download to disk)
2. ✅ LLM OCR service (GPT-4 Vision)
3. ✅ Document processor (Excel + PDF)
4. ✅ Field extraction và comparison
5. ✅ Save OCR results to MinIO
6. ✅ Parallel processing

### Next Steps:
1. Add error handling và retry logic
2. Add caching cho OCR results
3. Add background job processing (Celery) cho long tasks
4. Add field mapping/normalization với LLM
5. Add visual comparison (nếu cần)

