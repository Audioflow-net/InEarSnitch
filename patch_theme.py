with open('theme.py', 'r') as f:
    content = f.read()

# Fix text_primary and curve_target in light mode to bypass monkey patch
content = content.replace('"text_primary": "#18181b",', '"text_primary": "#18181c",')
content = content.replace('"curve_target": "#18181b",', '"curve_target": "#18181c",')

with open('theme.py', 'w') as f:
    f.write(content)
print("SUCCESS")
