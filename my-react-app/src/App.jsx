import { useState } from 'react'
import './App.css'
import ChatPanel from './components/chat/ChatPanel'
import Sidebar from './components/Sidebar'
import Header from './components/Header'

function App() {
  return (
    <div className="flex h-screen flex-col">
      <Header />
      <main className="flex min-h-0 flex-1">
        <Sidebar />
        <ChatPanel />
      </main>
    </div>
  )
}

export default App
