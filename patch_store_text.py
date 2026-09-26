import re

with open("main.py", "r") as f:
    content = f.read()

old_filter = """                class FocusSelectFilter(QtCore.QObject):
                    def eventFilter(self, obj, event):
                        if event.type() == QtCore.QEvent.MouseButtonRelease:
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
                                obj.setText(parent.currentText())
                        return super().eventFilter(obj, event)"""

new_filter = """                class FocusSelectFilter(QtCore.QObject):
                    def eventFilter(self, obj, event):
                        if event.type() == QtCore.QEvent.MouseButtonRelease:
                            parent = obj.parent()
                            # Save the current valid text BEFORE clearing
                            if not hasattr(self, 'saved_text') or obj.text():
                                self.saved_text = obj.text()
                            
                            # Clear text and show popup on click
                            obj.clear()
                            if hasattr(parent, "showPopup"):
                                QtCore.QTimer.singleShot(0, parent.showPopup)
                                # Force focus back to line edit so typing works
                                QtCore.QTimer.singleShot(50, obj.setFocus)
                        elif event.type() == QtCore.QEvent.FocusOut:
                            parent = obj.parent()
                            # Restore text if they didn't pick anything
                            if not obj.text() and hasattr(self, 'saved_text'):
                                obj.setText(self.saved_text)
                                # Ensure the combobox model matches the restored text
                                idx = parent.findText(self.saved_text)
                                if idx >= 0:
                                    parent.setCurrentIndex(idx)
                        return super().eventFilter(obj, event)"""

content = content.replace(old_filter, new_filter)

with open("main.py", "w") as f:
    f.write(content)
