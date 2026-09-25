import re

with open("main.py", "r") as f:
    content = f.read()

content = content.replace("profile_bar.setMinimumWidth(220)", "profile_bar.setMinimumWidth(240)")
content = content.replace("profile_bar.setMaximumWidth(320)", "profile_bar.setMaximumWidth(340)")

with open("main.py", "w") as f:
    f.write(content)
