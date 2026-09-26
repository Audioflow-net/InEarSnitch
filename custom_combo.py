from PySide6.QtWidgets import QComboBox, QCompleter
from PySide6.QtCore import Qt, Signal

class SearchableComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setEditable(True)
        self.setInsertPolicy(QComboBox.NoInsert)
        self.completer().setCompletionMode(QCompleter.PopupCompletion)
        self.completer().setFilterMode(Qt.MatchContains)
        
        self.lineEdit().mousePressEvent = self._handle_mouse_press
        
    def _handle_mouse_press(self, event):
        super(QComboBox, self).lineEdit().mousePressEvent(event)
        self.lineEdit().clear()
        self.showPopup()
