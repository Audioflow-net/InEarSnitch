import sys
import re

with open('analysis_ui.py', 'r') as f:
    content = f.read()

# 1. Need to import QButtonGroup at the top of the file
if "from PyQt5.QtWidgets import QButtonGroup" not in content:
    content = content.replace("from PyQt5.QtWidgets import ", "from PyQt5.QtWidgets import QButtonGroup, ")

# 2. Add new signals to AnalysisWidget
old_class_def = """class AnalysisWidget(QWidget):
    request_measurement = pyqtSignal()

    def __init__(self):"""
new_class_def = """class AnalysisWidget(QWidget):
    request_measurement = pyqtSignal()
    request_rta = pyqtSignal(bool)
    request_save = pyqtSignal()
    
    def __init__(self):"""
content = content.replace(old_class_def, new_class_def)

# 3. Replace the old zoom_layout block
old_toolbar = """        # --- Smart Toolbar (Global) ---
        zoom_layout = QHBoxLayout()
        zoom_layout.setSpacing(6)
        
        self.btn_chan_l = QPushButton("L")
        self.btn_chan_l.setCheckable(True)
        self.btn_chan_l.setChecked(True)
        self.btn_chan_l.setFixedSize(26, 22)
        self.btn_chan_l.setStyleSheet("QPushButton { background: #333; color: white; border-radius: 4px; font-weight: bold; font-size: 11px; } QPushButton:checked { background: #0ea5e9; color: white; }")
        
        self.btn_chan_r = QPushButton("R")
        self.btn_chan_r.setCheckable(True)
        self.btn_chan_r.setChecked(True)
        self.btn_chan_r.setFixedSize(26, 22)
        self.btn_chan_r.setStyleSheet("QPushButton { background: #333; color: white; border-radius: 4px; font-weight: bold; font-size: 11px; } QPushButton:checked { background: #ef4444; color: white; }")
        
        self.cb_ana_target = QComboBox()
        self.cb_ana_target.addItem("-- Target --")
        self.cb_ana_target.setToolTip("Select a target curve for analysis.")
        self.cb_ana_target.setMinimumWidth(120)
        self.cb_ana_target.setStyleSheet("QComboBox { background: #222; color: white; border: 1px solid #444; padding: 2px 6px; border-radius: 4px; font-size: 11px; }")
        
        self.cb_ana_history = QComboBox()
        self.cb_ana_history.addItem("-- History --")
        self.cb_ana_history.setToolTip("Select a historical measurement.")
        self.cb_ana_history.setMinimumWidth(120)
        self.cb_ana_history.setStyleSheet("QComboBox { background: #222; color: white; border: 1px solid #444; padding: 2px 6px; border-radius: 4px; font-size: 11px; }")
        
        self.btn_run_sweep = QPushButton("▶ MEASURE")
        self.btn_run_sweep.setStyleSheet("QPushButton { background: #db2777; color: white; border-radius: 4px; padding: 2px 12px; font-weight: bold; font-size: 11px; margin-left: 8px; } QPushButton:hover { background: #be185d; }")
        self.btn_run_sweep.clicked.connect(self.request_measurement.emit)
        self.btn_run_sweep.setToolTip("Run a new Sine Sweep measurement from within the Analysis tab")
        
        self.btn_reset_zoom = QPushButton("Reset Zoom")
        self.btn_reset_zoom.setStyleSheet("QPushButton { background: #333; color: white; border-radius: 4px; padding: 2px 8px; font-size: 10px; }")
        
        zoom_layout.addWidget(self.btn_chan_l)
        zoom_layout.addWidget(self.btn_chan_r)
        zoom_layout.addWidget(self.cb_ana_target)
        zoom_layout.addWidget(self.cb_ana_history)
        zoom_layout.addWidget(self.btn_run_sweep)
        zoom_layout.addStretch()
        zoom_layout.addWidget(self.btn_reset_zoom)"""

new_toolbar = """        # --- Smart Toolbar (Global Workspace Cockpit) ---
        zoom_layout = QHBoxLayout()
        zoom_layout.setSpacing(4)
        
        # 1. Measurement Ear selection (Mic L / Mic R)
        self.btn_meas_l = QPushButton("Mic L")
        self.btn_meas_l.setCheckable(True)
        self.btn_meas_l.setChecked(True)
        self.btn_meas_l.setFixedSize(45, 22)
        self.btn_meas_l.setStyleSheet("QPushButton { background: #333; color: white; border-top-left-radius: 4px; border-bottom-left-radius: 4px; font-weight: bold; font-size: 10px; } QPushButton:checked { background: #10b981; color: white; }")
        
        self.btn_meas_r = QPushButton("Mic R")
        self.btn_meas_r.setCheckable(True)
        self.btn_meas_r.setFixedSize(45, 22)
        self.btn_meas_r.setStyleSheet("QPushButton { background: #333; color: white; border-top-right-radius: 4px; border-bottom-right-radius: 4px; font-weight: bold; font-size: 10px; } QPushButton:checked { background: #10b981; color: white; }")
        
        self.mic_group = QButtonGroup()
        self.mic_group.addWidget(self.btn_meas_l)
        self.mic_group.addWidget(self.btn_meas_r)
        
        self.cb_avg = QComboBox()
        self.cb_avg.addItems(["1x", "3x", "5x"])
        self.cb_avg.setToolTip("Sweep Averaging")
        self.cb_avg.setStyleSheet("QComboBox { background: #222; color: white; border: 1px solid #444; padding: 2px 4px; border-radius: 4px; font-size: 10px; }")
        
        # 2. View Visibility (Eye L / Eye R)
        self.btn_chan_l = QPushButton("👁 L")
        self.btn_chan_l.setCheckable(True)
        self.btn_chan_l.setChecked(True)
        self.btn_chan_l.setFixedSize(36, 22)
        self.btn_chan_l.setStyleSheet("QPushButton { background: #333; color: white; border-radius: 4px; font-weight: bold; font-size: 10px; margin-left: 8px;} QPushButton:checked { background: #0ea5e9; color: white; }")
        
        self.btn_chan_r = QPushButton("👁 R")
        self.btn_chan_r.setCheckable(True)
        self.btn_chan_r.setChecked(True)
        self.btn_chan_r.setFixedSize(36, 22)
        self.btn_chan_r.setStyleSheet("QPushButton { background: #333; color: white; border-radius: 4px; font-weight: bold; font-size: 10px; } QPushButton:checked { background: #ef4444; color: white; }")
        
        # 3. Targets & History
        self.cb_ana_target = QComboBox()
        self.cb_ana_target.addItem("- Target -")
        self.cb_ana_target.setMinimumWidth(100)
        self.cb_ana_target.setStyleSheet("QComboBox { background: #222; color: white; border: 1px solid #444; padding: 2px 4px; border-radius: 4px; font-size: 10px; margin-left: 8px;}")
        
        self.cb_ana_history = QComboBox()
        self.cb_ana_history.addItem("- History -")
        self.cb_ana_history.setMinimumWidth(100)
        self.cb_ana_history.setStyleSheet("QComboBox { background: #222; color: white; border: 1px solid #444; padding: 2px 4px; border-radius: 4px; font-size: 10px; }")
        
        # 4. Action Buttons
        self.btn_run_sweep = QPushButton("▶ SWEEP")
        self.btn_run_sweep.setStyleSheet("QPushButton { background: #10b981; color: white; border-radius: 4px; padding: 2px 10px; font-weight: bold; font-size: 11px; margin-left: 8px; } QPushButton:hover { background: #059669; } QPushButton:disabled { background: #444; color: #888; }")
        self.btn_run_sweep.clicked.connect(self.request_measurement.emit)
        
        self.btn_rta = QPushButton("🔴 RTA")
        self.btn_rta.setCheckable(True)
        self.btn_rta.setStyleSheet("QPushButton { background: #333; color: white; border-radius: 4px; padding: 2px 10px; font-weight: bold; font-size: 11px; } QPushButton:checked { background: #db2777; } QPushButton:hover { background: #555; }")
        self.btn_rta.toggled.connect(self.request_rta.emit)
        
        self.btn_save_db = QPushButton("💾 SAVE")
        self.btn_save_db.setStyleSheet("QPushButton { background: #333; color: white; border-radius: 4px; padding: 2px 10px; font-weight: bold; font-size: 11px; } QPushButton:hover { background: #555; }")
        self.btn_save_db.clicked.connect(self.request_save.emit)
        
        self.btn_reset_zoom = QPushButton("Reset Zoom")
        self.btn_reset_zoom.setStyleSheet("QPushButton { background: #333; color: white; border-radius: 4px; padding: 2px 8px; font-size: 10px; }")
        
        zoom_layout.addWidget(self.btn_meas_l)
        zoom_layout.addWidget(self.btn_meas_r)
        zoom_layout.addWidget(self.cb_avg)
        zoom_layout.addWidget(self.btn_chan_l)
        zoom_layout.addWidget(self.btn_chan_r)
        zoom_layout.addWidget(self.cb_ana_target)
        zoom_layout.addWidget(self.cb_ana_history)
        zoom_layout.addWidget(self.btn_run_sweep)
        zoom_layout.addWidget(self.btn_rta)
        zoom_layout.addWidget(self.btn_save_db)
        zoom_layout.addStretch()
        zoom_layout.addWidget(self.btn_reset_zoom)"""

content = content.replace(old_toolbar, new_toolbar)
with open('analysis_ui.py', 'w') as f:
    f.write(content)
