# Frontend Testing Runbook (for a weak AI model)

> Mục đích: paste runbook này cho một AI agent dùng model yếu để nó **tự cài đặt, viết hết test case, và chạy đến khi xanh**. Làm tuần tự, KHÔNG bỏ bước. Sau mỗi phase chạy lệnh verify, sửa sạch lỗi rồi mới sang phase sau.
>
> Stack: React 19, Vite 7, TanStack Router/Query, Biome. Thư mục làm việc: `frontend/`.

## Nguyên tắc bắt buộc (đọc trước khi làm)

1. **1 test case = 1 `test()` / `it()`**. Tên test bắt đầu bằng ID, ví dụ `LOGIN-02: ...`.
2. **Cấu trúc AAA**: Arrange → Act → Assert. Mỗi test độc lập, không phụ thuộc test khác.
3. **Selector chỉ dùng `getByTestId` hoặc `getByRole`** — CẤM dùng CSS class / xpath / `nth-child`.
4. Nếu UI **chưa có `data-testid`** cần thiết → thêm `data-testid` vào component trước, rồi mới viết test.
5. Không chắc selector → chạy `npx playwright codegen <url>` để ghi thao tác sinh code thật, rồi sửa theo template.
6. **Không thêm thư viện** ngoài danh sách trong Phase 0.
7. Test chỉ tính là "xong" khi **chạy được và xanh**.

---

## Phase 0 — Cài dependencies

Chạy trong `frontend/`:

```bash
# Component / unit test
npm install -D vitest @testing-library/react @testing-library/jest-dom @testing-library/user-event jsdom

# E2E (Playwright đã có sẵn trong package.json, chỉ cần tải browser)
npx playwright install --with-deps chromium
```

Verify:

```bash
npx vitest --version
npx playwright --version
```

---

## Phase 1 — Thêm scripts vào `package.json`

Thêm vào mục `"scripts"` của `frontend/package.json`:

```json
"test": "vitest run",
"test:watch": "vitest",
"test:e2e": "playwright test",
"test:e2e:ui": "playwright test --ui"
```

---

## Phase 2 — Tạo `frontend/vitest.config.ts`

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

## Phase 3 — Tạo `frontend/vitest.setup.ts`

```ts
import "@testing-library/jest-dom/vitest"
import { cleanup } from "@testing-library/react"
import { afterEach } from "vitest"

afterEach(() => {
  cleanup()
})
```

---

## Phase 4 — Tạo `frontend/playwright.config.ts`

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

Đăng nhập 1 lần qua UI rồi lưu session; các test E2E sau khỏi login lại.

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

Thêm dòng này vào `frontend/.gitignore`:

```
tests/e2e/.auth/
```

---

## Phase 6 — Thêm `data-testid` còn thiếu (làm TRƯỚC khi viết E2E)

Trong `src/components/Chat/ChatInterface.tsx` (hiện chưa có testid nào):

- Ô input: `<Input ... data-testid="chat-input" />`
- Nút gửi: `<Button type="submit" ... data-testid="chat-send" />`
- Bong bóng message user: thêm `data-testid="user-message"`
- Bong bóng message assistant: thêm `data-testid="assistant-message"`

Login (`src/routes/login.tsx`) đã có sẵn `data-testid="email-input"` và `data-testid="password-input"` — KHÔNG cần thêm.

Quy ước: khi viết test cho bất kỳ màn hình nào mà thiếu testid, thêm testid vào component trước theo dạng `data-testid="<feature>-<phần-tử>"`.

---

## Phase 7 — Viết HẾT test case theo catalog

Mỗi dòng trong bảng = 1 test. Component test (Vitest) đặt cạnh file dưới dạng `*.test.tsx` trong `src/`. E2E đặt trong `tests/e2e/<feature>.spec.ts`.

### 7.1 Auth — `tests/e2e/auth.spec.ts` (E2E)

| ID | Given | When | Then (assert) |
|---|---|---|---|
| LOGIN-01 | ở `/login` | nhập email + pass đúng, bấm Log In | URL rời khỏi `/login` |
| LOGIN-02 | ở `/login` | bấm Log In khi email trống | hiện `FormMessage` lỗi |
| LOGIN-03 | ở `/login` | nhập password < 8 ký tự | hiện lỗi "at least 8 characters" |
| LOGIN-04 | ở `/login` | nhập sai mật khẩu | hiện thông báo lỗi, vẫn ở `/login` |
| SIGNUP-01 | ở `/signup` | điền form hợp lệ, submit | tạo account thành công / điều hướng |
| RECOVER-01 | ở `/recover-password` | nhập email, submit | hiện thông báo đã gửi |

### 7.2 Chat — `tests/e2e/chat.spec.ts` (E2E, cần đã đăng nhập)

| ID | Given | When | Then (assert) |
|---|---|---|---|
| CHAT-01 | ở `/chat` | gõ "Hello", bấm Send | `user-message` chứa "Hello" hiện ra |
| CHAT-02 | ở `/chat`, đã gửi tin | chờ phản hồi | `assistant-message` hiển thị và có nội dung |
| CHAT-03 | ở `/chat` | input trống | nút Send bị `disabled` |
| CHAT-04 | đang gửi (loading) | — | input bị disabled, nút hiện "Sending..." |

### 7.3 Table1 CRUD — `tests/e2e/table1.spec.ts` (E2E)

| ID | Given | When | Then (assert) |
|---|---|---|---|
| TABLE-01 | ở `/table1` | trang load | bảng + danh sách hiển thị |
| TABLE-02 | ở `/table1` | bấm Add → điền form → lưu | item mới xuất hiện trong bảng |
| TABLE-03 | có item | bấm Edit → đổi tên → lưu | tên mới hiển thị |
| TABLE-04 | có item | bấm Delete → xác nhận | item biến mất khỏi bảng |

### 7.4 User Settings — `tests/e2e/settings.spec.ts` (E2E)

| ID | Given | When | Then (assert) |
|---|---|---|---|
| SET-01 | đã đăng nhập | mở User Information → đổi tên → lưu | thấy thông báo thành công |
| SET-02 | — | Change Password với pass mới hợp lệ | thông báo thành công |
| SET-03 | — | Change Password với confirm không khớp | hiện lỗi validation |

### 7.5 Component / Unit — Vitest (`src/.../*.test.tsx`)

| ID | File | Kiểm tra |
|---|---|---|
| C-LOGIN-01 | `src/routes/login.test.tsx` | render form, submit khi trống → có `FormMessage` |
| C-LOGIN-02 | `src/routes/login.test.tsx` | nhập email sai định dạng → báo lỗi validation |
| C-CHAT-01 | `src/components/Chat/ChatInterface.test.tsx` | nút Send disable khi trống, enable khi có text |
| C-CHAT-02 | `src/components/Chat/ChatInterface.test.tsx` | gõ text + submit (mock `streamChat`) → hiện `user-message` |

> Mở rộng: với mỗi route/feature mới, thêm dòng vào bảng tương ứng rồi viết test theo template ở Phase dưới.

---

## Phase 8 — Template chuẩn (copy rồi điền)

### E2E (Playwright)

```ts
import { expect, test } from "@playwright/test"

test("CHAT-01: tin nhắn user hiển thị sau khi gửi", async ({ page }) => {
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
  it("C-CHAT-01: nút Send disabled khi input trống", async () => {
    // Arrange
    render(<ChatInterface />)
    const send = screen.getByTestId("chat-send")
    // Assert (trạng thái đầu)
    expect(send).toBeDisabled()
    // Act
    await userEvent.type(screen.getByTestId("chat-input"), "hi")
    // Assert
    expect(send).toBeEnabled()
  })
})
```

> Lưu ý: component gọi API (TanStack Query / fetch / service) thì wrap trong `QueryClientProvider` và **mock** service. Ví dụ mock `streamChat`:
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
> Nếu một case quá khó mock ở tầng component → chuyển nó xuống test E2E thay vì cố ép.

---

## Phase 9 — Vòng lặp tự sửa (self-correct)

```bash
cd frontend
npm run test       # Vitest phải xanh
npm run lint       # Biome phải sạch
npm run test:e2e   # Playwright phải xanh (cần backend chạy ở localhost:8000)
```

Khi fail:
- **Vitest**: đọc message lỗi → sửa assertion/mock → chạy lại.
- **Playwright**: xem trace `npx playwright show-trace` hoặc report HTML → sửa selector/chờ element → chạy lại.
- Lặp đến khi **cả 3 lệnh đều xanh (exit code 0)**.

---

## Definition of Done

- [ ] Mọi case trong catalog (Phase 7) đã có test tương ứng; tên test khớp ID.
- [ ] `npm run test`, `npm run lint`, `npm run test:e2e` đều exit code 0.
- [ ] Chỉ dùng `getByTestId` / `getByRole`, không có selector CSS class/xpath.
- [ ] Đã thêm `data-testid` còn thiếu (chat: input/send/user-message/assistant-message).
- [ ] Không thêm thư viện ngoài danh sách Phase 0.

---

## Ghi chú môi trường

- E2E (`auth.spec.ts`, `chat.spec.ts`, `table1.spec.ts`, `settings.spec.ts`) cần **backend chạy** và một tài khoản test hợp lệ. Mặc định runbook dùng `admin@example.com` / `changethis`; chỉnh qua biến môi trường `TEST_EMAIL`, `TEST_PASSWORD`, `PLAYWRIGHT_BASE_URL`.
- Component test (Vitest) **không cần backend** — ưu tiên làm nhóm này trước để có kết quả xanh ngay.
- Dev server frontend chạy ở `http://localhost:5173` (Vite mặc định).
