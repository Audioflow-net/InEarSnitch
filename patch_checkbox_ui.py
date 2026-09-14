import sys

with open('main.py', 'r') as f:
    content = f.read()

old_block = """        from PyQt5.QtWidgets import QCheckBox; self.chk_rta_helper = QCheckBox("8k Helper")
        self.chk_rta_helper.setChecked(True)
        self.chk_rta_helper.setStyleSheet("QCheckBox { color: #888; font-size: 10px; font-weight: bold; } QCheckBox::indicator { width: 12px; height: 12px; }")
        self.chk_rta_helper.toggled.connect(self.on_rta_helper_toggled)
        
        rta_layout.addWidget(self.btn_live_seal)
        rta_layout.addWidget(self.chk_rta_helper)"""

new_block = """        from PyQt5.QtWidgets import QCheckBox; from PyQt5.QtCore import Qt
        self.chk_rta_helper = QCheckBox("IEC Guide")
        self.chk_rta_helper.setChecked(True)
        
        # Nice custom dark mode checkbox styling
        chk_style = (
            "QCheckBox { color: #A0A0A0; font-size: 10px; font-weight: bold; spacing: 4px; }"
            "QCheckBox::indicator { width: 12px; height: 12px; border-radius: 3px; border: 1px solid #555; background: #222; }"
            "QCheckBox::indicator:hover { border: 1px solid #777; }"
            "QCheckBox::indicator:checked { background: #10b981; border: 1px solid #10b981; }"
        )
        self.chk_rta_helper.setStyleSheet(chk_style)
        self.chk_rta_helper.toggled.connect(self.on_rta_helper_toggled)
        
        rta_layout.addWidget(self.btn_live_seal)
        rta_layout.addWidget(self.chk_rta_helper, alignment=Qt.AlignHCenter)"""

content = content.replace(old_block, new_block)

with open('main.py', 'w') as f:
    f.write(content)
