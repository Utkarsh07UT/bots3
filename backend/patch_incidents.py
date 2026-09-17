import re

with open("frontend/src/components/views/IncidentsView.jsx", "r") as f:
    content = f.read()

# Fix search input class
old_input = 'className="w-full rounded-xl border border-slate-200 py-2 pl-9 pr-3 text-xs dark:border-slate-700 dark:bg-slate-900"'
new_input = 'className="w-full rounded-xl border border-slate-200 py-2 pl-9 pr-3 text-xs bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-slate-700"'
content = content.replace(old_input, new_input)

# Let's check if the text-slate-900 dark:text-slate-100 is needed anywhere else
content = content.replace('<h2 className="text-lg font-bold">', '<h2 className="text-lg font-bold text-slate-900 dark:text-slate-100">')
content = content.replace('<button onClick={onBackToOverview} className="rounded-xl bg-slate-100 px-4 py-2 text-xs font-semibold dark:bg-slate-800">', '<button onClick={onBackToOverview} className="rounded-xl bg-slate-100 px-4 py-2 text-xs font-semibold dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors">')
content = content.replace('bg-slate-100 dark:bg-slate-800"', 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors"')
content = content.replace('<h3 className="mt-1 text-sm font-bold">', '<h3 className="mt-1 text-sm font-bold text-slate-900 dark:text-slate-100">')
content = content.replace('<span className="font-bold">', '<span className="font-bold text-slate-900 dark:text-slate-200">')

with open("frontend/src/components/views/IncidentsView.jsx", "w") as f:
    f.write(content)
