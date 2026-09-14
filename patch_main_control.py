import re

with open("main.py", "r") as f:
    code = f.read()

# 1. Update initial style
old_style_1 = 'self.control_panel.setStyleSheet("#ControlPanel { background-color: #222; border-radius: 8px; }")'
new_style_1 = 'self.control_panel.setStyleSheet("#ControlPanel { background-color: #222; border: 1px solid #444; border-radius: 4px; }")'
code = code.replace(old_style_1, new_style_1)

# 2. Update dynamic style
old_style_2 = 'self.control_panel.setStyleSheet(f"#ControlPanel {{ background-color: {panel_bg}; border-top: 1px solid {border}; border-radius: 8px; }}")'
new_style_2 = 'self.control_panel.setStyleSheet(f"#ControlPanel {{ background-color: {panel_bg}; border: 1px solid {border}; border-radius: 4px; }}")'
code = code.replace(old_style_2, new_style_2)

with open("main.py", "w") as f:
    f.write(code)
