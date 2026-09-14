import sys

with open('analysis_ui.py', 'r') as f:
    content = f.read()

# Pass csd_data into run_full_diagnostics
old_call = "report = Analyzer.run_full_diagnostics(freqs, mag_l, mag_r, best_ref_l, best_ref_r, ir_l_f, ir_r_f, thd_data)"
new_call = "report = Analyzer.run_full_diagnostics(freqs, mag_l, mag_r, best_ref_l, best_ref_r, ir_l_f, ir_r_f, thd_data, csd_data)"
content = content.replace(old_call, new_call)

with open('analysis_ui.py', 'w') as f:
    f.write(content)
