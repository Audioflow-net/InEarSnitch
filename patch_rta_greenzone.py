import re
import sys

with open('main.py', 'r') as f:
    content = f.read()

# Add the green zone when turning on
old_on = """            self.live_rta_line = target_plot.plot(pen=pg.mkPen(color, width=2), name="Live Seal")
            self.live_rta_line.show()"""

new_on = """            self.live_rta_line = target_plot.plot(pen=pg.mkPen(color, width=2), name="Live Seal")
            self.live_rta_line.show()
            
            import numpy as np
            from PyQt5.QtCore import Qt
            if not hasattr(self, 'rta_target_region') or self.rta_target_region is None:
                self.rta_target_region = pg.LinearRegionItem(
                    values=[np.log10(7000), np.log10(8600)], 
                    movable=False, 
                    brush=pg.mkBrush(16, 185, 129, 35),
                    pen=pg.mkPen('#10b981', width=1, style=Qt.DashLine)
                )
                self.rta_target_region.setZValue(-10)
                target_plot.addItem(self.rta_target_region)"""

content = content.replace(old_on, new_on)

# Remove the green zone when turning off
old_off = """            if hasattr(self, 'live_rta_line') and self.live_rta_line is not None:
                try:
                    target = self.page_ana.plot_widget if hasattr(self, 'page_ana') else self.plot_widget
                    target.removeItem(self.live_rta_line)
                except Exception:
                    pass"""

new_off = """            if hasattr(self, 'live_rta_line') and self.live_rta_line is not None:
                try:
                    target = self.page_ana.plot_widget if hasattr(self, 'page_ana') else self.plot_widget
                    target.removeItem(self.live_rta_line)
                except Exception:
                    pass
            if hasattr(self, 'rta_target_region') and self.rta_target_region is not None:
                try:
                    target = self.page_ana.plot_widget if hasattr(self, 'page_ana') else self.plot_widget
                    target.removeItem(self.rta_target_region)
                except Exception:
                    pass
                self.rta_target_region = None"""

content = content.replace(old_off, new_off)

with open('main.py', 'w') as f:
    f.write(content)
