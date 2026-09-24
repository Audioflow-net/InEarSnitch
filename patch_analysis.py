import numpy as np

def auto_seal_detection(freqs, mag_l, mag_r):
    if len(freqs) == 0:
        return False, "Seal OK"
    
    idx_sub = np.where((freqs >= 20) & (freqs <= 40))[0]
    idx_mid = np.where((freqs >= 50) & (freqs <= 500))[0]
    
    warn_l = False
    warn_r = False
    
    if len(idx_sub) > 0 and len(idx_mid) > 0:
        avg_sub_l = np.mean(mag_l[idx_sub])
        avg_mid_l = np.mean(mag_l[idx_mid])
        if avg_mid_l - avg_sub_l > 10.0:
            warn_l = True
            
        avg_sub_r = np.mean(mag_r[idx_sub])
        avg_mid_r = np.mean(mag_r[idx_mid])
        if avg_mid_r - avg_sub_r > 10.0:
            warn_r = True
            
    if warn_l and warn_r:
        return True, "Warning: Left & Right seal breach suspected."
    elif warn_l:
        return True, "Warning: Left seal breach suspected."
    elif warn_r:
        return True, "Warning: Right seal breach suspected."
        
    return False, "Seal OK"

def lr_imbalance_check(freqs, mag_l, mag_r):
    if len(freqs) == 0:
        return False, "L/R Balance OK"
        
    idx = np.where((freqs >= 100) & (freqs <= 5000))[0]
    if len(idx) > 0:
        max_diff = np.max(np.abs(mag_l[idx] - mag_r[idx]))
        if max_diff > 2.5:
            return True, f"Imbalance Detected. Max diff: {max_diff:.1f} dB"
            
    return False, "L/R Balance OK"
