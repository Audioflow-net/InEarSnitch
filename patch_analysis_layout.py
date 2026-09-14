import re

with open("analysis_ui.py", "r") as f:
    code = f.read()

old_code = """        right_graphs_layout = QVBoxLayout()
        right_graphs_layout.setContentsMargins(0, 0, 0, 0)
        
        # 2. THD Graph"""

new_code = """        right_graphs_layout = QVBoxLayout()
        right_graphs_layout.setContentsMargins(0, 0, 0, 0)
        self.right_graphs_layout = right_graphs_layout
        
        # 2. THD Graph"""

code = code.replace(old_code, new_code)

with open("analysis_ui.py", "w") as f:
    f.write(code)

print("Layout variable patched.")
