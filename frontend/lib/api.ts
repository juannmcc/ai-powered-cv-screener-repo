import { ChatResponse } from "@/types/chat"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

export async function askQuestion(question: string): Promise<ChatResponse> {
  const res = await fetch(`${API_URL}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  })

  if (!res.ok) {
    const error = await res.json().catch(() => ({}))
    throw new Error(error.detail || `API error: ${res.status}`)
  }

  return res.json()
}
