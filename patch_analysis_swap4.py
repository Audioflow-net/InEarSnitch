import re

with open("analysis_ui.py", "r") as f:
    code = f.read()

# 1. Save left_layout
old_left = """        self.left_container = QWidget()
        left_layout = QVBoxLayout(self.left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)"""

new_left = """        self.left_container = QWidget()
        left_layout = QVBoxLayout(self.left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        self.left_layout = left_layout"""

code = code.replace(old_left, new_left)

# 2. Update swap logic
old_swap = """        if idx != -1:
            # Swap in layouts
            self.plots_layout.removeWidget(old_main)
            self.right_graphs_layout.removeWidget(target_widget)
            
            self.plots_layout.insertWidget(0, target_widget, stretch=2)
            self.right_graphs_layout.insertWidget(idx, old_main)"""

new_swap = """        if idx != -1:
            # Swap in layouts
            
            # Find index of old_main in left_layout
            left_idx = -1
            for i in range(self.left_layout.count()):
                item = self.left_layout.itemAt(i)
                if item and item.widget() == old_main:
                    left_idx = i
                    break
                    
            if left_idx != -1:
                self.left_layout.removeWidget(old_main)
                self.right_graphs_layout.removeWidget(target_widget)
                
                self.left_layout.insertWidget(left_idx, target_widget, stretch=1)
                self.right_graphs_layout.insertWidget(idx, old_main)"""

code = code.replace(old_swap, new_swap)

with open("analysis_ui.py", "w") as f:
    f.write(code)

print("Swap logic fixed.")
