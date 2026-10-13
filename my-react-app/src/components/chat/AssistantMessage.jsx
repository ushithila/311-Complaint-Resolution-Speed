function AssistantMessage( { text, time, info = [], onInfoClick } ){
  return (
    <div className="flex gap-3">
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