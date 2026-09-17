import re

with open("frontend/src/pages/DashboardPage.jsx", "r") as f:
    content = f.read()

# Add import
import_statement = 'import { SystemArchitectureView } from "../components/views/SystemArchitectureView";\n'
content = content.replace('import { IncidentsView } from "../components/views/IncidentsView";', 'import { IncidentsView } from "../components/views/IncidentsView";\n' + import_statement)

# Add component rendering
render_block = '''
        {activeTab === "system-status" && (
          <SystemArchitectureView />
        )}
'''
content = content.replace('        {activeTab === "incidents" && (\n          <IncidentsView onBackToOverview={() => setActiveTab("overview")} items={feed} />\n        )}', 
'        {activeTab === "incidents" && (\n          <IncidentsView onBackToOverview={() => setActiveTab("overview")} items={feed} />\n        )}\n' + render_block)

with open("frontend/src/pages/DashboardPage.jsx", "w") as f:
    f.write(content)
