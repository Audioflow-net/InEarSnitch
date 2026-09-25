with open("analysis_ui.py", "r") as f:
    content = f.read()

card_class = """class EQPresetCardWidget(QFrame):
    def __init__(self, name, apply_callback, parent=None):
        super().__init__(parent)
        self.preset_name = name
        self.apply_callback = apply_callback
        from PySide6.QtCore import Qt
        self.setCursor(Qt.PointingHandCursor)
        
    def mousePressEvent(self, event):
        self.apply_callback(self.preset_name)
        super().mousePressEvent(event)

class AnalysisWidget(QWidget):"""

if "class EQPresetCardWidget" not in content:
    content = content.replace("class AnalysisWidget(QWidget):", card_class)

with open("analysis_ui.py", "w") as f:
    f.write(content)

