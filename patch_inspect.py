import re

with open('main.py', 'r') as f:
    content = f.read()

# 1. Remove Emoji
content = content.replace('self.btn_live_seal = QPushButton("🎧 LIVE SEAL")', 'self.btn_live_seal = QPushButton("LIVE SEAL")')

# 2. Add Button
old_save_db = r"""        self.btn_save_db.clicked.connect(self.save_trace_to_db)
        control_layout.addWidget(self.btn_save_db, 1, 6)"""

new_save_db = r"""        self.btn_save_db.clicked.connect(self.save_trace_to_db)
        control_layout.addWidget(self.btn_save_db, 1, 6)
        
        self.btn_inspect = QPushButton("I\nN\nS\nP\nE\nC\nT")
        self.btn_inspect.setToolTip("Inspect current curve or selected history in Analysis tab")
        self.btn_inspect.setStyleSheet("QPushButton { background-color: #3b82f6; color: white; font-weight: bold; font-size: 10px; border-radius: 4px; padding-top: 4px; padding-bottom: 4px; } QPushButton:hover { background-color: #2563eb; }")
        self.btn_inspect.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.btn_inspect.setFixedWidth(24)
        self.btn_inspect.clicked.connect(self.inspect_current)
        control_layout.addWidget(self.btn_inspect, 0, 7, 2, 1)"""

if old_save_db in content:
    content = content.replace(old_save_db, new_save_db)
else:
    print("Failed to find save_db block")

# 3. Add Method
old_clear_trace = r"""    def clear_trace(self):"""
new_clear_trace = r"""    def inspect_current(self):
        # If there's no live measurement but history is selected, promote it to primary
        if getattr(self, 'temp_freqs', None) is None:
            if getattr(self, 'history_freqs', None) is not None:
                self.temp_freqs = self.history_freqs
                self.temp_mag_l = self.history_mag_l
                self.temp_mag_r = self.history_mag_r
                self.temp_thd_data = None
                self.temp_csd_data = None
                self.temp_ir_l = None
                self.temp_ir_r = None
        
        # Switch to analysis tab
        self.workspace_stacked.setCurrentIndex(2)
        # Update analysis view to ensure UI reflects current curve
        self.update_analysis_view()

    def clear_trace(self):"""

if old_clear_trace in content:
    content = content.replace(old_clear_trace, new_clear_trace)
else:
    print("Failed to find clear_trace method")

with open('main.py', 'w') as f:
    f.write(content)

print("Patch applied.")
