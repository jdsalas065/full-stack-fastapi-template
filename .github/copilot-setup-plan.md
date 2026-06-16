# AI Agent Quality Setup — GitHub Copilot (VS Code)

Công cụ thực tế: GitHub Copilot trong VS Code (không phải Cursor). Mục tiêu: chất lượng code cao, đúng convention sẵn có, và đặc biệt CHẠY ỔN ĐỊNH với model yếu (qwen 3.6 plus) nhờ hướng dẫn cực kỳ rõ ràng + recipe có sẵn + guardrails tất định (format-on-save) không phụ thuộc vào "độ thông minh" của model.

Nội dung các file hướng dẫn viết bằng tiếng Anh.

## Cơ chế tùy biến của Copilot

```
GitHub Copilot (VS Code)
  ├── .github/copilot-instructions.md          ← always-on, mọi chat request
  ├── .github/instructions/*.instructions.md   ← applyTo glob theo loại file
  └── .github/prompts/*.prompt.md              ← recipe gọi bằng / trong chat

Copilot sửa file → VS Code format-on-save (ruff/biome) → file luôn đúng style
```

- `.github/copilot-instructions.md`: hướng dẫn always-on cho mọi chat request.
- `.github/instructions/*.instructions.md`: frontmatter `applyTo` (glob) để chỉ áp dụng theo loại file.
- `.github/prompts/*.prompt.md`: prompt tái sử dụng, gọi bằng `/` trong chat (tương đương "skill").
- `.vscode/settings.json`: format-on-save chạy ruff/biome tất định sau mỗi lần lưu.

## Các file đã tạo

### 1. `.github/copilot-instructions.md` (always-on)

Ngắn gọn, đậm tính ra lệnh (tốt cho model yếu). Gồm:
- Stack + kiến trúc backend phân lớp `api/routes -> services -> crud -> models/schemas`, frontend React 19 + TanStack Query/Router + Tailwind/shadcn.
- Lệnh canonical: backend `uv run ...`; frontend `npm run dev|lint|build`.
- DANH SÁCH CẤM SỬA TAY: `frontend/src/routeTree.gen.ts`, `frontend/src/client/**`, `frontend/src/components/ui/**`, các file revision cũ trong `backend/app/alembic/versions/**`.
- Quy tắc cho model yếu: làm từng bước nhỏ; bám theo pattern file mẫu hiện có; không thêm thư viện mới nếu chưa có trong `pyproject.toml`/`package.json`; không viết lại file lớn.
- Checklist verify cuối mỗi task.

### 2. `.github/instructions/*.instructions.md` (theo path)

- `backend.instructions.md` (`applyTo: "backend/**/*.py"`): custom exceptions, `get_logger`, keyword-only args, type hints mypy strict, route có docstring + `response_model`, dùng `SessionDep`/`CurrentUser`. Kèm ví dụ GOOD/BAD.
- `frontend.instructions.md` (`applyTo: "frontend/src/**/*.ts,frontend/src/**/*.tsx"`): style Biome, TanStack Query/Router, react-hook-form + zod, không sửa `components/ui/**`. Chuẩn service: `src/lib/services/`.
- `migrations.instructions.md` (`applyTo: models + alembic`): đổi model phải tạo migration alembic, không sửa tay revision cũ.

### 3. `.github/prompts/*.prompt.md` (recipe = "skill")

Recipe tất định giúp model yếu đi đúng đường. Gọi bằng `/` trong chat.

- `/add-backend-resource`: checklist 10 bước thêm resource CRUD đầy đủ (model → schema → crud → service → route → router → migration → test → verify).
- `/add-frontend-feature`: checklist 7 bước thêm feature frontend (service → query hook → route → form → UI → nav → verify).
- `/verify-changes`: chạy toàn bộ ruff + mypy + pytest + biome + build, fix đến khi sạch.

### 4. `.vscode/settings.json` + `.vscode/extensions.json` (guardrail tất định — local only, gitignored)

- `editor.formatOnSave: true`; default formatter Python = Ruff, TS/TSX/JSON = Biome.
- Bật `chat.useAgentsMdFile` và `github.copilot.chat.codeGeneration.useInstructionFiles`.
- Extensions đề xuất: `charliermarsh.ruff`, `biomejs.biome`, `ms-python.python`, `ms-python.mypy-type-checker`.

## Quyết định đã chốt

- Vị trí service chuẩn frontend: `frontend/src/lib/services/` (đi cùng api-client trong `src/lib`). Không tạo file mới trong `src/services/`.

## Cách dùng

1. Mở repo trong VS Code → Copilot tự nạp `copilot-instructions.md` cho mọi chat.
2. Khi mở file backend/frontend → instructions tương ứng được nạp tự động theo `applyTo`.
3. Khi làm task lặp lại → gõ `/add-backend-resource` hoặc `/add-frontend-feature` trong chat.
4. Mỗi lần lưu file → VS Code tự format theo ruff/biome.
5. Trước khi commit → gõ `/verify-changes` để chạy toàn bộ kiểm tra.
