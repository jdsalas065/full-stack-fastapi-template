# Local Development Setup Guide

Hướng dẫn chạy full stack (Backend + Frontend + Database) lên local để test Chat API Streaming.

## Prerequisites

- Docker & Docker Compose
- Node.js 18+
- Python 3.10+
- Terminal / PowerShell

## Step 1: Start Database & Dependencies (Docker)

Mở terminal và chạy:

```bash
cd d:\full-stack-fastapi-template
docker-compose up -d
```

Chờ cho containers khởi động (khoảng 10-15 giây):
- PostgreSQL: localhost:5432
- MinIO: localhost:9000
- (Optional) Traefik: localhost:80

Verify:
```bash
docker-compose ps
```

**Output mong đợi:** Tất cả services có status "Up"

---

## Step 2: Backend Setup & Migration

### 2a. Setup virtual environment (nếu chưa làm)

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -e .
```

### 2b. Run Database Migration

```bash
cd backend
.\.venv\Scripts\python.exe -m alembic upgrade head
```

**Output mong đợi:**
```
INFO  [alembic.migration] Running upgrade 20260115_060010 -> 20260322_120000, 
add chat conversation and message tables

INFO  [alembic.env] Upgrade from 20260115_060010 -> 20260322_120000 complete
```

### 2c. Run Backend Server

Mở terminal mới ở thư mục `backend`:

```bash
cd backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Output mong đợi:**
```
INFO:     Application startup complete
Uvicorn running on http://0.0.0.0:8000
```

API Docs có sẵn tại: http://localhost:8000/api/v1/docs

---

## Step 3: Frontend Setup & Run

Mở terminal mới ở thư mục `frontend`:

```bash
cd frontend
npm install
npm run dev
```

**Output mong đợi:**
```
VITE v... dev server running at:

  ➜  Local:   http://localhost:5173/
```

---

## Step 4: Test Chat API Streaming

### Via Web UI

1. Mở trình duyệt: http://localhost:5173/
2. Login bằng:
   - Email: `admin@example.com`
   - Password: `changethis`
3. Permalink vào route `/chat` hoặc click "Chat" trong menu
4. Gõ message và bấm "Send"
5. Xem token được stream theo thời gian thực dạng SSE

### Via cURL (test API raw)

Trước hết lấy access token:

```bash
curl -X POST http://localhost:8000/api/v1/login/access-token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=changethis"
```

Copy `access_token` từ response, rồi:

```bash
curl -N -X POST http://localhost:8000/api/v1/chat \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, how are you?"}' 
```

**Mong đợi:** SSE events liên tục dạng:
```
event: start
data: {...}

event: token
data: {"delta": "I ", ...}

event: token
data: {"delta": "am ", ...}

...

event: done
data: {"content": "I am...", ...}
```

---

## Step 5: Test Endpoints (Optional)

### Health Check

```bash
curl http://localhost:8000/api/v1/utils/health
```

### API Docs (Swagger UI)

http://localhost:8000/api/v1/docs

Tại đây bạn có thể:
- Xem tất cả endpoints
- Thử gọi endpoint (sau khi authorize)
- Xem schema/response

---

## Troubleshooting

### Database Connection Error

**Vấn đề:** `connection failed: connection to server at "127.0.0.1", port 5432 failed`

**Giải pháp:**
```bash
docker-compose ps  # Check nếu postgres running
docker-compose logs postgres  # Xem logs
docker-compose down && docker-compose up -d  # Restart
```

### OPENAI_API_KEY Not Configured

Chỉnh sửa `backend/.env` thêm:

```
OPENAI_API_KEY=your-openai-api-key-here
```

Nếu không có OpenAI key, endpoint sẽ trả về lỗi 503 nhưng structure vẫn là đúng để test SSE parsing.

### Port Already in Use

Nếu port bận sẵn:

```bash
# Backend (change port)
uvicorn app.main:app --reload --port 8001

# Frontend (change port in vite.config.ts hoặc)
npm run dev -- --port 5174
```

### Frontend Can't Reach Backend API

Chắc `VITE_API_URL` env var sau nếu API server chạy port khác 8000:

```bash
# Trước khi chạy npm run dev
set VITE_API_URL=http://localhost:8001
npm run dev
```

---

## To Stop Everything

```bash
# Terminal Backend
Ctrl+C

# Terminal Frontend  
Ctrl+C

# Docker services
docker-compose down
```

---

## Checklist for Full-Stack Test

- [ ] Docker containers running (postgresql, minio, traefik)
- [ ] Migration applied (chat_conversation & chat_message tables created)
- [ ] Backend server running on http://localhost:8000
- [ ] Frontend dev server running on http://localhost:5173
- [ ] Logged in with admin@example.com / changethis
- [ ] Chat page loads
- [ ] Send a message and see SSE stream events
- [ ] Message persisted in DB (conversation/message records saved)

---

Good luck! 🚀
