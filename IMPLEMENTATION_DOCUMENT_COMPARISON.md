# Implementation Summary: Document Comparison Flow

## Overview

This implementation adds a comprehensive document comparison flow to the `/compare_document_contents` API endpoint, following the specified Vietnamese requirements.

## What Was Implemented

### 1. New Module: `app/services/document_comparison.py`

This module contains all the core functionality for document comparison:

#### Key Functions:

- **`load_document_set(task_id)`**: 
  - Downloads all files from MinIO storage for a given task_id
  - Stores files in local directory: `/tmp/documents/{task_id}/`
  - Returns the Path to the local directory

- **`classify_input_documents(task_id)`**:
  - Scans local directory for document files
  - Classifies by pattern matching based on filename and extension:
    - `settle_file_name`: Contains "Settle" + .XLSX/.XLS
    - `einvoice_file_name`: Contains "VAT" or "E-INV" + .XML
    - `cinvoice_file_name`: Contains "CI" + .XLSX/.XLS
    - `packing_list_file_name`: Contains "PKL" + .XLSX/.XLS
    - `cinvoice_plist_file_name`: Contains "CI&PKL" + .XLSX/.XLS
    - `export_CD_file_name`: Contains "TKX" + .XLSX/.XLS (can be multiple)
    - `PO_SO_file_name`: Contains "PO"/"SO"/"PC"/"SC" + .XLSX/.XLS
  - Returns dictionary with classified document names

- **`compare_document_pair(task_id, excel_file_name, pdf_file_name)` (CDP)**:
  - Main comparison function with the following steps:
    1. **Handle duplicate names**: Renames Excel file if it has same name as PDF
    2. **Convert Excel to PDF**: Uses LibreOffice (`soffice --headless`)
    3. **Export PDFs to images**: Converts both PDFs to JPG using pdf2image
    4. **Validate page count**: Ensures both documents have same number of pages
    5. **Loop through each page**:
       - Extract OCR text and bounding boxes using `extract_OCR_texts_2`
       - Find text differences using `find_text_differences`
       - Draw bounding boxes on differences using `draw_bounding_boxes`
       - Upload annotated images to MinIO using `save_image_to_storage`
    6. **Return result_images**: List of dictionaries with EXCEL and PDF image names

#### Supporting Functions:

- **`convert_excel_to_pdf(excel_path)`**: Uses LibreOffice to convert Excel to PDF
- **`export_pdf_to_images(pdf_path, dpi=200)`**: Converts PDF pages to JPG images with cropping
- **`extract_OCR_texts_2(image_path)`**: Extracts text and bounding boxes using Tesseract OCR
- **`find_text_differences(texts1, texts2)`**: Compares normalized texts (uppercase, no spaces)
- **`draw_bounding_boxes(image_path, bboxes, indices)`**: Draws red rectangles around differences using OpenCV
- **`save_image_to_storage(task_id, image_path)`**: Uploads images to MinIO

### 2. Updated API Endpoint: `/compare_document_contents`

**Changes to `backend/app/api/routes/document.py`:**

- Changed status code from `HTTP_200_OK` to `HTTP_201_CREATED`
- Updated flow to use the new document comparison functions:
  1. Load document set from MinIO
  2. Classify documents
  3. Compare document pair
  4. Return result_images
- Response format now includes:
  ```json
  {
    "status": "compared",
    "result": {
      "task_id": "...",
      "excel_file": "...",
      "pdf_file": "...",
      "classified_documents": {...},
      "result_images": [
        {"EXCEL": "..._page_1_with_bboxes.jpg", "PDF": "..._page_1_with_bboxes.jpg"},
        {"EXCEL": "..._page_2_with_bboxes.jpg", "PDF": "..._page_2_with_bboxes.jpg"}
      ]
    }
  }
  ```

### 3. Dependencies Added

**Python packages** (in `pyproject.toml`):
- `pdf2image>=1.16.0` - Convert PDF to images
- `pytesseract>=0.3.10` - OCR text extraction
- `opencv-python>=4.8.0` - Image processing and bounding boxes

**System packages** (in `Dockerfile`):
- `libreoffice` - Excel to PDF conversion
- `poppler-utils` - PDF processing (required by pdf2image)
- `tesseract-ocr` - OCR engine

### 4. Documentation

**Created `DOCUMENT_COMPARISON_SETUP.md`:**
- Complete setup guide
- System dependency installation instructions
- API flow documentation
- Document classification patterns
- Error handling
- Testing guidelines
- Performance considerations

### 5. Tests Updated

**Modified `backend/tests/api/routes/test_document.py`:**
- Updated test to expect status code 201 instead of 200 for successful comparisons

## Result Images Format

The `result_images` returned by the API is a list of dictionaries, one for each page:

```python
[
  {
    "EXCEL": "excel_file_page_1_with_bboxes.jpg",
    "PDF": "pdf_file_page_1_with_bboxes.jpg"
  },
  {
    "EXCEL": "excel_file_page_2_with_bboxes.jpg",
    "PDF": "pdf_file_page_2_with_bboxes.jpg"
  }
]
```

These image files are uploaded to MinIO at: `{task_id}/{filename}`

## How It Works

1. **User sends request** with task_id, excel_file_name, pdf_file_name
2. **API downloads files** from MinIO to local directory `/tmp/documents/{task_id}/`
3. **API classifies** all documents in the directory by pattern
4. **API compares** specified Excel and PDF files:
   - Converts Excel to PDF
   - Generates images from both PDFs
   - Extracts text using OCR
   - Finds differences
   - Draws red bounding boxes around differences
   - Uploads annotated images to MinIO
5. **API returns** result with classified documents and result_images list

## Security

- No security vulnerabilities detected by CodeQL
- All file operations use temp directories that are cleaned up
- MinIO credentials use existing secure storage service

## Next Steps for Deployment

1. **Build Docker image** with updated Dockerfile
2. **Verify system dependencies** are properly installed:
   ```bash
   docker run <image> soffice --version
   docker run <image> pdftoppm -v
   docker run <image> tesseract --version
   ```
3. **Test the endpoint** with sample documents
4. **Monitor performance** for large documents (may need background tasks)

## Files Changed

- `backend/app/services/document_comparison.py` (NEW) - 575 lines
- `backend/app/api/routes/document.py` - Updated endpoint
- `backend/pyproject.toml` - Added Python dependencies
- `backend/Dockerfile` - Added system dependencies
- `backend/tests/api/routes/test_document.py` - Updated test
- `DOCUMENT_COMPARISON_SETUP.md` (NEW) - Documentation

## Total Changes

- 804 insertions, 59 deletions
- 2 new files
- 4 modified files
