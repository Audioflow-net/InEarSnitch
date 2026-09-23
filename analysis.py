
import numpy as np

class Analyzer:
    @staticmethod
    def run_full_diagnostics(freqs, mag_l, mag_r, ref_mag_l=None, ref_mag_r=None, ir_l=None, ir_r=None, thd_data=None, csd_data=None, ref_type='target'):
        report = []
        
        # 1. Left vs Right Balance Check
        if mag_l is not None and mag_r is not None:
            # Split L/R check into two ranges:
            # Bass/Lower Mids (20-1kHz): No coupler resonances here, strict thresholds
            # Upper Mids (1k-5kHz): Coupler resonances cause natural variance, lenient thresholds
            
            # --- Range A: Bass/Lower Mids (20 Hz - 1 kHz) ---
            idx_lo = np.where((freqs >= 20) & (freqs <= 1000))[0]
            if len(idx_lo) > 0:
                diff_lo = np.abs(mag_l[idx_lo] - mag_r[idx_lo])
                max_diff_lo = np.max(diff_lo)
                avg_diff_lo = np.mean(diff_lo)
                
                if avg_diff_lo > 3.0 or max_diff_lo > 6.0:
                    report.append({'title': 'L/R Balance – Bass/Mids', 'status': 'FAIL', 'desc': f"Large volume difference in bass/mids ({max_diff_lo:.1f} dB max delta). One side may have a seal leak or dead driver.\n💡 Re-seat the IEM in the coupler and measure again to confirm.", 'band': (20, 1000)})
                elif avg_diff_lo > 1.5 or max_diff_lo > 3.0:
                    report.append({'title': 'L/R Balance – Bass/Mids', 'status': 'WARN', 'desc': f"Noticeable channel imbalance in bass/mids ({max_diff_lo:.1f} dB max delta).\n💡 Re-seat the IEM and measure again. This often fixes itself.", 'band': (20, 1000)})
                else:
                    report.append({'title': 'L/R Balance – Bass/Mids', 'status': 'OK', 'desc': "Left and Right channels are well matched in bass and mids.", 'band': None})
            
            # --- Range B: Upper Mids / Lower Treble (1 kHz - 5 kHz) ---
            idx_hi = np.where((freqs >= 1000) & (freqs <= 5000))[0]
            if len(idx_hi) > 0:
                diff_hi = np.abs(mag_l[idx_hi] - mag_r[idx_hi])
                max_diff_hi = np.max(diff_hi)
                avg_diff_hi = np.mean(diff_hi)
                
                if avg_diff_hi > 5.0 or max_diff_hi > 9.0:
                    report.append({'title': 'L/R Balance – Treble', 'status': 'FAIL', 'desc': f"Large treble imbalance ({max_diff_hi:.1f} dB max delta). Possible tweeter failure.\n💡 Re-seat IEM and measure again – insertion depth affects treble significantly.", 'band': (1000, 5000)})
                elif avg_diff_hi > 3.0 or max_diff_hi > 6.0:
                    report.append({'title': 'L/R Balance – Treble', 'status': 'WARN', 'desc': f"Some treble imbalance ({max_diff_hi:.1f} dB). Often caused by different insertion depth in the coupler.\n💡 Re-seat IEM and measure again before worrying.", 'band': (1000, 5000)})
                else:
                    report.append({'title': 'L/R Balance – Treble', 'status': 'OK', 'desc': "Left and Right treble response is well matched.", 'band': None})
                    
        # 2. Check against Reference
        def check_band(mag, ref, f_min, f_max, name):
            import numpy as np
            idx = np.where((freqs >= f_min) & (freqs <= f_max))[0]
            if len(idx) == 0: return 'OK', 'Not enough data in this band.'
            
            # Use raw difference to check if it's dropping (negative) or spiking (positive)
            raw_diff = mag[idx] - ref[idx]
            avg_raw = np.mean(raw_diff)
            avg_abs = np.mean(np.abs(raw_diff))
            
            if ref_type == 'target':
                if avg_abs > 10.0:
                    return 'FAIL', f"Massive tuning deviation ({avg_raw:+.1f} dB). This IEM sounds fundamentally different from the selected Target.\n💡 If this is unexpected, re-seat the IEM and measure again."
                elif avg_abs > 5.0:
                    return 'WARN', f"Noticeable tuning difference ({avg_raw:+.1f} dB) compared to Target.\n💡 Re-measure to confirm – coupler seal affects the result."
                return 'OK', f"Matches Target curve nicely."
                
            if name == "Bass (20-200Hz)":
                if avg_raw < -15.0:
                    return 'FAIL', f"Catastrophic bass drop ({avg_raw:.1f} dB). The Bass Driver/Woofer is DEAD or severely blocked.\n💡 Re-seat IEM with a tighter seal and measure again."
                elif avg_raw < -8.0:
                    return 'WARN', f"Bass drop ({avg_raw:.1f} dB vs. history). Likely an acoustic seal leak.\n💡 Re-seat the IEM, check blu-tack, and measure again – this is the #1 false alarm."
                elif avg_raw > 10.0:
                    return 'FAIL', f"Massive bass boost ({avg_raw:.1f} dB). Indicates crossover failure.\n💡 Re-measure to rule out a coupler anomaly."
            
            if name == "Highs (4k-7kHz)":
                if avg_raw < -15.0:
                    return 'FAIL', f"Massive treble drop ({avg_raw:.1f} dB). Tweeter is DEAD or the nozzle is completely clogged with earwax.\n💡 Clean the nozzle and re-measure."
                elif avg_raw < -8.0:
                    return 'WARN', f"Treble drop ({avg_raw:.1f} dB vs. history). Check nozzle for wax buildup.\n💡 Clean nozzle and re-measure to confirm."
            
            # Generic fallback
            if avg_abs > 12.0:
                return 'FAIL', f"Catastrophic deviation from Historical measurement (>{avg_abs:.1f} dB).\n💡 Re-seat IEM and measure again before assuming a defect."
            elif avg_abs > 6.0:
                return 'WARN', f"Significant deviation from Historical measurement (~{avg_abs:.1f} dB).\n💡 Re-measure to confirm – one bad measurement is not a diagnosis."
            return 'OK', f"{name} matches Historical measurement perfectly."
            
        if mag_l is not None and ref_mag_l is not None:
            st, msg = check_band(mag_l, ref_mag_l, 20, 200, "Bass (20-200Hz)")
            report.append({'title': 'Left Lows (Bass Driver)', 'status': st, 'desc': msg, 'band': (20, 200)})
            
            st, msg = check_band(mag_l, ref_mag_l, 200, 2000, "Mid-Range (200-2kHz)")
            report.append({'title': 'Left Mids (Mid Driver)', 'status': st, 'desc': msg, 'band': (200, 2000)})
            
            st, msg = check_band(mag_l, ref_mag_l, 4000, 7000, "Highs (4k-7kHz)")
            report.append({'title': 'Left Highs (Tweeter)', 'status': st, 'desc': msg, 'band': (4000, 7000)})
            
        if mag_r is not None and ref_mag_r is not None:
            st, msg = check_band(mag_r, ref_mag_r, 20, 200, "Bass (20-200Hz)")
            report.append({'title': 'Right Lows (Bass Driver)', 'status': st, 'desc': msg, 'band': (20, 200)})
            
            st, msg = check_band(mag_r, ref_mag_r, 200, 2000, "Mid-Range (200-2kHz)")
            report.append({'title': 'Right Mids (Mid Driver)', 'status': st, 'desc': msg, 'band': (200, 2000)})
            
            st, msg = check_band(mag_r, ref_mag_r, 4000, 7000, "Highs (4k-7kHz)")
            report.append({'title': 'Right Highs (Tweeter)', 'status': st, 'desc': msg, 'band': (4000, 7000)})
            
        # --- SINGLE CHANNEL ABSOLUTE CHECKS (If no reference and only 1 ear measured) ---
        if mag_l is not None and ref_mag_l is None and mag_r is None:
            report.extend(Analyzer.absolute_checks(freqs, mag_l, ir_l, "Left"))
        if mag_r is not None and ref_mag_r is None and mag_l is None:
            report.extend(Analyzer.absolute_checks(freqs, mag_r, ir_r, "Right"))
            
        if not report:
            report.append({
                'title': 'Insufficient Data',
                'status': 'WARN',
                'desc': 'Measure both Left and Right, or load a Target/Reference Curve to run diagnostics.',
                'band': None
            })
            
        left_inv = False
        right_inv = False
        if ir_l is not None and len(ir_l) > 0:
            left_inv = ir_l[np.argmax(np.abs(ir_l))] < 0
        if ir_r is not None and len(ir_r) > 0:
            right_inv = ir_r[np.argmax(np.abs(ir_r))] < 0

        if ir_l is not None and ir_r is not None and len(ir_l)>0 and len(ir_r)>0:
            if left_inv != right_inv:
                report.append({'title': 'Relative Phase (Polarity)', 'status': 'FAIL', 'desc': 'Left and Right channels are OUT OF PHASE with each other. This destroys the stereo image and bass.\n💡 Check the 2-pin cable orientation. If this persists after re-seating, the cable or driver wiring is inverted.', 'band': None})
            else:
                desc = 'Both channels are inverted (likely your soundcard or IEM crossover design). This is acoustically fine.' if left_inv else 'Acoustic polarity is correct (positive).'
                report.append({'title': 'Relative Phase (Polarity)', 'status': 'OK', 'desc': desc, 'band': None})
        else:
            ch = "Left" if ir_l is not None else "Right"
            inv = left_inv if ir_l is not None else right_inv
            desc = 'Inverted polarity detected, but cannot check relative phase without both channels. Often caused by soundcard.' if inv else 'Acoustic polarity is correct (positive).'
            report.append({'title': f'{ch} Polarity', 'status': 'OK', 'desc': desc, 'band': None})
                
        # Assign category FR to all existing checks
        for r in report:
            r['category'] = 'FR'

        # 5. Automated THD Diagnostics
        if thd_data is not None:
            thd_freqs, thd_l, thd_r = thd_data
            if thd_l is not None:
                thd_rep = Analyzer.evaluate_thd(thd_freqs, thd_l, "Left")
                for r in thd_rep: r['category'] = 'THD'
                report.extend(thd_rep)
            if thd_r is not None:
                thd_rep = Analyzer.evaluate_thd(thd_freqs, thd_r, "Right")
                for r in thd_rep: r['category'] = 'THD'
                report.extend(thd_rep)
                
        # 6. Automated CSD Diagnostics
        if csd_data is not None:
            # csd_data is dict: {'L': (freqs, times, csd_mag), 'R': ...}
            if 'L' in csd_data and csd_data['L'] is not None:
                cf, ct, cm = csd_data['L']
                csd_rep = Analyzer.evaluate_csd(cf, ct, cm, "Left")
                for r in csd_rep: r['category'] = 'CSD'
                report.extend(csd_rep)
            if 'R' in csd_data and csd_data['R'] is not None:
                cf, ct, cm = csd_data['R']
                csd_rep = Analyzer.evaluate_csd(cf, ct, cm, "Right")
                for r in csd_rep: r['category'] = 'CSD'
                report.extend(csd_rep)

        return report

    @staticmethod
    def absolute_checks(freqs, mag, ir, channel):
        if freqs is None or len(freqs) == 0:
            return []
            
        report = []
        idx_1k = (np.abs(freqs - 1000)).argmin()
        idx_50 = (np.abs(freqs - 50)).argmin()
        idx_5k = (np.abs(freqs - 5000)).argmin()
        
        val_1k = mag[idx_1k]
        val_50 = mag[idx_50]
        val_5k = mag[idx_5k]
        
        if val_50 < val_1k - 20:
            report.append({'title': f'{channel} Bass / Acoustic Seal', 'status': 'FAIL', 'desc': f'Severe bass roll-off detected ({val_50-val_1k:.1f} dB drop at 50Hz). This indicates a massive air leak or a dead Dynamic Driver.\n💡 Re-seat the IEM with a tighter seal and measure again.', 'band': (20, 100)})
        elif val_50 < val_1k - 14:
            report.append({'title': f'{channel} Bass / Acoustic Seal', 'status': 'WARN', 'desc': f'Noticeable bass roll-off ({val_50-val_1k:.1f} dB). Could be a seal leak or normal BA driver roll-off.\n💡 Re-seat IEM in coupler and measure again – this is the #1 false alarm.', 'band': (20, 100)})
        else:
            report.append({'title': f'{channel} Bass / Acoustic Seal', 'status': 'OK', 'desc': 'Bass extension is within normal limits for typical IEM tunings.', 'band': None})
            
        idx_4k = (np.abs(freqs - 4000)).argmin()
        idx_8k = (np.abs(freqs - 8000)).argmin()
        if idx_4k < idx_8k and len(mag[idx_4k:idx_8k]) > 0:
            # PRO-AUDIO UPDATE: Calculate average using linear power, not dB!
            linear_pwr = 10 ** (mag[idx_4k:idx_8k] / 20.0)
            avg_highs = 20 * np.log10(np.mean(linear_pwr) + 1e-12)
        else:
            avg_highs = val_5k
        
        if avg_highs < val_1k - 12:
            report.append({'title': f'{channel} Highs / Wax Clog', 'status': 'FAIL', 'desc': f'Severe high-frequency drop ({avg_highs - val_1k:.0f} dB vs 1 kHz). Nozzle is likely clogged with wax or tweeter is dead.\n💡 Clean the nozzle and re-measure to confirm.', 'band': (4000, 8000)})
        elif avg_highs < val_1k - 5:
            report.append({'title': f'{channel} Highs / Wax Clog', 'status': 'WARN', 'desc': f'Noticeable high-frequency drop ({avg_highs - val_1k:.0f} dB vs 1 kHz). Possible wax buildup in the nozzle.\n💡 Clean nozzle, re-seat IEM in coupler, and measure again.', 'band': (4000, 8000)})
        else:
            report.append({'title': f'{channel} Highs / Wax Clog', 'status': 'OK', 'desc': 'High frequencies are reaching the microphone properly (no severe wax clog).', 'band': None})
            
        return report

    @staticmethod
    def evaluate_thd(freqs, thd_percentage, channel="Left"):
        """
        Evaluates the THD across the frequency spectrum.
        
        Args:
            freqs (np.ndarray): Array of frequencies.
            thd_percentage (np.ndarray): Array of THD percentages.
            channel (str): The channel being evaluated.
            
        Returns:
            list: Diagnostics report items for THD.
        """
        report = []
        
        # Check mid-band THD (500Hz - 2kHz)
        # NOTE: These lenient thresholds compensate for missing noise-floor subtraction.
        # Once noise-floor measurement is implemented, lower to: FAIL max>3.0/avg>1.0, WARN max>1.0/avg>0.5
        idx_mid = np.where((freqs >= 500) & (freqs <= 2000))[0]
        if len(idx_mid) > 0:
            avg_thd_mid = np.clip(np.mean(thd_percentage[idx_mid]), 0, 100)
            max_thd_mid = np.clip(np.max(thd_percentage[idx_mid]), 0, 100)
            
            if max_thd_mid > 8.0 or avg_thd_mid > 3.0:
                report.append({'title': f'{channel} Mid-Band Distortion (THD)', 'status': 'FAIL', 'desc': f'High distortion in mid-range (Max: {max_thd_mid:.1f}%, Avg: {avg_thd_mid:.1f}%). Possible driver damage.\n💡 Ensure the room is quiet and measure again to rule out background noise.', 'band': (500, 2000), 'category': 'THD'})
            elif max_thd_mid > 4.0 or avg_thd_mid > 1.5:
                report.append({'title': f'{channel} Mid-Band Distortion (THD)', 'status': 'WARN', 'desc': f'Elevated distortion in mid-range (Max: {max_thd_mid:.1f}%, Avg: {avg_thd_mid:.1f}%).\n💡 Measure again in a quiet room to confirm.', 'band': (500, 2000), 'category': 'THD'})
            else:
                report.append({'title': f'{channel} Mid-Band Distortion (THD)', 'status': 'OK', 'desc': f'Mid-range THD within normal limits (Avg: {avg_thd_mid:.1f}%).', 'band': (500, 2000), 'category': 'THD'})
                
        # Check bass THD (50Hz - 200Hz)
        # NOTE: Lenient thresholds — no noise-floor subtraction yet.
        idx_bass = np.where((freqs >= 50) & (freqs <= 200))[0]
        if len(idx_bass) > 0:
            avg_thd_bass = np.clip(np.mean(thd_percentage[idx_bass]), 0, 100)
            max_thd_bass = np.clip(np.max(thd_percentage[idx_bass]), 0, 100)
            
            if max_thd_bass > 15.0 or avg_thd_bass > 8.0:
                report.append({'title': f'{channel} Bass Distortion (THD)', 'status': 'FAIL', 'desc': f'Severe distortion in bass (Max: {max_thd_bass:.1f}%, Avg: {avg_thd_bass:.1f}%). Check seal and driver.\n💡 Ensure no vibrations nearby (footsteps, HVAC). Re-seat IEM and measure again.', 'band': (50, 200), 'category': 'THD'})
            elif max_thd_bass > 8.0 or avg_thd_bass > 4.0:
                report.append({'title': f'{channel} Bass Distortion (THD)', 'status': 'WARN', 'desc': f'Elevated bass distortion (Max: {max_thd_bass:.1f}%, Avg: {avg_thd_bass:.1f}%). BA drivers naturally have higher bass THD.\n💡 Measure again in a quiet, vibration-free environment to confirm.', 'band': (50, 200), 'category': 'THD'})
            else:
                report.append({'title': f'{channel} Bass Distortion (THD)', 'status': 'OK', 'desc': f'Bass THD acceptable (Avg: {avg_thd_bass:.1f}%).', 'band': (50, 200), 'category': 'THD'})
                
        # Check treble THD (8kHz - 20kHz)
        # NOTE: IEC711 coupler resonance (~8kHz) naturally inflates treble THD readings.
        idx_treble = np.where((freqs >= 8000) & (freqs <= 20000))[0]
        if len(idx_treble) > 0:
            avg_thd_treble = np.clip(np.mean(thd_percentage[idx_treble]), 0, 100)
            max_thd_treble = np.clip(np.max(thd_percentage[idx_treble]), 0, 100)
            
            if max_thd_treble > 10.0 or avg_thd_treble > 5.0:
                report.append({'title': f'{channel} Treble Distortion (THD)', 'status': 'FAIL', 'desc': f'High distortion in treble (Max: {max_thd_treble:.1f}%, Avg: {avg_thd_treble:.1f}%).', 'band': (8000, 20000), 'category': 'THD'})
            elif max_thd_treble > 5.0 or avg_thd_treble > 2.5:
                report.append({'title': f'{channel} Treble Distortion (THD)', 'status': 'WARN', 'desc': f'Elevated distortion in treble (Max: {max_thd_treble:.1f}%, Avg: {avg_thd_treble:.1f}%).', 'band': (8000, 20000), 'category': 'THD'})
            else:
                report.append({'title': f'{channel} Treble Distortion (THD)', 'status': 'OK', 'desc': f'Treble THD acceptable (Avg: {avg_thd_treble:.1f}%).', 'band': (8000, 20000), 'category': 'THD'})

        return report

    @staticmethod
    def evaluate_csd(freqs, times, csd_mag, channel="Left"):
        """
        Evaluates the Cumulative Spectral Decay (CSD) for unwanted resonances.
        
        Args:
            freqs (np.ndarray): Array of frequencies.
            times (np.ndarray): Array of time slices (in ms).
            csd_mag (np.ndarray): 2D array of magnitudes (slices x freqs).
            channel (str): The channel being evaluated.
            
        Returns:
            list: Diagnostics report items for CSD.
        """
        report = []
        
        if csd_mag.shape[0] < 2:
            return report
            
        # Check for lingering resonances in treble (2kHz-7kHz, avoid 8kHz coupler resonance)
        idx_treble = np.where((freqs >= 2000) & (freqs <= 7000))[0]
        
        if len(idx_treble) > 0 and len(times) > 0:
            # Find a time slice around 1.5ms (BA drivers should decay ~20+ dB by then)
            t_target = 1.5
            slice_idx = (np.abs(times - t_target)).argmin()
            
            if times[slice_idx] >= 0.8:
                mag_initial = csd_mag[0, idx_treble]
                mag_later = csd_mag[slice_idx, idx_treble]
                
                decay = mag_initial - mag_later
                avg_decay = np.mean(decay)
                
                if avg_decay < 10.0:
                    report.append({'title': f'{channel} Treble Resonance (CSD)', 'status': 'WARN', 'desc': f'Slow treble decay ({avg_decay:.0f} dB after {times[slice_idx]:.1f}ms). May indicate an undamped BA resonance or missing acoustic filter.\n💡 Measure again to confirm – this can be caused by background noise.', 'band': (2000, 7000), 'category': 'CSD'})
                else:
                    report.append({'title': f'{channel} Treble Resonance (CSD)', 'status': 'OK', 'desc': f'Clean decay in treble ({avg_decay:.0f} dB after {times[slice_idx]:.1f}ms).', 'band': (2000, 7000), 'category': 'CSD'})
                    
        return report

