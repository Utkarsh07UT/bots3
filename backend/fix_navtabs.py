with open("frontend/src/data/mockData.js", "r") as f:
    content = f.read()

content = content.replace('export const navTabs = [\n  { id: "system-status", label: "AI Architecture" },\n  { id: "overview", label: "Overview" },\n  { id: "threat-feed", label: "Threat Feed" },\n  { id: "incidents", label: "Incidents", count: 12 },\n];', 
'export const navTabs = [\n  { id: "overview", label: "Overview" },\n  { id: "threat-feed", label: "Threat Feed" },\n  { id: "incidents", label: "Incidents", count: 12 },\n  { id: "system-status", label: "AI Architecture" },\n];')

with open("frontend/src/data/mockData.js", "w") as f:
    f.write(content)
