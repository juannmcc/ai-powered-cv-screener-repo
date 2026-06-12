"use client"

import { Candidate } from "@/lib/api"
import { User, ChevronRight, Users } from "lucide-react"
import { useState } from "react"

interface Props {
  candidates: Candidate[]
  onSelect: (name: string) => void
  isOpen: boolean
  onToggle: () => void
}

export default function CandidateBrowser({ candidates, onSelect, isOpen, onToggle }: Props) {
  return (
    <>
      {/* Toggle button */}
      <button
        onClick={onToggle}
        className={`fixed top-1/2 -translate-y-1/2 z-20
           flex items-center gap-2 px-3 py-4 rounded-r-xl
           text-xs font-medium transition-all duration-300 shadow-md
           ${isOpen
             ? "left-64 bg-blue-600 text-white"
             : "left-0 bg-white text-gray-600 border border-gray-200 hover:bg-blue-50 hover:text-blue-600"
           }`}
      >
        <Users size={14} />
        <span className="writing-mode-vertical hidden sm:block">
          {candidates.length} CVs
        </span>
      </button>

      {/* Drawer */}
      <div className={`fixed left-0 top-0 h-full z-10 transition-all duration-300
                       bg-white border-r border-gray-100 shadow-lg flex flex-col
                       ${isOpen ? "w-64 translate-x-0" : "w-64 -translate-x-full"}`}>

        {/* Header */}
        <div className="px-4 py-4 border-b border-gray-100">
          <div className="flex items-center gap-2">
            <Users size={16} className="text-blue-600" />
            <h2 className="text-sm font-semibold text-gray-800">Candidates</h2>
            <span className="ml-auto text-xs text-gray-400 bg-gray-100 
                             px-2 py-0.5 rounded-full">
              {candidates.length}
            </span>
          </div>
        </div>

        {/* List */}
        <div className="flex-1 overflow-y-auto py-2">
          {candidates.length === 0 ? (
            <p className="text-xs text-gray-400 text-center py-8 px-4">
              No candidates found.<br />Run ingest-cvs first.
            </p>
          ) : (
            candidates.map((c) => (
              <button
                key={c.name}
                onClick={() => onSelect(c.name)}
                className="w-full flex items-center gap-3 px-4 py-2.5
                           hover:bg-blue-50 hover:text-blue-600 transition-all
                           text-left group"
              >
                    <div className="w-8 h-8 rounded-full overflow-hidden flex-shrink-0
                    bg-blue-100 flex items-center justify-center border
                    border-blue-200">
                        <img
                            src={`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}${c.avatar}`}
                            alt={c.name}
                            className="w-full h-full object-cover"
                            onError={(e) => {
                            const target = e.currentTarget
                            target.style.display = "none"
                            const parent = target.parentElement
                            if (parent) {
                                parent.innerHTML = `
                                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14"
                                    viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2">
                                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                                    <circle cx="12" cy="7" r="4"/>
                                </svg>`
                            }
                            }}
                        />
                    </div>
                <span className="text-sm text-gray-700 group-hover:text-blue-600 
                                 truncate flex-1">
                  {c.name}
                </span>
                <ChevronRight size={12} className="text-gray-300 
                                                    group-hover:text-blue-400 
                                                    flex-shrink-0" />
              </button>
            ))
          )}
        </div>

        {/* Footer */}
        <div className="px-4 py-3 border-t border-gray-100">
          <p className="text-xs text-gray-400 text-center">
            Click a candidate to ask about them
          </p>
        </div>
      </div>
    </>
  )
}