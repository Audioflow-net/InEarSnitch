import re

with open("audio_engine.py", "r") as f:
    code = f.read()

# 1. Update generate_sweep defaults and fade
old_sweep = """    def generate_sweep(self, duration=2.0, f_start=20.0, f_end=20000.0):
        \"\"\"Generates a logarithmic sine sweep with fade-in and fade-out.\"\"\"
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        sweep = chirp(t, f0=f_start, f1=f_end, t1=duration, method='logarithmic')
        
        # Fade in / Fade out to prevent clicks (50ms)
        fade_len = int(0.05 * self.sample_rate)"""

new_sweep = """    def generate_sweep(self, duration=2.0, f_start=5.0, f_end=24000.0):
        \"\"\"Generates a logarithmic sine sweep with fade-in and fade-out.\"\"\"
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        sweep = chirp(t, f0=f_start, f1=f_end, t1=duration, method='logarithmic')
        
        # Fade in / Fade out to prevent clicks (10ms to preserve full 20Hz-20kHz bandwidth)
        fade_len = int(0.01 * self.sample_rate)"""

code = code.replace(old_sweep, new_sweep)

# 2. Update get_inverse_filter defaults
old_inv = """    def get_inverse_filter(self, sweep, duration, f_start=20.0, f_end=20000.0):"""
new_inv = """    def get_inverse_filter(self, sweep, duration, f_start=5.0, f_end=24000.0):"""
code = code.replace(old_inv, new_inv)

with open("audio_engine.py", "w") as f:
    f.write(code)

print("Sweep generator patched.")
