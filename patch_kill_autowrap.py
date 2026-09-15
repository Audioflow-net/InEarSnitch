import re

with open("analysis_ui.py", "r") as f:
    content = f.read()

# Replace AutoWrapLabel class completely
old_autowrap = """class AutoWrapLabel(QLabel):
    def __init__(self, text=""):
        super().__init__(text)
        self.setWordWrap(True)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        w = self.width()
        h = self.heightForWidth(w)
        if h > self.minimumHeight():
            self.setMinimumHeight(h)"""

new_autowrap = """class AutoWrapLabel(QLabel):
    def __init__(self, text=""):
        super().__init__(text)
        self.setWordWrap(True)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Minimum)
        
    def minimumSizeHint(self):
        from PySide6.QtCore import QSize
        # Force a small minimum width so it can be squished, but calculate height based on 320px
        # 320 is roughly the width of the right pane minus scrollbar and margins.
        h = self.heightForWidth(320)
        return QSize(10, h)
        
    def sizeHint(self):
        from PySide6.QtCore import QSize
        h = self.heightForWidth(320)
        return QSize(320, h)"""

content = content.replace(old_autowrap, new_autowrap)

with open("analysis_ui.py", "w") as f:
    f.write(content)
