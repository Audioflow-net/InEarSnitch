import re

with open("analysis_ui.py", "r") as f:
    code = f.read()

old_code = """        if freqs is not None:
            from audio_engine import AudioEngine
            if mag_l is not None:
                f_l, m_l, _ = AudioEngine.smooth_spectrum(freqs, mag_l, points=240)
                self.plot_widget.plot(f_l, m_l, pen=pg.mkPen(theme.get_color('curve_left'), width=2), name='Left')
            if mag_r is not None:
                f_r, m_r, _ = AudioEngine.smooth_spectrum(freqs, mag_r, points=240)
                self.plot_widget.plot(f_r, m_r, pen=pg.mkPen(theme.get_color('curve_right'), width=2, style=Qt.DashLine), name='Right')
            if best_ref_l is not None:
                f_ref, m_ref, _ = AudioEngine.smooth_spectrum(freqs, best_ref_l, points=240)
                self.plot_widget.plot(f_ref, m_ref, pen=pg.mkPen(theme.get_color('curve_target'), width=1, style=Qt.DotLine), name='Target/Reference')"""

new_code = """        if freqs is not None:
            from audio_engine import AudioEngine
            if mag_l is not None:
                f_l, m_l, _ = AudioEngine.smooth_spectrum(freqs, mag_l, points=240)
                self.plot_widget.plot(f_l, m_l, pen=pg.mkPen(theme.get_color('curve_left'), width=2), name='Left')
            if mag_r is not None:
                f_r, m_r, _ = AudioEngine.smooth_spectrum(freqs, mag_r, points=240)
                self.plot_widget.plot(f_r, m_r, pen=pg.mkPen(theme.get_color('curve_right'), width=2, style=Qt.DashLine), name='Right')
                
            # Plot Target (CSV)
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
            if ref_mag_l is not None and mag_l is not None:
                f_ref_l, m_ref_l, _ = AudioEngine.smooth_spectrum(freqs, ref_mag_l, points=240)
                self.plot_widget.plot(f_ref_l, m_ref_l, pen=hist_pen, name='History L')
            elif ref_mag_r is not None and mag_r is not None:
                f_ref_r, m_ref_r, _ = AudioEngine.smooth_spectrum(freqs, ref_mag_r, points=240)
                self.plot_widget.plot(f_ref_r, m_ref_r, pen=hist_pen, name='History R')"""

code = code.replace(old_code, new_code)

with open("analysis_ui.py", "w") as f:
    f.write(code)

print("plot logic updated.")
