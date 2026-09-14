import re

with open("audio_engine.py", "r") as f:
    code = f.read()

old_code = """        # 6. AUTO-GAIN NORMALIZATION (AI Fix)
        # Average the magnitude between 500Hz and 1000Hz (the most stable region for IEMs)
        # and shift the entire curve so this average sits exactly at 90.0 dB SPL.
        # This completely eliminates the interface physical gain knob variable!
        idx_band = np.where((freqs >= 500) & (freqs <= 1000))[0]
        if len(idx_band) > 0:
            avg_mag = np.mean(mag[idx_band])
            gain_offset = 90.0 - avg_mag
            mag += gain_offset"""

new_code = ""

code = code.replace(old_code, new_code)

with open("audio_engine.py", "w") as f:
    f.write(code)

print("Auto-gain patched.")
