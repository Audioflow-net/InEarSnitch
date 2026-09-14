import re

with open("main.py", "r") as f:
    code = f.read()

old_code = """        if hasattr(self, 'current_iem_name') and hasattr(self, 'current_musician_name'):
            name_text = f"{self.current_iem_name} - {self.current_musician_name}" if self.current_iem_name else self.current_musician_name
            self.lbl_subtitle.setText(f"DIAGNOSTICS  |  {name_text}")
"""

new_code = """        if hasattr(self, 'current_iem_name') and hasattr(self, 'current_musician_name'):
            name_text = f"{self.current_iem_name} - {self.current_musician_name}" if self.current_iem_name else self.current_musician_name
            self.lbl_subtitle.setText(f"DIAGNOSTICS")
            if hasattr(self, 'lbl_active_profile'):
                self.lbl_active_profile.setText(f"Profile: {self.current_musician_name}  |  IEM: {self.current_iem_name}")
"""

code = code.replace(old_code, new_code)

with open("main.py", "w") as f:
    f.write(code)

print("Profile label updated.")
