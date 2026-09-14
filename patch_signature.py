import sys

with open('analysis.py', 'r') as f:
    content = f.read()

old_sig = "    def run_full_diagnostics(freqs, mag_l, mag_r, ref_mag_l=None, ref_mag_r=None, ir_l=None, ir_r=None, thd_data=None):"
new_sig = "    def run_full_diagnostics(freqs, mag_l, mag_r, ref_mag_l=None, ref_mag_r=None, ir_l=None, ir_r=None, thd_data=None, csd_data=None):"

content = content.replace(old_sig, new_sig)

with open('analysis.py', 'w') as f:
    f.write(content)
