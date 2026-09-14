import re

with open("theme.py", "r") as f:
    code = f.read()

old_style = "selection-background-color: {get_color('accent')};\n        selection-color: white;"
new_style = "selection-background-color: {get_color('bg_hover')};\n        selection-color: {get_color('text_primary')};"
code = code.replace(old_style, new_style)

with open("theme.py", "w") as f:
    f.write(code)
