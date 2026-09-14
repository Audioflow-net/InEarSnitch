import re

with open("main.py", "r") as f:
    code = f.read()

old_dimmer = """        self.settings_dimmer.setStyleSheet("background: transparent; border: none;")"""
new_dimmer = """        self.settings_dimmer.setStyleSheet("background: rgba(0, 0, 0, 0.6); border: none;")"""
code = code.replace(old_dimmer, new_dimmer)

with open("main.py", "w") as f:
    f.write(code)

print("Dimmer alpha patched.")
