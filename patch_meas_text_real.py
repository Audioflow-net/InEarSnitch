import sys

with open('main.py', 'r') as f:
    content = f.read()

# Start
old_start = """        self.meas_overlay.start()
        self.btn_capture.setEnabled(False)"""

new_start = """        self.meas_overlay.start()
        self.btn_capture.setEnabled(False)
        if hasattr(self, 'page_ana') and hasattr(self.page_ana, 'btn_run_sweep'):
            self.page_ana.btn_run_sweep.setEnabled(False)
            self.page_ana.btn_run_sweep.setText("MEASURING...")"""
content = content.replace(old_start, new_start)

# End
old_end = """        self.is_measuring = False   # UI Hardening: release lock
        self.meas_overlay.stop()
        self.btn_capture.setEnabled(True)"""

new_end = """        self.is_measuring = False   # UI Hardening: release lock
        self.meas_overlay.stop()
        self.btn_capture.setEnabled(True)
        if hasattr(self, 'page_ana') and hasattr(self.page_ana, 'btn_run_sweep'):
            self.page_ana.btn_run_sweep.setEnabled(True)
            self.page_ana.btn_run_sweep.setText("▶ MEASURE")"""
content = content.replace(old_end, new_end)

with open('main.py', 'w') as f:
    f.write(content)
