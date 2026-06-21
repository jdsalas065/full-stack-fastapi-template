# PROMPT: Bảng đối soát thông tin OCR tài liệu (Layered Verification Table)

> File này là **prompt hoàn chỉnh** để đưa cho một AI coding agent (kể cả model yếu).
> Agent chỉ cần **làm tuần tự từng STEP**, **copy-paste đúng code**, **KHÔNG sáng tạo thêm**.
> Mọi đường dẫn file đều tính từ thư mục `frontend/`.

---

## 0. BỐI CẢNH DỰ ÁN (đọc kỹ, KHÔNG được làm sai)

Đây là frontend của một template FastAPI full-stack. Tech stack **CỐ ĐỊNH**:

| Hạng mục | Công nghệ | Ghi chú bắt buộc |
|---|---|---|
| Framework | React 19 + TypeScript | |
| Build tool | Vite 7 | |
| Router | TanStack Router (file-based, tự sinh `routeTree.gen.ts`) | |
| Bảng | shadcn `Table` (`@/components/ui/table`) | KHÔNG cần TanStack Table cho task này |
| UI components | shadcn/ui (Radix) trong `src/components/ui/` | **KHÔNG sửa** file trong thư mục này |
| CSS | Tailwind CSS v4 | dùng class utility, KHÔNG viết CSS file mới |
| Icons | `lucide-react` | |
| Linter/Formatter | **Biome** | xem QUY TẮC CODE bên dưới |

### QUY TẮC CODE (Biome) — TUYỆT ĐỐI tuân theo:
- **KHÔNG dùng dấu chấm phẩy `;`** ở cuối dòng (semicolons: asNeeded).
- **Dùng nháy kép `"`**, không dùng nháy đơn.
- **Thụt lề 2 spaces**.
- Import nội bộ dùng alias **`@/`** = `src/` (ví dụ `@/components/ui/table`).
- Dùng **self-closing tag** khi element rỗng.
- **KHÔNG có `else` thừa** sau `return`, **KHÔNG dùng ternary lồng nhau**.
- KHÔNG bọc `<button>`/`<input>` bên trong một `<button>` khác (HTML không hợp lệ).

### Component shadcn cần dùng (đã có sẵn, KHÔNG cài thêm):
`@/components/ui/table`, `@/components/ui/button`, `@/components/ui/input`,
`@/components/ui/popover`, và component sẵn có `@/components/Common/MediaViewer`.

> PHẠM VI: Task này chỉ làm **CÁI BẢNG đối soát**. Phần vẽ bounding box trên ảnh đã được
> xử lý sẵn ở backend (ảnh trả về đã có khung), nên frontend **KHÔNG tự vẽ overlay**.
> Ảnh chỉ cần click để xem nhanh bằng `MediaViewer`.

---

## 1. MỤC TIÊU & THIẾT KẾ UX (đọc để hiểu, KHÔNG bịa thêm tính năng)

Làm một bảng **đối soát kết quả OCR tài liệu**. Hệ thống OCR ra hóa đơn gồm các trường:
**Name, Money, Date, Currency**.

Bảng: **mỗi hàng = một tài liệu** (vd `abc.png`), **mỗi cột = một trường**.
Mỗi ô (1 trường của 1 tài liệu) có **5 lớp dữ liệu**:

| Lớp (LayerKey) | Ý nghĩa |
|---|---|
| `ocrA` | Giá trị OCR thô từ hệ thống A |
| `ocrB` | Giá trị OCR thô từ hệ thống B |
| `aggregated` | Giá trị tổng hợp từ tài liệu khác |
| `edited` | Giá trị user sửa tay |
| `final` | Giá trị chốt để dùng (mặc định hiển thị) |

**3 cơ chế UX để show hết 5 lớp trên CÙNG 1 bảng:**

1. **Layer switch (đổi mode lật cả bảng):** một thanh nút trên toolbar
   `Final · Edited · OCR A · OCR B · Aggregated`. Bấm phát → toàn bộ ô trong bảng
   hiển thị giá trị của lớp đó. Đây là cơ chế "lật bài" nhưng lật cả cỗ một lúc.
2. **Sửa inline:** khi đang ở lớp `Final`, mỗi ô là một `Input` sửa được ngay tại chỗ.
   Khi ở lớp khác, ô chỉ hiển thị read-only.
3. **Popover chi tiết 1 ô:** mỗi ô có icon nhỏ (Layers) → mở popover xếp chồng **cả 5 lớp**
   + nút "Dùng OCR A / OCR B / Aggregated" để gán nhanh vào Final.

**Animation (CSS thuần, không thêm thư viện) — gồm 6 hiệu ứng, mỗi cái nằm ở 1 file:**

| # | Hiệu ứng | File | Cơ chế |
|---|---|---|---|
| 1 | **Lật khi đổi lớp** | `FieldCell.tsx` (STEP 3) | `key={activeLayer}` + `animate-in fade-in-0 slide-in-from-bottom-1 duration-200` ở khối value |
| 2 | **Chấm trạng thái nảy** | `FieldCell.tsx` (STEP 3) | `key={status}` + `animate-in zoom-in-50 duration-300` ở chấm màu |
| 3 | **Flash xác nhận gán nhanh** | `FieldCell.tsx` (STEP 3) | state `flash` + `transition-colors duration-500` + nền vàng ~600ms |
| 4 | **Pill trượt trên LayerSwitch** | `LayerSwitch.tsx` (STEP 4) | 1 div pill `absolute` + `transition-all duration-300`, tính `left/width` theo index |
| 5 | **Row hover** | `OcrVerificationTable.tsx` (STEP 5) | `transition-colors hover:bg-muted/30` trên `TableRow` thân bảng |
| 6 | **Progress bar fill** | `OcrVerificationTable.tsx` (STEP 5) | thanh % trường đã khớp, `transition-all duration-500` để fill mượt khi sửa |

> Tất cả class `animate-in / fade-in-0 / slide-in-from-* / zoom-in-50` đều CÓ SẴN (component
> shadcn trong dự án đang dùng). KHÔNG cần cài thêm thư viện animation.

**Trạng thái mỗi ô (FieldStatus) + màu:**
- `match` (🟢 emerald): `ocrA === ocrB`.
- `mismatch` (🔴 red): `ocrA !== ocrB` → cần người xử lý.
- `edited` (🔵 blue): user đã sửa (final khác ocrA).
- `raw` (⚪ xám): chưa đụng tới.

**Cột phụ:**
- Cột đầu = **Tài liệu** (tên file + thumbnail click xem ảnh bằng `MediaViewer`).
- Cột cuối = **Trạng thái** tổng kết mỗi hàng dạng `3/4 ✓` (số trường không bị lệch).

> Dữ liệu là **mock hardcode** (chưa nối API). Mục 5 hướng dẫn nối API thật sau.

---

## 2. CÁC BƯỚC THỰC HIỆN (làm đúng thứ tự)

### STEP 1 — Tạo file dữ liệu mẫu + kiểu + helper

Tạo file mới **`src/data/ocrVerificationData.ts`** với nội dung **chính xác** sau:

```ts
export type FieldKey = "name" | "money" | "date" | "currency"

export type LayerKey = "final" | "edited" | "ocrA" | "ocrB" | "aggregated"

export type FieldStatus = "match" | "mismatch" | "edited" | "raw"

export interface FieldLayers {
  ocrA: string
  ocrB: string
  aggregated: string
  edited: string
  final: string
}

export interface DocumentRow {
  id: string
  fileName: string
  fileType: "image" | "pdf"
  fileUrl: string
  fields: Record<FieldKey, FieldLayers>
}

export const FIELD_DEFS: { key: FieldKey; label: string }[] = [
  { key: "name", label: "Name" },
  { key: "money", label: "Money" },
  { key: "date", label: "Date" },
  { key: "currency", label: "Currency" },
]

export const LAYER_DEFS: { key: LayerKey; label: string }[] = [
  { key: "final", label: "Final" },
  { key: "edited", label: "Edited" },
  { key: "ocrA", label: "OCR A" },
  { key: "ocrB", label: "OCR B" },
  { key: "aggregated", label: "Aggregated" },
]

export const STATUS_META: Record<
  FieldStatus,
  { label: string; dot: string; text: string }
> = {
  match: { label: "Khớp", dot: "bg-emerald-500", text: "text-emerald-600" },
  mismatch: { label: "Lệch", dot: "bg-red-500", text: "text-red-600" },
  edited: { label: "Đã sửa", dot: "bg-blue-500", text: "text-blue-600" },
  raw: {
    label: "Thô",
    dot: "bg-muted-foreground",
    text: "text-muted-foreground",
  },
}

export function getFieldStatus(layers: FieldLayers): FieldStatus {
  const edited = layers.edited.trim()
  if (edited !== "" && edited !== layers.ocrA) {
    return "edited"
  }
  if (layers.ocrA === layers.ocrB) {
    return "match"
  }
  return "mismatch"
}

export const ocrDocuments: DocumentRow[] = [
  {
    id: "doc-1",
    fileName: "abc.png",
    fileType: "image",
    fileUrl:
      "https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=800",
    fields: {
      name: {
        ocrA: "ACME Corp",
        ocrB: "ACME Corp",
        aggregated: "ACME Corp",
        edited: "",
        final: "ACME Corp",
      },
      money: {
        ocrA: "1,200,000",
        ocrB: "1,250,000",
        aggregated: "1,250,000",
        edited: "1,250,000",
        final: "1,250,000",
      },
      date: {
        ocrA: "20/06/2026",
        ocrB: "20/06/2026",
        aggregated: "",
        edited: "",
        final: "20/06/2026",
      },
      currency: {
        ocrA: "VND",
        ocrB: "USD",
        aggregated: "VND",
        edited: "",
        final: "",
      },
    },
  },
  {
    id: "doc-2",
    fileName: "def.pdf",
    fileType: "pdf",
    fileUrl:
      "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
    fields: {
      name: {
        ocrA: "Beta LLC",
        ocrB: "Beta LLC",
        aggregated: "Beta LLC",
        edited: "",
        final: "Beta LLC",
      },
      money: {
        ocrA: "980,000",
        ocrB: "980,000",
        aggregated: "980,000",
        edited: "",
        final: "980,000",
      },
      date: {
        ocrA: "18/06/2026",
        ocrB: "18/06/2026",
        aggregated: "",
        edited: "",
        final: "18/06/2026",
      },
      currency: {
        ocrA: "USD",
        ocrB: "USD",
        aggregated: "USD",
        edited: "",
        final: "USD",
      },
    },
  },
]
```

---

### STEP 2 — Popover chi tiết 1 ô (xếp chồng 5 lớp)

Tạo file mới **`src/components/OcrTable/CellLayersPopover.tsx`**:

```tsx
import {
  type FieldKey,
  type FieldLayers,
  FIELD_DEFS,
  LAYER_DEFS,
} from "@/data/ocrVerificationData"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

interface CellLayersPopoverProps {
  fieldKey: FieldKey
  layers: FieldLayers
  onChangeFinal: (value: string) => void
}

export function CellLayersPopover({
  fieldKey,
  layers,
  onChangeFinal,
}: CellLayersPopoverProps) {
  const label = FIELD_DEFS.find((f) => f.key === fieldKey)?.label ?? fieldKey
  const finalValue = layers.final

  return (
    <div className="space-y-3">
      <p className="text-sm font-semibold">Trường: {label}</p>
      <div className="space-y-1">
        {LAYER_DEFS.map((layer) => {
          const value = layers[layer.key]
          const isFinal = layer.key === "final"
          const isDiff = !isFinal && value !== "" && value !== finalValue
          return (
            <div
              key={layer.key}
              className="flex items-center justify-between gap-2 text-sm"
            >
              <span className="text-muted-foreground">{layer.label}</span>
              <span
                className={cn(
                  "font-medium",
                  isFinal && "text-primary",
                  isDiff && "text-amber-600",
                )}
              >
                {value || "—"}
              </span>
            </div>
          )
        })}
      </div>
      <div className="flex flex-wrap gap-2 border-t pt-3">
        <Button
          size="sm"
          variant="outline"
          onClick={() => onChangeFinal(layers.ocrA)}
        >
          Dùng OCR A
        </Button>
        <Button
          size="sm"
          variant="outline"
          onClick={() => onChangeFinal(layers.ocrB)}
        >
          Dùng OCR B
        </Button>
        <Button
          size="sm"
          variant="outline"
          onClick={() => onChangeFinal(layers.aggregated)}
        >
          Dùng Aggregated
        </Button>
      </div>
    </div>
  )
}
```

---

### STEP 3 — Ô dữ liệu (FieldCell): trạng thái + sửa inline + popover + animation

Tạo file mới **`src/components/OcrTable/FieldCell.tsx`**. Lưu ý 2 chỗ animation:
- `key={activeLayer}` + class `animate-in fade-in-0 slide-in-from-bottom-1 duration-200`
  ở khối value → hiệu ứng **lật khi đổi lớp**.
- state `flash` + `transition-colors duration-500` ở `div` ngoài → **flash xác nhận** khi gán nhanh.
  (Chú ý: chỉ nút trong popover dùng `handleQuickAssign` để flash; ô nhập inline dùng `onChangeFinal`
  trực tiếp nên gõ phím KHÔNG flash.)
- `key={status}` ở chấm màu → **chấm nảy** mỗi khi trạng thái ô đổi (vd sửa cho khớp → 🔴 sang 🔵).

```tsx
import { Layers } from "lucide-react"
import { useState } from "react"
import { CellLayersPopover } from "@/components/OcrTable/CellLayersPopover"
import { Input } from "@/components/ui/input"
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover"
import {
  type FieldKey,
  type FieldLayers,
  type LayerKey,
  getFieldStatus,
  STATUS_META,
} from "@/data/ocrVerificationData"
import { cn } from "@/lib/utils"

interface FieldCellProps {
  fieldKey: FieldKey
  layers: FieldLayers
  activeLayer: LayerKey
  onChangeFinal: (value: string) => void
}

export function FieldCell({
  fieldKey,
  layers,
  activeLayer,
  onChangeFinal,
}: FieldCellProps) {
  const [flash, setFlash] = useState(false)
  const status = getFieldStatus(layers)
  const meta = STATUS_META[status]
  const value = layers[activeLayer]
  const isEditable = activeLayer === "final"

  const handleQuickAssign = (next: string) => {
    onChangeFinal(next)
    setFlash(true)
    window.setTimeout(() => setFlash(false), 600)
  }

  return (
    <div
      className={cn(
        "flex items-center gap-2 rounded-md p-1 transition-colors duration-500",
        flash && "bg-amber-100 dark:bg-amber-950",
      )}
    >
      <span
        key={status}
        className={cn(
          "h-2 w-2 shrink-0 rounded-full duration-300 animate-in zoom-in-50",
          meta.dot,
        )}
        title={meta.label}
      />
      <div
        key={activeLayer}
        className="flex flex-1 items-center duration-200 animate-in fade-in-0 slide-in-from-bottom-1"
      >
        {isEditable ? (
          <Input
            value={value}
            onChange={(e) => onChangeFinal(e.target.value)}
            className="h-8"
          />
        ) : (
          <span className="flex-1 truncate text-sm">{value || "—"}</span>
        )}
      </div>
      <Popover>
        <PopoverTrigger asChild>
          <button
            type="button"
            className="shrink-0 rounded p-1 text-muted-foreground hover:bg-muted hover:text-foreground"
            aria-label="Xem các lớp dữ liệu"
          >
            <Layers className="h-4 w-4" />
          </button>
        </PopoverTrigger>
        <PopoverContent className="w-80" align="end">
          <CellLayersPopover
            fieldKey={fieldKey}
            layers={layers}
            onChangeFinal={handleQuickAssign}
          />
        </PopoverContent>
      </Popover>
    </div>
  )
}
```

---

### STEP 4 — Thanh đổi lớp (LayerSwitch) — có pill trượt

Tạo file mới **`src/components/OcrTable/LayerSwitch.tsx`**. Animation #4: một div "pill"
`absolute` nằm dưới các nút; vị trí `left` và `width` tính theo **index của lớp đang chọn**
(các nút đều `flex-1` nên rộng bằng nhau), cộng `transition-all duration-300` để pill
**trượt mượt** khi đổi lớp.

```tsx
import { type LayerKey, LAYER_DEFS } from "@/data/ocrVerificationData"
import { cn } from "@/lib/utils"

interface LayerSwitchProps {
  value: LayerKey
  onChange: (value: LayerKey) => void
}

export function LayerSwitch({ value, onChange }: LayerSwitchProps) {
  const activeIndex = LAYER_DEFS.findIndex((layer) => layer.key === value)
  const count = LAYER_DEFS.length

  return (
    <div className="relative inline-flex rounded-md border bg-muted/40 p-1">
      <div
        className="absolute inset-y-1 rounded bg-primary transition-all duration-300 ease-out"
        style={{
          left: `calc(${(activeIndex * 100) / count}% + 0.25rem)`,
          width: `calc(${100 / count}% - 0.5rem)`,
        }}
      />
      {LAYER_DEFS.map((layer) => {
        const isActive = layer.key === value
        return (
          <button
            key={layer.key}
            type="button"
            onClick={() => onChange(layer.key)}
            className={cn(
              "relative z-10 flex-1 whitespace-nowrap rounded px-3 py-1 text-sm font-medium transition-colors",
              isActive
                ? "text-primary-foreground"
                : "text-muted-foreground hover:text-foreground",
            )}
          >
            {layer.label}
          </button>
        )
      })}
    </div>
  )
}
```

---

### STEP 5 — Component chính (toolbar + bảng)

Tạo file mới **`src/components/OcrTable/OcrVerificationTable.tsx`**:

```tsx
import { useState } from "react"
import { MediaViewer } from "@/components/Common/MediaViewer"
import { FieldCell } from "@/components/OcrTable/FieldCell"
import { LayerSwitch } from "@/components/OcrTable/LayerSwitch"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import {
  type DocumentRow,
  type FieldKey,
  type LayerKey,
  FIELD_DEFS,
  getFieldStatus,
  ocrDocuments,
} from "@/data/ocrVerificationData"

const LEGEND = [
  { dot: "bg-emerald-500", label: "Khớp" },
  { dot: "bg-red-500", label: "Lệch" },
  { dot: "bg-blue-500", label: "Đã sửa" },
  { dot: "bg-muted-foreground", label: "Thô" },
]

function countOk(doc: DocumentRow): number {
  return FIELD_DEFS.filter(
    (f) => getFieldStatus(doc.fields[f.key]) !== "mismatch",
  ).length
}

export function OcrVerificationTable() {
  const [rows, setRows] = useState<DocumentRow[]>(ocrDocuments)
  const [activeLayer, setActiveLayer] = useState<LayerKey>("final")

  const handleChangeFinal = (
    docId: string,
    fieldKey: FieldKey,
    value: string,
  ) => {
    setRows((prev) =>
      prev.map((doc) => {
        if (doc.id !== docId) {
          return doc
        }
        return {
          ...doc,
          fields: {
            ...doc.fields,
            [fieldKey]: {
              ...doc.fields[fieldKey],
              final: value,
              edited: value,
            },
          },
        }
      }),
    )
  }

  const totalFields = rows.length * FIELD_DEFS.length
  const okFields = rows.reduce((sum, doc) => sum + countOk(doc), 0)
  const progress =
    totalFields === 0 ? 0 : Math.round((okFields / totalFields) * 100)

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground">
          {LEGEND.map((item) => (
            <span key={item.label} className="flex items-center gap-2">
              <span className={`h-2 w-2 rounded-full ${item.dot}`} />
              {item.label}
            </span>
          ))}
        </div>
        <LayerSwitch value={activeLayer} onChange={setActiveLayer} />
      </div>

      <div className="space-y-1">
        <div className="flex items-center justify-between text-sm">
          <span className="text-muted-foreground">Tiến độ đối soát</span>
          <span className="font-medium">
            {okFields}/{totalFields} trường khớp ({progress}%)
          </span>
        </div>
        <div className="h-2 w-full overflow-hidden rounded-full bg-muted">
          <div
            className="h-full rounded-full bg-emerald-500 transition-all duration-500 ease-out"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow className="hover:bg-transparent">
              <TableHead>Tài liệu</TableHead>
              {FIELD_DEFS.map((f) => (
                <TableHead key={f.key}>{f.label}</TableHead>
              ))}
              <TableHead>Trạng thái</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {rows.map((doc) => (
              <TableRow
                key={doc.id}
                className="transition-colors hover:bg-muted/30"
              >
                <TableCell className="align-top">
                  <MediaViewer
                    src={doc.fileUrl}
                    alt={doc.fileName}
                    type={doc.fileType}
                    thumbnailClassName="h-12 w-12"
                  />
                  <span className="mt-1 block text-xs">{doc.fileName}</span>
                </TableCell>
                {FIELD_DEFS.map((f) => (
                  <TableCell key={f.key} className="min-w-[200px] align-top">
                    <FieldCell
                      fieldKey={f.key}
                      layers={doc.fields[f.key]}
                      activeLayer={activeLayer}
                      onChangeFinal={(v) => handleChangeFinal(doc.id, f.key, v)}
                    />
                  </TableCell>
                ))}
                <TableCell className="whitespace-nowrap align-top text-sm font-medium">
                  {countOk(doc)}/{FIELD_DEFS.length} ✓
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  )
}
```

---

### STEP 6 — Tạo route trang

Tạo file mới **`src/routes/_layout/ocr.tsx`**:

```tsx
import { createFileRoute } from "@tanstack/react-router"
import { OcrVerificationTable } from "@/components/OcrTable/OcrVerificationTable"

export const Route = createFileRoute("/_layout/ocr")({
  component: OcrPage,
  head: () => ({
    meta: [
      {
        title: "OCR Đối soát - Portal",
      },
    ],
  }),
})

function OcrPage() {
  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">
          Đối soát tài liệu OCR
        </h1>
        <p className="mt-2 text-muted-foreground">
          So sánh các lớp dữ liệu OCR (A/B/Tổng hợp/Sửa tay) và chốt giá trị cuối
          cùng.
        </p>
      </div>
      <OcrVerificationTable />
    </div>
  )
}
```

---

### STEP 7 — Chạy dev để TanStack Router tự sinh route, rồi thêm vào menu

1. Tại thư mục `frontend/` chạy `npm run dev`. Việc này tự cập nhật `src/routeTree.gen.ts`
   (KHÔNG sửa file `.gen.ts` bằng tay).
2. Mở **`src/routes/_layout.tsx`**, TÌM đoạn:

```tsx
const navigationItems: NavItem[] = [
  { to: "/demo", label: "Demo" },
  { to: "/table1", label: "Table 1" },
]
```

THAY bằng:

```tsx
const navigationItems: NavItem[] = [
  { to: "/demo", label: "Demo" },
  { to: "/table1", label: "Table 1" },
  { to: "/ocr", label: "OCR Đối soát" },
]
```

> Nếu TypeScript báo `to: "/ocr"` không hợp lệ → do `routeTree.gen.ts` chưa sinh.
> Hãy chắc chắn `npm run dev` đang chạy rồi thử lại.

---

### STEP 8 — Chạy & kiểm tra

Đăng nhập vào portal, vào menu **OCR Đối soát** (hoặc URL `/ocr`), kiểm tra:

- Mặc định ở lớp **Final**: mỗi ô là một ô nhập, sửa được ngay.
- Bấm lần lượt **OCR A / OCR B / Aggregated / Edited** trên thanh LayerSwitch → toàn bảng
  đổi sang giá trị lớp đó (read-only).
- Ô `Money` của `abc.png` có **chấm xanh dương** (đã sửa); ô `Currency` của `abc.png`
  có **chấm đỏ** (OCR A ≠ OCR B).
- Bấm icon **Layers** trong 1 ô → popover hiện đủ 5 lớp; bấm "Dùng OCR A" → Final đổi theo
  và ô **lóe nền vàng** ~0.6s (flash xác nhận).
- Mỗi lần bấm LayerSwitch → giá trị trong các ô **fade + trượt nhẹ lên** (~0.2s),
  và **viên pill trượt** sang nút lớp mới (~0.3s).
- Sửa 1 ô cho khớp/lệch → **chấm trạng thái nảy** một nhịp.
- Rê chuột vào hàng → nền hàng đổi nhẹ (**row hover**).
- Sửa 1 ô lệch cho khớp → **thanh progress** phía trên fill tăng mượt (~0.5s).
- Bấm thumbnail ở cột Tài liệu → `MediaViewer` mở ảnh/PDF full màn hình có zoom.
- Cột Trạng thái hiển thị `3/4 ✓` cho `abc.png` (1 ô currency bị lệch).

Cuối cùng chạy linter:

```bash
npm run lint
```

---

## 3. DANH SÁCH NGHIỆM THU (Definition of Done)

- [ ] Tạo `src/data/ocrVerificationData.ts`.
- [ ] Tạo `src/components/OcrTable/CellLayersPopover.tsx`.
- [ ] Tạo `src/components/OcrTable/FieldCell.tsx`.
- [ ] Tạo `src/components/OcrTable/LayerSwitch.tsx`.
- [ ] Tạo `src/components/OcrTable/OcrVerificationTable.tsx`.
- [ ] Tạo route `src/routes/_layout/ocr.tsx` + thêm menu trong `_layout.tsx`.
- [ ] Bảng: hàng = tài liệu, cột = trường; LayerSwitch đổi được 5 lớp.
- [ ] Lớp Final sửa inline được; popover hiện đủ 5 lớp + nút gán nhanh.
- [ ] Trạng thái màu đúng (match/mismatch/edited/raw) + cột tổng kết `n/4 ✓`.
- [ ] Animation đủ 6: (1) lật khi đổi lớp, (2) chấm nảy khi đổi trạng thái,
      (3) flash khi gán nhanh, (4) pill trượt trên LayerSwitch, (5) row hover,
      (6) progress bar fill mượt khi sửa cho khớp.
- [ ] Click thumbnail mở `MediaViewer`.
- [ ] `npm run lint` không báo lỗi mới.

---

## 4. NHỮNG LỖI THƯỜNG GẶP — TUYỆT ĐỐI TRÁNH

1. ❌ Thêm dấu `;` cuối dòng hoặc dùng nháy đơn → sai chuẩn Biome.
2. ❌ Sửa file trong `src/components/ui/` hoặc sửa tay `routeTree.gen.ts` → KHÔNG đụng.
3. ❌ Bọc `FieldCell` (có `<input>`/`<button>`) bên trong một `<button>` → HTML không hợp lệ.
4. ❌ Tự vẽ overlay bounding box ở frontend → KHÔNG cần, backend đã vẽ sẵn vào ảnh.
5. ❌ Cài thêm thư viện (TanStack Table, chart…) → task này KHÔNG cần.
6. ❌ Quên chạy `npm run dev` trước khi thêm `{ to: "/ocr" }` → TS báo lỗi route.
7. ❌ Hardcode màu hex → dùng class Tailwind (`bg-emerald-500`, `text-primary`…).
8. ❌ Bỏ `flex-1` ở nút LayerSwitch hoặc bỏ `relative` ở container → pill trượt sai vị trí.
9. ❌ Đặt `key={activeLayer}` lên ô `<Input>` (thay vì div bọc value) → gõ phím bị mất focus.
   `key={activeLayer}` chỉ để ở div bọc value; `key={status}` chỉ để ở chấm màu.

---

## 5. SƠ ĐỒ & GỢI Ý NỐI API SAU NÀY

Wireframe:

```
Chú thích: 🟢 Khớp   🔴 Lệch   🔵 Đã sửa   ⚪ Thô     (Final)(Edited)(OCR A)(OCR B)(Aggregated)
┌──────────┬─────────────┬──────────────┬────────────┬────────────┬──────────┐
│ Tài liệu │ Name        │ Money        │ Date       │ Currency   │ Trạng thái│
├──────────┼─────────────┼──────────────┼────────────┼────────────┼──────────┤
│ 🖼 abc.png│ 🟢 ACME...  │ 🔵[1,250,000]│ 🟢20/06... │ 🔴 [     ] │ 3/4 ✓     │
│ 🖼 def.pdf│ 🟢 Beta LLC │ 🟢 980,000   │ 🟢18/06... │ 🟢 USD     │ 4/4 ✓     │
└──────────┴─────────────┴──────────────┴────────────┴────────────┴──────────┘
   click icon Layers trong ô → popover 5 lớp + nút "Dùng OCR A/B/Aggregated"
```

Nối dữ liệu thật (TÙY CHỌN):

Backend đã có pipeline OCR (`backend/app/api/routes/document.py` →
`process_document_submission`) trả về `document_results` + `comparison_result`,
và ảnh đã vẽ bounding box (`compare_document_contents` → `result_images`).
Khi nối thật:

1. Thay `ocrDocuments` (mock) bằng dữ liệu gọi API, **map đúng kiểu `DocumentRow`**:
   - `fields[x].ocrA` / `ocrB`: lấy từ kết quả OCR từng hệ thống.
   - `fields[x].aggregated`: lấy từ `comparison_result`.
   - `fields[x].edited` / `final`: ban đầu = giá trị mặc định; user sửa sẽ ghi đè.
   - `fileUrl`: trỏ tới ảnh đã có bounding box trong MinIO output bucket (đã vẽ sẵn).
2. Khi user sửa `final`, gọi API lưu lại (PATCH) thay vì chỉ `setRows` trong state.
3. Giữ nguyên toàn bộ component UI ở trên — chỉ đổi nguồn dữ liệu.

> Đây là phần mở rộng, **KHÔNG bắt buộc** cho task UI này.
```
