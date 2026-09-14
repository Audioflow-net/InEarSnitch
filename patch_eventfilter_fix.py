import re

with open("main.py", "r") as f:
    code = f.read()

old_code = """                # Also prevent closing if it's a click inside a popup/dialog (QMessageBox)
                # If obj is a window and not self, it might be a dialog
                is_dialog = obj.isWindow() and obj != self
                
                if not in_panel and not in_btn and not is_dialog:"""

new_code = """                # Also prevent closing if it's a click inside a popup/dialog (QMessageBox)
                is_dialog = False
                if hasattr(obj, 'isWindow'):
                    is_dialog = obj.isWindow() and obj != self
                
                if not in_panel and not in_btn and not is_dialog:"""

code = code.replace(old_code, new_code)

with open("main.py", "w") as f:
    f.write(code)

print("EventFilter patched.")
