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

  // text = what the backend receives, display = what the user sees in chat
  async function handleSend(text, display = text) {
    setMessages((m) => [...m, { role: "user", text: display }])
    setLoading(true)
    setError("")

    try {
      const result = await sendMessage(text, query, pendingField)

      if (result.status === "needs_clarification") {
        setQuery(result.query)
        setPendingField(result.pending_field)

        const hasOptions = Array.isArray(result.options) && result.options.length > 0
        setMessages((m) => [
          ...m,
          hasOptions
            ? {
                role: "assistant",
                type: "form",
                question: result.message,
                helper: "Select one option, then submit to continue.",
                options: result.options,
              }
            : { role: "assistant", text: result.message },
        ])
        return
      }

      if (result.status === "ready") {
        const prediction = await getPrediction(result.query)
        setMessages((m) => [
          ...m,
          { role: "assistant", type: "prediction", text: `Estimated resolution time: ${prediction.estimate}` },
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
        <ChatPanel
          messages={messages}
          loading={loading}
          error={error}
          onSend={handleSend}
          onFormSubmit={(option) => handleSend(option.value, option.label)}
        />
      </main>
    </div>
  )
}

export default App