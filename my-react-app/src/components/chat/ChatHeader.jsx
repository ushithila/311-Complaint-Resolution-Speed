import { Download, MoreHorizontal } from "lucide-react";
 
function ChatHeader({ title = "New prediction", subtitle = "Describe a 311 complaint" }) {
  return (
    <div className="flex items-center justify-between border-b border-slate-200 px-6 py-3">
      <div>
        <h2 className="text-sm font-semibold">{title}</h2>
        <p className="text-xs text-slate-500">{subtitle}</p>
      </div>
      <div className="flex gap-3 text-slate-500">
        <button aria-label="Download conversation"><Download size={16} /></button>
        <button aria-label="More options"><MoreHorizontal size={16} /></button>
      </div>
    </div>
  );
}

export default ChatHeader