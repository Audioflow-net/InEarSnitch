import re

with open("main.py", "r") as f:
    code = f.read()

code = code.replace(
    '{txt}</div>',
    '<center>{txt}</center></div>'
)

with open("main.py", "w") as f:
    f.write(code)

print("Center tag added.")
