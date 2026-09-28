import numpy as np

def calculate_measurement_snr(ir_data, sample_rate):
    if ir_data is None: return None
    peak_idx = np.argmax(np.abs(ir_data))
    
    # Signal window: Peak + 10ms
    signal_len = int(0.010 * sample_rate)
    signal_window = ir_data[peak_idx : peak_idx + signal_len]
    
    # Noise window: Peak + 50ms to 150ms
    noise_start = peak_idx + int(0.050 * sample_rate)
    noise_end = peak_idx + int(0.150 * sample_rate)
    
    if noise_end > len(ir_data):
        return 100.0 # Fallback if IR is too short
        
    noise_window = ir_data[noise_start : noise_end]
    
    rms_signal = np.sqrt(np.mean(signal_window**2))
    rms_noise = np.sqrt(np.mean(noise_window**2))
    rms_noise = max(rms_noise, 1e-12)
    
    snr_db = 20 * np.log10(rms_signal / rms_noise)
    return snr_db

# Let's generate a fake IR to see what happens
sr = 48000
ir = np.zeros(sr)
ir[100] = 1.0 # peak
print(calculate_measurement_snr(ir, sr))
