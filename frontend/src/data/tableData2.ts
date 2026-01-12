export interface TableItem2 {
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

export const tableData2: TableItem2[] = [
  {
    id: "5",
    name: "Robert Brown",
    email: "robert.brown@example.com",
    status: "pending",
    role: "Data Analyst",
    department: "Analytics",
    joinDate: "2024-01-10",
    lastActive: "2026-01-11T18:00:00Z",
    phone: "+1 (555) 567-8901",
    location: "Austin, USA",
    avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Robert",
  },
  {
    id: "6",
    name: "Sarah Wilson",
    email: "sarah.wilson@example.com",
    status: "active",
    role: "Marketing Manager",
    department: "Marketing",
    joinDate: "2023-06-15",
    lastActive: "2026-01-12T04:45:00Z",
    phone: "+1 (555) 678-9012",
    location: "Boston, USA",
    avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Sarah",
  },
  {
    id: "7",
    name: "David Martinez",
    email: "david.m@example.com",
    status: "active",
    role: "Backend Developer",
    department: "Engineering",
    joinDate: "2023-02-28",
    lastActive: "2026-01-12T02:30:00Z",
    phone: "+1 (555) 789-0123",
    location: "Chicago, USA",
    avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=David",
  },
  {
    id: "8",
    name: "Lisa Anderson",
    email: "lisa.anderson@example.com",
    status: "active",
    role: "HR Specialist",
    department: "Human Resources",
    joinDate: "2022-10-12",
    lastActive: "2026-01-12T01:20:00Z",
    phone: "+1 (555) 890-1234",
    location: "Miami, USA",
    avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Lisa",
  },
]
