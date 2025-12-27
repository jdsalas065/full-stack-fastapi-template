# Document Processing, OCR & AI Comparison System

## Tổng quan (Overview)

Hệ thống này cung cấp khả năng xử lý tài liệu, OCR và so sánh tài liệu sử dụng AI. Các tính năng chính:

- **OCR (Optical Character Recognition)**: Trích xuất văn bản từ hình ảnh và PDF
- **Tích hợp ChatGPT API**: Phân tích và so sánh tài liệu thông minh
- **So sánh tài liệu**: Đối chiếu hai tài liệu để kiểm tra tính nhất quán
- **Quản lý tài liệu**: Upload, lưu trữ và quản lý tài liệu

## Cấu trúc mã nguồn (Code Structure)

```
backend/app/
├── models/
│   └── document.py              # Database models cho tài liệu
│       ├── Document             # Model chính cho tài liệu
│       ├── DocumentComparison   # Model cho kết quả so sánh
│       ├── DocumentStatus       # Enum trạng thái
│       └── DocumentType         # Enum loại tài liệu
│
├── schemas/
│   └── document.py              # Pydantic schemas cho API
│       ├── DocumentUploadResponse
│       ├── DocumentProcessRequest/Response
│       ├── DocumentComparisonRequest/Response
│       └── DocumentDetailResponse
│
├── services/
│   ├── __init__.py              # Export services
│   ├── ocr_service.py           # Xử lý OCR
│   │   └── OCRService           # Trích xuất text từ image/PDF
│   ├── openai_service.py        # Tích hợp ChatGPT
│   │   └── OpenAIService        # Gọi OpenAI API
│   └── comparison_service.py    # So sánh tài liệu
│       └── DocumentComparisonService  # Logic so sánh
│
├── crud/
│   └── document.py              # Database operations
│       ├── DocumentCRUD         # CRUD cho documents
│       └── ComparisonCRUD       # CRUD cho comparisons
│
└── api/routes/
    └── documents.py             # API endpoints
        ├── POST /documents/upload/
        ├── POST /documents/process/
        ├── POST /documents/compare/
        ├── GET  /documents/{id}/
        └── GET  /documents/
```

## Cấu hình (Configuration)

Thêm các biến môi trường sau vào file `.env`:

```env
# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-4
OPENAI_MAX_TOKENS=2000
OPENAI_TEMPERATURE=0.7

# Document Processing
MAX_UPLOAD_SIZE_MB=10
OCR_LANGUAGE=vie+eng
DOCUMENT_STORAGE_PATH=storage/documents
```

## Cài đặt Dependencies (Installation)

Để sử dụng đầy đủ các tính năng, cần cài đặt thêm các thư viện:

```bash
# OCR Libraries
uv add pytesseract pillow pdf2image

# PDF Processing
uv add pypdf2 pdfplumber

# OpenAI Integration
uv add openai

# Text Similarity (optional)
uv add scikit-learn sentence-transformers
```

### Cài đặt Tesseract OCR

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-vie tesseract-ocr-eng
```

**macOS:**
```bash
brew install tesseract tesseract-lang
```

**Windows:**
Download từ: https://github.com/UB-Mannheim/tesseract/wiki

## Sử dụng API (API Usage)

### 1. Upload tài liệu

```bash
curl -X POST "http://localhost:8000/api/v1/documents/upload/" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.pdf" \
  -F "description=Contract document"
```

Response:
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "filename": "document.pdf",
  "file_type": "pdf",
  "size_bytes": 245680,
  "status": "uploaded",
  "uploaded_at": "2024-01-15T10:30:00Z",
  "message": "Document uploaded successfully"
}
```

### 2. Xử lý OCR

```bash
curl -X POST "http://localhost:8000/api/v1/documents/process/" \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "123e4567-e89b-12d3-a456-426614174000",
    "perform_ocr": true,
    "language": "vie+eng"
  }'
```

Response:
```json
{
  "document_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "completed",
  "ocr_text": "Extracted text content...",
  "ocr_confidence": 0.95,
  "processed_at": "2024-01-15T10:31:00Z",
  "message": "Document processed successfully"
}
```

### 3. So sánh hai tài liệu

```bash
curl -X POST "http://localhost:8000/api/v1/documents/compare/" \
  -H "Content-Type: application/json" \
  -d '{
    "document_1_id": "123e4567-e89b-12d3-a456-426614174000",
    "document_2_id": "223e4567-e89b-12d3-a456-426614174001",
    "use_ai_analysis": true,
    "comparison_prompt": "Compare these documents for legal consistency"
  }'
```

Response:
```json
{
  "comparison_id": "323e4567-e89b-12d3-a456-426614174002",
  "document_1_id": "123e4567-e89b-12d3-a456-426614174000",
  "document_2_id": "223e4567-e89b-12d3-a456-426614174001",
  "similarity_score": 0.87,
  "is_consistent": true,
  "differences": [
    "Document 1 contains 5 unique terms",
    "Minor formatting differences"
  ],
  "ai_analysis": "Both documents are substantially similar with minor variations...",
  "comparison_method": "ai_assisted",
  "processing_time_seconds": 2.34,
  "comparison_date": "2024-01-15T10:32:00Z"
}
```

### 4. Lấy thông tin tài liệu

```bash
curl -X GET "http://localhost:8000/api/v1/documents/123e4567-e89b-12d3-a456-426614174000/"
```

### 5. Danh sách tài liệu

```bash
curl -X GET "http://localhost:8000/api/v1/documents/?page=1&page_size=20&status=completed"
```

## Luồng xử lý (Processing Flow)

```
1. Upload Document
   ↓
   [Document saved to storage]
   ↓
2. Process with OCR
   ↓
   [OCR extracts text]
   ↓
   [Document status: completed]
   ↓
3. Compare Documents
   ↓
   [Text similarity analysis]
   ↓
   [Optional: AI analysis via ChatGPT]
   ↓
   [Comparison results returned]
```

## Tích hợp Services (Service Integration)

### OCR Service

```python
from app.services import ocr_service

# Extract text from image
result = await ocr_service.extract_text_from_image(
    "path/to/image.jpg",
    language="vie+eng"
)
print(result.text)
print(result.confidence)

# Extract text from PDF
result = await ocr_service.extract_text_from_pdf("path/to/document.pdf")
```

### OpenAI Service

```python
from app.services import openai_service

# Analyze document
analysis = await openai_service.analyze_document(
    document_text="Text content...",
    analysis_prompt="Summarize this document"
)

# Compare documents
comparison = await openai_service.compare_documents(
    document_1_text="First document...",
    document_2_text="Second document...",
    comparison_prompt="Find inconsistencies"
)
```

### Comparison Service

```python
from app.services import comparison_service
from app.crud import document_crud

# Get documents
doc1 = await document_crud.get("doc-id-1")
doc2 = await document_crud.get("doc-id-2")

# Compare
result = await comparison_service.compare_documents(
    doc1,
    doc2,
    use_ai_analysis=True
)
```

## Mở rộng và Tùy chỉnh (Extension & Customization)

### 1. Thêm OCR Provider mới

Chỉnh sửa `app/services/ocr_service.py`:

```python
async def extract_text_from_image_cloud(self, image_path: str):
    # Tích hợp Google Vision API, AWS Textract, etc.
    pass
```

### 2. Thêm AI Model khác

Tạo service mới trong `app/services/`:

```python
# app/services/custom_ai_service.py
class CustomAIService:
    async def analyze(self, text: str):
        # Tích hợp model AI tùy chỉnh
        pass
```

### 3. Thêm Database thực

Chuyển từ in-memory sang database:

1. Cài đặt SQLModel: `uv add sqlmodel`
2. Cập nhật models để extend SQLModel
3. Cập nhật CRUD để sử dụng database session

```python
from sqlmodel import Field, SQLModel

class Document(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    filename: str
    # ... other fields
```

## Best Practices

1. **Bảo mật API Keys**: Không commit API keys vào git
2. **Giới hạn kích thước file**: Đặt `MAX_UPLOAD_SIZE_MB` hợp lý
3. **Xử lý bất đồng bộ**: Dùng background tasks cho OCR và AI analysis
4. **Caching**: Cache kết quả OCR để tránh xử lý lại
5. **Rate Limiting**: Giới hạn số lượng requests đến OpenAI API
6. **Error Handling**: Log errors và trả về messages rõ ràng

## Testing

```bash
# Run tests
cd backend
pytest tests/

# Test specific module
pytest tests/services/test_ocr_service.py
```

## Troubleshooting

### OCR không hoạt động
- Kiểm tra Tesseract đã được cài đặt
- Kiểm tra ngôn ngữ OCR đã được cài đặt
- Xem logs: `OCR_LANGUAGE=vie+eng`

### OpenAI API lỗi
- Kiểm tra API key hợp lệ
- Kiểm tra quota và billing
- Xem rate limits

### Upload file lỗi
- Kiểm tra MIME type trong `ALLOWED_DOCUMENT_TYPES`
- Kiểm tra kích thước file < `MAX_UPLOAD_SIZE_MB`
- Kiểm tra quyền ghi vào `DOCUMENT_STORAGE_PATH`

## Liên hệ & Đóng góp

Để đóng góp hoặc báo cáo lỗi, vui lòng tạo issue trên GitHub repository.
