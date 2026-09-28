import re

with open('analysis_ui.py', 'r') as f:
    content = f.read()

# 1. Patch THD watermark
thd_target = """                if active_hohd is not None:
                    self.hohd_line.setData(thd_freqs, active_hohd)
            else:
                self.hohd_line.hide()"""

thd_replacement = """                if active_hohd is not None:
                    self.hohd_line.setData(thd_freqs, active_hohd)
            else:
                self.hohd_line.hide()
                
            poor_l = (thd_l is not None and is_poor_snr_l)
            poor_r = (thd_r is not None and is_poor_snr_r)
            if poor_l or poor_r:
                watermark = pg.TextItem(html='<div style="text-align: center;"><span style="color: rgba(255, 60, 60, 200); font-size: 24pt; font-weight: bold; background-color: rgba(0,0,0,150); padding: 5px; border-radius: 4px;">⚠️ NOISE CORRUPTED</span></div>', anchor=(0.5, 0.5))
                watermark.setPos(2.7, 2.5)
                watermark.setZValue(100)
                self.thd_widget.addItem(watermark)"""

content = content.replace(thd_target, thd_replacement)


# 2. Patch CSD coloring and watermark
csd_target = """                try:
                    base_rgb = theme.get_color('curve_right_rgb') if is_right else theme.get_color('curve_left_rgb')
                except Exception:
                    base_rgb = (255, 0, 85) if is_right else (0, 255, 255)"""

csd_replacement = """                try:
                    base_rgb = theme.get_color('curve_right_rgb') if is_right else theme.get_color('curve_left_rgb')
                except Exception:
                    base_rgb = (255, 0, 85) if is_right else (0, 255, 255)
                    
                snr_val = getattr(self, '_snr_r' if is_right else '_snr_l', None)
                is_poor_snr = snr_val is not None and snr_val < 75.0
                if is_poor_snr:
                    base_rgb = (100, 100, 105) # Gray scale for corrupted"""

content = content.replace(csd_target, csd_replacement)

csd_target_2 = """                    self.csd_widget.plot(
                        shift_freqs, 
                        shift_mag, 
                        pen=pg.mkPen(pen_color, width=1.5),
                        fillLevel=-100, 
                        brush=fill_brush,
                        name=f"CSD_{'R' if is_right else 'L'}_{i}" if i==0 else None
                    )"""

csd_replacement_2 = """                    self.csd_widget.plot(
                        shift_freqs, 
                        shift_mag, 
                        pen=pg.mkPen(pen_color, width=1.5),
                        fillLevel=-100, 
                        brush=fill_brush,
                        name=f"CSD_{'R' if is_right else 'L'}_{i}" if i==0 else None
                    )
                    
                if is_poor_snr:
                    watermark = pg.TextItem(html='<div style="text-align: center;"><span style="color: rgba(255, 60, 60, 200); font-size: 24pt; font-weight: bold; background-color: rgba(0,0,0,150); padding: 5px; border-radius: 4px;">⚠️ NOISE CORRUPTED</span></div>', anchor=(0.5, 0.5))
                    watermark.setPos(2.7, max_peak - 15)
                    watermark.setZValue(100)
                    self.csd_widget.addItem(watermark)"""
                    
content = content.replace(csd_target_2, csd_replacement_2)

with open('analysis_ui.py', 'w') as f:
    f.write(content)
print("Patched!")
