# MinIO Object Naming Migration Guide

## Overview
This document describes the changes made to implement consistent MinIO object naming using `task_id` prefixes for document processing workflows.

## Changes Made

### 1. Database Schema Changes

#### File Model (`backend/app/models/file.py`)
- Added `task_id` field (optional, indexed)
- Type: `str | None`
- Purpose: Links files to document processing tasks

#### Database Migration (`backend/app/alembic/versions/20260106_070400_add_task_id_to_file.py`)
- Adds `task_id` column to the `file` table
- Creates index on `task_id` for efficient lookups
- Nullable to support both new (task-based) and legacy (user-based) uploads

### 2. API Changes

#### File Upload Endpoint (`POST /api/v1/files/upload`)
- **New Query Parameter**: `task_id` (optional)
- **Behavior**:
  - With `task_id`: Stores file as `{task_id}/{filename}` in MinIO
  - Without `task_id`: Stores file as `{user_id}/{filename}` in MinIO (legacy behavior)
- **Validation**: Rejects empty or whitespace-only `task_id` values

#### Response Schema Updates
- `FileUploadResponse`: Added `task_id` field
- `FileInfo`: Added `task_id` field

### 3. CRUD Operations (`backend/app/crud/file.py`)
- Updated `create()` to accept optional `task_id` parameter
- Added `list_by_task_id()` function for querying files by task

### 4. MinIO Object Naming Convention

#### New Convention
```
documents/
├── {task_id}/
│   ├── file1.xlsx
│   ├── file2.pdf
│   └── ocr_results.json
└── {user_id}/
    └── personal_file.pdf
```

#### Usage
- **Document Processing**: Use `task_id` prefix
- **General File Storage**: Use `user_id` prefix (default)

## Migration Steps

### For New Deployments
1. Run database migration:
   ```bash
   cd backend
   alembic upgrade head
   ```

### For Existing Deployments

#### 1. Apply Database Migration
```bash
cd backend
alembic upgrade head
```

#### 2. Handle Existing Files (Optional)
Existing files stored with `{user_id}/{filename}` pattern will continue to work for general file operations. For document processing workflows:

**Option A**: Upload new files with `task_id`
- Upload files for document processing with `task_id` parameter
- Old files remain accessible via file management APIs

**Option B**: Migrate existing files (manual process)
- If you have existing files that should be used for document processing, you'll need to:
  1. Copy/move them in MinIO to new `{task_id}/{filename}` paths
  2. Update their database records with the new `object_name` and `task_id`

## API Usage Examples

### Upload File for Document Processing
```bash
# Upload Excel file
curl -X POST "http://localhost/api/v1/files/upload?task_id=invoice-batch-001" \
  -F "file=@invoice.xlsx"

# Upload PDF file
curl -X POST "http://localhost/api/v1/files/upload?task_id=invoice-batch-001" \
  -F "file=@invoice.pdf"
```

### Upload File for General Storage
```bash
# No task_id - uses user_id prefix
curl -X POST "http://localhost/api/v1/files/upload" \
  -F "file=@document.pdf"
```

### Process Documents
```bash
# Process all files for a task
curl -X POST "http://localhost/api/v1/document/process_document_submission" \
  -H "Content-Type: application/json" \
  -d '{"task_id": "invoice-batch-001"}'

# Compare specific documents
curl -X POST "http://localhost/api/v1/document/compare_document_contents" \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "invoice-batch-001",
    "excel_file_name": "invoice.xlsx",
    "pdf_file_name": "invoice.pdf"
  }'
```

## Testing

### Validation Tests
The following test scenarios are covered:
1. Upload file without `task_id` (legacy behavior)
2. Upload file with `task_id` (new behavior)
3. Upload file with empty `task_id` (validation error)
4. Upload multiple files with same `task_id`
5. Document processing with task-based files

### Running Tests
```bash
cd backend
source .venv/bin/activate
pytest tests/api/routes/test_files.py -v
pytest tests/api/routes/test_document.py -v
```

**Note**: Tests that interact with MinIO require MinIO to be running. Use Docker Compose:
```bash
docker-compose up -d minio
```

## Backward Compatibility

### What Still Works
- Existing file upload API without `task_id` parameter
- Existing files stored with `{user_id}/{filename}` pattern
- All file management operations (list, get, delete, download)

### What Requires Changes
- Document processing workflows now require files to be uploaded with `task_id`
- Applications using document comparison/processing APIs must upload files with `task_id` parameter

## Security Considerations

### Validation
- `task_id` must be non-empty when provided
- File size limits still apply (50MB default)
- File type restrictions still enforced

### Access Control
- Current implementation uses a default user ID
- **TODO**: Integrate with actual authentication system
- Consider adding `task_id` ownership validation

## Performance Notes

- Added index on `task_id` column for efficient queries
- MinIO prefix-based listing is optimized for task-based queries
- No performance impact on legacy upload flows

## Troubleshooting

### Files Not Found for Document Processing
**Symptom**: 404 error when calling document processing APIs

**Solutions**:
1. Verify files were uploaded with correct `task_id`
2. Check MinIO object names match `{task_id}/{filename}` pattern
3. Verify `task_id` in database matches API request

### Database Migration Fails
**Symptom**: Error during `alembic upgrade head`

**Solutions**:
1. Check database connection settings
2. Verify previous migrations are applied
3. Check for conflicting indexes or columns

### MinIO Connection Issues
**Symptom**: Connection refused or timeout errors

**Solutions**:
1. Verify MinIO is running: `docker-compose ps minio`
2. Check MinIO endpoint in configuration
3. Verify bucket exists: `documents`

## References

- File Upload API: `backend/app/api/routes/files.py`
- Document Processing APIs: `backend/app/api/routes/document.py`
- Storage Service: `backend/app/services/storage_service.py`
- Database Models: `backend/app/models/file.py`
- Migration: `backend/app/alembic/versions/20260106_070400_add_task_id_to_file.py`
