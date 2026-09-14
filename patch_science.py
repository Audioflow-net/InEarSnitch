import sys

with open('analysis.py', 'r') as f:
    content = f.read()

# 1. Update signature to include ref_type
old_sig = "def run_full_diagnostics(freqs, mag_l, mag_r, ref_mag_l=None, ref_mag_r=None, ir_l=None, ir_r=None, thd_data=None, csd_data=None):"
new_sig = "def run_full_diagnostics(freqs, mag_l, mag_r, ref_mag_l=None, ref_mag_r=None, ir_l=None, ir_r=None, thd_data=None, csd_data=None, ref_type='target'):"
content = content.replace(old_sig, new_sig)

# 2. Update check_band to handle ref_type
old_check_band = """        def check_band(mag, ref, f_min, f_max, name):
            import numpy as np
            idx = np.where((freqs >= f_min) & (freqs <= f_max))[0]
            if len(idx) == 0: return 'OK', 'Not enough data in this band.'
            
            # Use raw difference to check if it's dropping (negative) or spiking (positive)
            raw_diff = mag[idx] - ref[idx]
            avg_raw = np.mean(raw_diff)
            avg_abs = np.mean(np.abs(raw_diff))
            
            if name == "Bass (20-200Hz)":
                if avg_raw < -15.0:
                    return 'FAIL', f"Catastrophic bass drop ({avg_raw:.1f} dB). The Bass Driver/Woofer is DEAD or severely blocked."
                elif avg_raw < -4.0:
                    return 'WARN', f"Missing Bass ({avg_raw:.1f} dB). Because this is a gentle drop, this is almost certainly an ACOUSTIC SEAL LEAK (missing Blu-Tack/Knetmasse in the coupler), NOT a broken driver."
                elif avg_raw > 10.0:
                    return 'FAIL', f"Massive bass boost ({avg_raw:.1f} dB). Indicates crossover failure."
            
            if name == "Highs (5k-15kHz)":
                if avg_raw < -12.0:
                    return 'FAIL', f"Massive treble drop ({avg_raw:.1f} dB). Tweeter is DEAD or the nozzle is completely clogged with earwax."
                elif avg_raw < -5.0:
                    return 'WARN', f"Missing Treble ({avg_raw:.1f} dB). The acoustic filter might be dirty/clogged with wax."
            
            # Generic fallback
            if avg_abs > 12.0:
                return 'FAIL', f"Catastrophic deviation in {name} (>{avg_abs:.1f} dB)."
            elif avg_abs > 5.0:
                return 'WARN', f"Significant deviation in {name} (~{avg_abs:.1f} dB)."
            return 'OK', f"{name} matches reference closely.""""

new_check_band = """        def check_band(mag, ref, f_min, f_max, name):
            import numpy as np
            idx = np.where((freqs >= f_min) & (freqs <= f_max))[0]
            if len(idx) == 0: return 'OK', 'Not enough data in this band.'
            
            raw_diff = mag[idx] - ref[idx]
            avg_raw = np.mean(raw_diff)
            avg_abs = np.mean(np.abs(raw_diff))
            
            # If the reference is just a generic Target Curve, DO NOT diagnose hardware defects!
            if ref_type == 'target':
                if avg_abs > 10.0:
                    return 'FAIL', f"Massive tuning deviation ({avg_raw:+.1f} dB). This IEM sounds fundamentally different from the selected Target."
                elif avg_abs > 4.0:
                    return 'WARN', f"Noticeable tuning difference ({avg_raw:+.1f} dB) compared to Target."
                return 'OK', f"Matches Target curve nicely."
                
            # If the reference is a Historical Measurement of the SAME IEM, run hardware defect diagnostics:
            if name == "Bass (20-200Hz)":
                if avg_raw < -15.0:
                    return 'FAIL', f"Catastrophic bass drop ({avg_raw:.1f} dB). The Bass Driver/Woofer is DEAD or severely blocked."
                elif avg_raw < -4.0:
                    return 'WARN', f"Missing Bass ({avg_raw:.1f} dB). This is almost certainly an ACOUSTIC SEAL LEAK, NOT a broken driver."
                elif avg_raw > 10.0:
                    return 'FAIL', f"Massive bass boost ({avg_raw:.1f} dB). Indicates crossover failure."
            
            if name == "Highs (5k-15kHz)":
                if avg_raw < -12.0:
                    return 'FAIL', f"Massive treble drop ({avg_raw:.1f} dB). Tweeter is DEAD or the nozzle is completely clogged with earwax."
                elif avg_raw < -5.0:
                    return 'WARN', f"Missing Treble ({avg_raw:.1f} dB). The acoustic filter might be dirty/clogged with wax."
            
            # Generic fallback for History
            if avg_abs > 10.0:
                return 'FAIL', f"Catastrophic deviation from Historical measurement (>{avg_abs:.1f} dB)."
            elif avg_abs > 4.0:
                return 'WARN', f"Significant deviation from Historical measurement (~{avg_abs:.1f} dB)."
            return 'OK', f"{name} matches Historical measurement perfectly.""""

content = content.replace(old_check_band, new_check_band)

with open('analysis.py', 'w') as f:
    f.write(content)
