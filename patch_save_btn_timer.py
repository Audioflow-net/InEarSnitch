import re

with open("main.py", "r") as f:
    code = f.read()

pattern = r'''            # Button flash animation
            orig_text = self\.btn_save_db\.text\(\)
            orig_style = self\.btn_save_db\.styleSheet\(\)
            self\.btn_save_db\.setText\("Saved"\)
            self\.btn_save_db\.setStyleSheet\("QPushButton \{ background-color: #10b981; color: white; font-weight: bold; padding: 6px; border-radius: 4px; border: 1px solid #059669; \}"\)
            
            # Using QTimer to restore
            from PyQt5\.QtCore import QTimer
            QTimer\.singleShot\(1500, lambda: self\.btn_save_db\.setText\(orig_text\)\)
            QTimer\.singleShot\(1500, lambda: self\.btn_save_db\.setStyleSheet\(orig_style\)\)'''

replacement = '''            # Button flash animation
            self.btn_save_db.setText("Saved")
            self.btn_save_db.setStyleSheet("QPushButton { background-color: #10b981; color: white; font-weight: bold; padding: 6px; border-radius: 4px; border: 1px solid #059669; }")
            
            # Using QTimer to restore (hardcoded to avoid closure state bugs if clicked multiple times rapidly)
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(1500, lambda: self.btn_save_db.setText("Save"))
            QTimer.singleShot(1500, lambda: self.btn_save_db.setStyleSheet("QPushButton { background-color: #444; color: white; font-weight: bold; padding: 6px; border-radius: 4px; border: 1px solid #555; } QPushButton:disabled { background-color: #222; color: #555; border: 1px solid #333; } QPushButton:hover { background-color: #555; }"))'''

code = re.sub(pattern, replacement, code)

with open("main.py", "w") as f:
    f.write(code)

print("Save animation fixed.")
