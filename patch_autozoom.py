import sys

with open('main.py', 'r') as f:
    content = f.read()

old_btn = """        self.btn_reset_view = QPushButton("Reset Zoom")
        self.btn_reset_view.setToolTip("Reset graph zoom level")
        self.btn_reset_view.setMinimumWidth(100)
        self.btn_reset_view.setStyleSheet("background-color: transparent; color: #888; border: 1px solid #444; padding: 4px 12px; border-radius: 4px;")"""
        
new_btn = """        self.btn_reset_view = QPushButton("🔍 Autozoom")
        self.btn_reset_view.setToolTip("Autozoom graph to fit curves")
        self.btn_reset_view.setMinimumWidth(110)
        self.btn_reset_view.setStyleSheet("QPushButton { background-color: #3b82f6; color: white; border: none; padding: 6px 14px; border-radius: 4px; font-weight: bold; } QPushButton:hover { background-color: #2563eb; }")"""

content = content.replace(old_btn, new_btn)

# Also disable native pyqtgraph button
if "self.plot_widget.setLimits(yMin=20, yMax=140)" in content:
    content = content.replace("self.plot_widget.setLimits(yMin=20, yMax=140)", "self.plot_widget.setLimits(yMin=20, yMax=140)\n        self.plot_widget.hideButtons()")

with open('main.py', 'w') as f:
    f.write(content)
