import re

with open('main.py', 'r') as f:
    content = f.read()

old_rta_btn = """        self.btn_live_seal = QPushButton("R\\nT\\nA")
        self.btn_live_seal.setToolTip("Start Live Pink Noise RTA for Seal Check")
        self.btn_live_seal.setCheckable(True)
        self.btn_live_seal.setStyleSheet("QPushButton { background-color: #db2777; color: white; font-weight: bold; font-size: 13px; border-radius: 6px; border: none; } QPushButton:hover { background-color: #be185d; } QPushButton:checked { background-color: #fbcfe8; color: #831843; border: 2px solid #db2777; }")
        self.btn_live_seal.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        self.btn_live_seal.setMinimumHeight(60)
        self.btn_live_seal.setFixedWidth(40)
        self.btn_live_seal.clicked.connect(self.toggle_live_seal)
        control_layout.addWidget(self.btn_live_seal, 0, 4, 2, 1)"""

new_rta_btn = """        rta_container = QWidget()
        rta_layout = QVBoxLayout(rta_container)
        rta_layout.setContentsMargins(0, 0, 0, 0)
        rta_layout.setSpacing(2)
        
        self.btn_live_seal = QPushButton("RTA")
        self.btn_live_seal.setToolTip("Start Live Pink Noise RTA for Seal Check")
        self.btn_live_seal.setCheckable(True)
        self.btn_live_seal.setStyleSheet("QPushButton { background-color: #db2777; color: white; font-weight: bold; font-size: 13px; border-radius: 6px; border: none; } QPushButton:hover { background-color: #be185d; } QPushButton:checked { background-color: #fbcfe8; color: #831843; border: 2px solid #db2777; }")
        self.btn_live_seal.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.btn_live_seal.setMinimumHeight(40)
        self.btn_live_seal.clicked.connect(self.toggle_live_seal)
        
        self.chk_rta_helper = QCheckBox("8k Helper")
        self.chk_rta_helper.setChecked(True)
        self.chk_rta_helper.setStyleSheet("QCheckBox { color: #888; font-size: 10px; font-weight: bold; } QCheckBox::indicator { width: 12px; height: 12px; }")
        self.chk_rta_helper.toggled.connect(self.on_rta_helper_toggled)
        
        rta_layout.addWidget(self.btn_live_seal)
        rta_layout.addWidget(self.chk_rta_helper)
        control_layout.addWidget(rta_container, 0, 4, 2, 1)"""

content = content.replace(old_rta_btn, new_rta_btn)

# Add on_rta_helper_toggled method
method = """    def on_rta_helper_toggled(self, checked):
        if not self.btn_live_seal.isChecked():
            return
        if checked:
            if hasattr(self, 'rta_target_region') and self.rta_target_region is not None:
                self.rta_target_region.show()
            if hasattr(self, 'rta_peak_line') and self.rta_peak_line is not None:
                self.rta_peak_line.show()
            if hasattr(self, 'rta_big_lbl') and self.rta_big_lbl is not None:
                self.rta_big_lbl.show()
        else:
            if hasattr(self, 'rta_target_region') and self.rta_target_region is not None:
                self.rta_target_region.hide()
            if hasattr(self, 'rta_peak_line') and self.rta_peak_line is not None:
                self.rta_peak_line.hide()
            if hasattr(self, 'rta_big_lbl') and self.rta_big_lbl is not None:
                self.rta_big_lbl.hide()
"""
content = content.replace("    def toggle_live_seal(self, checked):", method + "\n    def toggle_live_seal(self, checked):")

with open('main.py', 'w') as f:
    f.write(content)
