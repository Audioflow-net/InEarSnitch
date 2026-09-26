import re

with open("main.py", "r") as f:
    content = f.read()

old_logic = """                        if event.type() == QtCore.QEvent.MouseButtonRelease:
                            # Clear text and show popup on click
                            obj.clear()
                            parent = obj.parent()
                            if hasattr(parent, "showPopup"):
                                QtCore.QTimer.singleShot(0, parent.showPopup)
                        elif event.type() == QtCore.QEvent.FocusOut:"""

new_logic = """                        if event.type() == QtCore.QEvent.MouseButtonRelease:
                            # Clear text and show popup on click
                            obj.clear()
                            parent = obj.parent()
                            if hasattr(parent, "showPopup"):
                                QtCore.QTimer.singleShot(0, parent.showPopup)
                                QtCore.QTimer.singleShot(10, obj.setFocus)
                        elif event.type() == QtCore.QEvent.FocusOut:"""

content = content.replace(old_logic, new_logic)

with open("main.py", "w") as f:
    f.write(content)
