import re

# --- 1. analysis.py ---
with open("analysis.py", "r") as f:
    code = f.read()

# Update signature
code = code.replace(
    'def run_full_diagnostics(freqs, mag_l, mag_r, ref_mag_l=None, ref_mag_r=None):',
    'def run_full_diagnostics(freqs, mag_l, mag_r, ref_mag_l=None, ref_mag_r=None, ir_l=None, ir_r=None):'
)

# Update calls to absolute_checks
code = code.replace(
    'report.extend(Analyzer.absolute_checks(freqs, mag_l, "Left"))',
    'report.extend(Analyzer.absolute_checks(freqs, mag_l, ir_l, "Left"))'
)
code = code.replace(
    'report.extend(Analyzer.absolute_checks(freqs, mag_r, "Right"))',
    'report.extend(Analyzer.absolute_checks(freqs, mag_r, ir_r, "Right"))'
)

with open("analysis.py", "w") as f:
    f.write(code)

# --- 2. analysis_ui.py ---
with open("analysis_ui.py", "r") as f:
    code = f.read()

code = code.replace(
    'def update_analysis(self, freqs, mag_l, mag_r, ref_mag_l=None, ref_mag_r=None, tgt_freqs=None, tgt_mags=None, thd_data=None, csd_data=None):',
    'def update_analysis(self, freqs, mag_l, mag_r, ref_mag_l=None, ref_mag_r=None, tgt_freqs=None, tgt_mags=None, thd_data=None, csd_data=None, ir_l=None, ir_r=None):'
)

code = code.replace(
    'self._last_data = (freqs, mag_l, mag_r, ref_mag_l, ref_mag_r, tgt_freqs, tgt_mags, thd_data, csd_data)',
    'self._last_data = (freqs, mag_l, mag_r, ref_mag_l, ref_mag_r, tgt_freqs, tgt_mags, thd_data, csd_data, ir_l, ir_r)'
)

pattern_unpack = r'''        if not hasattr\(self, '_last_data'\) or self\._last_data is None:
            return
            
        freqs, mag_l, mag_r, ref_mag_l, ref_mag_r, tgt_freqs, tgt_mags, thd_data, csd_data = self\._last_data'''
replacement_unpack = r'''        if not hasattr(self, '_last_data') or self._last_data is None:
            return
            
        try:
            freqs, mag_l, mag_r, ref_mag_l, ref_mag_r, tgt_freqs, tgt_mags, thd_data, csd_data, ir_l, ir_r = self._last_data
        except ValueError:
            # Fallback for old tuples
            freqs, mag_l, mag_r, ref_mag_l, ref_mag_r, tgt_freqs, tgt_mags, thd_data, csd_data = self._last_data
            ir_l = None
            ir_r = None'''
code = re.sub(pattern_unpack, replacement_unpack, code)

code = code.replace(
    'report = Analyzer.run_full_diagnostics(freqs, mag_l, mag_r, best_ref_l, best_ref_r)',
    'report = Analyzer.run_full_diagnostics(freqs, mag_l, mag_r, best_ref_l, best_ref_r, ir_l, ir_r)'
)

with open("analysis_ui.py", "w") as f:
    f.write(code)


# --- 3. main.py ---
with open("main.py", "r") as f:
    code = f.read()

code = code.replace(
    'csd_data=csd_data\n        )',
    "csd_data=csd_data,\n            ir_l=getattr(self, 'temp_ir_l', None),\n            ir_r=getattr(self, 'temp_ir_r', None)\n        )"
)

with open("main.py", "w") as f:
    f.write(code)

print("Crash patched.")
