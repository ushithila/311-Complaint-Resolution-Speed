export function Avatar() {
  return (
    <div className="grid h-8 w-8 shrink-0 place-items-center rounded-full bg-navy text-[10px] font-bold text-white">
      311
    </div>
  )
}

function AssistantMessage( { text, time, chips = [], onChipClick } ){
  return (
    <div className="flex gap-3">
      <Avatar />
      <div className="max-w-[75%]">
        <p className="mb-1 text-xs text-slate-500">
          NYC 311 Prediction Assistant{time && ` · ${time}`}
        </p>
        <div className="rounded-xl bg-slate-100 px-4 py-3 text-sm">
          <p>{text}</p>
          {chips.length > 0 && (
            <p className="mt-2 flex flex-wrap items-center gap-2 text-xs">
              <span className="text-slate-500">Try:</span>
              {chips.map((chip) => (
                <button key={chip} onClick={() => onChipClick?.(chip)} className="font-medium text-brand hover:underline">
                  {chip}
                </button>
              ))}
            </p>
          )}
        </div>
      </div>
    </div>
  )
}

export default AssistantMessage