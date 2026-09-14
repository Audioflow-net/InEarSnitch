import sys

with open('analysis_ui.py', 'r') as f:
    content = f.read()

# Connect L/R buttons
old_connect = """        self.btn_run_sweep.clicked.connect(self.request_measurement.emit)
        self.btn_run_sweep.setToolTip("Run a new Sine Sweep measurement from within the Analysis tab")
        
        zoom_layout.addWidget(self.btn_chan_l)"""

new_connect = """        self.btn_run_sweep.clicked.connect(self.request_measurement.emit)
        self.btn_run_sweep.setToolTip("Run a new Sine Sweep measurement from within the Analysis tab")
        
        self.btn_chan_l.clicked.connect(self.refresh_view)
        self.btn_chan_r.clicked.connect(self.refresh_view)
        
        zoom_layout.addWidget(self.btn_chan_l)"""
content = content.replace(old_connect, new_connect)

with open('analysis_ui.py', 'w') as f:
    f.write(content)
