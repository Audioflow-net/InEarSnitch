import re

with open("main.py", "r") as f:
    code = f.read()

code = code.replace(
"""        # Draw last 3 historical measurements faintly in the background
        if getattr(self, 'current_iem_id', None):


        # Now draw the current live measurement on top""",
"""        # Now draw the current live measurement on top"""
)

with open("main.py", "w") as f:
    f.write(code)

print("Indentation fixed.")
