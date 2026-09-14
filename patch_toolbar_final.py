import sys

with open('main.py', 'r') as f:
    content = f.read()

# 1. Replace Module 3 (Profiles) to include toggles
old_prof = """        # --- MODULE 3: PROFILES (Target & History) ---
        mod_prof = QVBoxLayout()
        mod_prof.setSpacing(6)
        
        self.cb_meas_target = QComboBox()
        self.cb_meas_target.setToolTip("Select a target curve. Type to search.")
        self.cb_meas_target.setMinimumWidth(180)
        self.cb_meas_target.setStyleSheet("QComboBox { background: #262626; color: #E0E0E0; border: 1px solid #555; padding: 6px; border-radius: 4px; font-size: 12px; font-weight: 500; } QComboBox QAbstractItemView { background-color: #222; color: white; selection-background-color: #10b981; }")
        self.cb_meas_target.currentIndexChanged.connect(self.on_meas_target_changed)
        
        self.cb_meas_history = QComboBox()
        self.cb_meas_history.setToolTip("Select a historical measurement. Type to search.")
        self.cb_meas_history.setMinimumWidth(180)
        self.cb_meas_history.setStyleSheet("QComboBox { background: #262626; color: #E0E0E0; border: 1px solid #555; padding: 6px; border-radius: 4px; font-size: 12px; font-weight: 500; } QComboBox QAbstractItemView { background-color: #222; color: white; selection-background-color: #10b981; }")
        self.cb_meas_history.currentIndexChanged.connect(self.on_meas_history_changed)
        
        mod_prof.addWidget(self.cb_meas_target)
        mod_prof.addWidget(self.cb_meas_history)
        control_layout.addLayout(mod_prof)"""

new_prof = """        # --- MODULE 3: PROFILES (Target & History) ---
        mod_prof = QVBoxLayout()
        mod_prof.setSpacing(6)
        
        # Target Row
        tgt_row = QHBoxLayout()
        tgt_row.setSpacing(4)
        self.btn_toggle_target = QPushButton("👁️")
        self.btn_toggle_target.setCheckable(True)
        self.btn_toggle_target.setChecked(True)
        self.btn_toggle_target.setToolTip("Toggle Target Visibility")
        self.btn_toggle_target.setStyleSheet("QPushButton { background: #333; color: white; border: 1px solid #555; border-radius: 4px; font-size: 10px; padding: 4px; } QPushButton:checked { background: #10b981; border: 1px solid #059669; }")
        self.btn_toggle_target.clicked.connect(self.redraw_graph)
        
        self.cb_meas_target = QComboBox()
        self.cb_meas_target.setToolTip("Select a target curve. Type to search.")
        self.cb_meas_target.setMinimumWidth(180)
        self.cb_meas_target.setStyleSheet("QComboBox { background: #262626; color: #E0E0E0; border: 1px solid #555; padding: 6px; border-radius: 4px; font-size: 12px; font-weight: 500; } QComboBox QAbstractItemView { background-color: #222; color: white; selection-background-color: #10b981; }")
        self.cb_meas_target.currentIndexChanged.connect(self.on_meas_target_changed)
        tgt_row.addWidget(self.btn_toggle_target)
        tgt_row.addWidget(self.cb_meas_target, stretch=1)
        
        # History Row
        hist_row = QHBoxLayout()
        hist_row.setSpacing(4)
        self.btn_toggle_history = QPushButton("👁️")
        self.btn_toggle_history.setCheckable(True)
        self.btn_toggle_history.setChecked(True)
        self.btn_toggle_history.setToolTip("Toggle History Visibility")
        self.btn_toggle_history.setStyleSheet("QPushButton { background: #333; color: white; border: 1px solid #555; border-radius: 4px; font-size: 10px; padding: 4px; } QPushButton:checked { background: #10b981; border: 1px solid #059669; }")
        self.btn_toggle_history.clicked.connect(self.redraw_graph)
        
        self.cb_meas_history = QComboBox()
        self.cb_meas_history.setToolTip("Select a historical measurement. Type to search.")
        self.cb_meas_history.setMinimumWidth(180)
        self.cb_meas_history.setStyleSheet("QComboBox { background: #262626; color: #E0E0E0; border: 1px solid #555; padding: 6px; border-radius: 4px; font-size: 12px; font-weight: 500; } QComboBox QAbstractItemView { background-color: #222; color: white; selection-background-color: #10b981; }")
        self.cb_meas_history.currentIndexChanged.connect(self.on_meas_history_changed)
        hist_row.addWidget(self.btn_toggle_history)
        hist_row.addWidget(self.cb_meas_history, stretch=1)
        
        mod_prof.addLayout(tgt_row)
        mod_prof.addLayout(hist_row)
        control_layout.addLayout(mod_prof)"""
        
content = content.replace(old_prof, new_prof)

# 2. Modify Module 4 RTA buttons sizes (make them a bit chunkier as requested)
content = content.replace("font-size: 13px; border-radius: 4px; border: none; padding: 8px 14px;", "font-size: 14px; border-radius: 6px; border: none; padding: 12px 18px;")
content = content.replace("border: 2px solid #db2777; padding: 6px 12px;", "border: 2px solid #db2777; padding: 10px 16px;")
content = content.replace("border: 2px solid #10b981; padding: 6px 12px;", "border: 2px solid #10b981; padding: 10px 16px;")


# 3. Replace Module 5 (Actions) to vertical layout: BIG RUN over Clear+Save
old_act = """        # --- MODULE 5: ACTIONS ---
        mod_act = QHBoxLayout()
        mod_act.setSpacing(10)
        
        # Run Button
        self.btn_capture = QPushButton("RUN")
        self.btn_capture.setToolTip("Start measurement capture (Space)")
        self.btn_capture.setStyleSheet("QPushButton { background-color: #10b981; color: black; font-weight: bold; font-size: 16px; border-radius: 6px; padding: 12px 24px;} QPushButton:disabled { background-color: #555; color: #888; } QPushButton:hover { background-color: #34d399; }")
        self.btn_capture.clicked.connect(self.run_measurement)
        mod_act.addWidget(self.btn_capture)
        
        # Sub actions (Save/Clear) stacked vertically
        sub_act_layout = QVBoxLayout()
        sub_act_layout.setSpacing(4)
        
        self.btn_trace = QPushButton("Clear")
        self.btn_trace.setStyleSheet("QPushButton { background-color: #ef4444; color: white; font-weight: bold; padding: 4px 12px; border-radius: 4px; border: none; } QPushButton:disabled { background-color: #7f1d1d; color: #fca5a5; } QPushButton:hover { background-color: #dc2626; }")
        self.btn_trace.clicked.connect(self.clear_trace)
        
        self.btn_save_db = QPushButton("Save")
        self.btn_save_db.setStyleSheet("QPushButton { background-color: #444; color: white; font-weight: bold; padding: 4px 12px; border-radius: 4px; border: 1px solid #555; } QPushButton:disabled { background-color: #222; color: #555; border: 1px solid #333; } QPushButton:hover { background-color: #555; }")
        self.btn_save_db.clicked.connect(self.save_trace_to_db)
        
        sub_act_layout.addWidget(self.btn_trace)
        sub_act_layout.addWidget(self.btn_save_db)
        mod_act.addLayout(sub_act_layout)
        
        control_layout.addLayout(mod_act)"""
        
new_act = """        # --- MODULE 5: ACTIONS ---
        mod_act = QVBoxLayout()
        mod_act.setSpacing(6)
        
        # Run Button
        self.btn_capture = QPushButton("RUN")
        self.btn_capture.setToolTip("Start measurement capture (Space)")
        self.btn_capture.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.btn_capture.setStyleSheet("QPushButton { background-color: #10b981; color: black; font-weight: bold; font-size: 20px; border-radius: 6px; padding: 8px 30px;} QPushButton:disabled { background-color: #555; color: #888; } QPushButton:hover { background-color: #34d399; }")
        self.btn_capture.clicked.connect(self.run_measurement)
        mod_act.addWidget(self.btn_capture, stretch=3)
        
        # Sub actions (Save/Clear) stacked horizontally
        sub_act_layout = QHBoxLayout()
        sub_act_layout.setSpacing(6)
        
        self.btn_trace = QPushButton("Clear")
        self.btn_trace.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.btn_trace.setStyleSheet("QPushButton { background-color: #ef4444; color: white; font-weight: bold; padding: 6px; border-radius: 4px; border: none; font-size: 13px;} QPushButton:disabled { background-color: #7f1d1d; color: #fca5a5; } QPushButton:hover { background-color: #dc2626; }")
        self.btn_trace.clicked.connect(self.clear_trace)
        
        self.btn_save_db = QPushButton("Save")
        self.btn_save_db.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.btn_save_db.setStyleSheet("QPushButton { background-color: #444; color: white; font-weight: bold; padding: 6px; border-radius: 4px; border: 1px solid #555; font-size: 13px;} QPushButton:disabled { background-color: #222; color: #555; border: 1px solid #333; } QPushButton:hover { background-color: #555; }")
        self.btn_save_db.clicked.connect(self.save_trace_to_db)
        
        sub_act_layout.addWidget(self.btn_trace)
        sub_act_layout.addWidget(self.btn_save_db)
        mod_act.addLayout(sub_act_layout, stretch=1)
        
        control_layout.addLayout(mod_act)"""

content = content.replace(old_act, new_act)

with open('main.py', 'w') as f:
    f.write(content)
