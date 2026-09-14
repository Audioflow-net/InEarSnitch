import sys

with open('analysis_ui.py', 'r') as f:
    content = f.read()

# Add signal
old_class_def = """class AnalysisWidget(QWidget):
    def __init__(self):"""

new_class_def = """class AnalysisWidget(QWidget):
    request_measurement = pyqtSignal()

    def __init__(self):"""

content = content.replace(old_class_def, new_class_def)

# Add button
old_layout_code = """        zoom_layout.addWidget(self.btn_chan_l)
        zoom_layout.addWidget(self.btn_chan_r)
        zoom_layout.addWidget(self.cb_ana_target)
        zoom_layout.addWidget(self.cb_ana_history)
        zoom_layout.addStretch()
        zoom_layout.addWidget(self.btn_reset_zoom)"""

new_layout_code = """        self.btn_run_sweep = QPushButton("▶ MEASURE")
        self.btn_run_sweep.setStyleSheet("QPushButton { background: #db2777; color: white; border-radius: 4px; padding: 2px 12px; font-weight: bold; font-size: 11px; margin-left: 8px; } QPushButton:hover { background: #be185d; }")
        self.btn_run_sweep.clicked.connect(self.request_measurement.emit)
        self.btn_run_sweep.setToolTip("Run a new Sine Sweep measurement from within the Analysis tab")
        
        zoom_layout.addWidget(self.btn_chan_l)
        zoom_layout.addWidget(self.btn_chan_r)
        zoom_layout.addWidget(self.cb_ana_target)
        zoom_layout.addWidget(self.cb_ana_history)
        zoom_layout.addWidget(self.btn_run_sweep)
        zoom_layout.addStretch()
        zoom_layout.addWidget(self.btn_reset_zoom)"""

content = content.replace(old_layout_code, new_layout_code)

with open('analysis_ui.py', 'w') as f:
    f.write(content)
