with open("backend/.env", "r") as f:
    content = f.read()

content = content.replace("https://your-project-id.supabase.co", "https://focoivjprqtixbtobpmb.supabase.co")

with open("backend/.env", "w") as f:
    f.write(content)
    
with open("backend/.env.example", "r") as f:
    content = f.read()

content = content.replace("https://your-project-id.supabase.co", "https://focoivjprqtixbtobpmb.supabase.co")

with open("backend/.env.example", "w") as f:
    f.write(content)
