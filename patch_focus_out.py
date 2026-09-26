import re

with open("main.py", "r") as f:
    content = f.read()

old_filter = """                class FocusSelectFilter(QtCore.QObject):
                    def eventFilter(self, obj, event):
                        if event.type() == QtCore.QEvent.MouseButtonPress:
                            # Clear text and show popup on click
                            obj.clear()
                            parent = obj.parent()
                            if hasattr(parent, "showPopup"):
                                QtCore.QTimer.singleShot(0, parent.showPopup)
                        return super().eventFilter(obj, event)"""

new_filter = """                class FocusSelectFilter(QtCore.QObject):
                    def eventFilter(self, obj, event):
                        if event.type() == QtCore.QEvent.MouseButtonPress:
                            # Clear text and show popup on click
                            obj.clear()
                            parent = obj.parent()
                            if hasattr(parent, "showPopup"):
                                QtCore.QTimer.singleShot(0, parent.showPopup)
                        elif event.type() == QtCore.QEvent.FocusOut:
                            parent = obj.parent()
                            if hasattr(parent, "currentText"):
                                obj.setText(parent.currentText())
                        return super().eventFilter(obj, event)"""

content = content.replace(old_filter, new_filter)

with open("main.py", "w") as f:
    f.write(content)
