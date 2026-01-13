# Hướng Dẫn Tách Frontend và Backend Độc Lập

Dự án đã được tách thành 2 phần độc lập: `frontend/` và `backend/`. Mỗi phần có thể chạy hoàn toàn độc lập mà không cần thư mục gốc.

## Cấu Trúc Mới

```
full-stack-fastapi-template/
├── backend/              # Backend độc lập
│   ├── .env              # Environment variables (tạo từ .env.example)
│   ├── docker-compose.yml # Docker Compose cho backend
│   ├── Dockerfile
│   └── ...
├── frontend/             # Frontend độc lập
│   ├── .env              # Environment variables (tạo từ .env.example)
│   ├── scripts/
│   │   └── generate-client.sh  # Script tạo client độc lập
│   ├── Dockerfile
│   └── ...
└── ...
```

## Backend Độc Lập

### Cấu Hình

1. **Tạo file `.env` trong `backend/`**:
   ```bash
   cd backend
   cp .env.example .env
   # Chỉnh sửa .env với các giá trị của bạn
   ```

2. **Các biến môi trường quan trọng**:
   - `POSTGRES_SERVER=db` (hoặc `localhost` nếu chạy không dùng Docker)
   - `POSTGRES_PASSWORD`, `POSTGRES_USER`, `POSTGRES_DB`
   - `SECRET_KEY`, `FIRST_SUPERUSER`, `FIRST_SUPERUSER_PASSWORD`
   - `MINIO_ENDPOINT`, `MINIO_ACCESS_KEY`, `MINIO_SECRET_KEY`

### Chạy Backend

**Với Docker Compose** (khuyến nghị):
```bash
cd backend
docker compose up -d
```

Backend sẽ chạy tại: http://localhost:8000

**Không dùng Docker**:
```bash
cd backend
uv sync
source .venv/bin/activate  # hoặc .venv\Scripts\activate trên Windows
fastapi dev app/main.py
```

### Thay Đổi Quan Trọng

- ✅ `backend/app/core/config.py` đã được sửa để đọc `.env` từ thư mục `backend/` thay vì thư mục gốc
- ✅ `backend/docker-compose.yml` đã được tạo với tất cả services cần thiết (PostgreSQL, MinIO, Backend)
- ✅ Tất cả scripts đã được kiểm tra và hoạt động độc lập

## Frontend Độc Lập

### Cấu Hình

1. **Tạo file `.env` trong `frontend/`**:
   ```bash
   cd frontend
   # Tạo file .env với nội dung:
   # VITE_API_URL=http://localhost:8000
   # NODE_ENV=development
   ```

2. **Cài đặt dependencies**:
   ```bash
   cd frontend
   npm install
   ```

### Chạy Frontend

```bash
cd frontend
npm run dev
```

Frontend sẽ chạy tại: http://localhost:5173

### Tạo OpenAPI Client

Frontend có script riêng để tạo client từ backend API:

```bash
cd frontend
bash scripts/generate-client.sh
```

Script này sẽ:
1. Tự động lấy OpenAPI schema từ backend đang chạy (theo `VITE_API_URL`)
2. Hoặc sử dụng file `openapi.json` nếu có sẵn
3. Tạo TypeScript client

### Thay Đổi Quan Trọng

- ✅ `frontend/scripts/generate-client.sh` đã được tạo để hoạt động độc lập
- ✅ Frontend chỉ cần `VITE_API_URL` để kết nối với backend
- ✅ Không cần backend code để chạy frontend

## Chạy Độc Lập

### ⚠️ QUAN TRỌNG: Không Cần .env Ở Thư Mục Gốc!

Cả 2 project đều có thể chạy độc lập mà **KHÔNG CẦN** file `.env` ở thư mục gốc. Mỗi project có `.env` riêng trong thư mục của nó.

### Chỉ Chạy Backend

```bash
cd backend
# Tạo .env TRONG thư mục backend (KHÔNG phải thư mục gốc)
cp .env.example .env
# Chỉnh sửa .env
docker compose up -d
```

Backend sẽ chạy với:
- API: http://localhost:8000
- PostgreSQL: localhost:5432
- MinIO: localhost:9000 (API), localhost:9001 (Console)
- Adminer: http://localhost:8080

**✅ Backend hoàn toàn độc lập, không cần `.env` ở thư mục gốc!**

### Chỉ Chạy Frontend

```bash
cd frontend
# Tạo .env TRONG thư mục frontend (KHÔNG phải thư mục gốc)
echo "VITE_API_URL=http://localhost:8000" > .env
npm install
npm run dev
```

Frontend sẽ chạy tại: http://localhost:5173

**✅ Frontend hoàn toàn độc lập, không cần `.env` ở thư mục gốc!**

**Lưu ý**: Frontend cần backend API đang chạy để hoạt động đầy đủ.

## Kết Nối Frontend với Backend

Frontend kết nối với backend thông qua biến môi trường `VITE_API_URL`:

- **Local development**: `VITE_API_URL=http://localhost:8000`
- **Remote API**: `VITE_API_URL=https://api.example.com`
- **Docker network**: Nếu cả 2 chạy trong Docker, có thể dùng service name

## Lợi Ích

1. **Độc lập hoàn toàn**: Mỗi project có thể chạy riêng biệt
2. **Deploy riêng**: Có thể deploy frontend và backend ở các server khác nhau
3. **Phát triển độc lập**: Team frontend và backend có thể làm việc độc lập
4. **Dễ bảo trì**: Mỗi project có cấu hình và dependencies riêng
5. **Không phụ thuộc**: Không cần thư mục gốc để chạy
6. **Không cần .env ở thư mục gốc**: Mỗi project có `.env` riêng trong thư mục của nó

## Troubleshooting

### Backend không kết nối được database

- Kiểm tra `POSTGRES_SERVER` trong `.env` (dùng `db` cho Docker, `localhost` cho local)
- Đảm bảo PostgreSQL đang chạy: `docker compose ps`

### Frontend không kết nối được backend

- Kiểm tra `VITE_API_URL` trong `frontend/.env`
- Đảm bảo backend đang chạy
- Kiểm tra CORS settings trong backend

### Generate client thất bại

- Đảm bảo backend đang chạy và có thể truy cập
- Kiểm tra `VITE_API_URL` đúng
- Hoặc đặt file `openapi.json` trong `frontend/` và chạy `npm run generate-client`

## Tài Liệu Thêm

- Xem `backend/README.md` để biết chi tiết về backend
- Xem `frontend/README.md` để biết chi tiết về frontend
