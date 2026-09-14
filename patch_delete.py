import re

with open("history_ui.py", "r") as f:
    code = f.read()

pattern = r'''                # Reload
                if hasattr\(self, 'current_iem_id'\):
                    self\.load_history\(self\.current_iem_id\)'''

replacement = r'''                # Reload
                if hasattr(self, 'last_m_id'):
                    self.load_history(self.last_m_id)
                import __main__
                if hasattr(__main__, 'window'):
                    __main__.window.load_targets()'''

code = re.sub(pattern, replacement, code)

with open("history_ui.py", "w") as f:
    f.write(code)

print("Delete patched.")
