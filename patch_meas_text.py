import sys

with open('main.py', 'r') as f:
    content = f.read()

# Start measurement
old_start = """        self.btn_capture.setEnabled(False)
        self.btn_capture.setText("MEASURING...")"""

new_start = """        self.btn_capture.setEnabled(False)
        self.btn_capture.setText("MEASURING...")
        if hasattr(self, 'page_ana') and hasattr(self.page_ana, 'btn_run_sweep'):
            self.page_ana.btn_run_sweep.setEnabled(False)
            self.page_ana.btn_run_sweep.setText("MEASURING...")"""

content = content.replace(old_start, new_start)

# End measurement
old_end = """        self.is_measuring = False   # UI Hardening: release lock
        self.meas_overlay.stop()
        self.btn_capture.setEnabled(True)
        self.btn_capture.setText("Run Sweep")"""

new_end = """        self.is_measuring = False   # UI Hardening: release lock
        if hasattr(self, 'meas_overlay'): self.meas_overlay.stop()
        self.btn_capture.setEnabled(True)
        self.btn_capture.setText("Run Sweep")
        if hasattr(self, 'page_ana') and hasattr(self.page_ana, 'btn_run_sweep'):
            self.page_ana.btn_run_sweep.setEnabled(True)
            self.page_ana.btn_run_sweep.setText("▶ MEASURE")"""

# Wait, `self.btn_capture.setText("Run Sweep")` might not be in main.py. Let's check what it is.
