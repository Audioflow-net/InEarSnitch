import re

with open("main.py", "r") as f:
    content = f.read()

content = content.replace("profile_bar.setFixedWidth(220)", "profile_bar.setMinimumWidth(170)\n        profile_bar.setMaximumWidth(280)")

with open("main.py", "w") as f:
    f.write(content)
