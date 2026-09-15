import re

with open("analysis_ui.py", "r") as f:
    content = f.read()

# Disable AutoRange completely on CSD widget
content = content.replace("self.csd_widget.setYRange(-60, 20)", "self.csd_widget.setYRange(-60, 20)\n        self.csd_widget.getViewBox().disableAutoRange()")

# Also, when switching tabs, let's trigger an explicit bounds lock for CSD
def_render = "def render_diagnostics(self):"
new_def = """def render_diagnostics(self):
        # Prevent any auto-range drift by explicitly re-asserting bounds
        tab_idx = self.graph_tabs.currentIndex()
        if tab_idx == 2:
            if hasattr(self, '_csd_max_peak'):
                p = self._csd_max_peak
                self.csd_widget.setXRange(np.log10(200), np.log10(20000), padding=0)
                self.csd_widget.setYRange(p - 45, p + 5, padding=0)
            else:
                self.csd_widget.setXRange(np.log10(200), np.log10(20000), padding=0)
                self.csd_widget.setYRange(-60, 20, padding=0)"""
content = content.replace(def_render, new_def)

with open("analysis_ui.py", "w") as f:
    f.write(content)
