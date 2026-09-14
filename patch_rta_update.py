import sys

with open('main.py', 'r') as f:
    content = f.read()

# Make update_live_rta respect the checkbox
old_update = """                        if peak_freq < 7000 or peak_freq > 8600:
                            self.rta_peak_line.setPen(pg.mkPen('#eab308', width=4))
                        else:
                            self.rta_peak_line.setPen(pg.mkPen('#10b981', width=4))
                        self.rta_peak_line.show()"""

new_update = """                        if peak_freq < 7000 or peak_freq > 8600:
                            self.rta_peak_line.setPen(pg.mkPen('#eab308', width=4))
                        else:
                            self.rta_peak_line.setPen(pg.mkPen('#10b981', width=4))
                        if hasattr(self, 'chk_rta_helper') and self.chk_rta_helper.isChecked():
                            self.rta_peak_line.show()"""

content = content.replace(old_update, new_update)

old_big_lbl = """            if depth_html or seal_html:
                # Make the text responsive based on viewbox width
                width = rect.width()
                if width < 300:
                    font_size = "18px"
                    sep = "<br>"
                elif width < 500:
                    font_size = "22px"
                    sep = "<br>"
                else:
                    font_size = "28px"
                    sep = "&nbsp;&nbsp;|&nbsp;&nbsp;"
                    
                combined = f"<div style='background: rgba(0,0,0,150); padding: 10px; border-radius: 8px; text-align: center; font-size: {font_size}; line-height: 1.3;'>{seal_html}{sep}{depth_html}</div>"
                self.rta_big_lbl.setHtml(combined)
                self.rta_big_lbl.setPos(rect.width() / 2, rect.height() - 20)
                self.rta_big_lbl.show()
            else:
                self.rta_big_lbl.hide()"""

new_big_lbl = """            if (depth_html or seal_html) and hasattr(self, 'chk_rta_helper') and self.chk_rta_helper.isChecked():
                # Make the text responsive based on viewbox width
                width = rect.width()
                if width < 300:
                    font_size = "18px"
                    sep = "<br>"
                elif width < 500:
                    font_size = "22px"
                    sep = "<br>"
                else:
                    font_size = "28px"
                    sep = "&nbsp;&nbsp;|&nbsp;&nbsp;"
                    
                combined = f"<div style='background: rgba(0,0,0,150); padding: 10px; border-radius: 8px; text-align: center; font-size: {font_size}; line-height: 1.3;'>{seal_html}{sep}{depth_html}</div>"
                self.rta_big_lbl.setHtml(combined)
                self.rta_big_lbl.setPos(rect.width() / 2, rect.height() - 20)
                self.rta_big_lbl.show()
            else:
                self.rta_big_lbl.hide()"""

content = content.replace(old_big_lbl, new_big_lbl)


# Update toggle_live_seal to hide target region if checked is false
old_toggle = """                self.rta_target_region.setZValue(-10)
                target_plot.addItem(self.rta_target_region)
            
            if not hasattr(self, 'rta_peak_line') or self.rta_peak_line is None:"""

new_toggle = """                self.rta_target_region.setZValue(-10)
                target_plot.addItem(self.rta_target_region)
            
            if hasattr(self, 'chk_rta_helper') and not self.chk_rta_helper.isChecked():
                self.rta_target_region.hide()
            
            if not hasattr(self, 'rta_peak_line') or self.rta_peak_line is None:"""

content = content.replace(old_toggle, new_toggle)


with open('main.py', 'w') as f:
    f.write(content)
