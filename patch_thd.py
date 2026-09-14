import re

with open("analysis_ui.py", "r") as f:
    code = f.read()

thd_old = """        # --- Update THD Plot ---
        self.thd_widget.clear()
        if thd_data is not None:
            # Expected format: (thd_freqs, thd_l, thd_r)
            thd_freqs, thd_l, thd_r = thd_data
            if thd_l is not None:
                self.thd_widget.plot(thd_freqs, thd_l, pen=pg.mkPen(theme.get_color('curve_left'), width=2), name='Left THD')
            if thd_r is not None:
                self.thd_widget.plot(thd_freqs, thd_r, pen=pg.mkPen(theme.get_color('curve_right'), width=2, style=Qt.DashLine), name='Right THD')"""

thd_new = """        # --- Update THD Plot ---
        self.thd_widget.clear()
        if thd_data is not None:
            # Expected format: (thd_freqs, orig_thd_l, orig_thd_r)
            thd_freqs, orig_thd_l, orig_thd_r = thd_data
            
            show_l = self.btn_chan_l.isChecked()
            thd_l = orig_thd_l if show_l else None
            thd_r = orig_thd_r if not show_l else None
            
            if thd_l is not None:
                self.thd_widget.plot(thd_freqs, thd_l, pen=pg.mkPen(theme.get_color('curve_left'), width=2), name='Left THD')
            if thd_r is not None:
                self.thd_widget.plot(thd_freqs, thd_r, pen=pg.mkPen(theme.get_color('curve_right'), width=2, style=Qt.DashLine), name='Right THD')"""

code = code.replace(thd_old, thd_new)

with open("analysis_ui.py", "w") as f:
    f.write(code)

print("THD Toggle Patched.")
