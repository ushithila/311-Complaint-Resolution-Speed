import { ChevronDown } from "lucide-react";

const NAV = ["Prediction chat", "Model insights", "Data sources"];

function Header( { signedIn, onSignIn, activeTab = "Prediction chat", initials = "JD" } ) {
    return (
        <header className="flex items-center justify-between bg-navy px-6 py-3 text-white">
            <div className="flex items-center gap-3">
                <div className="grid h-10 w-10 place-items-center rounded-md bg-brand text-sm font-bold">NYC</div>
                <div>
                <p className="text-[10px] font-medium uppercase tracking-wide text-blue-200">Office of Civic Analytics</p>
                <h1 className="text-lg font-semibold leading-tight">311 Resolution Predictor</h1>
                </div>
            </div>

            <nav className="flex items-center gap-6 text-sm">
                {NAV.map((tab) => (
                <button
                    key={tab}
                    aria-current={tab === activeTab ? "page" : undefined}
                    className={tab === activeTab ? "font-semibold text-white" : "text-blue-200 hover:text-white"}
                >
                    {tab}
                </button>
                ))}

                <span className="flex items-center gap-2 rounded-full bg-white/10 px-3 py-1 text-xs">
                <span className="h-2 w-2 rounded-full bg-emerald-400" /> Model online
                </span>

                {signedIn ? (
                <button aria-label="Account menu" className="flex items-center gap-1">
                    <span className="grid h-8 w-8 place-items-center rounded-full bg-cyan-500 text-xs font-semibold">{initials}</span>
                    <ChevronDown size={14} />
                </button>
                ) : (
                <button onClick={onSignIn} className="rounded-md bg-brand px-4 py-1.5 font-medium text-white">
                    Sign in
                </button>
                )}
            </nav>
        </header>
    )
}

export default Header