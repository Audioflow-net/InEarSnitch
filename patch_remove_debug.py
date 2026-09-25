import re

with open("analysis_ui.py", "r") as f:
    content = f.read()

content = content.replace("        print('[DEBUG] refresh_view called!')\n", "")

with open("analysis_ui.py", "w") as f:
    f.write(content)
