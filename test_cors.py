import re

origin = "https://frontend-zeta-three-69.vercel.app"
allow_origin_regex = r"https://.*\.vercel\.app|https://.*\.onrender\.com"

regex = re.compile(allow_origin_regex)
print(f"Match: {bool(regex.match(origin))}")
print(f"Fullmatch: {bool(regex.fullmatch(origin))}")
