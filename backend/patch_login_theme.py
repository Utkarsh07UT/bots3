import re

with open("frontend/src/pages/LoginPage.jsx", "r") as f:
    content = f.read()

# Left panel container
content = content.replace(
    'bg-gradient-to-br from-slate-900 via-[#0B1120] to-[#070A12] text-white p-8 sm:p-12 lg:p-16 flex flex-col justify-between overflow-hidden border-b lg:border-b-0 lg:border-r border-slate-800',
    'bg-gradient-to-br from-blue-50/50 via-white to-slate-50 dark:from-slate-900 dark:via-[#0B1120] dark:to-[#070A12] text-slate-900 dark:text-white p-8 sm:p-12 lg:p-16 flex flex-col justify-between overflow-hidden border-b lg:border-b-0 lg:border-r border-slate-200 dark:border-slate-800'
)

# Brand Logo
content = content.replace(
    'from-white via-slate-100 to-blue-200',
    'from-blue-900 via-blue-800 to-blue-600 dark:from-white dark:via-slate-100 dark:to-blue-200'
)

# Enterprise SOC badge
content = content.replace(
    'bg-blue-500/20 text-blue-300 border border-blue-400/30',
    'bg-blue-100 dark:bg-blue-500/20 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-400/30'
)

# Text slate 400
content = content.replace(
    'text-slate-400 font-medium',
    'text-slate-600 dark:text-slate-400 font-medium'
)
content = content.replace(
    'text-slate-400 leading-relaxed',
    'text-slate-600 dark:text-slate-400 leading-relaxed'
)
content = content.replace(
    'text-slate-400 uppercase tracking-wider',
    'text-slate-500 dark:text-slate-400 uppercase tracking-wider'
)

# Middle Hero Badge
content = content.replace(
    'bg-blue-500/10 border border-blue-500/30 text-blue-300',
    'bg-blue-50 dark:bg-blue-500/10 border border-blue-200 dark:border-blue-500/30 text-blue-700 dark:text-blue-300'
)

# Hero Gradient
content = content.replace(
    'from-blue-400 via-indigo-300 to-sky-400',
    'from-blue-600 via-indigo-500 to-sky-500 dark:from-blue-400 dark:via-indigo-300 dark:to-sky-400'
)

# Mini metrics container
content = content.replace(
    'bg-white/[0.04] border border-white/[0.08]',
    'bg-white/60 dark:bg-white/[0.04] border border-slate-200 dark:border-white/[0.08]'
)
content = content.replace(
    'border-white/10',
    'border-slate-200 dark:border-white/10'
)

# Metric colors
content = content.replace(
    'text-blue-400 font-mono',
    'text-blue-600 dark:text-blue-400 font-mono'
)
content = content.replace(
    'text-emerald-400 font-mono',
    'text-emerald-600 dark:text-emerald-400 font-mono'
)
content = content.replace(
    'text-amber-400 font-mono',
    'text-amber-600 dark:text-amber-400 font-mono'
)

# Footer badges
content = content.replace(
    'border-slate-800/80',
    'border-slate-200 dark:border-slate-800/80'
)

with open("frontend/src/pages/LoginPage.jsx", "w") as f:
    f.write(content)
