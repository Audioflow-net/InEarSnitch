import re

with open('analysis_ui.py', 'r') as f:
    content = f.read()

# Replace the broken theme.get_style with a literal string
bad_style = "theme.get_style('button_tab')"
good_style = '"QPushButton { background: #333; color: white; padding: 4px 8px; border-radius: 4px; } QPushButton:checked { background: #059669; color: white; font-weight: bold; }"'

content = content.replace(bad_style, good_style)

with open('analysis_ui.py', 'w') as f:
    f.write(content)
