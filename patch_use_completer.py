import re

with open("main.py", "r") as f:
    content = f.read()

old_filter = """                            # Clear text and show popup on click
                            obj.clear()
                            if hasattr(parent, "showPopup"):
                                QtCore.QTimer.singleShot(0, parent.showPopup)
                                # Force focus back to line edit so typing works
                                QtCore.QTimer.singleShot(50, obj.setFocus)"""

new_filter = """                            # Clear text and show popup on click
                            obj.clear()
                            if hasattr(parent, "completer") and parent.completer():
                                # Use completer popup instead of combobox popup so typing works natively
                                QtCore.QTimer.singleShot(0, parent.completer().complete)"""

content = content.replace(old_filter, new_filter)

with open("main.py", "w") as f:
    f.write(content)
