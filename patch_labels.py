import re

with open('analysis_ui.py', 'r') as f:
    content = f.read()

# Remove the old pg.TextItem from THD
thd_old = """            if poor_l or poor_r:
                watermark = pg.TextItem(html='<div style="text-align: center;"><span style="color: rgba(255, 60, 60, 200); font-size: 24pt; font-weight: bold; background-color: rgba(0,0,0,150); padding: 5px; border-radius: 4px;">⚠️ NOISE CORRUPTED</span></div>', anchor=(0.5, 0.5))
                watermark.setPos(2.7, 2.5)
                watermark.setZValue(100)
                self.thd_widget.addItem(watermark)"""

thd_new = """            if poor_l or poor_r:
                if hasattr(self, 'watermark_thd'): self.watermark_thd.show()
            else:
                if hasattr(self, 'watermark_thd'): self.watermark_thd.hide()"""

content = content.replace(thd_old, thd_new)

# Remove the old pg.TextItem from CSD
csd_old = """                if is_poor_snr:
                    watermark = pg.TextItem(html='<div style="text-align: center;"><span style="color: rgba(255, 60, 60, 200); font-size: 24pt; font-weight: bold; background-color: rgba(0,0,0,150); padding: 5px; border-radius: 4px;">⚠️ NOISE CORRUPTED</span></div>', anchor=(0.5, 0.5))
                    watermark.setPos(2.7, max_peak - 15)
                    watermark.setZValue(100)
                    self.csd_widget.addItem(watermark)"""

csd_new = """            if getattr(self, '_snr_l', None) is not None and getattr(self, '_snr_l', None) < 75.0 or getattr(self, '_snr_r', None) is not None and getattr(self, '_snr_r', None) < 75.0:
                if hasattr(self, 'watermark_csd'): self.watermark_csd.show()
            else:
                if hasattr(self, 'watermark_csd'): self.watermark_csd.hide()"""
content = content.replace(csd_old, "")

# We need to insert csd_new at the end of CSD update
csd_end_target = """        # Trigger EQ update to draw the virtual curve"""
content = content.replace(csd_end_target, csd_new + "\n\n        # Trigger EQ update to draw the virtual curve")

# Now inject the creation of labels in __init__
init_target = """        self.hohd_line = self.thd_widget.plot(pen=pg.mkPen('#ef4444', width=2, style=Qt.DashLine), name="R&B (HOHD)")
        self.hohd_line.hide()
        
        thd_layout.addWidget(self.thd_widget)"""
        
init_new = """        self.hohd_line = self.thd_widget.plot(pen=pg.mkPen('#ef4444', width=2, style=Qt.DashLine), name="R&B (HOHD)")
        self.hohd_line.hide()
        
        self.watermark_thd = QLabel("⚠️ NOISE CORRUPTED", self.thd_widget)
        self.watermark_thd.setStyleSheet("color: rgba(255, 60, 60, 200); font-size: 24pt; font-weight: bold; background-color: rgba(0,0,0,150); padding: 8px 16px; border-radius: 6px;")
        self.watermark_thd.setAlignment(Qt.AlignCenter)
        self.watermark_thd.hide()
        
        lay_thd = QVBoxLayout(self.thd_widget)
        lay_thd.addWidget(self.watermark_thd, 0, Qt.AlignCenter)
        
        thd_layout.addWidget(self.thd_widget)"""
content = content.replace(init_target, init_new)

init_target_2 = """        self.csd_widget.setYRange(-60, 20)
        self.csd_widget.getViewBox().disableAutoRange()
        
        csd_layout.addWidget(self.csd_widget)"""

init_new_2 = """        self.csd_widget.setYRange(-60, 20)
        self.csd_widget.getViewBox().disableAutoRange()
        
        self.watermark_csd = QLabel("⚠️ NOISE CORRUPTED", self.csd_widget)
        self.watermark_csd.setStyleSheet("color: rgba(255, 60, 60, 200); font-size: 24pt; font-weight: bold; background-color: rgba(0,0,0,150); padding: 8px 16px; border-radius: 6px;")
        self.watermark_csd.setAlignment(Qt.AlignCenter)
        self.watermark_csd.hide()
        
        lay_csd = QVBoxLayout(self.csd_widget)
        lay_csd.addWidget(self.watermark_csd, 0, Qt.AlignCenter)
        
        csd_layout.addWidget(self.csd_widget)"""
content = content.replace(init_target_2, init_new_2)

with open('analysis_ui.py', 'w') as f:
    f.write(content)
print("Patched!")
