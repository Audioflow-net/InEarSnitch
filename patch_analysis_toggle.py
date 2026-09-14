import re

with open("analysis_ui.py", "r") as f:
    code = f.read()

# 1. Add the toggle buttons to UI
ui_old = """        zoom_layout = QHBoxLayout()
        zoom_layout.addWidget(QLabel("ZOOM:", styleSheet="color: " + theme.get_color("text_secondary") + "; font-weight: bold; font-size: 11px;"))
        
        self.btn_zoom_bass = QPushButton("Bass")"""

ui_new = """        zoom_layout = QHBoxLayout()
        
        # --- Channel Toggle ---
        self.btn_chan_l = QPushButton("Left (L)")
        self.btn_chan_r = QPushButton("Right (R)")
        self.btn_chan_l.setCheckable(True)
        self.btn_chan_r.setCheckable(True)
        self.btn_chan_l.setChecked(True) # Default
        
        from PyQt5.QtWidgets import QButtonGroup
        self.chan_grp = QButtonGroup()
        self.chan_grp.addWidget(self.btn_chan_l)
        self.chan_grp.addWidget(self.btn_chan_r)
        
        for b in [self.btn_chan_l, self.btn_chan_r]:
            b.setCursor(Qt.PointingHandCursor)
            b.setStyleSheet("QPushButton { background-color: #222; color: #888; border: 1px solid #444; padding: 4px 16px; font-size: 12px; font-weight: bold; border-radius: 4px; } "
                            "QPushButton:checked { background-color: #00FF99; color: #000; border: 1px solid #00FF99; }")
            zoom_layout.addWidget(b)
            
        self.btn_chan_l.clicked.connect(self.refresh_view)
        self.btn_chan_r.clicked.connect(self.refresh_view)
        
        zoom_layout.addSpacing(20)
        
        # --- Zoom Controls ---
        zoom_layout.addWidget(QLabel("ZOOM:", styleSheet="color: " + theme.get_color("text_secondary") + "; font-weight: bold; font-size: 11px;"))
        
        self.btn_zoom_bass = QPushButton("Bass")"""
code = code.replace(ui_old, ui_new)

# 2. Modify update_analysis to store data and call refresh_view
ua_old = """    def update_analysis(self, freqs, mag_l, mag_r, ref_mag_l=None, ref_mag_r=None, tgt_freqs=None, tgt_mags=None, thd_data=None, csd_data=None):
        # Clear old report
        for i in reversed(range(self.report_layout.count())): 
            w = self.report_layout.itemAt(i).widget()
            if w:
                w.deleteLater()"""

ua_new = """    def update_analysis(self, freqs, mag_l, mag_r, ref_mag_l=None, ref_mag_r=None, tgt_freqs=None, tgt_mags=None, thd_data=None, csd_data=None):
        self._last_data = (freqs, mag_l, mag_r, ref_mag_l, ref_mag_r, tgt_freqs, tgt_mags, thd_data, csd_data)
        
        # Auto-switch to the channel that actually has data
        if mag_l is None and mag_r is not None:
            self.btn_chan_r.setChecked(True)
        elif mag_r is None and mag_l is not None:
            self.btn_chan_l.setChecked(True)
            
        self.refresh_view()
        
    def refresh_view(self):
        if not hasattr(self, '_last_data'): return
        freqs, orig_mag_l, orig_mag_r, ref_mag_l, ref_mag_r, tgt_freqs, tgt_mags, thd_data, csd_data = self._last_data
        
        # Filter based on toggle
        show_l = self.btn_chan_l.isChecked()
        mag_l = orig_mag_l if show_l else None
        mag_r = orig_mag_r if not show_l else None
        
        # Clear old report
        for i in reversed(range(self.report_layout.count())): 
            w = self.report_layout.itemAt(i).widget()
            if w:
                w.deleteLater()"""
code = code.replace(ua_old, ua_new)

# 3. Fix thd_data rendering in refresh_view (since update_analysis used thd_data directly)
# Search for:
#        if thd_data:
#            thd_freqs, thd_l, thd_r = thd_data
thd_old = """        if thd_data:
            thd_freqs, thd_l, thd_r = thd_data
            if thd_l is not None:
                self.thd_plot.plot(thd_freqs, thd_l, pen=pg.mkPen(theme.get_color('curve_left'), width=2), name='Left THD')
            if thd_r is not None:
                self.thd_plot.plot(thd_freqs, thd_r, pen=pg.mkPen(theme.get_color('curve_right'), width=2, style=Qt.DashLine), name='Right THD')"""
thd_new = """        if thd_data:
            thd_freqs, orig_thd_l, orig_thd_r = thd_data
            thd_l = orig_thd_l if show_l else None
            thd_r = orig_thd_r if not show_l else None
            
            if thd_l is not None:
                self.thd_plot.plot(thd_freqs, thd_l, pen=pg.mkPen(theme.get_color('curve_left'), width=2), name='Left THD')
            if thd_r is not None:
                self.thd_plot.plot(thd_freqs, thd_r, pen=pg.mkPen(theme.get_color('curve_right'), width=2, style=Qt.DashLine), name='Right THD')"""
code = code.replace(thd_old, thd_new)

# 4. Fix CSD data rendering
csd_old = """        if csd_data:
            csd_freqs, csd_slices = csd_data
            for i, (f_slice, m_slice) in enumerate(csd_slices):"""
csd_new = """        if csd_data and orig_mag_l is not None and show_l: # Only show CSD if it matches the left channel logic... wait CSD in main.py is currently only calculated for temp_mag_l!
            # Since CSD is currently heavily hardcoded to the left channel in main.py, we just show it if left is selected.
            # Or if it's generic, just show it regardless. We will show it if the toggle matches the CSD channel. 
            csd_freqs, csd_slices = csd_data
            for i, (f_slice, m_slice) in enumerate(csd_slices):"""
code = code.replace(csd_old, csd_new)

with open("analysis_ui.py", "w") as f:
    f.write(code)

print("Analysis Toggle Patched.")
