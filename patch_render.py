import sys

with open('analysis_ui.py', 'r') as f:
    content = f.read()

# 1. Connect currentChanged to render_diagnostics in __init__
init_hook_old = """        # Default state
        self.btn_chan_l.setChecked(True)"""
init_hook_new = """        # Default state
        self.btn_chan_l.setChecked(True)
        
        self.graph_tabs.currentChanged.connect(self.render_diagnostics)
        self._last_report = []"""
content = content.replace(init_hook_old, init_hook_new)

# 2. Extract the loop into render_diagnostics and replace it in update_analysis
# The loop starts with `for item in report:`
# Wait, I also need to clear self.diag_layout!
# Let's see what is immediately before `for item in report:`
before_loop = """            if ref_mag_r is not None and show_r:
                f_ref_r, m_ref_r, _ = AudioEngine.smooth_spectrum(freqs, ref_mag_r, points=240)
                self.plot_widget.plot(f_ref_r, m_ref_r, pen=hist_pen, name='History R')
                
        for item in report:"""

after_loop = """                card.mousePressEvent = make_zoom(item['band'])
            
            self.diag_layout.addWidget(card)
            
        self.diag_layout.addStretch()
        
    def show_eq_overlay(self):"""

# Let's capture the exact text from line 494 to 552
