import re

with open("analysis_ui.py", "r") as f:
    code = f.read()

old_pane = "border-bottom: none; border-top-left-radius: 4px; border-top-right-radius: 4px; border-bottom-left-radius: 0px; border-bottom-right-radius: 0px;"
new_pane = "border-radius: 4px;"

code = code.replace(old_pane, new_pane)

with open("analysis_ui.py", "w") as f:
    f.write(code)
