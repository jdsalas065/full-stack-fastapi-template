import { apiClient } from "../api-client"
import type {
  ItemCreate,
  ItemPublic,
  ItemsPublic,
  ItemUpdate,
  Message,
} from "../types"

export class ItemsService {
  /**
   * Read Items
   * Retrieve items.
   */
  public static async readItems(
    data: { skip?: number; limit?: number } = {},
  ): Promise<ItemsPublic> {
    const response = await apiClient.get<ItemsPublic>("/api/v1/items/", {
      params: {
        skip: data.skip,
        limit: data.limit,
      },
    })
    return response.data
  }

  /**
   * Create Item
   * Create new item.
   */
  public static async createItem(data: {
    requestBody: ItemCreate
  }): Promise<ItemPublic> {
    const response = await apiClient.post<ItemPublic>(
      "/api/v1/items/",
      data.requestBody,
    )
    return response.data
  }

  /**
   * Read Item
   * Get item by ID.
   */
  public static async readItem(data: { id: string }): Promise<ItemPublic> {
    const response = await apiClient.get<ItemPublic>(
      `/api/v1/items/${encodeURIComponent(data.id)}`,
    )
    return response.data
  }

  /**
   * Update Item
   * Update an item.
   */
  public static async updateItem(data: {
    id: string
    requestBody: ItemUpdate
  }): Promise<ItemPublic> {
    const response = await apiClient.put<ItemPublic>(
      `/api/v1/items/${encodeURIComponent(data.id)}`,
      data.requestBody,
    )
    return response.data
  }

  /**
   * Delete Item
   * Delete an item.
   */
  public static async deleteItem(data: { id: string }): Promise<Message> {
    const response = await apiClient.delete<Message>(
      `/api/v1/items/${encodeURIComponent(data.id)}`,
    )
    return response.data
  }
}
