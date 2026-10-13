// main chat feature
import { useState } from "react"
import ChatHeader from "./ChatHeader"
import MessageHistory from "./MessageHistory"
import UserMessage from "./UserMessage"

function ChatPanel(){
  return (
    <>
    <ChatHeader />
    <MessageHistory />
    <UserMessage />
    </>
  )
}

export default ChatPanel
