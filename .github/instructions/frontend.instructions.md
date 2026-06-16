---
applyTo: "frontend/src/**/*.ts,frontend/src/**/*.tsx"
---

# Frontend Conventions

## Code Style (Biome)

- **Double quotes** for strings.
- **No semicolons** at end of statements.
- **2-space indent**.
- Self-closing JSX elements when no children.

## Service / API Layer

**Canonical location**: `frontend/src/lib/services/`.
**API client**: always import from `frontend/src/lib/api-client.ts`.

```typescript
// ✅ GOOD — new service goes in src/lib/services/
import { apiClient } from "../api-client"

export const getItems = async (skip = 0, limit = 100) => {
  const { data } = await apiClient.get("/api/v1/items/", { params: { skip, limit } })
  return data
}

// ❌ BAD — do not create files in src/services/ (legacy location)
// ❌ BAD — do not create a second axios instance
```

## Data Fetching — TanStack Query

```typescript
// ✅ GOOD
const { data, isPending } = useQuery({
  queryKey: ["items", skip, limit],
  queryFn: () => getItems(skip, limit),
})

// ❌ BAD — useEffect + useState for fetching
```

## Forms — react-hook-form + zod

```typescript
// ✅ GOOD
const schema = z.object({ name: z.string().min(1) })
const form = useForm<z.infer<typeof schema>>({ resolver: zodResolver(schema) })

// ❌ BAD — manual useState for each field
```

## Routing — TanStack Router (file-based)

- New pages go in `src/routes/`.
- Use `createFileRoute` / `createLazyFileRoute`.
- Run `npm run dev` once to regenerate `routeTree.gen.ts` after adding a route.
- **Never edit `routeTree.gen.ts` manually.**

## UI Components

- Use existing components from `src/components/ui/` (shadcn).
- **Never modify files in `src/components/ui/`** — update via shadcn CLI.
- Use `cn()` from `src/lib/utils.ts` for conditional class merging.

## TypeScript

- Avoid `any` — define explicit types or use `unknown`.
- Avoid non-null assertions (`!`) unless genuinely safe.
