import re

with open('analysis_ui.py', 'r') as f:
    content = f.read()

# We need to manually position the watermarks in the resizeEvent of AnalysisWidget
# But wait, AnalysisWidget doesn't have the resizeEvent for the plot widgets.
# We can just add an event filter!

event_filter_class = """
class OverlayFilter(QObject):
    def __init__(self, overlay_widget, parent=None):
        super().__init__(parent)
        self.overlay_widget = overlay_widget

    def eventFilter(self, obj, event):
        if event.type() == event.Type.Resize:
            # Center the overlay widget
            w = obj.width()
            h = obj.height()
            ow = self.overlay_widget.width()
            oh = self.overlay_widget.height()
            self.overlay_widget.move((w - ow) // 2, (h - oh) // 2)
        return False
"""

# Let's inject this class at the top of the file
import_target = "class AutoWrapLabel(QLabel):"
content = content.replace(import_target, event_filter_class + "\n" + import_target)

# Now, remove the QVBoxLayout that was centering them, and apply the event filter
thd_target = """        lay_thd = QVBoxLayout(self.thd_widget)
        lay_thd.addWidget(self.watermark_thd, 0, Qt.AlignCenter)"""

thd_new = """        self.thd_filter = OverlayFilter(self.watermark_thd, self.thd_widget)
        self.thd_widget.installEventFilter(self.thd_filter)
        self.watermark_thd.raise_()"""
content = content.replace(thd_target, thd_new)

csd_target = """        lay_csd = QVBoxLayout(self.csd_widget)
        lay_csd.addWidget(self.watermark_csd, 0, Qt.AlignCenter)"""

csd_new = """        self.csd_filter = OverlayFilter(self.watermark_csd, self.csd_widget)
        self.csd_widget.installEventFilter(self.csd_filter)
        self.watermark_csd.raise_()"""
content = content.replace(csd_target, csd_new)

with open('analysis_ui.py', 'w') as f:
    f.write(content)
print("Patched!")
