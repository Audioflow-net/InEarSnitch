import re

with open("main.py", "r") as f:
    code = f.read()

# Insert update_analysis_view before on_measurement_finished
insert_point = r'(    def on_measurement_finished\(self, freqs, mag_l, mag_r, thd_data=None, csd_data=None\):)'

new_code = r"""    def update_analysis_view(self):
        if not hasattr(self, 'temp_freqs') or self.temp_freqs is None:
            return
            
        thd_data = getattr(self, 'temp_thd_data', None)
        csd_data = getattr(self, 'temp_csd_data', None)
        
        # Determine reference (history)
        ref_mag_l = None
        ref_mag_r = None
        if getattr(self, 'history_freqs', None) is not None:
            import numpy as np
            if getattr(self, 'history_mag_l', None) is not None:
                ref_mag_l = np.interp(self.temp_freqs, self.history_freqs, self.history_mag_l)
            if getattr(self, 'history_mag_r', None) is not None:
                ref_mag_r = np.interp(self.temp_freqs, self.history_freqs, self.history_mag_r)

        self.page_ana.update_analysis(
            self.temp_freqs, 
            self.temp_mag_l, 
            self.temp_mag_r,
            ref_mag_l=ref_mag_l,
            ref_mag_r=ref_mag_r,
            tgt_freqs=getattr(self, 'target_freqs', None),
            tgt_mags=getattr(self, 'target_mags', None),
            thd_data=thd_data,
            csd_data=csd_data
        )
        
\1"""

code = re.sub(insert_point, new_code, code)

with open("main.py", "w") as f:
    f.write(code)

print("update_analysis_view injected.")
