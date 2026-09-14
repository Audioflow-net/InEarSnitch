import re

with open("analysis_ui.py", "r") as f:
    code = f.read()

code = code.replace(
    '        mag_r = orig_mag_r if not show_l else None',
    '        mag_r = orig_mag_r if not show_l else None\n        ir_l_f = ir_l if show_l else None\n        ir_r_f = ir_r if not show_l else None'
)

code = code.replace(
    'report = Analyzer.run_full_diagnostics(freqs, mag_l, mag_r, best_ref_l, best_ref_r, ir_l, ir_r)',
    'report = Analyzer.run_full_diagnostics(freqs, mag_l, mag_r, best_ref_l, best_ref_r, ir_l_f, ir_r_f)'
)

code = code.replace(
    'if tgt_freqs is not None and tgt_mags is not None:',
    'if tgt_freqs is not None and tgt_mags is not None and (mag_l is not None or mag_r is not None):'
)

with open("analysis_ui.py", "w") as f:
    f.write(code)

print("Patched.")
