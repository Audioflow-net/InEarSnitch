import re

with open("analysis_ui.py", "r") as f:
    content = f.read()

# Add StableTabWidget class
stable_class = """class StableTabWidget(QTabWidget):
    def sizeHint(self):
        from PySide6.QtCore import QSize
        # Provide a stable width hint so QSplitter doesn't auto-collapse when empty
        hint = super().sizeHint()
        return QSize(345, hint.height())

class AnalysisWidget(QWidget):"""

content = content.replace("class AnalysisWidget(QWidget):", stable_class)

# Replace QTabWidget instantiation
content = content.replace(
    "self.tools_tabs = QTabWidget()\n        self.tools_tabs.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)",
    "self.tools_tabs = StableTabWidget()\n        # self.tools_tabs.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)"
)

with open("analysis_ui.py", "w") as f:
    f.write(content)
