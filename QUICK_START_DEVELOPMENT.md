# 🚀 Quick Start - Backend Development Guide

**Hướng dẫn chạy FastAPI local + Docker cho các service khác**

---

## ✅ Cách Nhanh Nhất (Recommended)

### 1️⃣ Bước 1: Chuẩn Bị (5 phút)

```powershell
# Cài đặt uv (Windows PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Hoặc cài đặt bằng pip (backup)
pip install uv
```

### 2️⃣ Bước 2: Khởi Động Docker Services (2 phút)

```powershell
# Từ thư mục gốc dự án
cd d:\full-stack-fastapi-template

# Chỉ khởi động Database + MinIO
docker compose up -d db minio

# Kiểm tra xem có chạy không
docker compose ps
```

**Kết quả mong đợi:**
```
NAME        STATUS      PORTS
db          Up          0.0.0.0:5432->5432/tcp
minio       Up          0.0.0.0:9000->9000/tcp
```

### 3️⃣ Bước 3: Cài Đặt Backend (3 phút)

```powershell
cd backend

# Cài đặt dependencies
uv sync

# Hoặc nếu không có uv
pip install -r requirements.txt
```

### 4️⃣ Bước 4: Setup Environment

```powershell
# Copy template
cp .env.example .env

# Edit .env với các giá trị này:
# POSTGRES_SERVER=localhost (KHÔNG phải 'db')
# POSTGRES_USER=postgres
# POSTGRES_PASSWORD=changethis
# POSTGRES_DB=app
# MINIO_ENDPOINT=localhost:9000
```

### 5️⃣ Bước 5: Database Migration (1 phút)

```powershell
uv run alembic upgrade head
```

### 6️⃣ Bước 6: Chạy FastAPI ✨

```powershell
uv run fastapi dev app/main.py
```

**✅ Xong! FastAPI chạy tại:** http://localhost:8000

---

## 🌐 Truy Cập Services

| Service | URL | Mô Tả |
|---------|-----|-------|
| **FastAPI API** | http://localhost:8000 | Backend chính |
| **Swagger Docs** | http://localhost:8000/docs | API documentation |
| **ReDoc** | http://localhost:8000/redoc | Alternative docs |
| **PostgreSQL** | localhost:5432 | Database |
| **MinIO** | http://localhost:9001 | File storage (user: minioadmin) |

---

## 📝 Commands Hữu Ích

### Xem Logs Services

```powershell
# Logs PostgreSQL
docker compose logs -f db

# Logs MinIO
docker compose logs -f minio

# Logs FastAPI (nếu chạy trong Docker)
docker compose logs -f backend
```

### Dừng Services

```powershell
# Dừng tất cả
docker compose down

# Dừng và xóa volumes (cẩn thận - mất dữ liệu)
docker compose down -v
```

### Chạy Tests

```powershell
# Từ thư mục backend
pytest

# Hoặc với coverage
pytest --cov=app
```

### Database Commands

```powershell
# Tạo migration mới (sau khi thay đổi models)
uv run alembic revision --autogenerate -m "Tên migration"

# Xem migration history
uv run alembic history

# Rollback 1 migration
uv run alembic downgrade -1
```

---

## 🎯 Development Workflow

### Mỗi Ngày Làm Việc:

```powershell
# Terminal 1: Khởi động services nếu chưa chạy
docker compose up -d db minio

# Terminal 2: Chạy FastAPI
cd backend
uv run fastapi dev app/main.py

# 👉 Code, refactor, test
# 👉 Changes auto-reload trong FastAPI dev mode
```

### Thêm Model Mới:

```powershell
# 1. Tạo model trong app/models/your_model.py
# 2. Tạo schema trong app/schemas/your_model.py
# 3. Tạo CRUD trong app/crud/your_model.py
# 4. Tạo routes trong app/api/routes/your_model.py

# 5. Database migration
uv run alembic revision --autogenerate -m "Add YourModel table"
uv run alembic upgrade head

# 6. Test API tại http://localhost:8000/docs
```

---

## ❌ Troubleshooting

### ❓ FastAPI không start

```powershell
# Kiểm tra Python version (phải >= 3.10)
python --version

# Cài lại dependencies
uv sync --force

# Kiểm tra database kết nối
python -c "from app.core.database import engine; print('DB OK')"
```

### ❓ Port 8000 đang dùng

```powershell
# Chạy trên port khác
uv run fastapi dev app/main.py --port 8001
```

### ❓ MinIO không kết nối

```powershell
# Kiểm tra MinIO chạy chưa
docker compose ps minio

# Restart MinIO
docker compose restart minio

# Check trong .env:
# MINIO_ENDPOINT=localhost:9000 (NOT minio:9000)
```

### ❓ Database connection refused

```powershell
# Kiểm tra PostgreSQL chạy chưa
docker compose ps db

# Restart PostgreSQL
docker compose restart db

# Check trong .env:
# POSTGRES_SERVER=localhost (NOT db)
```

---

## 🔄 Chạy Frontend Cùng (Optional)

Nếu muốn develop frontend cùng lúc:

```powershell
# Terminal 1: Docker services
docker compose up -d db minio

# Terminal 2: FastAPI backend
cd backend
uv run fastapi dev app/main.py

# Terminal 3: Frontend
cd frontend
npm install
npm run dev
```

Frontend: http://localhost:5173
Backend: http://localhost:8000

---

## 📚 Tài Liệu Đầy Đủ

Chi tiết hơn xem tại: [backend/README.md](backend/README.md)

---

## ✨ Tips & Tricks

1. **Hot Reload:** `fastapi dev` tự động reload khi thay đổi code ✅
2. **Type Checking:** Sử dụng Pydantic schemas để auto-validate input
3. **Database:** Luôn dùng Alembic migrations trong production
4. **Testing:** Viết tests khi thêm feature mới
5. **Security:** Không commit `.env` hoặc secrets vào Git

---

**Happy coding! 🎉**
