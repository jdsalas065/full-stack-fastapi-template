# Hướng Dẫn Chạy Frontend và Backend Độc Lập

## Tổng Quan

Dự án đã được tách thành 2 phần hoàn toàn độc lập:
- **Backend** (`backend/`): FastAPI backend với PostgreSQL và MinIO
- **Frontend** (`frontend/`): React frontend với Vite

Mỗi phần có thể chạy độc lập mà không cần thư mục gốc.

## Backend - Chạy Độc Lập

### Bước 1: Vào thư mục backend
```bash
cd backend
```

### Bước 2: Tạo file .env
Tạo file `.env` trong thư mục `backend/` với nội dung:

```env
PROJECT_NAME=FastAPI Backend
DOMAIN=localhost
ENVIRONMENT=local

FRONTEND_HOST=http://localhost:5173
BACKEND_CORS_ORIGINS=http://localhost:5173

SECRET_KEY=changethis
ACCESS_TOKEN_EXPIRE_MINUTES=11520

POSTGRES_SERVER=db
POSTGRES_PORT=5432
POSTGRES_DB=app
POSTGRES_USER=postgres
POSTGRES_PASSWORD=changethis

FIRST_SUPERUSER=admin@localhost
FIRST_SUPERUSER_PASSWORD=changethis

MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_SECURE=false
MINIO_BUCKET=documents

OPENAI_API_KEY=
SENTRY_DSN=

DOCKER_IMAGE_BACKEND=backend
TAG=latest
```

### Bước 3: Chạy với Docker
```bash
docker compose up -d
```

### Bước 4: Kiểm tra
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- MinIO Console: http://localhost:9001
- Adminer: http://localhost:8080

## Frontend - Chạy Độc Lập

### Bước 1: Vào thư mục frontend
```bash
cd frontend
```

### Bước 2: Tạo file .env
Tạo file `.env` trong thư mục `frontend/` với nội dung:

```env
VITE_API_URL=http://localhost:8000
NODE_ENV=development
```

### Bước 3: Cài đặt dependencies
```bash
npm install
```

### Bước 4: Chạy development server
```bash
npm run dev
```

### Bước 5: Kiểm tra
Frontend sẽ chạy tại: http://localhost:5173

## Tạo OpenAPI Client (Frontend)

Khi backend API thay đổi, cần tạo lại client:

```bash
cd frontend
bash scripts/generate-client.sh
```

Hoặc nếu có file `openapi.json`:
```bash
cd frontend
npm run generate-client
```

## Chạy Cả Hai

### Terminal 1 - Backend
```bash
cd backend
docker compose up
```

### Terminal 2 - Frontend
```bash
cd frontend
npm run dev
```

## Kết Nối với Backend Khác

Nếu muốn frontend kết nối với backend khác (remote, staging, etc.):

Chỉnh sửa `frontend/.env`:
```env
VITE_API_URL=https://api.example.com
```

Sau đó restart frontend:
```bash
npm run dev
```

## Lưu Ý Quan Trọng

1. **Backend độc lập**: 
   - Tất cả config trong `backend/.env` (KHÔNG cần `.env` ở thư mục gốc)
   - Docker Compose trong `backend/docker-compose.yml`
   - Không cần thư mục gốc
   - ✅ Có thể xóa `.env` ở thư mục gốc, backend vẫn chạy bình thường

2. **Frontend độc lập**:
   - Chỉ cần `VITE_API_URL` trong `frontend/.env` (KHÔNG cần `.env` ở thư mục gốc)
   - Không cần backend code
   - Có thể kết nối với bất kỳ backend API nào
   - ✅ Có thể xóa `.env` ở thư mục gốc, frontend vẫn chạy bình thường

3. **Deploy riêng biệt**:
   - Backend có thể deploy ở server A với `backend/.env`
   - Frontend có thể deploy ở server B với `frontend/.env`
   - Chỉ cần đảm bảo frontend có thể truy cập backend API
   - ✅ Hoàn toàn không cần `.env` ở thư mục gốc

## Troubleshooting

### Backend không chạy được
- Kiểm tra `.env` đã tạo chưa
- Kiểm tra ports 8000, 5432, 9000, 9001 có bị chiếm không
- Xem logs: `docker compose logs backend`

### Frontend không kết nối được backend
- Kiểm tra `VITE_API_URL` trong `frontend/.env`
- Đảm bảo backend đang chạy
- Kiểm tra CORS trong backend config

### Generate client lỗi
- Đảm bảo backend đang chạy
- Kiểm tra `VITE_API_URL` đúng
- Hoặc đặt `openapi.json` trong `frontend/` và chạy `npm run generate-client`

## Tài Liệu

- Chi tiết backend: `backend/README.md`
- Chi tiết frontend: `frontend/README.md`
- Setup guide: `STANDALONE_SETUP.md`
