import sys

with open('analysis_ui.py', 'r') as f:
    content = f.read()

old_tgt_plot = """            # Plot Target (CSV)
            print("TGT FREQS", tgt_freqs is not None, "TGT MAGS", tgt_mags is not None, "FREQS", freqs is not None)
            if tgt_freqs is not None and tgt_mags is not None:
                interp_tgt = np.interp(freqs, tgt_freqs, tgt_mags)
                idx_1k = (np.abs(freqs - 1000)).argmin()
                meas_val = mag_l[idx_1k] if mag_l is not None else (mag_r[idx_1k] if mag_r is not None else 80)
                if meas_val < 30 or meas_val > 140:
                    meas_val = 80  # Prevent aligning target to silence or garbage
                tgt_val = interp_tgt[idx_1k]
                interp_tgt += (meas_val - tgt_val)
                f_tgt, m_tgt, _ = AudioEngine.smooth_spectrum(freqs, interp_tgt, points=240)
                self.plot_widget.plot(f_tgt, m_tgt, pen=pg.mkPen(theme.get_color('curve_target'), width=2, style=Qt.DashLine), name='Target')"""

new_tgt_plot = """            # Plot Target (CSV)
            if tgt_freqs is not None and tgt_mags is not None:
                try:
                    import numpy as np
                    interp_tgt = np.interp(freqs, tgt_freqs, tgt_mags)
                    idx_1k = (np.abs(freqs - 1000)).argmin()
                    meas_val = mag_l[idx_1k] if mag_l is not None else (mag_r[idx_1k] if mag_r is not None else 80)
                    if meas_val < 30 or meas_val > 140:
                        meas_val = 80  # Prevent aligning target to silence or garbage
                    tgt_val = interp_tgt[idx_1k]
                    interp_tgt += (meas_val - tgt_val)
                    f_tgt, m_tgt, _ = AudioEngine.smooth_spectrum(freqs, interp_tgt, points=240)
                    self.plot_widget.plot(f_tgt, m_tgt, pen=pg.mkPen(theme.get_color('curve_target'), width=2, style=Qt.DashLine), name='Target')
                except Exception as e:
                    print("Target plot failed:", e)"""

content = content.replace(old_tgt_plot, new_tgt_plot)

with open('analysis_ui.py', 'w') as f:
    f.write(content)
