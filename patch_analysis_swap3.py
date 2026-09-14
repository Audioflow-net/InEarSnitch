import re

with open("analysis_ui.py", "r") as f:
    code = f.read()

old_end_setup = """        self.scroll.setWidget(self.report_container)
        self.splitter.addWidget(self.scroll)
        
        self.splitter.setSizes([450, 250])"""

new_end_setup = """        self.scroll.setWidget(self.report_container)
        self.splitter.addWidget(self.scroll)
        
        self.splitter.setSizes([450, 250])
        
        # Grid Swapping Logic
        self.current_main_widget = self.plot_widget
        self.grid_widgets = [self.plot_widget, self.thd_widget, self.csd_widget]
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

with open("analysis_ui.py", "w") as f:
    f.write(code)

print("Analysis swap patched 3.")
