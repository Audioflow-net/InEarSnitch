import sys

with open('analysis_ui.py', 'r') as f:
    content = f.read()

old_align = """            meas_val = mag_l[idx_1k] if mag_l is not None else (mag_r[idx_1k] if mag_r is not None else 80)
            tgt_val = interp_tgt[idx_1k]"""

new_align = """            meas_val = mag_l[idx_1k] if mag_l is not None else (mag_r[idx_1k] if mag_r is not None else 80)
            if meas_val < 30 or meas_val > 140:
                meas_val = 80  # Prevent aligning target to silence or garbage
            tgt_val = interp_tgt[idx_1k]"""

content = content.replace(old_align, new_align)

with open('analysis_ui.py', 'w') as f:
    f.write(content)
