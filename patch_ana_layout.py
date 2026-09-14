import re

with open('analysis_ui.py', 'r') as f:
    content = f.read()

old_block = """        lbl_vis = QLabel("Show:")
        lbl_vis.setStyleSheet("color: #888; font-size: 11px; font-weight: bold; margin-right: 4px;")
        zoom_layout.addWidget(lbl_vis)

        seg_widget = QWidget()
        seg_layout = QHBoxLayout(seg_widget)
        seg_layout.setContentsMargins(0,0,0,0)
        seg_layout.setSpacing(0)"""

new_block = """        vis_layout = QVBoxLayout()
        vis_layout.setSpacing(2)
        vis_layout.setContentsMargins(0, 0, 0, 0)

        seg_widget = QWidget()
        seg_layout = QHBoxLayout(seg_widget)
        seg_layout.setContentsMargins(0,0,0,0)
        seg_layout.setSpacing(0)"""
content = content.replace(old_block, new_block)

old_add = """        seg_layout.addWidget(self.btn_chan_l)
        seg_layout.addWidget(self.btn_chan_r)
        
        zoom_layout.addWidget(seg_widget)"""

new_add = """        seg_layout.addWidget(self.btn_chan_l)
        seg_layout.addWidget(self.btn_chan_r)
        
        lbl_vis = QLabel("SHOW")
        lbl_vis.setAlignment(Qt.AlignCenter)
        lbl_vis.setStyleSheet("color: #777; font-size: 9px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px;")
        
        vis_layout.addWidget(seg_widget)
        vis_layout.addWidget(lbl_vis)
        
        zoom_layout.addLayout(vis_layout)"""
content = content.replace(old_add, new_add)

with open('analysis_ui.py', 'w') as f:
    f.write(content)
print("SUCCESS")
