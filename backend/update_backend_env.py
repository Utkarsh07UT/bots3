with open("backend/.env", "r") as f:
    lines = f.readlines()

output = []
for line in lines:
    output.append(line)
    if line.startswith("API_PORT="):
        output.append("\n# External Service URLs\n")
        output.append("AI_SERVICE_URL=https://bots3-a8ta.onrender.com\n")
        output.append("BACKGROUND_WORKER_URL=https://cyber-threat-detection-background-worker.onrender.com\n")

with open("backend/.env", "w") as f:
    f.writelines(output)
with open("backend/.env.example", "w") as f:
    f.writelines(output)
