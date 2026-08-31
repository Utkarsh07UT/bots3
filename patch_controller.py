import re

with open("backend/app/controller/main_controller.py", "r") as f:
    content = f.read()

content = content.replace(
    'AI_SERVICE_URL = "https://three-1-1oz2.onrender.com"',
    'import os\nAI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "https://bots3-a8ta.onrender.com")'
)

with open("backend/app/controller/main_controller.py", "w") as f:
    f.write(content)
