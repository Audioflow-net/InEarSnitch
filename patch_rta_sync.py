import sys

with open('main.py', 'r') as f:
    content = f.read()
    
# Find toggle_live_seal top
old_toggle = """    def toggle_live_seal(self, checked):
        from PyQt5.QtWidgets import QMessageBox
        import pyqtgraph as pg"""
        
new_toggle = """    def toggle_live_seal(self, checked):
        from PyQt5.QtWidgets import QMessageBox
        import pyqtgraph as pg
        
        # Sync the buttons visually
        self.btn_live_seal.blockSignals(True)
        self.btn_live_seal.setChecked(checked)
        self.btn_live_seal.blockSignals(False)
        if hasattr(self, 'page_ana'):
            self.page_ana.btn_rta.blockSignals(True)
            self.page_ana.btn_rta.setChecked(checked)
            self.page_ana.btn_rta.blockSignals(False)
"""
content = content.replace(old_toggle, new_toggle)

with open('main.py', 'w') as f:
    f.write(content)
