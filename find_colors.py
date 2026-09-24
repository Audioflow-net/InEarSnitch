import re

with open("history_ui.py", "r") as f:
    text = f.read()

colors = re.findall(r'#[0-9a-fA-F]{3,6}', text)
for c in sorted(set(colors)):
    print(c)
