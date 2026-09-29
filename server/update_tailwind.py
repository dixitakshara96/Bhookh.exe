import os
import re

files = [
    'c:/Users/dixit/Music/Bhookh.exe/server/api/templates/search-results.html',
    'c:/Users/dixit/Music/Bhookh.exe/server/api/templates/profile.html',
    'c:/Users/dixit/Music/Bhookh.exe/server/api/templates/index.html',
    'c:/Users/dixit/Music/Bhookh.exe/server/api/templates/login.html',
    'c:/Users/dixit/Music/Bhookh.exe/server/api/templates/dish-details.html',
    'c:/Users/dixit/Music/Bhookh.exe/server/api/templates/favourites.html',
    'c:/Users/dixit/Music/Bhookh.exe/server/api/templates/partials/dish_details.html',
    'c:/Users/dixit/Music/Bhookh.exe/server/api/templates/partials/dish_list.html',
    'c:/Users/dixit/Music/Bhookh.exe/server/api/templates/partials/review_item.html',
    'c:/Users/dixit/Music/Bhookh.exe/server/api/templates/partials/review_list.html'
]

new_config = '''<script id="tailwind-config">
        tailwind.config = {
            theme: {
                extend: {
                    fontFamily: { sans: ['Outfit', 'sans-serif'] },
                    colors: { 
                        primary: "#16A34A", 
                        "primary-dark": "#15803D", 
                        accent: "#F59E0B",
                        "accent-dark": "#D97706",
                        surface: "#F8FAF8", 
                        "surface-dark": "#e2e8f0" 
                    },
                    borderRadius: {
                        'xl': '24px',
                        '2xl': '24px',
                        '3xl': '24px',
                        '4xl': '24px'
                    },
                    boxShadow: {
                        'sm': '0 2px 8px rgba(22, 163, 74, 0.04)',
                        'md': '0 4px 16px rgba(22, 163, 74, 0.08)',
                        'lg': '0 10px 24px rgba(22, 163, 74, 0.12)',
                        'xl': '0 20px 40px rgba(22, 163, 74, 0.16)',
                        '2xl': '0 25px 50px rgba(22, 163, 74, 0.20)',
                    }
                }
            }
        }
    </script>'''

for f in files:
    if not os.path.exists(f):
        continue
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Replace config
    content = re.sub(r'<script id="tailwind-config">.*?</script>', new_config, content, flags=re.DOTALL)
    
    # Replace buttons styles that were hardcoded to rounded-lg or rounded-md to rounded-xl
    # to enforce the 24px rule
    content = re.sub(r'rounded-lg(?!])', 'rounded-xl', content)
    content = re.sub(r'rounded-md(?!])', 'rounded-xl', content)
    
    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)

print('Tailwind config updated in all templates with consistent radius and shadows.')
