/**
 * Chat API service with SSE streaming support
 */

import { apiClient } from "./api"

export interface ChatRequest {
  conversation_id?: string
  message: string
  model?: string
  temperature?: number
  max_tokens?: number
}

export interface ChatStreamEvent {
  event: "start" | "token" | "heartbeat" | "done" | "error"
  conversation_id?: string
  message_id?: string
  delta?: string
  content?: string
  error?: string
  created_at?: string
}

/**
 * Stream chat completion as SSE events
 */
export async function* streamChat(payload: ChatRequest) {
  const token = localStorage.getItem("access_token")
  if (!token) {
    throw new Error("Not authenticated")
  }

  const response = await fetch(
    `${import.meta.env.VITE_API_URL || "http://localhost:8000"}/api/v1/chat`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(payload),
    },
  )

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.error?.message || "Chat request failed")
  }

  if (!response.body) {
    throw new Error("No response body")
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ""

  try {
    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })

      // Parse complete SSE events (format: event: start\ndata: {...}\n\n)
      const parts = buffer.split("\n\n")
      buffer = parts.pop() || ""

      for (const part of parts) {
        if (!part.trim()) continue

        const lines = part.split("\n")
        let eventType: string | null = null
        let data: string | null = null

        for (const line of lines) {
          if (line.startsWith("event:")) {
            eventType = line.slice(6).trim()
          } else if (line.startsWith("data:")) {
            data = line.slice(5).trim()
          }
        }

        if (eventType && data) {
          try {
            const parsed = JSON.parse(data) as ChatStreamEvent
            parsed.event = eventType as ChatStreamEvent["event"]
            yield parsed
          } catch {
            // Skip invalid JSON
          }
        }
      }
    }
  } finally {
    reader.releaseLock()
  }
}
