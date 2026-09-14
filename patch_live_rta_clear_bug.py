import re

with open('main.py', 'r') as f:
    content = f.read()

new_code = """            self.btn_capture.setEnabled(False)
            
            # Setup plot line for RTA (recreate to avoid Pyqtgraph clear() issues)
            import pyqtgraph as pg
            if hasattr(self, 'live_rta_line') and self.live_rta_line is not None:
                try:
                    self.plot_widget.removeItem(self.live_rta_line)
                except Exception:
                    pass
            self.live_rta_line = self.plot_widget.plot(pen=pg.mkPen('#db2777', width=2), name="Live Seal")
            self.live_rta_line.show()
            
            self.live_worker = LiveSealWorker(self.selected_in_idx, self.selected_out_idx, cal_f, cal_m)"""

content = re.sub(r"            self\.btn_capture\.setEnabled\(False\)\s+# Setup plot line for RTA\s+if not hasattr.*?self\.live_worker = LiveSealWorker", new_code, content, flags=re.DOTALL)

with open('main.py', 'w') as f:
    f.write(content)
