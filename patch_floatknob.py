import sys
import re

with open('analysis_ui.py', 'r') as f:
    content = f.read()

# Replace QDial size
content = content.replace("self.dial.setFixedSize(28, 28)", "self.dial.setFixedSize(45, 45)")

# Replace QLabel with QLineEdit
old_lbl = """        self.lbl_val = QLabel()
        self.lbl_val.setAlignment(Qt.AlignCenter)
        self.lbl_val.setStyleSheet("font-size: 9px; font-weight: bold; color: #ccc; border: none; background: transparent;")
        layout.addWidget(self.lbl_val)"""

new_txt = """        self.txt_val = QLineEdit()
        self.txt_val.setAlignment(Qt.AlignCenter)
        self.txt_val.setStyleSheet("QLineEdit { font-size: 10px; font-weight: bold; color: #ccc; border: 1px solid transparent; background: transparent; padding: 0px; } QLineEdit:focus { border: 1px solid #555; background: #222; }")
        self.txt_val.setFixedWidth(50)
        self.txt_val.editingFinished.connect(self._on_txt_changed)
        layout.addWidget(self.txt_val, alignment=Qt.AlignCenter)"""

content = content.replace(old_lbl, new_txt)

# Replace setText
content = content.replace("self.lbl_val.setText(txt + self.suffix)", "self.txt_val.setText(txt + self.suffix)")

# Add _on_txt_changed method
insert_pos = content.find("def value(self):")
if insert_pos != -1:
    new_method = """    def _on_txt_changed(self):
        txt = self.txt_val.text().replace(self.suffix, '').replace(',', '.').strip()
        try:
            if 'k' in txt.lower():
                val = float(txt.lower().replace('k', '')) * 1000
            else:
                val = float(txt)
            val = max(self.min_val, min(self.max_val, val))
            self.setValue(val)
        except ValueError:
            self.setValue(self.value()) # reset to current if invalid
            
    """
    content = content[:insert_pos] + new_method + content[insert_pos:]

with open('analysis_ui.py', 'w') as f:
    f.write(content)

