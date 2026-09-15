import re

with open("analysis_ui.py", "r") as f:
    content = f.read()

# Replace AutoWrapLabel's resizeEvent
old_resize = """    def resizeEvent(self, event):
        super().resizeEvent(event)
        w = event.size().width()
        h = self.heightForWidth(w)
        if self.minimumHeight() != h:
            self.setMinimumHeight(h)"""

new_resize = """    def resizeEvent(self, event):
        super().resizeEvent(event)
        w = self.width()
        h = self.heightForWidth(w)
        if h > self.minimumHeight():
            self.setMinimumHeight(h)"""

content = content.replace(old_resize, new_resize)

# Replace StableTabWidget's minimumSizeHint
old_min_hint = """    def minimumSizeHint(self):
        from PySide6.QtCore import QSize
        hint = super().minimumSizeHint()
        return QSize(220, hint.height())"""

new_min_hint = """    def minimumSizeHint(self):
        from PySide6.QtCore import QSize
        hint = super().minimumSizeHint()
        return QSize(220, 0)"""

content = content.replace(old_min_hint, new_min_hint)

with open("analysis_ui.py", "w") as f:
    f.write(content)
