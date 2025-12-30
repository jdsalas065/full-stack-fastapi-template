# File Management CRUD API Implementation

This document describes the implementation of a file management system with CRUD operations using MinIO for storage, replacing the streaming approach with a temp file-based approach.

## Overview

The implementation provides:
1. **File Upload API**: Upload documents (Excel, PDF, Word, Images) to MinIO
2. **File Management**: List, view, download, and delete files
3. **Document Processing**: Extract content and fields from uploaded files
4. **Temp File Processing**: Files are downloaded to temp directory for processing (instead of streaming)

## Changes Made

### 1. Storage Service (`app/services/storage_service.py`)

#### New Methods:
- **`download_file_to_temp(object_name)`**: Downloads file from MinIO to temp directory
  - Returns: Path to temp file
  - Auto-cleanup on error
  - Preserves file extension

- **`upload_file(file_path, object_name, content_type)`**: Uploads file from local path to MinIO
  - Used for uploading user files
  - Supports content type specification

- **`delete_file(object_name)`**: Deletes file from MinIO storage

#### Modified:
- **`get_file_stream()`**: Marked as DEPRECATED, kept for backward compatibility

### 2. Document Processor (`app/services/document_processor.py`)

#### New Methods:
- **`process_file_from_path(file_path, file_name, file_type)`**: Process files from local path
  - Supports: Excel, PDF, Word (basic), Images
  - Returns structured data and extracted fields

- **`_process_excel_from_path()`**: Process Excel files from path
- **`_process_pdf_from_path()`**: Process PDF files from path
- **`_process_doc_from_path()`**: Process Word documents (placeholder)
- **`_process_image_from_path()`**: Process images using LLM OCR

#### Modified:
- **`_detect_file_type()`**: Now supports additional file types:
  - `.doc`, `.docx` → "docx"
  - `.png`, `.jpg`, `.jpeg`, `.bmp`, `.tiff`, `.gif` → "image"

- **`process_file()`**: Marked as DEPRECATED, kept for backward compatibility

### 3. File CRUD Operations (`app/crud/file.py`)

New in-memory file metadata storage:

```python
class FileCRUD:
    def create(user_id, filename, file_type, file_size, object_name)
    def get(file_id)
    def list_by_user(user_id)
    def delete(file_id)
    def update(file_id, **kwargs)
```

**Note**: Currently uses in-memory storage. Can be upgraded to SQLModel/database when needed.

### 4. File Schemas (`app/schemas/file.py`)

New Pydantic models:
- `FileUploadResponse`: Response after file upload
- `FileInfo`: File metadata
- `FileListResponse`: List of files with total count
- `FileDeleteResponse`: Deletion confirmation
- `FileProcessRequest`: Request to process a file
- `FileProcessResponse`: Processing results

### 5. File Management API (`app/api/routes/files.py`)

New endpoints:

#### POST `/api/v1/files/upload`
- Upload file to MinIO storage
- Validates file type and size (max 50MB)
- Supported formats: Excel, PDF, Word, Images
- Returns: File ID and metadata

#### GET `/api/v1/files`
- List all files for current user
- Returns: Array of file metadata

#### GET `/api/v1/files/{file_id}`
- Get file details
- Validates user ownership
- Returns: File metadata

#### GET `/api/v1/files/{file_id}/download`
- Download file
- Returns: File content as attachment

#### DELETE `/api/v1/files/{file_id}`
- Delete file from storage and metadata
- Validates user ownership

#### POST `/api/v1/files/{file_id}/process`
- Process file to extract content and fields
- Downloads to temp, processes, then cleans up
- Returns: Extracted data and fields

### 6. Updated Document Routes (`app/api/routes/document.py`)

Modified to use temp file approach:
- `process_document_submission`: Now downloads files to temp before processing
- `compare_document_contents`: Downloads both files to temp before comparison
- Automatic cleanup of temp files after processing

## Supported File Types

| Extension | Type | Processing Method |
|-----------|------|------------------|
| .xlsx, .xls | Excel | pandas/openpyxl |
| .pdf | PDF | PyMuPDF + LLM OCR |
| .doc, .docx | Word | Placeholder (needs python-docx) |
| .png, .jpg, .jpeg, .bmp, .tiff, .gif | Image | LLM OCR |

## Flow Comparison

### Old Flow (Streaming)
```
MinIO → BytesIO Stream → Process → Extract → Return
```

### New Flow (Temp Files)
```
MinIO → Download to Temp → Process from Path → Extract → Cleanup Temp → Return
```

## Benefits of Temp File Approach

1. **Better Memory Management**: Large files don't need to be kept in memory
2. **Library Compatibility**: Many libraries work better with file paths than streams
3. **Debugging**: Easier to inspect files during development
4. **Retry Logic**: Can retry processing without re-downloading
5. **Progress Tracking**: Can track file I/O progress

## User Authentication

Currently uses a placeholder function `get_current_user_id()` that returns `"default-user"`.

**TODO**: Replace with actual authentication using:
- JWT tokens
- FastAPI security dependencies
- User session management

## Database Migration Path

The current in-memory `FileCRUD` can be upgraded to SQLModel:

```python
from sqlmodel import Field, SQLModel

class FileDocument(SQLModel, table=True):
    __tablename__ = "files"
    
    file_id: str = Field(primary_key=True)
    user_id: str = Field(index=True)
    filename: str
    file_type: str
    file_size: int
    object_name: str
    uploaded_at: datetime
    updated_at: datetime
```

## Testing

Tests added in `tests/api/routes/test_files.py`:
- File upload with various types
- File listing
- File retrieval
- File deletion
- Validation tests

Run tests with:
```bash
cd backend
bash scripts/test.sh
```

## Configuration

File management uses existing MinIO settings from `.env`:
- `MINIO_ENDPOINT`: MinIO server endpoint
- `MINIO_ACCESS_KEY`: Access key
- `MINIO_SECRET_KEY`: Secret key
- `MINIO_SECURE`: Use HTTPS (true/false)
- `MINIO_BUCKET`: Bucket name for storing files

## API Examples

### Upload a File
```bash
curl -X POST "http://localhost:8000/api/v1/files/upload" \
  -F "file=@document.pdf"
```

### List Files
```bash
curl "http://localhost:8000/api/v1/files"
```

### Download File
```bash
curl "http://localhost:8000/api/v1/files/{file_id}/download" \
  -O -J
```

### Process File
```bash
curl -X POST "http://localhost:8000/api/v1/files/{file_id}/process" \
  -H "Content-Type: application/json" \
  -d '{"file_id": "123", "extract_fields": true}'
```

### Delete File
```bash
curl -X DELETE "http://localhost:8000/api/v1/files/{file_id}"
```

## Future Enhancements

1. **Authentication**: Implement proper user authentication
2. **Database**: Migrate from in-memory to SQLModel/PostgreSQL
3. **Batch Upload**: Support multiple file uploads at once
4. **File Sharing**: Share files between users
5. **Versioning**: Keep file version history
6. **Thumbnails**: Generate thumbnails for images/PDFs
7. **Search**: Full-text search across document contents
8. **Webhooks**: Notify when processing completes
9. **Quota Management**: User storage limits
10. **File Compression**: Automatic compression for large files

## Security Considerations

1. **File Validation**: Validates file types and sizes before upload
2. **User Ownership**: Verifies user owns files before access
3. **Temp File Cleanup**: Automatically cleans up temporary files
4. **Content Type Validation**: Validates MIME types
5. **Path Traversal Prevention**: Uses safe path operations

**TODO**: Add virus scanning for uploaded files

## Error Handling

All endpoints include comprehensive error handling:
- 400: Invalid file type or size
- 403: Access denied (wrong user)
- 404: File not found
- 413: File too large
- 500: Server errors with logging

## Temp File Management

Temp files are automatically cleaned up:
- After successful processing
- On error (in finally blocks)
- Uses Python's `tempfile.mkstemp()` for secure temp file creation
- Preserves file extensions for proper processing

## Logging

All operations are logged with appropriate levels:
- INFO: Successful operations
- WARNING: Non-critical issues (cleanup failures)
- ERROR: Critical failures with stack traces
