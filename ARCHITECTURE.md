# Kiến trúc Hệ thống Xử lý Tài liệu (Document Processing Architecture)

## Tổng quan Kiến trúc

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                            │
│  (Frontend/Mobile App/External Systems)                         │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTP/REST API
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                        API LAYER                                │
│  FastAPI Routes (app/api/routes/documents.py)                   │
│  - POST /documents/upload/                                      │
│  - POST /documents/process/                                     │
│  - POST /documents/compare/                                     │
│  - GET  /documents/{id}/                                        │
│  - GET  /documents/                                             │
└────────────────┬────────────────────┬───────────────────────────┘
                 │                    │
                 ▼                    ▼
┌─────────────────────────┐  ┌──────────────────────────┐
│   BUSINESS LOGIC LAYER   │  │    DATA ACCESS LAYER    │
│  (Services)              │  │    (CRUD)               │
│                          │  │                         │
│  ┌────────────────────┐ │  │  ┌──────────────────┐  │
│  │  OCRService        │ │  │  │ DocumentCRUD     │  │
│  │  - extract_text    │ │  │  │ - create()       │  │
│  │  - image OCR       │ │  │  │ - get()          │  │
│  │  - PDF OCR         │ │  │  │ - update()       │  │
│  └────────────────────┘ │  │  │ - delete()       │  │
│                          │  │  │ - list()         │  │
│  ┌────────────────────┐ │  │  └──────────────────┘  │
│  │  OpenAIService     │ │  │                         │
│  │  - analyze_doc     │ │  │  ┌──────────────────┐  │
│  │  - compare_docs    │ │  │  │ ComparisonCRUD   │  │
│  │  - extract_data    │ │  │  │ - create()       │  │
│  └────────────────────┘ │  │  │ - get()          │  │
│                          │  │  │ - list_by_doc()  │  │
│  ┌────────────────────┐ │  │  └──────────────────┘  │
│  │ ComparisonService  │ │  │                         │
│  │ - compare_docs     │ │  └─────────┬───────────────┘
│  │ - calc_similarity  │ │            │
│  │ - extract_diffs    │ │            ▼
│  └────────────────────┘ │  ┌──────────────────────┐
│                          │  │   DATA LAYER        │
└────────┬─────────────────┘  │   (Models/Schemas)  │
         │                    │                     │
         ▼                    │  - Document         │
┌─────────────────────────┐   │  - DocumentStatus   │
│   EXTERNAL SERVICES     │   │  - DocumentType     │
│                         │   │  - Comparison       │
│  ┌──────────────────┐  │   └─────────────────────┘
│  │  Tesseract OCR   │  │            │
│  │  (Local)         │  │            ▼
│  └──────────────────┘  │   ┌──────────────────────┐
│                         │   │    STORAGE LAYER    │
│  ┌──────────────────┐  │   │                     │
│  │  OpenAI API      │  │   │  - PostgreSQL DB    │
│  │  (ChatGPT)       │  │   │  - File Storage     │
│  └──────────────────┘  │   │    (documents/)     │
│                         │   └─────────────────────┘
│  ┌──────────────────┐  │
│  │  Cloud OCR       │  │
│  │  (Optional)      │  │
│  │  - Google Vision │  │
│  │  - AWS Textract  │  │
│  └──────────────────┘  │
└─────────────────────────┘
```

## Luồng Xử lý Dữ liệu (Data Flow)

### 1. Upload Document
```
Client → API (POST /upload) → Save File → Create Document Record → Return Document ID
```

### 2. Process with OCR
```
Client → API (POST /process) 
       → Get Document 
       → OCRService.extract_text() 
       → [Tesseract/Cloud OCR]
       → Update Document with OCR text
       → Return OCR Results
```

### 3. Compare Documents
```
Client → API (POST /compare)
       → Get Document 1 & 2
       → ComparisonService.compare_documents()
       → Calculate Text Similarity
       → [Optional] OpenAIService.compare_documents()
       → Generate Comparison Report
       → Save Comparison Record
       → Return Results
```

## Chi tiết Layer

### 1. Models Layer (`app/models/`)
**Trách nhiệm**: Định nghĩa cấu trúc dữ liệu
- `Document`: Metadata tài liệu, OCR results
- `DocumentComparison`: Kết quả so sánh
- `DocumentStatus`: Enum trạng thái xử lý
- `DocumentType`: Enum loại tài liệu

### 2. Schemas Layer (`app/schemas/`)
**Trách nhiệm**: Validation API request/response
- `DocumentUploadResponse`: Response sau upload
- `DocumentProcessRequest/Response`: OCR processing
- `DocumentComparisonRequest/Response`: So sánh tài liệu
- `DocumentDetailResponse`: Chi tiết tài liệu

### 3. Services Layer (`app/services/`)
**Trách nhiệm**: Business logic, orchestration
- **OCRService**: 
  - Extract text từ images (pytesseract)
  - Extract text từ PDFs (PyPDF2/pdfplumber)
  - Hỗ trợ multiple languages
  
- **OpenAIService**:
  - Gọi ChatGPT API
  - Document analysis
  - Semantic comparison
  - Structured data extraction
  
- **ComparisonService**:
  - Text similarity calculation
  - Orchestrate AI comparison
  - Generate difference reports

### 4. CRUD Layer (`app/crud/`)
**Trách nhiệm**: Database operations
- **DocumentCRUD**: CRUD cho documents
- **ComparisonCRUD**: CRUD cho comparisons
- Hiện tại: In-memory storage
- Tương lai: SQLAlchemy/SQLModel integration

### 5. API Layer (`app/api/routes/`)
**Trách nhiệm**: HTTP endpoints, validation
- Request validation
- Error handling
- Response formatting
- API documentation

## Tích hợp Bên ngoài (External Integrations)

### OCR Providers
1. **Tesseract OCR** (Local)
   - Miễn phí, open source
   - Hỗ trợ nhiều ngôn ngữ
   - Tốc độ nhanh
   
2. **Google Cloud Vision API** (Optional)
   - Độ chính xác cao
   - Hỗ trợ handwriting
   - Phí theo usage
   
3. **AWS Textract** (Optional)
   - Xử lý forms, tables
   - High accuracy
   - Phí theo usage

### AI Services
1. **OpenAI GPT-4**
   - Semantic analysis
   - Context understanding
   - Multi-language support
   
2. **Alternative AI Models** (Future)
   - Anthropic Claude
   - Google Gemini
   - Local LLMs (Llama, etc.)

## Bảo mật và Performance

### Security Considerations
```
┌─────────────────────────────────────────┐
│  Security Layers                        │
├─────────────────────────────────────────┤
│  1. API Authentication (JWT)            │
│  2. File Type Validation                │
│  3. File Size Limits                    │
│  4. API Key Protection (env vars)       │
│  5. Rate Limiting (OpenAI calls)        │
│  6. Input Sanitization                  │
└─────────────────────────────────────────┘
```

### Performance Optimization
```
┌─────────────────────────────────────────┐
│  Performance Strategies                 │
├─────────────────────────────────────────┤
│  1. Async Processing (FastAPI)          │
│  2. Background Tasks (OCR, AI)          │
│  3. Caching (OCR results)               │
│  4. Connection Pooling (Database)       │
│  5. File Chunking (Large documents)     │
│  6. Queue System (Celery/RQ - future)   │
└─────────────────────────────────────────┘
```

## Mở rộng Tương lai (Future Extensions)

### Phase 1 (Current)
- [x] Basic file upload
- [x] OCR integration structure
- [x] OpenAI integration structure
- [x] Document comparison logic
- [x] REST API endpoints

### Phase 2 (Next)
- [ ] Implement real OCR (pytesseract)
- [ ] Implement real OpenAI calls
- [ ] Database integration (PostgreSQL)
- [ ] User authentication
- [ ] File storage (S3/MinIO)

### Phase 3 (Advanced)
- [ ] Background job processing (Celery)
- [ ] WebSocket for real-time updates
- [ ] Batch processing
- [ ] Advanced comparison algorithms
- [ ] Document versioning
- [ ] Audit trail

### Phase 4 (Enterprise)
- [ ] Multi-tenancy
- [ ] Advanced analytics
- [ ] Custom AI model training
- [ ] Workflow automation
- [ ] Integration with external systems
- [ ] Compliance features (GDPR, etc.)

## Deployment Architecture

```
┌──────────────────────────────────────────────────────────┐
│                     Load Balancer                        │
│                      (Traefik)                           │
└────────────────┬────────────────┬────────────────────────┘
                 │                │
      ┌──────────▼──────┐  ┌──────▼──────────┐
      │  FastAPI App 1  │  │  FastAPI App 2  │
      │  (Container)    │  │  (Container)    │
      └────────┬────────┘  └────────┬────────┘
               │                     │
               └──────────┬──────────┘
                          │
              ┌───────────▼───────────┐
              │   PostgreSQL          │
              │   (Database)          │
              └───────────────────────┘
                          │
              ┌───────────▼───────────┐
              │   File Storage        │
              │   (Volume/S3)         │
              └───────────────────────┘
```

## Monitoring & Logging

```
Application
    ├── Structured Logging (app/core/logging.py)
    ├── Error Tracking (Sentry - optional)
    ├── Performance Metrics
    │   ├── OCR processing time
    │   ├── AI API latency
    │   └── Endpoint response times
    └── Audit Logs
        ├── Document uploads
        ├── Processing events
        └── Comparison operations
```

## Configuration Management

```
.env
├── DATABASE_URL
├── OPENAI_API_KEY
├── OCR_LANGUAGE
├── MAX_UPLOAD_SIZE_MB
├── DOCUMENT_STORAGE_PATH
└── ALLOWED_DOCUMENT_TYPES
```

Tất cả cấu hình được quản lý tập trung trong `app/core/config.py` sử dụng Pydantic Settings.
