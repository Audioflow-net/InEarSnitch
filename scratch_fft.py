import numpy as np

sample_rate = 48000
duration = 0.1
t = np.linspace(0, duration, int(duration * sample_rate), False)
freq = 1000.0
probe_amp = 0.125
# Pure sine wave
tone = np.sin(2 * np.pi * freq * t) * probe_amp

# Add some bass noise
bass_noise = np.sin(2 * np.pi * 50 * t) * 0.5
mixed = tone + bass_noise

# 1. Time Domain max
td_max_tone = np.max(np.abs(tone))
td_max_mixed = np.max(np.abs(mixed))

# 2. Frequency Domain
N = len(mixed)
fft_res = np.fft.rfft(mixed)
freqs = np.fft.rfftfreq(N, 1.0 / sample_rate)
bin_idx = np.argmin(np.abs(freqs - freq))
fft_amp = np.abs(fft_res[bin_idx]) * 2.0 / N

print(f"Time-domain Tone Amplitude: {td_max_tone}")
print(f"Time-domain Mixed Amplitude: {td_max_mixed}")
print(f"FFT Extracted 1kHz Amplitude: {fft_amp}")

