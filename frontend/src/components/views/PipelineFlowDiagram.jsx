import React from "react";
import { 
  Cpu, Bot, Database, Activity, ShieldCheck,
  Server, Globe, ArrowDown, ActivitySquare, Link
} from "lucide-react";

export function PipelineFlowDiagram() {
  return (
    <div className="bg-white dark:bg-[#1A1E27] rounded-3xl border border-slate-200 dark:border-white/[0.08] shadow-card dark:shadow-card-dark p-8">
      <h3 className="text-sm font-bold text-slate-800 dark:text-slate-200 mb-8 flex items-center gap-2 uppercase tracking-wide">
        <ActivitySquare className="w-4 h-4 text-emerald-500" /> Pipeline Flow
      </h3>

      <div className="flex flex-col items-center max-w-sm mx-auto space-y-2 relative">
        {/* Step 1 */}
        <div className="w-full bg-sky-50 dark:bg-sky-950/30 border border-sky-200 dark:border-sky-800/50 rounded-2xl p-4 flex items-center justify-center gap-3 text-sky-800 dark:text-sky-300 shadow-sm relative z-10">
          <Globe className="w-6 h-6" />
          <div className="text-center">
            <div className="font-bold text-sm">Receive Traffic</div>
            <div className="text-[10px] opacity-80">(PCAP / NetFlow / Live Capture)</div>
          </div>
        </div>

        <ArrowDown className="w-5 h-5 text-slate-300 dark:text-slate-600 my-1 animate-pulse" />

        {/* Step 2 */}
        <div className="w-full bg-teal-50 dark:bg-teal-950/30 border border-teal-200 dark:border-teal-800/50 rounded-2xl p-4 flex items-center justify-center gap-3 text-teal-800 dark:text-teal-300 shadow-sm relative z-10">
          <Cpu className="w-6 h-6" />
          <div className="font-bold text-sm">Feature Extractor</div>
        </div>

        <ArrowDown className="w-5 h-5 text-slate-300 dark:text-slate-600 my-1 animate-pulse" />

        {/* Step 3: AI Bots */}
        <div className="w-full p-4 rounded-2xl border border-dashed border-rose-300 dark:border-rose-500/30 bg-rose-50/50 dark:bg-rose-950/10 relative z-10">
          <div className="flex items-center justify-center gap-2 text-rose-600 dark:text-rose-400 font-bold text-sm mb-4">
            <Bot className="w-5 h-5" /> Send Features to AI Bots
          </div>
          <div className="grid grid-cols-2 gap-2">
            {["DDoS Bot", "Beaconing Bot", "DGA DNS Bot", "Encrypted Malware Bot", "Scanning Bot", "Exfiltration Bot"].map(b => (
              <div key={b} className="bg-white dark:bg-[#12151C] border border-rose-100 dark:border-rose-900/50 rounded-xl p-2 flex items-center justify-center gap-1.5 text-[10px] font-semibold text-rose-800 dark:text-rose-200 shadow-sm">
                <Bot className="w-3.5 h-3.5" /> {b}
              </div>
            ))}
          </div>
        </div>

        <ArrowDown className="w-5 h-5 text-slate-300 dark:text-slate-600 my-1 animate-pulse" />

        {/* Step 4: Redis */}
        <div className="w-full bg-rose-50 dark:bg-rose-950/30 border border-rose-200 dark:border-rose-800/50 rounded-2xl p-4 flex items-center justify-center gap-3 text-rose-800 dark:text-rose-300 shadow-sm relative z-10">
          <Database className="w-5 h-5" />
          <div className="font-bold text-sm">Redis Event Bus + Sliding Window</div>
        </div>

        <ArrowDown className="w-5 h-5 text-slate-300 dark:text-slate-600 my-1 animate-pulse" />

        {/* Step 5: Controller */}
        <div className="w-full bg-emerald-50 dark:bg-emerald-950/30 border border-emerald-200 dark:border-emerald-800/50 rounded-2xl p-4 flex items-center justify-center gap-3 text-emerald-800 dark:text-emerald-300 shadow-sm relative z-10">
          <Activity className="w-6 h-6" />
          <div className="text-center">
            <div className="font-bold text-sm">Main Controller</div>
            <div className="text-[10px] opacity-80">(Score Fusion)</div>
          </div>
        </div>

        <div className="flex w-full justify-around mt-1">
          <ArrowDown className="w-5 h-5 text-slate-300 dark:text-slate-600 animate-pulse translate-x-4" />
          <ArrowDown className="w-5 h-5 text-slate-300 dark:text-slate-600 animate-pulse -translate-x-4" />
        </div>

        {/* Step 6: Storage */}
        <div className="w-full grid grid-cols-2 gap-3 relative z-10">
          <div className="bg-emerald-50/50 dark:bg-emerald-950/20 border border-emerald-200 dark:border-emerald-800/40 rounded-2xl p-3 flex flex-col items-center justify-center gap-1.5 text-emerald-800 dark:text-emerald-400 text-center">
            <Database className="w-5 h-5" />
            <div className="text-[10px] font-bold">Save Alert in PostgreSQL</div>
          </div>
          <div className="bg-emerald-50/50 dark:bg-emerald-950/20 border border-emerald-200 dark:border-emerald-800/40 rounded-2xl p-3 flex flex-col items-center justify-center gap-1.5 text-emerald-800 dark:text-emerald-400 text-center">
            <Link className="w-5 h-5" />
            <div className="text-[10px] font-bold">Log Alert Hash on Blockchain</div>
          </div>
        </div>

        <ArrowDown className="w-5 h-5 text-slate-300 dark:text-slate-600 my-1 animate-pulse" />

        {/* Step 7: Dashboard */}
        <div className="w-full bg-emerald-50 dark:bg-emerald-950/30 border border-emerald-200 dark:border-emerald-800/50 rounded-2xl p-4 flex items-center justify-center gap-3 text-emerald-800 dark:text-emerald-300 shadow-sm relative z-10">
          <Server className="w-6 h-6" />
          <div className="font-bold text-sm">Push Live Alert to Dashboard</div>
        </div>
        
        <ArrowDown className="w-5 h-5 text-slate-300 dark:text-slate-600 my-1 animate-pulse" />

        <div className="w-full bg-emerald-50 dark:bg-emerald-950/30 border border-emerald-200 dark:border-emerald-800/50 rounded-2xl p-4 flex items-center justify-center gap-3 text-emerald-800 dark:text-emerald-300 shadow-sm relative z-10">
          <ShieldCheck className="w-6 h-6" />
          <div className="text-center">
            <div className="font-bold text-sm">Security Analyst</div>
            <div className="text-[10px] opacity-80">Views Alert + Evidence</div>
          </div>
        </div>

        {/* Ambient Background Line */}
        <div className="absolute top-0 bottom-0 left-1/2 w-0.5 bg-slate-100 dark:bg-slate-800 -translate-x-1/2 z-0" />
      </div>
    </div>
  );
}
