import re

with open("history_ui.py", "r") as f:
    content = f.read()

# Create a small event filter for the search bar
filter_code = """        self.search_bar.setStyleSheet(f"background-color: {bg_hover}; color: {fg}; border: 1px solid {border}; padding: 6px; border-radius: 4px;")
        
        # Add ESC key handling to drop focus and clear
        from PySide6.QtCore import QObject, QEvent, Qt
        class SearchBarFilter(QObject):
            def eventFilter(self, obj, event):
                if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Escape:
                    obj.clear()
                    obj.clearFocus()
                    return True
                return super().eventFilter(obj, event)
        self._search_filter = SearchBarFilter(self.search_bar)
        self.search_bar.installEventFilter(self._search_filter)
        
        self.search_bar.textChanged.connect(self.filter_history)"""

content = content.replace('        self.search_bar.setStyleSheet(f"background-color: {bg_hover}; color: {fg}; border: 1px solid {border}; padding: 6px; border-radius: 4px;")\n        self.search_bar.textChanged.connect(self.filter_history)', filter_code)

with open("history_ui.py", "w") as f:
    f.write(content)
