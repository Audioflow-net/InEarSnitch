import re

with open('analysis_ui.py', 'r') as f:
    content = f.read()

# 1. Update OverlayFilter class
target_class = """class OverlayFilter(QObject):
    def __init__(self, overlay_widget, parent=None):
        super().__init__(parent)
        self.overlay_widget = overlay_widget

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Resize:
            w = obj.width()
            h = obj.height()
            ow = self.overlay_widget.width()
            oh = self.overlay_widget.height()
            
            # THD widget is shorter because of the STRESS TEST button below it.
            # We add a ~20px offset to THD so its watermark visually aligns with CSD.
            y_offset = 20 if hasattr(self.overlay_widget.parent(), 'hohd_line') else 0
            
            self.overlay_widget.move((w - ow) // 2, (h - oh) // 2 + y_offset)
        return False"""

replacement_class = """class OverlayFilter(QObject):
    def __init__(self, overlay_widget, y_offset=0, parent=None):
        super().__init__(parent)
        self.overlay_widget = overlay_widget
        self.y_offset = y_offset

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Resize:
            w = obj.width()
            h = obj.height()
            ow = self.overlay_widget.width()
            oh = self.overlay_widget.height()
            self.overlay_widget.move((w - ow) // 2, (h - oh) // 2 + self.y_offset)
        return False"""
content = content.replace(target_class, replacement_class)

# 2. Update THD Filter instantiation
target_thd_filter = """        self.thd_filter = OverlayFilter(self.watermark_thd, self.thd_widget)"""
replacement_thd_filter = """        self.thd_filter = OverlayFilter(self.watermark_thd, y_offset=20, parent=self.thd_widget)"""
content = content.replace(target_thd_filter, replacement_thd_filter)

# 3. Update CSD Filter instantiation
target_csd_filter = """        self.csd_filter = OverlayFilter(self.watermark_csd, self.csd_widget)"""
replacement_csd_filter = """        self.csd_filter = OverlayFilter(self.watermark_csd, y_offset=0, parent=self.csd_widget)"""
content = content.replace(target_csd_filter, replacement_csd_filter)

# 4. Fix size illusion by enforcing absolute size
target_thd_lbl = """        self.watermark_thd.setStyleSheet("color: rgba(255, 60, 60, 200); font-size: 24pt; font-weight: bold; background-color: rgba(0,0,0,150); padding: 8px 16px; border-radius: 6px;")
        self.watermark_thd.setAlignment(Qt.AlignCenter)
        self.watermark_thd.hide()"""

replacement_thd_lbl = """        self.watermark_thd.setStyleSheet("color: rgba(255, 60, 60, 200); font-size: 24pt; font-weight: bold; background-color: rgba(0,0,0,150); border-radius: 6px;")
        self.watermark_thd.setFixedSize(500, 60)
        self.watermark_thd.setAlignment(Qt.AlignCenter)
        self.watermark_thd.hide()"""
content = content.replace(target_thd_lbl, replacement_thd_lbl)

target_csd_lbl = """        self.watermark_csd.setStyleSheet("color: rgba(255, 60, 60, 200); font-size: 24pt; font-weight: bold; background-color: rgba(0,0,0,150); padding: 8px 16px; border-radius: 6px;")
        self.watermark_csd.setAlignment(Qt.AlignCenter)
        self.watermark_csd.hide()"""

replacement_csd_lbl = """        self.watermark_csd.setStyleSheet("color: rgba(255, 60, 60, 200); font-size: 24pt; font-weight: bold; background-color: rgba(0,0,0,150); border-radius: 6px;")
        self.watermark_csd.setFixedSize(500, 60)
        self.watermark_csd.setAlignment(Qt.AlignCenter)
        self.watermark_csd.hide()"""
content = content.replace(target_csd_lbl, replacement_csd_lbl)

with open('analysis_ui.py', 'w') as f:
    f.write(content)
print("Fix applied successfully!")
