with open('main.py', 'r') as f:
    content = f.read()

content = content.replace(
    'page_set.setStyleSheet("#SettingsPanel { background-color: #1a1a1e; border-left: 1px solid #333; }")', 
    'page_set.setStyleSheet(f"#SettingsPanel {{ background-color: {theme.get_color(\'bg_panel\')}; border-left: 1px solid {theme.get_color(\'border\')}; }}")'
)

with open('main.py', 'w') as f:
    f.write(content)
print("SUCCESS")
