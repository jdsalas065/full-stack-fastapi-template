# Development Setup Guide

This comprehensive guide covers setting up the Full Stack FastAPI project for development, including both Docker-based and manual installation methods.

## Table of Contents

1. [Docker-Based Development (Recommended)](#docker-based-development-recommended)
2. [Manual Installation for Development](#manual-installation-for-development)
3. [Individual Service Setup](#individual-service-setup)
4. [Development Tools](#development-tools)
5. [Troubleshooting](#troubleshooting)

---

## Docker-Based Development (Recommended)

### Prerequisites

Install the following software:

#### 1. Docker Desktop

**Windows:**
```bash
# Download from: https://www.docker.com/products/docker-desktop
# Or use winget:
winget install Docker.DockerDesktop
```

**macOS:**
```bash
# Download from: https://www.docker.com/products/docker-desktop
# Or use Homebrew:
brew install --cask docker
```

**Linux (Ubuntu/Debian):**
```bash
# Install Docker Engine
sudo apt-get update
sudo apt-get install ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Add your user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

#### 2. Git

**Windows:**
```bash
winget install Git.Git
```

**macOS:**
```bash
brew install git
```

**Linux:**
```bash
sudo apt-get install git
```

### Quick Start with Docker

1. **Clone the repository:**
```bash
git clone https://github.com/jdsalas065/full-stack-fastapi-template.git
cd full-stack-fastapi-template
```

2. **Review and configure environment variables:**
```bash
# The .env file is already configured with defaults
cat .env

# Optional: Edit .env for your needs
nano .env  # or vim .env, or use your preferred editor
```

3. **Start all services:**
```bash
docker compose watch
```

This command will:
- Download and build all Docker images (first time only)
- Start PostgreSQL database
- Start MinIO object storage
- Run database migrations
- Initialize MinIO bucket
- Start backend API (with hot reload)
- Start frontend (with hot reload)
- Start Adminer for database management

4. **Verify services are running:**
```bash
docker compose ps
```

Expected output:
```
NAME                          STATUS          PORTS
full-stack-fastapi-template-adminer-1    running    0.0.0.0:8080->8080/tcp
full-stack-fastapi-template-backend-1    running    0.0.0.0:8000->8000/tcp
full-stack-fastapi-template-db-1         running    0.0.0.0:5432->5432/tcp
full-stack-fastapi-template-frontend-1   running    0.0.0.0:5173->80/tcp
full-stack-fastapi-template-minio-1      running    0.0.0.0:9000-9001->9000-9001/tcp
```

5. **Access the applications:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Adminer (DB): http://localhost:8080
- MinIO Console: http://localhost:9001 (minioadmin/minioadmin)

### Development Workflow with Docker

#### View Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f db
docker compose logs -f minio
```

#### Restart Services
```bash
# Restart all
docker compose restart

# Restart specific service
docker compose restart backend
docker compose restart frontend
```

#### Stop Services
```bash
# Stop all services (keeps data)
docker compose stop

# Stop and remove containers (keeps data)
docker compose down

# Stop and remove everything including volumes (deletes data)
docker compose down -v
```

#### Execute Commands in Containers
```bash
# Backend shell
docker compose exec backend bash

# Run migrations manually
docker compose exec backend alembic upgrade head

# Create a new migration
docker compose exec backend alembic revision --autogenerate -m "description"

# Run tests
docker compose exec backend pytest

# Frontend shell
docker compose exec frontend sh
```

#### Rebuild After Dependency Changes
```bash
# Rebuild backend after requirements.txt changes
docker compose build backend
docker compose up -d backend

# Rebuild frontend after package.json changes
docker compose build frontend
docker compose up -d frontend
```

---

## Manual Installation for Development

For development without Docker, install each component individually.

### Prerequisites

#### 1. Python 3.10+

**Windows:**
```bash
winget install Python.Python.3.12
```

**macOS:**
```bash
brew install python@3.12
```

**Linux:**
```bash
sudo apt-get update
sudo apt-get install python3.12 python3.12-venv python3.12-dev
```

#### 2. Node.js 20+

**Windows:**
```bash
winget install OpenJS.NodeJS.LTS
```

**macOS:**
```bash
brew install node@20
```

**Linux:**
```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
```

#### 3. PostgreSQL 17

**Windows:**
```bash
winget install PostgreSQL.PostgreSQL
```

**macOS:**
```bash
brew install postgresql@17
brew services start postgresql@17
```

**Linux:**
```bash
sudo apt-get install postgresql-17 postgresql-contrib-17
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### 4. MinIO

**Windows:**
```powershell
# Download from https://min.io/download
# Or use chocolatey:
choco install minio
```

**macOS:**
```bash
brew install minio/stable/minio
```

**Linux:**
```bash
wget https://dl.min.io/server/minio/release/linux-amd64/minio
chmod +x minio
sudo mv minio /usr/local/bin/
```

### Backend Setup

1. **Navigate to backend directory:**
```bash
cd backend
```

2. **Create virtual environment:**
```bash
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

4. **Configure environment:**
```bash
# Copy example env file
cp ../.env.example ../.env

# Edit .env with your local settings
# Update these for local development:
# POSTGRES_SERVER=localhost
# MINIO_ENDPOINT=localhost:9000
```

5. **Run database migrations:**
```bash
alembic upgrade head
```

6. **Start backend server:**
```bash
# Development mode with auto-reload
fastapi dev app/main.py

# Or using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at http://localhost:8000

### Frontend Setup

1. **Navigate to frontend directory:**
```bash
cd frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Start development server:**
```bash
npm run dev
```

Frontend will be available at http://localhost:5173

### Database Setup (PostgreSQL)

1. **Create database user and database:**
```bash
# Connect to PostgreSQL
sudo -u postgres psql

# In PostgreSQL shell:
CREATE USER postgres WITH PASSWORD 'changethis';
CREATE DATABASE app OWNER postgres;
GRANT ALL PRIVILEGES ON DATABASE app TO postgres;
\q
```

2. **Verify connection:**
```bash
psql -h localhost -U postgres -d app
# Enter password: changethis
```

### MinIO Setup

1. **Start MinIO server:**
```bash
# Create data directory
mkdir -p ~/minio/data

# Start MinIO
minio server ~/minio/data --console-address ":9001"
```

MinIO will be available at:
- API: http://localhost:9000
- Console: http://localhost:9001

2. **Create bucket:**
```bash
# Install MinIO client
brew install minio/stable/mc  # macOS
# or download from https://min.io/docs/minio/linux/reference/minio-mc.html

# Configure client
mc alias set local http://localhost:9000 minioadmin minioadmin

# Create bucket
mc mb local/documents
```

---

## Individual Service Setup

### PostgreSQL (Development Database)

#### Installation

**Via Docker (Easiest):**
```bash
docker run -d \
  --name postgres-dev \
  -e POSTGRES_PASSWORD=changethis \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_DB=app \
  -p 5432:5432 \
  -v postgres-data:/var/lib/postgresql/data \
  postgres:17
```

#### Configuration

Create `~/.pgpass` for passwordless access:
```bash
echo "localhost:5432:app:postgres:changethis" > ~/.pgpass
chmod 600 ~/.pgpass
```

#### Management Tools

**pgAdmin (GUI):**
```bash
# Windows
winget install PostgreSQL.pgAdmin

# macOS
brew install --cask pgadmin4

# Linux
sudo apt-get install pgadmin4
```

**psql (CLI):**
```bash
# Connect to database
psql -h localhost -U postgres -d app

# Common commands:
\l              # List databases
\dt             # List tables
\d table_name   # Describe table
\q              # Quit
```

### MinIO (Object Storage)

#### Development Setup

**Via Docker (Easiest):**
```bash
docker run -d \
  --name minio-dev \
  -e MINIO_ROOT_USER=minioadmin \
  -e MINIO_ROOT_PASSWORD=minioadmin \
  -p 9000:9000 \
  -p 9001:9001 \
  -v minio-data:/data \
  minio/minio server /data --console-address ":9001"
```

#### MinIO Client (mc)

```bash
# Install
brew install minio/stable/mc  # macOS
sudo apt-get install minio-client  # Linux

# Configure
mc alias set local http://localhost:9000 minioadmin minioadmin

# Commands
mc ls local/                  # List buckets
mc mb local/documents         # Create bucket
mc rb local/documents         # Remove bucket
mc cp file.pdf local/documents/  # Upload file
mc cat local/documents/file.pdf  # View file
```

### Adminer (Database UI)

**Via Docker:**
```bash
docker run -d \
  --name adminer-dev \
  -p 8080:8080 \
  --link postgres-dev:db \
  adminer
```

Access at http://localhost:8080
- System: PostgreSQL
- Server: db (or localhost if not using Docker link)
- Username: postgres
- Password: changethis
- Database: app

---

## Development Tools

### Backend Development

#### 1. UV (Modern Python Package Manager)

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Use uv for faster package management
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
uv run pytest
```

#### 2. Code Quality Tools

```bash
# Install development tools
pip install ruff mypy pytest pytest-cov

# Linting
ruff check .
ruff format .

# Type checking
mypy app/

# Testing
pytest
pytest --cov=app tests/
```

#### 3. Database Tools

```bash
# Install Alembic for migrations
pip install alembic

# Create migration
alembic revision --autogenerate -m "Add new table"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Frontend Development

#### 1. Package Management

```bash
# Install dependencies
npm install

# Add new package
npm install package-name

# Remove package
npm uninstall package-name

# Update packages
npm update
```

#### 2. Development Scripts

```bash
# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint

# Type check
npm run type-check
```

#### 3. Generate OpenAPI Client

```bash
# Generate TypeScript client from backend OpenAPI spec
npm run generate-client
```

### IDE Setup

#### VS Code (Recommended)

Install extensions:
- Python (Microsoft)
- Pylance
- ESLint
- Prettier
- Docker
- PostgreSQL

**Backend settings (.vscode/settings.json):**
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/backend/.venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.formatting.provider": "black",
  "[python]": {
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.organizeImports": true
    }
  }
}
```

#### PyCharm

1. Set Python interpreter to `.venv/bin/python`
2. Mark `backend/app` as Sources Root
3. Enable Docker integration
4. Configure database connection

---

## Troubleshooting

### Docker Issues

**Port already in use:**
```bash
# Find process using port
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill process or change port in docker-compose.override.yml
```

**Docker out of space:**
```bash
# Clean up unused containers, images, volumes
docker system prune -a
docker volume prune
```

**Containers won't start:**
```bash
# Check logs
docker compose logs backend

# Restart Docker Desktop
# Rebuild images
docker compose build --no-cache
docker compose up -d
```

### Backend Issues

**Import errors:**
```bash
# Ensure PYTHONPATH is set
export PYTHONPATH="${PYTHONPATH}:${PWD}/backend"

# Or use absolute imports from 'app'
```

**Database connection errors:**
```bash
# Check PostgreSQL is running
pg_isready -h localhost -p 5432

# Check credentials in .env
# Verify database exists
psql -h localhost -U postgres -l
```

**Migration errors:**
```bash
# Reset migrations (development only!)
alembic downgrade base
rm -rf alembic/versions/*.py
alembic revision --autogenerate -m "initial"
alembic upgrade head
```

### Frontend Issues

**Node modules errors:**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

**Port 5173 in use:**
```bash
# Kill process
lsof -i :5173 | grep LISTEN | awk '{print $2}' | xargs kill -9

# Or change port in vite.config.ts
```

**Build errors:**
```bash
# Clear Vite cache
rm -rf .vite
npm run build
```

### MinIO Issues

**Bucket not created:**
```bash
# Create manually
mc alias set local http://localhost:9000 minioadmin minioadmin
mc mb local/documents

# Or restart backend to trigger auto-creation
```

**Connection refused:**
```bash
# Check MinIO is running
curl http://localhost:9000/minio/health/live

# Check firewall settings
# Verify MINIO_ENDPOINT in .env
```

### PostgreSQL Issues

**Cannot connect:**
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql  # Linux
brew services list  # macOS

# Check pg_hba.conf allows local connections
sudo nano /etc/postgresql/17/main/pg_hba.conf
# Add: host all all 127.0.0.1/32 md5
```

**Database doesn't exist:**
```bash
# Create database
createdb -h localhost -U postgres app

# Or using psql
psql -h localhost -U postgres
CREATE DATABASE app;
```

---

## Next Steps

1. **Explore the API:**
   - Visit http://localhost:8000/docs for interactive API documentation
   - Try uploading a file via the `/api/v1/files/upload` endpoint

2. **Test File Management:**
   - Upload files through the API
   - Check MinIO console to see stored files
   - Query database to see file metadata

3. **Customize the Application:**
   - Modify models in `backend/app/models/`
   - Create new API endpoints in `backend/app/api/routes/`
   - Update frontend components in `frontend/src/`

4. **Learn the Stack:**
   - [FastAPI Documentation](https://fastapi.tiangolo.com/)
   - [React Documentation](https://react.dev/)
   - [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
   - [MinIO Documentation](https://min.io/docs/minio/linux/index.html)

---

## Additional Resources

- [Project README](./README.md)
- [Quick Installation Guide](./INSTALLATION.md)
- [Deployment Guide](./deployment.md)
- [Development Guide](./development.md)
- [Backend README](./backend/README.md)
- [Frontend README](./frontend/README.md)
