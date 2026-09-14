import re

with open("main.py", "r") as f:
    code = f.read()

# In update_watermark, right after we determine name_text:
insert_target = r'''        if hasattr\(self, 'current_iem_name'\) and hasattr\(self, 'current_musician_name'\):
            name_text = f"\{self\.current_iem_name\} - \{self\.current_musician_name\}" if self\.current_iem_name else self\.current_musician_name
            self\.watermark_item\.setHtml'''

new_code = r"""        if hasattr(self, 'current_iem_name') and hasattr(self, 'current_musician_name'):
            name_text = f"{self.current_iem_name} - {self.current_musician_name}" if self.current_iem_name else self.current_musician_name
            if hasattr(self, 'lbl_active_profile'):
                self.lbl_active_profile.setText(f"Profile: {self.current_musician_name}  |  IEM: {self.current_iem_name}")
                self.lbl_active_profile.setStyleSheet("color: #00FF99; font-size: 13px; font-weight: bold; margin-right: 15px;")
            self.watermark_item.setHtml"""

code = re.sub(insert_target, new_code, code)

with open("main.py", "w") as f:
    f.write(code)

print("Top label injected.")
