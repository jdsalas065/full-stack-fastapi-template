# Changelog

## [Unreleased] - 2025-01-27

### Added

#### New Services
- **Storage Service** (`app/services/storage_service.py`)
  - MinIO streaming support (no disk download)
  - List files by task_id
  - Get file streams (in-memory)
  - Save/retrieve OCR results

- **LLM OCR Service** (`app/services/llm_ocr_service.py`)
  - GPT-4 Vision integration for OCR
  - Extract text and structured fields from images
  - Parallel processing for multiple images
  - JSON response format with field extraction

- **Document Processor** (`app/services/document_processor.py`)
  - Excel processing with pandas/openpyxl
  - PDF processing with PyMuPDF + LLM OCR
  - Field extraction from Excel and PDF
  - Auto-detect file type

- **Field Comparison Service** (`app/services/field_comparison_service.py`)
  - Compare multiple documents field-by-field
  - Identify differences (numeric, text, missing)
  - Normalize values for comparison

#### API Enhancements
- **`/process_document_submission`**
  - Process multiple documents in parallel
  - Extract fields using LLM OCR
  - Compare fields across documents
  - Save OCR results to MinIO (background task)
  - Return field-by-field comparison results

- **`/compare_document_contents`**
  - Compare Excel vs PDF using LLM OCR
  - Extract structured fields from both
  - Return detailed field differences
  - Save OCR results

#### Configuration
- MinIO settings (endpoint, credentials, bucket)
- OpenAI settings (API key, model)

### Changed

#### API Routes
- **`app/api/routes/document.py`**
  - Complete refactor with new implementation
  - Streaming from MinIO instead of downloading
  - Parallel processing for multiple files
  - Background tasks for saving OCR results
  - Improved error handling

#### Dependencies
- Added `minio>=7.2.0` for MinIO client
- Added `openai>=1.12.0` for OpenAI API
- Added `pandas>=2.0.0` for Excel processing
- Added `openpyxl>=3.1.0` for Excel file handling
- Added `PyMuPDF>=1.23.0` for PDF to images conversion
- Added `Pillow>=10.0.0` for image processing

### Removed

- Old document processing functions (replaced with new services)
- Hardcoded MinIO configuration (moved to environment variables)
- Local file system download logic (replaced with streaming)

### Fixed

- Storage flow: Now uses streaming instead of downloading to disk
- OCR implementation: Now uses LLM (GPT-4 Vision) instead of placeholder
- Field extraction: Now properly extracts structured fields
- Comparison logic: Now properly compares fields across documents

### Security

- Moved MinIO credentials to environment variables
- Moved OpenAI API key to environment variables

### Performance

- Parallel processing for multiple files
- Streaming from MinIO (no disk I/O)
- Background tasks for saving OCR results

### Documentation

- Added `IMPLEMENTATION_SUMMARY.md`
- Added `SOLUTIONS_IMPLEMENTATION.md`
- Added `API_ARCHITECTURE_REVIEW.md`
- Added `PR_DESCRIPTION.md`
- Updated `app/services/__init__.py` with new exports

---

## Migration Notes

### Environment Variables

Add to `.env`:
```env
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_SECURE=false
MINIO_BUCKET=documents
OPENAI_API_KEY=your-api-key-here
OPENAI_MODEL=gpt-4o
```

### Installation

```bash
cd backend
uv sync
```

### API Response Changes

**Before:**
```json
{
  "status": "processed",
  "result": {...}
}
```

**After:**
```json
{
  "status": "processed",
  "result": {
    "task_id": "...",
    "documents_processed": 2,
    "comparison": {
      "field_comparisons": {...},
      "differences": [...],
      "matches": [...],
      "total_fields": 5,
      "matched_fields": 3,
      "different_fields": 2
    }
  }
}
```

---

## Breaking Changes

1. **Storage Flow**: Files are now streamed from MinIO instead of downloaded to `/tmp/documents`
2. **OCR Method**: Now uses LLM (GPT-4 Vision) instead of pytesseract
3. **API Response**: New response format with field comparison details
4. **Dependencies**: New dependencies required (see above)

---

## Known Issues

- Large files (>100MB) are loaded entirely into memory (may need optimization)
- No retry logic for OpenAI API calls (may fail on network issues)
- No caching for OCR results (may re-process same files)

---

## Future Improvements

- [ ] Add unit tests for all services
- [ ] Add integration tests for APIs
- [ ] Add caching for OCR results
- [ ] Add retry logic for API calls
- [ ] Add chunked processing for large files
- [ ] Add field mapping/normalization with LLM
- [ ] Add background job processing (Celery) for long tasks
- [ ] Add visual comparison support

