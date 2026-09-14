import re

with open("main.py", "r") as f:
    code = f.read()

old_btn = """        self.btn_auto_cal = QPushButton("Start Auto-Calibration")
        self.btn_auto_cal.setStyleSheet("background: #00FF99; color: black; padding: 8px; font-weight: bold; border-radius: 4px;")
        self.btn_auto_cal.clicked.connect(self._run_level_calibration)
        cal_layout.addWidget(self.btn_auto_cal)"""

new_btn = """        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(0, 10, 0, 0)
        self.btn_auto_cal = QPushButton("Start Auto-Calibration")
        self.btn_auto_cal.setCursor(Qt.PointingHandCursor)
        self.btn_auto_cal.setStyleSheet("QPushButton { background-color: #222; color: #0ea5e9; border: 1px solid #0ea5e9; padding: 6px 16px; font-weight: bold; border-radius: 4px; } QPushButton:hover { background-color: #0ea5e9; color: white; }")
        self.btn_auto_cal.clicked.connect(self._run_level_calibration)
        btn_layout.addWidget(self.btn_auto_cal)
        btn_layout.addStretch()
        cal_layout.addLayout(btn_layout)"""

code = code.replace(old_btn, new_btn)

with open("main.py", "w") as f:
    f.write(code)
