import re

with open('main.py', 'r') as f:
    content = f.read()

btn_code = """
        self.btn_live_seal = QPushButton("🎧 LIVE SEAL")
        self.btn_live_seal.setToolTip("Start Live Pink Noise RTA for Seal Check")
        self.btn_live_seal.setCheckable(True)
        self.btn_live_seal.setStyleSheet("QPushButton { background-color: #333; color: white; font-weight: bold; font-size: 13px; border-radius: 6px; border: 1px solid #555; } QPushButton:checked { background-color: #db2777; color: white; border: 1px solid #be185d; }")
        self.btn_live_seal.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.btn_live_seal.clicked.connect(self.toggle_live_seal)
        control_layout.addWidget(self.btn_live_seal, 0, 4, 1, 1)

        self.btn_capture = QPushButton("RUN")"""

content = content.replace('        self.btn_capture = QPushButton("RUN")', btn_code)

with open('main.py', 'w') as f:
    f.write(content)
