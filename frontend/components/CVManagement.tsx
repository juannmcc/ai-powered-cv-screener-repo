"use client"

import { useState, useEffect, useRef } from "react"
import { Trash2, RefreshCw, Play, FolderOpen, AlertTriangle, Check } from "lucide-react"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

interface Folder {
  name: string
  count: number
  pdfs: string[]
}

interface CVStats {
  folders: Folder[]
  total_pdfs: number
  ingested_chunks: number
}

export default function CVManagement() {
  const [stats, setStats]                   = useState<CVStats | null>(null)
  const [logs, setLogs]                     = useState<string[]>([])
  const [running, setRunning]               = useState<string | null>(null)
  const [confirm, setConfirm]               = useState<string | null>(null)
  const [limit, setLimit]                   = useState(25)
  const [noImage, setNoImage]               = useState(false)
  const [expandedFolder, setExpanded]       = useState<string | null>(null)
  const [selectedFolder, setSelectedFolder] = useState<string | null>(null)
  const [ingestedFolder, setIngestedFolder] = useState<string | null>(null)
  const logsRef                             = useRef<HTMLDivElement>(null)
  const abortRef                            = useRef<AbortController | null>(null)

  useEffect(() => { loadStats() }, [])
  useEffect(() => {
    logsRef.current?.scrollTo(0, logsRef.current.scrollHeight)
  }, [logs])

  async function loadStats() {
    const res  = await fetch(`${API_URL}/api/cvs`)
    const data = await res.json()
    setStats(data)
  }

  async function streamAction(url: string, label: string) {
    const controller = new AbortController()
    abortRef.current = controller

    setRunning(label)
    setLogs([`▶ Starting ${label}...`])

    try {
      const res     = await fetch(url, { method: "POST", signal: controller.signal })
      const reader  = res.body!.getReader()
      const decoder = new TextDecoder()

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        const text  = decoder.decode(value)
        const lines = text.split("\n").filter(l => l.startsWith("data: "))
        for (const line of lines) {
          const msg = line.replace("data: ", "").trim()
          if (msg === "__DONE__") {
            setLogs(prev => [...prev, "✅ Done!"])
            if (label === "ingest") {
              setIngestedFolder(selectedFolder || stats?.folders[0]?.name || null)
            }
            setRunning(null)
            loadStats()
            return
          }
          if (msg) setLogs(prev => [...prev, msg])
        }
      }
    } catch (err: any) {
      if (err.name === "AbortError") {
        setLogs(prev => [...prev, "⛔ Cancelled."])
      }
    }

    setRunning(null)
    loadStats()
  }

  function cancelAction() {
    abortRef.current?.abort()
    setRunning(null)
  }

  async function deleteFolder(name: string) {
    await fetch(`${API_URL}/api/cvs/${name}`, { method: "DELETE" })
    setConfirm(null)
    if (ingestedFolder === name) setIngestedFolder(null)
    if (selectedFolder === name) setSelectedFolder(null)
    loadStats()
  }

  async function deleteAll() {
    await fetch(`${API_URL}/api/cvs`, { method: "DELETE" })
    setConfirm(null)
    setLogs([])
    setIngestedFolder(null)
    setSelectedFolder(null)
    loadStats()
  }

  return (
    <div className="space-y-5">

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-3 gap-3">
          {[
            { label: "Folders", value: stats.folders.length },
            { label: "PDFs",    value: stats.total_pdfs },
            { label: "Chunks",  value: stats.ingested_chunks },
          ].map(s => (
            <div key={s.label} className="bg-gray-50 rounded-xl px-4 py-3 text-center">
              <p className="text-xl font-bold text-gray-800">{s.value}</p>
              <p className="text-xs text-gray-400">{s.label}</p>
            </div>
          ))}
        </div>
      )}

      {/* Folders list */}
      {stats && stats.folders.length > 0 && (
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">
              Generated folders
            </p>
            <button
              onClick={() => setConfirm("all")}
              className="text-xs text-red-400 hover:text-red-600 flex items-center gap-1"
            >
              <Trash2 size={11} />
              Delete all
            </button>
          </div>

          {stats.folders.map((f, idx) => {
            const isActive = ingestedFolder ? f.name === ingestedFolder : idx === 0
            return (
              <div key={f.name} className={`border rounded-xl overflow-hidden ${
                isActive ? "border-blue-200" : "border-gray-100"
              }`}>
                <div className={`flex items-center gap-3 px-4 py-3 ${
                  isActive ? "bg-blue-50" : "bg-gray-50"
                }`}>
                  <FolderOpen size={14} className={isActive ? "text-blue-400" : "text-gray-400"} />
                  <span className="text-sm text-gray-700 font-mono flex-1">{f.name}</span>
                  {isActive && (
                    <span className="flex items-center gap-1 text-xs text-blue-600
                                     bg-blue-100 px-2 py-0.5 rounded-full">
                      <Check size={10} />
                      Active
                    </span>
                  )}
                  <span className="text-xs text-gray-400">{f.count} PDFs</span>
                  <button
                    onClick={() => setExpanded(expandedFolder === f.name ? null : f.name)}
                    className="text-xs text-blue-500 hover:text-blue-700"
                  >
                    {expandedFolder === f.name ? "Hide" : "View"}
                  </button>
                  <button
                    onClick={() => setConfirm(f.name)}
                    className="text-red-400 hover:text-red-600"
                  >
                    <Trash2 size={13} />
                  </button>
                </div>

                {expandedFolder === f.name && (
                  <div className="px-4 py-3 grid grid-cols-2 gap-1 bg-white">
                    {f.pdfs.map(pdf => (
                      <p key={pdf} className="text-xs text-gray-500 truncate">
                        {pdf.replace(".pdf", "").replace(/^cv_\d+_/, "").replace(/_/g, " ")}
                      </p>
                    ))}
                  </div>
                )}
              </div>
            )
          })}

          <p className="text-xs text-gray-400 text-center pt-1">
            Active folder is the one currently ingested in ChromaDB
          </p>
        </div>
      )}

      {/* Confirm dialog */}
      {confirm && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 flex items-center gap-3">
          <AlertTriangle size={16} className="text-red-500 flex-shrink-0" />
          <p className="text-sm text-red-700 flex-1">
            {confirm === "all"
              ? "Delete all CV folders, avatars and ChromaDB?"
              : `Delete folder "${confirm}"?`}
          </p>
          <button
            onClick={() => confirm === "all" ? deleteAll() : deleteFolder(confirm)}
            className="text-xs px-3 py-1.5 bg-red-600 text-white rounded-lg hover:bg-red-700"
          >
            Delete
          </button>
          <button
            onClick={() => setConfirm(null)}
            className="text-xs px-3 py-1.5 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
          >
            Cancel
          </button>
        </div>
      )}

      {/* Actions */}
      <div className="space-y-3">
        <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">Actions</p>

        {/* Generate */}
        <div className="border border-gray-100 rounded-xl p-4 space-y-3">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-700">Generate CVs</p>
              <p className="text-xs text-gray-400">Creates PDF CVs using Ollama + AI photos</p>
            </div>
            <div className="flex flex-col items-end gap-1">
              <button
                onClick={() => {
                  const url = `${API_URL}/api/cvs/generate?limit=${limit}${noImage ? "&no_image=true" : ""}`
                  streamAction(url, "generate")
                }}
                disabled={!!running}
                className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white
                           rounded-xl text-sm hover:bg-green-700 disabled:opacity-40 transition-all"
              >
                {running === "generate"
                  ? <RefreshCw size={14} className="animate-spin" />
                  : <Play size={14} />
                }
                Generate
              </button>
              {running === "generate" && (
                <button
                  onClick={cancelAction}
                  className="text-xs text-red-400 underline hover:text-red-600 transition-colors"
                >
                  cancel
                </button>
              )}
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <label className="text-xs text-gray-500">Count:</label>
              <input
                type="number"
                min={1}
                max={25}
                value={limit || ""}
                onChange={e => {
                  const raw = e.target.value
                  if (raw === "") { setLimit(1); return }
                  const val = parseInt(raw)
                  if (!isNaN(val)) setLimit(Math.min(25, Math.max(1, val)))
                }}
                className="w-16 text-xs border border-gray-200 rounded-lg px-2 py-1
                           text-gray-800 bg-white focus:outline-none focus:border-blue-300"
              />
            </div>
            <label className="flex items-center gap-2 text-xs text-gray-500 cursor-pointer">
              <input
                type="checkbox"
                checked={noImage}
                onChange={e => setNoImage(e.target.checked)}
                className="rounded"
              />
              Skip AI photos (faster)
            </label>
          </div>
        </div>

        {/* Ingest */}
        <div className="border border-gray-100 rounded-xl p-4 space-y-3">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-700">Ingest CVs</p>
              <p className="text-xs text-gray-400">Embeds PDFs into ChromaDB vector store</p>
            </div>
            <div className="flex flex-col items-end gap-1">
              <button
                onClick={() => {
                  const selected = selectedFolder || stats?.folders[0]?.name
                  if (!selected) return
                  streamAction(`${API_URL}/api/cvs/ingest?folder=${selected}`, "ingest")
                }}
                disabled={!!running || !stats?.total_pdfs || !stats?.folders.length}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white
                           rounded-xl text-sm hover:bg-blue-700 disabled:opacity-40 transition-all"
              >
                {running === "ingest"
                  ? <RefreshCw size={14} className="animate-spin" />
                  : <Play size={14} />
                }
                Ingest
              </button>
              {running === "ingest" && (
                <button
                  onClick={cancelAction}
                  className="text-xs text-red-400 underline hover:text-red-600 transition-colors"
                >
                  cancel
                </button>
              )}
            </div>
          </div>

          {/* Folder selector */}
          {stats && stats.folders.length > 0 && (
            <div className="flex items-center gap-2">
              <label className="text-xs text-gray-500">Folder:</label>
              <select
                value={selectedFolder || stats.folders[0]?.name}
                onChange={e => setSelectedFolder(e.target.value)}
                className="text-xs border border-gray-200 rounded-lg px-2 py-1 text-gray-700
                           focus:outline-none focus:border-blue-300 flex-1"
              >
                {stats.folders.map((f, idx) => (
                  <option key={f.name} value={f.name}>
                    {f.name} ({f.count} PDFs){idx === 0 ? " — latest" : ""}
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Warning if selected folder has 0 PDFs */}
          {stats && selectedFolder && (() => {
            const f = stats.folders.find(f => f.name === selectedFolder)
            if (f && f.count === 0) return (
              <p className="text-xs text-red-400 flex items-center gap-1">
                <AlertTriangle size={11} />
                This folder has no PDFs — select another or generate first.
              </p>
            )
            return null
          })()}
        </div>
      </div>

      {/* Logs */}
      {logs.length > 0 && (
        <div
          ref={logsRef}
          className="bg-gray-900 rounded-xl p-4 h-48 overflow-y-auto font-mono"
        >
          {logs.map((log, i) => (
            <p key={i} className={`text-xs leading-5 ${
              log.startsWith("OK")   ? "text-green-400" :
              log.startsWith("▶")   ? "text-blue-400"  :
              log.startsWith("NO OK")  ? "text-orange-400" :
              log.includes("Error") ? "text-red-400"   :
              log.includes("failed")? "text-red-400"   :
              "text-gray-300"
            }`}>
              {log}
            </p>
          ))}
          {running && (
            <p className="text-xs text-yellow-400 animate-pulse">Running...</p>
          )}
        </div>
      )}
    </div>
  )
}