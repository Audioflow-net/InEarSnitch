import re

with open("main.py", "r") as f:
    code = f.read()

code = code.replace(
    'self.lbl_selected_musician.setText(f"{c.name} / {c.band}")',
    '# self.lbl_selected_musician.setText(f"{c.name} / {c.band}")  # removed, label no longer exists'
)

with open("main.py", "w") as f:
    f.write(code)

print("Label patched.")
