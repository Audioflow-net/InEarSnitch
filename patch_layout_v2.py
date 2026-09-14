import re
with open("history_ui.py", "r") as f:
    code = f.read()

# 1. Main layout
code = code.replace("self.layout = QHBoxLayout(self)", "self.layout = QVBoxLayout(self)")

# 2. Add split_layout before LEFT PANE
code = code.replace("        # --- LEFT PANE ---", "        split_layout = QHBoxLayout()\n        split_layout.setContentsMargins(0, 0, 0, 0)\n        split_layout.setSpacing(0)\n\n        # --- LEFT PANE ---")

# 3. Change left layout margins to match analysis_ui (bottom margin 0)
code = code.replace("left_layout.setContentsMargins(4, 4, 4, 4)", "left_layout.setContentsMargins(4, 4, 4, 0)")

# 4. Remove left_layout.addWidget(self.edit_container) and edit_container.setEnabled(False)
code = code.replace("        left_layout.addWidget(self.edit_container)\n        self.edit_container.setEnabled(False) # Default disabled\n", "")
# if there's a variation of it:
code = code.replace("        left_layout.addWidget(self.edit_container)\n        self.edit_container.setEnabled(False)\n", "")
# just the addWidget
code = code.replace("left_layout.addWidget(self.edit_container)", "")

# 5. Add left_pane to split_layout instead of self.layout
code = code.replace("self.layout.addWidget(left_pane, stretch=1)", "split_layout.addWidget(left_pane, stretch=1)")

# 6. Add tools_tabs to split_layout instead of self.layout, then add split_layout and bottom_container to self.layout
code = code.replace("        self.layout.addWidget(self.tools_tabs)", "        split_layout.addWidget(self.tools_tabs)\n        self.layout.addLayout(split_layout)\n        \n        bottom_container = QVBoxLayout()\n        bottom_container.setContentsMargins(0, 0, 0, 0)\n        bottom_container.addWidget(self.edit_container)\n        self.layout.addLayout(bottom_container)")

# 7. Style the edit container properly and set height to 113
# We look for where edit_container is created:
# self.edit_container = QWidget()
# self.edit_container.setFixedHeight(...)
# ...
import re
code = re.sub(r'self\.edit_container = QWidget\(\)\n\s*self\.edit_container\.setFixedHeight\(\d+\)\n\s*self\.edit_container\.setStyleSheet\(.*?\)\n\s*edit_layout = QHBoxLayout\(self\.edit_container\)\n\s*edit_layout\.setContentsMargins\(.*?\)\n\s*edit_layout\.setSpacing\(\d+\)', 
    'self.edit_container = QFrame()\n        self.edit_container.setFixedHeight(113)\n        self.edit_container.setObjectName("EditContainer")\n        self.edit_container.setStyleSheet("#EditContainer { background-color: #222; border-radius: 8px; }")\n        edit_layout = QHBoxLayout(self.edit_container)\n        edit_layout.setContentsMargins(15, 12, 15, 12)\n        edit_layout.setSpacing(20)', code, flags=re.DOTALL)

with open("history_ui.py", "w") as f:
    f.write(code)
