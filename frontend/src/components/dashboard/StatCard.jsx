import React from "react";
import {
  ShieldCheck,
  Flame,
  AlertTriangle,
  ShieldAlert,
  ServerCrash,
  ArrowUpRight,
  ArrowDownRight,
  TrendingUp,
  ExternalLink
} from "lucide-react";
import { StatCardSkeleton } from "../common/SkeletonLoader";
import { useTilt } from "../../hooks/useTilt";
import { useCountUp } from "../../hooks/useCountUp";
import { Tooltip } from "../common/Tooltip";

const iconComponents = {
  ShieldCheck: ShieldCheck,
  Flame: Flame,
  AlertTriangle: AlertTriangle,
  ShieldAlert: ShieldAlert,
  ServerCrash: ServerCrash,
};

export const StatCard = ({ stat, isLoading, compact, onClick }) => {
  const { ref, style, onMouseMove, onMouseLeave } = useTilt({
    maxTilt: 7,
    scale: 1.02,
  });

  const animatedValue = useCountUp(stat.displayValue, 1100);

  if (isLoading) {
    return <StatCardSkeleton compact={compact} />;
  }

  const IconComponent = iconComponents[stat.iconName] || ShieldCheck;
  const isHighlighted = stat.isPrimaryHighlight;

  // Trend Badge
  const renderTrend = () => {
    const isPositiveSentiment = stat.trendSentiment === "positive";

    if (isHighlighted) {
      return (
        <div className={`flex items-center gap-1 text-[11px] font-bold text-blue-100 bg-white/20 dark:bg-white/10 backdrop-blur-md ${compact ? 'px-2 py-0' : 'px-2.5 py-0.5'} rounded-full border border-white/20`}>
          <TrendingUp className="w-3 h-3 text-emerald-300" />
          <span>{stat.trend}</span>
          {!compact && <span className="opacity-80 hidden xl:inline">{stat.trendLabel}</span>}
        </div>
      );
    }

    return (
      <div
        className={`flex items-center gap-1 text-[11px] font-bold px-2 py-0.5 rounded-full border ${
          isPositiveSentiment
            ? "bg-emerald-50 dark:bg-emerald-950/50 text-emerald-700 dark:text-emerald-400 border-emerald-200/60 dark:border-emerald-800/60"
            : "bg-rose-50 dark:bg-rose-950/50 text-rose-700 dark:text-rose-400 border-rose-200/80 dark:border-rose-800/60"
        }`}
      >
        {stat.trendDirection === "down" ? (
          <ArrowDownRight className="w-3.5 h-3.5" />
        ) : (
          <ArrowUpRight className="w-3.5 h-3.5" />
        )}
        <span>{stat.trend}</span>
        {!compact && (
          <span className="font-normal opacity-75 text-[10.5px] hidden xl:inline">
            {stat.trendLabel}
          </span>
        )}
      </div>
    );
  };

  // 1. PRIMARY HIGHLIGHTED CARD (Security Score: 94/100)
  if (isHighlighted) {
    return (
      <div
        ref={ref}
        style={style}
        onMouseMove={onMouseMove}
        onMouseLeave={onMouseLeave}
        onClick={onClick}
        className={`relative overflow-hidden rounded-2xl ${compact ? 'p-3' : 'p-5'} bg-gradient-to-br from-blue-600 via-blue-700 to-indigo-800 dark:from-blue-600 dark:via-indigo-700 dark:to-slate-900 text-white shadow-lg shadow-blue-500/25 dark:shadow-[0_0_30px_rgba(59,130,246,0.35)] border border-blue-400/30 hover:border-blue-300 transition-all duration-200 cursor-pointer flex flex-col justify-between group preserve-3d`}
      >
        {/* Glow ambient shapes */}
        <div className="absolute -right-8 -top-8 w-32 h-32 bg-white/15 dark:bg-blue-400/20 rounded-full blur-2xl pointer-events-none group-hover:scale-110 transition-transform" />
        <div className="absolute -left-6 -bottom-6 w-24 h-24 bg-indigo-400/20 rounded-full blur-xl pointer-events-none" />

        {/* Top: Icon & External Link Tooltip */}
        <div className={`flex items-center justify-between ${compact ? 'mb-1' : 'mb-3'} relative z-10`}>
          <div className={`p-2 rounded-xl bg-white/15 dark:bg-white/10 backdrop-blur-md border border-white/20 text-white shadow-inner`}>
            <IconComponent className={`${compact ? 'w-4 h-4' : 'w-5 h-5'}`} />
          </div>
          {!compact && (
            <Tooltip content="Explore defensive posture details" position="top">
              <div className="p-1 rounded-lg text-white/70 hover:text-white hover:bg-white/10 transition-colors">
                <ExternalLink className="w-4 h-4 opacity-75 group-hover:opacity-100" />
              </div>
            </Tooltip>
          )}
        </div>

        {/* Middle: Label & Big Tabular Number */}
        <div className={`relative z-10 ${compact ? 'mb-1' : 'mb-3'}`}>
          <div className="text-[10px] font-bold text-blue-100 dark:text-blue-200 uppercase tracking-wider mb-0.5">
            {stat.label}
          </div>
          <div className="flex items-baseline gap-2">
            <span className={`${compact ? 'text-2xl sm:text-2xl' : 'text-3xl sm:text-4xl'} font-extrabold tracking-tight tabular-nums font-sans drop-shadow-md`}>
              {animatedValue}
            </span>
          </div>
        </div>

        {/* Bottom: Trend Badge & Sub-label */}
        <div className={`flex items-center justify-between relative z-10 ${compact ? 'pt-1' : 'pt-2'} border-t border-white/15`}>
          {renderTrend()}
          {!compact && <span className="text-[10.5px] font-semibold text-blue-100/90">Optimal Posture</span>}
        </div>
      </div>
    );
  }

  // 2. STANDARD CARDS WITH GLOW & 3D TILT
  const glowMap = {
    critical_incidents: "hover:shadow-glow-red dark:hover:shadow-[0_0_25px_rgba(239,68,68,0.3)]",
    active_threats: "hover:shadow-glow-orange dark:hover:shadow-[0_0_25px_rgba(249,115,22,0.3)]",
    threats_blocked: "hover:shadow-glow-green dark:hover:shadow-[0_0_25px_rgba(16,185,129,0.3)]",
    vulnerable_assets: "hover:shadow-glow-blue dark:hover:shadow-[0_0_25px_rgba(59,130,246,0.3)]",
  };

  return (
    <div
      ref={ref}
      style={style}
      onMouseMove={onMouseMove}
      onMouseLeave={onMouseLeave}
      onClick={onClick}
      className={`relative rounded-2xl ${compact ? 'p-3' : 'p-5'} bg-white dark:bg-[#1A1E27] border border-slate-200/80 dark:border-white/[0.08] shadow-card dark:shadow-card-dark hover:shadow-card-hover dark:hover:shadow-card-hover-dark hover:border-slate-300 dark:hover:border-slate-600 transition-all duration-200 cursor-pointer flex flex-col justify-between group preserve-3d ${glowMap[stat.id] || ""}`}
    >
      {/* Top: Icon & Tooltip */}
      <div className={`flex items-center justify-between ${compact ? 'mb-1' : 'mb-3'}`}>
        <div
          className={`p-2 rounded-xl ${
            stat.id === "critical_incidents"
              ? "bg-rose-50 dark:bg-rose-950/60 text-rose-600 dark:text-rose-400 border border-rose-100 dark:border-rose-800/60"
              : stat.id === "active_threats"
              ? "bg-amber-50 dark:bg-amber-950/60 text-amber-600 dark:text-amber-400 border border-amber-100 dark:border-amber-800/60"
              : stat.id === "vulnerable_assets"
              ? "bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400 border border-emerald-100 dark:border-emerald-800/60"
              : "bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400 border border-blue-100 dark:border-blue-800/60"
          }`}
        >
          <IconComponent className={`${compact ? 'w-4 h-4' : 'w-5 h-5'}`} />
        </div>
        {!compact && (
          <Tooltip content={`View ${stat.label} telemetry report`} position="top">
            <div className="p-1 rounded-lg text-slate-400 dark:text-slate-500 hover:text-slate-700 dark:hover:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors">
              <ExternalLink className="w-4 h-4 opacity-60 group-hover:opacity-100" />
            </div>
          </Tooltip>
        )}
      </div>

      {/* Middle: Label & Big Tabular Number */}
      <div className={`${compact ? 'mb-1' : 'mb-3'}`}>
        <div className="text-[10px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-0.5">
          {stat.label}
        </div>
        <div className={`${compact ? 'text-xl sm:text-2xl' : 'text-2xl sm:text-3xl'} font-extrabold text-slate-900 dark:text-[#E4E6EB] tracking-tight tabular-nums`}>
          {animatedValue}
        </div>
      </div>

      {/* Bottom: Trend and Subtext */}
      <div className={`flex items-center justify-between ${compact ? 'pt-1' : 'pt-2'} border-t border-slate-100 dark:border-slate-800/80`}>
        {renderTrend()}
        {!compact && <span className="text-[10px] text-slate-400 font-mono">24h delta</span>}
      </div>
    </div>
  );
};
