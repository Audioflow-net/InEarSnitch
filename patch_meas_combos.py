import re

with open("main.py", "r") as f:
    code = f.read()

insert_point = r'(        control_layout\.addWidget\(self\.btn_save_db, 1, 8\)\n\n)'

new_code = r"""\1
        # --- Row 1: Target and History ---
        from PyQt5.QtWidgets import QComboBox, QSizePolicy
        
        control_layout.addWidget(QLabel("Target:", styleSheet="color: #AAA; font-weight: bold;"), 1, 0)
        self.cb_meas_target = QComboBox()
        self.cb_meas_target.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.cb_meas_target.setStyleSheet("QComboBox { background: #333; color: white; border: 1px solid #555; padding: 6px; border-radius: 4px; }")
        self.cb_meas_target.currentIndexChanged.connect(self.on_meas_target_changed)
        control_layout.addWidget(self.cb_meas_target, 1, 1, 1, 2)
        
        control_layout.addWidget(QLabel("History:", styleSheet="color: #AAA; font-weight: bold;"), 1, 3)
        self.cb_meas_history = QComboBox()
        self.cb_meas_history.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.cb_meas_history.setStyleSheet("QComboBox { background: #333; color: white; border: 1px solid #555; padding: 6px; border-radius: 4px; }")
        self.cb_meas_history.currentIndexChanged.connect(self.on_meas_history_changed)
        control_layout.addWidget(self.cb_meas_history, 1, 4, 1, 3)
"""

code = re.sub(insert_point, new_code, code)

with open("main.py", "w") as f:
    f.write(code)

print("Measurement comboboxes patched.")
