import { useState } from "react";
import { Database, Plus, Search } from "lucide-react";
import ConversationItem from "./ConversationItem";

function SideBar( { conversations = [], activeId, onSelect, onNew } ){
  // conversation items render here once we have data, pass conversations from app.jsx to here

  const [query, setQuery] = useState("");
  const [selectedId, setSelectedId] = useState(activeId ?? conversations[0]?.id);

  const visible = conversations.filter((c) => c.title.toLowerCase().includes(query.trim().toLowerCase()));

  function select(id) {
    setSelectedId(id);
    onSelect?.(id);
  }

  return ( 
    <aside className="hidden w-60 shrink-0 flex-col border-r border-slate-200 bg-white md:flex">
      <div className="space-y-3 p-4">
        <button onClick={onNew} className="flex w-full items-center justify-center gap-2 rounded-md bg-brand py-2 text-sm font-medium text-white">
          <Plus size={16} /> New prediction
        </button>
        <label className="flex items-center gap-2 rounded-md border border-slate-300 px-3 py-2 focus-within:border-brand">
          <Search size={14} className="text-slate-400" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search conversations"
            aria-label="Search conversations"
            className="w-full bg-transparent text-sm outline-none"
          />
        </label>
      </div>

      <div className="flex-1 overflow-y-auto px-4">
        <p className="mb-2 text-[10px] font-semibold uppercase tracking-wide text-slate-500">Recent conversations</p>
        {visible.length === 0 ? (
          <p className="text-sm text-slate-500">No conversations found.</p>
        ) : (
          <ul className="space-y-2">
            {visible.map((c) => (
              <ConversationItem key={c.id} {...c} active={c.id === selectedId} onClick={() => select(c.id)} />
            ))}
          </ul>
        )}
      </div>

      <div className="flex items-center gap-2 border-t border-slate-200 p-4 text-xs text-slate-500">
        <Database size={14} />
        <div>
          <p className="font-medium text-slate-600">NYC Open Data</p>
          <p>Updated daily</p>
        </div>
      </div>
    </aside>
  )
}

export default SideBar