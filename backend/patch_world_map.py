import re

with open("frontend/src/components/dashboard/WorldMapWidget.jsx", "r") as f:
    content = f.read()

# 1. Remove mock data imports
content = re.sub(r"import \{\n\s*mockTopAttackOrigins,\n\s*mockAttackVectors,\n\s*mockSOCDestination,\n\s*mockAuxiliaryDefenseHubs\n\} from \"\.\.\/\.\.\/data\/mockData\";", "", content)

# 2. Add signature
content = content.replace("export const WorldMapWidget = ({ isLoading }) => {", "export const WorldMapWidget = ({ isLoading, alerts = [] }) => {")

# 3. Add dynamic logic right after the component signature
dynamic_logic = """
  // Dynamic Map Data Generation
  const dynamicSOCDestination = { coordinates: [8.6821, 50.1109] }; // Frankfurt, default SOC
  
  const { dynamicAttackOrigins, dynamicAttackVectors } = useMemo(() => {
    if (!alerts || alerts.length === 0) {
      return { dynamicAttackOrigins: [], dynamicAttackVectors: [] };
    }

    const originsMap = {};
    const vectors = [];

    alerts.forEach((alert) => {
      // Deterministic pseudo-random lat/lng based on source IP string
      let hash = 0;
      const ip = alert.source || "0.0.0.0";
      for (let i = 0; i < ip.length; i++) {
        hash = (hash << 5) - hash + ip.charCodeAt(i);
        hash |= 0;
      }
      
      const pseudoLat = (Math.abs(hash) % 120) - 60; // -60 to +60
      const pseudoLng = (Math.abs(hash * 31) % 360) - 180; // -180 to +180
      
      const countryCode = "UN"; // Unknown
      const originKey = `${pseudoLng},${pseudoLat}`;

      if (!originsMap[originKey]) {
        originsMap[originKey] = {
          country: "Unknown Region",
          code: countryCode,
          flag: "🌍",
          count: 0,
          threatType: alert.attackType,
          color: threatTypeColors[alert.attackType] || threatTypeColors["Malware"],
          coordinates: [pseudoLng, pseudoLat],
          topAsn: "Unknown ASN",
          recentIoc: ip,
        };
      }
      originsMap[originKey].count += 1;

      vectors.push({
        id: alert.id,
        originName: "Unknown Region",
        originCoords: [pseudoLng, pseudoLat],
        destCoords: dynamicSOCDestination.coordinates,
        threatType: alert.attackType,
        severity: alert.severity.toLowerCase(),
        color: threatTypeColors[alert.attackType] || threatTypeColors["Malware"],
        ip: ip,
        target: alert.destination,
        speed: "live",
      });
    });

    const origins = Object.values(originsMap).sort((a, b) => b.count - a.count);
    const total = alerts.length;
    origins.forEach((o) => (o.percentage = ((o.count / total) * 100).toFixed(1)));

    return { dynamicAttackOrigins: origins.slice(0, 15), dynamicAttackVectors: vectors.slice(0, 50) }; // cap vectors for performance
  }, [alerts]);
"""

content = content.replace("export const WorldMapWidget = ({ isLoading, alerts = [] }) => {", "export const WorldMapWidget = ({ isLoading, alerts = [] }) => {" + dynamic_logic)

# 4. Replace mock usages
content = content.replace("mockSOCDestination", "dynamicSOCDestination")
content = content.replace("mockTopAttackOrigins", "dynamicAttackOrigins")
content = content.replace("mockAttackVectors", "dynamicAttackVectors")
content = content.replace("mockAuxiliaryDefenseHubs.map", "[] /* auxiliary hubs removed for real data */ .map")

with open("frontend/src/components/dashboard/WorldMapWidget.jsx", "w") as f:
    f.write(content)

print("Patched WorldMapWidget.jsx")
