export interface Source {
  candidate: string
  source: string
  score: number
}

export interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  sources?: Source[]
  timestamp: Date
}

export interface ChatResponse {
  answer: string
  sources: Source[]
}

export interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  sources?: Source[]
  suggestions?: string[]
  timestamp: Date
}