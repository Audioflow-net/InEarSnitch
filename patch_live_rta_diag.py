import re

with open('main.py', 'r') as f:
    content = f.read()

# We want to replace the current update_live_rta entirely with our new one
old_func = r"""    def update_live_rta\(self, freqs, mag_db\):
        import numpy as np
        mask = \(freqs >= 20\) & \(freqs <= 20000\)
        
        mask_1k = \(freqs >= 500\) & \(freqs <= 2000\)
        current_mean = np\.mean\(mag_db\[mask_1k\]\)
        target_db = 85\.0
        calculated_shift = target_db - current_mean
        
        if not hasattr\(self, '_rta_shift'\):
            self\._rta_shift = calculated_shift
        else:
            self\._rta_shift = 0\.8 \* self\._rta_shift \+ 0\.2 \* calculated_shift
            
        self\.live_rta_line\.setData\(freqs\[mask\], mag_db\[mask\] \+ self\._rta_shift\)"""

new_func = """    def update_live_rta(self, freqs, mag_db):
        import numpy as np
        mask = (freqs >= 20) & (freqs <= 20000)
        
        mask_1k = (freqs >= 500) & (freqs <= 2000)
        current_mean = np.mean(mag_db[mask_1k])
        target_db = 85.0
        calculated_shift = target_db - current_mean
        
        if not hasattr(self, '_rta_shift'):
            self._rta_shift = calculated_shift
        else:
            self._rta_shift = 0.8 * self._rta_shift + 0.2 * calculated_shift
            
        self.live_rta_line.setData(freqs[mask], mag_db[mask] + self._rta_shift)
        
        # --- Live IEC 711 Positioning Diagnostics ---
        try:
            # 1. Depth (8kHz peak)
            mask_treble = (freqs >= 6000) & (freqs <= 10000)
            if np.any(mask_treble):
                treble_freqs = freqs[mask_treble]
                treble_mags = mag_db[mask_treble]
                peak_freq = treble_freqs[np.argmax(treble_mags)]
                
                if peak_freq < 7800:
                    depth_html = "<span style='color: #ef4444; font-weight: bold;'>Tiefer (Peak: {:.1f}kHz)</span>".format(peak_freq/1000)
                elif peak_freq > 8200:
                    depth_html = "<span style='color: #ef4444; font-weight: bold;'>Rausziehen (Peak: {:.1f}kHz)</span>".format(peak_freq/1000)
                else:
                    depth_html = "<span style='color: #10b981; font-weight: bold;'>Tiefe: PERFEKT (8kHz)</span>"
            else:
                depth_html = ""

            # 2. Seal (40Hz vs 500Hz)
            mask_40 = (freqs >= 35) & (freqs <= 45)
            mask_500 = (freqs >= 450) & (freqs <= 550)
            if np.any(mask_40) and np.any(mask_500):
                val_40 = np.mean(mag_db[mask_40])
                val_500 = np.mean(mag_db[mask_500])
                if val_40 < val_500 - 15:
                    seal_html = "<span style='color: #ef4444; font-weight: bold;'>🔴 Seal Leak! (Bass fehlt)</span>"
                else:
                    seal_html = "<span style='color: #10b981; font-weight: bold;'>🟢 Seal OK</span>"
            else:
                seal_html = ""
                
            self.sub_lbl.setText(f"Live RTA | {seal_html} | {depth_html}")
        except Exception as e:
            pass"""

if re.search(old_func, content):
    content = re.sub(old_func, new_func, content)
    with open('main.py', 'w') as f:
        f.write(content)
    print("Patched successfully.")
else:
    print("Could not find the function to patch. Checking file...")
    print(content[content.find('def update_live_rta'):content.find('def update_live_rta')+500])
