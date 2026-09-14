import sys

with open('audio_engine.py', 'r') as f:
    content = f.read()

old_fft = """        freqs = rfftfreq(N, 1 / self.sample_rate)
        fft_res = rfft(ir_windowed)"""

new_fft = """        freqs = rfftfreq(N, 1 / self.sample_rate)
        
        # WISSENSCHAFTLICHES UPDATE: Time Alignment (Zero-Phase Reference)
        # We circularly shift the IR so the peak is exactly at t=0.
        # This completely eliminates random USB latency from the phase response
        # and allows mathematically perfect L/R phase comparisons.
        ir_shifted = np.roll(ir_windowed, -peak_idx)
        fft_res = rfft(ir_shifted)"""

content = content.replace(old_fft, new_fft)

with open('audio_engine.py', 'w') as f:
    f.write(content)
