with open("frontend/src/components/dashboard/WorldMapWidget.jsx", "r") as f:
    content = f.read()

# Fix deep space radial glow
old_bg = '<div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_45%,#1E293B_0%,#090D16_80%)] pointer-events-none opacity-90" />'
new_bg = '<div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_45%,#E2E8F0_0%,#F8FAFC_80%)] dark:bg-[radial-gradient(circle_at_50%_45%,#1E293B_0%,#090D16_80%)] pointer-events-none opacity-90" />'
content = content.replace(old_bg, new_bg)

# The crosshair grid overlay had opacity-10, we could make it slightly different for light mode
old_crosshair = '<div\n          className="absolute inset-0 opacity-10 pointer-events-none"\n          style={{\n            backgroundImage: `radial-gradient(circle, #38BDF8 1px, transparent 1px)`,\n            backgroundSize: "28px 28px",\n          }}\n        />'
new_crosshair = '<div\n          className="absolute inset-0 opacity-20 dark:opacity-10 pointer-events-none"\n          style={{\n            backgroundImage: `radial-gradient(circle, #38BDF8 1px, transparent 1px)`,\n            backgroundSize: "28px 28px",\n          }}\n        />'
content = content.replace(old_crosshair, new_crosshair)

with open("frontend/src/components/dashboard/WorldMapWidget.jsx", "w") as f:
    f.write(content)
