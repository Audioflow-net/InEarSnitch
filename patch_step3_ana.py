import sys

with open('analysis_ui.py', 'r') as f:
    content = f.read()

# Fix the plotting conditions in analysis_ui.py
old_target = """            # Plot Target (CSV)
            if tgt_freqs is not None and tgt_mags is not None and (mag_l is not None or mag_r is not None):
                interp_tgt = np.interp(freqs, tgt_freqs, tgt_mags)
                idx_1k = (np.abs(freqs - 1000)).argmin()
                meas_val = mag_l[idx_1k] if mag_l is not None else (mag_r[idx_1k] if mag_r is not None else 80)
                tgt_val = interp_tgt[idx_1k]
                interp_tgt += (meas_val - tgt_val)
                f_tgt, m_tgt, _ = AudioEngine.smooth_spectrum(freqs, interp_tgt, points=240)
                self.plot_widget.plot(f_tgt, m_tgt, pen=pg.mkPen(theme.get_color('curve_target'), width=2, style=Qt.DashLine), name='Target')
                
            # Plot History (DB)
            hist_pen = pg.mkPen((255, 165, 0, 150), width=2, style=Qt.DashLine)
            if ref_mag_l is not None and mag_l is not None:
                f_ref_l, m_ref_l, _ = AudioEngine.smooth_spectrum(freqs, ref_mag_l, points=240)
                self.plot_widget.plot(f_ref_l, m_ref_l, pen=hist_pen, name='History L')
            elif ref_mag_r is not None and mag_r is not None:
                f_ref_r, m_ref_r, _ = AudioEngine.smooth_spectrum(freqs, ref_mag_r, points=240)
                self.plot_widget.plot(f_ref_r, m_ref_r, pen=hist_pen, name='History R')"""

new_target = """            # Plot Target (CSV)
            if tgt_freqs is not None and tgt_mags is not None:
                interp_tgt = np.interp(freqs, tgt_freqs, tgt_mags)
                idx_1k = (np.abs(freqs - 1000)).argmin()
                meas_val = mag_l[idx_1k] if mag_l is not None else (mag_r[idx_1k] if mag_r is not None else 80)
                tgt_val = interp_tgt[idx_1k]
                interp_tgt += (meas_val - tgt_val)
                f_tgt, m_tgt, _ = AudioEngine.smooth_spectrum(freqs, interp_tgt, points=240)
                self.plot_widget.plot(f_tgt, m_tgt, pen=pg.mkPen(theme.get_color('curve_target'), width=2, style=Qt.DashLine), name='Target')
                
            # Plot History (DB)
            hist_pen = pg.mkPen((255, 165, 0, 150), width=2, style=Qt.DashLine)
            if ref_mag_l is not None and show_l:
                f_ref_l, m_ref_l, _ = AudioEngine.smooth_spectrum(freqs, ref_mag_l, points=240)
                self.plot_widget.plot(f_ref_l, m_ref_l, pen=hist_pen, name='History L')
            if ref_mag_r is not None and not show_l:
                f_ref_r, m_ref_r, _ = AudioEngine.smooth_spectrum(freqs, ref_mag_r, points=240)
                self.plot_widget.plot(f_ref_r, m_ref_r, pen=hist_pen, name='History R')"""
content = content.replace(old_target, new_target)

with open('analysis_ui.py', 'w') as f:
    f.write(content)
