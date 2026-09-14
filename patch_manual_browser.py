with open('main.py', 'r') as f:
    content = f.read()

content = content.replace(
    'self.manual_browser.setStyleSheet(\n            "background: #18181b; color: #ddd; border: 1px solid #333; "\n            "border-radius: 4px; padding: 10px;"\n        )',
    'self.manual_browser.setStyleSheet(f"background-color: {theme.get_color(\'bg_main\')}; color: {theme.get_color(\'text_primary\')}; border: 1px solid {theme.get_color(\'border\')}; border-radius: 4px; padding: 10px;")'
)

with open('main.py', 'w') as f:
    f.write(content)
print("SUCCESS")
