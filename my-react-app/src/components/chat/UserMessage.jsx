import { MapPin } from "lucide-react"

function UserMessage ({message, time, location}){
  return ( 
    <div className="flex flex-col items-end">
      <p className="mb-1 text-xs text-slate-500">You{time && ` · ${time}`}</p>
      <div className="max-w-[75%] rounded-xl bg-brand px-4 py-3 text-sm text-white">
        <p>{text}</p>
        {location && (
          <p className="mt-2 flex items-center gap-2 rounded-md bg-white/15 px-3 py-1.5 text-xs">
            <MapPin size={12} /> {location}
          </p>
        )}
      </div>
    </div>
  )
}

export default UserMessage