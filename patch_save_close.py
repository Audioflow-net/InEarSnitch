import sys

with open('main.py', 'r') as f:
    content = f.read()

old_save = """    def save_settings(self):
        from PyQt5.QtCore import QSettings
        self.selected_in_idx = self.in_combo.currentData()
        self.selected_out_idx = self.out_combo.currentData()

        s = QSettings("InEar Snitch", "InEarSnitchApp")
        s.setValue("audio/input_device_name",  self.in_combo.currentText())
        s.setValue("audio/output_device_name", self.out_combo.currentText())
        s.setValue("audio/auto_normalize", self.chk_normalize.isChecked())
        s.setValue("audio/coupler_cal_path",   self.mic_cal_combo.currentData() or "")
        s.setValue("audio/spl_offset_db",      getattr(self, "spl_offset_db", 0.0))
        s.sync()

        # Inline feedback – no popup, panel stays open
        self.settings_save_lbl.setText("Saved")
        QTimer.singleShot(2500, lambda: self.settings_save_lbl.setText(""))"""

new_save = """    def save_settings(self):
        from PyQt5.QtCore import QSettings
        self.selected_in_idx = self.in_combo.currentData()
        self.selected_out_idx = self.out_combo.currentData()

        s = QSettings("InEar Snitch", "InEarSnitchApp")
        s.setValue("audio/input_device_name",  self.in_combo.currentText())
        s.setValue("audio/output_device_name", self.out_combo.currentText())
        s.setValue("audio/auto_normalize", self.chk_normalize.isChecked())
        s.setValue("audio/coupler_cal_path",   self.mic_cal_combo.currentData() or "")
        s.setValue("audio/spl_offset_db",      getattr(self, "spl_offset_db", 0.0))
        s.sync()

        # Close the slide-out panel automatically upon saving
        self.settings_panel.setVisible(False)
        if hasattr(self, 'settings_dimmer'):
            self.settings_dimmer.setVisible(False)
            
        self.settings_save_lbl.setText("Saved")
        QTimer.singleShot(2500, lambda: self.settings_save_lbl.setText(""))"""

content = content.replace(old_save, new_save)

with open('main.py', 'w') as f:
    f.write(content)
