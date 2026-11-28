import { useState } from "react";
import { Activity, ArrowRight, Bookmark, Database, Eye, EyeOff, Lock, Mail, MessageSquare, ShieldCheck, User } from "lucide-react";

const FEATURES = [
  { icon: MessageSquare, title: "Start your conversations", text: "Get resolution estimates with the prediction assistant." },
  { icon: Bookmark, title: "Keep your predictions together", text: "Save resolution estimates and revisit your analysis." },
  { icon: Activity, title: "Understand the factors", text: "Explore complaint types, borough trends, and service coverage." },
];

function validate({ name, email, password }) {
  const errors = {};
  if (!name.trim()) errors.name = "Enter your full name.";
  if (!/^\S+@\S+\.\S+$/.test(email.trim())) errors.email = "Enter a valid email address.";
  if (password.length < 8 || !/\d/.test(password)) errors.password = "Use at least 8 characters, including a number.";
  return errors;
}

function Field({ id, label, icon: Icon, error, children }) {
  return (
    <div>
      <label htmlFor={id} className="mb-1 block text-[11px] font-semibold uppercase tracking-wide text-slate-500">
        {label}
      </label>
      <div className={`flex items-center gap-2 rounded-lg border bg-white px-3 py-2.5 focus-within:border-brand ${error ? "border-red-400" : "border-slate-300"}`}>
        <Icon size={16} className="text-slate-400" />
        {children}
      </div>
      {error && <p role="alert" className="mt-1 text-xs text-red-600">{error}</p>}
    </div>
  );
}

function CreateAccount({ onCreate, onSignIn }) {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [errors, setErrors] = useState({});

  function submit(e) {
    e.preventDefault();
    const found = validate({ name, email, password });
    setErrors(found);
    if (Object.keys(found).length > 0) return;
    // TODO: replace with a real sign-up call once the auth approach is chosen.
    onCreate?.({ name: name.trim(), email: email.trim() });
  }

  return (
    <div className="flex min-h-0 flex-1 flex-col overflow-y-auto bg-surface">
      <div className="flex items-center justify-between border-b border-slate-200 bg-white px-6 py-3">
        <div>
          <h2 className="text-base font-semibold text-slate-800">Create an account</h2>
          <p className="text-xs text-slate-500">Set up your prediction workspace</p>
        </div>
        <p className="flex items-center gap-1.5 text-xs text-slate-500">
          <ShieldCheck size={14} /> Secure account creation
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
              <h2 className="text-2xl font-bold text-navy">Create your account</h2>
              <p className="mt-1 text-sm text-slate-500">Save your predictions and continue your conversations.</p>
            </div>

            <Field id="name" label="Full name" icon={User} error={errors.name}>
              <input
                id="name"
                type="text"
                autoComplete="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                aria-invalid={Boolean(errors.name)}
                placeholder="Enter your full name"
                className="w-full bg-transparent text-sm outline-none"
              />
            </Field>

            <Field id="email" label="Email address" icon={Mail} error={errors.email}>
              <input
                id="email"
                type="email"
                autoComplete="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                aria-invalid={Boolean(errors.email)}
                placeholder="Enter your email address"
                className="w-full bg-transparent text-sm outline-none"
              />
            </Field>

            <div>
              <Field id="password" label="Password" icon={Lock} error={errors.password}>
                <input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  autoComplete="new-password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  aria-invalid={Boolean(errors.password)}
                  placeholder="Create a password"
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
              <p className="mt-2 text-xs text-slate-500">Use at least 8 characters, including a number.</p>
            </div>

            <button type="submit" className="flex w-full items-center justify-center gap-2 rounded-lg bg-brand py-2.5 text-sm font-semibold text-white">
              Create account <ArrowRight size={16} />
            </button>

            <div className="border-t border-slate-200 pt-4 text-center">
              <p className="mb-2 text-sm text-slate-500">Already have an account?</p>
              <button
                type="button"
                onClick={() => onSignIn?.()}
                className="w-full rounded-lg bg-blue-50 py-2.5 text-sm font-semibold text-brand hover:bg-blue-100"
              >
                Sign in
              </button>
            </div>

            <p className="text-center text-xs text-slate-500">
              By creating an account, you agree to our <button type="button" className="text-brand hover:underline">Terms of use</button> and{" "}
              <button type="button" className="text-brand hover:underline">Privacy policy</button>.
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

export default CreateAccount;