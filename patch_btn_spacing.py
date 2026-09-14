import re

with open("history_ui.py", "r") as f:
    code = f.read()

# 1. Change Spacing
code = code.replace("right_edit_layout.setSpacing(10)", "right_edit_layout.setSpacing(6)")

# 2. Change Padding
code = code.replace("padding: 6px 12px;", "padding: 6px 6px;")

# 3. Change Button Text
code = code.replace('QPushButton("⎘ EXPORT CSV")', 'QPushButton("Export CSV")')
code = code.replace('QPushButton("⤓ SAVE TARGET")', 'QPushButton("Save Target")')
code = code.replace('QPushButton("🗑 DELETE")', 'QPushButton("🗑 Delete")')

with open("history_ui.py", "w") as f:
    f.write(code)
