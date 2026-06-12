import { Message } from "@/types/chat"
import SourceBadge from "./SourceBadge"
import SuggestedQuestions from "./SuggestedQuestions"
import { User, Bot } from "lucide-react"

interface Props {
  message: Message
  onSuggestionSelect?: (q: string) => void
}

export default function ChatMessage({ message, onSuggestionSelect }: Props) {
  const isUser = message.role === "user"

  return (
    <div className={`flex gap-3 ${isUser ? "flex-row-reverse" : "flex-row"}`}>
      {/* Avatar */}
      <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center
                       justify-center ${isUser ? "bg-blue-600" : "bg-gray-100"}`}>
        {isUser
          ? <User size={16} className="text-white" />
          : <Bot size={16} className="text-gray-600" />
        }
      </div>

      {/* Bubble */}
      <div className={`max-w-[75%] rounded-2xl px-4 py-3 ${
        isUser
          ? "bg-blue-600 text-white rounded-tr-sm"
          : "bg-white border border-gray-100 text-gray-800 rounded-tl-sm shadow-sm"
      }`}>
        <p className="text-sm leading-relaxed whitespace-pre-wrap">
          {message.content}
        </p>
        {!isUser && message.sources && (
          <SourceBadge sources={message.sources} />
        )}
        {!isUser && message.suggestions && onSuggestionSelect && (
          <SuggestedQuestions
            suggestions={message.suggestions}
            onSelect={onSuggestionSelect}
          />
        )}
      </div>
    </div>
  )
}