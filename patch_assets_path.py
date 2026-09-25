import re

with open("main.py", "r") as f:
    content = f.read()

old_path = 'img_path = os.path.join("assets", "tips", img_name) if img_name else None'
new_path = 'img_path = os.path.join(os.path.dirname(__file__), "assets", "tips", img_name) if img_name else None'

content = content.replace(old_path, new_path)

with open("main.py", "w") as f:
    f.write(content)
