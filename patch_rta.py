import sys

with open('main.py', 'r') as f:
    content = f.read()

# Fix the AGC shift to be very slow so taps are visible
old_agc = """        if not hasattr(self, '_rta_shift'):
            self._rta_shift = calculated_shift
        else:
            self._rta_shift = 0.8 * self._rta_shift + 0.2 * calculated_shift"""

new_agc = """        if not hasattr(self, '_rta_shift'):
            self._rta_shift = calculated_shift
        else:
            # VERY slow adaptation so transients (like mic taps) are visibly preserved
            self._rta_shift = 0.98 * self._rta_shift + 0.02 * calculated_shift"""

content = content.replace(old_agc, new_agc)

# Setup a huge text overlay for RTA helper instead of hiding it in the sidebar
old_helper = """                if val_40 < val_500 - 15:
                    seal_html = "<span style='color: #ef4444; font-weight: bold;'>🔴 Seal Leak! (Bass fehlt)</span>"
                else:
                    seal_html = "<span style='color: #10b981; font-weight: bold;'>🟢 Seal OK</span>"
            else:
                seal_html = ""
                
            self.sub_lbl.setText(f"Live RTA | {seal_html} | {depth_html}")
        except Exception as e:
            pass"""

new_helper = """                if val_40 < val_500 - 15:
                    seal_html = "<span style='color: #ef4444; font-weight: bold;'>🔴 SEAL LEAK!</span>"
                else:
                    seal_html = "<span style='color: #10b981; font-weight: bold;'>🟢 SEAL OK</span>"
            else:
                seal_html = ""
                
            self.sub_lbl.setText(f"Live RTA | {seal_html} | {depth_html}")
            
            # Big on-screen text
            if not hasattr(self, 'rta_big_lbl'):
                import pyqtgraph as pg
                self.rta_big_lbl = pg.TextItem(html='', anchor=(0.5, 0.5))
                self.rta_big_lbl.setZValue(100)
                if hasattr(self, 'page_ana'):
                    self.rta_big_lbl.setParentItem(self.page_ana.plot_widget.getViewBox())
                else:
                    self.rta_big_lbl.setParentItem(self.plot_widget.getViewBox())
                    
            if hasattr(self, 'page_ana'):
                rect = self.page_ana.plot_widget.getViewBox().boundingRect()
            else:
                rect = self.plot_widget.getViewBox().boundingRect()
                
            self.rta_big_lbl.setPos(rect.width()/2, rect.height() - 50)
            self.rta_big_lbl.setHtml(f"<div style='font-family: Arial; font-size: 28px; background-color: rgba(0,0,0,150); padding: 10px; border-radius: 8px;'><center>{seal_html} &nbsp;&nbsp;|&nbsp;&nbsp; {depth_html}</center></div>")
            self.rta_big_lbl.show()
            
        except Exception as e:
            pass"""
content = content.replace(old_helper, new_helper)

# We also need to hide this rta_big_lbl when RTA stops!
old_stop = """            if hasattr(self, 'live_worker'):
                self.live_worker.stop()
                self.live_worker.wait()
            if hasattr(self, 'live_rta_line') and self.live_rta_line is not None:
                try:"""
                
new_stop = """            if hasattr(self, 'live_worker'):
                self.live_worker.stop()
                self.live_worker.wait()
            if hasattr(self, 'rta_big_lbl'):
                self.rta_big_lbl.hide()
            if hasattr(self, 'live_rta_line') and self.live_rta_line is not None:
                try:"""
content = content.replace(old_stop, new_stop)

with open('main.py', 'w') as f:
    f.write(content)
