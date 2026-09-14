import re

with open("analysis_ui.py", "r") as f:
    code = f.read()

old_swap = """                self.left_layout.removeWidget(old_main)
                self.right_graphs_layout.removeWidget(target_widget)
                
                self.left_layout.insertWidget(left_idx, target_widget, stretch=1)
                self.right_graphs_layout.insertWidget(idx, old_main)"""

new_swap = """                self.left_layout.removeWidget(old_main)
                self.right_graphs_layout.removeWidget(target_widget)
                
                # Swap minimum heights so the layout doesn't break
                old_h = old_main.minimumHeight()
                new_h = target_widget.minimumHeight()
                old_main.setMinimumHeight(new_h)
                target_widget.setMinimumHeight(old_h)
                
                self.left_layout.insertWidget(left_idx, target_widget, stretch=1)
                self.right_graphs_layout.insertWidget(idx, old_main)"""

code = code.replace(old_swap, new_swap)

with open("analysis_ui.py", "w") as f:
    f.write(code)

print("Heights swapped.")
