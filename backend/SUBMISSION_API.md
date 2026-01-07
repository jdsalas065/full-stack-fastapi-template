# Submission Management API

This document describes the new submission management and file upload endpoints added to the FastAPI backend.

## Overview

The submission management system allows users to:
- Create and manage submissions
- Upload files to submissions
- Download files with presigned URLs
- Delete files and submissions

## Database Models

### Submission
- `id`: UUID (primary key)
- `title`: String (max 255 characters)
- `description`: String (optional, max 1000 characters)
- `owner_id`: UUID (foreign key to User)
- Relationships: `owner` (User), `documents` (list of SubmissionDocument)

### SubmissionDocument
- `id`: UUID (primary key)
- `filename`: String (max 255 characters)
- `file_path`: String (max 500 characters) - path in MinIO
- `file_size`: Integer - size in bytes
- `content_type`: String (max 100 characters)
- `submission_id`: UUID (foreign key to Submission)
- Relationship: `submission` (Submission)

## API Endpoints

### Submissions

#### GET /api/v1/submissions/
List submissions for the current user (or all submissions for superusers).

**Query Parameters:**
- `skip`: int (default: 0) - Number of records to skip
- `limit`: int (default: 100) - Maximum number of records to return

**Response:** `SubmissionsPublic` - List of submissions with count

#### GET /api/v1/submissions/{id}
Get a specific submission by ID.

**Path Parameters:**
- `id`: UUID - Submission ID

**Response:** `SubmissionPublic`

#### POST /api/v1/submissions/
Create a new submission.

**Request Body:** `SubmissionCreate`
```json
{
  "title": "My Submission",
  "description": "Optional description"
}
```

**Response:** `SubmissionPublic`

#### PUT /api/v1/submissions/{id}
Update an existing submission.

**Path Parameters:**
- `id`: UUID - Submission ID

**Request Body:** `SubmissionUpdate`
```json
{
  "title": "Updated Title",
  "description": "Updated description"
}
```

**Response:** `SubmissionPublic`

#### DELETE /api/v1/submissions/{id}
Delete a submission and all associated files.

**Path Parameters:**
- `id`: UUID - Submission ID

**Response:** `Message` - Success message

### Files

#### POST /api/v1/files/upload
Upload a file to a submission.

**Form Data:**
- `file`: UploadFile - The file to upload
- `submission_id`: string - UUID of the submission

**Response:** `SubmissionDocumentPublic`

**Features:**
- Pre-generated UUID for atomic operations
- Automatic rollback on error (both database and MinIO)
- Files stored in MinIO under folder: `{submission_id}/{uuid}_{filename}`

#### GET /api/v1/files/download/{document_id}
Get a presigned URL for downloading a file.

**Path Parameters:**
- `document_id`: UUID - Document ID

**Response:**
```json
{
  "download_url": "https://minio.example.com/..."
}
```

**Note:** The presigned URL is valid for 1 hour by default.

#### DELETE /api/v1/files/{document_id}
Delete a file.

**Path Parameters:**
- `document_id`: UUID - Document ID

**Response:** `Message` - Success message

## Permissions

- **Regular Users:** Can only access their own submissions and files
- **Superusers:** Can access all submissions and files

## MinIO Configuration

The following environment variables are required for MinIO integration:

- `MINIO_URL`: MinIO server URL (default: `localhost:9000`)
- `MINIO_ACCESS_KEY`: MinIO access key (default: `minioadmin`)
- `MINIO_SECRET_KEY`: MinIO secret key (default: `minioadmin`)
- `MINIO_BUCKET`: Bucket name for storing files (default: `submissions`)
- `MINIO_SECURE`: Use HTTPS (default: `False`)

## Database Migration

The database migration creates two new tables:
- `submission` - Stores submission metadata
- `submissiondocument` - Stores file metadata and references

To apply the migration:
```bash
cd backend
alembic upgrade head
```

## Error Handling

The API includes proper error handling with rollback mechanisms:
- If file upload to MinIO fails, no database record is created
- If database record creation fails, the uploaded file is deleted from MinIO
- All operations are atomic to maintain data consistency

## Example Usage

### Create a submission and upload a file

```python
import requests

# Login to get access token
login_response = requests.post(
    "http://localhost:8000/api/v1/login/access-token",
    data={"username": "user@example.com", "password": "password"}
)
token = login_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Create a submission
submission = requests.post(
    "http://localhost:8000/api/v1/submissions/",
    json={"title": "My First Submission", "description": "Test submission"},
    headers=headers
).json()

submission_id = submission["id"]

# Upload a file
with open("document.pdf", "rb") as f:
    files = {"file": f}
    data = {"submission_id": submission_id}
    document = requests.post(
        "http://localhost:8000/api/v1/files/upload",
        files=files,
        data=data,
        headers=headers
    ).json()

print(f"File uploaded: {document['filename']}")

# Get download URL
download = requests.get(
    f"http://localhost:8000/api/v1/files/download/{document['id']}",
    headers=headers
).json()

print(f"Download URL: {download['download_url']}")
```
