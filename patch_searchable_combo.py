import re

with open("main.py", "r") as f:
    content = f.read()

# 1. Define the custom class at the top of main.py
custom_combo_class = """
from PySide6.QtWidgets import QComboBox, QCompleter
from PySide6.QtCore import Qt, Signal

class SearchableComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setEditable(True)
        self.setInsertPolicy(QComboBox.NoInsert)
        self.completer().setCompletionMode(QCompleter.PopupCompletion)
        self.completer().setFilterMode(Qt.MatchContains)
        
        # When clicking into the text area, clear text and show popup
        self.lineEdit().mousePressEvent = self._handle_mouse_press
        
    def _handle_mouse_press(self, event):
        super(QComboBox, self).lineEdit().mousePressEvent(event)
        self.lineEdit().clear()
        self.showPopup()
        
class LiveSealWorker(QThread):
"""
content = content.replace("class LiveSealWorker(QThread):", custom_combo_class)

# 2. Replace QComboBox() with SearchableComboBox() for cb_meas_target and cb_meas_history
content = content.replace("self.cb_meas_target = QComboBox()", "self.cb_meas_target = SearchableComboBox()")
content = content.replace("self.cb_meas_history = QComboBox()", "self.cb_meas_history = SearchableComboBox()")

with open("main.py", "w") as f:
    f.write(content)

with open("analysis_ui.py", "r") as f:
    ana_content = f.read()

ana_class = """
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

class FreqAxisItem(pg.AxisItem):
"""
ana_content = ana_content.replace("class FreqAxisItem(pg.AxisItem):", ana_class)
ana_content = ana_content.replace("self.cb_ana_target = QComboBox()", "self.cb_ana_target = SearchableComboBox()")
ana_content = ana_content.replace("self.cb_ana_history = QComboBox()", "self.cb_ana_history = SearchableComboBox()")

with open("analysis_ui.py", "w") as f:
    f.write(ana_content)
