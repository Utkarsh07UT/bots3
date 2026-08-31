import { useCallback, useEffect, useMemo, useState } from "react";
import { fetchAlerts, fetchBotMetrics, isSupabaseConfigured } from "../api/supabase";

const titleCase = (value = "Unknown") => value.charAt(0) + value.slice(1).toLowerCase();
const iconFor = (attackType = "") => {
  const type = attackType.toLowerCase();
  if (type.includes("phish")) return "mail";
  if (type.includes("ransom") || type.includes("malware")) return "lock";
  if (type.includes("scan")) return "file";
  return "hammer";
};

const makeTrend = (alerts) => {
  const now = new Date();
  return Array.from({ length: 24 }, (_, offset) => {
    const start = new Date(now);
    start.setHours(now.getHours() - 23 + offset, 0, 0, 0);
    const end = new Date(start);
    end.setHours(end.getHours() + 1);
    const bucket = alerts.filter((alert) => {
      const created = new Date(alert.created_at);
      return created >= start && created < end;
    });
    return {
      time: start.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      threats: bucket.length,
      blocked: bucket.filter((alert) => alert.status === "RESOLVED").length,
      incidents: bucket.filter((alert) => ["HIGH", "CRITICAL"].includes(alert.severity)).length,
    };
  });
};

const makeDistribution = (alerts) => {
  const colors = ["#3B82F6", "#EF4444", "#F97316", "#10B981", "#8B5CF6", "#EAB308"];
  const counts = alerts.reduce((result, alert) => {
    const key = alert.attack_type || "Unknown";
    result[key] = (result[key] || 0) + 1;
    return result;
  }, {});
  const total = alerts.length;
  return Object.entries(counts)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 6)
    .map(([name, value], index) => ({
      name,
      value,
      percentage: total ? Math.round((value / total) * 100) : 0,
      color: colors[index],
      description: `${value} alert${value === 1 ? "" : "s"} reported by deployed detectors.`,
    }));
};

export function useSocData() {
  const [alerts, setAlerts] = useState([]);
  const [botMetrics, setBotMetrics] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const refresh = useCallback(async () => {
    if (!isSupabaseConfigured) {
      setError("Supabase is not configured for this frontend deployment.");
      setIsLoading(false);
      return;
    }
    setError(null);
    try {
      const [nextAlerts, nextMetrics] = await Promise.all([fetchAlerts(), fetchBotMetrics()]);
      setAlerts(nextAlerts || []);
      setBotMetrics(nextMetrics || []);
    } catch (requestError) {
      setError(requestError.message || "Unable to load SOC telemetry.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
    const interval = window.setInterval(refresh, 15000);
    return () => window.clearInterval(interval);
  }, [refresh]);

  const data = useMemo(() => {
    const active = alerts.filter((alert) => ["NEW", "INVESTIGATING"].includes(alert.status));
    const critical = active.filter((alert) => alert.severity === "CRITICAL");
    const resolved = alerts.filter((alert) => alert.status === "RESOLVED");
    const healthyBots = botMetrics.filter((bot) => ["HEALTHY", "ONLINE"].includes((bot.status || "").toUpperCase())).length;
    const stats = [
      { id: "security_score", label: "Security Score", value: String(Math.round(Math.max(14, 100 - critical.length * 1.2 - active.filter((a) => a.severity === "HIGH").length * 0.4))), totalPossible: "100", displayValue: `${Math.round(Math.max(14, 100 - critical.length * 1.2 - active.filter((a) => a.severity === "HIGH").length * 0.4))}/100`, isPrimaryHighlight: true, trend: "Live", trendDirection: "down", trendSentiment: "negative", trendLabel: "system under stress", iconName: "ShieldCheck", details: "Calculated from active alert severity.", linkHref: "#" },
      { id: "active_threats", label: "Active Threats", value: String(active.length), displayValue: String(active.length), trend: "Live", trendDirection: "up", trendSentiment: active.length > 50 ? "negative" : "positive", trendLabel: "open alerts", iconName: "Flame", details: "New and investigating alerts.", linkHref: "#" },
      { id: "critical_incidents", label: "Critical Incidents", value: String(critical.length), displayValue: String(critical.length), trend: "Live", trendDirection: "up", trendSentiment: critical.length > 10 ? "negative" : "positive", trendLabel: "requiring triage", iconName: "AlertTriangle", details: "Critical alerts not resolved.", linkHref: "#" },
      { id: "threats_blocked", label: "Threats Resolved", value: String(resolved.length), displayValue: String(resolved.length), trend: "Live", trendDirection: "up", trendSentiment: "positive", trendLabel: "in loaded history", iconName: "ShieldAlert", details: "Resolved alerts in Supabase.", linkHref: "#" },
      { id: "healthy_bots", label: "Healthy Bots", value: String(healthyBots), displayValue: String(healthyBots), trend: "Live", trendDirection: "up", trendSentiment: healthyBots ? "positive" : "negative", trendLabel: `of ${botMetrics.length} deployed`, iconName: "ServerCrash", details: "Bot health reported by the backend.", linkHref: "#" },
    ];
    return {
      stats,
      trend: makeTrend(alerts),
      distribution: makeDistribution(alerts),
      feed: alerts.map((alert) => ({ id: alert.alert_id || alert.id, title: alert.title, source: alert.source_ip, destination: `${alert.target_ip}${alert.target_port ? `:${alert.target_port}` : ""}`, severity: titleCase(alert.severity), timestamp: new Date(alert.created_at).toLocaleString(), iconType: iconFor(alert.attack_type), attackType: alert.attack_type, status: alert.status, raw: alert })),
      insight: { active: active.length, critical: critical.length, resolved: resolved.length, healthyBots, totalBots: botMetrics.length },
    };
  }, [alerts, botMetrics]);

  return { ...data, isLoading, error, refresh };
}
