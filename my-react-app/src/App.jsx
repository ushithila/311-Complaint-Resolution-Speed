import { useState } from 'react'
import ChatPanel from './components/chat/ChatPanel'
import Sidebar from './components/Sidebar'
import Header from './components/Header'
import { sendMessage } from './api'

//testing mock, remove 
import { chatMessages } from './mocks/MockMessages'

function App() {  
  const [messages, setMessages] = useState(chatMessages)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  async function handleSend(text) {
    setMessages((m) => [...m, { role: "user", text }])
    setLoading(true)
    setError("")
    try {
      const { reply } = await sendMessage(text)
      setMessages((m) => [...m, { role: "assistant", type: "prediction", text: reply }])
    } catch {
      setError("Couldn't get a prediction. Try again.")
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