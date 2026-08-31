import React, { useEffect, useState } from "react";
import { getMode, switchMode } from "../../api/backend";

export const ModeToggle = () => {
  const [mode, setMode] = useState("live");
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    getMode()
      .then((res) => setMode(res.current_mode))
      .catch((err) => console.error("Failed to fetch mode", err));
  }, []);

  const handleToggle = async () => {
    setIsLoading(true);
    const newMode = mode === "live" ? "replay" : "live";
    try {
      const res = await switchMode(newMode);
      setMode(res.new_mode);
    } catch (err) {
      console.error("Failed to switch mode", err);
    } finally {
      setIsLoading(false);
    }
  };

  const isLive = mode === "live";

  return (
    <button
      onClick={handleToggle}
      disabled={isLoading}
      className={`hidden lg:flex items-center gap-2 px-2.5 py-1 rounded-full border text-xs font-bold shadow-xs transition-colors duration-200 ${
        isLive
          ? "bg-emerald-50 dark:bg-emerald-950/40 border-emerald-200 dark:border-emerald-800/60 text-emerald-700 dark:text-emerald-400"
          : "bg-amber-50 dark:bg-amber-950/40 border-amber-200 dark:border-amber-800/60 text-amber-700 dark:text-amber-400"
      }`}
    >
      <span className="relative flex h-2 w-2">
        {isLive ? (
          <>
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
          </>
        ) : (
          <span className="relative inline-flex rounded-full h-2 w-2 bg-amber-500"></span>
        )}
      </span>
      <span className="tracking-wide">
        {isLoading ? "SWITCHING..." : isLive ? "LIVE TELEMETRY" : "REPLAY MODE"}
      </span>
    </button>
  );
};
