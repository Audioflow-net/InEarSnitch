import re

with open('main.py', 'r') as f:
    content = f.read()

new_code = r"""    def update_analysis_view(self):
        freqs = getattr(self, 'temp_freqs', None)
        mag_l = getattr(self, 'temp_mag_l', None)
        mag_r = getattr(self, 'temp_mag_r', None)
        thd_data = getattr(self, 'temp_thd_data', None)
        csd_data = getattr(self, 'temp_csd_data', None)
        ir_l = getattr(self, 'temp_ir_l', None)
        ir_r = getattr(self, 'temp_ir_r', None)
        
        ref_mag_l = None
        ref_mag_r = None

        history_freqs = getattr(self, 'history_freqs', None)
        history_mag_l = getattr(self, 'history_mag_l', None)
        history_mag_r = getattr(self, 'history_mag_r', None)

        if freqs is None and history_freqs is not None:
            # Wenn keine Live-Messung existiert, nutze die History als primäre Kurve (für volle Analyse)
            freqs = history_freqs
            mag_l = history_mag_l
            mag_r = history_mag_r
        elif freqs is not None and history_freqs is not None:
            # Wenn eine Live-Messung existiert, nutze History als gestrichelte Referenz
            import numpy as np
            if history_mag_l is not None:
                ref_mag_l = np.interp(freqs, history_freqs, history_mag_l)
            if history_mag_r is not None:
                ref_mag_r = np.interp(freqs, history_freqs, history_mag_r)

        if freqs is None:
            return

        self.page_ana.update_analysis(
            freqs, 
            mag_l, 
            mag_r,
            ref_mag_l=ref_mag_l,
            ref_mag_r=ref_mag_r,
            tgt_freqs=getattr(self, 'target_freqs', None),
            tgt_mags=getattr(self, 'target_mags', None),
            thd_data=thd_data,
            csd_data=csd_data,
            ir_l=ir_l,
            ir_r=ir_r
        )"""

old_code = re.compile(r"    def update_analysis_view\(self\):.*?        self\.page_ana\.update_analysis\([^)]+\)", re.DOTALL)

content = old_code.sub(new_code, content)

with open('main.py', 'w') as f:
    f.write(content)
print("Patched main.py")
