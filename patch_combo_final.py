import re

with open("main.py", "r") as f:
    content = f.read()

old_logic = """                        if event.type() == QtCore.QEvent.MouseButtonRelease:
                            # Clear text and show popup on click
                            obj.clear()
                            parent = obj.parent()
                            if hasattr(parent, "completer") and parent.completer():
                                parent.completer().complete()
                        elif event.type() == QtCore.QEvent.FocusOut:
                            parent = obj.parent()
                            if hasattr(parent, "currentText"):
                                obj.setText(parent.currentText())"""

new_logic = """                        if event.type() == QtCore.QEvent.MouseButtonRelease:
                            # Clear text and show popup on click
                            obj.clear()
                            parent = obj.parent()
                            if hasattr(parent, "showPopup"):
                                QtCore.QTimer.singleShot(0, parent.showPopup)
                                # Force focus back to line edit so typing works
                                QtCore.QTimer.singleShot(50, obj.setFocus)
                        elif event.type() == QtCore.QEvent.FocusOut:
                            parent = obj.parent()
                            # Restore text if they didn't pick anything
                            if hasattr(parent, "currentText") and not obj.text():
                                obj.setText(parent.currentText())"""

content = content.replace(old_logic, new_logic)

with open("main.py", "w") as f:
    f.write(content)
