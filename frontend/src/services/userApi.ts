import type { UserCreate, UserPublic, UserUpdate } from "@/client"
import { UsersService } from "@/client"

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

function userToTeamMember(user: UserPublic): TeamMember {
  return {
    id: user.id,
    name: user.full_name || user.email.split("@")[0],
    email: user.email,
    role: user.is_superuser ? "Admin" : "User",
    department: "Engineering",
    status: user.is_active ? "active" : "inactive",
    location: "N/A",
    phone: "N/A",
    avatar: `https://api.dicebear.com/7.x/avataaars/svg?seed=${user.email}`,
    joinDate: new Date().toISOString(),
    lastActive: new Date().toISOString(),
  }
}

function teamMemberToUserCreate(member: Omit<TeamMember, "id">): UserCreate {
  return {
    email: member.email,
    password: "ChangeMe123!",
    full_name: member.name,
    is_active: member.status === "active",
    is_superuser: false,
  }
}

function teamMemberToUserUpdate(member: Partial<TeamMember>): UserUpdate {
  const update: UserUpdate = {}

  if (member.name !== undefined) {
    update.full_name = member.name
  }
  if (member.email !== undefined) {
    update.email = member.email
  }
  if (member.status !== undefined) {
    update.is_active = member.status === "active"
  }

  return update
}

export const apiService = {
  async getAll(): Promise<TeamMember[]> {
    const response = await UsersService.readUsers({ skip: 0, limit: 100 })
    return response.data.map(userToTeamMember)
  },

  async getById(id: string): Promise<TeamMember | null> {
    try {
      const user = await UsersService.readUserById({ userId: id })
      return userToTeamMember(user)
    } catch (error) {
      console.error("Failed to fetch user:", error)
      return null
    }
  },

  async create(member: Omit<TeamMember, "id">): Promise<TeamMember> {
    const userCreate = teamMemberToUserCreate(member)
    const user = await UsersService.createUser({ requestBody: userCreate })
    return userToTeamMember(user)
  },

  async update(id: string, updates: Partial<TeamMember>): Promise<TeamMember> {
    const userUpdate = teamMemberToUserUpdate(updates)
    const user = await UsersService.updateUser({
      userId: id,
      requestBody: userUpdate,
    })
    return userToTeamMember(user)
  },

  async delete(id: string): Promise<void> {
    await UsersService.deleteUser({ userId: id })
  },
}
