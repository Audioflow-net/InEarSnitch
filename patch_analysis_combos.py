import re

with open("analysis_ui.py", "r") as f:
    code = f.read()

insert_point = r'(        desc\.setStyleSheet\("color: #888; font-size: 13px; margin-bottom: 15px;"\)\n        self\.layout\.addWidget\(desc\)\n)'

new_code = r"""\1
        # Target and History Selectors
        sel_layout = QHBoxLayout()
        sel_layout.setContentsMargins(0, 0, 0, 10)
        from PyQt5.QtWidgets import QComboBox
        sel_layout.addWidget(QLabel("Target:", styleSheet="color: #AAA; font-weight: bold; font-size: 12px;"))
        self.cb_ana_target = QComboBox()
        self.cb_ana_target.setMinimumWidth(200)
        self.cb_ana_target.setStyleSheet("QComboBox { background: #222; color: white; border: 1px solid #444; padding: 4px; border-radius: 4px; font-size: 12px; } QComboBox QAbstractItemView { background-color: #222; color: white; }")
        sel_layout.addWidget(self.cb_ana_target)
        
        sel_layout.addSpacing(20)
        
        sel_layout.addWidget(QLabel("History:", styleSheet="color: #AAA; font-weight: bold; font-size: 12px;"))
        self.cb_ana_history = QComboBox()
        self.cb_ana_history.setMinimumWidth(250)
        self.cb_ana_history.setStyleSheet("QComboBox { background: #222; color: white; border: 1px solid #444; padding: 4px; border-radius: 4px; font-size: 12px; } QComboBox QAbstractItemView { background-color: #222; color: white; }")
        sel_layout.addWidget(self.cb_ana_history)
        
        sel_layout.addStretch()
        self.layout.addLayout(sel_layout)
"""

code = re.sub(insert_point, new_code, code)

with open("analysis_ui.py", "w") as f:
    f.write(code)

print("Analysis comboboxes patched.")
