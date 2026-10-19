import { Sparkles } from "lucide-react";
import { Avatar } from "./AssistantMessage"  

function PredictionCard({ text, time }) {
  return (
    <div className="flex gap-3">
      <Avatar />
      <div className="max-w-[75%]">
        <p className="mb-1 text-xs text-slate-500">
          NYC 311 Prediction Assistant{time && ` · ${time}`}
        </p>
        <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
          <h3 className="mb-2 flex items-center gap-2 text-sm font-semibold">
            <Sparkles size={14} className="text-brand" /> Prediction complete
          </h3>
          <p className="text-sm">{text}</p>
          <p className="mt-3 border-t border-slate-200 pt-2 text-xs text-slate-500">
            This is an estimate based on historical 311 outcomes, not an official service commitment.
          </p>
        </div>
      </div>
    </div>
  );
}
 
export default PredictionCard