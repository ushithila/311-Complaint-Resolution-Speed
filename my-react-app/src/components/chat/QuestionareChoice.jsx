import { useState } from "react";
import { Avatar } from "./AssistantMessage";

function Questionare( { id = "choice", question, helper, options = [], time, answer = null, onSubmit } ) {
      const [selected, setSelected] = useState(answer)
  const [locked, setLocked] = useState(answer !== null)
 
  function submit(e) {
    e.preventDefault()
    if (selected === null || locked) return
    setLocked(true)
    onSubmit?.(options.find((o) => o.value === selected))
  }
 
  return (
    <div className="flex gap-3">
      <Avatar />
      <div className="w-full max-w-lg">
        <p className="mb-1 text-xs text-slate-500">
          NYC 311 Prediction Assistant{time && ` · ${time}`}
        </p>
        <form onSubmit={submit} className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
          <fieldset disabled={locked}>
            <legend className="text-sm font-semibold">{question}</legend>
            {helper && <p className="mt-1 text-xs text-slate-500">{helper}</p>}
            <div className="mt-3 grid grid-cols-1 gap-2 sm:grid-cols-2">
              {options.map((opt) => (
                <label
                  key={opt.value}
                  className="flex cursor-pointer items-center gap-2 rounded-md border border-slate-200 px-3 py-2 text-sm has-[:checked]:border-brand has-[:checked]:bg-blue-50 has-[:checked]:font-medium has-[:focus-visible]:ring-2 has-[:focus-visible]:ring-brand/40"
                >
                  <input
                    type="radio"
                    name={id}
                    value={opt.value}
                    checked={selected === opt.value}
                    onChange={() => setSelected(opt.value)}
                    className="accent-brand"
                  />
                  {opt.label}
                </label>
              ))}
            </div>
          </fieldset>
          <div className="mt-3 flex items-center justify-between">
            <span className="text-xs text-slate-500">
              {selected === null ? "No option selected" : "One option selected"}
            </span>
            <button
              type="submit"
              disabled={selected === null || locked}
              className="rounded-md bg-brand px-5 py-2 text-sm font-medium text-white disabled:opacity-40"
            >
              Submit
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default Questionare