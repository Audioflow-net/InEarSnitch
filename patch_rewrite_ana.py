import re

with open("analysis_ui.py", "r") as f:
    content = f.read()

old_combo_def = """class SearchableComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setEditable(True)
        self.setInsertPolicy(QComboBox.NoInsert)
        self.completer().setCompletionMode(QCompleter.PopupCompletion)
        self.completer().setFilterMode(Qt.MatchContains)
        
        pass"""

new_combo_def = """from PySide6.QtGui import QMouseEvent
from PySide6 import QtCore
class SearchableComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setEditable(True)
        self.setInsertPolicy(QComboBox.NoInsert)
        self.setMaxVisibleItems(25)
        
        self.completer().setCompletionMode(QCompleter.PopupCompletion)
        self.completer().setFilterMode(Qt.MatchContains)
        
        self._last_valid_text = ""
        self.currentIndexChanged.connect(self._on_index_changed)
        
        self.lineEdit().installEventFilter(self)
        
    def _on_index_changed(self, idx):
        if idx >= 0:
            self._last_valid_text = self.itemText(idx)
            
    def eventFilter(self, obj, event):
        if obj == self.lineEdit():
            if event.type() == QtCore.QEvent.MouseButtonPress:
                if self.lineEdit().text():
                    self._last_valid_text = self.lineEdit().text()
                self.lineEdit().clear()
                QtCore.QTimer.singleShot(50, self.showPopup)
                return True
                
            elif event.type() == QtCore.QEvent.FocusOut:
                if not self.lineEdit().text():
                    self.lineEdit().setText(self._last_valid_text)
                    idx = self.findText(self._last_valid_text)
                    if idx >= 0:
                        self.setCurrentIndex(idx)
        return super().eventFilter(obj, event)
        
    def showPopup(self):
        super().showPopup()
        self.lineEdit().setFocus()"""

content = content.replace(old_combo_def, new_combo_def)

with open("analysis_ui.py", "w") as f:
    f.write(content)
