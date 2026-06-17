# Frontend Testing Runbook

> Detailed reference for the `frontend-testing` skill. Stack: React 19, Vite 7, TanStack Router/Query, Biome. Work in `frontend/`. Do phases in order; verify after each.

## Mandatory rules

1. One test case = one `test()` / `it()`. Name starts with the ID, e.g. `LOGIN-02: ...`.
2. AAA: Arrange → Act → Assert. Each test independent.
3. Selectors: only `getByTestId` or `getByRole`. Never CSS class / xpath / `nth-child`.
4. If a needed `data-testid` is missing, add it to the component first.
5. If unsure of a selector, run `npx playwright codegen <url>` to record real actions, then adapt to the template.
6. Do not add libraries beyond the Phase 0 list.
7. A test is "done" only when it runs and is green.

---

## Phase 0 — Install dependencies

```bash
# Component / unit tests
npm install -D vitest @testing-library/react @testing-library/jest-dom @testing-library/user-event jsdom

# E2E (Playwright already in package.json, just install the browser)
npx playwright install --with-deps chromium
```

Verify: `npx vitest --version` and `npx playwright --version`.

---

## Phase 1 — Add scripts to `package.json`

```json
"test": "vitest run",
"test:watch": "vitest",
"test:e2e": "playwright test",
"test:e2e:ui": "playwright test --ui"
```

---

## Phase 2 — `frontend/vitest.config.ts`

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
  resolve: {
    alias: { "@": path.resolve(__dirname, "./src") },
  },
})
```

---

## Phase 3 — `frontend/vitest.setup.ts`

```ts
import "@testing-library/jest-dom/vitest"
import { cleanup } from "@testing-library/react"
import { afterEach } from "vitest"

afterEach(() => {
  cleanup()
})
```

---

## Phase 4 — `frontend/playwright.config.ts`

```ts
import { defineConfig, devices } from "@playwright/test"

export default defineConfig({
  testDir: "./tests/e2e",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  reporter: "html",
  use: {
    baseURL: process.env.PLAYWRIGHT_BASE_URL || "http://localhost:5173",
    trace: "on-first-retry",
    testIdAttribute: "data-testid",
  },
  projects: [
    { name: "setup", testMatch: /auth\.setup\.ts/ },
    {
      name: "chromium",
      use: {
        ...devices["Desktop Chrome"],
        storageState: "tests/e2e/.auth/user.json",
      },
      dependencies: ["setup"],
    },
  ],
  webServer: {
    command: "npm run dev",
    url: "http://localhost:5173",
    reuseExistingServer: !process.env.CI,
    timeout: 120000,
  },
})
```

---

## Phase 5 — Auth fixture `frontend/tests/e2e/auth.setup.ts`

Log in once via UI and save the session so later E2E tests skip login.

```ts
import { expect, test as setup } from "@playwright/test"

const authFile = "tests/e2e/.auth/user.json"

setup("authenticate", async ({ page }) => {
  await page.goto("/login")
  await page
    .getByTestId("email-input")
    .fill(process.env.TEST_EMAIL || "admin@example.com")
  await page
    .getByTestId("password-input")
    .fill(process.env.TEST_PASSWORD || "changethis")
  await page.getByRole("button", { name: "Log In" }).click()
  await expect(page).not.toHaveURL(/.*login/)
  await page.context().storageState({ path: authFile })
})
```

Add `tests/e2e/.auth/` to `frontend/.gitignore`.

---

## Phase 6 — Add missing `data-testid` (before writing E2E)

In `src/components/Chat/ChatInterface.tsx` (currently has none):

- Input: `<Input ... data-testid="chat-input" />`
- Send button: `<Button type="submit" ... data-testid="chat-send" />`
- User message bubble: `data-testid="user-message"`
- Assistant message bubble: `data-testid="assistant-message"`

Login (`src/routes/login.tsx`) already has `email-input` and `password-input`.

Convention: when a screen lacks a needed testid, add `data-testid="<feature>-<element>"` to the component first.

---

## Phase 7 — Write all test cases (catalog)

One row = one test. Vitest component tests as `*.test.tsx` next to the source in `src/`. E2E in `tests/e2e/<feature>.spec.ts`.

### 7.1 Auth — `tests/e2e/auth.spec.ts`

| ID | Given | When | Then |
|---|---|---|---|
| LOGIN-01 | at `/login` | enter valid email + pass, click Log In | URL leaves `/login` |
| LOGIN-02 | at `/login` | click Log In with empty email | a `FormMessage` error appears |
| LOGIN-03 | at `/login` | enter password < 8 chars | "at least 8 characters" error |
| LOGIN-04 | at `/login` | enter wrong password | error shown, stays on `/login` |
| SIGNUP-01 | at `/signup` | fill valid form, submit | account created / redirected |
| RECOVER-01 | at `/recover-password` | enter email, submit | "email sent" notice shown |

### 7.2 Chat — `tests/e2e/chat.spec.ts` (requires auth)

| ID | Given | When | Then |
|---|---|---|---|
| CHAT-01 | at `/chat` | type "Hello", click Send | `user-message` contains "Hello" |
| CHAT-02 | at `/chat`, message sent | wait for response | `assistant-message` visible with content |
| CHAT-03 | at `/chat` | empty input | Send button is `disabled` |
| CHAT-04 | sending (loading) | — | input disabled, button shows "Sending..." |

### 7.3 Table1 CRUD — `tests/e2e/table1.spec.ts`

| ID | Given | When | Then |
|---|---|---|---|
| TABLE-01 | at `/table1` | page loads | table + list shown |
| TABLE-02 | at `/table1` | Add → fill form → save | new item appears in table |
| TABLE-03 | item exists | Edit → change name → save | new name shown |
| TABLE-04 | item exists | Delete → confirm | item removed from table |

### 7.4 User Settings — `tests/e2e/settings.spec.ts`

| ID | Given | When | Then |
|---|---|---|---|
| SET-01 | logged in | open User Information → change name → save | success notice |
| SET-02 | — | Change Password with valid new pass | success notice |
| SET-03 | — | Change Password with mismatched confirm | validation error |

### 7.5 Component / Unit — Vitest (`src/.../*.test.tsx`)

| ID | File | Checks |
|---|---|---|
| C-LOGIN-01 | `src/routes/login.test.tsx` | render form, submit empty → `FormMessage` |
| C-LOGIN-02 | `src/routes/login.test.tsx` | invalid email format → validation error |
| C-CHAT-01 | `src/components/Chat/ChatInterface.test.tsx` | Send disabled when empty, enabled with text |
| C-CHAT-02 | `src/components/Chat/ChatInterface.test.tsx` | type + submit (mock `streamChat`) → `user-message` shown |

> Extend: for each new route/feature, add a row to the matching table and write the test using the templates below.

---

## Phase 8 — Templates

### E2E (Playwright)

```ts
import { expect, test } from "@playwright/test"

test("CHAT-01: user message shown after send", async ({ page }) => {
  // Arrange
  await page.goto("/chat")
  // Act
  await page.getByTestId("chat-input").fill("Hello")
  await page.getByTestId("chat-send").click()
  // Assert
  await expect(page.getByTestId("user-message")).toContainText("Hello")
})
```

### Component (Vitest + React Testing Library)

```tsx
import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { describe, expect, it } from "vitest"
import { ChatInterface } from "@/components/Chat/ChatInterface"

describe("ChatInterface", () => {
  it("C-CHAT-01: Send disabled when input empty", async () => {
    // Arrange
    render(<ChatInterface />)
    const send = screen.getByTestId("chat-send")
    // Assert (initial)
    expect(send).toBeDisabled()
    // Act
    await userEvent.type(screen.getByTestId("chat-input"), "hi")
    // Assert
    expect(send).toBeEnabled()
  })
})
```

> If a component calls an API (TanStack Query / fetch / service), wrap it in `QueryClientProvider` and **mock** the service. Example mocking `streamChat`:
>
> ```tsx
> import { vi } from "vitest"
> vi.mock("@/services/chatService", () => ({
>   streamChat: async function* () {
>     yield { event: "start", conversation_id: "test" }
>     yield { event: "token", delta: "Hi" }
>     yield { event: "done", content: "Hi" }
>   },
> }))
> ```
>
> If a case is too hard to mock at the component level, move it to an E2E test instead.

---

## Phase 9 — Self-correct loop

```bash
cd frontend
npm run test       # Vitest must be green
npm run lint       # Biome must be clean
npm run test:e2e   # Playwright must be green (needs backend at localhost:8000)
```

On failure:
- **Vitest**: read the error → fix assertion/mock → rerun.
- **Playwright**: inspect trace (`npx playwright show-trace`) or HTML report → fix selector/waiting → rerun.
- Repeat until all three exit code 0.

---

## Definition of Done

- [ ] Every catalog case (Phase 7) has a matching test; test name matches the ID.
- [ ] `npm run test`, `npm run lint`, `npm run test:e2e` all exit code 0.
- [ ] Only `getByTestId` / `getByRole` selectors; no CSS class/xpath.
- [ ] Missing `data-testid` added (chat: input/send/user-message/assistant-message).
- [ ] No libraries added beyond the Phase 0 list.

---

## Environment notes

- E2E specs need the **backend running** and a valid test account. Defaults: `admin@example.com` / `changethis`; override via `TEST_EMAIL`, `TEST_PASSWORD`, `PLAYWRIGHT_BASE_URL`.
- Vitest component tests need **no backend** — do these first for fast green results.
- Frontend dev server runs at `http://localhost:5173` (Vite default).
