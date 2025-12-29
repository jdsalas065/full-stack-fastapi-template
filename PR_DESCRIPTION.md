# 🚀 PR: Implement Document Processing với LLM OCR và MinIO Streaming

## 📋 Summary

Implement document processing system với:
- **LLM-based OCR** sử dụng GPT-4 Vision (thay vì pytesseract)
- **MinIO streaming** để process files trực tiếp (không download về disk)
- **Field extraction và comparison** cho nhiều documents với templates khác nhau
- **Parallel processing** để tăng performance

## 🎯 Changes

### ✨ New Services

1. **`app/services/storage_service.py`**
   - MinIO storage service với streaming support
   - List files, get file streams (in-memory)
   - Save/retrieve OCR results

2. **`app/services/llm_ocr_service.py`**
   - LLM OCR service sử dụng GPT-4 Vision
   - Extract text và structured fields từ images
   - Parallel processing cho multiple images

3. **`app/services/document_processor.py`**
   - Process Excel files (pandas/openpyxl)
   - Process PDF files (PyMuPDF + LLM OCR)
   - Extract structured fields

4. **`app/services/field_comparison_service.py`**
   - Compare fields từ multiple documents
   - Identify differences (numeric, text, missing)
   - Field-by-field comparison

### 🔄 Updated Files

1. **`app/api/routes/document.py`**
   - Refactor hoàn toàn với implementation mới
   - `/process_document_submission`: Process nhiều files, extract fields, compare
   - `/compare_document_contents`: Compare Excel vs PDF với LLM OCR
   - Streaming từ MinIO thay vì download
   - Background tasks để save OCR results

2. **`app/core/config.py`**
   - Thêm MinIO settings (endpoint, credentials, bucket)
   - Thêm OpenAI settings (API key, model)

3. **`backend/pyproject.toml`**
   - Thêm dependencies:
     - `minio>=7.2.0`
     - `openai>=1.12.0`
     - `pandas>=2.0.0`
     - `openpyxl>=3.1.0`
     - `PyMuPDF>=1.23.0`
     - `Pillow>=10.0.0`

4. **`app/services/__init__.py`**
   - Export các services mới

## 🔧 Architecture Changes

### Before:
```
MinIO → Download to /tmp → Process → Compare
```
- ❌ Tốn disk space
- ❌ Không scale được
- ❌ OCR tools chưa implement
- ❌ Không có LLM integration

### After:
```
MinIO → Stream → Process (parallel) → LLM OCR → Extract Fields → Compare → Save Results
```
- ✅ Streaming (không cần disk)
- ✅ Parallel processing
- ✅ LLM OCR với GPT-4 Vision
- ✅ Field extraction và comparison
- ✅ Save OCR results to MinIO

## 📦 Dependencies Added

```toml
minio>=7.2.0          # MinIO client
openai>=1.12.0        # OpenAI API client
pandas>=2.0.0         # Excel processing
openpyxl>=3.1.0       # Excel file handling
PyMuPDF>=1.23.0       # PDF to images
Pillow>=10.0.0        # Image processing
```

## 🔐 Environment Variables Required

Thêm vào `.env`:

```env
# MinIO Settings
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_SECURE=false
MINIO_BUCKET=documents

# OpenAI Settings
OPENAI_API_KEY=your-api-key-here
OPENAI_MODEL=gpt-4o
```

## 🧪 Testing

### Manual Testing:

1. **Setup MinIO:**
   ```bash
   # Ensure MinIO is running
   # Create bucket: documents
   # Upload test files with structure: {task_id}/file.xlsx
   ```

2. **Test API:**
   ```bash
   # Process multiple documents
   curl -X POST http://localhost:8000/api/v1/document/process_document_submission \
     -H "Content-Type: application/json" \
     -d '{"task_id": "test-123"}'

   # Compare documents
   curl -X POST http://localhost:8000/api/v1/document/compare_document_contents \
     -H "Content-Type: application/json" \
     -d '{
       "task_id": "test-123",
       "excel_file_name": "invoice.xlsx",
       "pdf_file_name": "invoice.pdf"
     }'
   ```

## ⚠️ Breaking Changes

- **Removed**: Old document processing functions (đã replace)
- **Changed**: API response format (thêm field comparison details)
- **Changed**: Storage flow (streaming thay vì download)

## 📝 Notes

1. **MinIO Setup**: Đảm bảo MinIO đang chạy và bucket `documents` đã được tạo
2. **OpenAI API Key**: Cần có API key hợp lệ để LLM OCR hoạt động
3. **File Organization**: Files phải được organize theo `task_id` trong MinIO
4. **Large Files**: Hiện tại load toàn bộ file vào memory, có thể cần optimize cho files lớn (>100MB)

## 🔄 Migration Guide

### For Existing Code:

1. **Update environment variables** trong `.env`
2. **Install dependencies**: `uv sync` hoặc `pip install -r requirements.txt`
3. **Update MinIO bucket name** nếu khác default
4. **Test với sample files** trước khi deploy production

### API Changes:

**Before:**
```python
# Old response format
{
  "status": "processed",
  "result": {...}
}
```

**After:**
```python
# New response format với field comparison
{
  "status": "processed",
  "result": {
    "task_id": "...",
    "documents_processed": 2,
    "comparison": {
      "field_comparisons": {...},
      "differences": [...],
      "matches": [...]
    }
  }
}
```

## ✅ Checklist

- [x] Code implementation hoàn tất
- [x] Type hints đầy đủ
- [x] Error handling
- [x] Logging
- [x] No linter errors
- [ ] Unit tests (TODO)
- [ ] Integration tests (TODO)
- [ ] Documentation updates
- [ ] Environment variables documented

## 🚀 Next Steps (Future PRs)

1. Add unit tests cho các services
2. Add integration tests cho APIs
3. Add caching cho OCR results
4. Add retry logic cho API calls
5. Add chunked processing cho large files
6. Add field mapping/normalization với LLM
7. Add background job processing (Celery) cho long tasks

## 📚 Related Documentation

- `IMPLEMENTATION_SUMMARY.md` - Chi tiết implementation
- `SOLUTIONS_IMPLEMENTATION.md` - Solutions và architecture
- `API_ARCHITECTURE_REVIEW.md` - Review architecture

---

**Reviewer Notes:**
- Code đã được review về architecture và flow
- Không có linter errors
- Type hints đầy đủ
- Error handling comprehensive
- Cần test với real MinIO và OpenAI API

