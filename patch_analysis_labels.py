import re

with open("analysis_ui.py", "r") as f:
    code = f.read()

code = re.sub(r'        sel_layout\.addWidget\(QLabel\("Target:".*?\)\n', '', code)
code = re.sub(r'        sel_layout\.addWidget\(QLabel\("History:".*?\)\n', '', code)

with open("analysis_ui.py", "w") as f:
    f.write(code)

print("Analysis labels removed.")
