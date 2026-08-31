import React, { useMemo, useState } from "react";
import { AlertTriangle, Search, User, Link as LinkIcon, ShieldCheck } from "lucide-react";
import { logAlertToBlockchain, verifyAlertOnBlockchain } from "../../api/backend";

export function IncidentsView({ onBackToOverview, items = [] }) {
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("All");
  const incidents = useMemo(() => items.filter((incident) => {
    const search = searchTerm.toLowerCase();
    const matchesSearch = !search || [incident.id, incident.title, incident.source, incident.destination].filter(Boolean).some((value) => value.toLowerCase().includes(search));
    return matchesSearch && (statusFilter === "All" || incident.status === statusFilter);
  }), [items, searchTerm, statusFilter]);

  return <div className="space-y-6">
    <div className="flex flex-col gap-4 rounded-2xl border border-slate-200/80 bg-white p-5 shadow-card dark:border-white/[0.08] dark:bg-[#1A1E27] sm:flex-row sm:items-center sm:justify-between">
      <div className="flex items-center gap-3"><div className="rounded-xl bg-rose-50 p-2.5 text-rose-600 dark:bg-rose-950/60"><AlertTriangle className="h-6 w-6" /></div><div><h2 className="text-lg font-bold text-slate-900 dark:text-slate-100">Live security incidents</h2><p className="text-xs text-slate-500">Alerts loaded from Supabase telemetry.</p></div></div>
      <button onClick={onBackToOverview} className="rounded-xl bg-slate-100 px-4 py-2 text-xs font-semibold dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors">← Return to Overview</button>
    </div>
    <div className="flex flex-wrap gap-3 rounded-2xl border border-slate-200/80 bg-white p-4 dark:border-white/[0.08] dark:bg-[#1A1E27]"><div className="relative flex-1"><Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" /><input value={searchTerm} onChange={(event) => setSearchTerm(event.target.value)} placeholder="Search alert, source, or target" className="w-full rounded-xl border border-slate-200 py-2 pl-9 pr-3 text-xs bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-slate-700" /></div>{["All", "NEW", "INVESTIGATING", "RESOLVED", "FALSE_POSITIVE"].map((status) => <button key={status} onClick={() => setStatusFilter(status)} className={`rounded-lg px-3 py-1 text-xs font-semibold ${statusFilter === status ? "bg-blue-600 text-white" : "bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors"}`}>{status}</button>)}</div>
    <div className="overflow-hidden rounded-2xl border border-slate-200/80 bg-white shadow-card dark:border-white/[0.08] dark:bg-[#1A1E27]">{incidents.length ? incidents.map((incident) => <div key={incident.id} className="flex flex-col justify-between gap-3 border-b border-slate-100 p-5 last:border-0 md:flex-row md:items-center dark:border-slate-800"><div><div className="flex gap-2 text-xs"><span className="font-mono font-bold text-blue-600">{incident.id}</span><span className="font-bold text-slate-900 dark:text-slate-200">{incident.severity}</span><span className="text-slate-500">{incident.status}</span></div><h3 className="mt-1 text-sm font-bold text-slate-900 dark:text-slate-100">{incident.title}</h3><p className="mt-1 text-xs text-slate-500">{incident.source} → {incident.destination} · {incident.attackType}</p></div><div className="flex items-center gap-3"><div className="flex items-center gap-1 text-xs text-slate-500"><User className="h-3.5 w-3.5" /> Supabase · {incident.timestamp}</div><BlockchainActions alertId={incident.id} isVerified={incident.raw?.blockchain_verified} txHash={incident.raw?.blockchain_tx_hash} /></div></div>) : <p className="p-10 text-center text-sm text-slate-500">No live incidents match this filter.</p>}</div>
  </div>;
}

function BlockchainActions({ alertId, isVerified, txHash }) {
  const [loading, setLoading] = useState(false);
  const [verified, setVerified] = useState(isVerified);
  const [hash, setHash] = useState(txHash);
  
  const handleLog = async () => {
    setLoading(true);
    try {
      const res = await logAlertToBlockchain(alertId);
      if (res.status === "success" || res.status === "already_logged") {
        setVerified(true);
        setHash(res.tx_hash);
      }
    } catch (err) {
      console.error(err);
      alert("Failed to log to blockchain");
    } finally {
      setLoading(false);
    }
  };

  const handleVerify = async () => {
    setLoading(true);
    try {
      const res = await verifyAlertOnBlockchain(alertId);
      if (res.on_chain_verified) {
        alert("Alert verified on blockchain!");
      } else {
        alert("Alert could not be verified on chain.");
      }
    } catch (err) {
      console.error(err);
      alert("Failed to verify on blockchain");
    } finally {
      setLoading(false);
    }
  };

  if (verified) {
    return (
      <button onClick={handleVerify} disabled={loading} className="flex items-center gap-1 rounded-lg bg-emerald-50 px-2 py-1 text-xs font-semibold text-emerald-600 dark:bg-emerald-950/60 dark:text-emerald-400 hover:bg-emerald-100 transition-colors" title={`TxHash: ${hash}`}>
        <ShieldCheck className="h-3.5 w-3.5" />
        {loading ? "..." : "Verified"}
      </button>
    );
  }

  return (
    <button onClick={handleLog} disabled={loading} className="flex items-center gap-1 rounded-lg bg-blue-50 px-2 py-1 text-xs font-semibold text-blue-600 dark:bg-blue-950/60 dark:text-blue-400 hover:bg-blue-100 transition-colors">
      <LinkIcon className="h-3.5 w-3.5" />
      {loading ? "..." : "Log to Chain"}
    </button>
  );
}
