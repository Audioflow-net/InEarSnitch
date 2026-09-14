import re

with open("main.py", "r") as f:
    code = f.read()

old_logic = """    def run_measurement(self):
        from PyQt5.QtWidgets import QMessageBox
        
        if not self.current_iem_id:
            QMessageBox.warning(self, "No Profile Selected", "Please select or create a Musician Profile from the left sidebar before measuring.")
            return
        
        # UI Hardening: block concurrent sweep attempts"""

new_logic = """    def run_measurement(self):
        from PyQt5.QtWidgets import QMessageBox
        
        if not self.current_iem_id:
            QMessageBox.warning(self, "No Profile Selected", "Please select or create a Musician Profile from the left sidebar before measuring.")
            return
            
        # SAFETY HARDENING: Block playback over internal speakers
        out_device = self.out_combo.currentText().lower()
        if any(bad in out_device for bad in ["lautsprecher", "speaker", "internal", "built-in"]):
            QMessageBox.critical(self, "Hardware Warning", 
                                 "Playback over internal speakers is strictly blocked to prevent severe acoustic feedback loops and hardware damage.\\n\\n"
                                 "Please connect and select a dedicated audio interface for IEM measurement.")
            return
        
        # UI Hardening: block concurrent sweep attempts"""

code = code.replace(old_logic, new_logic)

with open("main.py", "w") as f:
    f.write(code)

print("Speaker block patched.")
