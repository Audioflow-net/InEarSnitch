import sys

with open('main.py', 'r') as f:
    content = f.read()

# 1. Override getters
old_get_chan = """    def get_current_channel(self):
        if hasattr(self, 'btn_grp_chan'):
            return self.btn_grp_chan.checkedButton().text()
        return "Left"
        
    def get_current_sweeps(self):
        if hasattr(self, 'btn_grp_sweeps'):
            return self.btn_grp_sweeps.checkedButton().text()
        return "1x\""""

new_get_chan = """    def get_current_channel(self):
        if hasattr(self, 'page_ana') and hasattr(self.page_ana, 'btn_meas_l'):
            if self.page_ana.btn_meas_l.isChecked(): return "Left"
            if self.page_ana.btn_meas_r.isChecked(): return "Right"
        if hasattr(self, 'btn_grp_chan'):
            return self.btn_grp_chan.checkedButton().text()
        return "Left"
        
    def get_current_sweeps(self):
        if hasattr(self, 'page_ana') and hasattr(self.page_ana, 'cb_avg'):
            return self.page_ana.cb_avg.currentText().replace(" Avg", "")
        if hasattr(self, 'btn_grp_sweeps'):
            return self.btn_grp_sweeps.checkedButton().text()
        return "1x\""""

content = content.replace(old_get_chan, new_get_chan)

# 2. Hide Measurement Tab and rename Analysis Tab
old_tab_setup = """        # Profile Tabs
        self.btn_nav_prof = QPushButton(" Profiles")
        self.btn_nav_meas = QPushButton(" Measurement")
        self.btn_nav_ana = QPushButton(" Analysis")"""

new_tab_setup = """        # Profile Tabs
        self.btn_nav_prof = QPushButton(" Profiles")
        self.btn_nav_meas = QPushButton(" Measurement")
        self.btn_nav_meas.hide()
        self.btn_nav_ana = QPushButton(" Workspace")"""

content = content.replace(old_tab_setup, new_tab_setup)

# 3. Connect signals from page_ana
old_setup_ana = """        self.page_ana = AnalysisWidget()
        self.page_ana.request_measurement.connect(self.run_measurement)
        self.workspace_stacked.addWidget(self.page_ana)"""

new_setup_ana = """        self.page_ana = AnalysisWidget()
        self.page_ana.request_measurement.connect(self.run_measurement)
        self.page_ana.request_rta.connect(self.toggle_live_seal)
        self.page_ana.request_save.connect(self.save_measurement_to_db)
        self.workspace_stacked.addWidget(self.page_ana)"""
        
content = content.replace(old_setup_ana, new_setup_ana)

# 4. Make sure on_measurement_finished resets the RTA button just in case
old_rta = """        if checked:
            if self.selected_in_idx is None or self.selected_out_idx is None:
                QMessageBox.critical(self, "Hardware Not Configured", "Audio Interface not configured!")
                self.btn_live_seal.setChecked(False)"""
new_rta = """        if checked:
            if self.selected_in_idx is None or self.selected_out_idx is None:
                QMessageBox.critical(self, "Hardware Not Configured", "Audio Interface not configured!")
                self.btn_live_seal.setChecked(False)
                if hasattr(self, 'page_ana'):
                    self.page_ana.btn_rta.blockSignals(True)
                    self.page_ana.btn_rta.setChecked(False)
                    self.page_ana.btn_rta.blockSignals(False)"""
content = content.replace(old_rta, new_rta)

with open('main.py', 'w') as f:
    f.write(content)
