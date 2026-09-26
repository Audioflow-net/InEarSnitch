import re

with open("main.py", "r") as f:
    content = f.read()

old_filter = """                        if event.type() == QtCore.QEvent.MouseButtonPress:
                            # Clear text and show popup on click
                            obj.clear()
                            parent = obj.parent()
                            if hasattr(parent, "showPopup"):
                                QtCore.QTimer.singleShot(0, parent.showPopup)
                        elif event.type() == QtCore.QEvent.FocusOut:"""

new_filter = """                        if event.type() == QtCore.QEvent.MouseButtonRelease:
                            # Clear text and show popup on click
                            obj.clear()
                            parent = obj.parent()
                            if hasattr(parent, "showPopup"):
                                QtCore.QTimer.singleShot(0, parent.showPopup)
                        elif event.type() == QtCore.QEvent.FocusOut:"""

content = content.replace(old_filter, new_filter)

# Also add setMaxVisibleItems
old_edit = """            # Make combobox searchable
            b.setEditable(True)"""

new_edit = """            # Make combobox searchable
            b.setEditable(True)
            b.setMaxVisibleItems(25)"""

content = content.replace(old_edit, new_edit)

with open("main.py", "w") as f:
    f.write(content)
