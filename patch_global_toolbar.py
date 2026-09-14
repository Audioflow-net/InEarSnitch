import sys

with open('analysis_ui.py', 'r') as f:
    content = f.read()

# 1. Refactor the Splitter and Toolbar layout
old_layout_1 = """        self.splitter = QSplitter(Qt.Horizontal)
        self.layout.addWidget(self.splitter)
        
        # --- Left Pane: Graphs (QTabWidget) ---
        self.graph_tabs = QTabWidget()"""

new_layout_1 = """        self.splitter = QSplitter(Qt.Horizontal)
        self.layout.addWidget(self.splitter)
        
        # --- Left Pane ---
        left_pane_widget = QWidget()
        left_pane_layout = QVBoxLayout(left_pane_widget)
        left_pane_layout.setContentsMargins(4, 4, 4, 4)
        left_pane_layout.setSpacing(6)
        
        # --- Smart Toolbar (Global) ---
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
        zoom_layout.addWidget(self.btn_reset_zoom)
        left_pane_layout.addLayout(zoom_layout)
        
        # --- Left Pane: Graphs (QTabWidget) ---
        self.graph_tabs = QTabWidget()"""

content = content.replace(old_layout_1, new_layout_1)

# Now remove the old zoom_layout from fr_container
old_fr_toolbar = """        # --- Smart Toolbar (Inline) ---
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
        zoom_layout.addWidget(self.btn_reset_zoom)
        fr_layout.addLayout(zoom_layout)"""

content = content.replace(old_fr_toolbar, "")

# And we need to add left_pane_widget to the splitter instead of graph_tabs
old_splitter_add = """        self.splitter.addWidget(self.graph_tabs)"""
new_splitter_add = """        left_pane_layout.addWidget(self.graph_tabs)
        self.splitter.addWidget(left_pane_widget)"""
content = content.replace(old_splitter_add, new_splitter_add)

# 2. Modify Analyzer call to include thd_data
old_analyzer_call = """report = Analyzer.run_full_diagnostics(freqs, mag_l, mag_r, best_ref_l, best_ref_r, ir_l_f, ir_r_f)"""
new_analyzer_call = """report = Analyzer.run_full_diagnostics(freqs, mag_l, mag_r, best_ref_l, best_ref_r, ir_l_f, ir_r_f, thd_data)"""
content = content.replace(old_analyzer_call, new_analyzer_call)

with open('analysis_ui.py', 'w') as f:
    f.write(content)
