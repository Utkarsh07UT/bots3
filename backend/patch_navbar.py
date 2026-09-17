import re

with open("frontend/src/pages/DashboardPage.jsx", "r") as f:
    content = f.read()
content = content.replace("<Navbar activeTab={activeTab} onTabChange={setActiveTab} />", "<Navbar activeTab={activeTab} onTabChange={setActiveTab} activeIncidents={insight?.active || 0} />")
with open("frontend/src/pages/DashboardPage.jsx", "w") as f:
    f.write(content)

with open("frontend/src/components/layout/Navbar.jsx", "r") as f:
    nav_content = f.read()

# Replace signature
nav_content = nav_content.replace("export const Navbar = ({ activeTab, onTabChange }) => {", "export const Navbar = ({ activeTab, onTabChange, activeIncidents = 0 }) => {")

# Find where tab.count is rendered and replace it for 'incidents'
nav_content = nav_content.replace("{tab.count !== undefined && (", "{ (tab.id === 'incidents' ? activeIncidents > 0 : tab.count !== undefined) && (")
nav_content = nav_content.replace("{tab.count}", "{tab.id === 'incidents' ? activeIncidents : tab.count}")

with open("frontend/src/components/layout/Navbar.jsx", "w") as f:
    f.write(nav_content)

print("Patched Navbar.jsx")
