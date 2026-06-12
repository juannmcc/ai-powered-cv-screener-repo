import { ChatResponse } from "@/types/chat"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

export interface Stats {
  chunks: number
  estimated_cvs: number
  provider: string
  model: string
}

export interface Candidate {
  name: string
  source: string
  avatar: string
}

export interface HealthStatus {
  ok: boolean
  ingested: boolean
  chunks: number
}

export class APIError extends Error {
  constructor(
    public code: string,
    message: string,
    public status: number,
  ) {
    super(message)
    this.name = "APIError"
  }
}

export async function askQuestion(question: string): Promise<ChatResponse> {
  const res = await fetch(`${API_URL}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  })

  if (!res.ok) {
    const error = await res.json().catch(() => ({}))
    throw new APIError(
      error.error || "unknown_error",
      error.detail || `API error: ${res.status}`,
      res.status,
    )
  }

  return res.json()
}

export async function checkHealth(): Promise<HealthStatus> {
  try {
    const res = await fetch(`${API_URL}/health`, {
      signal: AbortSignal.timeout(3000)
    })
    if (!res.ok) return { ok: false, ingested: false, chunks: 0 }
    const data = await res.json()
    return {
      ok:       data.status === "ok",
      ingested: data.ingested ?? false,
      chunks:   data.chunks ?? 0,
    }
  } catch {
    return { ok: false, ingested: false, chunks: 0 }
  }
}

export async function fetchStats(): Promise<Stats> {
  const res = await fetch(`${API_URL}/api/stats`)
  if (!res.ok) throw new Error("Failed to fetch stats")
  return res.json()
}

export async function fetchCandidates(): Promise<Candidate[]> {
  const res = await fetch(`${API_URL}/api/candidates`)
  if (!res.ok) throw new Error("Failed to fetch candidates")
  const data = await res.json()
  return data.candidates
}

export async function fetchSuggestions(question: string): Promise<string[]> {
  try {
    const res = await fetch(`${API_URL}/api/suggestions`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    })
    if (!res.ok) return []
    const data = await res.json()
    return data.suggestions || []
  } catch {
    return []
  }
}