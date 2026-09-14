import sys

with open('main.py', 'r') as f:
    content = f.read()

old_err = """    def on_measurement_error(self, err_msg):
        self.is_measuring = False
        self.btn_capture.setEnabled(True)
        self.meas_overlay.stop()
        self.sub_lbl.setText(f"Error: {err_msg}")
        self.sub_lbl.setStyleSheet("color: #FF3333; font-size: 13px; font-weight: bold;")"""

new_err = """    def on_measurement_error(self, err_msg):
        from PyQt5.QtWidgets import QMessageBox
        self.is_measuring = False
        self.btn_capture.setEnabled(True)
        self.meas_overlay.stop()
        self.sub_lbl.setText(f"Error: {err_msg}")
        self.sub_lbl.setStyleSheet("color: #FF3333; font-size: 13px; font-weight: bold;")
        QMessageBox.critical(self, "Measurement Error", f"Audio Engine failed with error:\\n\\n{err_msg}")"""

content = content.replace(old_err, new_err)

with open('main.py', 'w') as f:
    f.write(content)
