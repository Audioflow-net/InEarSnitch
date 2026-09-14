import re

with open("main.py", "r") as f:
    code = f.read()

# Match from "control_layout = QGridLayout(control_panel)" down to the end of the Target and History addition.
pattern = r'(        control_layout = QGridLayout\(control_panel\)[\s\S]*?self\.cb_meas_history\.currentIndexChanged\.connect\(self\.on_meas_history_changed\)\n        control_layout\.addWidget\(self\.cb_meas_history, 1, 4, 1, 3\))'

new_code = r"""        control_layout = QGridLayout(control_panel)
        control_layout.setContentsMargins(15, 15, 15, 15)
        control_layout.setHorizontalSpacing(15)
        control_layout.setVerticalSpacing(15)

        # --- Row 0 ---
        control_layout.addWidget(QLabel("Channel:", styleSheet="color: #AAA; font-weight: bold;"), 0, 0)
        self.cb_chan = QComboBox()
        self.cb_chan.addItems(["Left", "Right"])
        self.cb_chan.setStyleSheet("QComboBox { background: #333; color: white; border: 1px solid #555; padding: 6px; border-radius: 4px; font-weight: bold; min-width: 70px; } QComboBox QAbstractItemView { background-color: #222; color: white; selection-background-color: #008888; }")
        self.cb_chan.currentTextChanged.connect(self.update_watermark)
        control_layout.addWidget(self.cb_chan, 0, 1)
        
        control_layout.addWidget(QLabel("Sweeps:", styleSheet="color: #AAA; font-weight: bold;"), 0, 2)
        self.cb_sweeps = QComboBox()
        self.cb_sweeps.addItems(["1x", "3x", "5x"])
        self.cb_sweeps.setStyleSheet("QComboBox { background: #333; color: white; border: 1px solid #555; padding: 6px; border-radius: 4px; font-weight: bold; min-width: 70px; } QComboBox QAbstractItemView { background-color: #222; color: white; selection-background-color: #008888; }")
        control_layout.addWidget(self.cb_sweeps, 0, 3)
        
        # --- Row 1 ---
        from PyQt5.QtWidgets import QSizePolicy
        control_layout.addWidget(QLabel("Target:", styleSheet="color: #AAA; font-weight: bold;"), 1, 0)
        self.cb_meas_target = QComboBox()
        self.cb_meas_target.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.cb_meas_target.setMinimumWidth(180)
        self.cb_meas_target.setStyleSheet("QComboBox { background: #333; color: white; border: 1px solid #555; padding: 6px; border-radius: 4px; }")
        self.cb_meas_target.currentIndexChanged.connect(self.on_meas_target_changed)
        control_layout.addWidget(self.cb_meas_target, 1, 1)

        control_layout.addWidget(QLabel("History:", styleSheet="color: #AAA; font-weight: bold;"), 1, 2)
        self.cb_meas_history = QComboBox()
        self.cb_meas_history.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.cb_meas_history.setMinimumWidth(220)
        self.cb_meas_history.setStyleSheet("QComboBox { background: #333; color: white; border: 1px solid #555; padding: 6px; border-radius: 4px; }")
        self.cb_meas_history.currentIndexChanged.connect(self.on_meas_history_changed)
        control_layout.addWidget(self.cb_meas_history, 1, 3)

        # Spacer column (Column 4) allows the panel to stretch
        control_layout.setColumnStretch(4, 1)

        # --- Buttons ---
        self.btn_capture = QPushButton("RUN")
        self.btn_capture.setToolTip("Start measurement capture")
        self.btn_capture.setStyleSheet("QPushButton { background-color: #10b981; color: black; font-weight: bold; font-size: 14px; border-radius: 6px; } QPushButton:disabled { background-color: #555; color: #888; }")
        self.btn_capture.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.btn_capture.clicked.connect(self.run_measurement)
        control_layout.addWidget(self.btn_capture, 0, 5, 1, 2)

        self.btn_trace = QPushButton("Clear")
        self.btn_trace.setToolTip("Clear measurement trace")
        self.btn_trace.setMinimumWidth(80)
        self.btn_trace.setStyleSheet("QPushButton { background-color: #ef4444; color: white; font-weight: bold; padding: 6px; border-radius: 4px; border: none; } QPushButton:disabled { background-color: #7f1d1d; color: #fca5a5; } QPushButton:hover { background-color: #dc2626; }")
        self.btn_trace.clicked.connect(self.clear_trace)
        control_layout.addWidget(self.btn_trace, 1, 5)
        
        self.btn_save_db = QPushButton("Save")
        self.btn_save_db.setToolTip("Save measurement to database")
        self.btn_save_db.setMinimumWidth(80)
        self.btn_save_db.setStyleSheet("QPushButton { background-color: #0ea5e9; color: white; font-weight: bold; padding: 6px; border-radius: 4px; border: none; } QPushButton:disabled { background-color: #0369a1; color: #7dd3fc; } QPushButton:hover { background-color: #0284c7; }")
        self.btn_save_db.clicked.connect(self.save_trace_to_db)
        control_layout.addWidget(self.btn_save_db, 1, 6)"""

# We need to make sure the regex matches properly.
code = re.sub(pattern, new_code, code)

with open("main.py", "w") as f:
    f.write(code)

print("Layout replaced.")
