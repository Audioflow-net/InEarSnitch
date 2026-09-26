import re

with open("main.py", "r") as f:
    content = f.read()

# Remove the messy event filter from load_targets completely!
old_event_filter = """            # Styling the line edit inside the combobox
            line_edit = b.lineEdit()
            if line_edit:
                line_edit.setStyleSheet("background: transparent; color: white; border: none; padding: 2px;")
                
                # Allow normal click-to-open behavior without eating events
                from PySide6 import QtCore
                class FocusSelectFilter(QtCore.QObject):
                    def eventFilter(self, obj, event):
                        if event.type() == QtCore.QEvent.MouseButtonRelease:
                            parent = obj.parent()
                            # Save the current valid text BEFORE clearing
                            if not hasattr(self, 'saved_text') or obj.text():
                                self.saved_text = obj.text()
                            
                            # Clear text and show popup on click
                            obj.clear()
                            if hasattr(parent, "completer") and parent.completer():
                                # Use completer popup instead of combobox popup so typing works natively
                                QtCore.QTimer.singleShot(0, parent.completer().complete)
                        elif event.type() == QtCore.QEvent.FocusOut:
                            parent = obj.parent()
                            # Restore text if they didn't pick anything
                            if not obj.text() and hasattr(self, 'saved_text'):
                                obj.setText(self.saved_text)
                                # Ensure the combobox model matches the restored text
                                idx = parent.findText(self.saved_text)
                                if idx >= 0:
                                    parent.setCurrentIndex(idx)
                        return super().eventFilter(obj, event)
                
                b._focus_filter = FocusSelectFilter(b)
                line_edit.installEventFilter(b._focus_filter)
                # Update placeholder text manually if empty
                if b.count() > 0 and b.currentIndex() == -1:
                    line_edit.setText(b.itemText(0))"""

new_event_filter = """            # Styling the line edit inside the combobox
            line_edit = b.lineEdit()
            if line_edit:
                line_edit.setStyleSheet("background: transparent; color: white; border: none; padding: 2px;")
                # The SearchableComboBox class handles its own events now."""

content = content.replace(old_event_filter, new_event_filter)

# Now redefine SearchableComboBox at the top of main.py
old_combo_def = """class SearchableComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setEditable(True)
        self.setInsertPolicy(QComboBox.NoInsert)
        self.completer().setCompletionMode(QCompleter.PopupCompletion)
        self.completer().setFilterMode(Qt.MatchContains)
        
        # Event handling is done via eventFilter in load_targets"""

new_combo_def = """from PySide6.QtGui import QMouseEvent
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
        
        # We hook into the line edit's mouse press event
        self.lineEdit().installEventFilter(self)
        
    def _on_index_changed(self, idx):
        if idx >= 0:
            self._last_valid_text = self.itemText(idx)
            
    def eventFilter(self, obj, event):
        if obj == self.lineEdit():
            if event.type() == QtCore.QEvent.MouseButtonPress:
                # Store text and clear it so completer shows all options
                if self.lineEdit().text():
                    self._last_valid_text = self.lineEdit().text()
                self.lineEdit().clear()
                # Use QTimer to open the popup AFTER the mouse click is fully processed
                QtCore.QTimer.singleShot(50, self.showPopup)
                return True # We handled the click
                
            elif event.type() == QtCore.QEvent.FocusOut:
                # If they clicked away and left it empty, restore the old text
                if not self.lineEdit().text():
                    self.lineEdit().setText(self._last_valid_text)
                    idx = self.findText(self._last_valid_text)
                    if idx >= 0:
                        self.setCurrentIndex(idx)
        return super().eventFilter(obj, event)
        
    # We override showPopup to force focus back to the line edit!
    def showPopup(self):
        super().showPopup()
        self.lineEdit().setFocus()"""

content = content.replace(old_combo_def, new_combo_def)

with open("main.py", "w") as f:
    f.write(content)
