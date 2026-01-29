# Libraries and External Services Summary

This document provides a comprehensive overview of all libraries and external services used in the Document Comparison implementation, organized by step.

## Overview

The `/compare_document_contents` API endpoint uses a combination of Python standard libraries, third-party Python packages, and external services to perform document comparison with visual OCR.

## Step-by-Step Breakdown

### Step 1: Request Handling
- **Function**: `request.get_json()` (handled by FastAPI)
- **Libraries**: FastAPI framework (built-in)
- **External Services**: None

### Step 2: load_document_set(task_id)
- **Purpose**: Download files from MinIO storage to local directory
- **Python Libraries**:
  - `pathlib.Path` (Python standard library) - File path handling
  - `shutil` (Python standard library) - File operations
  - `minio` (Third-party) - MinIO client for object storage
- **External Services**:
  - **MinIO Server** - Object storage for document files
    - Downloads files from configured bucket (MINIO_BUCKET)
    - Stores locally in `/tmp/documents/{task_id}/`

### Step 3: classify_input_documents(task_id)
- **Purpose**: Classify documents by pattern matching
- **Python Libraries**:
  - `os` (Python standard library) - Directory scanning
  - `pathlib.Path` (Python standard library) - File path operations
  - `re` (Python standard library) - Regular expressions (implicit in pattern matching)
- **External Services**: None
- **Classification Patterns**:
  - settle_file_name: Contains "Settle" + .XLSX/.XLS
  - einvoice_file_name: Contains "VAT" or "E-INV" + .XML
  - cinvoice_file_name: Contains "CI" + .XLSX/.XLS
  - packing_list_file_name: Contains "PKL" + .XLSX/.XLS
  - cinvoice_plist_file_name: Contains "CI&PKL" + .XLSX/.XLS
  - export_CD_file_name: Contains "TKX" + .XLSX/.XLS (can be multiple)
  - PO_SO_file_name: Contains "PO", "SO", "PC", or "SC" + .XLSX/.XLS

### Step 4: CDP(task_id, excel_file_name, pdf_file_name)

#### Step 4.1: File Name Handling & Excel to PDF Conversion
- **Purpose**: Handle duplicate names and convert Excel to PDF
- **Python Libraries**:
  - `os` (Python standard library) - File operations
  - `subprocess` (Python standard library) - Execute system commands
  - `pathlib.Path` (Python standard library) - File path handling
- **External Services**:
  - **LibreOffice (soffice)** - Excel to PDF conversion
    - Command: `soffice --headless --convert-to pdf --outdir {dir} {file}`
    - Runs in headless mode (no GUI)
    - Timeout: 60 seconds

#### Step 4.2: Export PDF to Images
- **Purpose**: Convert PDF pages to JPG images with whitespace cropping
- **Python Libraries**:
  - `pdf2image` (Third-party) - PDF to image conversion
    - Function: `convert_from_path()`
    - Uses poppler-utils under the hood
  - `cv2` / `opencv-python` (Third-party) - Image processing
    - Used for whitespace detection and cropping
  - `numpy` (Third-party, dependency of opencv) - Array operations
  - `PIL` / `Pillow` (Third-party) - Image manipulation
- **External Services**: None (uses local system libraries)

#### Step 4.3: Extract Text (OCR) - extract_OCR_texts_2
- **Purpose**: Extract text and bounding boxes from images using AI
- **Python Libraries**:
  - `openai` (Third-party) - OpenAI SDK configured for custom endpoint
    - Function: `client.chat.completions.create()`
    - Configured with custom base_url for VLM endpoint
  - `base64` (Python standard library) - Image encoding
  - `re` (Python standard library) - JSON extraction from response
  - `time` (Python standard library) - Performance timing
  - `json` (Python standard library) - JSON parsing
- **External Services**:
  - **VLM API (Vision Language Model)**
    - Endpoint: Configured in `VLM_ENDPOINT` setting
    - Model: Configured in `VLM_ID` setting
    - Authentication: Uses `VLM_API_KEY` or falls back to `OPENAI_API_KEY`
    - Purpose: Text recognition and bounding box coordinate extraction
    - Input: Base64-encoded image
    - Output: JSON array with text and coordinates
    - Falls back to standard OpenAI GPT-4 Vision if VLM not configured

#### Step 4.4: Process Differences & Draw Bounding Boxes
- **Purpose**: Compare texts and draw red rectangles around differences
- **Python Libraries**:
  - `cv2` / `opencv-python` (Third-party) - Drawing operations
    - Function: `cv2.rectangle()` - Draw red bounding boxes
    - Function: `cv2.imread()`, `cv2.imwrite()` - Image I/O
  - `re` (Python standard library) - Text normalization
- **External Services**: None

#### Step 4.5: Save Images - save_image_to_storage
- **Purpose**: Upload annotated images to MinIO storage
- **Python Libraries**:
  - `minio` (Third-party) - MinIO client
  - `pathlib.Path` (Python standard library) - File path operations
- **External Services**:
  - **MinIO Server** - Object storage for processed images
    - Bucket: `vpas-output` (configured in MINIO_OUTPUT_BUCKET)
    - Path: `{task_id}/{filename}`
    - Content-Type: `image/jpeg`

## Complete Library List

### Python Standard Libraries (Built-in)
1. `os` - Operating system interface
2. `subprocess` - Subprocess management
3. `pathlib` - Object-oriented filesystem paths
4. `base64` - Base64 encoding/decoding
5. `re` - Regular expressions
6. `time` - Time-related functions
7. `json` - JSON parsing and generation
8. `shutil` - High-level file operations

### Third-Party Python Packages
1. `pdf2image>=1.16.0` - PDF to image conversion
2. `opencv-python>=4.8.0` - Computer vision and image processing
3. `minio>=7.2.0` - MinIO object storage client
4. `openai>=1.12.0` - OpenAI/VLM API client
5. `Pillow>=10.0.0` - Python Imaging Library
6. `numpy>=1.24.0` - Numerical computing (opencv dependency)

### System Dependencies
1. **LibreOffice** - Office suite for document conversion
   - Package: `libreoffice`
   - Command: `soffice`
   - Used for: Excel to PDF conversion

2. **Poppler Utils** - PDF rendering library
   - Package: `poppler-utils`
   - Used by: `pdf2image` for PDF processing
   - Commands: `pdftoppm`, `pdftocairo`

## External Services

### 1. LibreOffice (Local System Service)
- **Type**: Local command-line tool
- **Purpose**: Convert Excel files to PDF format
- **Configuration**: System installation required
- **Usage**: Called via subprocess.run()
- **Mode**: Headless (no GUI)

### 2. VLM API (Remote AI Service)
- **Type**: HTTP API endpoint
- **Purpose**: Vision Language Model for OCR with bounding boxes
- **Configuration**:
  - `VLM_ENDPOINT` - API base URL
  - `VLM_ID` - Model identifier
  - `VLM_API_KEY` - Authentication key
- **Input**: Base64-encoded images
- **Output**: JSON with text and bounding box coordinates
- **Fallback**: OpenAI GPT-4 Vision if VLM not configured

### 3. MinIO Server (Remote Object Storage)
- **Type**: S3-compatible object storage
- **Purpose**: Store input and output files
- **Configuration**:
  - `MINIO_ENDPOINT` - Server address
  - `MINIO_ACCESS_KEY` - Access key
  - `MINIO_SECRET_KEY` - Secret key
  - `MINIO_BUCKET` - Input bucket name (default: "documents")
  - `MINIO_OUTPUT_BUCKET` - Output bucket name (default: "vpas-output")
- **Buckets**:
  - Input: Stores original Excel and PDF files
  - Output: Stores annotated comparison images

## Configuration Summary

### Required Environment Variables

```env
# VLM API Configuration
VLM_ENDPOINT=https://your-vlm-endpoint.com/v1
VLM_ID=your-vlm-model-id
VLM_API_KEY=your-api-key

# MinIO Configuration
MINIO_ENDPOINT=your-minio-server:9000
MINIO_ACCESS_KEY=your-access-key
MINIO_SECRET_KEY=your-secret-key
MINIO_BUCKET=documents
MINIO_OUTPUT_BUCKET=vpas-output

# Optional: OpenAI Fallback
OPENAI_API_KEY=your-openai-key
OPENAI_MODEL=gpt-4o
```

## Docker Installation

```dockerfile
FROM python:3.10

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libreoffice \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies installed via pip/uv from pyproject.toml
```

## Service Flow Diagram

```
Input Files (MinIO)
  ↓ (minio)
Local Storage (/tmp/documents/{task_id}/)
  ↓ (os, pathlib)
Classification (pattern matching)
  ↓ (subprocess)
Excel → PDF (LibreOffice)
  ↓ (pdf2image, cv2)
PDF → Images
  ↓ (openai, base64)
OCR Text Extraction (VLM API)
  ↓ (re, text comparison)
Find Differences
  ↓ (cv2)
Draw Bounding Boxes
  ↓ (minio)
Upload to Output Bucket (vpas-output)
```

## Performance Considerations

1. **LibreOffice**: Can be slow for large Excel files (timeout: 60s)
2. **VLM API**: Remote API calls add latency, consider caching or local models
3. **Image Processing**: Memory-intensive for high-DPI images
4. **MinIO**: Network latency for file downloads/uploads

## Error Handling

Each step includes comprehensive error handling:
- File not found errors
- LibreOffice conversion failures
- VLM API timeout/rate limits
- MinIO connection issues
- Image processing errors

All errors are logged with full context and propagated as appropriate HTTP exceptions.
