import re

with open("analysis_ui.py", "r") as f:
    code = f.read()

# 1. Update setup_ui to save right_graphs_layout and setup click events
old_setup_plots = """        # 2. THD Plot
        self.thd_widget = pg.PlotWidget(title="THD (Total Harmonic Distortion)", axisItems={"bottom": FreqAxisItem(orientation="bottom")})"""

new_setup_plots = """        # 2. THD Plot
        self.right_graphs_layout = right_graphs_layout # Save layout reference
        self.thd_widget = pg.PlotWidget(title="THD (Total Harmonic Distortion)", axisItems={"bottom": FreqAxisItem(orientation="bottom")})"""
code = code.replace(old_setup_plots, new_setup_plots)

# Add swapping logic at the end of setup_ui
old_end_setup = """        self.scroll.setWidget(self.report_container)
        self.splitter.addWidget(self.scroll)
        
        main_layout.addWidget(self.splitter)"""

new_end_setup = """        self.scroll.setWidget(self.report_container)
        self.splitter.addWidget(self.scroll)
        
        main_layout.addWidget(self.splitter)
        
        # Grid Swapping Logic
        self.current_main_widget = self.plot_main
        self.grid_widgets = [self.plot_main, self.thd_widget, self.csd_widget]
        for w in self.grid_widgets:
            # We must use a wrapper function to capture w correctly in the lambda
            w.scene().sigMouseClicked.connect(self._create_click_handler(w))
            
    def _create_click_handler(self, w):
        return lambda ev: self.swap_to_main(ev, w)
        
    def swap_to_main(self, ev, target_widget):
        from PyQt5.QtCore import Qt
        if ev.button() != Qt.LeftButton or target_widget == self.current_main_widget:
            return
            
        old_main = self.current_main_widget
        
        # Find index of target_widget in right_graphs_layout
        idx = -1
        for i in range(self.right_graphs_layout.count()):
            if self.right_graphs_layout.itemAt(i).widget() == target_widget:
                idx = i
                break
                
        if idx != -1:
            # Swap in layouts
            self.plots_layout.removeWidget(old_main)
            self.right_graphs_layout.removeWidget(target_widget)
            
            self.plots_layout.insertWidget(0, target_widget, stretch=2)
            self.right_graphs_layout.insertWidget(idx, old_main)
            
            self.current_main_widget = target_widget"""
code = code.replace(old_end_setup, new_end_setup)

# 2. Update Zoom buttons to target self.current_main_widget
old_zoom_bass = """    def btn_zoom_bass(self):
        self.plot_main.setXRange(np.log10(20), np.log10(300), padding=0)"""
new_zoom_bass = """    def btn_zoom_bass(self):
        self.current_main_widget.setXRange(np.log10(20), np.log10(300), padding=0)"""
code = code.replace(old_zoom_bass, new_zoom_bass)

old_zoom_mids = """    def btn_zoom_mids(self):
        self.plot_main.setXRange(np.log10(300), np.log10(4000), padding=0)"""
new_zoom_mids = """    def btn_zoom_mids(self):
        self.current_main_widget.setXRange(np.log10(300), np.log10(4000), padding=0)"""
code = code.replace(old_zoom_mids, new_zoom_mids)

old_zoom_treble = """    def btn_zoom_treble(self):
        self.plot_main.setXRange(np.log10(4000), np.log10(20000), padding=0)"""
new_zoom_treble = """    def btn_zoom_treble(self):
        self.current_main_widget.setXRange(np.log10(4000), np.log10(20000), padding=0)"""
code = code.replace(old_zoom_treble, new_zoom_treble)

old_zoom_all = """    def btn_zoom_all(self):
        self.plot_main.setXRange(np.log10(20), np.log10(20000), padding=0)"""
new_zoom_all = """    def btn_zoom_all(self):
        self.current_main_widget.setXRange(np.log10(20), np.log10(20000), padding=0)"""
code = code.replace(old_zoom_all, new_zoom_all)

with open("analysis_ui.py", "w") as f:
    f.write(code)

print("Analysis swap patched.")
