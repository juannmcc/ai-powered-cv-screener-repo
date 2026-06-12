"use client"

import { AlertTriangle, Terminal } from "lucide-react"

interface Props {
  ingested: boolean
  backendOk: boolean
}

export default function IngestBanner({ ingested, backendOk }: Props) {
console.log("IngestBanner props:", { ingested, backendOk })
  if (!backendOk || ingested) return null

  return (
    <div className="relative z-10 bg-amber-50 border-b border-amber-200 px-6 py-3">
      <div className="max-w-3xl mx-auto flex items-center gap-3">
        <AlertTriangle size={16} className="text-amber-500 flex-shrink-0" />
        <p className="text-sm text-amber-700">
          No CVs ingested yet.
        </p>
        <div className="flex items-center gap-1.5 px-3 py-1 bg-amber-100 
                        rounded-lg border border-amber-200 ml-auto flex-shrink-0">
          <Terminal size={12} className="text-amber-600" />
          <code className="text-xs text-amber-700 font-mono">
            Go to <a href="/settings">Settings</a> to ingest CVs now.
          </code>
        </div>
      </div>
    </div>
  )
}