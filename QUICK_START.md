# Quick Start Guide - Document Processing System

## Hướng dẫn Nhanh (Vietnamese)

### 1. Cài đặt Dependencies

```bash
cd backend

# Core dependencies
uv add pytesseract pillow pdf2image pypdf2 pdfplumber openai

# Optional: Advanced text processing
uv add scikit-learn sentence-transformers
```

### 2. Cấu hình Environment Variables

Tạo/cập nhật file `.env` ở thư mục root:

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-4
OPENAI_MAX_TOKENS=2000
OPENAI_TEMPERATURE=0.7

# Document Processing
MAX_UPLOAD_SIZE_MB=10
OCR_LANGUAGE=vie+eng
DOCUMENT_STORAGE_PATH=storage/documents

# Existing settings
PROJECT_NAME=Document Processing API
SECRET_KEY=your-secret-key
# ... other settings
```

### 3. Cài đặt Tesseract OCR

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-vie tesseract-ocr-eng
```

**macOS:**
```bash
brew install tesseract tesseract-lang
```

**Windows:**
- Download từ: https://github.com/UB-Mannheim/tesseract/wiki
- Thêm Tesseract vào PATH

### 4. Kích hoạt OCR Service

Cập nhật `backend/app/services/ocr_service.py`:

```python
import pytesseract
from PIL import Image

async def extract_text_from_image(self, image_path: str, language: Optional[str] = None):
    lang = language or self.language
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image, lang=lang)
    data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
    
    # Calculate confidence
    confidences = [c for c in data['conf'] if c != -1]
    confidence = sum(confidences) / len(confidences) if confidences else 0
    
    return OCRResult(text=text, confidence=confidence / 100)
```

### 5. Kích hoạt OpenAI Service

Cập nhật `backend/app/services/openai_service.py`:

```python
import openai

async def compare_documents(self, document_1_text: str, document_2_text: str, comparison_prompt: Optional[str] = None):
    openai.api_key = self.api_key
    
    prompt = comparison_prompt or self._default_comparison_prompt()
    full_prompt = prompt.format(doc1=document_1_text, doc2=document_2_text)
    
    response = await openai.ChatCompletion.acreate(
        model=self.model,
        messages=[
            {"role": "system", "content": "You are a document comparison expert."},
            {"role": "user", "content": full_prompt}
        ],
        max_tokens=self.max_tokens,
        temperature=self.temperature
    )
    
    analysis = response.choices[0].message.content
    
    # Parse response
    is_consistent = "consistent" in analysis.lower() and "not consistent" not in analysis.lower()
    
    return {
        "analysis": analysis,
        "is_consistent": is_consistent,
        "key_differences": self._extract_differences_from_analysis(analysis),
        "similarity_assessment": self._extract_similarity_from_analysis(analysis),
    }
```

### 6. Chạy Application

```bash
# Development mode
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Hoặc với Docker
cd ..
docker-compose up
```

### 7. Truy cập API Documentation

Mở browser và truy cập:
- Swagger UI: http://localhost:8000/api/v1/docs
- ReDoc: http://localhost:8000/api/v1/redoc

### 8. Test API

#### Upload một tài liệu:
```bash
curl -X POST "http://localhost:8000/api/v1/documents/upload/" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/your/document.pdf"
```

#### Xử lý OCR:
```bash
curl -X POST "http://localhost:8000/api/v1/documents/process/" \
  -H "Content-Type: application/json" \
  -d '{"document_id": "YOUR_DOCUMENT_ID", "perform_ocr": true}'
```

#### So sánh hai tài liệu:
```bash
curl -X POST "http://localhost:8000/api/v1/documents/compare/" \
  -H "Content-Type: application/json" \
  -d '{
    "document_1_id": "DOC_ID_1",
    "document_2_id": "DOC_ID_2",
    "use_ai_analysis": true
  }'
```

## API Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/documents/upload/` | Upload tài liệu |
| POST | `/api/v1/documents/process/` | Xử lý OCR |
| POST | `/api/v1/documents/compare/` | So sánh 2 tài liệu |
| GET | `/api/v1/documents/{id}/` | Lấy chi tiết tài liệu |
| GET | `/api/v1/documents/` | Danh sách tài liệu |

## Code Structure Reference

```
backend/app/
├── api/routes/documents.py      # API endpoints
├── services/
│   ├── ocr_service.py           # OCR logic
│   ├── openai_service.py        # AI integration
│   └── comparison_service.py    # Comparison logic
├── crud/document.py             # Database operations
├── models/document.py           # Data models
├── schemas/document.py          # Request/response schemas
└── core/config.py               # Configuration

Documentation:
├── DOCUMENT_PROCESSING_README.md  # Full documentation
├── ARCHITECTURE.md                # System architecture
└── QUICK_START.md                 # This file
```

## Common Issues & Solutions

### Issue: Tesseract not found
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# Check installation
tesseract --version
```

### Issue: OpenAI API Error
- Kiểm tra API key hợp lệ
- Kiểm tra credit balance
- Kiểm tra rate limits

### Issue: File upload failed
- Kiểm tra MIME type trong ALLOWED_DOCUMENT_TYPES
- Kiểm tra file size < MAX_UPLOAD_SIZE_MB
- Kiểm tra quyền ghi vào DOCUMENT_STORAGE_PATH

### Issue: OCR confidence thấp
- Cải thiện chất lượng ảnh input
- Thử với ngôn ngữ OCR khác
- Xem xét dùng cloud OCR (Google Vision, AWS Textract)

## Next Steps

1. **Implement Database**: Chuyển từ in-memory sang PostgreSQL
2. **Add Authentication**: JWT authentication cho API
3. **Background Tasks**: Celery cho xử lý bất đồng bộ
4. **Caching**: Redis cho cache OCR results
5. **Monitoring**: Sentry, Prometheus cho monitoring
6. **Testing**: Viết unit tests và integration tests

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
- [OpenAI API](https://platform.openai.com/docs)
- [PyPDF2](https://pypdf2.readthedocs.io/)
- [Pydantic](https://docs.pydantic.dev/)

## Support

Để được hỗ trợ hoặc báo cáo lỗi, vui lòng tạo issue trên GitHub repository.
