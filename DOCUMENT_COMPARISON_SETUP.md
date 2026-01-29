# Document Comparison Setup Guide

This document describes the setup and requirements for the Document Comparison feature in the `/compare_document_contents` API endpoint.

## Overview

The `/compare_document_contents` API endpoint implements a visual document comparison workflow that:
1. Downloads documents from MinIO storage to local directory
2. Classifies documents by pattern matching
3. Converts Excel files to PDF
4. Extracts text and bounding boxes using VLM (Vision Language Model) API
5. Compares documents and highlights differences
6. Returns annotated images with highlighted differences

## Libraries Used by Step

### Step 3: classify_input_documents(task_id)
- **Libraries**: `os` (Python standard library)
- **External Services**: None

### Step 4: CDP(task_id, excel_file_name, pdf_file_name)

#### 4.1 File Name Handling & Excel to PDF Conversion
- **Libraries**: `os`, `subprocess` (Python standard library)
- **External Service**: LibreOffice (soffice) - Converts Excel to PDF in headless mode

#### 4.2 Export PDF to Images
- **Libraries**: `pdf2image`, `cv2` (opencv-python) - PDF conversion and image processing (autocrop whitespace)
- **External Services**: None

#### 4.3 Extract Text (OCR) - extract_OCR_texts_2
- **Libraries**: `openai` (SDK configured for custom endpoint), `base64`, `re`, `time` (Python standard library)
- **External Service**: VLM Endpoint (Vision Language Model API) - Configured in settings (VLM_ENDPOINT and VLM_ID) for text recognition and bounding box coordinates from images

#### 4.4 Process Differences & Draw Boxes
- **Libraries**: `cv2` (opencv-python) - Draws rectangles (bounding boxes) at difference locations
- **External Services**: None

#### 4.5 Save Images - save_image_to_storage
- **Libraries**: `minio` (Python client for MinIO)
- **External Service**: MinIO Server - Upload processed images to object storage (bucket: vpas-output)

## Summary of Dependencies

### Main Python Libraries
- `os`, `subprocess` - File operations and system commands
- `pdf2image` - PDF to image conversion
- `opencv-python` (cv2) - Image processing and bounding box drawing
- `minio` - MinIO object storage client
- `openai` - API client for VLM endpoint

### External Services
1. **LibreOffice (soffice)** - Excel to PDF file conversion
2. **VLM API** - Vision Language Model for OCR with bounding boxes
3. **MinIO Server** - Object storage for input and output files
   - Input bucket: As configured in MINIO_BUCKET
   - Output bucket: vpas-output (for annotated images)

## System Dependencies

The document comparison feature requires the following system packages to be installed:

### LibreOffice (for Excel to PDF conversion)
```bash
# Ubuntu/Debian
apt-get update && apt-get install -y libreoffice

# Alpine (for Docker)
apk add --no-cache libreoffice

# macOS
brew install libreoffice
```

### Poppler (for PDF to image conversion)
```bash
# Ubuntu/Debian
apt-get update && apt-get install -y poppler-utils

# Alpine (for Docker)
apk add --no-cache poppler-utils

# macOS
brew install poppler
```

## Python Dependencies

The following Python packages are required (already added to `pyproject.toml`):
- `pdf2image>=1.16.0` - Convert PDF pages to images
- `opencv-python>=4.8.0` - Image processing and bounding box drawing
- `openai>=1.12.0` - OpenAI SDK (configured with custom VLM endpoint)

## Configuration

### Environment Variables

Add the following to your `.env` file:

```env
# VLM (Vision Language Model) Settings for OCR
VLM_ENDPOINT=https://your-vlm-api-endpoint.com/v1
VLM_ID=your-vlm-model-id
VLM_API_KEY=your-vlm-api-key

# MinIO Output Bucket
MINIO_OUTPUT_BUCKET=vpas-output

# Optional: OpenAI settings (if using standard OpenAI as fallback)
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4o
```

### VLM API Configuration

The VLM (Vision Language Model) API is used for OCR text extraction with bounding boxes. The system uses the OpenAI SDK configured with a custom endpoint:

- **VLM_ENDPOINT**: Base URL for the VLM API endpoint
- **VLM_ID**: Model identifier for the VLM
- **VLM_API_KEY**: API key for authentication (falls back to OPENAI_API_KEY if not set)

If VLM settings are not configured, the system will fall back to standard OpenAI GPT-4 Vision.

## Docker Setup

To use this feature in Docker, update the `backend/Dockerfile` to include system dependencies:

```dockerfile
FROM python:3.10

# Install system dependencies for document comparison
RUN apt-get update && apt-get install -y \
    libreoffice \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# ... rest of Dockerfile
```

## API Flow

### Endpoint: POST `/api/v1/document/compare_document_contents`

**Request Body:**
```json
{
  "task_id": "unique-task-id",
  "excel_file_name": "document.xlsx",
  "pdf_file_name": "document.pdf"
}
```

**Response (Status 201):**
```json
{
  "status": "compared",
  "result": {
    "task_id": "unique-task-id",
    "excel_file": "document.xlsx",
    "pdf_file": "document.pdf",
    "classified_documents": {
      "settle_file_name": "Settle_Report.xlsx",
      "cinvoice_file_name": "CI_Invoice.xlsx",
      ...
    },
    "result_images": [
      {
        "EXCEL": "document_page_1_with_bboxes.jpg",
        "PDF": "document_page_1_with_bboxes.jpg"
      },
      {
        "EXCEL": "document_page_2_with_bboxes.jpg",
        "PDF": "document_page_2_with_bboxes.jpg"
      }
    ]
  }
}
```

## Document Classification Patterns

The `classify_input_documents` function classifies documents based on filename patterns:

| Document Type | Pattern | Extensions |
|--------------|---------|------------|
| Settle | Contains "Settle" | .XLSX, .XLS |
| E-Invoice | Contains "VAT" or "E-INV" | .XML |
| Commercial Invoice | Contains "CI" | .XLSX, .XLS |
| Packing List | Contains "PKL" | .XLSX, .XLS |
| CI & PKL Combined | Contains "CI&PKL" | .XLSX, .XLS |
| Export CD | Contains "TKX" | .XLSX, .XLS |
| PO/SO | Contains "PO", "SO", "PC", or "SC" | .XLSX, .XLS |

## Comparison Process

The `compare_document_pair` (CDP) function performs the following steps:

1. **Handle Duplicate Names**: If Excel and PDF have the same base name, renames Excel file to avoid collision
2. **Convert Excel to PDF**: Uses LibreOffice headless mode (`soffice --headless`)
3. **Export PDFs to Images**: Converts both PDFs to JPG images using pdf2image
4. **Validate Page Count**: Ensures both documents have the same number of pages
5. **Extract OCR Text**: Uses VLM API to extract text and bounding boxes from each page
6. **Find Differences**: Compares normalized text (uppercase, no spaces) between documents
7. **Draw Bounding Boxes**: Highlights differences with red rectangles using OpenCV
8. **Upload to Storage**: Saves annotated images to MinIO output bucket (vpas-output)

## Storage

- **Input Files**: Downloaded from MinIO bucket to `/tmp/documents/{task_id}/`
- **Output Files**: Uploaded to MinIO output bucket `vpas-output` at `{task_id}/{filename}`
- **Buckets**: 
  - Input: Configured in `MINIO_BUCKET` (default: "documents")
  - Output: Configured in `MINIO_OUTPUT_BUCKET` (default: "vpas-output")

## Error Handling

- **FileNotFoundError**: Returns 404 if documents not found
- **ValueError**: Returns 503 if page counts don't match
- **VLM API Errors**: Returns 503 with error details if OCR fails
- **General Errors**: Returns 503 with error details

## Testing

To test the endpoint:

1. Upload Excel and PDF files to MinIO under a task_id
2. Configure VLM API settings in environment variables
3. Call the API endpoint with the task_id and file names
4. Check the response for `result_images` array
5. Download the annotated images from MinIO output bucket to verify highlights

## Performance Considerations

- VLM API calls can be time-intensive for large documents
- Consider implementing background task processing for large documents
- Temp files are stored in `/tmp/documents/` and should be cleaned up periodically
- Image resolution (DPI) affects both quality and processing time (default: 200 DPI)
- VLM API may have rate limits - implement appropriate retry logic
