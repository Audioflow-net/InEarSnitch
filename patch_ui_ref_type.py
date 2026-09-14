import sys

with open('analysis_ui.py', 'r') as f:
    content = f.read()

old_call = "        report = Analyzer.run_full_diagnostics(freqs, mag_l, mag_r, best_ref_l, best_ref_r, ir_l_f, ir_r_f, thd_data, csd_data)"
new_call = """        ref_type = 'target' if (tgt_freqs is not None and tgt_mags is not None) else 'history'
        report = Analyzer.run_full_diagnostics(freqs, mag_l, mag_r, best_ref_l, best_ref_r, ir_l_f, ir_r_f, thd_data, csd_data, ref_type)"""

content = content.replace(old_call, new_call)

with open('analysis_ui.py', 'w') as f:
    f.write(content)
