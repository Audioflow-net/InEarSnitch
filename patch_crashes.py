import re

with open("main.py", "r") as f:
    code = f.read()

# Fix 1: DB column names
code = code.replace(
    "c.execute('SELECT freqs, mag_l, mag_r FROM Measurements WHERE id=?', (data,))",
    "c.execute('SELECT frequencies, magnitude_l, magnitude_r FROM Measurements WHERE id=?', (data,))"
)

# Fix 2: Remove chk_target
code = code.replace(
    "if self.target_freqs is not None and self.target_mags is not None and self.chk_target.isChecked():",
    "if self.target_freqs is not None and self.target_mags is not None:"
)

with open("main.py", "w") as f:
    f.write(code)

print("Crashes patched.")
