---
name: add-frontend-feature
description: Add a full frontend feature to this React 19 + TanStack + Tailwind project (API service, TanStack Query hook, file-based route/page, react-hook-form + zod form, shadcn UI). Use when adding a new page, screen, or UI feature on the frontend.
---

<!--
HƯỚNG DẪN DÙNG (How to use)
- Antigravity tự nhận skill này trong project (.agent/skills/). Để kích hoạt, nhắn agent kèm tên feature, ví dụ:
    "Dùng skill add-frontend-feature để thêm feature: orders"
  hoặc chỉ mô tả: "Thêm trang quản lý orders" — agent tự khớp theo description.
- Thay <feature> trong các bước bằng tên thật (camelCase cho hook/biến, kebab/lowercase cho route).
- Yêu cầu trước: frontend chạy được (npm install xong); API backend tương ứng đã có.
- Sau khi tạo route mới, chạy `npm run dev` 1 lần để regenerate routeTree.gen.ts.
- Sao chép skill sang tool khác: copy thư mục này vào .github/skills/ (Copilot) hoặc .claude/skills/ (Claude). Trong Copilot tương đương prompt file /add-frontend-feature.
-->

# Add Frontend Feature

Add a new feature following project conventions. Work in `frontend/`. Do each step in order; match existing patterns; do not add dependencies not already in `package.json`.

## Steps

1. **Service** — Create/extend `frontend/src/lib/services/<feature>.ts`.
   - Import `apiClient` from `../api-client`. Export typed async functions.
   - Define TypeScript interfaces for request/response.
   - Canonical location is `src/lib/services/`. Do NOT create files in `src/services/` and do NOT create a second axios instance.
2. **TanStack Query hooks**:
   ```typescript
   export const useFeatureList = () =>
     useQuery({ queryKey: ["feature"], queryFn: getFeatureList })
   ```
3. **Route/Page** — `frontend/src/routes/_layout/<feature>.tsx` (or nested).
   - Use `createFileRoute` / `createLazyFileRoute`.
   - Fetch via the query hook; show skeleton while `isPending`.
   - Run `npm run dev` once to regenerate `routeTree.gen.ts`. Never edit `routeTree.gen.ts` by hand.
4. **Form** (if needed) — `react-hook-form` + `zod`:
   ```typescript
   const schema = z.object({ name: z.string().min(1) })
   const form = useForm<z.infer<typeof schema>>({ resolver: zodResolver(schema) })
   ```
5. **UI** — Use existing components from `src/components/ui/`. Never modify `src/components/ui/`. Use `cn()` from `src/lib/utils.ts` for conditional classes.
6. **Navigation** (if needed) — add a link in the sidebar/nav.

## Code style (Biome)

Double quotes, no semicolons, 2-space indent, self-closing JSX when no children. Avoid `any` and non-null assertions.

## Done when

```bash
cd frontend && npm run lint && npm run build
```
All commands exit 0.
