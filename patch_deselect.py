import re

with open("main.py", "r") as f:
    content = f.read()

# Replace all occurrences of QTimer.singleShot(0, self.lineEdit().deselect)
# with a more robust lambda that sets cursor position.
old_deselect = "QTimer.singleShot(0, self.lineEdit().deselect)"
new_deselect = "QTimer.singleShot(50, lambda: self.lineEdit().setCursorPosition(0))"

content = content.replace(old_deselect, new_deselect)

# Also fix the initial click behavior. The user previously wanted the text to clear on click.
# The subagent changed it to selectAll. Let's change it back to clear() so it doesn't look blue when they just click!
old_click = """            if event.type() == QEvent.MouseButtonPress:
                if self.lineEdit().text():
                    self._last_valid_text = self.lineEdit().text()
                # Delay selectAll slightly to override default selection behavior
                QTimer.singleShot(0, self.lineEdit().selectAll)"""

new_click = """            if event.type() == QEvent.MouseButtonPress:
                if self.lineEdit().text():
                    self._last_valid_text = self.lineEdit().text()
                self.lineEdit().clear()"""

content = content.replace(old_click, new_click)

# Also fix showPopup which was changed to selectAll
old_popup = """    def showPopup(self):
        if self.lineEdit().text():
            self._last_valid_text = self.lineEdit().text()
        self.lineEdit().selectAll()"""

new_popup = """    def showPopup(self):
        if self.lineEdit().text():
            self._last_valid_text = self.lineEdit().text()
        self.lineEdit().clear()"""

content = content.replace(old_popup, new_popup)

with open("main.py", "w") as f:
    f.write(content)

with open("analysis_ui.py", "r") as f:
    content_ana = f.read()
    content_ana = content_ana.replace(old_deselect, new_deselect)
    content_ana = content_ana.replace(old_click, new_click)
    content_ana = content_ana.replace(old_popup, new_popup)
with open("analysis_ui.py", "w") as f:
    f.write(content_ana)
