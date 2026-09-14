import re

with open("main.py", "r") as f:
    code = f.read()

code = code.replace(
    "c.execute('SELECT freqs, mag_l, mag_r, gain_db FROM Measurements WHERE iem_id = ? ORDER BY timestamp DESC LIMIT 1', (self.current_iem_id,))",
    "c.execute('SELECT frequencies, magnitude_l, magnitude_r, gain_db FROM Measurements WHERE iem_id = ? ORDER BY timestamp DESC LIMIT 1', (self.current_iem_id,))"
)

with open("main.py", "w") as f:
    f.write(code)

print("Second crash patched.")
