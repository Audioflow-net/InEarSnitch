import numpy as np
from scipy import signal

class DSPEngine:
    def __init__(self):
        self.filters = []  # List of dicts: {'type': 'peq', 'freq': 1000, 'gain': 0, 'q': 1.0, 'enabled': True}
        self.master_enabled = False

    def set_filters(self, filter_list):
        self.filters = filter_list

    def set_master(self, enabled):
        self.master_enabled = enabled

    def _get_biquad(self, ftype, freq, gain, q, fs):
        q = max(float(q), 0.001)
        fs = max(int(fs), 1)
        A = 10 ** (gain / 40)
        w0 = 2 * np.pi * freq / fs
        alpha = np.sin(w0) / (2 * q)

        if ftype == 'peq':
            b0 = 1 + alpha * A
            b1 = -2 * np.cos(w0)
            b2 = 1 - alpha * A
            a0 = 1 + alpha / A
            a1 = -2 * np.cos(w0)
            a2 = 1 - alpha / A
        elif ftype == 'lowshelf':
            b0 = A * ((A + 1) - (A - 1) * np.cos(w0) + 2 * np.sqrt(A) * alpha)
            b1 = 2 * A * ((A - 1) - (A + 1) * np.cos(w0))
            b2 = A * ((A + 1) - (A - 1) * np.cos(w0) - 2 * np.sqrt(A) * alpha)
            a0 = (A + 1) + (A - 1) * np.cos(w0) + 2 * np.sqrt(A) * alpha
            a1 = -2 * ((A - 1) + (A + 1) * np.cos(w0))
            a2 = (A + 1) + (A - 1) * np.cos(w0) - 2 * np.sqrt(A) * alpha
        elif ftype == 'highshelf':
            b0 = A * ((A + 1) + (A - 1) * np.cos(w0) + 2 * np.sqrt(A) * alpha)
            b1 = -2 * A * ((A - 1) + (A + 1) * np.cos(w0))
            b2 = A * ((A + 1) + (A - 1) * np.cos(w0) - 2 * np.sqrt(A) * alpha)
            a0 = (A + 1) - (A - 1) * np.cos(w0) + 2 * np.sqrt(A) * alpha
            a1 = 2 * ((A - 1) - (A + 1) * np.cos(w0))
            a2 = (A + 1) - (A - 1) * np.cos(w0) - 2 * np.sqrt(A) * alpha
        else:
            # Flat
            return np.array([1, 0, 0]), np.array([1, 0, 0])

        b = np.array([b0, b1, b2]) / a0
        a = np.array([a0, a1, a2]) / a0
        return b, a

    def process(self, audio_data, fs):
        if not self.master_enabled or not self.filters:
            return audio_data

        y = audio_data.copy()
        for f in self.filters:
            if not f.get('enabled', True) or f['gain'] == 0.0:
                continue
                
            # Caching biquad coefficients to save massive CPU load in the audio thread
            if (f.get('_cached_fs') != fs or 
                f.get('_cached_gain') != f['gain'] or 
                f.get('_cached_freq') != f['freq'] or 
                f.get('_cached_q') != f['q'] or 
                f.get('_cached_type') != f.get('type', 'peq')):
                
                b, a = self._get_biquad(f.get('type', 'peq'), f['freq'], f['gain'], f['q'], fs)
                f['_cached_b'] = b
                f['_cached_a'] = a
                f['_cached_fs'] = fs
                f['_cached_gain'] = f['gain']
                f['_cached_freq'] = f['freq']
                f['_cached_q'] = f['q']
                f['_cached_type'] = f.get('type', 'peq')
                f['_cached_zi'] = None  # Invalidate state on parameter change
                
            if f.get('_cached_zi') is None:
                f['_cached_zi'] = signal.lfilter_zi(f['_cached_b'], f['_cached_a']) * y[0]
                
            y, zf = signal.lfilter(f['_cached_b'], f['_cached_a'], y, zi=f['_cached_zi'])
            f['_cached_zi'] = zf

        # Normalize to prevent digital clipping if EQ pushes > 0dBFS
        # But for measurements we want to keep absolute SPL scale if possible, 
        # so we only clip or normalize if we exceed 1.0
        # PRO-AUDIO UPDATE: Never auto-normalize! It destroys absolute SPL references.
        # If the user boosts EQ into clipping, we hard-clip to prevent audio driver crashes, 
        # but we preserve the exact gain ratio for the rest of the frequency spectrum.
        y = np.clip(y, -0.99, 0.99)

        return y

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

# Global instance for the app
dsp_engine = DSPEngine()
