"use client"

import { useState, useRef, useEffect } from "react"
import { Message } from "@/types/chat"
import CandidateBrowser from "@/components/CandidateBrowser"
import { askQuestion, checkHealth, fetchStats, fetchCandidates, fetchSuggestions, APIError, Stats, Candidate } from "@/lib/api"
import ChatMessage from "@/components/ChatMessage"
import TypingIndicator from "@/components/TypingIndicator"
import { Send, BrainCircuit, RotateCcw, Database, Settings, Copy, Check } from "lucide-react"
import IngestBanner from "@/components/IngestBanner"

const BASE_SUGGESTIONS = [
  "Who has experience with Python?",
  "Which candidates have a background in machine learning?",
  "Who is the most senior engineer?",
]

const START_CMD = "cd backend && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000"

export default function Home() {
  const [messages, setMessages]           = useState<Message[]>([])
  const [input, setInput]                 = useState("")
  const [loading, setLoading]             = useState(false)
  const [backendStatus, setBackendStatus] = useState<"checking" | "ok" | "error">("checking")
  const [ingested, setIngested]           = useState(false)
  const [stats, setStats]                 = useState<Stats | null>(null)
  const [candidates, setCandidates]       = useState<Candidate[]>([])
  const [browserOpen, setBrowserOpen]     = useState(false)
  const [copied, setCopied]               = useState(false)
  const bottomRef                         = useRef<HTMLDivElement>(null)

  useEffect(() => {
    async function check() {
      const health = await checkHealth()
      setBackendStatus(health.ok ? "ok" : "error")
      setIngested(health.ingested)
      if (health.ok) {
        try { const s = await fetchStats(); setStats(s) } catch {}
        try { const c = await fetchCandidates(); setCandidates(c) } catch {}
      } else {
        setStats(null)
        setCandidates([])
      }
    }
    check()
    const interval = setInterval(check, 5000)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages, loading])

  const dynamicSuggestions = [
    ...BASE_SUGGESTIONS,
    candidates.length > 0
      ? `Summarize the profile of ${candidates[0].name}`
      : "Who is the most experienced candidate?",
  ]

  async function sendMessage(question: string) {
    if (!question.trim() || loading || backendStatus !== "ok" || !ingested) return

    const userMsg: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content: question,
      timestamp: new Date(),
    }

    setMessages(prev => [...prev, userMsg])
    setInput("")
    setLoading(true)

    try {
      const [data, suggestions] = await Promise.all([
        askQuestion(question),
        fetchSuggestions(question),
      ])

      const assistantMsg: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: data.answer,
        sources: data.sources,
        suggestions,
        timestamp: new Date(),
      }
      setMessages(prev => [...prev, assistantMsg])
    } catch (err) {
      let content = "Sorry, something went wrong. Make sure the backend is running."
      if (err instanceof APIError) {
        if (err.code === "no_cvs_ingested") {
          content = "No CVs found in the database. Please run: uv run ingest-cvs"
        } else if (err.code === "provider_unavailable") {
          content = `LLM provider error: ${err.message}. Check your provider configuration.`
        } else {
          content = err.message
        }
      }
      setMessages(prev => [...prev, {
        id: crypto.randomUUID(),
        role: "assistant",
        content,
        timestamp: new Date(),
      }])
    } finally {
      setLoading(false)
    }
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      sendMessage(input)
    }
  }

  function handleCandidateSelect(name: string) {
    setBrowserOpen(false)
    sendMessage(`Summarize the profile of ${name}`)
  }

  async function copyCommand() {
    await navigator.clipboard.writeText(START_CMD)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const isOffline = backendStatus === "error"

  return (
    <div className={`flex flex-col h-screen bg-gray-50 transition-all duration-300 ${browserOpen ? "ml-64" : "ml-0"}`}>

      <CandidateBrowser
        candidates={candidates}
        onSelect={handleCandidateSelect}
        isOpen={browserOpen && !isOffline}
        onToggle={() => !isOffline && setBrowserOpen(prev => !prev)}
      />

      {/* Header */}
      <header className="bg-white border-b border-gray-100 px-6 py-4 shadow-sm">
        <div className="max-w-3xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 bg-blue-600 rounded-xl flex items-center justify-center">
              <BrainCircuit size={20} className="text-white" />
            </div>
            <div>
              <h1 className="text-base font-semibold text-gray-900">CV Screener</h1>
              <div className="flex items-center gap-1.5">
                <p className="text-xs text-gray-400">AI-powered candidate search</p>
                <span className="text-gray-300">·</span>
                <div className="flex items-center gap-1">
                  <div className={`w-1.5 h-1.5 rounded-full ${
                    backendStatus === "ok"    ? "bg-green-400" :
                    backendStatus === "error" ? "bg-red-400" :
                    "bg-yellow-400 animate-pulse"
                  }`} />
                  <span className={`text-xs ${
                    backendStatus === "ok"    ? "text-green-500" :
                    backendStatus === "error" ? "text-red-400" :
                    "text-yellow-500"
                  }`}>
                    {backendStatus === "ok"    ? "Backend connected" :
                     backendStatus === "error" ? "Backend offline" :
                     "Connecting..."}
                  </span>
                </div>
                {stats && !isOffline && (
                  <>
                    <span className="text-gray-300">·</span>
                    <div className="flex items-center gap-1 text-xs text-gray-400">
                      <Database size={10} />
                      <span>{stats.estimated_cvs} CVs</span>
                    </div>
                  </>
                )}
              </div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <a
              href="/settings"
              className={`flex items-center gap-2 px-3 py-1.5 text-xs rounded-lg transition-all ${
                isOffline
                  ? "text-gray-300 cursor-not-allowed pointer-events-none"
                  : "text-gray-400 hover:text-gray-600 hover:bg-gray-50"
              }`}
            >
              <Settings size={13} />
              Settings
            </a>
            {messages.length > 0 && !isOffline && (
              <button
                onClick={() => setMessages([])}
                className="flex items-center gap-2 px-3 py-1.5 text-xs text-gray-400
                           hover:text-gray-600 hover:bg-gray-50 rounded-lg transition-all"
              >
                <RotateCcw size={13} />
                New conversation
              </button>
            )}
          </div>
        </div>
      </header>

      {!isOffline && (
        <IngestBanner
          ingested={ingested}
          backendOk={backendStatus === "ok"}
        />
      )}

      {/* Messages */}
      <main className="flex-1 overflow-y-auto px-4 py-6">
        <div className="max-w-3xl mx-auto space-y-6">

          {messages.length === 0 && (
            <div className="text-center pt-16">
              <div className={`w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-4 ${
                isOffline ? "bg-red-50" : "bg-blue-50"
              }`}>
                <BrainCircuit size={32} className={isOffline ? "text-red-400" : "text-blue-600"} />
              </div>

              {isOffline ? (
                <>
                  <h2 className="text-xl font-semibold text-gray-800 mb-2">
                    Backend offline
                  </h2>
                  <p className="text-gray-400 text-sm mb-4">
                    Start the backend server to get started.
                  </p>
                  <div className="inline-flex items-center gap-2 bg-gray-900 rounded-xl px-4 py-3">
                    <code className="text-xs text-gray-300 font-mono">
                      {START_CMD}
                    </code>
                    <button
                      onClick={copyCommand}
                      className="ml-2 text-gray-500 hover:text-white transition-colors flex-shrink-0"
                      title="Copy command"
                    >
                      {copied
                        ? <Check size={14} className="text-green-400" />
                        : <Copy size={14} />
                      }
                    </button>
                  </div>
                  {copied && (
                    <p className="text-xs text-green-500 mt-2">Copied!</p>
                  )}
                </>
              ) : (
                <>
                  <h2 className="text-xl font-semibold text-gray-800 mb-2">
                    Ask about your candidates
                  </h2>
                  <p className="text-gray-400 text-sm mb-8">
                    Search across{" "}
                    <span className="text-blue-500 font-medium">
                      {stats?.estimated_cvs ?? "..."} CVs
                    </span>{" "}
                    using natural language
                  </p>
                  {ingested && candidates.length > 0 && (
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-lg mx-auto">
                      {dynamicSuggestions.map((s) => (
                        <button
                          key={s}
                          onClick={() => sendMessage(s)}
                          className="text-left px-4 py-3 bg-white border border-gray-100
                                     rounded-xl text-sm text-gray-600 hover:border-blue-200
                                     hover:text-blue-600 hover:bg-blue-50 transition-all shadow-sm"
                        >
                          {s}
                        </button>
                      ))}
                    </div>
                  )}
                </>
              )}
            </div>
          )}

          {messages.map((msg) => (
            <ChatMessage
              key={msg.id}
              message={msg}
              onSuggestionSelect={sendMessage}
            />
          ))}

          {loading && <TypingIndicator />}
          <div ref={bottomRef} />
        </div>
      </main>

      {/* Input */}
      <footer className="bg-white border-t border-gray-100 px-4 py-4">
        <div className="max-w-3xl mx-auto flex gap-3">
          <input
            type="text"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={
              isOffline  ? "Backend offline — start the server first" :
              !ingested  ? "No CVs ingested — go to Settings first" :
              "Ask about candidates..."
            }
            disabled={loading || isOffline || !ingested}
            className="flex-1 px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl
                       text-sm text-gray-800 placeholder-gray-400 outline-none
                       focus:border-blue-300 focus:bg-white transition-all
                       disabled:opacity-50 disabled:cursor-not-allowed"
          />
          <button
            onClick={() => sendMessage(input)}
            disabled={loading || !input.trim() || isOffline || !ingested}
            className="w-11 h-11 bg-blue-600 hover:bg-blue-700 disabled:opacity-40
                       rounded-xl flex items-center justify-center transition-all
                       disabled:cursor-not-allowed"
          >
            <Send size={16} className="text-white" />
          </button>
        </div>
      </footer>

    </div>
  )
}