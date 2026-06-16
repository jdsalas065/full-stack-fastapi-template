import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card } from "@/components/ui/card"
import { streamChat, type ChatRequest, type ChatStreamEvent } from "@/services/chatService"
import { toast } from "sonner"

interface Message {
  role: "user" | "assistant"
  content: string
  status?: string
}

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const [conversationId, setConversationId] = useState<string | undefined>()

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || loading) return

    const userMessage = input.trim()
    setInput("")
    setMessages((prev) => [...prev, { role: "user", content: userMessage }])
    setLoading(true)

    try {
      const payload: ChatRequest = {
        message: userMessage,
        conversation_id: conversationId,
        temperature: 0.2,
      }

      let assistantContent = ""
      let newConversationId = conversationId

      for await (const event of streamChat(payload)) {
        if (event.event === "start") {
          setMessages((prev) => [
            ...prev,
            { role: "assistant", content: "", status: "streaming" },
          ])
          if (event.conversation_id) {
            newConversationId = event.conversation_id
            setConversationId(event.conversation_id)
          }
        } else if (event.event === "token") {
          assistantContent += event.delta || ""
          setMessages((prev) => {
            const updated = [...prev]
            const lastMsg = updated[updated.length - 1]
            if (lastMsg && lastMsg.role === "assistant") {
              lastMsg.content = assistantContent
            }
            return updated
          })
        } else if (event.event === "done") {
          assistantContent = event.content || assistantContent
          setMessages((prev) => {
            const updated = [...prev]
            const lastMsg = updated[updated.length - 1]
            if (lastMsg && lastMsg.role === "assistant") {
              lastMsg.content = assistantContent
              lastMsg.status = "completed"
            }
            return updated
          })
        } else if (event.event === "error") {
          toast.error(`Chat error: ${event.error}`)
          setMessages((prev) => {
            const updated = [...prev]
            const lastMsg = updated[updated.length - 1]
            if (lastMsg && lastMsg.role === "assistant") {
              lastMsg.status = "error"
            }
            return updated
          })
        }
      }
    } catch (error) {
      toast.error(
        error instanceof Error ? error.message : "Failed to send message",
      )
      setMessages((prev) =>
        prev.filter((msg) => !(msg.role === "assistant" && !msg.content)),
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-screen bg-background">
      {/* Header */}
      <div className="border-b px-4 py-3 bg-card">
        <h1 className="text-2xl font-bold">Chat Assistant</h1>
        {conversationId && (
          <p className="text-sm text-muted-foreground">
            Conversation: {conversationId.slice(0, 8)}...
          </p>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full text-muted-foreground">
            <p>Start a conversation...</p>
          </div>
        ) : (
          messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex gap-3 ${
                msg.role === "user" ? "justify-end" : "justify-start"
              }`}
            >
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
            </div>
          ))
        )}
      </div>

      {/* Input */}
      <form onSubmit={handleSendMessage} className="border-t p-4 bg-card">
        <div className="flex gap-2">
          <Input
            type="text"
            placeholder="Type your message..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={loading}
            className="flex-1"
          />
          <Button type="submit" disabled={loading || !input.trim()}>
            {loading ? "Sending..." : "Send"}
          </Button>
        </div>
      </form>
    </div>
  )
}
