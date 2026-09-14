import re

with open("main.py", "r") as f:
    code = f.read()

# Pattern for the block to remove
# We want to keep self.lbl_active_profile and top_layout.addWidget(self.lbl_active_profile)
# and remove the combo boxes
pattern = r'        from PyQt5\.QtWidgets import QComboBox\n        self\.cb_global_target = QComboBox\(\)[\s\S]*?self\.cb_global_history\.currentIndexChanged\.connect\(self\.on_global_history_changed\)\n'

# We also need to add self.lbl_active_profile back to the top_layout since it was matched.
# Wait, the addWidget(self.lbl_active_profile) is INSIDE the matched block.
# Let's just find the whole block:
full_pattern = r'        # New Global Status & Selectors[\s\S]*?self\.cb_global_history\.currentIndexChanged\.connect\(self\.on_global_history_changed\)\n'

new_code = """        # Global Status
        self.lbl_active_profile = QLabel("No Profile Selected")
        self.lbl_active_profile.setStyleSheet("color: #00FF99; font-size: 13px; font-weight: bold; margin-right: 15px;")
        top_layout.addWidget(self.lbl_active_profile)
"""

code = re.sub(full_pattern, new_code, code)

with open("main.py", "w") as f:
    f.write(code)

print("Top bar comboboxes removed.")
