import re

with open("frontend/src/components/dashboard/WorldMapWidget.jsx", "r") as f:
    content = f.read()

# Fix duplicates
content = re.sub(r'dark:hover:bg-slate-100\s+dark:hover:bg-slate-100\s+dark:bg-slate-800', 'dark:hover:bg-slate-800', content)
content = re.sub(r'dark:hover:bg-slate-100\s+dark:bg-slate-800', 'dark:hover:bg-slate-800', content)
content = re.sub(r'hover:bg-slate-100\s+dark:hover:bg-slate-100\s+dark:bg-slate-800', 'hover:bg-slate-100 dark:hover:bg-slate-800', content)
content = re.sub(r'dark:hover:bg-slate-100\s+dark:hover:bg-slate-100', 'dark:hover:bg-slate-800', content)

content = re.sub(r'dark:text-slate-700\s+dark:text-slate-300', 'dark:text-slate-300', content)
content = re.sub(r'dark:text-slate-800\s+dark:text-slate-200', 'dark:text-slate-200', content)
content = re.sub(r'dark:border-slate-200\s+dark:border-slate-800', 'dark:border-slate-800', content)
content = re.sub(r'dark:border-slate-200\s+dark:border-slate-700', 'dark:border-slate-700', content)
content = re.sub(r'dark:hover:text-slate-900\s+dark:hover:text-white', 'dark:hover:text-white', content)
content = re.sub(r'dark:bg-slate-100\s+dark:bg-slate-800', 'dark:bg-slate-800', content)

with open("frontend/src/components/dashboard/WorldMapWidget.jsx", "w") as f:
    f.write(content)
