import re

with open("main.py", "r") as f:
    code = f.read()

# We look for:
#        self.lbl_subtitle = QLabel("DIAGNOSTICS")
#        self.lbl_subtitle.setStyleSheet(...)
#        
#        top_layout.addWidget(lbl_title)
#        top_layout.addWidget(self.lbl_subtitle)
#        top_layout.addStretch()

insert_point = r'(        top_layout\.addWidget\(self\.lbl_subtitle\)\n        top_layout\.addStretch\(\)\n)'

new_code = r"""\1
        # New Global Status & Selectors
        self.lbl_active_profile = QLabel("No Profile Selected")
        self.lbl_active_profile.setStyleSheet("color: #00FF99; font-size: 13px; font-weight: bold; margin-right: 15px;")
        
        from PyQt5.QtWidgets import QComboBox
        self.cb_global_target = QComboBox()
        self.cb_global_target.setMinimumWidth(200)
        self.cb_global_target.addItem("No Target Selected", None)
        self.cb_global_target.setStyleSheet("QComboBox { background: #222; color: white; border: 1px solid #444; padding: 4px; border-radius: 4px; font-size: 11px; margin-right: 5px; } QComboBox QAbstractItemView { background-color: #222; color: white; }")
        
        self.cb_global_history = QComboBox()
        self.cb_global_history.setMinimumWidth(250)
        self.cb_global_history.addItem("No History Selected", None)
        self.cb_global_history.setStyleSheet("QComboBox { background: #222; color: white; border: 1px solid #444; padding: 4px; border-radius: 4px; font-size: 11px; margin-right: 15px; } QComboBox QAbstractItemView { background-color: #222; color: white; }")
        
        top_layout.addWidget(self.lbl_active_profile)
        top_layout.addWidget(self.cb_global_target)
        top_layout.addWidget(self.cb_global_history)
        
        self.cb_global_target.currentIndexChanged.connect(self.on_global_target_changed)
        self.cb_global_history.currentIndexChanged.connect(self.on_global_history_changed)
"""

code = re.sub(insert_point, new_code, code)

with open("main.py", "w") as f:
    f.write(code)

print("Top bar patched safely.")
