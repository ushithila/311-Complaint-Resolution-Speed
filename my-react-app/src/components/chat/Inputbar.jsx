import { ArrowUp, MapPin, Paperclip } from "lucide-react";

function InputBar( { value, onChange, onSend, disabled } ){
    return (
        <div className="mt-auto border-t border-slate-200 p-4">
            <div className="flex items-center gap-2 rounded-lg border border-slate-300 px-3 py-2 focus-within:border-brand">
                <button aria-label="Attach a photo" className="text-slate-500"><Paperclip size={16} /></button>
                <button aria-label="Add a location" className="text-slate-500"><MapPin size={16} /></button>
                <input
                value={value}
                onChange={(e) => onChange(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && onSend()}
                placeholder="Add details or ask a follow-up…"
                className="flex-1 bg-transparent text-sm outline-none"
                />
                <button
                aria-label="Send message"
                onClick={onSend}
                disabled={disabled || !value.trim()}
                className="grid h-8 w-8 place-items-center rounded-md bg-brand text-white disabled:opacity-40"
                >
                <ArrowUp size={16} />
                </button>
            </div>
            <p className="mt-1 text-xs text-slate-500">Enter to send · Attach a photo or location to improve the prediction</p>
        </div>
    )
}

export default InputBar