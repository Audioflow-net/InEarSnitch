import re

with open('audio_engine.py', 'r') as f:
    content = f.read()

old_code = r"""        if abs\(latency_ms\) < 0\.1:
            raise RuntimeError\("Electrical Loopback Detected! The signal has zero acoustic delay. Turn off 'Direct Monitoring' on your audio interface and ensure you selected the correct measurement microphone."\)"""

new_code = """        if abs(latency_ms) < 0.1:
            raise RuntimeError("Electrical Loopback Detected! The signal has zero acoustic delay. Turn off 'Direct Monitoring' on your audio interface and ensure you selected the correct measurement microphone.")
            
        # Advanced Electrical Loopback Check (Flatness)
        # IEMs are never perfectly flat. If the IR is perfectly flat, it's a hardware loopback
        # that slipped past the latency check (e.g., Direct Monitor with USB buffer delay).
        temp_fft = np.fft.rfft(ir)
        temp_mag = 20 * np.log10(np.abs(temp_fft) + 1e-12)
        temp_freqs = np.fft.rfftfreq(len(ir), 1 / self.sample_rate)
        valid = (temp_freqs > 100) & (temp_freqs < 10000)
        if np.any(valid):
            mag_range = np.max(temp_mag[valid]) - np.min(temp_mag[valid])
            if mag_range < 3.0:
                raise RuntimeError(f"Electrical Loopback Detected! The frequency response is completely flat ({mag_range:.1f} dB variance). You are measuring the soundcard itself, not the microphone.\\n\\nTurn off 'Direct Monitoring' / 'Loopback' on your audio interface, and check your input selection.")"""

if re.search(old_code, content):
    content = re.sub(old_code, new_code, content)
    with open('audio_engine.py', 'w') as f:
        f.write(content)
    print("PATCH APPLIED SUCCESSFULLY")
else:
    print("COULD NOT MATCH OLD LOGIC")
