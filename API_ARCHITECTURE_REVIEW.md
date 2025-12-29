# 📋 Review Architecture & Flow cho 2 APIs

## Tổng Quan

Review về flow, architecture, storage solution, và libraries cho:
1. `/process_document_submission` - Load và so sánh documents
2. `/compare_document_contents` - Convert, OCR, và compare với LLM

---

## 🔍 API 1: `/process_document_submission`

### Current Flow:
```
1. Load documents từ MinIO (theo task_id)
   ↓
2. Download về local filesystem (/tmp/documents/{task_id})
   ↓
3. Classify documents (placeholder - chưa implement)
   ↓
4. Check documents - validate và cross-reference
   ↓
5. Return results
```

### ✅ Điểm Tốt:
- Async/await pattern đúng
- Error handling có
- Logging đầy đủ
- Task-specific directories (isolation)

### ⚠️ Vấn Đề:

#### 1. **Storage Flow - Download về Local Filesystem**
```python
# Current: Download tất cả về /tmp/documents/{task_id}
task_dir = Path(BASE_DOCUMENT_PATH) / task_id
task_dir.mkdir(parents=True, exist_ok=True)
```

**Vấn đề:**
- ❌ Tốn disk space (files lớn)
- ❌ Không scale được (nhiều concurrent requests)
- ❌ Cleanup không rõ ràng (có thể leak disk space)
- ❌ Không phù hợp với containerized environment (ephemeral storage)

**Solution đề xuất:**
```python
# Option 1: Process trực tiếp từ MinIO (streaming)
async def process_from_minio_stream(task_id: str):
    minio_client = get_minio_client()
    obj = minio_client.get_object(bucket, object_name)
    # Process stream without saving to disk
    
# Option 2: Temporary storage với auto-cleanup
from tempfile import TemporaryDirectory
with TemporaryDirectory() as tmpdir:
    # Process files
    # Auto cleanup khi xong
```

#### 2. **Document Classification - Chưa Implement**
```python
def classify_input_documents(task_id: str) -> dict[str, Any]:
    # Placeholder implementation
    return {"task_id": task_id, "classification": "pending"}
```

**Cần làm rõ:**
- Classification dùng gì? (file extension, content analysis, ML model?)
- Output format như thế nào?

#### 3. **Field Comparison Logic - Chưa Rõ**
```python
def check_documents(task_id: str, document_names: dict[str, Any]):
    # TODO: Extract and compare amounts
    # TODO: Extract and compare line items
```

**Cần làm rõ:**
- So sánh structured data (parse Excel/PDF) hay chỉ text comparison?
- Cần extract fields cụ thể nào? (amounts, dates, line items, etc.)

---

## 🔍 API 2: `/compare_document_contents`

### Current Flow:
```
1. Load documents từ MinIO
   ↓
2. Download về local
   ↓
3. Convert Excel → PDF (chưa implement)
   ↓
4. Convert PDF → Images (chưa implement)
   ↓
5. OCR extraction (chưa implement)
   ↓
6. Compare OCR texts (chưa implement, chỉ placeholder)
   ↓
7. Return results
```

### ⚠️ Vấn Đề Nghiêm Trọng:

#### 1. **LLM Integration - CHƯA CÓ**
```python
# Current: Chỉ có OCR text comparison
comparison_result = compare_ocr_texts(excel_texts, pdf_texts)
# ❌ Không có LLM để semantic comparison
```

**Requirement bạn nói:** "dùng ocr và mô hình llm để compare"

**Solution cần:**
```python
# app/services/llm_comparison.py
from openai import OpenAI  # hoặc Anthropic, etc.

async def compare_with_llm(
    excel_texts: list[dict],
    pdf_texts: list[dict],
    comparison_prompt: str
) -> dict:
    """
    Dùng LLM để so sánh semantic, extract fields, và tìm differences.
    """
    client = OpenAI()
    
    # Prepare context
    excel_content = "\n".join([t["text"] for t in excel_texts])
    pdf_content = "\n".join([t["text"] for t in pdf_texts])
    
    response = client.chat.completions.create(
        model="gpt-4o",  # hoặc gpt-4-vision nếu cần xem images
        messages=[
            {
                "role": "system",
                "content": "You are an expert at comparing financial documents..."
            },
            {
                "role": "user",
                "content": f"""
                Compare these two documents:
                
                Excel Document:
                {excel_content}
                
                PDF Document:
                {pdf_content}
                
                Extract and compare:
                1. Amounts
                2. Dates
                3. Line items
                4. Any discrepancies
                """
            }
        ],
        response_format={"type": "json_object"}
    )
    
    return json.loads(response.choices[0].message.content)
```

#### 2. **OCR Tools - Tất Cả Chưa Implement**
```python
# app/services/ocr_tools.py
def convert_excel_to_pdf(...) -> Path:
    # TODO: Implement
    logger.warning("Excel to PDF conversion not implemented")
    return pdf_path  # ❌ File không tồn tại

def convert_pdf_to_images(...) -> list[Image.Image]:
    # TODO: Implement
    logger.warning("PDF to images conversion not implemented")
    return []  # ❌ Empty list

def extract_ocr_texts(...) -> list[dict]:
    # TODO: Implement
    return []  # ❌ Empty results
```

**Solution cần implement:**

```python
# Option 1: LibreOffice (đơn giản, cross-platform)
def convert_excel_to_pdf(excel_path: Path) -> Path:
    import subprocess
    pdf_path = excel_path.with_suffix('.pdf')
    subprocess.run([
        'libreoffice', '--headless', '--convert-to', 'pdf',
        '--outdir', str(excel_path.parent),
        str(excel_path)
    ], check=True)
    return pdf_path

# Option 2: pdf2image (cần poppler)
def convert_pdf_to_images(pdf_path: Path, dpi: int = 200):
    from pdf2image import convert_from_path
    return convert_from_path(str(pdf_path), dpi=dpi)

# Option 3: PyMuPDF (fitz) - không cần system dependencies
def convert_pdf_to_images(pdf_path: Path):
    import fitz  # PyMuPDF
    doc = fitz.open(str(pdf_path))
    images = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        pix = page.get_pixmap(dpi=200)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        images.append(img)
    return images

# OCR: pytesseract hoặc cloud APIs
def extract_ocr_texts(images: list[Image.Image]):
    import pytesseract
    results = []
    for idx, image in enumerate(images):
        text = pytesseract.image_to_string(image)
        data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
        results.append({
            "page_num": idx,
            "text": text,
            "confidence": sum(data['conf']) / len(data['conf']) if data['conf'] else 0,
            "words": data['text']
        })
    return results
```

#### 3. **Flow Architecture - Có Vấn Đề**

**Current flow có vấn đề:**
```
MinIO → Download to /tmp → Convert → Images → OCR → Compare
         ↑
         ❌ Tốn disk, không scale
```

**Better flow:**
```
MinIO → Stream/Process → Convert (in-memory or temp) → OCR → LLM → Results
         ↑
         ✅ Không cần persistent storage
```

---

## 📦 Storage Solution Review

### MinIO (Object Storage) - ✅ Tốt

**Điểm tốt:**
- ✅ S3-compatible API
- ✅ Scalable
- ✅ Phù hợp cho file storage
- ✅ Có thể dùng AWS S3, GCS thay thế

**Vấn đề implementation:**
- ❌ Config hardcoded (cần move to env vars)
- ❌ Client chưa initialize (placeholder)
- ❌ Không có connection pooling/retry logic

**Solution:**
```python
# app/core/storage.py
from minio import Minio
from minio.error import S3Error
from app.core.config import settings

class StorageService:
    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE
        )
    
    async def get_file_stream(self, bucket: str, object_name: str):
        """Get file as stream without downloading"""
        return self.client.get_object(bucket, object_name)
    
    async def download_to_temp(self, bucket: str, object_name: str) -> Path:
        """Download to temporary file with auto-cleanup"""
        import tempfile
        tmp_file = tempfile.NamedTemporaryFile(delete=False)
        obj = self.client.get_object(bucket, object_name)
        tmp_file.write(obj.read())
        obj.close()
        return Path(tmp_file.name)
```

---

## 🏗️ Architecture Issues

### 1. **Synchronous Operations trong Async Context**

```python
# Current: Blocking operations
excel_pdf_path = convert_excel_to_pdf(excel_path)  # ❌ Blocking
excel_images = convert_pdf_to_images(excel_pdf_path)  # ❌ Blocking
```

**Solution:**
```python
# Use asyncio.to_thread for CPU-bound tasks
excel_pdf_path = await asyncio.to_thread(
    convert_excel_to_pdf, excel_path
)

# Or use ProcessPoolExecutor for heavy tasks
from concurrent.futures import ProcessPoolExecutor
with ProcessPoolExecutor() as executor:
    excel_images = await asyncio.get_event_loop().run_in_executor(
        executor, convert_pdf_to_images, excel_pdf_path
    )
```

### 2. **Error Handling - Không Đầy Đủ**

```python
# Current: Generic exception handling
except Exception as e:
    return {"comparison_status": "error", "error": str(e)}
```

**Cần:**
- Specific exception types
- Retry logic cho network operations
- Graceful degradation

### 3. **Resource Cleanup - Không Rõ Ràng**

```python
# Current: Files tồn tại trong /tmp/documents/{task_id}
# Không có cleanup mechanism
```

**Solution:**
```python
from contextlib import asynccontextmanager
from tempfile import TemporaryDirectory

@asynccontextmanager
async def temporary_document_workspace(task_id: str):
    """Auto-cleanup workspace"""
    with TemporaryDirectory(prefix=f"task_{task_id}_") as tmpdir:
        yield Path(tmpdir)
        # Auto cleanup khi exit context
```

---

## 📚 Libraries Review

### ✅ Libraries Được Chọn - Tốt:
1. **pdf2image** - PDF to images (cần poppler)
2. **pytesseract** - OCR (cần tesseract)
3. **Pillow** - Image processing
4. **openpyxl** - Excel parsing

### ⚠️ Cần Thêm:
1. **LLM Client** - OpenAI, Anthropic, hoặc local LLM
2. **LibreOffice** - Excel to PDF conversion (hoặc alternative)
3. **PyMuPDF (fitz)** - Alternative PDF processing (không cần system deps)

### 🔄 Alternative Libraries:

**Excel to PDF:**
- ✅ LibreOffice (subprocess) - Free, cross-platform
- ✅ win32com (Windows only) - Native Excel
- ⚠️ openpyxl + reportlab - Phức tạp, layout khó giữ

**PDF to Images:**
- ✅ pdf2image - Standard, cần poppler
- ✅ PyMuPDF (fitz) - Không cần system deps, nhanh hơn
- ⚠️ wand (ImageMagick) - Nặng

**OCR:**
- ✅ pytesseract - Free, local
- ✅ EasyOCR - Deep learning, chính xác hơn
- ✅ Google Cloud Vision API - Cloud, rất chính xác
- ✅ AWS Textract - Cloud, tốt cho forms/tables

**LLM:**
- ✅ OpenAI GPT-4/GPT-4o - Best for structured output
- ✅ Anthropic Claude - Good for long documents
- ✅ Local LLM (Ollama, llama.cpp) - Privacy, cost-effective

---

## 🎯 Recommended Architecture

### Flow Mới (Improved):

```
┌─────────────────────────────────────────────────────────┐
│                    API Request                           │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│        1. Load Metadata từ MinIO (không download)       │
│           - List objects theo task_id                   │
│           - Get file metadata                           │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│    2. Process Files (Streaming hoặc Temp Storage)      │
│       Option A: Stream từ MinIO → Process              │
│       Option B: Download to temp (auto-cleanup)          │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│    3. Convert & Extract (Parallel nếu có thể)          │
│       - Excel → PDF (LibreOffice hoặc in-memory)       │
│       - PDF → Images (pdf2image hoặc PyMuPDF)           │
│       - OCR Extraction (pytesseract hoặc cloud API)      │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│    4. LLM Comparison (Async)                            │
│       - Prepare context từ OCR results                  │
│       - Call LLM API (OpenAI, Anthropic, etc.)         │
│       - Parse structured response                       │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│    5. Return Results                                     │
│       - Cleanup temp files                              │
│       - Return comparison results                        │
└─────────────────────────────────────────────────────────┘
```

---

## ✅ Solutions Đề Xuất

### 1. **Storage Service Layer**
```python
# app/services/storage_service.py
class StorageService:
    async def get_file_stream(self, bucket, object_name):
        """Stream file without downloading"""
        pass
    
    async def process_file_in_memory(self, bucket, object_name, processor):
        """Process file in memory"""
        pass
```

### 2. **Document Processing Pipeline**
```python
# app/services/document_pipeline.py
class DocumentPipeline:
    async def process(self, task_id: str):
        # 1. Load metadata
        # 2. Process files (streaming)
        # 3. Convert & OCR (parallel)
        # 4. LLM comparison
        # 5. Return results
        pass
```

### 3. **LLM Integration Service**
```python
# app/services/llm_service.py
class LLMComparisonService:
    async def compare_documents(self, excel_texts, pdf_texts):
        """Use LLM to compare documents semantically"""
        pass
```

### 4. **Background Task Processing**
```python
# Long-running tasks nên dùng background jobs
from fastapi import BackgroundTasks

@router.post("/compare_document_contents")
async def compare_document_contents(
    payload: CompareDocumentRequest,
    background_tasks: BackgroundTasks
):
    # Start background task
    task_id = create_task()
    background_tasks.add_task(process_comparison, task_id, payload)
    return {"task_id": task_id, "status": "processing"}
```

---

## ❓ Questions Cần Làm Rõ

1. **`/process_document_submission`:**
   - So sánh "các trường" là structured data comparison hay text comparison?
   - Input là 2 files hay nhiều files?
   - Cần extract fields cụ thể nào?

2. **`/compare_document_contents`:**
   - LLM dùng để làm gì? (semantic comparison, field extraction, etc.)
   - Output format mong muốn?
   - Có cần streaming response không? (long-running task)

3. **Storage:**
   - Có cần download về local không?
   - Files sau khi process có cần lưu lại không?

---

## 📝 Tóm Tắt

### ✅ Điểm Tốt:
- Architecture tổng thể OK
- MinIO storage phù hợp
- Async patterns đúng

### ❌ Vấn Đề:
- ❌ Tất cả OCR tools chưa implement
- ❌ LLM integration chưa có
- ❌ Download về local filesystem không scale
- ❌ Classification logic chưa có
- ❌ Field comparison logic chưa rõ

### 🎯 Cần Làm:
1. Implement OCR tools (hoặc dùng cloud APIs)
2. Thêm LLM service cho comparison
3. Refactor storage flow (streaming hoặc temp với cleanup)
4. Implement classification logic
5. Implement field extraction & comparison

---

**Vui lòng trả lời các câu hỏi ở trên để tôi có thể đưa ra solutions chi tiết hơn!**

