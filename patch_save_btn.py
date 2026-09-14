import re

with open("main.py", "r") as f:
    code = f.read()

insert_point = r'(            self\.sub_lbl\.setText\("Status: Saved to Database\."\)\n            self\.sub_lbl\.setStyleSheet\("color: #00FF99; font-size: 12px;"\))'

new_code = r"""\1
            
            # Button flash animation
            orig_text = self.btn_save_db.text()
            orig_style = self.btn_save_db.styleSheet()
            self.btn_save_db.setText("Saved")
            self.btn_save_db.setStyleSheet("QPushButton { background-color: #10b981; color: white; font-weight: bold; padding: 6px; border-radius: 4px; border: 1px solid #059669; }")
            
            # Using QTimer to restore
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(1500, lambda: self.btn_save_db.setText(orig_text))
            QTimer.singleShot(1500, lambda: self.btn_save_db.setStyleSheet(orig_style))"""
            
code = re.sub(insert_point, new_code, code)

with open("main.py", "w") as f:
    f.write(code)

print("Save animation injected.")
