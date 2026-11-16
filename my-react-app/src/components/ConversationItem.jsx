// title = name of convo 
// dateTime = when user was active on it 
// active = if user is in the chat
// onClick = if user clicks that specific item

function ConversationItem ( { title, dateTime, active, onClick } ){
    return (
        <li>
        <button
        onClick={onClick}
        aria-current={active ? "true" : undefined}
        className={`w-full rounded-md border px-3 py-2 text-left transition ${
          active ? "border-blue-200 bg-blue-50" : "border-slate-200 bg-white hover:bg-slate-50"
        }`}
      >
        <span className={`block text-sm ${active ? "font-semibold text-navy" : "font-medium"}`}>{title}</span>
        <span className="text-xs text-slate-500">{dateTime}</span>
      </button> 
        </li>
    )
}

export default ConversationItem