import re
import glob

files_to_update = ["frontend/.env", "frontend/.env.example"]
for filepath in files_to_update:
    try:
        with open(filepath, "r") as f:
            content = f.read()
            
        content = content.replace("https://three-1-1oz2.onrender.com", "https://cyber-threat-detection-backend-z6ta.onrender.com")
        content = content.replace("wss://three-1-1oz2.onrender.com", "wss://cyber-threat-detection-backend-z6ta.onrender.com")
        
        with open(filepath, "w") as f:
            f.write(content)
        print(f"Updated {filepath}")
    except FileNotFoundError:
        pass
