with open("frontend/.env", "r") as f:
    lines = f.readlines()

output = []
for line in lines:
    if line.startswith("VITE_WS_URL="):
        output.append(line)
        output.append("\n# Backend Background Worker URL\n")
        output.append("VITE_BACKGROUND_WORKER_URL=https://cyber-threat-detection-background-worker.onrender.com\n")
        output.append("\n# AI Model API URL\n")
        output.append("VITE_AI_SERVICE_URL=https://bots3-a8ta.onrender.com\n")
    else:
        output.append(line)

with open("frontend/.env", "w") as f:
    f.writelines(output)
with open("frontend/.env.example", "w") as f:
    f.writelines(output)
