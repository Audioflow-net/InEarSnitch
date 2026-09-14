import re

with open("main.py", "r") as f:
    code = f.read()

code = code.replace(
    'report_l = Analyzer.absolute_checks(freqs, self.temp_mag_l, "Left")',
    'report_l = Analyzer.absolute_checks(freqs, self.temp_mag_l, self.temp_ir_l, "Left")'
)

code = code.replace(
    'report_r = Analyzer.absolute_checks(freqs, self.temp_mag_r, "Right")',
    'report_r = Analyzer.absolute_checks(freqs, self.temp_mag_r, self.temp_ir_r, "Right")'
)

with open("main.py", "w") as f:
    f.write(code)

print("Main polarity patched.")
