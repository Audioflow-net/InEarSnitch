import sys

with open('main.py', 'r') as f:
    content = f.read()

# For target
if "if self.target_freqs is not None and self.target_mags is not None:" in content:
    content = content.replace(
        "if self.target_freqs is not None and self.target_mags is not None:",
        "if self.target_freqs is not None and self.target_mags is not None and self.btn_toggle_target.isChecked():"
    )

# For history
if "if self.history_freqs_l is not None and self.history_mags_l is not None:" in content:
    content = content.replace(
        "if self.history_freqs_l is not None and self.history_mags_l is not None:",
        "if self.history_freqs_l is not None and self.history_mags_l is not None and self.btn_toggle_history.isChecked():"
    )
if "if self.history_freqs_r is not None and self.history_mags_r is not None:" in content:
    content = content.replace(
        "if self.history_freqs_r is not None and self.history_mags_r is not None:",
        "if self.history_freqs_r is not None and self.history_mags_r is not None and self.btn_toggle_history.isChecked():"
    )

with open('main.py', 'w') as f:
    f.write(content)
