import { apiClient } from "../api-client"
import type {
  Message,
  UpdatePassword,
  UserCreate,
  UserPublic,
  UserRegister,
  UsersPublic,
  UserUpdate,
  UserUpdateMe,
} from "../types"

export class UsersService {
  /**
   * Read Users
   * Retrieve users.
   */
  public static async readUsers(
    data: { skip?: number; limit?: number } = {},
  ): Promise<UsersPublic> {
    const response = await apiClient.get<UsersPublic>("/api/v1/users/", {
      params: {
        skip: data.skip,
        limit: data.limit,
      },
    })
    return response.data
  }

  /**
   * Create User
   * Create new user.
   */
  public static async createUser(data: {
    requestBody: UserCreate
  }): Promise<UserPublic> {
    const response = await apiClient.post<UserPublic>(
      "/api/v1/users/",
      data.requestBody,
    )
    return response.data
  }

  /**
   * Read User Me
   * Get current user.
   */
  public static async readUserMe(): Promise<UserPublic> {
    const response = await apiClient.get<UserPublic>("/api/v1/users/me")
    return response.data
  }

  /**
   * Delete User Me
   * Delete own user.
   */
  public static async deleteUserMe(): Promise<Message> {
    const response = await apiClient.delete<Message>("/api/v1/users/me")
    return response.data
  }

  /**
   * Update User Me
   * Update own user.
   */
  public static async updateUserMe(data: {
    requestBody: UserUpdateMe
  }): Promise<UserPublic> {
    const response = await apiClient.patch<UserPublic>(
      "/api/v1/users/me",
      data.requestBody,
    )
    return response.data
  }

  /**
   * Update Password Me
   * Update own password.
   */
  public static async updatePasswordMe(data: {
    requestBody: UpdatePassword
  }): Promise<Message> {
    const response = await apiClient.patch<Message>(
      "/api/v1/users/me/password",
      data.requestBody,
    )
    return response.data
  }

  /**
   * Register User
   * Create new user without the need to be logged in.
   */
  public static async registerUser(data: {
    requestBody: UserRegister
  }): Promise<UserPublic> {
    const response = await apiClient.post<UserPublic>(
      "/api/v1/users/signup",
      data.requestBody,
    )
    return response.data
  }

  /**
   * Read User By Id
   * Get a specific user by id.
   */
  public static async readUserById(data: {
    userId: string
  }): Promise<UserPublic> {
    const response = await apiClient.get<UserPublic>(
      `/api/v1/users/${encodeURIComponent(data.userId)}`,
    )
    return response.data
  }

  /**
   * Update User
   * Update a user.
   */
  public static async updateUser(data: {
    userId: string
    requestBody: UserUpdate
  }): Promise<UserPublic> {
    const response = await apiClient.patch<UserPublic>(
      `/api/v1/users/${encodeURIComponent(data.userId)}`,
      data.requestBody,
    )
    return response.data
  }

  /**
   * Delete User
   * Delete a user.
   */
  public static async deleteUser(data: { userId: string }): Promise<Message> {
    const response = await apiClient.delete<Message>(
      `/api/v1/users/${encodeURIComponent(data.userId)}`,
    )
    return response.data
  }
}
