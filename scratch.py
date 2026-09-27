import numpy as np

fs = 48000
frames = 1024
t = np.arange(frames) / fs

# sine wave amp 1 at 2000 Hz
sig = np.sin(2 * np.pi * 2000 * t)

# Time domain RMS
rms = np.sqrt(np.mean(sig**2))
print("Time RMS:", rms)
print("Time dBFS (20*log10(RMS)): ", 20*np.log10(rms))
print("Time dBFS (20*log10(RMS/sqrt(0.5))): ", 20*np.log10(rms / np.sqrt(0.5)))

# Freq domain
window = np.hanning(frames)
X = np.fft.rfft(sig * window)
freqs = np.fft.rfftfreq(frames, 1/fs)
high_mask = freqs > 1000

high_power = np.sum((np.abs(X[high_mask]) / frames)**2) * 2.0
# Hanning window correction for power is 8/3 (approx 2.6666)
high_power *= (8.0/3.0)

print("Freq Power:", high_power)
print("Freq dBFS (10*log10(Power)): ", 10*np.log10(high_power))
print("Freq dBFS (10*log10(Power/0.5)): ", 10*np.log10(high_power / 0.5))
