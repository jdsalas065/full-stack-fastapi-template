# Document Comparison Setup Guide

This document describes the setup and requirements for the Document Comparison feature in the `/compare_document_contents` API endpoint.

## Overview

The `/compare_document_contents` API endpoint implements a visual document comparison workflow that:
1. Downloads documents from MinIO storage to local directory
2. Classifies documents by pattern matching
3. Converts Excel files to PDF
4. Extracts text and bounding boxes using OCR
5. Compares documents and highlights differences
6. Returns annotated images with highlighted differences

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

### Tesseract OCR (for text extraction)
```bash
# Ubuntu/Debian
apt-get update && apt-get install -y tesseract-ocr

# Alpine (for Docker)
apk add --no-cache tesseract-ocr

# macOS
brew install tesseract
```

## Python Dependencies

The following Python packages are required (already added to `pyproject.toml`):
- `pdf2image>=1.16.0` - Convert PDF pages to images
- `pytesseract>=0.3.10` - OCR text extraction
- `opencv-python>=4.8.0` - Image processing and bounding box drawing

## Docker Setup

To use this feature in Docker, update the `backend/Dockerfile` to include system dependencies:

```dockerfile
FROM python:3.10

# Install system dependencies for document comparison
RUN apt-get update && apt-get install -y \
    libreoffice \
    poppler-utils \
    tesseract-ocr \
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
5. **Extract OCR Text**: Uses Tesseract to extract text and bounding boxes from each page
6. **Find Differences**: Compares normalized text (uppercase, no spaces) between documents
7. **Draw Bounding Boxes**: Highlights differences with red rectangles using OpenCV
8. **Upload to Storage**: Saves annotated images to MinIO bucket

## Storage

- **Input Files**: Downloaded from MinIO bucket to `/tmp/documents/{task_id}/`
- **Output Files**: Uploaded to MinIO bucket at `{task_id}/{filename}`
- **Bucket**: Uses the configured MinIO bucket (default: as per `settings.MINIO_BUCKET`)

## Error Handling

- **FileNotFoundError**: Returns 404 if documents not found
- **ValueError**: Returns 503 if page counts don't match
- **General Errors**: Returns 503 with error details

## Testing

To test the endpoint:

1. Upload Excel and PDF files to MinIO under a task_id
2. Call the API endpoint with the task_id and file names
3. Check the response for `result_images` array
4. Download the annotated images from MinIO to verify highlights

## Performance Considerations

- OCR processing can be CPU-intensive for large documents
- Consider implementing background task processing for large documents
- Temp files are stored in `/tmp/documents/` and should be cleaned up periodically
- Image resolution (DPI) affects both quality and processing time (default: 200 DPI)
