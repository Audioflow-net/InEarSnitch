import re

with open('main.py', 'r') as f:
    content = f.read()

# First, remove any existing btn_live_seal just in case
content = re.sub(r'\n\s*self\.btn_live_seal.*?(?=self\.btn_capture)', '\n', content, flags=re.DOTALL)

btn_code = """
        self.btn_live_seal = QPushButton("R T A")
        self.btn_live_seal.setToolTip("Start Live Pink Noise RTA for Seal Check")
        self.btn_live_seal.setCheckable(True)
        self.btn_live_seal.setStyleSheet("QPushButton { background-color: #333; color: white; font-weight: bold; font-size: 13px; border-radius: 6px; border: 1px solid #555; } QPushButton:checked { background-color: #db2777; color: white; border: 1px solid #be185d; }")
        self.btn_live_seal.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.btn_live_seal.setFixedWidth(40)
        self.btn_live_seal.clicked.connect(self.toggle_live_seal)
        control_layout.addWidget(self.btn_live_seal, 0, 4, 2, 1)

        self.btn_capture"""

content = content.replace('        self.btn_capture', btn_code, 1)

with open('main.py', 'w') as f:
    f.write(content)
