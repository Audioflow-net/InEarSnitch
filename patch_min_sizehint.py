import re

with open("analysis_ui.py", "r") as f:
    content = f.read()

# Replace StableTabWidget class
stable_class_new = """class StableTabWidget(QTabWidget):
    def sizeHint(self):
        from PySide6.QtCore import QSize
        hint = super().sizeHint()
        return QSize(345, hint.height())
        
    def minimumSizeHint(self):
        from PySide6.QtCore import QSize
        hint = super().minimumSizeHint()
        return QSize(345, hint.height())

class AnalysisWidget(QWidget):"""

content = re.sub(r"class StableTabWidget\(QTabWidget\):.*?class AnalysisWidget\(QWidget\):", stable_class_new, content, flags=re.DOTALL)

with open("analysis_ui.py", "w") as f:
    f.write(content)
