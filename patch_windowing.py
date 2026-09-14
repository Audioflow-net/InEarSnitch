import sys

with open('audio_engine.py', 'r') as f:
    content = f.read()

old_fft = """        # 4. Compute Frequency Response via FFT
        N = len(ir)
        freqs = rfftfreq(N, 1 / self.sample_rate)
        fft_res = rfft(ir)"""

new_fft = """        # 4. Compute Frequency Response via FFT
        # WISSENSCHAFTLICHES UPDATE: Time-Domain Windowing!
        # We must window the IR to exclude background noise (from the 1s record time)
        # and more importantly: to exclude Farina's harmonic distortion impulses
        # which sit at -95ms and earlier. This dramatically cleans up the Phase and Magnitude!
        N = len(ir)
        peak_idx = np.argmax(np.abs(ir))
        
        # Window: -10ms to +100ms (100ms resolves down to 10Hz, completely capturing IEM bass)
        win_pre = int(0.01 * self.sample_rate)
        win_post = int(0.10 * self.sample_rate)
        w_start = max(0, peak_idx - win_pre)
        w_end = min(N, peak_idx + win_post)
        
        # Apply a Tukey-like window (flat in middle, Hann tapered at edges)
        from scipy.signal.windows import hann
        import numpy as np
        taper_len = int(0.005 * self.sample_rate) # 5ms taper
        window = np.ones(w_end - w_start)
        if len(window) > 2 * taper_len:
            window[:taper_len] = hann(taper_len * 2)[:taper_len]
            window[-taper_len:] = hann(taper_len * 2)[taper_len:]
            
        ir_windowed = np.zeros_like(ir)
        ir_windowed[w_start:w_end] = ir[w_start:w_end] * window
        
        freqs = rfftfreq(N, 1 / self.sample_rate)
        fft_res = rfft(ir_windowed)"""

content = content.replace(old_fft, new_fft)

with open('audio_engine.py', 'w') as f:
    f.write(content)
