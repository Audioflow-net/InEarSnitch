import re

with open("main.py", "r") as f:
    code = f.read()

code = code.replace(
    'self.lbl_active_profile.setStyleSheet("color: #00FF99; font-size: 13px; font-weight: bold; margin-right: 15px;")',
    'self.lbl_active_profile.setStyleSheet("color: #00FF99; font-size: 13px; font-weight: bold;")'
)

with open("main.py", "w") as f:
    f.write(code)

print("Margin removed from dynamic update.")
