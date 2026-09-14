import re

with open("analysis_ui.py", "r") as f:
    code = f.read()

pattern = r"        if not hasattr\(self, '_last_data'\): return\n        freqs, orig_mag_l, orig_mag_r, ref_mag_l, ref_mag_r, tgt_freqs, tgt_mags, thd_data, csd_data = self\._last_data"

replacement = r'''        if not hasattr(self, '_last_data'): return
        try:
            freqs, orig_mag_l, orig_mag_r, ref_mag_l, ref_mag_r, tgt_freqs, tgt_mags, thd_data, csd_data, ir_l, ir_r = self._last_data
        except ValueError:
            freqs, orig_mag_l, orig_mag_r, ref_mag_l, ref_mag_r, tgt_freqs, tgt_mags, thd_data, csd_data = self._last_data
            ir_l = None
            ir_r = None'''

code = re.sub(pattern, replacement, code)

with open("analysis_ui.py", "w") as f:
    f.write(code)

print("Analysis unpack patched.")
