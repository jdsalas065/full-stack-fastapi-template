---
name: verify-changes
description: Run all quality checks for this full-stack project (ruff, mypy, pytest on backend; biome lint and build on frontend) and fix every error found. Use before finishing any task, committing, or opening a PR.
---

<!--
HƯỚNG DẪN DÙNG (How to use)
- Dùng SAU khi đã sửa code, TRƯỚC khi báo xong / commit / mở PR.
- Kích hoạt: "Dùng skill verify-changes" hoặc "Chạy verify rồi sửa hết lỗi".
- Agent sẽ chạy ruff + mypy + pytest (backend) và biome + build (frontend), rồi sửa đến khi tất cả exit code 0.
- Phần test (npm run test / test:e2e) chỉ chạy nếu đã setup test (xem skill frontend-testing); test:e2e cần backend đang chạy.
- Sao chép skill sang tool khác: copy thư mục này vào .github/skills/ hoặc .claude/skills/. Trong Copilot tương đương prompt file /verify-changes.
-->

# Verify Changes

Run every check below and fix all errors before declaring done.

## Backend (`backend/`)

```bash
uv run ruff format .          # auto-format
uv run ruff check . --fix     # lint + auto-fix
uv run mypy app               # type check, must be zero errors
uv run pytest                 # all tests must pass
```

## Frontend (`frontend/`)

```bash
npm run lint                  # biome lint + format (auto-fix)
npm run build                 # tsc + vite build, must succeed
```

If frontend tests are set up, also run:

```bash
npm run test                  # vitest
npm run test:e2e              # playwright (needs backend running)
```

## Fix strategy

- **Ruff**: most issues auto-fix with `--fix`; fix the rest per the rule.
- **mypy**: add missing annotations; replace `Any` with proper types; use `cast()` only when unavoidable.
- **pytest**: read the full traceback and fix the root cause; do not skip or mock the failure away.
- **build**: resolve all TypeScript errors; avoid `// @ts-ignore` unless truly unavoidable.

## Done when

All commands exit code 0.
