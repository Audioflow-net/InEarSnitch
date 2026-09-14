import sys

with open('main.py', 'r') as f:
    content = f.read()

old_csd = """            # CSD (Just use Left or Right, prefer Left)
            csd_freqs, csd_slices = None, None
            if getattr(self, 'temp_ir_l', None) is not None:
                csd_freqs, _, csd_mag = self.audio_engine.calculate_csd(self.temp_ir_l)
                csd_slices = csd_mag
            elif getattr(self, 'temp_ir_r', None) is not None:
                csd_freqs, _, csd_mag = self.audio_engine.calculate_csd(self.temp_ir_r)
                csd_slices = csd_mag
                
            if csd_freqs is not None and csd_slices is not None:
                csd_data = (csd_freqs, csd_slices)"""

new_csd = """            # CSD
            csd_data = {}
            if getattr(self, 'temp_ir_l', None) is not None:
                cf, ct, cm = self.audio_engine.calculate_csd(self.temp_ir_l)
                csd_data['L'] = (cf, ct, cm)
            if getattr(self, 'temp_ir_r', None) is not None:
                cf, ct, cm = self.audio_engine.calculate_csd(self.temp_ir_r)
                csd_data['R'] = (cf, ct, cm)
            if not csd_data:
                csd_data = None"""
content = content.replace(old_csd, new_csd)

with open('main.py', 'w') as f:
    f.write(content)
