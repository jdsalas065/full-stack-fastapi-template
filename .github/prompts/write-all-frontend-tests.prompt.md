---
description: Set up frontend testing (Vitest + Playwright) and write all test cases following the runbook, then run until green. Use when asked to add or write frontend tests.
---

# Write All Frontend Tests

Thực hiện theo `frontend/TESTING_RUNBOOK.md`. Làm **tuần tự từng Phase**, KHÔNG bỏ bước. Sau mỗi Phase chạy lệnh verify, sửa sạch lỗi rồi mới sang Phase kế tiếp.

## Nguyên tắc bắt buộc

1. 1 test case = 1 `test()` / `it()`. Tên test bắt đầu bằng ID (vd `LOGIN-02: ...`).
2. Cấu trúc AAA: Arrange → Act → Assert. Mỗi test độc lập.
3. Selector CHỈ dùng `getByTestId` hoặc `getByRole`. Cấm CSS class / xpath.
4. UI thiếu `data-testid` → thêm vào component trước, rồi mới viết test.
5. Không thêm thư viện ngoài danh sách trong runbook Phase 0.
6. Test chỉ "xong" khi chạy được và xanh.

## Checklist thực thi

- [ ] **Phase 0** — Cài deps: `npm install -D vitest @testing-library/react @testing-library/jest-dom @testing-library/user-event jsdom` và `npx playwright install --with-deps chromium`.
- [ ] **Phase 1** — Thêm scripts `test`, `test:watch`, `test:e2e`, `test:e2e:ui` vào `frontend/package.json`.
- [ ] **Phase 2** — Tạo `frontend/vitest.config.ts` (jsdom + alias `@`).
- [ ] **Phase 3** — Tạo `frontend/vitest.setup.ts` (jest-dom + cleanup).
- [ ] **Phase 4** — Tạo `frontend/playwright.config.ts` (testIdAttribute, webServer, storageState).
- [ ] **Phase 5** — Tạo `frontend/tests/e2e/auth.setup.ts` + thêm `tests/e2e/.auth/` vào `.gitignore`.
- [ ] **Phase 6** — Thêm `data-testid` còn thiếu vào `src/components/Chat/ChatInterface.tsx`: `chat-input`, `chat-send`, `user-message`, `assistant-message`.
- [ ] **Phase 7** — Viết HẾT test case theo catalog trong runbook:
  - Component/Unit (Vitest, không cần backend) — LÀM TRƯỚC: `C-LOGIN-01`, `C-LOGIN-02`, `C-CHAT-01`, `C-CHAT-02`.
  - E2E (Playwright, cần backend): Auth, Chat, Table1 CRUD, Settings.
- [ ] **Phase 8/9** — Verify đến khi xanh:
  ```bash
  cd frontend
  npm run test
  npm run lint
  npm run test:e2e
  ```

## Done khi

- Mọi case trong catalog có test khớp ID.
- `npm run test`, `npm run lint`, `npm run test:e2e` đều exit code 0.
- Chỉ dùng `getByTestId` / `getByRole`.

Chi tiết đầy đủ (nội dung từng file config, bảng catalog, template, cách mock `streamChat`) xem trong `frontend/TESTING_RUNBOOK.md`.
