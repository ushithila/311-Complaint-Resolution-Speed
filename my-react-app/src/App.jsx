import { useState } from 'react'
import './App.css'
import ChatPanel from './components/chat/ChatPanel'
import Sidebar from './components/Sidebar'

function App() {
  return (
    <div className="flex h-screen">
      <Sidebar />
      <ChatPanel />
    </div>
  )
}

export default App
