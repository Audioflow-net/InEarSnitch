import sys

with open('main.py', 'r') as f:
    content = f.read()

old_block = """        rta_container = QWidget()
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
        
        from PyQt5.QtWidgets import QCheckBox
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
        rta_layout.addWidget(self.chk_rta_helper, alignment=Qt.AlignHCenter)
        control_layout.addWidget(rta_container, 0, 4, 2, 1)"""


new_block = """        rta_container = QWidget()
        from PyQt5.QtWidgets import QHBoxLayout, QCheckBox
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
        from PyQt5.QtCore import Qt
        rta_layout.addStretch()
        rta_layout.addWidget(self.chk_rta_helper, alignment=Qt.AlignVCenter)
        rta_layout.addWidget(self.btn_live_seal)
        
        control_layout.addWidget(rta_container, 0, 4, 2, 1)"""

content = content.replace(old_block, new_block)

with open('main.py', 'w') as f:
    f.write(content)
