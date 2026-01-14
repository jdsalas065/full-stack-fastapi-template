export interface TeamMember {
  id: string
  name: string
  email: string
  role: string
  department: string
  status: "active" | "inactive" | "pending"
  location: string
  phone: string
  avatar?: string
  joinDate: string
  lastActive: string
}

const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))

export const fakeApiService = {
  async getAll(): Promise<TeamMember[]> {
    await delay(500)
    const data = localStorage.getItem("table1Data")
    return data ? JSON.parse(data) : []
  },

  async getById(id: string): Promise<TeamMember | null> {
    await delay(300)
    const data = localStorage.getItem("table1Data")
    const members = data ? JSON.parse(data) : []
    return members.find((m: TeamMember) => m.id === id) || null
  },

  async create(member: Omit<TeamMember, "id">): Promise<TeamMember> {
    await delay(500)
    const newMember = {
      ...member,
      id: `member-${Date.now()}-${Math.random().toString(36).slice(2, 11)}`,
    }
    const data = localStorage.getItem("table1Data")
    const members = data ? JSON.parse(data) : []
    members.push(newMember)
    localStorage.setItem("table1Data", JSON.stringify(members))
    return newMember
  },

  async update(id: string, updates: Partial<TeamMember>): Promise<TeamMember> {
    await delay(500)
    const data = localStorage.getItem("table1Data")
    const members = data ? JSON.parse(data) : []
    const index = members.findIndex((m: TeamMember) => m.id === id)
    if (index === -1) {
      throw new Error("Member not found")
    }
    members[index] = { ...members[index], ...updates }
    localStorage.setItem("table1Data", JSON.stringify(members))
    return members[index]
  },

  async delete(id: string): Promise<void> {
    await delay(500)
    const data = localStorage.getItem("table1Data")
    const members = data ? JSON.parse(data) : []
    const filtered = members.filter((m: TeamMember) => m.id !== id)
    localStorage.setItem("table1Data", JSON.stringify(filtered))
  },

  initializeData(initialData: TeamMember[]): void {
    const existing = localStorage.getItem("table1Data")
    if (!existing) {
      localStorage.setItem("table1Data", JSON.stringify(initialData))
    }
  },
}
