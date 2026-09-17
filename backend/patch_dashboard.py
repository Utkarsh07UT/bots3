import re

with open("frontend/src/pages/DashboardPage.jsx", "r") as f:
    content = f.read()

# Add import
import_statement = 'import { AIAssistantBot } from "../components/dashboard/AIAssistantBot";\n'
content = content.replace('import { Toast } from "../components/common/Toast";', 'import { Toast } from "../components/common/Toast";\n' + import_statement)

# Add component at the end of the return statement
content = content.replace('    </div>\n  );\n};\n', '      <AIAssistantBot />\n    </div>\n  );\n};\n')

with open("frontend/src/pages/DashboardPage.jsx", "w") as f:
    f.write(content)
