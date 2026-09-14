import re

with open('analysis_ui.py', 'r') as f:
    content = f.read()

pattern = r"(meas_val = mag_l\[idx_1k\].*?)\n(\s*tgt_val = interp_tgt\[idx_1k\])"
replacement = r"\1\n\2\n        if meas_val < 30 or meas_val > 140:\n            meas_val = 80"

# Actually, the logic needs to happen BEFORE tgt_val is subtracted from meas_val
pattern2 = r"(meas_val = mag_l\[idx_1k\] if mag_l is not None else \(mag_r\[idx_1k\] if mag_r is not None else 80\))\n(\s*if meas_val < 30 or meas_val > 140:\n\s*meas_val = 80\s*\n\s*)?(tgt_val = interp_tgt\[idx_1k\])"

def repl(m):
    return m.group(1) + "\n" + (" " * 16) + "if meas_val < 30 or meas_val > 140:\n" + (" " * 20) + "meas_val = 80\n" + (" " * 16) + m.group(3)

content = re.sub(pattern2, repl, content)

with open('analysis_ui.py', 'w') as f:
    f.write(content)
