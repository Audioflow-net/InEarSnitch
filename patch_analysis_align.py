import re

with open("analysis_ui.py", "r") as f:
    code = f.read()

old_code = """        # Right Side (THD and CSD vertically stacked)
        right_graphs_layout = QVBoxLayout()
        right_graphs_layout.setContentsMargins(0, 0, 0, 0)
        self.right_graphs_layout = right_graphs_layout
        
        # 2. THD Graph"""

new_code = """        # Right Side (THD and CSD vertically stacked)
        right_graphs_layout = QVBoxLayout()
        right_graphs_layout.setContentsMargins(0, 0, 0, 0)
        self.right_graphs_layout = right_graphs_layout
        
        # Add a dummy row to align with the zoom buttons on the left
        align_layout = QHBoxLayout()
        dummy_btn = QPushButton(" ")
        dummy_btn.setStyleSheet("padding: 4px 16px; font-size: 12px; border: 1px solid transparent;")
        sp = dummy_btn.sizePolicy()
        sp.setRetainSizeWhenHidden(True)
        dummy_btn.setSizePolicy(sp)
        dummy_btn.hide()
        align_layout.addWidget(dummy_btn)
        right_graphs_layout.addLayout(align_layout)
        
        # 2. THD Graph"""

code = code.replace(old_code, new_code)

with open("analysis_ui.py", "w") as f:
    f.write(code)

print("Alignment patched.")
