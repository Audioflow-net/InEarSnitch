import re

with open('main.py', 'r') as f:
    content = f.read()

old_style = r'self\.btn_live_seal\.setStyleSheet\("QPushButton \{ background-color: #333;.*?"\)'
new_style = 'self.btn_live_seal.setStyleSheet("QPushButton { background-color: #db2777; color: white; font-weight: bold; font-size: 13px; border-radius: 6px; border: none; } QPushButton:hover { background-color: #be185d; } QPushButton:checked { background-color: #fbcfe8; color: #831843; border: 2px solid #db2777; }")'

content = re.sub(old_style, new_style, content)

with open('main.py', 'w') as f:
    f.write(content)
