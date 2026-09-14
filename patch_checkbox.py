import re

with open("main.py", "r") as f:
    code = f.read()

# 1. Add Checkbox to routing tab
old_routing = """        btn_refresh_dev.clicked.connect(self.populate_devices)
        routing_layout.addWidget(btn_refresh_dev)
        routing_layout.addStretch()"""
new_routing = """        btn_refresh_dev.clicked.connect(self.populate_devices)
        routing_layout.addWidget(btn_refresh_dev)
        
        routing_layout.addSpacing(10)
        from PyQt5.QtWidgets import QCheckBox
        self.chk_normalize = QCheckBox("Auto-Normalize to 80 dB (Align to Target)")
        self.chk_normalize.setStyleSheet("color: white; font-size: 13px;")
        self.chk_normalize.setChecked(True)
        routing_layout.addWidget(self.chk_normalize)
        
        routing_layout.addStretch()"""
code = code.replace(old_routing, new_routing)

# 2. Save Settings
old_save = """        s.setValue("audio/output_device_name", self.out_combo.currentText())
        s.setValue("audio/coupler_cal_path",   self.mic_cal_combo.currentData() or "")"""
new_save = """        s.setValue("audio/output_device_name", self.out_combo.currentText())
        s.setValue("audio/auto_normalize", self.chk_normalize.isChecked())
        s.setValue("audio/coupler_cal_path",   self.mic_cal_combo.currentData() or "")"""
code = code.replace(old_save, new_save)

# 3. Load Settings
old_load = """        saved_out = s.value("audio/output_device_name", "")
        saved_cal = s.value("audio/coupler_cal_path",   "")"""
new_load = """        saved_out = s.value("audio/output_device_name", "")
        saved_norm = s.value("audio/auto_normalize", type=bool)
        if saved_norm is None: saved_norm = True # Default True
        self.chk_normalize.setChecked(saved_norm)
        saved_cal = s.value("audio/coupler_cal_path",   "")"""
code = code.replace(old_load, new_load)

# 4. Use it in on_measurement_finished
old_norm = """        # 2. Smart Post-Normalization
        if np.isfinite(raw_val_1k):
            mag = mag + (80.0 - raw_val_1k)"""
new_norm = """        # 2. Smart Post-Normalization
        if self.chk_normalize.isChecked() and np.isfinite(raw_val_1k):
            mag = mag + (80.0 - raw_val_1k)"""
code = code.replace(old_norm, new_norm)

with open("main.py", "w") as f:
    f.write(code)

print("Checkbox patched.")
