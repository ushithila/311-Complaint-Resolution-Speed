import { useState } from 'react'
import ChatPanel from './components/chat/ChatPanel'
import Sidebar from './components/Sidebar'
import Header from './components/Header'
import { sendMessage, getPrediction } from './api'

function App() {
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [query, setQuery] = useState(null)
  const [pendingField, setPendingField] = useState(null)

  async function handleSend(text) {
    setMessages((m) => [...m, { role: "user", text }])
    setLoading(true)
    setError("")

    try {
      const result = await sendMessage(text, query, pendingField)

      if (result.status === "needs_clarification") {
        setQuery(result.query)
        setPendingField(result.pending_field)
        setMessages((m) => [...m, { role: "assistant", text: result.message, options: result.options ?? null }])
        return
      }

      if (result.status === "ready") {
        const prediction = await getPrediction(result.query)
        setMessages((m) => [
          ...m,
          {
            role: "assistant",
            type: "prediction",
            text: `Estimated resolution time: ${prediction.hours.toFixed(1)} hours`,
          },
        ])
        setQuery(null)
        setPendingField(null)
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex h-screen flex-col">
      <Header />
      <main className="flex min-h-0 flex-1">
        <Sidebar />
        <ChatPanel messages={messages} loading={loading} error={error} onSend={handleSend} />
      </main>
    </div>
  )
}

export default App