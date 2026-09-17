with open("frontend/src/components/dashboard/WorldMapWidget.jsx", "r") as f:
    content = f.read()

content = content.replace('className={`transition-colors duration-150 cursor-pointer ${isHovered ? "fill-slate-200 dark:fill-[#2C384E]" : "fill-white dark:fill-[#1A2234]"}`}\n                  className="stroke-slate-300 dark:stroke-[#2E3C56]"', 
'className={`transition-colors duration-150 cursor-pointer stroke-slate-300 dark:stroke-[#2E3C56] ${isHovered ? "fill-slate-200 dark:fill-[#2C384E]" : "fill-slate-100 dark:fill-[#1A2234]"}`}')

with open("frontend/src/components/dashboard/WorldMapWidget.jsx", "w") as f:
    f.write(content)
