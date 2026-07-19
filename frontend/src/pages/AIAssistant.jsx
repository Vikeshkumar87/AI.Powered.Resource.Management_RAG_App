import { useState, useRef, useEffect } from 'react'
import axios from 'axios'
import ChatMessage from '../components/ChatMessage'

const EXAMPLES = [
  'Find two available Python developers with Azure experience for a healthcare project.',
  'Suggest Java developers with AWS experience for a banking portal.',
  'Who are the best GenAI engineers available right now?',
  'Find a DevOps engineer with Kubernetes and Terraform skills.',
  'Recommend a senior project manager for an agile banking programme.',
]

function RecommendationCard({ rec, rank }) {
  const score = rec.match_score ?? 0
  const badge = score >= 85 ? '🟢' : score >= 70 ? '🟡' : '🔴'

  return (
    <div className="border border-gray-200 rounded-xl p-4 bg-white shadow-sm">
      <div className="flex items-center justify-between mb-3">
        <div className="font-semibold text-gray-900">
          {badge} {rank}. {rec.name}
          <span className="ml-2 text-xs font-mono text-gray-400">{rec.employee_id}</span>
        </div>
        <span className="bg-blue-600 text-white text-sm font-bold px-3 py-1 rounded-full">
          {score}% Match
        </span>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
        <div>
          <p className="font-medium text-green-700 mb-1">✅ Why they fit:</p>
          <ul className="list-disc list-inside space-y-0.5 text-gray-700">
            {(rec.reasons || []).map((r, i) => <li key={i}>{r}</li>)}
          </ul>
        </div>
        <div className="space-y-2">
          {rec.skill_gaps?.length > 0 && (
            <div>
              <p className="font-medium text-orange-600 mb-1">⚠️ Skill Gaps:</p>
              <ul className="list-disc list-inside space-y-0.5 text-gray-700">
                {rec.skill_gaps.map((g, i) => <li key={i}>{g}</li>)}
              </ul>
            </div>
          )}
          {rec.upskilling_suggestions?.length > 0 && (
            <div>
              <p className="font-medium text-purple-600 mb-1">📚 Upskilling:</p>
              <ul className="list-disc list-inside space-y-0.5 text-gray-700">
                {rec.upskilling_suggestions.map((s, i) => <li key={i}>{s}</li>)}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default function AIAssistant() {
  const [messages, setMessages] = useState([])
  const [input, setInput]       = useState('')
  const [topK, setTopK]         = useState(3)
  const [loading, setLoading]   = useState(false)
  const bottomRef               = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const sendQuery = async (query) => {
    if (!query.trim() || loading) return
    setMessages(prev => [...prev, { role: 'user', content: query }])
    setInput('')
    setLoading(true)

    try {
      const { data } = await axios.post('/api/rag/query', { query, top_k: topK })
      setMessages(prev => [...prev, { role: 'assistant', data }])
    } catch (e) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        data: { error: 'Cannot reach backend. Ensure FastAPI is running on port 8000.' },
      }])
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    sendQuery(input)
  }

  return (
    <div className="flex flex-col h-[calc(100vh-140px)]">
      <div className="mb-4">
        <h2 className="text-2xl font-bold text-gray-900">💬 AI Staffing Assistant</h2>
        <p className="text-gray-500 text-sm mt-1">
          Ask in plain English — the AI retrieves best-matched employees and explains why they fit.
        </p>
      </div>

      {/* Settings bar */}
      <div className="flex items-center gap-4 mb-3 text-sm">
        <label className="text-gray-600 font-medium">Recommendations:</label>
        {[1, 2, 3, 4, 5].map(n => (
          <button
            key={n}
            onClick={() => setTopK(n)}
            className={`w-8 h-8 rounded-full font-medium transition-colors ${
              topK === n ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {n}
          </button>
        ))}
        {messages.length > 0 && (
          <button
            onClick={() => setMessages([])}
            className="ml-auto text-red-500 hover:text-red-700 text-xs"
          >
            🗑️ Clear Chat
          </button>
        )}
      </div>

      {/* Example queries */}
      {messages.length === 0 && (
        <div className="mb-4 bg-blue-50 rounded-xl p-4">
          <p className="text-xs font-semibold text-blue-700 mb-2">💡 Try these example queries:</p>
          <div className="flex flex-wrap gap-2">
            {EXAMPLES.map((ex, i) => (
              <button
                key={i}
                onClick={() => sendQuery(ex)}
                className="text-xs bg-white border border-blue-200 text-blue-700 hover:bg-blue-100 px-3 py-1.5 rounded-full transition-colors text-left"
              >
                {ex}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Chat messages */}
      <div className="flex-1 overflow-y-auto space-y-4 pr-1">
        {messages.map((msg, i) => {
          if (msg.role === 'user') {
            return <ChatMessage key={i} role="user" content={msg.content} />
          }
          // Assistant response
          const { data } = msg
          if (data?.error) {
            return (
              <div key={i} className="flex justify-start">
                <div className="bg-red-50 border border-red-200 text-red-700 rounded-2xl px-5 py-3 text-sm max-w-xl">
                  ⚠️ {data.error}
                </div>
              </div>
            )
          }
          return (
            <div key={i} className="space-y-3">
              {data?.summary && (
                <div className="bg-blue-50 border border-blue-200 text-blue-800 rounded-xl px-4 py-2 text-sm">
                  {data.summary}
                </div>
              )}
              {(data?.recommendations || []).map((rec, j) => (
                <RecommendationCard key={j} rec={rec} rank={j + 1} />
              ))}
            </div>
          )
        })}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-white border border-gray-200 rounded-2xl px-5 py-3 text-sm text-gray-500 animate-pulse">
              Searching employee profiles…
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="mt-4 flex gap-3">
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder="Describe your staffing requirement…"
          className="flex-1 border border-gray-300 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-medium px-6 py-3 rounded-xl text-sm transition-colors"
        >
          {loading ? '…' : 'Send'}
        </button>
      </form>
    </div>
  )
}
