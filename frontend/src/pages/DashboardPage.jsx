import React, { useState } from "react";
import { motion } from "framer-motion";
import { Navbar } from "../components/layout/Navbar";
import { PageHeader } from "../components/layout/PageHeader";
import { StatCard } from "../components/dashboard/StatCard";
import { WorldMapWidget } from "../components/dashboard/WorldMapWidget";
import { ThreatFeed } from "../components/dashboard/ThreatFeed";
import { ThreatTrendChart } from "../components/dashboard/ThreatTrendChart";
import { ThreatDistributionChart } from "../components/dashboard/ThreatDistributionChart";
import { SecurityInsightPanel } from "../components/dashboard/SecurityInsightPanel";
import { IncidentsView } from "../components/views/IncidentsView";
import { SystemArchitectureView } from "../components/views/SystemArchitectureView";

import { Toast } from "../components/common/Toast";
import { AIAssistantBot } from "../components/dashboard/AIAssistantBot";

import { useSocData } from "../hooks/useSocData";

// Framer motion stagger animation variants
const containerVariants = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.07,
      delayChildren: 0.05,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 18 },
  show: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.35,
      ease: [0.16, 1, 0.3, 1],
    },
  },
};

export const DashboardPage = () => {
  const [activeTab, setActiveTab] = useState("overview");
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [lastSyncTime, setLastSyncTime] = useState("2 min ago");
  const [isLoadingSkeletons, setIsLoadingSkeletons] = useState(false);
  const [toastMessage, setToastMessage] = useState(null);
  const [toastType, setToastType] = useState("success");
  const { stats, feed, trend, distribution, insight, isLoading, error, refresh } = useSocData();

  const showToast = (message, type = "success") => {
    setToastMessage(message);
    setToastType(type);
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await refresh();
    setIsRefreshing(false);
    setLastSyncTime("Just now");
    showToast("SOC telemetry refreshed from Supabase.", "success");
  };

  const handleExport = (format = "csv") => {
    // TODO: replace with API call: GET /api/v1/soc/reports/export?format=${format}
    if (format === "json") {
      const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify({ stats, feed, trend, distribution }, null, 2));
      const downloadAnchor = document.createElement("a");
      downloadAnchor.setAttribute("href", dataStr);
      downloadAnchor.setAttribute("download", `TheThirdEYE_SOC_Export_${new Date().toISOString().slice(0, 10)}.json`);
      document.body.appendChild(downloadAnchor);
      downloadAnchor.click();
      downloadAnchor.remove();
      showToast("Exported TheThirdEYE raw telemetry JSON payload.", "info");
    } else if (format === "pdf") {
      window.print();
      showToast("Opening TheThirdEYE executive PDF print briefing...", "info");
    } else {
      const headers = "Metric,Value,Trend,Sentiment\n";
      const rows = stats.map((s) => `"${s.label}","${s.displayValue}","${s.trend}","${s.trendSentiment}"`).join("\n");
      const csvBlob = new Blob([headers + rows], { type: "text/csv;charset=utf-8;" });
      const url = URL.createObjectURL(csvBlob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `TheThirdEYE_SOC_Summary_${new Date().toISOString().slice(0, 10)}.csv`;
      a.click();
      URL.revokeObjectURL(url);
      showToast("TheThirdEYE SOC summary report (CSV) downloaded successfully.", "success");
    }
  };

  const handleActionToggle = (actionTitle, completed) => {
    if (completed) {
      showToast(`Action item marked complete: "${actionTitle}"`, "success");
    } else {
      showToast(`Action item reopened: "${actionTitle}"`, "info");
    }
  };

  return (
    <div className="min-h-screen bg-[#F5F6FA] dark:bg-[#0B0E14] text-slate-800 dark:text-[#E4E6EB] flex flex-col antialiased selection:bg-blue-500/20 selection:text-blue-500 transition-colors duration-300 relative">
      
      {/* Subtle Background Cyber Ambient Grid & Glow Mesh */}
      <div className="fixed inset-0 cyber-grid-light dark:cyber-grid-dark pointer-events-none opacity-60 z-0" />
      <div className="fixed top-0 left-1/4 w-96 h-96 bg-blue-500/5 dark:bg-blue-600/10 rounded-full blur-3xl pointer-events-none z-0" />
      <div className="fixed bottom-0 right-1/4 w-96 h-96 bg-indigo-500/5 dark:bg-indigo-600/10 rounded-full blur-3xl pointer-events-none z-0" />

      {/* TOP NAVBAR */}
      <Navbar activeTab={activeTab} onTabChange={setActiveTab} activeIncidents={insight?.active || 0} />

      {/* MAIN CONTENT WRAPPER */}
      <main className="flex-1 max-w-[1600px] w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 relative z-10">
        
        {/* PAGE HEADER TOOLBAR */}
        <PageHeader
          activeTab={activeTab}
          onRefresh={handleRefresh}
          isRefreshing={isRefreshing}
          lastSyncTime={lastSyncTime}
          onExport={handleExport}
          isLoadingSkeletons={isLoadingSkeletons}
          onToggleSkeletons={() => setIsLoadingSkeletons(!isLoadingSkeletons)}
        />

        {error && (
          <div className="mb-5 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800 dark:border-rose-900/70 dark:bg-rose-950/30 dark:text-rose-200">
            Live data is unavailable: {error}
          </div>
        )}

        {/* OVERVIEW DASHBOARD VIEW WITH FRAMER MOTION ANIMATION */}
        {activeTab === "overview" && (
          <motion.div
            variants={containerVariants}
            initial="hidden"
            animate="show"
            className="flex flex-col xl:flex-row gap-6"
          >
            {/* LEFT SIDEBAR: STAT CARDS (Vertically) */}
            <motion.section 
              variants={itemVariants} 
              aria-label="Security Operations Key Metrics"
              className="xl:w-64 flex flex-col gap-3 shrink-0"
            >
              {stats.map((stat) => (
                <StatCard
                  key={stat.id}
                  stat={stat}
                  isLoading={isLoading || isLoadingSkeletons}
                  compact={true}
                  onClick={() => {
                    if (stat.id === "critical_incidents") setActiveTab("incidents");
                    if (stat.id === "active_threats") setActiveTab("threat-feed");
                  }}
                />
              ))}
            </motion.section>

            {/* RIGHT MAIN AREA */}
            <div className="flex-1 flex flex-col gap-6 min-w-0">
              {/* TWO-COLUMN: GLOBAL THREAT MAP & LIVE THREAT FEED */}
              <motion.section variants={itemVariants} aria-label="Live Threat Map and Telemetry Feed">
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-stretch">
                  
                  {/* Left (Larger): Global Threat Activity World Map */}
                  <div className="lg:col-span-8 flex flex-col">
                    <WorldMapWidget isLoading={isLoading || isLoadingSkeletons} alerts={feed} />
                  </div>

                  {/* Right (Smaller): Live Threats Feed */}
                  <div className="lg:col-span-4 flex flex-col">
                    <ThreatFeed
                      isLoading={isLoading || isLoadingSkeletons}
                      items={feed}
                      onSelectThreat={(threat) => {
                        showToast(`Opened telemetry investigation for ${threat.title} (${threat.source})`, "info");
                      }}
                    />
                  </div>

                </div>
              </motion.section>

              {/* BOTTOM ROW: THREE COLUMNS */}
              <motion.section variants={itemVariants} aria-label="Trend Analytics and Security Insights">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
                  
                  {/* Threat Trend 24h Area Chart */}
                  <div className="flex flex-col">
                    <ThreatTrendChart isLoading={isLoading || isLoadingSkeletons} data={trend} />
                  </div>

                  {/* Threat Distribution Donut Chart */}
                  <div className="flex flex-col">
                    <ThreatDistributionChart isLoading={isLoading || isLoadingSkeletons} data={distribution} total={feed.length} />
                  </div>

                  {/* Security Insight Panel */}
                  <div className="flex flex-col">
                    <SecurityInsightPanel
                      isLoading={isLoading || isLoadingSkeletons}
                      insight={insight}
                      onActionToggle={handleActionToggle}
                    />
                  </div>

                </div>
              </motion.section>
            </div>
          </motion.div>
        )}

        {/* AUXILIARY TAB VIEWS */}
        {activeTab === "threat-feed" && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
              <div className="lg:col-span-8">
                <WorldMapWidget isLoading={isLoading || isLoadingSkeletons} alerts={feed} />
              </div>
              <div className="lg:col-span-4">
                <ThreatFeed isLoading={isLoading || isLoadingSkeletons} items={feed} />
              </div>
            </div>
          </div>
        )}

        {activeTab === "incidents" && (
          <IncidentsView onBackToOverview={() => setActiveTab("overview")} items={feed} />
        )}

        {activeTab === "system-status" && (
          <SystemArchitectureView />
        )}




      </main>

      {/* FOOTER */}
      <footer className="mt-12 py-6 border-t border-slate-200/80 dark:border-white/[0.08] bg-white/50 dark:bg-[#12151C]/50 backdrop-blur-md text-xs text-slate-500 dark:text-slate-400">
        <div className="max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <span className="font-bold text-slate-700 dark:text-slate-200">TheThirdEYE</span>
            <span>—</span>
            <span>Enterprise Security Telemetry & Autonomous Cyber Defense</span>
          </div>
          <div className="flex items-center gap-4 font-mono text-[11px]">
            <span>ENGINE: v4.8.2-SEC</span>
            <span>•</span>
            <span className="text-emerald-600 dark:text-emerald-400 font-bold">ALL SYSTEMS NOMINAL</span>
          </div>
        </div>
      </footer>

      {/* TOAST ALERTS */}
      <Toast
        message={toastMessage}
        type={toastType}
        onClose={() => setToastMessage(null)}
      />

      <AIAssistantBot />
    </div>
  );
};
