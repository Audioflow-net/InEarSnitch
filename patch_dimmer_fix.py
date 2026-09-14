import re

with open("main.py", "r") as f:
    code = f.read()

old_code = """        # SETTINGS PANEL (OVERLAY)
        # =========================================================
        page_set = QFrame(central)"""

new_code = """        # SETTINGS PANEL (OVERLAY)
        # =========================================================
        from PyQt5.QtWidgets import QPushButton
        self.settings_dimmer = QPushButton(central)
        self.settings_dimmer.setStyleSheet("background: rgba(0, 0, 0, 0.6); border: none;")
        self.settings_dimmer.hide()
        self.settings_dimmer.clicked.connect(lambda: self.settings_panel.setVisible(False) or self.settings_dimmer.setVisible(False))
        
        page_set = QFrame(central)"""

code = code.replace(old_code, new_code)

with open("main.py", "w") as f:
    f.write(code)

print("Dimmer properly added.")
