import re

with open("analysis_ui.py", "r") as f:
    content = f.read()

content = content.replace("def refresh_view(self):", "def refresh_view(self):\n        print('[DEBUG] refresh_view called!')")

with open("analysis_ui.py", "w") as f:
    f.write(content)
