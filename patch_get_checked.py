import re

with open("history_ui.py", "r") as f:
    code = f.read()

code = code.replace("widget = self.table.cellWidget(i, 3)", "widget = self.table.cellWidget(i, 5)")

with open("history_ui.py", "w") as f:
    f.write(code)

print("Checked rows patched.")
