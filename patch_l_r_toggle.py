import sys

with open('analysis_ui.py', 'r') as f:
    content = f.read()

old_logic = """        # Filter based on toggle
        show_l = self.btn_chan_l.isChecked()
        mag_l = orig_mag_l if show_l else None
        mag_r = orig_mag_r if not show_l else None
        ir_l_f = ir_l if show_l else None
        ir_r_f = ir_r if not show_l else None"""

new_logic = """        # Filter based on toggle independently!
        show_l = self.btn_chan_l.isChecked()
        show_r = self.btn_chan_r.isChecked()
        mag_l = orig_mag_l if show_l else None
        mag_r = orig_mag_r if show_r else None
        ir_l_f = ir_l if show_l else None
        ir_r_f = ir_r if show_r else None"""
content = content.replace(old_logic, new_logic)

# Then update history plotting condition
old_hist = """            if ref_mag_l is not None and show_l:
                f_ref_l, m_ref_l, _ = AudioEngine.smooth_spectrum(freqs, ref_mag_l, points=240)
                self.plot_widget.plot(f_ref_l, m_ref_l, pen=hist_pen, name='History L')
            if ref_mag_r is not None and not show_l:
                f_ref_r, m_ref_r, _ = AudioEngine.smooth_spectrum(freqs, ref_mag_r, points=240)
                self.plot_widget.plot(f_ref_r, m_ref_r, pen=hist_pen, name='History R')"""

new_hist = """            if ref_mag_l is not None and show_l:
                f_ref_l, m_ref_l, _ = AudioEngine.smooth_spectrum(freqs, ref_mag_l, points=240)
                self.plot_widget.plot(f_ref_l, m_ref_l, pen=hist_pen, name='History L')
            if ref_mag_r is not None and show_r:
                f_ref_r, m_ref_r, _ = AudioEngine.smooth_spectrum(freqs, ref_mag_r, points=240)
                self.plot_widget.plot(f_ref_r, m_ref_r, pen=hist_pen, name='History R')"""
content = content.replace(old_hist, new_hist)

with open('analysis_ui.py', 'w') as f:
    f.write(content)
