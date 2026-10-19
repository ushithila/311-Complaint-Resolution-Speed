import { useEffect, useRef } from "react";
import AssistantMessage from "./AssistantMessage";
import UserMessage from "./UserMessage";
import PredictionCard from "./PredictionCard";

const INTRO = {
    text: "Describe the issue and where it occurred. I'll estimate how quickly a similar 311 complaint is likely to be resolved.",
    chips: ["street condition", "noise", "sanitation"],
}

function renderMessage(message, onChipClick) {
    if (message.role === "user") return <UserMessage {...message} />
    if (message.type === "prediction") return <PredictionCard {...message} />
    return <AssistantMessage {...message} onChipClick={onChipClick} />
}

function MessageHistory( { messages = [], loading, error, onChipClick } ){
    const endRef = useRef(null)

    useEffect(() => {
        endRef.current?.scrollIntoView?.({ behavior: "smooth" });
    }, [messages, loading])

    return (
        <div role="log" aria-live="polite" className="flex-1 space-y-5 overflow-y-auto p-6">
            {messages.length === 0 && <AssistantMessage {...INTRO} onChipClick={onChipClick} />}
            {messages.map((m, i) => (
                <div key={m.id ?? i}>{renderMessage(m, onChipClick)}</div>
            ))}
            {loading && <p className="text-sm text-slate-500">Estimating resolution time…</p>}
            {error && <p role="alert" className="text-sm text-red-600">{error}</p>}
            <div ref={endRef} />
        </div>
    )
}

export default MessageHistory