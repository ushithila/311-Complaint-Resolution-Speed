import { useState } from 'react'
import './App.css'
import ChatPanel from './components/chat/ChatPanel'
import SideBar from './components/Sidebar'

function App() {
  return (
    <>
    <SideBar />
    <ChatPanel />
    </>
  )
}

export default App
