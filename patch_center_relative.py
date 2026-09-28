with open('analysis_ui.py', 'r') as f:
    content = f.read()

target = """    def eventFilter(self, obj, event):
        if event.type() == event.Type.Resize:
            w = obj.width()
            ow = self.overlay_widget.width()
            # Fixed Y distance from the top edge so it never jumps 
            # when switching between tabs of different heights (e.g. THD has Stress Test button underneath)
            self.overlay_widget.move((w - ow) // 2, 320)
        return False"""

replacement = """    def eventFilter(self, obj, event):
        if event.type() == event.Type.Resize:
            w = obj.width()
            h = obj.height()
            ow = self.overlay_widget.width()
            oh = self.overlay_widget.height()
            
            # THD widget is shorter because of the STRESS TEST button below it.
            # We add a ~20px offset to THD so its watermark visually aligns with CSD.
            y_offset = 20 if hasattr(self.overlay_widget.parent(), 'hohd_line') else 0
            
            self.overlay_widget.move((w - ow) // 2, (h - oh) // 2 + y_offset)
        return False"""

content = content.replace(target, replacement)

with open('analysis_ui.py', 'w') as f:
    f.write(content)
print("Relative centering applied!")
