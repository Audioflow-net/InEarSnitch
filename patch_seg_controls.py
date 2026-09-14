import re

with open("main.py", "r") as f:
    code = f.read()

# Replace usages FIRST:
code = code.replace("self.cb_chan.currentText()", "self.get_current_channel()")
code = code.replace("self.cb_chan.currentIndex() == 0", 'self.get_current_channel() == "Left"')
code = code.replace("self.cb_sweeps.currentText()", "self.get_current_sweeps()")

# Add helper methods near the top of MainWindow
code = code.replace("def update_watermark(self):", """def get_current_channel(self):
        if hasattr(self, 'btn_grp_chan'):
            return self.btn_grp_chan.checkedButton().text()
        return "Left"
        
    def get_current_sweeps(self):
        if hasattr(self, 'btn_grp_sweeps'):
            return self.btn_grp_sweeps.checkedButton().text()
        return "1x"

    def update_watermark(self):""")

# Rewrite the control_layout
pattern = r'(        control_layout = QGridLayout\(control_panel\)[\s\S]*?self\.cb_meas_history\.currentIndexChanged\.connect\(self\.on_meas_history_changed\)\n        control_layout\.addWidget\(self\.cb_meas_history, 1, 3\))'

new_code = r"""        control_layout = QGridLayout(control_panel)
        control_layout.setContentsMargins(15, 15, 15, 15)
        control_layout.setHorizontalSpacing(15)
        control_layout.setVerticalSpacing(15)

        # Helper to create segmented buttons
        def create_seg_btn(text, pos):
            from PyQt5.QtWidgets import QPushButton
            btn = QPushButton(text)
            btn.setCheckable(True)
            # Base style
            rad = "4px"
            bl = rad if pos in ("left", "only") else "0px"
            tl = rad if pos in ("left", "only") else "0px"
            br = rad if pos in ("right", "only") else "0px"
            tr = rad if pos in ("right", "only") else "0px"
            b_right = "0px" if pos == "left" or pos == "middle" else "1px solid #555"
            
            btn.setStyleSheet(f'''
                QPushButton {{
                    background-color: #222;
                    color: #AAA;
                    border: 1px solid #555;
                    border-right: {b_right};
                    border-top-left-radius: {tl};
                    border-bottom-left-radius: {bl};
                    border-top-right-radius: {tr};
                    border-bottom-right-radius: {br};
                    padding: 6px 12px;
                    font-weight: bold;
                    font-size: 13px;
                }}
                QPushButton:checked {{
                    background-color: #0ea5e9;
                    color: white;
                    border-color: #0ea5e9;
                }}
                QPushButton:hover:!checked {{
                    background-color: #333;
                }}
            ''')
            btn.setCursor(Qt.PointingHandCursor)
            return btn

        # --- Row 0 ---
        from PyQt5.QtWidgets import QButtonGroup, QHBoxLayout, QWidget, QSizePolicy
        
        # Channel Segmented Control
        chan_widget = QWidget()
        chan_layout = QHBoxLayout(chan_widget)
        chan_layout.setContentsMargins(0, 0, 0, 0)
        chan_layout.setSpacing(0)
        self.btn_grp_chan = QButtonGroup(chan_widget)
        
        btn_l = create_seg_btn("Left", "left")
        btn_l.setChecked(True)
        btn_r = create_seg_btn("Right", "right")
        
        self.btn_grp_chan.addButton(btn_l, 0)
        self.btn_grp_chan.addButton(btn_r, 1)
        chan_layout.addWidget(btn_l)
        chan_layout.addWidget(btn_r)
        
        self.btn_grp_chan.buttonClicked.connect(self.update_watermark)
        control_layout.addWidget(chan_widget, 0, 0, 1, 2)
        
        # Sweeps Segmented Control
        sweeps_widget = QWidget()
        sweeps_layout = QHBoxLayout(sweeps_widget)
        sweeps_layout.setContentsMargins(0, 0, 0, 0)
        sweeps_layout.setSpacing(0)
        self.btn_grp_sweeps = QButtonGroup(sweeps_widget)
        
        btn_1x = create_seg_btn("1x", "left")
        btn_1x.setChecked(True)
        btn_3x = create_seg_btn("3x", "middle")
        btn_5x = create_seg_btn("5x", "right")
        
        self.btn_grp_sweeps.addButton(btn_1x, 1)
        self.btn_grp_sweeps.addButton(btn_3x, 3)
        self.btn_grp_sweeps.addButton(btn_5x, 5)
        sweeps_layout.addWidget(btn_1x)
        sweeps_layout.addWidget(btn_3x)
        sweeps_layout.addWidget(btn_5x)
        
        control_layout.addWidget(sweeps_widget, 0, 2, 1, 2)
        
        # --- Row 1 ---
        self.cb_meas_target = QComboBox()
        self.cb_meas_target.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.cb_meas_target.setMinimumWidth(180)
        self.cb_meas_target.setStyleSheet("QComboBox { background: #333; color: white; border: 1px solid #555; padding: 6px; border-radius: 4px; }")
        self.cb_meas_target.currentIndexChanged.connect(self.on_meas_target_changed)
        control_layout.addWidget(self.cb_meas_target, 1, 0, 1, 2)

        self.cb_meas_history = QComboBox()
        self.cb_meas_history.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.cb_meas_history.setMinimumWidth(220)
        self.cb_meas_history.setStyleSheet("QComboBox { background: #333; color: white; border: 1px solid #555; padding: 6px; border-radius: 4px; }")
        self.cb_meas_history.currentIndexChanged.connect(self.on_meas_history_changed)
        control_layout.addWidget(self.cb_meas_history, 1, 2, 1, 2)"""

code = re.sub(pattern, new_code, code)

with open("main.py", "w") as f:
    f.write(code)

print("Segmented controls patched.")
