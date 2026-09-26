import re

with open("main.py", "r") as f:
    content = f.read()

old_filter = """    def eventFilter(self, obj, event):
        if obj == self.lineEdit():
            if event.type() == QEvent.MouseButtonPress:
                if self.lineEdit().text():
                    self._last_valid_text = self.lineEdit().text()
                self.lineEdit().clear()
            elif event.type() == QEvent.MouseButtonRelease:
                self.completer().setCompletionPrefix("")
                self.completer().complete()
            elif event.type() == QEvent.FocusOut:
                # Use a singleShot to check after all other events (like popup closing) have resolved
                QTimer.singleShot(0, self._check_restore)
        return super().eventFilter(obj, event)
        
    def _check_restore(self):
        # If popup is still open (e.g. clicking its scrollbar), do not restore yet
        if self.completer().popup() and self.completer().popup().isVisible():
            return
        # If they clicked away and left it empty, restore the old text
        if not self.lineEdit().text():
            self.lineEdit().setText(self._last_valid_text)
            idx = self.findText(self._last_valid_text)
            if idx >= 0:
                self.setCurrentIndex(idx)"""

new_filter = """    def eventFilter(self, obj, event):
        if obj == self.lineEdit():
            if event.type() == QEvent.MouseButtonPress:
                if self.lineEdit().text():
                    self._last_valid_text = self.lineEdit().text()
                self.lineEdit().clear()
            elif event.type() == QEvent.MouseButtonRelease:
                self.completer().setCompletionPrefix("")
                self.completer().complete()
            elif event.type() == QEvent.KeyPress:
                # If they press Escape, or Return/Enter when empty, restore it immediately
                if event.key() == Qt.Key_Escape or (event.key() in (Qt.Key_Return, Qt.Key_Enter) and not self.lineEdit().text()):
                    self._do_restore()
                    if event.key() == Qt.Key_Escape and self.completer().popup():
                        self.completer().popup().hide()
            elif event.type() == QEvent.FocusOut:
                QTimer.singleShot(100, self._check_restore)
        return super().eventFilter(obj, event)
        
    def _check_restore(self):
        # If the line edit regained focus (e.g. returning from popup scrollbar), don't restore yet
        if self.lineEdit().hasFocus():
            return
        # If popup is still fully visible and active, wait
        if self.completer().popup() and self.completer().popup().isVisible() and self.completer().popup().hasFocus():
            return
            
        self._do_restore()

    def _do_restore(self):
        if not self.lineEdit().text() and self._last_valid_text:
            self.lineEdit().setText(self._last_valid_text)
            idx = self.findText(self._last_valid_text)
            if idx >= 0:
                self.setCurrentIndex(idx)"""

content = content.replace(old_filter, new_filter)

with open("main.py", "w") as f:
    f.write(content)
    
with open("analysis_ui.py", "r") as f:
    content_ana = f.read()
    content_ana = content_ana.replace(old_filter, new_filter)
with open("analysis_ui.py", "w") as f:
    f.write(content_ana)
