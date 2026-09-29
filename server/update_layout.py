import os
import re

navbar = '''    <!-- Navbar -->
    <nav class="glass sticky top-0 z-50 px-6 h-[72px] flex items-center justify-between shadow-sm">
        <a href="/" class="flex items-center gap-2">
            <span class="material-symbols-outlined text-primary text-3xl">restaurant_menu</span>
            <span class="text-2xl font-extrabold tracking-tight text-slate-900 mt-1">NIVAALA</span>
        </a>
        <div class="flex items-center gap-6 hidden md:flex">
            <a href="/" class="text-sm font-bold text-slate-600 hover:text-primary transition-colors">Home</a>
            <a href="/search-results" class="text-sm font-bold text-slate-600 hover:text-primary transition-colors">Search</a>
            <a href="/favourites" class="text-sm font-bold text-slate-600 hover:text-primary transition-colors">Saved</a>
            <a href="/login" class="text-sm font-bold text-slate-500 hover:text-primary transition-colors ml-4 border-l border-slate-300 pl-4">Sign In</a>
        </div>
    </nav>
'''

files = [
    'c:/Users/dixit/Music/Bhookh.exe/server/api/templates/search-results.html',
    'c:/Users/dixit/Music/Bhookh.exe/server/api/templates/profile.html',
    'c:/Users/dixit/Music/Bhookh.exe/server/api/templates/index.html',
    'c:/Users/dixit/Music/Bhookh.exe/server/api/templates/favourites.html',
]

for f in files:
    if not os.path.exists(f):
        continue
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Standardize body class for background
    content = re.sub(r'bg-slate-50', 'bg-surface', content)
    
    # Replace existing nav with standardized nav
    if '<nav class="glass' in content:
        content = re.sub(r'<nav class="glass.*?</nav>', navbar, content, flags=re.DOTALL)
    elif '<body' in content and 'index.html' in f:
        # For index.html, inject it after body and remove absolute logo
        content = re.sub(r'(<body[^>]*>)', r'\1\n' + navbar, content)
        content = re.sub(r'<div class="absolute top-6 left-6 flex items-center gap-2">.*?</div>', '', content, flags=re.DOTALL)

    # Convert common rounded-xl/2xl to 3xl for cards in html
    content = re.sub(r'rounded-2xl', 'rounded-3xl', content)
    
    # Inject footer before closing body
    if 'footer' not in content:
        footer = '''
    <footer class="hidden md:block py-8 text-center text-slate-500 text-sm mt-auto border-t border-slate-200 bg-white/50">
        © 2026 NIVAALA. Eat with confidence.
    </footer>
'''
        content = content.replace('</body>', footer + '</body>')

    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)

print('Standardized Navbars, Footer, and Background across main pages.')
