import re

with open("main.py", "r") as f:
    code = f.read()

# 1. Connect signals in setup_ui
code = code.replace("        self.load_targets()\n\n        self.btn_capture.setEnabled(False)", 
"""        self.page_ana.cb_ana_target.currentIndexChanged.connect(self.on_ana_target_changed)
        self.page_ana.cb_ana_history.currentIndexChanged.connect(self.on_ana_history_changed)
        self.load_targets()

        self.btn_capture.setEnabled(False)""")

# 2. Fix cb_target reference in save_as_target
code = code.replace("idx = self.cb_target.findText(", "idx = self.cb_meas_target.findText(")
code = code.replace("self.cb_target.setCurrentIndex(idx)", "self.cb_meas_target.setCurrentIndex(idx)")

with open("main.py", "w") as f:
    f.write(code)

print("Connections and save fixed.")
