import sys
import re

with open('main.py', 'r') as f:
    content = f.read()

# 1. Replace the UI creation block
old_ui = """        rta_container = QWidget()
        from PyQt5.QtWidgets import QCheckBox
        rta_layout = QHBoxLayout(rta_container)
        rta_layout.setContentsMargins(0, 0, 0, 0)
        rta_layout.setSpacing(15)
        
        self.chk_rta_helper = QCheckBox("IEC Guide")
        self.chk_rta_helper.setChecked(True)
        
        # Gross und lesbar!
        chk_style = (
            "QCheckBox { color: #E0E0E0; font-size: 13px; font-weight: bold; spacing: 8px; }"
            "QCheckBox::indicator { width: 20px; height: 20px; border-radius: 4px; border: 2px solid #555; background: #222; }"
            "QCheckBox::indicator:hover { border: 2px solid #777; }"
            "QCheckBox::indicator:checked { background: #10b981; border: 2px solid #10b981; }"
        )
        self.chk_rta_helper.setStyleSheet(chk_style)
        self.chk_rta_helper.toggled.connect(self.on_rta_helper_toggled)
        
        self.btn_live_seal = QPushButton("R\\nT\\nA")
        self.btn_live_seal.setToolTip("Start Live Pink Noise RTA for Seal Check")
        self.btn_live_seal.setCheckable(True)
        self.btn_live_seal.setStyleSheet("QPushButton { background-color: #db2777; color: white; font-weight: bold; font-size: 13px; border-radius: 6px; border: none; } QPushButton:hover { background-color: #be185d; } QPushButton:checked { background-color: #fbcfe8; color: #831843; border: 2px solid #db2777; }")
        
        # Original size policy! 40px breit, füllt die Höhe.
        self.btn_live_seal.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        self.btn_live_seal.setMinimumHeight(60)
        self.btn_live_seal.setFixedWidth(40)
        self.btn_live_seal.clicked.connect(self.toggle_live_seal)
        
        # Stretch nach links, sodass die Knöpfe rechtsbündig anliegen!
        rta_layout.addStretch()
        rta_layout.addWidget(self.chk_rta_helper, alignment=Qt.AlignVCenter)
        rta_layout.addWidget(self.btn_live_seal)
        
        control_layout.addWidget(rta_container, 0, 4, 2, 1)"""

new_ui = """        rta_container = QWidget()
        rta_layout = QHBoxLayout(rta_container)
        rta_layout.setContentsMargins(0, 0, 0, 0)
        rta_layout.setSpacing(6)
        
        self.btn_rta_raw = QPushButton("R\\nT\\nA")
        self.btn_rta_raw.setToolTip("Start Raw Live RTA")
        self.btn_rta_raw.setCheckable(True)
        self.btn_rta_raw.setStyleSheet("QPushButton { background-color: #db2777; color: white; font-weight: bold; font-size: 13px; border-radius: 6px; border: none; } QPushButton:hover { background-color: #be185d; } QPushButton:checked { background-color: #fbcfe8; color: #831843; border: 2px solid #db2777; }")
        self.btn_rta_raw.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        self.btn_rta_raw.setMinimumHeight(60)
        self.btn_rta_raw.setFixedWidth(40)
        self.btn_rta_raw.clicked.connect(self.on_rta_button_clicked)
        
        self.btn_iec_guide = QPushButton("I\\nE\\nC")
        self.btn_iec_guide.setToolTip("Start Live RTA with 8k IEC Guide")
        self.btn_iec_guide.setCheckable(True)
        self.btn_iec_guide.setStyleSheet("QPushButton { background-color: #10b981; color: white; font-weight: bold; font-size: 13px; border-radius: 6px; border: none; } QPushButton:hover { background-color: #059669; } QPushButton:checked { background-color: #a7f3d0; color: #064e3b; border: 2px solid #10b981; }")
        self.btn_iec_guide.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        self.btn_iec_guide.setMinimumHeight(60)
        self.btn_iec_guide.setFixedWidth(40)
        self.btn_iec_guide.clicked.connect(self.on_rta_button_clicked)
        
        rta_layout.addStretch()
        rta_layout.addWidget(self.btn_rta_raw)
        rta_layout.addWidget(self.btn_iec_guide)
        
        control_layout.addWidget(rta_container, 0, 4, 2, 1)"""
        
content = content.replace(old_ui, new_ui)

# 2. Add the router method and update toggle_live_seal signature
old_toggle_sig = """    def toggle_live_seal(self, checked):"""
new_router = """    def on_rta_button_clicked(self):
        sender = self.sender()
        
        if sender == self.btn_rta_raw:
            if self.btn_rta_raw.isChecked():
                self.btn_iec_guide.setChecked(False)
        else:
            if self.btn_iec_guide.isChecked():
                self.btn_rta_raw.setChecked(False)
                
        is_active = self.btn_rta_raw.isChecked() or self.btn_iec_guide.isChecked()
        is_running = getattr(self, 'live_worker', None) and self.live_worker.isRunning()
        
        if is_active and not is_running:
            self.toggle_live_seal(True)
        elif not is_active and is_running:
            self.toggle_live_seal(False)
        elif is_active and is_running:
            self.on_rta_helper_toggled()
            
    def toggle_live_seal(self, checked):"""

content = content.replace(old_toggle_sig, new_router)

# 3. Update the old toggle_live_seal to not look at chk_rta_helper, but btn_iec_guide
content = content.replace("self.btn_live_seal.setChecked(False)", "self.btn_rta_raw.setChecked(False)\n            self.btn_iec_guide.setChecked(False)")
content = content.replace("hasattr(self, 'chk_rta_helper') and not self.chk_rta_helper.isChecked()", "not self.btn_iec_guide.isChecked()")
content = content.replace("hasattr(self, 'chk_rta_helper') and self.chk_rta_helper.isChecked()", "self.btn_iec_guide.isChecked()")

# Update on_rta_helper_toggled which is now our visual updater
old_helper_toggled = """    def on_rta_helper_toggled(self, checked):
        if not self.btn_live_seal.isChecked():
            return
        if checked:"""
new_helper_toggled = """    def on_rta_helper_toggled(self):
        if not getattr(self, 'live_worker', None) or not self.live_worker.isRunning():
            return
        if self.btn_iec_guide.isChecked():"""

content = content.replace(old_helper_toggled, new_helper_toggled)

with open('main.py', 'w') as f:
    f.write(content)
