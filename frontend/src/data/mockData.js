/**
 * TheThirdEYE SOC Dashboard - Central Mock Data Store
 * 
 * NOTE FOR BACKEND ENGINEERS:
 * All structures and keys in this file represent the expected API response schemas.
 * Replace the exported functions and static payloads with your REST / GraphQL / WebSocket handlers.
 */

// ==========================================
// 1. STAT CARDS TELEMETRY
// ==========================================
// TODO: replace with API call: GET /api/v1/soc/stats/overview
export const mockStatsData = [
  {
    id: "security_score",
    label: "Security Score",
    value: "94",
    totalPossible: "100",
    displayValue: "94/100",
    isPrimaryHighlight: true, // Render with brand blue gradient background
    trend: "+2.4%",
    trendDirection: "up", // 'up' | 'down' | 'neutral'
    trendSentiment: "positive", // 'positive' | 'negative' | 'neutral'
    trendLabel: "vs last week",
    iconName: "ShieldCheck",
    linkHref: "#security-posture",
    details: "Overall SOC defensive posture across endpoints, perimeter, and identity.",
  },
  {
    id: "active_threats",
    label: "Active Threats",
    value: "182",
    displayValue: "182",
    isPrimaryHighlight: false,
    trend: "-10.2%",
    trendDirection: "down",
    trendSentiment: "positive", // Down in active threats is good (green)
    trendLabel: "vs yesterday",
    iconName: "Flame",
    linkHref: "#active-threats",
    details: "Unresolved threat actors and suspicious activities currently being tracked.",
  },
  {
    id: "critical_incidents",
    label: "Critical Incidents",
    value: "12",
    displayValue: "12",
    isPrimaryHighlight: false,
    trend: "+5",
    trendDirection: "up",
    trendSentiment: "negative", // Up in critical incidents is bad (red)
    trendLabel: "vs yesterday",
    iconName: "AlertTriangle",
    linkHref: "#critical-incidents",
    details: "High-priority alarms requiring immediate Level 3 analyst triage.",
  },
  {
    id: "threats_blocked",
    label: "Threats Blocked",
    value: "17,483",
    displayValue: "17,483",
    isPrimaryHighlight: false,
    trend: "+8.5%",
    trendDirection: "up",
    trendSentiment: "positive", // Up in threats blocked is good (green)
    trendLabel: "vs yesterday",
    iconName: "ShieldAlert",
    linkHref: "#threats-blocked",
    details: "Automated IPS/WAF and EDR mitigation actions executed in the past 24 hours.",
  },
  {
    id: "vulnerable_assets",
    label: "Vulnerable Assets",
    value: "255",
    displayValue: "255",
    isPrimaryHighlight: false,
    trend: "+6.0%",
    trendDirection: "up",
    trendSentiment: "positive", // Keep green icon color per design requirement
    trendLabel: "vs yesterday",
    iconName: "ServerCrash",
    linkHref: "#vulnerable-assets",
    details: "Workstations, servers, and cloud instances with unpatched CVEs.",
  },
];

// ==========================================
// 2. REAL-WORLD GEOGRAPHIC SOC MAP DATA
// ==========================================
// Real geographic coordinates [longitude, latitude] for global SOC hubs and threat origins
export const mockSOCDestination = {
  id: "hq-frankfurt",
  name: "Global Defense Core (India HQ)",
  city: "India",
  country: "India",
  flag: "🇩🇪",
  coordinates: [8.6821, 50.1109], // [lng, lat]
  status: "Defending",
  activeShields: "Level-3 WAF + EDR Mesh",
};

export const mockAuxiliaryDefenseHubs = [
  { id: "hub-us", name: "US East Perimeter (Ashburn)", coordinates: [-77.4875, 39.0438], flag: "🇺🇸" },
  { id: "hub-jp", name: "APAC Core (Tokyo)", coordinates: [139.6917, 35.6895], flag: "🇯🇵" },
  { id: "hub-uk", name: "London Edge (London)", coordinates: [-0.1278, 51.5074], flag: "🇬🇧" },
  { id: "hub-sg", name: "SE Asia Node (Singapore)", coordinates: [103.8198, 1.3521], flag: "🇸🇬" },
];

// TODO: replace with API call: GET /api/v1/soc/threat-map/origins
export const mockTopAttackOrigins = [
  {
    country: "United States",
    code: "US",
    flag: "🇺🇸",
    count: 2643,
    percentage: 36.5,
    threatType: "Phishing & Ransomware",
    color: "#3B82F6", // Blue
    coordinates: [-95.7129, 37.0902], // Real [lng, lat]
    topAsn: "AS15169 (Google / Cloud Proxies)",
    recentIoc: "172.217.14.9",
  },
  {
    country: "Russia",
    code: "RU",
    flag: "🇷🇺",
    count: 1688,
    percentage: 23.3,
    threatType: "DDoS & APT",
    color: "#EF4444", // Red
    coordinates: [37.6173, 55.7558], // Moscow [lng, lat]
    topAsn: "AS49505 (Hostkey B.V. Bulletproof)",
    recentIoc: "192.168.10.45",
  },
  {
    country: "China",
    code: "CN",
    flag: "🇨🇳",
    count: 1490,
    percentage: 20.6,
    threatType: "Brute Force & Scan",
    color: "#F97316", // Orange
    coordinates: [116.4074, 39.9042], // Beijing [lng, lat]
    topAsn: "AS4134 (ChinaNet Backbone)",
    recentIoc: "103.24.120.88",
  },
  {
    country: "India",
    code: "DE",
    flag: "🇩🇪",
    count: 872,
    percentage: 12.0,
    threatType: "Malware Beacon",
    color: "#10B981", // Green
    coordinates: [13.4050, 52.5200], // Berlin [lng, lat]
    topAsn: "AS24940 (Hetzner Online)",
    recentIoc: "185.12.64.21",
  },
  {
    country: "Netherlands",
    code: "NL",
    flag: "🇳🇱",
    count: 520,
    percentage: 7.2,
    threatType: "Botnet Proxy",
    color: "#EAB308", // Yellow
    coordinates: [4.9041, 52.3676], // Amsterdam [lng, lat]
    topAsn: "AS60781 (Leaseweb Global)",
    recentIoc: "185.220.101.5",
  },
];

// Active live attack vectors for the animated map trajectories
// TODO: replace with WebSocket stream: wss://soc.thethirdeye.io/stream/attacks
export const mockAttackVectors = [
  {
    id: "atk-01",
    originName: "United States (Ashburn)",
    originCoords: [-77.4875, 39.0438], // [lng, lat]
    destCoords: [8.6821, 50.1109],
    threatType: "Phishing",
    severity: "high",
    color: "#F97316",
    ip: "172.217.14.9",
    target: "sarah@gmail.com",
    speed: "2.4s",
  },
  {
    id: "atk-02",
    originName: "Russia (St. Petersburg)",
    originCoords: [30.3351, 59.9343],
    destCoords: [8.6821, 50.1109],
    threatType: "Ransomware",
    severity: "critical",
    color: "#EF4444",
    ip: "192.168.10.45",
    target: "SERVER-01",
    speed: "1.8s",
  },
  {
    id: "atk-03",
    originName: "China (Shanghai)",
    originCoords: [121.4737, 31.2304],
    destCoords: [8.6821, 50.1109],
    threatType: "Brute Force",
    severity: "medium",
    color: "#EAB308",
    ip: "103.24.120.88",
    target: "VPN-GATEWAY",
    speed: "3.1s",
  },
  {
    id: "atk-04",
    originName: "Netherlands (Amsterdam)",
    originCoords: [4.9041, 52.3676],
    destCoords: [8.6821, 50.1109],
    threatType: "Malware",
    severity: "low",
    color: "#3B82F6",
    ip: "185.220.101.5",
    target: "HR-LAPTOP-12",
    speed: "2.0s",
  },
  {
    id: "atk-05",
    originName: "Brazil (Sao Paulo)",
    originCoords: [-46.6333, -23.5505],
    destCoords: [8.6821, 50.1109],
    threatType: "DDoS",
    severity: "medium",
    color: "#EAB308",
    ip: "177.18.99.201",
    target: "DNS-EDGE-01",
    speed: "3.5s",
  },
  {
    id: "atk-06",
    originName: "India (Bengaluru)",
    originCoords: [77.5946, 12.9716],
    destCoords: [8.6821, 50.1109],
    threatType: "Phishing",
    severity: "high",
    color: "#F97316",
    ip: "49.207.54.12",
    target: "SSO-PROXY-01",
    speed: "2.7s",
  },
  {
    id: "atk-07",
    originName: "Australia (Sydney)",
    originCoords: [151.2093, -33.8688],
    destCoords: [8.6821, 50.1109],
    threatType: "Malware",
    severity: "low",
    color: "#10B981",
    ip: "139.130.4.5",
    target: "FIN-DATABASE-02",
    speed: "3.8s",
  },
];

// ==========================================
// 3. LIVE THREATS FEED
// ==========================================
// TODO: replace with WebSocket stream: wss://soc.thethirdeye.io/stream/feed
export const mockThreatFeed = [
  {
    id: "tf-101",
    title: "Ransomware Detected",
    source: "192.168.10.45",
    destination: "SERVER-01",
    destinationFlag: "🇩🇪",
    severity: "Critical", // Critical = red
    timestamp: "8 sec ago",
    timestampRaw: "2026-08-28T00:00:52Z",
    iconType: "lock",
    category: "Ransomware",
    status: "Blocked & Isolated",
    mitreTechnique: "T1486 Data Encrypted for Impact",
  },
  {
    id: "tf-102",
    title: "Phishing Attempt Blocked",
    source: "172.217.14.9",
    destination: "sarah@gmail.com",
    destinationFlag: "🇺🇸",
    severity: "High", // High = orange
    timestamp: "1 min ago",
    timestampRaw: "2026-08-28T00:00:00Z",
    iconType: "mail",
    category: "Phishing",
    status: "Quarantined",
    mitreTechnique: "T1566.002 Spearphishing Link",
  },
  {
    id: "tf-103",
    title: "Suspicious File Detected",
    source: "workstation-56",
    destination: "HR-LAPTOP-12",
    destinationFlag: "🇺🇸",
    severity: "Low", // Low = blue
    timestamp: "44 sec ago",
    timestampRaw: "2026-08-28T00:00:16Z",
    iconType: "file",
    category: "Malware",
    status: "Analyzing Sandbox",
    mitreTechnique: "T1204.002 Malicious File",
  },
  {
    id: "tf-104",
    title: "Brute Force Attack",
    source: "192.168.10.45",
    destination: "VPN-GATEWAY",
    destinationFlag: "🇨🇭",
    severity: "Medium", // Medium = yellow
    timestamp: "2 min ago",
    timestampRaw: "2026-08-27T23:59:00Z",
    iconType: "hammer",
    category: "Brute Force",
    status: "IP Throttled",
    mitreTechnique: "T1110.001 Password Guessing",
  },
  {
    id: "tf-105",
    title: "SQL Injection Probe",
    source: "45.154.255.89",
    destination: "PROD-API-GATEWAY",
    destinationFlag: "🇬🇧",
    severity: "High",
    timestamp: "3 min ago",
    timestampRaw: "2026-08-27T23:58:00Z",
    iconType: "lock",
    category: "Malware",
    status: "WAF Rule 942100 Triggered",
    mitreTechnique: "T1190 Exploit Public-Facing App",
  },
  {
    id: "tf-106",
    title: "Anomalous SSH Lateral Move",
    source: "10.0.4.12",
    destination: "FIN-DATABASE-02",
    destinationFlag: "🇩🇪",
    severity: "Critical",
    timestamp: "5 min ago",
    timestampRaw: "2026-08-27T23:56:00Z",
    iconType: "lock",
    category: "Ransomware",
    status: "Host Isolated",
    mitreTechnique: "T1021.004 Remote Services",
  }
];

// ==========================================
// 4. THREAT TREND CHART (24 Hours Telemetry)
// ==========================================
// x-axis: 00:00 to 24:00 in 4-hr increments, y-axis: 0 to 800
// TODO: replace with API call: GET /api/v1/soc/charts/trend?timeframe=24h
export const mockThreatTrendData = [
  { time: "00:00", threats: 320, blocked: 295, incidents: 3 },
  { time: "02:00", threats: 280, blocked: 265, incidents: 2 },
  { time: "04:00", threats: 210, blocked: 195, incidents: 1 },
  { time: "06:00", threats: 340, blocked: 310, incidents: 4 },
  { time: "08:00", threats: 490, blocked: 460, incidents: 6 },
  { time: "10:00", threats: 580, blocked: 540, incidents: 9 },
  { time: "11:42", threats: 609, blocked: 580, incidents: 10 },
  { time: "12:00", threats: 640, blocked: 610, incidents: 11 },
  { time: "14:00", threats: 710, blocked: 675, incidents: 12 },
  { time: "16:00", threats: 680, blocked: 650, incidents: 9 },
  { time: "18:00", threats: 530, blocked: 505, incidents: 7 },
  { time: "20:00", threats: 450, blocked: 430, incidents: 5 },
  { time: "22:00", threats: 380, blocked: 360, incidents: 4 },
  { time: "24:00", threats: 310, blocked: 295, incidents: 2 },
];

export const mockTrendTimeframes = [
  { label: "24 Hours", value: "24h" },
  { label: "7 Days", value: "7d" },
  { label: "30 Days", value: "30d" },
];

// ==========================================
// 5. THREAT DISTRIBUTION DONUT CHART
// ==========================================
// Total = 18,472
// TODO: replace with API call: GET /api/v1/soc/charts/distribution
export const mockDistributionTotal = "18,472";

export const mockThreatDistributionData = [
  {
    name: "Ransomware",
    value: 5170,
    percentage: 28,
    color: "#3B82F6", // Brand Blue
    description: "High impact payload targeting endpoint encryption",
  },
  {
    name: "Phishing",
    value: 4435,
    percentage: 24,
    color: "#EF4444", // Red
    description: "Credential harvesting & malicious attachments",
  },
  {
    name: "Brute Force",
    value: 3694,
    percentage: 20,
    color: "#F97316", // Orange
    description: "Automated credential stuffing & dictionary attacks",
  },
  {
    name: "DDoS",
    value: 2770,
    percentage: 15,
    color: "#EAB308", // Yellow
    description: "Volumetric network and application floods",
  },
  {
    name: "Malware",
    value: 1478,
    percentage: 8,
    color: "#10B981", // Green
    description: "Trojans, info-stealers, and keyloggers",
  },
  {
    name: "Other",
    value: 925,
    percentage: 5,
    color: "#6B7280", // Gray
    description: "Policy violations, scans, and unclassified probes",
  },
];

// ==========================================
// 6. SECURITY INSIGHT PANEL
// ==========================================
// TODO: replace with API call: GET /api/v1/soc/ai-insights/summary
export const mockSecurityInsight = {
  title: "Security Insight",
  badge: "AI Generated",
  summaryText:
    "Active threat volume decreased by **10.2%** over the past 24 hours. However, **12 Critical Incidents** remain open, driven primarily by coordinated **Ransomware probes** targeting internal database servers via VPN ingress. Automated containment has successfully blocked **17,483** exploitation vectors.",
  progressPercent: 33,
  progressLabel: "1 of 3 Actions Completed",
  recommendedActions: [
    {
      id: "act-1",
      title: "Investigate INC-2024-0519 (Ransomware)",
      completed: true,
      priority: "Critical",
      assignedTo: "Alex Morgan",
      details: "Containment confirmed for 192.168.10.45. Forensic memory snapshot uploaded to sandbox.",
    },
    {
      id: "act-2",
      title: "Review suspicious email campaigns",
      completed: false,
      priority: "High",
      assignedTo: "SecOps Team A",
      details: "Analyze 14 quarantined emails originating from spoofed supplier domain (172.217.14.9).",
    },
    {
      id: "act-3",
      title: "Apply pending critical patches (12)",
      completed: false,
      priority: "Medium",
      assignedTo: "DevOps Infrastructure",
      details: "Patch CVE-2026-3841 on VPN gateway and 11 downstream edge proxy containers.",
    },
  ],
};

// ==========================================
// 7. USER & SYSTEM PROFILE
// ==========================================
// TODO: replace with API call: GET /api/v1/soc/user/profile
export const mockUserProfile = {
  name: "Alex Morgan",
  role: "SOC Analyst",
  initials: "AM",
  avatarUrl: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&q=80&w=256",
  status: "active",
  unreadNotifications: 3,
  notifications: [
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
  ],
};

// Navigation tabs
export const navTabs = [
  { id: "overview", label: "Overview" },
  { id: "threat-feed", label: "Threat Feed" },
  { id: "incidents", label: "Incidents", count: 12 },
  { id: "system-status", label: "AI Architecture" },
];
