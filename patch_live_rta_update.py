import re

with open('main.py', 'r') as f:
    content = f.read()

new_code = """    def update_live_rta(self, freqs, mag_db):
        import numpy as np
        mask = (freqs >= 20) & (freqs <= 20000)
        
        # Smooth shift calculation over a broader range (e.g. 500Hz to 2000Hz)
        mask_1k = (freqs >= 500) & (freqs <= 2000)
        current_mean = np.mean(mag_db[mask_1k])
        
        # Exponential moving average for the shift so it doesn't jump wildly
        target_db = 85.0
        calculated_shift = target_db - current_mean
        
        if not hasattr(self, '_rta_shift'):
            self._rta_shift = calculated_shift
        else:
            self._rta_shift = 0.8 * self._rta_shift + 0.2 * calculated_shift
            
        self.live_rta_line.setData(freqs[mask], mag_db[mask] + self._rta_shift)"""

content = re.sub(r"    def update_live_rta\(self, freqs, mag_db\):.*?self\.live_rta_line\.setData\(freqs\[mask\], mag_db\[mask\] \+ shift\)", new_code, content, flags=re.DOTALL)

with open('main.py', 'w') as f:
    f.write(content)
