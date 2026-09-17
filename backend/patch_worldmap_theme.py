import re

with open("frontend/src/components/dashboard/WorldMapWidget.jsx", "r") as f:
    content = f.read()

# 1. SVG graticule
content = content.replace('stroke="#1E293B"', 'className="stroke-slate-200 dark:stroke-[#1E293B]"')

# 2. SVG countries
content = content.replace('fill={isHovered ? "#2C384E" : "#1A2234"}', 'className={`transition-colors duration-150 cursor-pointer ${isHovered ? "fill-slate-200 dark:fill-[#2C384E]" : "fill-white dark:fill-[#1A2234]"}`}')
content = content.replace('stroke="#2E3C56"', 'className="stroke-slate-300 dark:stroke-[#2E3C56]"')
# Note: we also have className="transition-colors duration-150 cursor-pointer" on the line below in the original, we should remove the duplicate or just replace both.
content = re.sub(r'className="transition-colors duration-150 cursor-pointer"\s*', '', content)

# 3. SVG borders
content = content.replace('stroke="#334155"', 'className="stroke-slate-300 dark:stroke-[#334155]"')

# 4. Top-right legend/stats overlay
content = content.replace('bg-slate-900/90 dark:bg-[#12151C]/90 backdrop-blur-md rounded-xl border border-slate-800/90', 'bg-white/90 dark:bg-[#12151C]/90 backdrop-blur-md rounded-xl border border-slate-200 dark:border-slate-800/90')
content = content.replace('border-slate-800"', 'border-slate-200 dark:border-slate-800"')
content = content.replace('border-slate-800 ', 'border-slate-200 dark:border-slate-800 ')
content = content.replace('text-slate-300 ', 'text-slate-700 dark:text-slate-300 ')
content = content.replace('text-slate-200 ', 'text-slate-800 dark:text-slate-200 ')

# 5. Bottom-left toolbar overlay
content = content.replace('bg-slate-900/90 dark:bg-[#12151C]/90 backdrop-blur-md p-1.5 rounded-xl border border-slate-800', 'bg-white/90 dark:bg-[#12151C]/90 backdrop-blur-md p-1.5 rounded-xl border border-slate-200 dark:border-slate-800')

# 6. Button hovers inside toolbars
content = content.replace('hover:bg-slate-800 ', 'hover:bg-slate-100 dark:hover:bg-slate-800 ')
content = content.replace('hover:bg-slate-800"', 'hover:bg-slate-100 dark:hover:bg-slate-800"')
content = content.replace('hover:text-white', 'hover:text-slate-900 dark:hover:text-white')

# 7. Hover tooltips and popovers
content = content.replace('bg-slate-950/95 text-white', 'bg-white/95 dark:bg-slate-950/95 text-slate-900 dark:text-white')
content = content.replace('border-slate-700', 'border-slate-200 dark:border-slate-700')
content = content.replace('bg-slate-900/98 text-white', 'bg-white/98 dark:bg-slate-900/98 text-slate-900 dark:text-white')
content = content.replace('text-slate-100"', 'text-slate-900 dark:text-slate-100"')
content = content.replace('bg-slate-800 ', 'bg-slate-100 dark:bg-slate-800 ')
content = content.replace('bg-slate-800"', 'bg-slate-100 dark:bg-slate-800"')

with open("frontend/src/components/dashboard/WorldMapWidget.jsx", "w") as f:
    f.write(content)

print("Patched WorldMapWidget.jsx colors")
