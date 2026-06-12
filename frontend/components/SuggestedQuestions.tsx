import { Sparkles } from "lucide-react"

interface Props {
  suggestions: string[]
  onSelect: (q: string) => void
}

export default function SuggestedQuestions({ suggestions, onSelect }: Props) {
  if (!suggestions?.length) return null

  return (
    <div className="mt-3 pt-3 border-t border-gray-100">
      <div className="flex items-center gap-1.5 mb-2">
        <Sparkles size={11} className="text-purple-400" />
        <p className="text-xs text-gray-400 font-medium uppercase tracking-wide">
          Follow-up questions
        </p>
      </div>
      <div className="flex flex-col gap-1.5">
        {suggestions.map((s, i) => (
          <button
            key={i}
            onClick={() => onSelect(s)}
            className="text-left text-xs px-3 py-2 bg-purple-50 text-purple-700
                       rounded-lg hover:bg-purple-100 transition-all border
                       border-purple-100 hover:border-purple-200"
          >
            {s}
          </button>
        ))}
      </div>
    </div>
  )
}