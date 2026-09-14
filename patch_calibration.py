with open('calibration_ui.py', 'r') as f:
    content = f.read()

content = content.replace('self.setStyleSheet("background-color: #18181b; color: white;")', '')
content = content.replace("setPen('w')", "setPen(theme.get_color('pg_fg'))")
content = content.replace("pg.mkPen('#00FFFF', width=2)", "pg.mkPen(theme.get_color('accent'), width=2)")
content = content.replace('self.load_button.setStyleSheet("background-color: #333333; padding: 5px;")', 'self.load_button.setStyleSheet("padding: 5px;")')
content = content.replace('self.apply_button.setStyleSheet("background-color: #333333; padding: 5px;")', 'self.apply_button.setStyleSheet("padding: 5px;")')
content = content.replace('self.gen_button.setStyleSheet("background-color: #008888; padding: 5px; font-weight: bold;")', 'self.gen_button.setProperty("class", "accent")')

with open('calibration_ui.py', 'w') as f:
    f.write(content)
print("SUCCESS")
