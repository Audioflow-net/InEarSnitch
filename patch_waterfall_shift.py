import re

with open("analysis_ui.py", "r") as f:
    content = f.read()

# Change left-shift (0.99) to right-shift (1.015)
content = content.replace("shift_freqs = csd_freqs * (0.99 ** i)", "shift_freqs = csd_freqs * (1.015 ** i)")

# Disable updates during drawing to ensure instant render
old_loop_start = """                for i in range(num_slices):"""
new_loop_start = """                self.csd_widget.setUpdatesEnabled(False)
                for i in range(num_slices):"""
content = content.replace(old_loop_start, new_loop_start)

# Re-enable updates after loop
old_loop_end = """                        pen=pg.mkPen(color=color, width=pen_width)
                    )"""
new_loop_end = """                        pen=pg.mkPen(color=color, width=pen_width)
                    )
                self.csd_widget.setUpdatesEnabled(True)"""
content = content.replace(old_loop_end, new_loop_end)

with open("analysis_ui.py", "w") as f:
    f.write(content)
