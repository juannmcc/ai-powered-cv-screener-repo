import { Source } from "@/types/chat"
import { FileText } from "lucide-react"

interface Props {
  sources: Source[]
}

export default function SourceBadge({ sources }: Props) {
  if (!sources?.length) return null

  return (
    <div className="mt-3 pt-3 border-t border-gray-100">
      <p className="text-xs text-gray-400 mb-2 font-medium uppercase tracking-wide">
        Sources
      </p>
      <div className="flex flex-wrap gap-2">
        {sources.map((s) => (
          <div
            key={s.candidate}
            className="flex items-center gap-1.5 px-2.5 py-1 bg-blue-50 
                       text-blue-700 rounded-full text-xs font-medium"
          >
            <FileText size={11} />
            <span>{s.candidate}</span>
            <span className="text-blue-400">·</span>
            <span className="text-blue-400">{Math.round(s.score * 100)}%</span>
          </div>
        ))}
      </div>
    </div>
  )
}
