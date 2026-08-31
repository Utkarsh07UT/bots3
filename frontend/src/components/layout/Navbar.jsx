import { sendTestNotification } from "../../api/backend";
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Shield,
  Bell,
  ChevronDown,
  Activity,
  AlertTriangle,
  Server,
  Layers,
  Search,
  CheckCircle2,
  Settings,
  LogOut,
  User,
  Radio,
  ExternalLink,
  ShieldCheck
} from "lucide-react";
import { useAuth } from "../../context/AuthContext";
import { ThemeToggle } from "./ThemeToggle";
import { ModeToggle } from "./ModeToggle";
import { Tooltip } from "../common/Tooltip";
import { navTabs } from "../../data/mockData";

export const Navbar = ({ activeTab, onTabChange, activeIncidents = 0 }) => {
  const navigate = useNavigate();
  const { user, signOut } = useAuth();

  const [showNotifications, setShowNotifications] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [isSigningOut, setIsSigningOut] = useState(false);
  const [confirmSignOut, setConfirmSignOut] = useState(false);
  const [isTestLoading, setIsTestLoading] = useState(false);

  const [notifications, setNotifications] = useState([
    {
      id: "n-1",
      title: "Critical Ransomware Alarm",
      description: "Automated isolation initiated for SERVER-01",
      time: "2m ago",
      type: "critical",
    },
    {
      id: "n-2",
      title: "WAF Rule Triggered",
      description: "Over 4,000 requests throttled from AS49505",
      time: "14m ago",
      type: "warning",
    },
    {
      id: "n-3",
      title: "Daily Security Briefing Ready",
      description: "AI Summary report for Jul 31, 2026 compiled",
      time: "1h ago",
      type: "info",
    },
  ]);

  const clearNotification = (id) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id));
  };

  const handleSignOut = async () => {
    if (!confirmSignOut) {
      setConfirmSignOut(true);
      return;
    }
    setIsSigningOut(true);
    // TODO: replace with actual Supabase client call — supabase.auth.signOut()
    await signOut();
    navigate("/login");
  };

  const handleTestNotification = async () => {
    setIsTestLoading(true);
    try {
      const email = user?.email || "dark@thethirdeye.sec";
      await sendTestNotification(email, "console", "HIGH");
      alert(`Test notification sent successfully to ${email}!`);
    } catch (e) {
      alert(`Failed to send test notification: ${e.message}`);
    } finally {
      setIsTestLoading(false);
    }
  };

  const userName = user?.user_metadata?.full_name || "DarkTheUnk";
  const userRole = user?.user_metadata?.role || "Administrator";
  const userEmail = user?.email || "dark@thethirdeye.sec";
  const avatarUrl =
    user?.user_metadata?.avatar_url ||
    "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&q=80&w=256";

  return (
    <header className="sticky top-0 z-40 bg-white/95 dark:bg-[#0B0E14]/95 border-b border-slate-200/80 dark:border-white/[0.08] shadow-xs backdrop-blur-md transition-colors duration-300">
      <div className="max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          
          {/* LEFT: Brand Logo & Navigation */}
          <div className="flex items-center gap-8">
            <div
              onClick={() => onTabChange("overview")}
              className="flex items-center gap-3 cursor-pointer group select-none"
            >
              <div className="relative flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-600 text-white shadow-md shadow-blue-500/20 group-hover:scale-105 group-hover:shadow-glow-blue transition-all duration-200">
                <Shield className="w-5 h-5" />
                <div className="absolute top-1 right-1 w-2.5 h-2.5 bg-emerald-400 border-2 border-white dark:border-slate-900 rounded-full" />
              </div>
              <div className="flex flex-col">
                <div className="flex items-center gap-1.5">
                  <span className="text-xl font-bold tracking-tight bg-gradient-to-r from-slate-900 via-slate-800 to-blue-900 dark:from-white dark:via-slate-100 dark:to-blue-300 bg-clip-text text-transparent">
                    TheThirdEYE
                  </span>
                  <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-blue-50 dark:bg-blue-950/60 text-blue-700 dark:text-blue-400 border border-blue-200/60 dark:border-blue-800/60 uppercase tracking-wide">
                    SOC
                  </span>
                </div>
                <span className="text-[11px] text-slate-500 dark:text-slate-400 font-medium -mt-0.5">
                  Cyber Operations Core
                </span>
              </div>
            </div>

            {/* Nav Tabs */}
            <nav className="hidden md:flex items-center gap-1">
              {navTabs.map((tab) => {
                const isActive = activeTab === tab.id;
                return (
                  <button
                    key={tab.id}
                    id={`nav-tab-${tab.id}`}
                    onClick={() => onTabChange(tab.id)}
                    className={`relative px-3.5 py-2 rounded-xl text-xs font-semibold transition-all duration-150 flex items-center gap-2 ${
                      isActive
                        ? "text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-950/40 shadow-xs"
                        : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100 hover:bg-slate-100 dark:hover:bg-slate-800/60"
                    }`}
                  >
                    <span>{tab.label}</span>
                    { (tab.id === 'incidents' ? activeIncidents > 0 : tab.count !== undefined) && (
                      <span
                        className={`text-[10px] px-1.5 py-0.2 rounded-full font-bold ${
                          isActive
                            ? "bg-blue-600 text-white"
                            : "bg-slate-200 dark:bg-slate-800 text-slate-600 dark:text-slate-400"
                        }`}
                      >
                        {tab.id === 'incidents' ? activeIncidents : tab.count}
                      </span>
                    )}
                    {isActive && (
                      <span className="absolute bottom-0 left-3 right-3 h-0.5 bg-blue-600 dark:bg-blue-400 rounded-full" />
                    )}
                  </button>
                );
              })}
            </nav>
          </div>

          {/* RIGHT: Live Pulse, Theme Toggle, Notification Bell, User Avatar */}
          <div className="flex items-center gap-2.5 sm:gap-3">
            
            {/* Live Telemetry Pulse / Mode Toggle */}
            <ModeToggle />

            {/* THEME TOGGLE BUTTON (Sun/Moon) */}
            <ThemeToggle />

            {/* NOTIFICATION BELL WITH POPUP */}
            <div className="relative">
              <Tooltip content="Security notifications" position="bottom">
                <button
                  id="notification-bell-btn"
                  onClick={() => {
                    setShowNotifications(!showNotifications);
                    setShowUserMenu(false);
                  }}
                  aria-label="View security notifications"
                  className="relative p-2 rounded-xl text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 border border-slate-200/80 dark:border-white/[0.08] shadow-xs active:scale-95 transition-all duration-150 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40"
                >
                  <Bell className="w-4 h-4" />
                  {notifications.length > 0 && (
                    <span className="absolute top-1.5 right-1.5 flex h-2.5 w-2.5">
                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-400 opacity-75"></span>
                      <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-rose-500 border-2 border-white dark:border-slate-900"></span>
                    </span>
                  )}
                </button>
              </Tooltip>

              {/* Notifications Dropdown */}
              {showNotifications && (
                <div className="absolute right-0 mt-2 w-80 sm:w-96 bg-white dark:bg-[#1A1E27] rounded-2xl shadow-2xl border border-slate-200/90 dark:border-white/[0.08] py-3 z-50 animate-in fade-in zoom-in-95 duration-150 backdrop-blur-xl">
                  <div className="px-4 py-2 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-slate-800 dark:text-slate-100 text-xs uppercase tracking-wider">
                        Security Alerts
                      </span>
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-rose-100 dark:bg-rose-950/60 text-rose-700 dark:text-rose-400">
                        {notifications.length} New
                      </span>
                    </div>
                    {notifications.length > 0 && (
                      <button
                        onClick={() => setNotifications([])}
                        className="text-xs text-blue-600 dark:text-blue-400 hover:underline font-semibold"
                      >
                        Clear all
                      </button>
                    )}
                  </div>

                  <div className="max-h-72 overflow-y-auto divide-y divide-slate-100 dark:divide-slate-800 custom-scrollbar">
                    {notifications.length === 0 ? (
                      <div className="py-8 text-center text-slate-400 text-xs">
                        <CheckCircle2 className="w-8 h-8 mx-auto text-emerald-500 mb-2 opacity-80" />
                        No unread security alerts
                      </div>
                    ) : (
                      notifications.map((n) => (
                        <div
                          key={n.id}
                          className="px-4 py-3 hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors flex items-start justify-between gap-3 group"
                        >
                          <div className="flex items-start gap-2.5">
                            <div
                              className={`w-2 h-2 mt-1.5 rounded-full flex-shrink-0 ${
                                n.type === "critical"
                                  ? "bg-rose-500 shadow-glow-red"
                                  : n.type === "warning"
                                  ? "bg-amber-500 shadow-glow-yellow"
                                  : "bg-blue-500 shadow-glow-blue"
                              }`}
                            />
                            <div>
                              <div className="text-xs font-bold text-slate-900 dark:text-slate-100">
                                {n.title}
                              </div>
                              <div className="text-xs text-slate-500 dark:text-slate-400 mt-0.5 leading-relaxed">
                                {n.description}
                              </div>
                              <span className="text-[10px] text-slate-400 font-mono mt-1 inline-block">
                                {n.time}
                              </span>
                            </div>
                          </div>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              clearNotification(n.id);
                            }}
                            className="opacity-0 group-hover:opacity-100 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 text-xs p-1"
                            aria-label="Dismiss alert"
                          >
                            ×
                          </button>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* USER PROFILE AVATAR & DROPDOWN */}
            <div className="relative">
              <Tooltip content="SOC analyst profile & settings" position="bottom">
                <button
                  id="user-profile-btn"
                  onClick={() => {
                    setShowUserMenu(!showUserMenu);
                    setShowNotifications(false);
                    setConfirmSignOut(false);
                  }}
                  aria-label="SOC user profile menu"
                  className="flex items-center gap-2.5 p-1.5 pl-2 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 border border-transparent hover:border-slate-200 dark:hover:border-white/[0.08] transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 text-left select-none"
                >
                  <div className="relative">
                    <img
                      src={avatarUrl}
                      alt={userName}
                      className="w-8 h-8 rounded-xl object-cover ring-2 ring-blue-500/30 shadow-xs"
                    />
                    <div className="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 rounded-full bg-emerald-500 border-2 border-white dark:border-slate-900" />
                  </div>
                  <div className="hidden sm:block">
                    <div className="text-xs font-bold text-slate-900 dark:text-slate-100 leading-tight">
                      {userName}
                    </div>
                    <div className="text-[10.5px] text-slate-500 dark:text-slate-400 font-medium">
                      {userRole}
                    </div>
                  </div>
                  <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
                </button>
              </Tooltip>

              {/* User Dropdown */}
              {showUserMenu && (
                <div className="absolute right-0 mt-2 w-64 bg-white dark:bg-[#1A1E27] rounded-2xl shadow-2xl border border-slate-200/90 dark:border-white/[0.08] py-2 z-50 animate-in fade-in zoom-in-95 duration-150 backdrop-blur-xl">
                  <div className="px-4 py-3 border-b border-slate-100 dark:border-slate-800">
                    <p className="text-xs font-bold text-slate-900 dark:text-slate-100">{userName}</p>
                    <p className="text-[11px] text-slate-500 dark:text-slate-400 font-mono truncate">{userEmail}</p>
                    <div className="mt-2 inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-400 text-[10px] font-bold border border-emerald-200/60 dark:border-emerald-800/60">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span> Level 3 SOC Clearance
                    </div>
                  </div>

                  <div className="py-1 text-xs">
                    <button className="w-full px-4 py-2 text-left text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800/60 flex items-center gap-2.5">
                      <User className="w-4 h-4 text-slate-400" /> Analyst Preferences
                    </button>
                    <button className="w-full px-4 py-2 text-left text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800/60 flex items-center gap-2.5">
                      <Settings className="w-4 h-4 text-slate-400" /> SIEM Integrations
                    </button>
                    <button className="w-full px-4 py-2 text-left text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800/60 flex items-center gap-2.5">
                      <ShieldCheck className="w-4 h-4 text-slate-400" /> SOAR Automation Rules
                    </button>
                    <button 
                      onClick={handleTestNotification}
                      disabled={isTestLoading}
                      className="w-full px-4 py-2 text-left text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800/60 flex items-center gap-2.5"
                    >
                      <Bell className="w-4 h-4 text-slate-400" /> {isTestLoading ? "Sending..." : "Test Email Notification"}
                    </button>
                  </div>

                  {/* Destructive Action with Confirm State */}
                  <div className="border-t border-slate-100 dark:border-slate-800 pt-1">
                    <button
                      onClick={handleSignOut}
                      className="w-full px-4 py-2.5 text-left text-rose-600 dark:text-rose-400 hover:bg-rose-50 dark:hover:bg-rose-950/30 flex items-center justify-between text-xs font-semibold transition-colors"
                    >
                      <div className="flex items-center gap-2.5">
                        <LogOut className="w-4 h-4" />
                        <span>{confirmSignOut ? "Click again to confirm Sign out" : "Sign out of SOC"}</span>
                      </div>
                      {confirmSignOut && <span className="text-[10px] bg-rose-600 text-white px-1.5 py-0.5 rounded font-mono">CONFIRM</span>}
                    </button>
                  </div>
                </div>
              )}
            </div>

          </div>
        </div>

        {/* Mobile Sub-Navigation */}
        <div className="flex md:hidden overflow-x-auto py-2 border-t border-slate-100 dark:border-slate-800 gap-1 custom-scrollbar">
          {navTabs.map((tab) => {
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => onTabChange(tab.id)}
                className={`px-3 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap flex items-center gap-1.5 ${
                  isActive
                    ? "text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-950/50"
                    : "text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800"
                }`}
              >
                <span>{tab.label}</span>
                { (tab.id === 'incidents' ? activeIncidents > 0 : tab.count !== undefined) && (
                  <span
                    className={`text-[10px] px-1.5 py-0.2 rounded-full ${
                      isActive ? "bg-blue-600 text-white" : "bg-slate-200 dark:bg-slate-800 text-slate-600 dark:text-slate-400"
                    }`}
                  >
                    {tab.id === 'incidents' ? activeIncidents : tab.count}
                  </span>
                )}
              </button>
            );
          })}
        </div>

      </div>
    </header>
  );
};
