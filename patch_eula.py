import sys

with open('main.py', 'r') as f:
    content = f.read()

# 1. Add QTimer call to end of __init__
init_end = """        QShortcut(QKeySequence("Ctrl+3"), self).activated.connect(lambda: self.switch_workspace_tab(3))"""
init_end_new = """        QShortcut(QKeySequence("Ctrl+3"), self).activated.connect(lambda: self.switch_workspace_tab(3))
        
        # Delayed EULA check
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(500, self.check_eula)"""

if init_end in content:
    content = content.replace(init_end, init_end_new)
else:
    print("Could not find init_end")

# 2. Add check_eula method
check_eula_method = """    def check_eula(self):
        from PyQt5.QtCore import QSettings
        from PyQt5.QtWidgets import QMessageBox
        import sys
        
        s = QSettings("InEar Snitch", "InEarSnitchApp")
        if not s.value("eula_accepted", False, type=bool):
            msg = QMessageBox(self)
            msg.setWindowTitle("Health & Safety Warning")
            msg.setIcon(QMessageBox.Warning)
            msg.setText("<b>WARNING: High-Level Sine Sweeps</b>")
            msg.setInformativeText(
                "This software generates loud, high-frequency audio sweeps which can cause <b>permanent hearing damage</b> "
                "if listened to directly, or <b>hardware damage</b> (blown drivers) if the gain is incorrectly staged.<br><br>"
                "• NEVER wear the In-Ear Monitors (IEMs) while running a measurement.<br>"
                "• ALWAYS double-check your audio interface output volume before clicking RUN.<br><br>"
                "By clicking 'Accept', you confirm you understand these risks and release the developers of InEar Snitch from any liability regarding hearing loss or equipment damage."
            )
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Abort)
            msg.button(QMessageBox.Ok).setText("Accept")
            msg.button(QMessageBox.Abort).setText("Decline")
            
            ret = msg.exec_()
            if ret == QMessageBox.Ok:
                s.setValue("eula_accepted", True)
                s.sync()
            else:
                sys.exit(0)

    def setup_ui(self):"""

content = content.replace("    def setup_ui(self):", check_eula_method)

with open('main.py', 'w') as f:
    f.write(content)

