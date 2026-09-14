import sys

with open('main.py', 'r') as f:
    content = f.read()

# 1. Un-hide the bottom bar dropdowns
content = content.replace("self.cb_meas_target.hide()", "")
content = content.replace("self.cb_meas_history.hide()", "")

# 2. Add the sync logic right after we add bottom_container
sync_logic = """        self.page_ana.layout.addLayout(bottom_container)
        
        # Sync bottom bar dropdowns with the hidden Analysis dropdowns
        self.cb_meas_target.currentIndexChanged.connect(self.page_ana.cb_ana_target.setCurrentIndex)
        self.cb_meas_history.currentIndexChanged.connect(self.page_ana.cb_ana_history.setCurrentIndex)"""
content = content.replace("        self.page_ana.layout.addLayout(bottom_container)", sync_logic)

with open('main.py', 'w') as f:
    f.write(content)

with open('analysis_ui.py', 'r') as f:
    content = f.read()
    
# 3. Hide the redundant dropdowns in the top toolbar
content = content.replace("self.cb_ana_target = QComboBox()", "self.cb_ana_target = QComboBox()\n        self.cb_ana_target.hide()")
content = content.replace("self.cb_ana_history = QComboBox()", "self.cb_ana_history = QComboBox()\n        self.cb_ana_history.hide()")

with open('analysis_ui.py', 'w') as f:
    f.write(content)
