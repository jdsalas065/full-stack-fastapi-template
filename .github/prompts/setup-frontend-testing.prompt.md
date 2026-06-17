---
description: Set up the frontend testing infrastructure (Vitest + React Testing Library + Playwright config + auth fixture + missing data-testid). Use before writing any frontend tests.
---

# Setup Frontend Testing Infrastructure

Chỉ lo phần HẠ TẦNG test (chưa viết test case — việc đó dùng `/write-all-frontend-tests`). Làm tuần tự trong `frontend/`, verify sau mỗi bước.

## Checklist

- [ ] **1. Cài deps**
  ```bash
  npm install -D vitest @testing-library/react @testing-library/jest-dom @testing-library/user-event jsdom
  npx playwright install --with-deps chromium
  ```

- [ ] **2. Scripts** — Thêm vào `frontend/package.json` mục `"scripts"`:
  ```json
  "test": "vitest run",
  "test:watch": "vitest",
  "test:e2e": "playwright test",
  "test:e2e:ui": "playwright test --ui"
  ```

- [ ] **3. `frontend/vitest.config.ts`**
  ```ts
  import react from "@vitejs/plugin-react-swc"
  import path from "node:path"
  import { defineConfig } from "vitest/config"

  export default defineConfig({
    plugins: [react()],
    test: {
      environment: "jsdom",
      globals: true,
      setupFiles: ["./vitest.setup.ts"],
      include: ["src/**/*.{test,spec}.{ts,tsx}"],
    },
    resolve: { alias: { "@": path.resolve(__dirname, "./src") } },
  })
  ```

- [ ] **4. `frontend/vitest.setup.ts`**
  ```ts
  import "@testing-library/jest-dom/vitest"
  import { cleanup } from "@testing-library/react"
  import { afterEach } from "vitest"

  afterEach(() => cleanup())
  ```

- [ ] **5. `frontend/playwright.config.ts`** — copy từ `frontend/TESTING_RUNBOOK.md` Phase 4 (có `testIdAttribute: "data-testid"`, `webServer`, `storageState`).

- [ ] **6. Auth fixture** — Tạo `frontend/tests/e2e/auth.setup.ts` (copy từ runbook Phase 5) và thêm `tests/e2e/.auth/` vào `frontend/.gitignore`.

- [ ] **7. Thêm `data-testid` còn thiếu** vào `src/components/Chat/ChatInterface.tsx`: `chat-input`, `chat-send`, `user-message`, `assistant-message`. (Login đã có sẵn.)

- [ ] **8. Verify hạ tầng**
  ```bash
  npx vitest --version
  npx playwright --version
  cd frontend && npm run lint
  ```

Xong hạ tầng → chạy `/write-all-frontend-tests` để viết test case.

Chi tiết đầy đủ: `frontend/TESTING_RUNBOOK.md`.
