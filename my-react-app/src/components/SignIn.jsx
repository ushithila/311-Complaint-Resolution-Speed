import { useState } from "react";
import { ArrowRight, Bookmark, Activity, Database, Eye, EyeOff, Lock, Mail, MessageSquare, ShieldCheck, User } from "lucide-react";

const FEATURES = [
  { icon: MessageSquare, title: "Continue your conversations", text: "Pick up where you left off with the prediction assistant." },
  { icon: Bookmark, title: "Keep your predictions together", text: "Save resolution estimates and revisit your analysis." },
  { icon: Activity, title: "Understand the factors", text: "Explore complaint types, borough trends, and service coverage." },
];

function Field({ id, label, icon: Icon, children }) {
  return (
    <div>
      <label htmlFor={id} className="mb-1 block text-[11px] font-semibold uppercase tracking-wide text-slate-500">
        {label}
      </label>
      <div className="flex items-center gap-2 rounded-lg border border-slate-300 bg-white px-3 py-2.5 focus-within:border-brand">
        <Icon size={16} className="text-slate-400" />
        {children}
      </div>
    </div>
  );
}

function SignIn({ onSignIn, onGuest, onCreateAccount }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [remember, setRemember] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");

  function submit(e) {
    e.preventDefault();
    if (!email.trim() || !password) {
      setError("Enter your email and password.");
      return;
    }
    setError("");
    // TODO: replace with a real auth call once the sign-in approach is chosen.
    onSignIn?.({ email: email.trim(), remember });
  }

  return (
    <div className="flex min-h-0 flex-1 flex-col overflow-y-auto bg-surface">
      <div className="flex items-center justify-between border-b border-slate-200 bg-white px-6 py-3">
        <div>
          <h2 className="text-base font-semibold text-slate-800">Account access</h2>
          <p className="text-xs text-slate-500">Sign in to your prediction workspace</p>
        </div>
        <p className="flex items-center gap-1.5 text-xs text-slate-500">
          <ShieldCheck size={14} /> Secure account access
        </p>
      </div>

      <main className="grid flex-1 place-items-center px-6 py-10">
        <div className="grid w-full max-w-5xl items-center gap-16 md:grid-cols-2">
          <section className="hidden md:block">
            <p className="text-[11px] font-semibold uppercase tracking-wide text-brand">NYC 311 · Civic Analytics</p>
            <h2 className="mt-3 text-3xl font-bold text-navy">Your city. Clearer expectations.</h2>
            <p className="mt-3 max-w-sm text-sm text-slate-600">
              Use historical NYC 311 data to understand how quickly a service request may be resolved.
            </p>
            <ul className="mt-6 space-y-4">
              {FEATURES.map(({ icon: Icon, title, text }) => (
                <li key={title} className="flex items-start gap-3">
                  <span className="grid h-8 w-8 shrink-0 place-items-center rounded-md bg-blue-50 text-brand">
                    <Icon size={16} />
                  </span>
                  <div>
                    <p className="text-sm font-semibold text-slate-800">{title}</p>
                    <p className="text-xs text-slate-500">{text}</p>
                  </div>
                </li>
              ))}
            </ul>
            <div className="mt-6 flex items-start gap-3 rounded-lg border border-blue-200 bg-blue-50 p-3">
              <Database size={16} className="mt-0.5 text-brand" />
              <div>
                <p className="text-sm font-semibold text-brand">Powered by NYC Open Data</p>
                <p className="text-xs text-slate-500">Updated daily · Estimates, not official service commitments.</p>
              </div>
            </div>
          </section>

          <form onSubmit={submit} noValidate className="space-y-4 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <span className="grid h-10 w-10 place-items-center rounded-lg bg-blue-50 text-brand">
              <User size={18} />
            </span>
            <div>
              <h2 className="text-2xl font-bold text-navy">Sign in</h2>
              <p className="mt-1 text-sm text-slate-500">Welcome back to NYC 311 Resolution Predictor.</p>
            </div>

            <Field id="email" label="Email address" icon={Mail}>
              <input
                id="email"
                type="email"
                autoComplete="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Enter your email address"
                className="w-full bg-transparent text-sm outline-none"
              />
            </Field>

            <Field id="password" label="Password" icon={Lock}>
              <input
                id="password"
                type={showPassword ? "text" : "password"}
                autoComplete="current-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
                className="w-full bg-transparent text-sm outline-none"
              />
              <button
                type="button"
                aria-label={showPassword ? "Hide password" : "Show password"}
                onClick={() => setShowPassword((s) => !s)}
                className="text-slate-400 hover:text-slate-600"
              >
                {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </Field>

            <div className="flex items-center justify-between text-sm">
              <label className="flex items-center gap-2 text-slate-600">
                <input type="checkbox" checked={remember} onChange={(e) => setRemember(e.target.checked)} className="accent-brand" />
                Remember me
              </label>
              <button type="button" className="font-medium text-brand hover:underline">Forgot password?</button>
            </div>

            {error && <p role="alert" className="text-sm text-red-600">{error}</p>}

            <button type="submit" className="flex w-full items-center justify-center gap-2 rounded-lg bg-brand py-2.5 text-sm font-semibold text-white transition-colors duration-200 ease-in-out hover:bg-navy cursor-pointer">
              Sign in <ArrowRight size={16} />
            </button>

            <div className="flex items-center gap-3 text-xs text-slate-400">
              <span className="h-px flex-1 bg-slate-200" /> or <span className="h-px flex-1 bg-slate-200" />
            </div>

            <button
              type="button"
              onClick={() => onGuest?.()}
              className="w-full rounded-lg border border-slate-300 bg-white py-2.5 text-sm font-semibold text-slate-700 hover:bg-slate-50 cursor-pointer"
            >
              Continue as guest
            </button>

            <div className="border-t border-slate-200 pt-4 text-center">
              <p className="mb-2 text-sm text-slate-500">New to the predictor?</p>
              <button
                type="button"
                onClick={() => onCreateAccount?.()}
                className="w-full rounded-lg bg-blue-50 py-2.5 text-sm font-semibold text-brand hover:bg-blue-100 cursor-pointer"
              >
                Create an account
              </button>
            </div>

            <p className="text-center text-xs text-slate-500">
              By signing in, you agree to our <button type="button" className="text-brand hover:underline">Terms of use</button> and{" "}
              <button type="button" className="text-brand hover:underline cursor-pointer">Privacy policy</button>.
            </p>
          </form>
        </div>
      </main>

      <footer className="flex items-center justify-between border-t border-slate-200 bg-white px-6 py-3 text-xs text-slate-500">
        <div>
          <p className="font-medium text-slate-600">Office of Civic Analytics · NYC 311 Resolution Predictor</p>
          <p>For analysis only. To submit an official service request, visit NYC 311.</p>
        </div>
        <div className="flex gap-6 font-medium text-brand">
          <button type="button">Help &amp; support</button>
          <button type="button">NYC 311</button>
        </div>
      </footer>
    </div>
  );
}

export default SignIn;