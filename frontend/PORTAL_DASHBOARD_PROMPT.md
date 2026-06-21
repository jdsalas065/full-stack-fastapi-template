# PROMPT: Cho chatbot trả lời bằng BIỂU ĐỒ trong chat room

> File này là **prompt hoàn chỉnh** để đưa cho một AI coding agent (kể cả model yếu).
> Agent chỉ cần **làm tuần tự từng STEP**, **copy-paste đúng code**, **không sáng tạo thêm**.
> Mọi đường dẫn file đều tính từ thư mục `frontend/`.

---

## 0. BỐI CẢNH DỰ ÁN (đọc kỹ, KHÔNG được làm sai)

Đây là frontend của một template FastAPI full-stack. Tech stack **CỐ ĐỊNH**:

| Hạng mục | Công nghệ | Ghi chú bắt buộc |
|---|---|---|
| Framework | React 19 + TypeScript | |
| Build tool | Vite 7 | |
| UI components | shadcn/ui (Radix) trong `src/components/ui/` | **KHÔNG sửa** file trong thư mục này |
| CSS | Tailwind CSS v4 | dùng class utility, KHÔNG viết CSS file mới |
| Icons | `lucide-react` | |
| Thông báo | `sonner` (`toast`) | đã có sẵn |
| Linter/Formatter | **Biome** | xem mục QUY TẮC CODE bên dưới |

### QUY TẮC CODE (Biome) — TUYỆT ĐỐI tuân theo:
- **KHÔNG dùng dấu chấm phẩy `;`** ở cuối dòng (semicolons: asNeeded).
- **Dùng nháy kép `"`**, không dùng nháy đơn.
- **Thụt lề 2 spaces**.
- Import nội bộ dùng alias **`@/`** = `src/` (ví dụ `@/components/ui/card`).
- Dùng **self-closing tag** khi element rỗng.
- **KHÔNG có `else` thừa** sau `return`, **KHÔNG dùng ternary lồng nhau**.

---

## 1. MỤC TIÊU

Hiện tại đã có component chat tại **`src/components/Chat/ChatInterface.tsx`** (một "chat room"
với danh sách tin nhắn + ô nhập + nút gửi). Tin nhắn của bot đang chỉ là **text**.

**Yêu cầu:** Khi người dùng hỏi về số liệu/thống kê (ví dụ gõ "biểu đồ", "thống kê phòng ban"…),
bot sẽ trả lời bằng **một biểu đồ** hiển thị **ngay trong khung hội thoại như một message bubble**
(thay vì text). Dùng **dữ liệu mẫu hardcode** (chưa nối API).

Hỗ trợ 3 loại biểu đồ: **cột (bar)**, **vùng (area)**, **tròn (pie)** — dùng thư viện **Recharts**.
Theme đã có sẵn 5 biến màu: `var(--chart-1)` … `var(--chart-5)`.

> KHÔNG tạo route/trang mới. KHÔNG đụng vào portal quản lý. CHỈ làm trong phạm vi chatbot.

---

## 2. CÁC BƯỚC THỰC HIỆN (làm đúng thứ tự)

### STEP 1 — Cài thư viện biểu đồ

Mở terminal tại thư mục `frontend/` và chạy:

```bash
npm install recharts
```

> Nếu báo lỗi peer dependency với React 19, chạy lại bằng:
> ```bash
> npm install recharts --legacy-peer-deps
> ```

---

### STEP 2 — Tạo file dữ liệu + logic chọn biểu đồ

Tạo file mới: **`src/data/chatChartData.ts`** với nội dung **chính xác** sau:

```ts
export type ChatChartType = "bar" | "area" | "pie"

export interface ChatChartPayload {
  type: ChatChartType
  title: string
  data: { name: string; value: number }[]
}

const departmentChart: ChatChartPayload = {
  type: "bar",
  title: "Người dùng theo phòng ban",
  data: [
    { name: "Engineering", value: 86 },
    { name: "Product", value: 42 },
    { name: "Design", value: 28 },
    { name: "Marketing", value: 35 },
    { name: "Sales", value: 51 },
    { name: "HR", value: 18 },
  ],
}

const trendChart: ChatChartPayload = {
  type: "area",
  title: "Người dùng hoạt động theo tháng",
  data: [
    { name: "T1", value: 1200 },
    { name: "T2", value: 1350 },
    { name: "T3", value: 1280 },
    { name: "T4", value: 1500 },
    { name: "T5", value: 1680 },
    { name: "T6", value: 1832 },
  ],
}

const statusChart: ChatChartPayload = {
  type: "pie",
  title: "Phân bố trạng thái người dùng",
  data: [
    { name: "Active", value: 1832 },
    { name: "Inactive", value: 412 },
    { name: "Pending", value: 176 },
  ],
}

const CHART_KEYWORDS = [
  "biểu đồ",
  "bieu do",
  "chart",
  "thống kê",
  "thong ke",
  "dashboard",
  "báo cáo",
  "bao cao",
]

export function isChartRequest(message: string): boolean {
  const text = message.toLowerCase()
  return CHART_KEYWORDS.some((keyword) => text.includes(keyword))
}

export function getMockChartReply(message: string): ChatChartPayload {
  const text = message.toLowerCase()
  if (
    text.includes("tròn") ||
    text.includes("pie") ||
    text.includes("trạng thái")
  ) {
    return statusChart
  }
  if (
    text.includes("vùng") ||
    text.includes("area") ||
    text.includes("xu hướng") ||
    text.includes("tháng")
  ) {
    return trendChart
  }
  return departmentChart
}
```

---

### STEP 3 — Tạo component vẽ biểu đồ trong message bubble

Tạo file mới: **`src/components/Chat/ChatChart.tsx`** với nội dung **chính xác** sau:

```tsx
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"
import type { ChatChartPayload } from "@/data/chatChartData"

const PIE_COLORS = [
  "var(--chart-1)",
  "var(--chart-2)",
  "var(--chart-3)",
  "var(--chart-4)",
  "var(--chart-5)",
]

const tooltipStyle = {
  background: "var(--card)",
  border: "1px solid var(--border)",
  borderRadius: "8px",
}

export function ChatChart({ chart }: { chart: ChatChartPayload }) {
  function renderChart() {
    if (chart.type === "bar") {
      return (
        <BarChart data={chart.data}>
          <CartesianGrid strokeDasharray="3 3" vertical={false} />
          <XAxis dataKey="name" tickLine={false} axisLine={false} />
          <YAxis tickLine={false} axisLine={false} />
          <Tooltip contentStyle={tooltipStyle} />
          <Bar dataKey="value" fill="var(--chart-1)" radius={[6, 6, 0, 0]} />
        </BarChart>
      )
    }

    if (chart.type === "area") {
      return (
        <AreaChart data={chart.data}>
          <CartesianGrid strokeDasharray="3 3" vertical={false} />
          <XAxis dataKey="name" tickLine={false} axisLine={false} />
          <YAxis tickLine={false} axisLine={false} />
          <Tooltip contentStyle={tooltipStyle} />
          <Area
            type="monotone"
            dataKey="value"
            stroke="var(--chart-1)"
            strokeWidth={2}
            fill="var(--chart-1)"
            fillOpacity={0.2}
          />
        </AreaChart>
      )
    }

    return (
      <PieChart>
        <Pie
          data={chart.data}
          dataKey="value"
          nameKey="name"
          cx="50%"
          cy="50%"
          outerRadius={80}
          label
        >
          {chart.data.map((entry, index) => (
            <Cell
              key={entry.name}
              fill={PIE_COLORS[index % PIE_COLORS.length]}
            />
          ))}
        </Pie>
        <Tooltip contentStyle={tooltipStyle} />
      </PieChart>
    )
  }

  return (
    <div className="w-full">
      <p className="mb-2 text-sm font-medium">{chart.title}</p>
      <ResponsiveContainer width="100%" height={240}>
        {renderChart()}
      </ResponsiveContainer>
    </div>
  )
}
```

---

### STEP 4 — Sửa `ChatInterface.tsx` (chỉnh tại chỗ, làm đủ 4 phần 4a→4d)

Mở file **`src/components/Chat/ChatInterface.tsx`**.

#### 4a. Thêm 2 import (đặt chung với các import sẵn có ở đầu file)

Thêm 2 khối import sau vào nhóm import đầu file:

```tsx
import { ChatChart } from "@/components/Chat/ChatChart"
import {
  getMockChartReply,
  isChartRequest,
  type ChatChartPayload,
} from "@/data/chatChartData"
```

#### 4b. Thêm trường `chart` vào interface `Message`

TÌM đoạn:

```tsx
interface Message {
  role: "user" | "assistant"
  content: string
  status?: string
}
```

THAY bằng:

```tsx
interface Message {
  role: "user" | "assistant"
  content: string
  status?: string
  chart?: ChatChartPayload
}
```

#### 4c. Khi là yêu cầu biểu đồ → trả về biểu đồ mẫu, KHÔNG gọi API

TÌM đoạn (đầu hàm `handleSendMessage`):

```tsx
    const userMessage = input.trim()
    setInput("")
    setMessages((prev) => [...prev, { role: "user", content: userMessage }])
    setLoading(true)
```

THAY bằng:

```tsx
    const userMessage = input.trim()
    setInput("")
    setMessages((prev) => [...prev, { role: "user", content: userMessage }])

    if (isChartRequest(userMessage)) {
      const chart = getMockChartReply(userMessage)
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: chart.title,
          status: "completed",
          chart,
        },
      ])
      return
    }

    setLoading(true)
```

#### 4d. Render biểu đồ trong message bubble (nếu tin nhắn có `chart`)

TÌM đoạn render `Card` của mỗi tin nhắn:

```tsx
              <Card
                className={`max-w-md px-4 py-2 ${
                  msg.role === "user"
                    ? "bg-blue-500 text-white"
                    : "bg-muted text-foreground"
                }`}
              >
                <p className="break-words">{msg.content}</p>
                {msg.status === "streaming" && (
                  <p className="text-xs mt-1">streaming...</p>
                )}
                {msg.status === "error" && (
                  <p className="text-xs mt-1 text-red-400">error</p>
                )}
              </Card>
```

THAY bằng:

```tsx
              <Card
                className={`${
                  msg.chart ? "max-w-xl w-full" : "max-w-md"
                } px-4 py-2 ${
                  msg.role === "user"
                    ? "bg-blue-500 text-white"
                    : "bg-muted text-foreground"
                }`}
              >
                {msg.chart ? (
                  <ChatChart chart={msg.chart} />
                ) : (
                  <p className="break-words">{msg.content}</p>
                )}
                {msg.status === "streaming" && (
                  <p className="text-xs mt-1">streaming...</p>
                )}
                {msg.status === "error" && (
                  <p className="text-xs mt-1 text-red-400">error</p>
                )}
              </Card>
```

---

### STEP 5 — Chạy & kiểm tra

Tại thư mục `frontend/`:

```bash
npm run dev
```

Mở chat room, thử gõ lần lượt các câu sau và xem bot trả lời bằng biểu đồ:

- `thống kê phòng ban` → ra **biểu đồ cột**
- `biểu đồ xu hướng theo tháng` → ra **biểu đồ vùng**
- `biểu đồ trạng thái người dùng` → ra **biểu đồ tròn**
- Gõ câu bình thường khác (không chứa từ khóa) → bot trả lời text như cũ (gọi API).

Cuối cùng chạy linter:

```bash
npm run lint
```

---

## 3. DANH SÁCH NGHIỆM THU (Definition of Done)

- [ ] Đã cài `recharts` (có trong `package.json` → dependencies).
- [ ] Đã tạo `src/data/chatChartData.ts`.
- [ ] Đã tạo `src/components/Chat/ChatChart.tsx`.
- [ ] Đã sửa `ChatInterface.tsx` đủ 4 phần (4a, 4b, 4c, 4d).
- [ ] Gõ câu chứa từ khóa ("biểu đồ"/"thống kê"…) → bot trả lời **biểu đồ** trong bubble.
- [ ] Gõ câu thường → bot vẫn trả lời **text** qua API như cũ.
- [ ] 3 loại biểu đồ (cột / vùng / tròn) đều hiển thị đúng, co giãn theo bề rộng.
- [ ] `npm run lint` không báo lỗi mới.

---

## 4. NHỮNG LỖI THƯỜNG GẶP — TUYỆT ĐỐI TRÁNH

1. ❌ Tạo route/trang mới hoặc sửa portal quản lý → SAI, chỉ làm trong component chat.
2. ❌ Thêm dấu `;` cuối dòng hoặc dùng nháy đơn → sai chuẩn Biome.
3. ❌ Dùng **ternary lồng nhau** trong `ChatChart` → đã tách bằng hàm `renderChart()`, giữ nguyên.
4. ❌ Đặt biểu đồ Recharts mà không bọc trong `<ResponsiveContainer>` có `height` cụ thể → không hiển thị.
5. ❌ Dùng màu hardcode hex → hãy dùng `var(--chart-1)` … `var(--chart-5)` để khớp theme sáng/tối.
6. ❌ Cài thêm thư viện chart khác (chart.js, nivo…) → CHỈ dùng `recharts`.
7. ❌ Sửa file trong `src/components/ui/` → KHÔNG đụng vào.
8. ❌ Quên `return` sau khi push tin nhắn biểu đồ ở STEP 4c → sẽ gọi luôn cả API gây lỗi.

---

## 5. (TÙY CHỌN) Nối dữ liệu thật sau này

- Hiện dữ liệu biểu đồ **hardcode** trong `src/data/chatChartData.ts`.
- Khi back-end có thể trả về dữ liệu biểu đồ, cho server gửi kèm một payload dạng
  `ChatChartPayload` trong sự kiện stream (xem `src/services/chatService.ts`), rồi gán vào
  `chart` của tin nhắn assistant thay cho `getMockChartReply`. Giữ nguyên `ChatChart` để
  không phải sửa phần render.
- Đây là phần mở rộng, **KHÔNG bắt buộc** cho task này.
```
