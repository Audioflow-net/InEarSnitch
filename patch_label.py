import re

with open("analysis_ui.py", "r") as f:
    content = f.read()

# Add the AutoWrapLabel class at the top
autowrap_class = """class AutoWrapLabel(QLabel):
    def __init__(self, text=""):
        super().__init__(text)
        self.setWordWrap(True)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Ensure layout recalculates height properly in QScrollArea
        self.setMinimumHeight(self.heightForWidth(self.width()))

class AnalysisWidget(QWidget):"""

content = content.replace("class AnalysisWidget(QWidget):", autowrap_class)

# Replace the label creation for desc in render_diagnostics
content = content.replace(
    "desc = QLabel(item.get('desc', ''))\n            desc.setWordWrap(True)",
    "desc = AutoWrapLabel(item.get('desc', ''))"
)

with open("analysis_ui.py", "w") as f:
    f.write(content)
