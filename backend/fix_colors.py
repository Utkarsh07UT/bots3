with open("frontend/src/components/dashboard/WorldMapWidget.jsx", "r") as f:
    content = f.read()

helper = """
    const getColor = (type) => {
      const t = (type || "").toLowerCase();
      if (t.includes("ransom")) return "#3B82F6";
      if (t.includes("phish")) return "#EF4444";
      if (t.includes("brute") || t.includes("c2")) return "#F97316";
      if (t.includes("ddos") || t.includes("flood")) return "#EAB308";
      return "#10B981"; // malware/default
    };
"""

content = content.replace("const vectors = [];", helper + "\n    const vectors = [];")
content = content.replace("color: threatTypeColors[alert.attackType] || threatTypeColors[\"Malware\"],", "color: getColor(alert.attackType),")

with open("frontend/src/components/dashboard/WorldMapWidget.jsx", "w") as f:
    f.write(content)
