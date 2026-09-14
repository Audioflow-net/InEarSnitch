import sys

with open('main.py', 'r') as f:
    content = f.read()

# 1. Update toggle_live_seal to create the line
old_on = """                self.rta_target_region.setZValue(-10)
                target_plot.addItem(self.rta_target_region)"""

new_on = """                self.rta_target_region.setZValue(-10)
                target_plot.addItem(self.rta_target_region)
            
            if not hasattr(self, 'rta_peak_line') or self.rta_peak_line is None:
                self.rta_peak_line = pg.InfiniteLine(angle=90, movable=False)
                self.rta_peak_line.setZValue(20)
                target_plot.addItem(self.rta_peak_line)
            self.rta_peak_line.hide()"""

content = content.replace(old_on, new_on)


# 2. Update toggle_live_seal off to remove the line
old_off = """                    target = self.page_ana.plot_widget if hasattr(self, 'page_ana') else self.plot_widget
                    target.removeItem(self.rta_target_region)
                except Exception:
                    pass
                self.rta_target_region = None"""

new_off = """                    target = self.page_ana.plot_widget if hasattr(self, 'page_ana') else self.plot_widget
                    target.removeItem(self.rta_target_region)
                except Exception:
                    pass
                self.rta_target_region = None
                
            if hasattr(self, 'rta_peak_line') and self.rta_peak_line is not None:
                try:
                    target = self.page_ana.plot_widget if hasattr(self, 'page_ana') else self.plot_widget
                    target.removeItem(self.rta_peak_line)
                except Exception:
                    pass
                self.rta_peak_line = None"""

content = content.replace(old_off, new_off)


# 3. Update update_live_rta to hide the line if silence
old_silence = """                # Signal dropped by > 15dB compared to recent max. It was pulled out.
                seal_html = "<span style='color: #a8a29e; font-weight: bold;'>IEM Not Detected (Silence)</span>"
                depth_html = \"\""""

new_silence = """                # Signal dropped by > 15dB compared to recent max. It was pulled out.
                seal_html = "<span style='color: #a8a29e; font-weight: bold;'>IEM Not Detected (Silence)</span>"
                depth_html = \"\"
                if hasattr(self, 'rta_peak_line') and self.rta_peak_line is not None:
                    self.rta_peak_line.hide()"""

content = content.replace(old_silence, new_silence)


# 4. Update update_live_rta to move the line and color it
old_depth = """                    if peak_freq < 7000:
                        depth_html = "<span style='color: #eab308; font-weight: bold;'>Push Deeper (Peak: {:.1f}kHz)</span>".format(peak_freq/1000)
                    elif peak_freq > 8600:
                        depth_html = "<span style='color: #eab308; font-weight: bold;'>Pull Out Slightly (Peak: {:.1f}kHz)</span>".format(peak_freq/1000)
                    else:
                        depth_html = "<span style='color: #10b981; font-weight: bold;'>Depth OK ({:.1f}kHz)</span>".format(peak_freq/1000)"""

new_depth = """                    if hasattr(self, 'rta_peak_line') and self.rta_peak_line is not None:
                        import pyqtgraph as pg
                        import numpy as np
                        self.rta_peak_line.setValue(np.log10(peak_freq))
                        if peak_freq < 7000 or peak_freq > 8600:
                            self.rta_peak_line.setPen(pg.mkPen('#eab308', width=4))
                        else:
                            self.rta_peak_line.setPen(pg.mkPen('#10b981', width=4))
                        self.rta_peak_line.show()

                    if peak_freq < 7000:
                        depth_html = "<span style='color: #eab308; font-weight: bold;'>Push Deeper (Peak: {:.1f}kHz)</span>".format(peak_freq/1000)
                    elif peak_freq > 8600:
                        depth_html = "<span style='color: #eab308; font-weight: bold;'>Pull Out Slightly (Peak: {:.1f}kHz)</span>".format(peak_freq/1000)
                    else:
                        depth_html = "<span style='color: #10b981; font-weight: bold;'>Depth OK ({:.1f}kHz)</span>".format(peak_freq/1000)"""

content = content.replace(old_depth, new_depth)

# 5. Handle "else" for mask_treble
old_notreble = """                else:
                    depth_html = \"\""""

new_notreble = """                else:
                    depth_html = \"\"
                    if hasattr(self, 'rta_peak_line') and self.rta_peak_line is not None:
                        self.rta_peak_line.hide()"""

content = content.replace(old_notreble, new_notreble)

with open('main.py', 'w') as f:
    f.write(content)
