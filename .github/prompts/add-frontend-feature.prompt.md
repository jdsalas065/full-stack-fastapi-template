---
description: Add a full frontend feature (service → query hook → route/page → form). Use when adding a new page or UI feature.
---

# Add Frontend Feature: ${input:featureName}

Follow these steps **in order**. Complete and verify each step before moving to the next.

## Checklist

- [ ] **1. Service** — Create or extend `frontend/src/lib/services/${input:featureName}.ts`
  - Use `apiClient` from `../api-client`.
  - Export typed async functions for each API call.
  - Define TypeScript interfaces for request/response shapes.
  - Do NOT create files in `src/services/` — use `src/lib/services/` only.

- [ ] **2. TanStack Query hooks** — Add query/mutation hooks in the same service file or a colocated `hooks/use${input:featureName}.ts`
  ```typescript
  export const use${input:featureName}List = () =>
    useQuery({ queryKey: ["${input:featureName}"], queryFn: get${input:featureName}List })
  ```

- [ ] **3. Route/Page** — Create `frontend/src/routes/_layout/${input:featureName}.tsx` (or nested as needed)
  - Use `createFileRoute` or `createLazyFileRoute`.
  - Fetch data with the query hook; show loading skeleton while `isPending`.
  - Run `npm run dev` once after creating the file to regenerate `routeTree.gen.ts`.

- [ ] **4. Form** (if needed) — Use `react-hook-form` + `zod`:
  ```typescript
  const schema = z.object({ name: z.string().min(1) })
  type FormData = z.infer<typeof schema>
  const form = useForm<FormData>({ resolver: zodResolver(schema) })
  ```

- [ ] **5. UI components** — Use existing components from `src/components/ui/`.
  - DO NOT modify files in `src/components/ui/`.
  - Use `cn()` from `src/lib/utils.ts` for conditional classes.

- [ ] **6. Navigation** (if needed) — Add a link in the sidebar or nav component.

- [ ] **7. Verify** — Run:
  ```bash
  cd frontend && npm run lint && npm run build
  ```
  Fix all errors before declaring done.
