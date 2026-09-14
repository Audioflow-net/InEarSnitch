import re

with open('main.py', 'r') as f:
    content = f.read()

# Replace the button creation and grid placement
old_btn = r'        self\.btn_live_seal = QPushButton\("🎧 LIVE SEAL"\).*?control_layout\.addWidget\(self\.btn_live_seal, 0, 4, 1, 1\)'

new_btn = """        self.btn_live_seal = QPushButton("L\\nI\\nV\\nE")
        self.btn_live_seal.setToolTip("Start Live Pink Noise RTA for Seal Check")
        self.btn_live_seal.setCheckable(True)
        self.btn_live_seal.setStyleSheet("QPushButton { background-color: #333; color: white; font-weight: bold; font-size: 13px; border-radius: 6px; border: 1px solid #555; padding-top: 10px; padding-bottom: 10px; } QPushButton:checked { background-color: #db2777; color: white; border: 1px solid #be185d; }")
        self.btn_live_seal.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.btn_live_seal.setFixedWidth(40)
        self.btn_live_seal.clicked.connect(self.toggle_live_seal)
        control_layout.addWidget(self.btn_live_seal, 0, 4, 2, 1)"""

content = re.sub(old_btn, new_btn, content, flags=re.DOTALL)

with open('main.py', 'w') as f:
    f.write(content)
