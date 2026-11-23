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
  const [confirmed, setConfirmed] = useState(false)
  const [failedAttempts, setFailedAttempts] = useState(0)

  // text = what the backend receives, display = what the user sees in chat
  async function handleSend(text, display = text) {
    setMessages((m) => [
      ...m.map((x) => (x.type === "form" ? { ...x, answered: true } : x)),
      { role: "user", text: display },
    ])
    setLoading(true)
    setError("")

    try {
      const result = await sendMessage(text, query, pendingField, confirmed, failedAttempts)
      setFailedAttempts(0)
      
      if (result.status === "needs_clarification") {
        setQuery(result.query)
        setPendingField(result.pending_field)
        setConfirmed(result.confirmed)

        const options = (result.options ?? []).map((o) =>
          typeof o === "string" ? { value: o, label: o } : o
        )

        setMessages((m) => [
          ...m,
          options.length > 0
            ? {
                role: "assistant",
                type: "form",
                question: result.message,
                helper:
                result.pending_field === "confirmation"
                  ? "Choose Yes, or type what needs to change below." : "Select one option, then submit to continue.",
                options,
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
        setConfirmed(false)
      }
    } catch (err) {
      const detail = err.detail
      if (err.status === 422 && detail?.failed_attempts != null) {
        setFailedAttempts(detail.failed_attempts)
        setMessages((m) => [
          ...m,
          detail.options?.length
            ? {
                role: "assistant",
                type: "form",
                question: detail.message,
                helper: "Select one option, or describe the issue in your own words.",
                options: detail.options,
              }
            : { role: "assistant", text: detail.message },
        ])
      } else {
        setError(err.message)
      }
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
          onFormSubmit={(option) => {
            const lastMsg = messages[messages.length - 1]
            if (lastMsg?.type !== "form" || lastMsg.answered) return
            handleSend(option.value, option.label)
          }}
        />
      </main>
    </div>
  )
}

export default App