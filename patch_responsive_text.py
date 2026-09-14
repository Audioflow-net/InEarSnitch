import sys

with open('main.py', 'r') as f:
    content = f.read()

old_rta_init = """            if not hasattr(self, 'rta_big_lbl'):
                import pyqtgraph as pg
                self.rta_big_lbl = pg.TextItem(html='', anchor=(0.5, 0.5))"""

new_rta_init = """            if not hasattr(self, 'rta_big_lbl'):
                import pyqtgraph as pg
                self.rta_big_lbl = pg.TextItem(html='', anchor=(0.5, 1.0))"""

content = content.replace(old_rta_init, new_rta_init)

old_rta_update = """            if hasattr(self, 'page_ana'):
                rect = self.page_ana.plot_widget.getViewBox().boundingRect()
            else:
                rect = self.plot_widget.getViewBox().boundingRect()
                
            self.rta_big_lbl.setPos(rect.width()/2, rect.height() - 50)
            divider = "&nbsp;&nbsp;|&nbsp;&nbsp;" if seal_html and depth_html else ""
            self.rta_big_lbl.setHtml(f"<div style='font-family: Arial; font-size: 28px; background-color: rgba(0,0,0,150); padding: 10px; border-radius: 8px;'><center>{seal_html} {divider} {depth_html}</center></div>")"""

new_rta_update = """            if hasattr(self, 'page_ana'):
                rect = self.page_ana.plot_widget.getViewBox().boundingRect()
            else:
                rect = self.plot_widget.getViewBox().boundingRect()
                
            w = rect.width()
            if w < 600:
                font_size = 18
            elif w < 900:
                font_size = 22
            else:
                font_size = 28
                
            # Anchor is (0.5, 1.0) - bottom center
            self.rta_big_lbl.setPos(w/2, rect.height() - 20)
            divider = "<br>" if seal_html and depth_html else ""
            self.rta_big_lbl.setHtml(f"<div style='font-family: Arial; font-size: {font_size}px; background-color: rgba(0,0,0,150); padding: 8px; border-radius: 8px;'><center>{seal_html}{divider}{depth_html}</center></div>")"""

content = content.replace(old_rta_update, new_rta_update)

with open('main.py', 'w') as f:
    f.write(content)
