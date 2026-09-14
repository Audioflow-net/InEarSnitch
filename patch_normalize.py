import re

with open("main.py", "r") as f:
    code = f.read()

old_finish = """    def on_measurement_finished(self, freqs, mag, phase, ir, channel):
        self.is_measuring = False   # UI Hardening: release lock
        self.meas_overlay.stop()
        self.btn_capture.setEnabled(True)
        if hasattr(self, 'btn_save_tgt'): self.btn_save_tgt.setEnabled(True)
        
        self.temp_freqs = freqs
        if channel == 'L':
            self.temp_mag_l = mag
            self.temp_phase_l = phase
            self.temp_ir_l = ir
        else:
            self.temp_mag_r = mag
            self.temp_phase_r = phase
            self.temp_ir_r = ir"""

new_finish = """    def on_measurement_finished(self, freqs, mag, phase, ir, channel):
        self.is_measuring = False   # UI Hardening: release lock
        self.meas_overlay.stop()
        self.btn_capture.setEnabled(True)
        if hasattr(self, 'btn_save_tgt'): self.btn_save_tgt.setEnabled(True)
        
        import numpy as np
        # 1. Check raw volume
        idx_1k = (np.abs(freqs - 1000)).argmin()
        raw_val_1k = mag[idx_1k]
        low_vol_warning = False
        if raw_val_1k < 75.0:
            low_vol_warning = True
            
        # 2. Smart Post-Normalization
        if np.isfinite(raw_val_1k):
            mag = mag + (80.0 - raw_val_1k)
        
        self.temp_freqs = freqs
        if channel == 'L':
            self.temp_mag_l = mag
            self.temp_phase_l = phase
            self.temp_ir_l = ir
        else:
            self.temp_mag_r = mag
            self.temp_phase_r = phase
            self.temp_ir_r = ir
            
        self.low_vol_warning = low_vol_warning"""

code = code.replace(old_finish, new_finish)

old_sub_lbl = """        if self.temp_mag_l is not None and self.temp_mag_r is not None:
            self.sub_lbl.setText("Measurement complete! Ready to save.")
            self.sub_lbl.setStyleSheet("color: #00FF00; font-size: 13px; font-weight: bold;")
        else:
            other = "Right" if channel == "L" else "Left"
            self.sub_lbl.setText(f"{channel} channel captured. Measure the {other} side, or Save to DB.")
            self.sub_lbl.setStyleSheet("color: #00FF00; font-size: 13px;")"""

new_sub_lbl = """        if self.temp_mag_l is not None and self.temp_mag_r is not None:
            txt = "Measurement complete! Ready to save."
        else:
            other = "Right" if channel == "L" else "Left"
            txt = f"{channel} channel captured. Measure the {other} side, or Save to DB."
            
        if getattr(self, 'low_vol_warning', False):
            txt += " (WARN: Raw volume was very low. Turn up Interface Gain!)"
            self.sub_lbl.setStyleSheet("color: #FFB300; font-size: 13px; font-weight: bold;")
        else:
            self.sub_lbl.setStyleSheet("color: #00FF00; font-size: 13px; font-weight: bold;")
        self.sub_lbl.setText(txt)"""

code = code.replace(old_sub_lbl, new_sub_lbl)

with open("main.py", "w") as f:
    f.write(code)

print("main.py patched with smart normalization.")
