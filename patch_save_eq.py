with open('analysis_ui.py', 'r') as f:
    content = f.read()

content = content.replace(
    'self.btn_save_eq.setStyleSheet("QPushButton { background: #059669; color: white; border-radius: 4px; padding: 4px 8px; font-weight: bold; font-size: 11px; }")',
    'self.btn_save_eq.setProperty("class", "accent")'
)
with open('analysis_ui.py', 'w') as f:
    f.write(content)
print("SUCCESS")
