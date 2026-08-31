import React, { useState, useMemo, useRef, useEffect } from "react";
import {
  Globe,
  Plus,
  Minus,
  Navigation,
  GitCommit,
  Maximize2,
  Minimize2,
  ChevronDown,
  ChevronUp,
  Shield,
  Radio,
  Zap,
  Activity,
  Layers,
  Crosshair,
  Wifi,
  Eye,
  Sliders,
  X,
  Clock,
  Server
} from "lucide-react";
import * as d3Geo from "d3-geo";
import * as topojson from "topojson-client";
import worldData from "world-atlas/countries-110m.json";

import { MapSkeleton } from "../common/SkeletonLoader";
import { Tooltip } from "../common/Tooltip";
import { Badge } from "../common/Badge";

const SVG_WIDTH = 960;
const SVG_HEIGHT = 480;

// Threat type color lookup per requirement:
// Ransomware=blue (#3B82F6), Phishing=red (#EF4444), Brute Force=orange (#F97316), DDoS=yellow (#EAB308), Malware=green (#10B981), Benign=slate (#94A3B8)
const threatTypeColors = {
  Ransomware: "#3B82F6",
  Phishing: "#EF4444",
  "Brute Force": "#F97316",
  DDoS: "#EAB308",
  Malware: "#10B981",
  Benign: "#94A3B8",
};

export const WorldMapWidget = ({ isLoading, alerts = [] }) => {
  // Dynamic Map Data Generation
  const dynamicSOCDestination = { coordinates: [78.9629, 20.5937] }; // India, default SOC
  
  const { dynamicAttackOrigins, dynamicAttackVectors } = useMemo(() => {
    if (!alerts || alerts.length === 0) {
      return { dynamicAttackOrigins: [], dynamicAttackVectors: [] };
    }

    const originsMap = {};
    
    const getColor = (type) => {
      const t = (type || "").toLowerCase();
      if (t.includes("benign")) return "#94A3B8";
      if (t.includes("ransom")) return "#3B82F6";
      if (t.includes("phish")) return "#EF4444";
      if (t.includes("brute") || t.includes("c2") || t.includes("beaconing")) return "#F97316";
      if (t.includes("ddos") || t.includes("flood")) return "#EAB308";
      return "#10B981"; // malware/default
    };

    const vectors = [];

    const MAJOR_ORIGINS = [
      { country: "Russia", flag: "🇷🇺", coordinates: [37.6173, 55.7558], code: "RU", asn: "AS12389 Rostelecom" },
      { country: "China", flag: "🇨🇳", coordinates: [116.4074, 39.9042], code: "CN", asn: "AS4134 Chinanet" },
      { country: "United States", flag: "🇺🇸", coordinates: [-77.0369, 38.9072], code: "US", asn: "AS7922 Comcast" },
      { country: "Brazil", flag: "🇧🇷", coordinates: [-47.9292, -15.7801], code: "BR", asn: "AS28573 Claro" },
      { country: "Iran", flag: "🇮🇷", coordinates: [51.3890, 35.6892], code: "IR", asn: "AS12880 ITC" },
      { country: "North Korea", flag: "🇰🇵", coordinates: [125.7625, 39.0392], code: "KP", asn: "AS131279 Ryugyong" },
      { country: "Germany", flag: "🇩🇪", coordinates: [13.4050, 52.5200], code: "DE", asn: "AS3320 DTAG" },
      { country: "Vietnam", flag: "🇻🇳", coordinates: [105.8342, 21.0278], code: "VN", asn: "AS45899 VNPT" },
      { country: "Nigeria", flag: "🇳🇬", coordinates: [3.3792, 6.5244], code: "NG", asn: "AS36873 Globacom" },
      { country: "Ukraine", flag: "🇺🇦", coordinates: [30.5238, 50.4501], code: "UA", asn: "AS15895 Kyivstar" },
      { country: "South Korea", flag: "🇰🇷", coordinates: [126.9780, 37.5665], code: "KR", asn: "AS4766 Korea Telecom" },
      { country: "Japan", flag: "🇯🇵", coordinates: [139.6917, 35.6895], code: "JP", asn: "AS2516 KDDI" },
      { country: "United Kingdom", flag: "🇬🇧", coordinates: [-0.1276, 51.5074], code: "GB", asn: "AS2856 BT" },
      { country: "Netherlands", flag: "🇳🇱", coordinates: [4.9041, 52.3676], code: "NL", asn: "AS1136 KPN" },
      { country: "Singapore", flag: "🇸🇬", coordinates: [103.8198, 1.3521], code: "SG", asn: "AS7473 SingTel" },
    ];

    alerts.forEach((alert) => {
      // Deterministic pseudo-random location based on source IP string
      let hash = 0;
      const ip = alert.source || "0.0.0.0";
      for (let i = 0; i < ip.length; i++) {
        hash = (hash << 5) - hash + ip.charCodeAt(i);
        hash |= 0;
      }
      
      const originIndex = Math.abs(hash) % MAJOR_ORIGINS.length;
      const origin = MAJOR_ORIGINS[originIndex];
      const originKey = `${origin.code}`;

      if (!originsMap[originKey]) {
        originsMap[originKey] = {
          country: origin.country,
          code: origin.code,
          flag: origin.flag,
          count: 0,
          threatType: alert.attackType,
          color: getColor(alert.attackType),
          coordinates: origin.coordinates,
          topAsn: origin.asn,
          recentIoc: ip,
        };
      }
      originsMap[originKey].count += 1;
    });

    const origins = Object.values(originsMap).sort((a, b) => b.count - a.count);
    const total = alerts.length;
    origins.forEach((o) => (o.percentage = ((o.count / total) * 100).toFixed(1)));

    // Generate exactly one trajectory vector per origin country
    const uniqueVectors = origins.map((origin) => ({
      id: origin.code,
      originName: origin.country,
      originCoords: origin.coordinates,
      destCoords: dynamicSOCDestination.coordinates,
      threatType: origin.threatType,
      severity: "high", // proxy severity
      color: origin.color,
      ip: origin.recentIoc,
      target: "SOC HQ",
      speed: "live",
    }));

    return { dynamicAttackOrigins: origins.slice(0, 15), dynamicAttackVectors: uniqueVectors }; 
  }, [alerts]);

  // Pan & Zoom state
  const [zoomLevel, setZoomLevel] = useState(1);
  const [panOffset, setPanOffset] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });

  // Map Feature Toggles
  const [selectedRegion, setSelectedRegion] = useState("All Regions");
  const [showRegionDropdown, setShowRegionDropdown] = useState(false);
  const [showAttackRoutes, setShowAttackRoutes] = useState(true);
  const [showGraticule, setShowGraticule] = useState(true);
  const [isGlobeView, setIsGlobeView] = useState(false); // Toggle between Natural Earth & Orthographic
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isTopOriginsCollapsed, setIsTopOriginsCollapsed] = useState(false);
  const [globeRotation, setGlobeRotation] = useState(0);

  // Rotate globe when in globe view
  useEffect(() => {
    let animationFrame;
    if (isGlobeView) {
      const rotate = () => {
        setGlobeRotation((prev) => (prev + 0.3) % 360);
        animationFrame = requestAnimationFrame(rotate);
      };
      animationFrame = requestAnimationFrame(rotate);
    }
    return () => cancelAnimationFrame(animationFrame);
  }, [isGlobeView]);

  // Interactive Hover and Popover States
  const [hoveredOrigin, setHoveredOrigin] = useState(null);
  const [hoveredCountry, setHoveredCountry] = useState(null);
  const [hoveredVectorId, setHoveredVectorId] = useState(null);
  const [selectedNodeDetails, setSelectedNodeDetails] = useState(null);
  const [tooltipPos, setTooltipPos] = useState({ x: 0, y: 0 });

  const svgRef = useRef(null);
  const popoverRef = useRef(null);

  // Close popover on outside click
  useEffect(() => {
    const handleOutsideClick = (e) => {
      if (popoverRef.current && !popoverRef.current.contains(e.target)) {
        // If clicked outside popover and not on a node
        if (!e.target.closest(".interactive-node")) {
          setSelectedNodeDetails(null);
        }
      }
    };
    document.addEventListener("mousedown", handleOutsideClick);
    return () => document.removeEventListener("mousedown", handleOutsideClick);
  }, []);

  // Map Projection calculation (Natural Earth vs Orthographic)
  const { landFeature, countryFeatures, bordersMesh, graticuleLines, projection, geoPath } = useMemo(() => {
    let proj;
    if (isGlobeView) {
      proj = d3Geo
        .geoOrthographic()
        .scale(190)
        .translate([SVG_WIDTH / 2, SVG_HEIGHT / 2 + 10])
        .clipAngle(90)
        .rotate([globeRotation, -10]);
    } else {
      proj = d3Geo
        .geoNaturalEarth1()
        .scale(152)
        .translate([SVG_WIDTH / 2, SVG_HEIGHT / 2 + 15]);
    }

    const pathGen = d3Geo.geoPath().projection(proj);
    const land = topojson.feature(worldData, worldData.objects.land);
    const countries = topojson.feature(worldData, worldData.objects.countries).features;
    const borders = topojson.mesh(worldData, worldData.objects.countries, (a, b) => a !== b);
    const graticule = d3Geo.geoGraticule10();

    return {
      landFeature: land,
      countryFeatures: countries,
      bordersMesh: borders,
      graticuleLines: graticule,
      projection: proj,
      geoPath: pathGen,
    };
  }, [isGlobeView, globeRotation]);

  // Projected 2D screen positions
  const projectedDestination = useMemo(() => {
    const coords = projection(dynamicSOCDestination.coordinates);
    return coords ? { x: coords[0], y: coords[1] } : { x: SVG_WIDTH / 2, y: SVG_HEIGHT / 2 };
  }, [projection]);

  const projectedOrigins = useMemo(() => {
    return dynamicAttackOrigins.map((orig) => {
      const coords = projection(orig.coordinates);
      return {
        ...orig,
        screenX: coords ? coords[0] : 0,
        screenY: coords ? coords[1] : 0,
        visible: coords !== null,
      };
    });
  }, [projection]);

  const projectedAttackVectors = useMemo(() => {
    return dynamicAttackVectors.map((atk) => {
      const start = projection(atk.originCoords);
      const end = projection(atk.destCoords);
      if (!start || !end) return null;

      const [x1, y1] = start;
      const [x2, y2] = end;

      const dx = x2 - x1;
      const dy = y2 - y1;
      const dist = Math.sqrt(dx * dx + dy * dy);
      const midX = (x1 + x2) / 2;
      const arcHeight = Math.min(Math.max(dist * 0.35, 30), 85);
      const midY = (y1 + y2) / 2 - arcHeight;

      const pathData = `M ${x1} ${y1} Q ${midX} ${midY} ${x2} ${y2}`;
      const color = threatTypeColors[atk.threatType] || atk.color;

      return {
        ...atk,
        x1,
        y1,
        x2,
        y2,
        midX,
        midY,
        pathData,
        color,
      };
    }).filter(Boolean);
  }, [projection]);

  // Pan & Zoom Handlers with clamping
  const handleMouseDown = (e) => {
    if (e.button !== 0) return;
    setIsDragging(true);
    setDragStart({ x: e.clientX - panOffset.x, y: e.clientY - panOffset.y });
  };

  const handleMouseMove = (e) => {
    if (isDragging) {
      const maxPan = 400 * zoomLevel;
      const newX = Math.min(Math.max(e.clientX - dragStart.x, -maxPan), maxPan);
      const newY = Math.min(Math.max(e.clientY - dragStart.y, -maxPan), maxPan);
      setPanOffset({ x: newX, y: newY });
    }

    if (svgRef.current) {
      const rect = svgRef.current.getBoundingClientRect();
      setTooltipPos({
        x: e.clientX - rect.left,
        y: e.clientY - rect.top,
      });
    }
  };

  const handleMouseUp = () => setIsDragging(false);

  const handleWheel = (e) => {
    e.preventDefault();
    const zoomDelta = e.deltaY > 0 ? -0.15 : 0.15;
    setZoomLevel((prev) => Math.min(Math.max(prev + zoomDelta, 0.8), 3.5));
  };

  const handleZoomIn = () => setZoomLevel((prev) => Math.min(prev + 0.3, 3.5));
  const handleZoomOut = () => setZoomLevel((prev) => Math.max(prev - 0.3, 0.8));
  const handleReset = () => {
    setZoomLevel(1);
    setPanOffset({ x: 0, y: 0 });
    setSelectedRegion("All Regions");
  };

  const handleSelectRegion = (region) => {
    setSelectedRegion(region);
    setShowRegionDropdown(false);

    if (region === "All Regions") {
      setZoomLevel(1);
      setPanOffset({ x: 0, y: 0 });
    } else if (region === "North America") {
      setZoomLevel(1.9);
      setPanOffset({ x: 260, y: 30 });
    } else if (region === "Europe & EMEA") {
      setZoomLevel(2.4);
      setPanOffset({ x: -40, y: 20 });
    } else if (region === "Asia-Pacific (APAC)") {
      setZoomLevel(1.8);
      setPanOffset({ x: -280, y: 0 });
    } else if (region === "Latin America") {
      setZoomLevel(1.8);
      setPanOffset({ x: 190, y: -130 });
    }
  };

  if (isLoading) {
    return <MapSkeleton />;
  }

  const regions = [
    "All Regions",
    "North America",
    "Europe & EMEA",
    "Asia-Pacific (APAC)",
    "Latin America",
  ];

  return (
    <div
      className={`relative bg-white dark:bg-[#1A1E27] rounded-2xl border border-slate-200/80 dark:border-white/[0.08] shadow-card dark:shadow-card-dark hover:shadow-card-hover dark:hover:shadow-card-hover-dark transition-all duration-300 flex flex-col justify-between overflow-hidden ${
        isFullscreen
          ? "fixed inset-4 z-50 shadow-2xl bg-white/98 dark:bg-[#0B0E14]/98 backdrop-blur-2xl"
          : "h-full min-h-[500px]"
      }`}
    >
      {/* CARD HEADER */}
      <div className="p-5 pb-3 flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 dark:border-slate-800/80 relative z-20">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400 border border-blue-100 dark:border-blue-800/60 shadow-xs">
            <Globe className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-base font-bold text-slate-900 dark:text-[#E4E6EB] leading-none">
                Global Threat Activity
              </h2>
              {/* LIVE ACTIVE COUNTER BADGE WITH PULSING GREEN DOT */}
              <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-400 border border-emerald-200/60 dark:border-emerald-800/60 text-[10.5px] font-bold shadow-xs">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                </span>
                <span>Live • 182 active</span>
              </span>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
              Cartographic interception coordinates & ballistic trajectory tracking
            </p>
          </div>
        </div>

        {/* Region Filter & Fullscreen Toggle */}
        <div className="flex items-center gap-2">
          {/* Region Dropdown */}
          <div className="relative">
            <Tooltip content="Filter map focus by global theater" position="bottom">
              <button
                id="region-filter-dropdown"
                onClick={() => setShowRegionDropdown(!showRegionDropdown)}
                aria-label="Filter region"
                className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-50 dark:bg-slate-800 hover:bg-slate-100 dark:hover:bg-slate-700 text-xs font-semibold text-slate-700 dark:text-slate-200 border border-slate-200 dark:border-slate-700 shadow-xs transition-colors"
              >
                <span>{selectedRegion}</span>
                <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
              </button>
            </Tooltip>

            {showRegionDropdown && (
              <div className="absolute right-0 mt-1.5 w-48 bg-white dark:bg-[#1A1E27] rounded-xl shadow-2xl border border-slate-200 dark:border-slate-700 py-1.5 z-30 animate-in fade-in zoom-in-95 backdrop-blur-xl">
                {regions.map((reg) => (
                  <button
                    key={reg}
                    onClick={() => handleSelectRegion(reg)}
                    className={`w-full text-left px-3.5 py-1.5 text-xs font-medium flex items-center justify-between transition-colors ${
                      selectedRegion === reg
                        ? "bg-blue-50 dark:bg-blue-950/60 text-blue-700 dark:text-blue-400 font-bold"
                        : "text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800"
                    }`}
                  >
                    <span>{reg}</span>
                    {selectedRegion === reg && (
                      <span className="w-1.5 h-1.5 rounded-full bg-blue-600 dark:bg-blue-400" />
                    )}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Fullscreen Expand Button */}
          <Tooltip content={isFullscreen ? "Exit Fullscreen" : "Expand Fullscreen"} position="bottom">
            <button
              onClick={() => setIsFullscreen(!isFullscreen)}
              aria-label={isFullscreen ? "Exit Fullscreen" : "Expand Fullscreen"}
              className="p-1.5 rounded-xl text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 border border-slate-200 dark:border-slate-700 shadow-xs transition-colors"
            >
              {isFullscreen ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
            </button>
          </Tooltip>
        </div>
      </div>

      {/* MAP CANVAS CONTAINER */}
      <div
        className="relative flex-1 bg-[#090D16] overflow-hidden flex items-center justify-center min-h-[380px] select-none cursor-grab active:cursor-grabbing"
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        onWheel={handleWheel}
        ref={svgRef}
      >
        {/* Deep space radial glow */}
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_45%,#E2E8F0_0%,#F8FAFC_80%)] dark:bg-[radial-gradient(circle_at_50%_45%,#1E293B_0%,#090D16_80%)] pointer-events-none opacity-90" />

        {/* Ambient coordinate crosshair overlay */}
        <div
          className="absolute inset-0 opacity-20 dark:opacity-10 pointer-events-none"
          style={{
            backgroundImage: `radial-gradient(circle, #38BDF8 1px, transparent 1px)`,
            backgroundSize: "28px 28px",
          }}
        />

        {/* REALISTIC SVG WORLD MAP */}
        <svg
          viewBox={`0 0 ${SVG_WIDTH} ${SVG_HEIGHT}`}
          className="w-full h-full max-h-[500px]"
          preserveAspectRatio="xMidYMid slice"
          style={{
            transform: `translate(${panOffset.x}px, ${panOffset.y}px) scale(${zoomLevel})`,
            transformOrigin: "center center",
            transition: isDragging ? "none" : "transform 0.25s ease-out",
          }}
        >
          <defs>
            <filter id="laserGlowRealistic" x="-50%" y="-50%" width="200%" height="200%">
              <feGaussianBlur in="SourceGraphic" stdDeviation="2.5" result="blur" />
              <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>

            <filter id="hubGlow" x="-100%" y="-100%" width="300%" height="300%">
              <feGaussianBlur in="SourceGraphic" stdDeviation="4" result="blur" />
              <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>

          {/* 1. GRATICULE (Lat / Long grid) */}
          {showGraticule && (
            <path
              d={geoPath(graticuleLines)}
              fill="none"
              className="stroke-slate-200 dark:stroke-[#1E293B]"
              strokeWidth="0.6"
              strokeDasharray="2 3"
              opacity="0.75"
            />
          )}

          {/* 2. REALISTIC WORLD LANDMASSES */}
          <g className="world-landmasses">
            {countryFeatures.map((country, idx) => {
              const isHovered = hoveredCountry === country.id;
              return (
                <path
                  key={country.id || idx}
                  d={geoPath(country)}
                  className={`transition-colors duration-150 cursor-pointer stroke-slate-300 dark:stroke-[#2E3C56] ${isHovered ? "fill-slate-200 dark:fill-[#2C384E]" : "fill-slate-100 dark:fill-[#1A2234]"}`}
                  strokeWidth="0.45"
                  onMouseEnter={() => setHoveredCountry(country.id)}
                  onMouseLeave={() => setHoveredCountry(null)}
                />
              );
            })}

            {bordersMesh && (
              <path
                d={geoPath(bordersMesh)}
                fill="none"
                className="stroke-slate-300 dark:stroke-[#334155]"
                strokeWidth="0.5"
                strokeOpacity="0.75"
              />
            )}
          </g>

          {/* 3. ANIMATED BALLISTIC ATTACK ARCS */}
          {showAttackRoutes && (
            <g className="attack-trajectories">
              {projectedAttackVectors.map((vector) => {
                const isHoveredLine = hoveredVectorId === vector.id;
                const isDimmed = hoveredVectorId !== null && !isHoveredLine;

                return (
                  <g
                    key={vector.id}
                    onMouseEnter={() => setHoveredVectorId(vector.id)}
                    onMouseLeave={() => setHoveredVectorId(null)}
                    className="cursor-pointer"
                  >
                    {/* Background Faint Glow Path */}
                    <path
                      d={vector.pathData}
                      fill="none"
                      stroke={vector.color}
                      strokeWidth={isHoveredLine ? 3 : 1.2}
                      strokeOpacity={isDimmed ? 0.15 : isHoveredLine ? 0.5 : 0.25}
                      className="transition-all duration-150"
                    />

                    {/* Flowing Laser Dash Path */}
                    <path
                      d={vector.pathData}
                      fill="none"
                      stroke={vector.color}
                      strokeWidth={isHoveredLine ? 3.5 : 2}
                      strokeOpacity={isDimmed ? 0.3 : 1}
                      className="attack-arc-anim transition-all duration-150"
                      filter="url(#laserGlowRealistic)"
                    />

                    {/* Moving Gradient Pulse / Traveling Particle Bullet (Looping continuously) */}
                    <circle
                      r={isHoveredLine ? "3.5" : "2.5"}
                      fill="#FFFFFF"
                      opacity={isDimmed ? 0.3 : 1}
                      filter="url(#laserGlowRealistic)"
                    >
                      <animateMotion
                        path={vector.pathData}
                        dur={vector.speed || "2.2s"}
                        repeatCount="indefinite"
                      />
                    </circle>

                    <circle
                      r={isHoveredLine ? "6" : "4.5"}
                      fill={vector.color}
                      fillOpacity={isDimmed ? 0.2 : 0.6}
                      filter="url(#laserGlowRealistic)"
                    >
                      <animateMotion
                        path={vector.pathData}
                        dur={vector.speed || "2.2s"}
                        repeatCount="indefinite"
                      />
                    </circle>
                  </g>
                );
              })}
            </g>
          )}

          {/* 4. TOP ATTACK ORIGIN NODES (Interactive onClick & onHover) */}
          <g className="attack-origin-nodes">
            {projectedOrigins.map((orig) => {
              if (!orig.visible) return null;
              const isHovered = hoveredOrigin?.code === orig.code;
              const isSelected = selectedNodeDetails?.code === orig.code;

              return (
                <g
                  key={orig.code}
                  className="cursor-pointer group interactive-node"
                  transform={`translate(${orig.screenX}, ${orig.screenY})`}
                  onClick={(e) => {
                    e.stopPropagation();
                    setSelectedNodeDetails({
                      type: "origin",
                      title: `${orig.flag} ${orig.country}`,
                      count: orig.count,
                      threatType: orig.threatType,
                      lastSeen: "4 sec ago",
                      asn: orig.topAsn,
                      ioc: orig.recentIoc,
                      severity: "Critical",
                      status: "Edge Throttled",
                    });
                  }}
                  onMouseEnter={() => setHoveredOrigin(orig)}
                  onMouseLeave={() => setHoveredOrigin(null)}
                >
                  {/* Outer Pulsing Ping Ring */}
                  <circle
                    r={isHovered || isSelected ? "12" : "9"}
                    fill="none"
                    stroke={orig.color}
                    strokeWidth={isHovered ? "2" : "1.5"}
                    opacity="0.85"
                    className="animate-ping"
                  />

                  {/* Secondary Glow */}
                  <circle
                    r={isHovered || isSelected ? "8" : "6"}
                    fill={orig.color}
                    fillOpacity="0.4"
                    filter="url(#laserGlowRealistic)"
                  />

                  {/* Core Node Point */}
                  <circle
                    r={isHovered || isSelected ? "5.5" : "4"}
                    fill={orig.color}
                    stroke="#FFFFFF"
                    strokeWidth={isHovered ? "2" : "1.5"}
                    className="transition-all duration-150"
                  />

                  {/* Geographic Tag Label */}
                  <text
                    x="8"
                    y="3.5"
                    fill="#E2E8F0"
                    fontSize="9.5"
                    fontWeight="700"
                    fontFamily="Inter, sans-serif"
                    className="drop-shadow-md select-none pointer-events-none"
                  >
                    {orig.flag} {orig.country}
                  </text>
                </g>
              );
            })}
          </g>

          {/* 5. CENTRAL SOC DEFENSE HUB (India Core Hub) */}
          <g
            className="defense-soc-core cursor-pointer interactive-node"
            transform={`translate(${projectedDestination.x}, ${projectedDestination.y})`}
            onClick={(e) => {
              e.stopPropagation();
              setSelectedNodeDetails({
                type: "destination",
                title: "🇮🇳 Global Defense Core (India HQ)",
                count: 17483,
                threatType: "Multi-vector Shield",
                lastSeen: "Real-time Stream",
                asn: "AS24940 (Autonomous Perimeter)",
                ioc: "Core Ingress Gateway",
                severity: "Optimal",
                status: "Defending (99.99% Blocked)",
              });
            }}
          >
            {/* Radar Wave Ping Ring */}
            <circle
              r="24"
              fill="none"
              stroke="#38BDF8"
              strokeWidth="1.2"
              className="pulse-target-ring"
            />
            <circle
              r="15"
              fill="none"
              stroke="#3B82F6"
              strokeWidth="1.5"
              strokeDasharray="4 3"
            />

            {/* Radar beam animation */}
            <g className="animate-radar-sweep origin-center">
              <line x1="0" y1="0" x2="30" y2="0" stroke="#60A5FA" strokeWidth="1.8" opacity="0.8" />
              <circle cx="30" cy="0" r="1.8" fill="#93C5FD" />
            </g>

            {/* Shield Core */}
            <circle r="9" fill="#1D4ED8" fillOpacity="0.7" filter="url(#hubGlow)" />
            <circle r="5" fill="#60A5FA" stroke="#FFFFFF" strokeWidth="2" />

            {/* Label Badge */}
            <g transform="translate(0, 20)">
              <rect
                x="-44"
                y="0"
                width="88"
                height="17"
                rx="4"
                fill="#0F172A"
                stroke="#3B82F6"
                strokeWidth="1"
                className="drop-shadow-lg"
              />
              <text
                x="0"
                y="12"
                fill="#F8FAFC"
                fontSize="8.5"
                fontWeight="800"
                textAnchor="middle"
                fontFamily="Inter, sans-serif"
              >
                SOC CORE 🇮🇳
              </text>
            </g>
          </g>
        </svg>

        {/* COLLAPSIBLE TOP ATTACK ORIGIN OVERLAY CARD (Top-Right) */}
        <div
          className={`absolute top-3 right-3 z-20 bg-white/90 dark:bg-[#12151C]/90 backdrop-blur-md rounded-xl border border-slate-200 dark:border-slate-800/90 p-3 shadow-2xl transition-all duration-200 pointer-events-auto ${
            isTopOriginsCollapsed ? "w-44" : "w-56 sm:w-64"
          }`}
        >
          <div className="flex items-center justify-between pb-1.5 border-b border-slate-200 dark:border-slate-800">
            <span className="text-[10px] font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
              <Zap className="w-3 h-3 text-amber-400" /> TOP ATTACK ORIGIN
            </span>
            <Tooltip content={isTopOriginsCollapsed ? "Expand panel" : "Collapse panel"} position="left">
              <button
                onClick={() => setIsTopOriginsCollapsed(!isTopOriginsCollapsed)}
                className="p-1 text-slate-400 hover:text-slate-900 dark:hover:text-white rounded hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                aria-label="Toggle panel collapse"
              >
                {isTopOriginsCollapsed ? (
                  <ChevronDown className="w-3.5 h-3.5" />
                ) : (
                  <ChevronUp className="w-3.5 h-3.5" />
                )}
              </button>
            </Tooltip>
          </div>

          {!isTopOriginsCollapsed && (
            <div className="space-y-1.5 mt-2">
              {dynamicAttackOrigins.map((item) => (
                <div
                  key={item.code}
                  onMouseEnter={() => setHoveredOrigin(item)}
                  onMouseLeave={() => setHoveredOrigin(null)}
                  onClick={() => {
                    setSelectedNodeDetails({
                      type: "origin",
                      title: `${item.flag} ${item.country}`,
                      count: item.count,
                      threatType: item.threatType,
                      lastSeen: "Just now",
                      asn: item.topAsn,
                      ioc: item.recentIoc,
                      severity: "Critical",
                      status: "Edge Ingress",
                    });
                  }}
                  className={`flex items-center justify-between py-1 px-1.5 rounded-lg transition-colors cursor-pointer text-xs ${
                    hoveredOrigin?.code === item.code
                      ? "bg-slate-100 dark:bg-slate-800 text-white"
                      : "hover:bg-slate-800/60 text-slate-300"
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <span className="text-sm">{item.flag}</span>
                    <span className="font-medium truncate max-w-[95px]">{item.country}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-10 h-1.5 rounded-full bg-slate-100 dark:bg-slate-800 overflow-hidden hidden sm:block">
                      <div
                        className="h-full rounded-full transition-all duration-300"
                        style={{
                          width: `${item.percentage * 2}%`,
                          backgroundColor: item.color,
                        }}
                      />
                    </div>
                    <span className="font-mono text-slate-800 dark:text-slate-200 font-bold text-[11px]">
                      {item.count.toLocaleString()}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* MAP CONTROLS TOOLBAR (Responsive bottom-left or bottom center on mobile) */}
        <div className="absolute bottom-3 left-3 z-20 flex items-center gap-1 bg-slate-900/90 dark:bg-[#12151C]/90 backdrop-blur-md p-1.5 rounded-xl border border-slate-200 dark:border-slate-800 shadow-xl pointer-events-auto">
          <Tooltip content="Zoom in (+)" position="top">
            <button
              onClick={handleZoomIn}
              aria-label="Zoom in"
              className="p-1.5 rounded-lg text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            >
              <Plus className="w-3.5 h-3.5" />
            </button>
          </Tooltip>

          <Tooltip content="Zoom out (-)" position="top">
            <button
              onClick={handleZoomOut}
              aria-label="Zoom out"
              className="p-1.5 rounded-lg text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            >
              <Minus className="w-3.5 h-3.5" />
            </button>
          </Tooltip>

          <div className="w-[1px] h-4 bg-slate-100 dark:bg-slate-800 my-auto" />

          <Tooltip content="Reset default view" position="top">
            <button
              onClick={handleReset}
              aria-label="Reset view"
              className="p-1.5 rounded-lg text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            >
              <Navigation className="w-3.5 h-3.5" />
            </button>
          </Tooltip>

          <Tooltip content={isGlobeView ? "Switch to Flat Projection" : "Switch to Globe View"} position="top">
            <button
              onClick={() => setIsGlobeView(!isGlobeView)}
              aria-label="Toggle globe projection"
              className={`p-1.5 rounded-lg transition-colors ${
                isGlobeView ? "text-indigo-400 bg-indigo-500/20" : "text-slate-400 hover:text-slate-900 dark:hover:text-white"
              }`}
            >
              <Globe className="w-3.5 h-3.5" />
            </button>
          </Tooltip>

          <Tooltip content={showAttackRoutes ? "Hide attack trajectories" : "Show attack trajectories"} position="top">
            <button
              onClick={() => setShowAttackRoutes(!showAttackRoutes)}
              aria-label="Toggle attack trajectories"
              className={`p-1.5 rounded-lg transition-colors ${
                showAttackRoutes ? "text-blue-400 bg-blue-500/20" : "text-slate-500 hover:text-slate-900 dark:hover:text-white"
              }`}
            >
              <GitCommit className="w-3.5 h-3.5" />
            </button>
          </Tooltip>
        </div>

        {/* HOVER TOOLTIP */}
        {hoveredOrigin && !selectedNodeDetails && (
          <div
            className="absolute z-30 pointer-events-none bg-white/95 dark:bg-slate-950/95 text-slate-900 dark:text-white p-2.5 rounded-xl border border-slate-200 dark:border-slate-700 shadow-2xl text-xs backdrop-blur-md animate-in fade-in zoom-in-95"
            style={{
              left: Math.min(Math.max(tooltipPos.x + 12, 10), 650),
              top: Math.min(Math.max(tooltipPos.y - 60, 10), 320),
            }}
          >
            <div className="flex items-center gap-2 font-bold mb-1">
              <span>{hoveredOrigin.flag}</span>
              <span>{hoveredOrigin.country}</span>
              <span className="font-mono text-amber-400">({hoveredOrigin.count.toLocaleString()} attacks)</span>
            </div>
            <p className="text-[10px] text-slate-400 font-mono">Click dot for full forensic intelligence</p>
          </div>
        )}

        {/* CLICKED NODE DETAIL POPOVER (Floating Modal/Card) */}
        {selectedNodeDetails && (
          <div
            ref={popoverRef}
            className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-40 w-80 bg-white/98 dark:bg-slate-900/98 text-slate-900 dark:text-white p-4 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-2xl backdrop-blur-xl animate-in zoom-in-95 duration-200"
          >
            <div className="flex items-start justify-between pb-2 mb-3 border-b border-slate-200 dark:border-slate-800">
              <div className="flex items-center gap-2">
                <div className="p-1.5 rounded-lg bg-blue-500/20 text-blue-400 border border-blue-500/30">
                  <Shield className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-xs font-bold text-slate-900 dark:text-slate-100">{selectedNodeDetails.title}</h3>
                  <span className="text-[10px] font-mono text-slate-400">STATUS: {selectedNodeDetails.status}</span>
                </div>
              </div>
              <button
                onClick={() => setSelectedNodeDetails(null)}
                className="text-slate-400 hover:text-slate-900 dark:hover:text-white p-1 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800"
                aria-label="Close intelligence popover"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-2 text-xs font-mono">
              <div className="flex justify-between text-slate-400">
                <span>24h Ingress Volume:</span>
                <strong className="text-white font-bold">{selectedNodeDetails.count.toLocaleString()} packets</strong>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>Threat Payload:</span>
                <strong className="text-amber-400">{selectedNodeDetails.threatType}</strong>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>Autonomous System:</span>
                <span className="text-slate-700 dark:text-slate-300 truncate max-w-[140px]">{selectedNodeDetails.asn}</span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>Observed Ingress:</span>
                <span className="text-emerald-400">{selectedNodeDetails.ioc}</span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>Last Telemetry:</span>
                <span className="text-slate-300">{selectedNodeDetails.lastSeen}</span>
              </div>
            </div>

            <div className="mt-4 pt-3 border-t border-slate-200 dark:border-slate-800 flex gap-2">
              <button
                onClick={() => setSelectedNodeDetails(null)}
                className="flex-1 py-1.5 rounded-lg bg-slate-100 dark:bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-800 dark:text-slate-200 transition-colors"
              >
                Dismiss
              </button>
              <button
                onClick={() => setSelectedNodeDetails(null)}
                className="flex-1 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-xs font-semibold text-white shadow-md shadow-blue-500/20 transition-colors"
              >
                Isolate Vector
              </button>
            </div>
          </div>
        )}

      </div>

      {/* FOOTER THREAT LEGEND BAR */}
      <div className="px-5 py-2.5 bg-slate-50 dark:bg-[#12151C] border-t border-slate-100 dark:border-slate-800/80 flex flex-wrap items-center justify-between text-xs text-slate-500 dark:text-slate-400 gap-2">
        <div className="flex items-center gap-4 flex-wrap">
          <span className="text-[11px] font-bold text-slate-400 uppercase">Threat Legend:</span>
          <span className="flex items-center gap-1.5 text-xs text-slate-700 dark:text-slate-300">
            <span className="w-2 h-2 rounded-full bg-[#94A3B8] shadow-xs" /> Benign (Slate)
          </span>
          <span className="flex items-center gap-1.5 text-xs text-slate-700 dark:text-slate-300">
            <span className="w-2 h-2 rounded-full bg-[#3B82F6] shadow-xs" /> Ransomware (Blue)
          </span>
          <span className="flex items-center gap-1.5 text-xs text-slate-700 dark:text-slate-300">
            <span className="w-2 h-2 rounded-full bg-[#EF4444] shadow-xs" /> Phishing (Red)
          </span>
          <span className="flex items-center gap-1.5 text-xs text-slate-700 dark:text-slate-300">
            <span className="w-2 h-2 rounded-full bg-[#F97316] shadow-xs" /> Brute Force (Orange)
          </span>
          <span className="flex items-center gap-1.5 text-xs text-slate-700 dark:text-slate-300">
            <span className="w-2 h-2 rounded-full bg-[#EAB308] shadow-xs" /> DDoS (Yellow)
          </span>
          <span className="flex items-center gap-1.5 text-xs text-slate-700 dark:text-slate-300">
            <span className="w-2 h-2 rounded-full bg-[#10B981] shadow-xs" /> Malware (Green)
          </span>
        </div>
        <div className="flex items-center gap-2 text-[11px] font-mono text-slate-400">
          <span>Projection: {isGlobeView ? "Orthographic Globe" : "Natural Earth (WGS84)"}</span>
          <span>•</span>
          <span className="text-emerald-600 dark:text-emerald-400 font-semibold">Active Shielding</span>
        </div>
      </div>
    </div>
  );
};
