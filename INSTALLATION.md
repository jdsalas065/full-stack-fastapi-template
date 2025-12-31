# Installation Guide - File Management API

This guide covers the complete setup for running the Full Stack FastAPI project with File Management features, including MinIO object storage.

## Prerequisites

- Docker and Docker Compose installed
- Git
- A text editor

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd full-stack-fastapi-template
```

### 2. Configure Environment Variables

The `.env` file contains all necessary configuration. The default values work for local development:

```bash
# The .env file is already configured with defaults
# Review and update if needed:
cat .env
```

**Important environment variables:**

```bash
# Database
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_DB=app
POSTGRES_USER=postgres
POSTGRES_PASSWORD=changethis  # Change for production!

# Security
SECRET_KEY=changethis  # Change for production!
FIRST_SUPERUSER=admin@example.com
FIRST_SUPERUSER_PASSWORD=changethis  # Change for production!

# MinIO Object Storage
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin  # Change for production!
MINIO_SECURE=false  # Set to true in production with HTTPS
MINIO_BUCKET=documents

# OpenAI (Optional - for AI-powered file processing)
OPENAI_API_KEY=  # Add your API key if using AI features
```

### 3. Start All Services

```bash
docker compose watch
```

This single command will:
- Start PostgreSQL database
- Start MinIO object storage
- Run database migrations
- Create MinIO bucket
- Start backend API server
- Start frontend application
- Start Adminer (database admin UI)
- Start MailCatcher (email testing)

**First startup may take 2-3 minutes** while Docker downloads images and initializes services.

### 4. Access the Applications

Once all services are running (check with `docker compose logs`):

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:5173 | Main dashboard |
| **Backend API** | http://localhost:8000 | REST API |
| **API Docs** | http://localhost:8000/docs | Interactive API documentation (Swagger) |
| **Adminer** | http://localhost:8080 | Database management UI |
| **MinIO Console** | http://localhost:9001 | Object storage admin UI |
| **MailCatcher** | http://localhost:1080 | Email testing interface |

## Service Details

### PostgreSQL Database

- **Port:** 5432
- **Database:** app
- **User:** postgres
- **Password:** changethis (from .env)

**Connect via Adminer:**
1. Go to http://localhost:8080
2. System: PostgreSQL
3. Server: db
4. Username: postgres
5. Password: changethis
6. Database: app

### MinIO Object Storage

MinIO is an S3-compatible object storage service used for file uploads.

- **API Port:** 9000
- **Console Port:** 9001
- **Default Credentials:**
  - Username: minioadmin
  - Password: minioadmin

**Access MinIO Console:**
1. Go to http://localhost:9001
2. Login with minioadmin / minioadmin
3. Browse the `documents` bucket to see uploaded files

**MinIO features:**
- S3-compatible API
- File versioning
- Access policies
- Bucket management
- Web console for file browsing

### Backend API

The FastAPI backend provides:
- RESTful API endpoints
- File upload/download/management
- User authentication
- Database ORM with SQLModel
- Automatic API documentation

**File Management Endpoints:**
- `POST /api/v1/files/upload` - Upload files (Excel, PDF, Word, images)
- `GET /api/v1/files` - List all files
- `GET /api/v1/files/{file_id}` - Get file details
- `GET /api/v1/files/{file_id}/download` - Download file
- `DELETE /api/v1/files/{file_id}` - Delete file
- `POST /api/v1/files/{file_id}/process` - Process file content

**Supported file types:**
- Excel: .xlsx, .xls
- PDF: .pdf
- Word: .doc, .docx
- Images: .png, .jpg, .jpeg, .bmp, .tiff, .gif
- Max file size: 50MB

## Testing the File Upload Feature

### Using the API Documentation

1. Open http://localhost:8000/docs
2. Find the `POST /api/v1/files/upload` endpoint
3. Click "Try it out"
4. Click "Choose File" and select a file
5. Click "Execute"
6. Check the response for file metadata

### Using curl

```bash
# Upload a file
curl -X POST "http://localhost:8000/api/v1/files/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/your/file.pdf"

# List files
curl -X GET "http://localhost:8000/api/v1/files" \
  -H "accept: application/json"

# Download a file (replace FILE_ID with actual ID)
curl -X GET "http://localhost:8000/api/v1/files/FILE_ID/download" \
  --output downloaded_file.pdf
```

## Viewing Uploaded Files

### In MinIO Console
1. Go to http://localhost:9001
2. Login (minioadmin / minioadmin)
3. Click "Buckets" → "documents"
4. Browse uploaded files organized by user ID

### In Database
1. Go to http://localhost:8080 (Adminer)
2. Login to database
3. Select "file" table to see metadata

## Checking Logs

View logs for all services:
```bash
docker compose logs
```

View logs for specific service:
```bash
docker compose logs backend
docker compose logs minio
docker compose logs db
```

Follow logs in real-time:
```bash
docker compose logs -f backend
```

## Stopping Services

Stop all services:
```bash
docker compose down
```

Stop and remove all data (including database and uploaded files):
```bash
docker compose down -v
```

## Database Migrations

Migrations run automatically on startup via the prestart script.

To create a new migration manually:
```bash
# Enter backend container
docker compose exec backend bash

# Create migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head
```

## Troubleshooting

### Services not starting

Check service status:
```bash
docker compose ps
```

Check logs for errors:
```bash
docker compose logs backend
docker compose logs minio
```

### MinIO connection errors

1. Ensure MinIO is running:
   ```bash
   docker compose ps minio
   ```

2. Check MinIO logs:
   ```bash
   docker compose logs minio
   ```

3. Verify bucket exists:
   - Go to http://localhost:9001
   - Check if "documents" bucket exists
   - If not, restart services: `docker compose restart`

### Database connection errors

1. Check database is running:
   ```bash
   docker compose ps db
   ```

2. Check database logs:
   ```bash
   docker compose logs db
   ```

3. Verify credentials in `.env` match

### File upload fails

1. Check file size (max 50MB)
2. Verify file type is supported
3. Check MinIO is accessible
4. Review backend logs:
   ```bash
   docker compose logs backend
   ```

### Port already in use

If you get "port already allocated" errors:

```bash
# Find process using port (example for port 8000)
lsof -i :8000

# Kill the process or change port in docker-compose.override.yml
```

## Production Deployment

For production deployment:

1. **Update security settings in `.env`:**
   ```bash
   # Generate secure keys
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   
   # Update .env
   SECRET_KEY=<generated-key>
   POSTGRES_PASSWORD=<secure-password>
   FIRST_SUPERUSER_PASSWORD=<secure-password>
   MINIO_SECRET_KEY=<secure-password>
   ```

2. **Enable HTTPS for MinIO:**
   ```bash
   MINIO_SECURE=true
   MINIO_ENDPOINT=minio.yourdomain.com
   ```

3. **Configure domain:**
   ```bash
   DOMAIN=yourdomain.com
   FRONTEND_HOST=https://dashboard.yourdomain.com
   ```

4. **Use production compose file:**
   ```bash
   docker compose -f docker-compose.yml up -d
   ```

See [deployment.md](./deployment.md) for detailed production setup.

## Development

### Local Development Without Docker

See [development.md](./development.md) for instructions on running services locally for development.

### Running Backend Locally

1. Stop Docker backend:
   ```bash
   docker compose stop backend
   ```

2. Run locally:
   ```bash
   cd backend
   fastapi dev app/main.py
   ```

Database and MinIO will still run in Docker.

## Next Steps

- Explore API documentation at http://localhost:8000/docs
- Upload files and test the file management API
- Check MinIO console to see stored files
- Review the database schema in Adminer
- Read the [development guide](./development.md) for more details

## Support

For issues or questions:
1. Check the logs: `docker compose logs`
2. Review troubleshooting section above
3. Check existing issues on GitHub
4. Create a new issue with logs and error details
