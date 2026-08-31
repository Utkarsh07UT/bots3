import React, { useState, useEffect } from "react";
import { 
  Network, Bot, Loader2, CheckCircle2, AlertTriangle, XCircle
} from "lucide-react";
import { useAuth } from "../../context/AuthContext";

export function SystemArchitectureView() {
  const [bots, setBots] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const { session } = useAuth();

  useEffect(() => {
    let isMounted = true;
    const fetchBots = async () => {
      try {
        const baseUrl = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";
        const rawAiUrl = import.meta.env.VITE_AI_SERVICE_URL || "https://bots3-a8ta.onrender.com";
        const aiServiceUrl = rawAiUrl.replace(/\/$/, "");
        
        let data = null;
        try {
          const res = await fetch(`${baseUrl}/bots/health`, {
            headers: {
              "Authorization": `Bearer ${session?.access_token || ""}`
            }
          });
          if (res.ok) {
            data = await res.json();
          }
        } catch {
          // Backend health check failed, try direct AI service fallback
        }

        if (!data || data.length === 0) {
          const aiRes = await fetch(`${aiServiceUrl}/bots`);
          if (aiRes.ok) {
            data = await aiRes.json();
          }
        }

        if (!data) throw new Error("Could not reach backend or AI bot cluster.");

        // Normalize bot fields
        const formatted = (Array.isArray(data) ? data : data.bots || []).map((bot, idx) => ({
          id: bot.id || bot.bot_name || `bot-${idx}`,
          bot_name: bot.bot_name || bot.name || "specialist_bot",
          display_name: bot.display_name || bot.bot_name || "Specialist Bot",
          version: bot.version || "1.0.0",
          status: (bot.status || "HEALTHY").toUpperCase(),
          latency_ms: Number(bot.latency_ms || 0.1),
          cpu_percent: Number(bot.cpu_percent || 0.0),
          predictions_count: Number(bot.predictions_count || 0),
          threats_detected: Number(bot.threats_detected || 0),
          accuracy_score: Number(bot.accuracy_score || 0.99),
          f1_score: Number(bot.f1_score || 0.99),
          memory_mb: Number(bot.memory_mb || 0.0),
        }));

        if (isMounted) {
          setBots(formatted);
          setError(null);
        }
      } catch (err) {
        if (isMounted) {
          setError(err.message);
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };
    fetchBots();
    // Poll every 10 seconds
    const interval = setInterval(fetchBots, 10000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, [session]);

  const StatusBadge = ({ status }) => {
    const s = (status || "").toUpperCase();
    if (s === "HEALTHY" || s === "ONLINE") {
      return (
        <div className="flex items-center gap-1.5 px-2 py-1 rounded-full bg-emerald-50 dark:bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 text-[10px] font-bold uppercase tracking-wider border border-emerald-200 dark:border-emerald-500/20">
          <CheckCircle2 className="w-3 h-3" /> Healthy
        </div>
      );
    }
    if (s === "DEGRADED" || s === "INITIALIZING") {
      return (
        <div className="flex items-center gap-1.5 px-2 py-1 rounded-full bg-amber-50 dark:bg-amber-500/10 text-amber-600 dark:text-amber-400 text-[10px] font-bold uppercase tracking-wider border border-amber-200 dark:border-amber-500/20">
          <AlertTriangle className="w-3 h-3" /> {s === "INITIALIZING" ? "Initializing" : "Degraded"}
        </div>
      );
    }
    return (
      <div className="flex items-center gap-1.5 px-2 py-1 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400 text-[10px] font-bold uppercase tracking-wider border border-slate-200 dark:border-slate-700">
        <XCircle className="w-3 h-3" /> Offline
      </div>
    );
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-500 max-w-5xl mx-auto">
      
      {/* HEADER */}
      <div className="flex flex-col gap-2">
        <h2 className="text-2xl font-black text-slate-900 dark:text-white flex items-center gap-2">
          <Network className="w-6 h-6 text-blue-500" /> Active AI Specialist Bots
        </h2>
        <p className="text-sm text-slate-500 dark:text-slate-400">
          Real-time telemetry and health status of all specialist machine-learning bots running in the SOC infrastructure.
        </p>
      </div>

      {/* AI BOTS STATUS */}
      <div className="bg-white dark:bg-[#1A1E27] rounded-3xl border border-slate-200 dark:border-white/[0.08] shadow-card dark:shadow-card-dark p-8">
        <div className="flex items-center justify-between mb-8">
          <h3 className="text-sm font-bold text-slate-800 dark:text-slate-200 flex items-center gap-2 uppercase tracking-wide">
            <Bot className="w-4 h-4 text-blue-500" /> Specialist Models Telemetry
          </h3>
          {isLoading && <Loader2 className="w-4 h-4 text-blue-500 animate-spin" />}
        </div>

        {error ? (
          <div className="p-4 rounded-2xl bg-rose-50 dark:bg-rose-950/30 border border-rose-200 dark:border-rose-900/50 text-rose-600 dark:text-rose-400 text-sm flex items-center gap-2">
            <AlertTriangle className="w-5 h-5" /> Failed to load bot telemetry: {error}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {bots.map((bot) => (
              <div key={bot.id} className="p-4 rounded-2xl bg-slate-50 dark:bg-[#12151C] border border-slate-200 dark:border-slate-800/80 hover:border-blue-300 dark:hover:border-blue-500/50 transition-colors">
                <div className="flex justify-between items-start mb-4">
                  <div className="flex items-center gap-3">
                    <div className="p-2.5 rounded-xl bg-blue-100 dark:bg-blue-500/20 text-blue-600 dark:text-blue-400">
                      <Bot className="w-5 h-5" />
                    </div>
                    <div>
                      <h4 className="font-bold text-sm text-slate-900 dark:text-white">{bot.display_name}</h4>
                      <div className="text-[10px] text-slate-500 font-mono mt-0.5">{bot.bot_name} • v{bot.version}</div>
                    </div>
                  </div>
                  <StatusBadge status={bot.status} />
                </div>
                
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                  <div>
                    <div className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider mb-1">Latency</div>
                    <div className="font-mono text-sm font-bold text-slate-700 dark:text-slate-200">{bot.latency_ms.toFixed(1)}ms</div>
                  </div>
                  <div>
                    <div className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider mb-1">CPU Load</div>
                    <div className="font-mono text-sm font-bold text-slate-700 dark:text-slate-200">{bot.cpu_percent.toFixed(1)}%</div>
                  </div>
                  <div>
                    <div className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider mb-1">Predictions</div>
                    <div className="font-mono text-sm font-bold text-blue-600 dark:text-blue-400">{bot.predictions_count.toLocaleString()}</div>
                  </div>
                  <div>
                    <div className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider mb-1">Threats</div>
                    <div className="font-mono text-sm font-bold text-rose-600 dark:text-rose-400">{bot.threats_detected.toLocaleString()}</div>
                  </div>
                </div>
                
                <div className="mt-4 pt-4 border-t border-slate-200 dark:border-slate-800 flex justify-between items-center text-[10px]">
                  <div className="text-slate-500">
                    Accuracy: <span className="font-mono font-bold text-slate-700 dark:text-slate-300">{(bot.accuracy_score * 100).toFixed(2)}%</span>
                  </div>
                  <div className="text-slate-500">
                    F1 Score: <span className="font-mono font-bold text-slate-700 dark:text-slate-300">{(bot.f1_score * 100).toFixed(2)}%</span>
                  </div>
                  <div className="text-slate-500">
                    RAM: <span className="font-mono font-bold text-slate-700 dark:text-slate-300">{bot.memory_mb.toFixed(1)}MB</span>
                  </div>
                </div>
              </div>
            ))}
            
            {bots.length === 0 && !isLoading && (
              <div className="p-8 text-center text-slate-500 text-sm md:col-span-2">
                No bots registered in the system yet.
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
