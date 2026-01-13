export interface TableItem3 {
  id: string
  name: string
  email: string
  status: "active" | "inactive" | "pending"
  role: string
  department: string
  joinDate: string
  lastActive: string
  phone: string
  location: string
  avatar?: string
}

export const tableData3: TableItem3[] = [
  {
    id: "9",
    name: "James Taylor",
    email: "james.taylor@example.com",
    status: "inactive",
    role: "QA Engineer",
    department: "Engineering",
    joinDate: "2023-04-20",
    lastActive: "2026-01-09T16:00:00Z",
    phone: "+1 (555) 901-2345",
    location: "Denver, USA",
    avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=James",
  },
  {
    id: "10",
    name: "Patricia Garcia",
    email: "patricia.g@example.com",
    status: "active",
    role: "Sales Director",
    department: "Sales",
    joinDate: "2022-05-08",
    lastActive: "2026-01-12T05:00:00Z",
    phone: "+1 (555) 012-3456",
    location: "Dallas, USA",
    avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Patricia",
  },
  {
    id: "11",
    name: "Christopher Lee",
    email: "chris.lee@example.com",
    status: "active",
    role: "Frontend Developer",
    department: "Engineering",
    joinDate: "2023-07-01",
    lastActive: "2026-01-12T06:15:00Z",
    phone: "+1 (555) 123-9876",
    location: "Portland, USA",
    avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Christopher",
  },
  {
    id: "12",
    name: "Jennifer White",
    email: "jennifer.w@example.com",
    status: "pending",
    role: "Content Writer",
    department: "Marketing",
    joinDate: "2024-01-18",
    lastActive: "2026-01-11T20:30:00Z",
    phone: "+1 (555) 234-8765",
    location: "Phoenix, USA",
    avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Jennifer",
  },
]
