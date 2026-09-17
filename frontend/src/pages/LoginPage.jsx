import { Shield } from "lucide-react";
import { useState } from "react";
import { useAuth } from "../context/AuthContext";

export function LoginPage() {
  const { signInWithOAuth } = useAuth();
  const [error, setError] = useState("");
  const [pending, setPending] = useState(false);
  const signIn = async () => {
    setPending(true); setError("");
    const result = await signInWithOAuth("google");
    if (result.error) { setError(result.error.message || "Google sign-in could not be started."); setPending(false); }
  };
  return <main className="grid min-h-screen place-items-center bg-[#090d14] p-6 text-slate-100">
    <section className="w-full max-w-sm rounded-xl border border-slate-800 bg-[#101620] p-8 shadow-2xl shadow-black/30">
      <div className="mb-8 text-center"><div className="mx-auto mb-4 grid h-11 w-11 place-items-center rounded-lg border border-sky-400/30 bg-sky-400/10 text-sky-300"><Shield size={22} /></div><h1 className="text-xl font-semibold tracking-tight">UniThreat</h1><p className="mt-2 text-sm text-slate-400">Security operations console</p></div>
      {error && <p className="mb-4 rounded-md border border-red-900/70 bg-red-950/30 px-3 py-2 text-xs text-red-300">{error}</p>}
      <button onClick={signIn} disabled={pending} className="flex w-full items-center justify-center gap-3 rounded-md border border-slate-700 bg-slate-50 px-4 py-2.5 text-sm font-medium text-slate-900 transition hover:bg-white disabled:cursor-wait disabled:opacity-70"><span className="grid h-4 w-4 place-items-center rounded-full bg-white text-xs font-bold text-[#4285f4]">G</span>{pending ? "Opening Google…" : "Continue with Google"}</button>
      <p className="mt-8 text-center text-xs text-slate-500">Authorized access only</p>
    </section>
  </main>;
}
