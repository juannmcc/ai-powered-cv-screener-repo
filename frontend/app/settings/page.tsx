"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { ArrowLeft, Check, X, Loader2, RefreshCw, Server, Image, Cpu, Key } from "lucide-react"
import CVManagement from "@/components/CVManagement"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

interface Settings {
  llm_provider: string
  llm_model: string
  embed_model: string
  image_provider: string
  ollama_base_url: string
  has_gemini_key: boolean
  has_openrouter_key: boolean
  has_cloudflare_key: boolean
  has_openai_key: boolean
}

interface ValidationResult {
  valid: boolean
  message: string
  models?: string[]
}

type StatusType = "idle" | "checking" | "valid" | "invalid"

function StatusDot({ status }: { status: StatusType }) {
  if (status === "checking") return <Loader2 size={14} className="text-yellow-500 animate-spin" />
  if (status === "valid")    return <Check size={14} className="text-green-500" />
  if (status === "invalid")  return <X size={14} className="text-red-500" />
  return <div className="w-2 h-2 rounded-full bg-gray-300" />
}

function StatusMessage({ status, message }: { status: StatusType; message: string }) {
  if (status === "idle") return null
  const color = status === "valid" ? "text-green-600" : status === "invalid" ? "text-red-500" : "text-yellow-600"
  return <p className={`text-xs mt-1 ${color}`}>{message}</p>
}

export default function SettingsPage() {
  const router                              = useRouter()
  const [settings, setSettings]             = useState<Settings | null>(null)
  const [validations, setValidations]       = useState<Record<string, StatusType>>({})
  const [validationMsgs, setValidationMsgs] = useState<Record<string, string>>({})
  const [ollamaModels, setOllamaModels]     = useState<string[]>([])
  const [saving, setSaving]                 = useState<string | null>(null)
  const [keyInputs, setKeyInputs]           = useState<Record<string, string>>({})

  useEffect(() => { loadSettings() }, [])

  async function loadSettings() {
    const res  = await fetch(`${API_URL}/api/settings`)
    const data = await res.json()
    setSettings(data)
    validateAll(data)
    loadOllamaModels()
  }

  async function loadOllamaModels() {
    const res  = await fetch(`${API_URL}/api/settings/ollama-models`)
    const data = await res.json()
    setOllamaModels(data.models || [])
  }

  async function validateProvider(provider: string) {
    setValidations(prev => ({ ...prev, [provider]: "checking" }))
    setValidationMsgs(prev => ({ ...prev, [provider]: "Checking..." }))
    const res  = await fetch(`${API_URL}/api/settings/validate/${provider}`)
    const data: ValidationResult = await res.json()
    setValidations(prev => ({ ...prev, [provider]: data.valid ? "valid" : "invalid" }))
    setValidationMsgs(prev => ({ ...prev, [provider]: data.message }))
    if (data.models) setOllamaModels(data.models)
  }

  async function validateAll(s: Settings) {
    const providers = ["ollama", "gemini", "openrouter", "cloudflare"]
    for (const p of providers) {
      validateProvider(p)
    }
  }

  async function saveSetting(key: string, value: string) {
    setSaving(key)
    await fetch(`${API_URL}/api/settings`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ key, value }),
    })
    await loadSettings()
    setSaving(null)
  }

  async function saveKey(envKey: string, provider: string) {
    const value = keyInputs[envKey] || ""
    if (!value.trim()) return
    await saveSetting(envKey, value)
    setKeyInputs(prev => ({ ...prev, [envKey]: "" }))
    validateProvider(provider)
  }

  if (!settings) return (
    <div className="flex items-center justify-center h-screen bg-gray-50">
      <Loader2 size={24} className="animate-spin text-blue-600" />
    </div>
  )

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-100 px-6 py-4 shadow-sm">
        <div className="max-w-2xl mx-auto flex items-center gap-4">
          <button
            onClick={() => router.push("/")}
            className="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-800 transition-all"
          >
            <ArrowLeft size={16} />
            Back to chat
          </button>
          <h1 className="text-base font-semibold text-gray-900">Settings</h1>
          <button
            onClick={loadSettings}
            className="ml-auto flex items-center gap-1.5 text-xs text-gray-400 hover:text-gray-600"
          >
            <RefreshCw size={13} />
            Refresh
          </button>
        </div>
      </header>

      <main className="max-w-2xl mx-auto px-6 py-8 space-y-6">

        {/* LLM Provider */}
        <section className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-50 flex items-center gap-2">
            <Server size={16} className="text-blue-600" />
            <h2 className="text-sm font-semibold text-gray-800">LLM Provider</h2>
          </div>
          <div className="p-6 space-y-4">

            {/* Ollama */}
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <StatusDot status={validations["ollama"] || "idle"} />
                  <span className="text-sm font-medium text-gray-700">Ollama (local)</span>
                  {settings.llm_provider === "ollama" && (
                    <span className="text-xs bg-blue-100 text-blue-600 px-2 py-0.5 rounded-full">Active</span>
                  )}
                </div>
                <p className="text-xs text-gray-400">Free, local. No API key needed.</p>
                <StatusMessage status={validations["ollama"] || "idle"} message={validationMsgs["ollama"] || ""} />
              </div>
              <button
                onClick={() => saveSetting("LLM_PROVIDER", "ollama")}
                disabled={settings.llm_provider === "ollama" || saving === "LLM_PROVIDER"}
                className="text-xs px-3 py-1.5 bg-blue-600 text-white rounded-lg 
                           hover:bg-blue-700 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
              >
                {settings.llm_provider === "ollama" ? "Active" : "Use"}
              </button>
            </div>

            {/* Ollama model selector */}
            {ollamaModels.length > 0 && (
              <div className="ml-6 flex items-center gap-2">
                <span className="text-xs text-gray-500">Model:</span>
                <select
                  value={settings.llm_model}
                  onChange={e => saveSetting("LLM_MODEL", e.target.value)}
                  className="text-xs border border-gray-200 rounded-lg px-2 py-1 text-gray-700
                             focus:outline-none focus:border-blue-300"
                >
                  {ollamaModels.map(m => (
                    <option key={m} value={m}>{m}</option>
                  ))}
                </select>
              </div>
            )}

            <hr className="border-gray-50" />

            {/* Gemini */}
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <StatusDot status={validations["gemini"] || "idle"} />
                  <span className="text-sm font-medium text-gray-700">Google Gemini</span>
                  {settings.llm_provider === "gemini" && (
                    <span className="text-xs bg-blue-100 text-blue-600 px-2 py-0.5 rounded-full">Active</span>
                  )}
                </div>
                <p className="text-xs text-gray-400">Free tier (region restricted). Requires API key.</p>
                <StatusMessage status={validations["gemini"] || "idle"} message={validationMsgs["gemini"] || ""} />
                {!settings.has_gemini_key && (
                  <div className="flex gap-2 mt-2">
                    <input
                      type="password"
                      placeholder="AIza..."
                      value={keyInputs["GEMINI_API_KEY"] || ""}
                      onChange={e => setKeyInputs(prev => ({ ...prev, GEMINI_API_KEY: e.target.value }))}
                      className="text-xs border border-gray-200 rounded-lg px-3 py-1.5 flex-1
                                 focus:outline-none focus:border-blue-300"
                    />
                    <button
                      onClick={() => saveKey("GEMINI_API_KEY", "gemini")}
                      className="text-xs px-3 py-1.5 bg-gray-800 text-white rounded-lg hover:bg-gray-900"
                    >
                      Save
                    </button>
                  </div>
                )}
              </div>
              <button
                onClick={() => saveSetting("LLM_PROVIDER", "gemini")}
                disabled={settings.llm_provider === "gemini" || !settings.has_gemini_key || validations["gemini"] === "invalid"}
                className="text-xs px-3 py-1.5 bg-blue-600 text-white rounded-lg
                           hover:bg-blue-700 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
              >
                {settings.llm_provider === "gemini" ? "Active" : "Use"}
              </button>
            </div>

            <hr className="border-gray-50" />

            {/* OpenRouter */}
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <StatusDot status={validations["openrouter"] || "idle"} />
                  <span className="text-sm font-medium text-gray-700">OpenRouter</span>
                  {settings.llm_provider === "openrouter" && (
                    <span className="text-xs bg-blue-100 text-blue-600 px-2 py-0.5 rounded-full">Active</span>
                  )}
                </div>
                <p className="text-xs text-gray-400">Free tier / pay-as-you-go. Requires API key.</p>
                <StatusMessage status={validations["openrouter"] || "idle"} message={validationMsgs["openrouter"] || ""} />
                {!settings.has_openrouter_key && (
                  <div className="flex gap-2 mt-2">
                    <input
                      type="password"
                      placeholder="sk-or-..."
                      value={keyInputs["OPENROUTER_API_KEY"] || ""}
                      onChange={e => setKeyInputs(prev => ({ ...prev, OPENROUTER_API_KEY: e.target.value }))}
                      className="text-xs border border-gray-200 rounded-lg px-3 py-1.5 flex-1
                                 focus:outline-none focus:border-blue-300"
                    />
                    <button
                      onClick={() => saveKey("OPENROUTER_API_KEY", "openrouter")}
                      className="text-xs px-3 py-1.5 bg-gray-800 text-white rounded-lg hover:bg-gray-900"
                    >
                      Save
                    </button>
                  </div>
                )}
              </div>
              <button
                onClick={() => saveSetting("LLM_PROVIDER", "openrouter")}
                disabled={settings.llm_provider === "openrouter" || !settings.has_openrouter_key || validations["openrouter"] === "invalid"}
                className="text-xs px-3 py-1.5 bg-blue-600 text-white rounded-lg
                           hover:bg-blue-700 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
              >
                {settings.llm_provider === "openrouter" ? "Active" : "Use"}
              </button>
            </div>
          </div>
        </section>

        {/* Image Provider */}
        <section className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-50 flex items-center gap-2">
            <Image size={16} className="text-purple-600" />
            <h2 className="text-sm font-semibold text-gray-800">Image Provider</h2>
          </div>
          <div className="p-6 space-y-4">

            {/* Cloudflare */}
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <StatusDot status={validations["cloudflare"] || "idle"} />
                  <span className="text-sm font-medium text-gray-700">Cloudflare Workers AI</span>
                  {settings.image_provider === "cloudflare" && (
                    <span className="text-xs bg-purple-100 text-purple-600 px-2 py-0.5 rounded-full">Active</span>
                  )}
                </div>
                <p className="text-xs text-gray-400">Free (10k/day). FLUX AI-generated photos.</p>
                <StatusMessage status={validations["cloudflare"] || "idle"} message={validationMsgs["cloudflare"] || ""} />
                {!settings.has_cloudflare_key && (
                  <div className="flex gap-2 mt-2">
                    <input
                      type="password"
                      placeholder="Cloudflare API Token"
                      value={keyInputs["CLOUDFLARE_API_TOKEN"] || ""}
                      onChange={e => setKeyInputs(prev => ({ ...prev, CLOUDFLARE_API_TOKEN: e.target.value }))}
                      className="text-xs border border-gray-200 rounded-lg px-3 py-1.5 flex-1
                                 focus:outline-none focus:border-blue-300"
                    />
                    <button
                      onClick={() => saveKey("CLOUDFLARE_API_TOKEN", "cloudflare")}
                      className="text-xs px-3 py-1.5 bg-gray-800 text-white rounded-lg hover:bg-gray-900"
                    >
                      Save
                    </button>
                  </div>
                )}
              </div>
              <button
                onClick={() => saveSetting("IMAGE_PROVIDER", "cloudflare")}
                disabled={settings.image_provider === "cloudflare" || !settings.has_cloudflare_key}
                className="text-xs px-3 py-1.5 bg-purple-600 text-white rounded-lg
                           hover:bg-purple-700 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
              >
                {settings.image_provider === "cloudflare" ? "Active" : "Use"}
              </button>
            </div>

            <hr className="border-gray-50" />

            {/* Placeholder */}
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <StatusDot status="valid" />
                  <span className="text-sm font-medium text-gray-700">Placeholder avatars</span>
                  {settings.image_provider === "placeholder" && (
                    <span className="text-xs bg-purple-100 text-purple-600 px-2 py-0.5 rounded-full">Active</span>
                  )}
                </div>
                <p className="text-xs text-gray-400">Free, no setup. Colored initials avatar.</p>
              </div>
              <button
                onClick={() => saveSetting("IMAGE_PROVIDER", "placeholder")}
                disabled={settings.image_provider === "placeholder"}
                className="text-xs px-3 py-1.5 bg-purple-600 text-white rounded-lg
                           hover:bg-purple-700 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
              >
                {settings.image_provider === "placeholder" ? "Active" : "Use"}
              </button>
            </div>
          </div>
        </section>

        {/* CV Management */}
        <section className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-50 flex items-center gap-2">
                <Cpu size={16} className="text-green-600" />
                <h2 className="text-sm font-semibold text-gray-800">CV Management</h2>
            </div>
            <div className="p-6 space-y-6">
                <CVManagement />
            </div>
        </section>

        {/* Info */}
        <p className="text-xs text-gray-400 text-center pb-8">
          Changes are saved to <code className="bg-gray-100 px-1 rounded">backend/.env</code> immediately.
          Restart the backend to apply LLM provider changes.
        </p>

      </main>
    </div>
  )
}