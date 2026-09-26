import re

with open("main.py", "r") as f:
    content = f.read()

# We want to inject the restore logic at the end of load_targets, which is right before:
#     def style_tab(self, btn, active):
# Wait, let's find the exact end of load_targets:
old_end = """                # Update placeholder text manually if empty
                if b.count() > 0 and b.currentIndex() == -1:
                    line_edit.setText(b.itemText(0))

    def style_tab(self, btn, active):"""

new_end = """                # Update placeholder text manually if empty
                if b.count() > 0 and b.currentIndex() == -1:
                    line_edit.setText(b.itemText(0))
                    
        # Restore selections
        if saved_hist and saved_hist != "No History Selected":
            idx = self.cb_meas_history.findText(saved_hist)
            if idx >= 0:
                for b in boxes_hist:
                    b.setCurrentIndex(idx)
        if saved_tgt and saved_tgt != "No Target Selected":
            idx = self.cb_meas_target.findText(saved_tgt)
            if idx >= 0:
                for b in boxes_tgt:
                    b.setCurrentIndex(idx)

    def style_tab(self, btn, active):"""

content = content.replace(old_end, new_end)

with open("main.py", "w") as f:
    f.write(content)
