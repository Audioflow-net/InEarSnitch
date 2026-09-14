import sys

with open('analysis_ui.py', 'r') as f:
    content = f.read()

old_l_btn = """        self.btn_chan_l = QPushButton("L")
        self.btn_chan_l.setCheckable(True)
        self.btn_chan_l.setChecked(True)
        self.btn_chan_l.setFixedSize(26, 22)
        self.btn_chan_l.setStyleSheet("QPushButton { background: #333; color: white; border-radius: 4px; font-weight: bold; font-size: 11px; } QPushButton:checked { background: #0ea5e9; color: white; }")
        
        self.btn_chan_r = QPushButton("R")
        self.btn_chan_r.setCheckable(True)
        self.btn_chan_r.setChecked(True)
        self.btn_chan_r.setFixedSize(26, 22)
        self.btn_chan_r.setStyleSheet("QPushButton { background: #333; color: white; border-radius: 4px; font-weight: bold; font-size: 11px; } QPushButton:checked { background: #ef4444; color: white; }")"""

new_l_btn = """        from PyQt5.QtWidgets import QLabel
        lbl_vis = QLabel("Show Curves:")
        lbl_vis.setStyleSheet("color: #888; font-size: 10px; font-weight: bold;")
        zoom_layout.addWidget(lbl_vis)

        self.btn_chan_l = QPushButton("👁 L")
        self.btn_chan_l.setToolTip("Show/Hide Left Channel Curve")
        self.btn_chan_l.setCheckable(True)
        self.btn_chan_l.setChecked(True)
        self.btn_chan_l.setFixedSize(36, 22)
        self.btn_chan_l.setStyleSheet("QPushButton { background: #333; color: white; border-radius: 4px; font-weight: bold; font-size: 11px; } QPushButton:checked { background: #0ea5e9; color: white; }")
        
        self.btn_chan_r = QPushButton("👁 R")
        self.btn_chan_r.setToolTip("Show/Hide Right Channel Curve")
        self.btn_chan_r.setCheckable(True)
        self.btn_chan_r.setChecked(True)
        self.btn_chan_r.setFixedSize(36, 22)
        self.btn_chan_r.setStyleSheet("QPushButton { background: #333; color: white; border-radius: 4px; font-weight: bold; font-size: 11px; } QPushButton:checked { background: #ef4444; color: white; }")"""

content = content.replace(old_l_btn, new_l_btn)

with open('analysis_ui.py', 'w') as f:
    f.write(content)
