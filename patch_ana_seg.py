import re

with open('analysis_ui.py', 'r') as f:
    content = f.read()

old_block = """        self.btn_chan_l = QPushButton("Left")
        self.btn_chan_l.setToolTip("Show/Hide Left Channel Curve")
        self.btn_chan_l.setCheckable(True)
        self.btn_chan_l.setChecked(True)
        self.btn_chan_l.setFixedSize(45, 24)
        self.btn_chan_l.setProperty("class", "chan_toggle")
        self.btn_chan_l.setProperty("chan", "L")
        
        self.btn_chan_r = QPushButton("Right")
        self.btn_chan_r.setToolTip("Show/Hide Right Channel Curve")
        self.btn_chan_r.setCheckable(True)
        self.btn_chan_r.setChecked(True)
        self.btn_chan_r.setFixedSize(45, 24)
        self.btn_chan_r.setProperty("class", "chan_toggle")
        self.btn_chan_r.setProperty("chan", "R")"""

new_block = """        seg_widget = QWidget()
        seg_layout = QHBoxLayout(seg_widget)
        seg_layout.setContentsMargins(0,0,0,0)
        seg_layout.setSpacing(0)

        self.btn_chan_l = QPushButton("Left")
        self.btn_chan_l.setToolTip("Show/Hide Left Channel Curve")
        self.btn_chan_l.setCheckable(True)
        self.btn_chan_l.setChecked(True)
        self.btn_chan_l.setStyleSheet("QPushButton { background-color: #1f1f23; color: #888; border: 1px solid #3f3f46; border-top-left-radius: 4px; border-bottom-left-radius: 4px; border-right: none; padding: 4px 10px; font-weight: bold; font-size: 11px; } QPushButton:checked { background-color: #0ea5e9; color: white; border-color: #0ea5e9; }")
        
        self.btn_chan_r = QPushButton("Right")
        self.btn_chan_r.setToolTip("Show/Hide Right Channel Curve")
        self.btn_chan_r.setCheckable(True)
        self.btn_chan_r.setChecked(True)
        self.btn_chan_r.setStyleSheet("QPushButton { background-color: #1f1f23; color: #888; border: 1px solid #3f3f46; border-top-right-radius: 4px; border-bottom-right-radius: 4px; padding: 4px 10px; font-weight: bold; font-size: 11px; } QPushButton:checked { background-color: #ef4444; color: white; border-color: #ef4444; }")

        seg_layout.addWidget(self.btn_chan_l)
        seg_layout.addWidget(self.btn_chan_r)"""

content = content.replace(old_block, new_block)

old_layout = """        zoom_layout.addWidget(self.btn_chan_l)
        zoom_layout.addWidget(self.btn_chan_r)"""

new_layout = """        zoom_layout.addWidget(seg_widget)"""

content = content.replace(old_layout, new_layout)

with open('analysis_ui.py', 'w') as f:
    f.write(content)
print("SUCCESS")
