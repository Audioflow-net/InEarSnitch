import re

with open('eq_math.py', 'r') as f:
    content = f.read()

# Add get_magnitude_response
new_method = """        return y

    def get_magnitude_response(self, freqs, fs):
        import numpy as np
        from scipy import signal
        
        total_mag_db = np.zeros_like(freqs, dtype=float)
        
        if not self.filters:
            return total_mag_db
            
        w = 2 * np.pi * freqs / fs
        
        for f in self.filters:
            if not f.get('enabled', True):
                continue
            if f['gain'] == 0.0:
                continue
                
            b, a = self._get_biquad(f.get('type', 'peq'), f['freq'], f['gain'], f['q'], fs)
            
            # Fast frequency response calculation at specific frequencies
            _, h = signal.freqz(b, a, worN=w)
            total_mag_db += 20 * np.log10(np.maximum(np.abs(h), 1e-12))
            
        return total_mag_db

# Global instance for the app"""

content = content.replace("        return y\n        \n# Global instance for the app", new_method)

with open('eq_math.py', 'w') as f:
    f.write(content)
