import sys

with open('main.py', 'r') as f:
    content = f.read()

old_logic = """        # --- Live IEC 711 Positioning Diagnostics ---
        try:
            # 1. Depth (8kHz peak)
            mask_treble = (freqs >= 6000) & (freqs <= 10000)
            if np.any(mask_treble):
                treble_freqs = freqs[mask_treble]
                treble_mags = mag_db[mask_treble]
                peak_freq = treble_freqs[np.argmax(treble_mags)]
                
                if peak_freq < 7800:
                    depth_html = "<span style='color: #ef4444; font-weight: bold;'>Tiefer reindrücken! (Peak: {:.1f}kHz -> Ziel: 8kHz)</span>".format(peak_freq/1000)
                elif peak_freq > 8200:
                    depth_html = "<span style='color: #ef4444; font-weight: bold;'>Etwas rausziehen! (Peak: {:.1f}kHz -> Ziel: 8kHz)</span>".format(peak_freq/1000)
                else:
                    depth_html = "<span style='color: #10b981; font-weight: bold;'>Tiefe: PERFEKT (Resonanz bei 8kHz)</span>"
            else:
                depth_html = ""

            # 2. Seal (40Hz vs 500Hz)
            mask_40 = (freqs >= 35) & (freqs <= 45)
            mask_500 = (freqs >= 450) & (freqs <= 550)
            if np.any(mask_40) and np.any(mask_500):
                val_40 = np.mean(mag_db[mask_40])
                val_500 = np.mean(mag_db[mask_500])
                if val_40 < val_500 - 15:
                    seal_html = "<span style='color: #ef4444; font-weight: bold;'>🔴 SEAL LEAK!</span>"
                else:
                    seal_html = "<span style='color: #10b981; font-weight: bold;'>🟢 SEAL OK</span>"
            else:
                seal_html = ""
                
            self.sub_lbl.setText(f"Live RTA | {seal_html} | {depth_html}")"""

new_logic = """        # --- Live IEC 711 Positioning Diagnostics ---
        try:
            # Detect if IEM is pulled out (massive drop in volume from recent peak)
            if not hasattr(self, '_max_rta_mean'):
                self._max_rta_mean = current_mean
            
            # Slowly decay the peak tracking, but jump up instantly
            if current_mean > self._max_rta_mean:
                self._max_rta_mean = current_mean
            else:
                self._max_rta_mean = 0.99 * self._max_rta_mean + 0.01 * current_mean

            if current_mean < self._max_rta_mean - 15.0:
                # Signal dropped by > 15dB compared to recent max. It was pulled out.
                seal_html = "<span style='color: #a8a29e; font-weight: bold;'>IEM nicht erkannt (Stille)</span>"
                depth_html = ""
            else:
                # 1. Depth (8kHz peak)
                mask_treble = (freqs >= 6000) & (freqs <= 10000)
                if np.any(mask_treble):
                    treble_freqs = freqs[mask_treble]
                    treble_mags = mag_db[mask_treble]
                    peak_freq = treble_freqs[np.argmax(treble_mags)]
                    
                    if peak_freq < 7800:
                        depth_html = "<span style='color: #ef4444; font-weight: bold;'>Tiefer reindrücken! (Peak: {:.1f}kHz -> Ziel: 8kHz)</span>".format(peak_freq/1000)
                    elif peak_freq > 8200:
                        depth_html = "<span style='color: #ef4444; font-weight: bold;'>Etwas rausziehen! (Peak: {:.1f}kHz -> Ziel: 8kHz)</span>".format(peak_freq/1000)
                    else:
                        depth_html = "<span style='color: #10b981; font-weight: bold;'>Tiefe: PERFEKT (Resonanz bei 8kHz)</span>"
                else:
                    depth_html = ""
    
                # 2. Seal (40Hz vs 500Hz)
                mask_40 = (freqs >= 35) & (freqs <= 45)
                mask_500 = (freqs >= 450) & (freqs <= 550)
                if np.any(mask_40) and np.any(mask_500):
                    val_40 = np.mean(mag_db[mask_40])
                    val_500 = np.mean(mag_db[mask_500])
                    # Check for bass roll-off OR overall low signal variance (just noise floor)
                    if val_40 < val_500 - 12:
                        seal_html = "<span style='color: #ef4444; font-weight: bold;'>🔴 SEAL LEAK!</span>"
                    else:
                        seal_html = "<span style='color: #10b981; font-weight: bold;'>🟢 SEAL OK</span>"
                else:
                    seal_html = ""
                
            self.sub_lbl.setText(f"Live RTA | {seal_html} | {depth_html}")"""

content = content.replace(old_logic, new_logic)

with open('main.py', 'w') as f:
    f.write(content)
