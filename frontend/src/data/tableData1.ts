export interface TableItem1 {
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

export const tableData1: TableItem1[] = [
  {
    id: "1",
    name: "John Doe",
    email: "john.doe@example.com",
    status: "active",
    role: "Software Engineer",
    department: "Engineering",
    joinDate: "2023-01-15",
    lastActive: "2026-01-12T06:00:00Z",
    phone: "+1 (555) 123-4567",
    location: "New York, USA",
    avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=John",
  },
  {
    id: "2",
    name: "Jane Smith",
    email: "jane.smith@example.com",
    status: "active",
    role: "Product Manager",
    department: "Product",
    joinDate: "2022-11-20",
    lastActive: "2026-01-12T05:30:00Z",
    phone: "+1 (555) 234-5678",
    location: "San Francisco, USA",
    avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Jane",
  },
  {
    id: "3",
    name: "Michael Johnson",
    email: "michael.j@example.com",
    status: "inactive",
    role: "UX Designer",
    department: "Design",
    joinDate: "2023-03-10",
    lastActive: "2026-01-10T14:20:00Z",
    phone: "+1 (555) 345-6789",
    location: "Los Angeles, USA",
    avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Michael",
  },
  {
    id: "4",
    name: "Emily Davis",
    email: "emily.davis@example.com",
    status: "active",
    role: "DevOps Engineer",
    department: "Engineering",
    joinDate: "2022-08-05",
    lastActive: "2026-01-12T03:15:00Z",
    phone: "+1 (555) 456-7890",
    location: "Seattle, USA",
    avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Emily",
  },
]
