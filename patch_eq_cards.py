import re

with open('analysis_ui.py', 'r') as f:
    content = f.read()

# Fix card text color
content = content.replace(
    'lbl.setStyleSheet("font-weight: bold; font-size: 11px; color: #eee; border: none;")',
    'lbl.setStyleSheet(f"font-weight: bold; font-size: 11px; color: {theme.get_color(\'text_primary\')}; border: none;")'
)

# Fix mini_plot background
content = content.replace(
    "mini_plot.setBackground('#222')",
    "mini_plot.setBackground(theme.get_color('bg_main'))"
)

# Fix mini_plot line color
content = content.replace(
    "pen=pg.mkPen('#0ea5e9', width=1.5)",
    "pen=pg.mkPen(theme.get_color('accent'), width=2)"
)

# Fix buttons
content = content.replace(
    'btn_load.setStyleSheet("QPushButton { background: #0284c7; color: white; border-radius: 4px; padding: 2px 8px; font-size: 10px; font-weight: bold; } QPushButton:hover { background: #0369a1; }")',
    'btn_load.setProperty("class", "accent")'
)

content = content.replace(
    'btn_del.setStyleSheet("QPushButton { background: transparent; color: #ef4444; border-radius: 4px; padding: 2px 6px; font-size: 10px; font-weight: bold; } QPushButton:hover { background: #fef2f2; }")',
    'btn_del.setProperty("class", "danger")'
)

with open('analysis_ui.py', 'w') as f:
    f.write(content)
print("SUCCESS")
