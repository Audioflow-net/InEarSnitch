import numpy as np
import time
from scipy import interpolate

blocksize = 8192
mag = np.random.rand(blocksize//2 + 1)
freqs = np.fft.rfftfreq(blocksize, 1/48000)

# Current method
start = time.perf_counter()
for _ in range(100):
    kernel_size = 15
    kernel = np.ones(kernel_size) / kernel_size
    mag_smooth = np.convolve(mag, kernel, mode='same')
end = time.perf_counter()
print(f"Current convolve 100x: {(end-start)*1000:.2f} ms")

# Fractional octave interpolation method (1/12 octave)
start = time.perf_counter()
for _ in range(100):
    # Log-spaced frequencies
    f_log = np.logspace(np.log10(20), np.log10(20000), 500)
    interp_func = interpolate.interp1d(freqs, mag, bounds_error=False, fill_value=0.0)
    mag_log = interp_func(f_log)
end = time.perf_counter()
print(f"Interp1d 100x: {(end-start)*1000:.2f} ms")

# Alternative: Precomputed logarithmic binning matrix
start = time.perf_counter()
# Create mapping matrix once
num_bins = 100
f_log = np.logspace(np.log10(20), np.log10(20000), num_bins)
bin_matrix = np.zeros((num_bins, len(freqs)))
for i in range(num_bins-1):
    idx = (freqs >= f_log[i]) & (freqs < f_log[i+1])
    if np.sum(idx) > 0:
        bin_matrix[i, idx] = 1.0 / np.sum(idx)
end_precompute = time.perf_counter()

start_mat = time.perf_counter()
for _ in range(100):
    mag_binned = bin_matrix @ mag
end_mat = time.perf_counter()
print(f"Matrix multiply 100x: {(end_mat-start_mat)*1000:.2f} ms (precompute took {(end_precompute-start)*1000:.2f} ms)")
