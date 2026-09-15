import re

with open("analysis_ui.py", "r") as f:
    content = f.read()

old_resize = """    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Ensure layout recalculates height properly in QScrollArea
        self.setMinimumHeight(self.heightForWidth(self.width()))"""

new_resize = """    def resizeEvent(self, event):
        super().resizeEvent(event)
        w = event.size().width()
        h = self.heightForWidth(w)
        if self.minimumHeight() != h:
            self.setMinimumHeight(h)"""

content = content.replace(old_resize, new_resize)

with open("analysis_ui.py", "w") as f:
    f.write(content)
