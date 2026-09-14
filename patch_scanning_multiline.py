import re

with open("main.py", "r") as f:
    code = f.read()

# 1. Update set_text to center the text
code = code.replace(
    'text-transform: uppercase;">{txt}</div>',
    'text-transform: uppercase; text-align: center;">{txt}</div>'
)

# 2. Update the string in update_anim_sync
code = code.replace(
    'self.set_text(f"SCANNING {sweep_num}/{self.sweeps}")',
    'self.set_text(f"SCANNING<br><span style=\\"font-size: 48px;\\">{sweep_num}/{self.sweeps}</span>")'
)

with open("main.py", "w") as f:
    f.write(code)

print("Scanning multiline patched.")
