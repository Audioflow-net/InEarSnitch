import re

with open('analysis_ui.py', 'r') as f:
    content = f.read()

old_reset = """    def reset_zoom(self):
        if hasattr(self, 'plot_widget'):
            self.plot_widget.getViewBox().autoRange()
        if hasattr(self, 'thd_widget'):
            self.thd_widget.getViewBox().autoRange()
        if hasattr(self, 'csd_widget'):
            self.csd_widget.getViewBox().autoRange()"""

new_reset = """    def reset_zoom(self):
        import numpy as np
        if hasattr(self, 'plot_widget'):
            self.plot_widget.setXRange(np.log10(20), np.log10(20000), padding=0.0)
            self.plot_widget.setYRange(40, 110, padding=0.0)
        if hasattr(self, 'thd_widget'):
            self.thd_widget.setXRange(np.log10(20), np.log10(20000), padding=0.0)
            self.thd_widget.setYRange(0, 5, padding=0.0)
        if hasattr(self, 'csd_widget'):
            self.csd_widget.setXRange(np.log10(2000), np.log10(20000), padding=0.0)
            self.csd_widget.setYRange(-60, 20, padding=0.0)"""

content = content.replace(old_reset, new_reset)
with open('analysis_ui.py', 'w') as f:
    f.write(content)

with open('history_ui.py', 'r') as f:
    content = f.read()

content = content.replace(
    "self.btn_reset_zoom.clicked.connect(lambda: self.plot_widget.autoRange())",
    "self.btn_reset_zoom.clicked.connect(self.reset_zoom)"
)

# Insert the function
reset_func = """
    def reset_zoom(self):
        import numpy as np
        self.plot_widget.setXRange(np.log10(20), np.log10(20000), padding=0.0)
        self.plot_widget.setYRange(40, 110, padding=0.0)
"""
# insert before def load_history
content = content.replace("    def load_history(", reset_func + "\n    def load_history(")

# Also apply it at startup in history_ui
init_patch = """        self.plot_widget.addLegend()
        self.reset_zoom()"""
content = content.replace("        self.plot_widget.addLegend()", init_patch)

with open('history_ui.py', 'w') as f:
    f.write(content)
print("SUCCESS")
