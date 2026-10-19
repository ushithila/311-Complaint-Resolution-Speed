// main chat feature
import { useState } from "react"
import ChatHeader from "./ChatHeader"
import MessageHistory from "./MessageHistory"
import InputBar from "./Inputbar"

function ChatPanel( { messages = [], loading = false, error = "", onSend, title, subtitle }){
  const [draft, setDraft] = useState("")

  function send() {
    const text = draft.trim()
    if (!text || loading) return
    setDraft("")
    onSend?.(text)
  }

  return (
    <section className="flex min-h-0 min-w-0 flex-1 flex-col bg-white">
      <ChatHeader title={title} subtitle={subtitle} />
      <MessageHistory messages={messages} loading={loading} error={error} onInfoClick={setDraft} />
      <InputBar value={draft} onChange={setDraft} onSend={send} disabled={loading} />
    </section>
  )
}

export default ChatPanel
