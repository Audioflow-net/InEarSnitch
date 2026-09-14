import re

with open("history_ui.py", "r") as f:
    code = f.read()

# Current __init__ structure:
#         self.layout = QHBoxLayout(self)
#         self.layout.setContentsMargins(0, 0, 0, 0)
#         
#         bg = theme.get_color("bg_sec")
# ...
#         left_layout.addWidget(self.edit_container)
#         self.edit_container.setEnabled(False) # Default disabled
#         self.layout.addWidget(left_pane, stretch=1)
# ...
#         self.layout.addWidget(self.tools_tabs)

# We need to change `self.layout` to QVBoxLayout.
# We will create `split_layout = QHBoxLayout()`
# left_pane and tools_tabs go into split_layout.
# edit_container goes into self.layout at the bottom.

# 1. Change self.layout to QVBoxLayout
code = code.replace("self.layout = QHBoxLayout(self)", "self.layout = QVBoxLayout(self)\n        self.layout.setSpacing(0)")

# 2. Add split_layout
code = code.replace("left_pane = QWidget()", "split_layout = QHBoxLayout()\n        split_layout.setContentsMargins(0, 0, 0, 0)\n        split_layout.setSpacing(0)\n        \n        # --- LEFT PANE ---\n        left_pane = QWidget()")

# 3. Change left_layout margins to match analysis_ui (4,4,4,0)
code = code.replace("left_layout.setContentsMargins(4, 4, 4, 4)", "left_layout.setContentsMargins(4, 4, 4, 0)")

# 4. Remove left_layout.addWidget(self.edit_container)
code = code.replace("left_layout.addWidget(self.edit_container)", "")

# 5. Change self.layout.addWidget(left_pane, stretch=1) to split_layout.addWidget
code = code.replace("self.layout.addWidget(left_pane, stretch=1)", "split_layout.addWidget(left_pane, stretch=1)")

# 6. Change self.layout.addWidget(self.tools_tabs) to split_layout.addWidget
# AND then add split_layout and edit_container to self.layout
code = code.replace("self.layout.addWidget(self.tools_tabs)", "split_layout.addWidget(self.tools_tabs)\n        \n        self.layout.addLayout(split_layout)\n        \n        # Bottom Container for exact height matching\n        bottom_container = QVBoxLayout()\n        bottom_container.setContentsMargins(0, 0, 0, 0)\n        self.edit_container.setFixedHeight(83) # Match exact height of Workspace control_panel\n        bottom_container.addWidget(self.edit_container)\n        self.layout.addLayout(bottom_container)")

# 7. Update edit_container height definition which might be 70
code = code.replace("self.edit_container.setFixedHeight(70)", "")

with open("history_ui.py", "w") as f:
    f.write(code)
