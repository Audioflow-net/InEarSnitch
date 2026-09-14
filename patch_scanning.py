import re

with open("main.py", "r") as f:
    code = f.read()

code = code.replace(
    'self.set_text(f"SWEEP {sweep_num} / {self.sweeps}")',
    'self.set_text(f"SCANNING {sweep_num}/{self.sweeps}")'
)

with open("main.py", "w") as f:
    f.write(code)

print("Scanning patched.")
