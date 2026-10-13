import { useState } from 'react'
import ChatPanel from './components/ChatPanel'
import SideBar from './components/Sidebar'
import './App.css'
import PredictionPanel from './components/PredictionPanel'

function App() {

  return (
    <div>
      <SideBar />
      <ChatPanel />
      <PredictionPanel />
    </div>
  )
}

export default App
