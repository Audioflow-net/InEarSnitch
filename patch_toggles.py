import sys

with open('main.py', 'r') as f:
    content = f.read()

# 1. Fix the connected signals to prevent TypeError (lambda fixes it and adds update for analysis page)
old_tgt_conn = "self.btn_toggle_target.clicked.connect(self.redraw_graph)"
new_tgt_conn = "self.btn_toggle_target.clicked.connect(lambda: self.redraw_graph() or (self.page_ana.refresh_view() if hasattr(self, 'page_ana') else None))"
content = content.replace(old_tgt_conn, new_tgt_conn)

old_hist_conn = "self.btn_toggle_history.clicked.connect(self.redraw_graph)"
new_hist_conn = "self.btn_toggle_history.clicked.connect(lambda: self.redraw_graph() or (self.page_ana.refresh_view() if hasattr(self, 'page_ana') else None))"
content = content.replace(old_hist_conn, new_hist_conn)

# 2. Inject main_window reference to analysis_ui
old_ana_init = "self.page_ana = AnalysisWidget()"
new_ana_init = "self.page_ana = AnalysisWidget()\n        self.page_ana.main_window = self"
content = content.replace(old_ana_init, new_ana_init)

with open('main.py', 'w') as f:
    f.write(content)


with open('analysis_ui.py', 'r') as f:
    ana_content = f.read()

# 3. Prevent drawing and processing in analysis_ui if toggled off
# Find the start of the reference determination in refresh_view
old_ref_logic = """        # Determine best reference
        best_ref_l = None
        best_ref_r = None
        
        if tgt_freqs is not None and tgt_mags is not None:
            import numpy as np
            interp_tgt = np.interp(freqs, tgt_freqs, tgt_mags)
            idx_1k = (np.abs(freqs - 1000)).argmin()
            meas_val = mag_l[idx_1k] if mag_l is not None else (mag_r[idx_1k] if mag_r is not None else 80)
            tgt_val = interp_tgt[idx_1k]
            interp_tgt += (meas_val - tgt_val)
            best_ref_l = interp_tgt
            best_ref_r = interp_tgt
        elif ref_mag_l is not None or ref_mag_r is not None:
            best_ref_l = ref_mag_l
            best_ref_r = ref_mag_r
            
        ref_type = 'target' if (tgt_freqs is not None and tgt_mags is not None) else 'history'"""

new_ref_logic = """        # Determine best reference
        best_ref_l = None
        best_ref_r = None
        
        import numpy as np
        
        target_on = hasattr(self, 'main_window') and hasattr(self.main_window, 'btn_toggle_target') and self.main_window.btn_toggle_target.isChecked()
        history_on = hasattr(self, 'main_window') and hasattr(self.main_window, 'btn_toggle_history') and self.main_window.btn_toggle_history.isChecked()
        
        # Override to None if toggled off
        if not target_on:
            tgt_freqs = None
            tgt_mags = None
        if not history_on:
            ref_mag_l = None
            ref_mag_r = None
            
        if tgt_freqs is not None and tgt_mags is not None:
            interp_tgt = np.interp(freqs, tgt_freqs, tgt_mags)
            idx_1k = (np.abs(freqs - 1000)).argmin()
            meas_val = mag_l[idx_1k] if mag_l is not None else (mag_r[idx_1k] if mag_r is not None else 80)
            tgt_val = interp_tgt[idx_1k]
            interp_tgt += (meas_val - tgt_val)
            best_ref_l = interp_tgt
            best_ref_r = interp_tgt
        elif ref_mag_l is not None or ref_mag_r is not None:
            best_ref_l = ref_mag_l
            best_ref_r = ref_mag_r
            
        ref_type = 'target' if (tgt_freqs is not None and tgt_mags is not None) else 'history'"""

ana_content = ana_content.replace(old_ref_logic, new_ref_logic)

with open('analysis_ui.py', 'w') as f:
    f.write(ana_content)
