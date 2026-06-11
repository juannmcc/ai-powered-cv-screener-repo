export default function TypingIndicator() {
  return (
    <div className="flex gap-3">
      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-100 
                      flex items-center justify-center">
        <div className="w-4 h-4 rounded-full bg-gray-400 animate-pulse" />
      </div>
      <div className="bg-white border border-gray-100 rounded-2xl rounded-tl-sm 
                      px-4 py-3 shadow-sm">
        <div className="flex gap-1 items-center h-5">
          <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:0ms]" />
          <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:150ms]" />
          <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:300ms]" />
        </div>
      </div>
    </div>
  )
}