---
name: frontend-testing
description: Set up frontend testing infrastructure (Vitest + React Testing Library + Playwright) and write all test cases for this React project, then run until green. Use when asked to add, write, or set up frontend tests, unit tests, component tests, or E2E tests.
---

<!--
HƯỚNG DẪN DÙNG (How to use)
- Kích hoạt: "Dùng skill frontend-testing để viết test cho frontend" hoặc "Setup test + viết hết test case".
- Agent làm theo Phase 0→9; nội dung chi tiết (config từng file, bảng catalog, template) nằm ở references/runbook.md — agent đọc khi cần.
- Mẹo cho model yếu: yêu cầu "làm Vitest (component) trước cho xanh, E2E làm sau" — Vitest không cần backend.
- Yêu cầu trước cho E2E: backend chạy ở localhost:8000 + tài khoản test (mặc định admin@example.com / changethis; đổi qua TEST_EMAIL, TEST_PASSWORD, PLAYWRIGHT_BASE_URL).
- Sao chép skill sang tool khác: copy CẢ thư mục (kèm references/) vào .github/skills/ (Copilot) hoặc .claude/skills/ (Claude). Trong Copilot tương đương prompt file /write-all-frontend-tests + /setup-frontend-testing.
-->

# Frontend Testing

Set up testing and write all test cases for the frontend. Work in `frontend/`. Do phases in order; verify after each. Optimized for reliable execution: give exact file contents, follow the rules strictly.

The full, detailed runbook (all config file contents, the complete test-case catalog, and templates) lives in `references/runbook.md`. Read it when you need exact content.

## Mandatory rules

1. One test case = one `test()` / `it()`. Name starts with the case ID (e.g. `LOGIN-02: ...`).
2. AAA structure: Arrange → Act → Assert. Each test independent.
3. Selectors: only `getByTestId` or `getByRole`. Never CSS class / xpath.
4. If a needed `data-testid` is missing, add it to the component first.
5. Do not add libraries beyond the Phase 0 list.
6. A test is "done" only when it runs and is green.

## Phases

1. **Install** (Phase 0): `npm install -D vitest @testing-library/react @testing-library/jest-dom @testing-library/user-event jsdom` and `npx playwright install --with-deps chromium`.
2. **Scripts** (Phase 1): add `test`, `test:watch`, `test:e2e`, `test:e2e:ui` to `package.json`.
3. **Configs** (Phases 2-4): create `vitest.config.ts`, `vitest.setup.ts`, `playwright.config.ts` — exact contents in `references/runbook.md`.
4. **Auth fixture** (Phase 5): `tests/e2e/auth.setup.ts` + add `tests/e2e/.auth/` to `.gitignore`.
5. **Add missing `data-testid`** (Phase 6): in `src/components/Chat/ChatInterface.tsx` add `chat-input`, `chat-send`, `user-message`, `assistant-message`. Login already has its testids.
6. **Write all test cases** (Phase 7): implement every row of the catalog in `references/runbook.md`.
   - Do the **Vitest component/unit tests first** (no backend needed) so you get green results fast.
   - Then E2E (needs backend running + test credentials).

## Templates

See `references/runbook.md` Phase 8 for the Playwright and Vitest+RTL templates, including how to mock `streamChat`.

## Done when

```bash
cd frontend
npm run test
npm run lint
npm run test:e2e   # needs backend at localhost:8000
```
All exit code 0, every catalog case has a matching test (name = ID), selectors are testid/role only.
